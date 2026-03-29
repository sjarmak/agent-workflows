import { createServer, IncomingMessage, ServerResponse } from "node:http";
import { createHmac, randomUUID } from "node:crypto";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type EventType =
  | "EventReceived"
  | "SubscriberRegistered"
  | "DeliveryAttempted"
  | "DeliverySucceeded"
  | "DeliveryFailed"
  | "DeliveryAbandoned";

interface LogEntry {
  readonly seq: number;
  readonly type: EventType;
  readonly timestamp: string;
  readonly payload: Record<string, unknown>;
}

interface Subscriber {
  readonly id: string;
  readonly url: string;
  readonly secret: string;
}

interface DeliveryState {
  readonly eventId: string;
  readonly subscriberId: string;
  readonly status:
    | "pending"
    | "delivering"
    | "succeeded"
    | "failed"
    | "abandoned";
  readonly attempts: number;
  readonly lastAttemptAt: string | null;
  readonly nextRetryAt: number | null;
}

// ---------------------------------------------------------------------------
// Append-only event log
// ---------------------------------------------------------------------------

const log: LogEntry[] = [];
let seqCounter = 0;

function appendEvent(
  type: EventType,
  payload: Record<string, unknown>,
): LogEntry {
  const entry: LogEntry = {
    seq: ++seqCounter,
    type,
    timestamp: new Date().toISOString(),
    payload,
  };
  log.push(entry);
  return entry;
}

// ---------------------------------------------------------------------------
// State projector -- derives current state from log replay
// ---------------------------------------------------------------------------

function projectDeliveryStates(): ReadonlyArray<DeliveryState> {
  const states = new Map<string, DeliveryState>();

  for (const entry of log) {
    const key =
      entry.payload.eventId && entry.payload.subscriberId
        ? `${entry.payload.eventId}::${entry.payload.subscriberId}`
        : null;

    switch (entry.type) {
      case "EventReceived": {
        // Pair with every subscriber known at this point
        const subscribers = projectSubscribers(entry.seq);
        for (const sub of subscribers) {
          const k = `${entry.payload.id}::${sub.id}`;
          states.set(k, {
            eventId: entry.payload.id as string,
            subscriberId: sub.id,
            status: "pending",
            attempts: 0,
            lastAttemptAt: null,
            nextRetryAt: Date.now(),
          });
        }
        break;
      }
      case "DeliveryAttempted": {
        if (!key) break;
        const prev = states.get(key);
        if (prev) {
          states.set(key, {
            ...prev,
            status: "delivering",
            lastAttemptAt: entry.timestamp,
          });
        }
        break;
      }
      case "DeliverySucceeded": {
        if (!key) break;
        const prev = states.get(key);
        if (prev) {
          states.set(key, { ...prev, status: "succeeded" });
        }
        break;
      }
      case "DeliveryFailed": {
        if (!key) break;
        const prev = states.get(key);
        if (prev) {
          const attempts = (entry.payload.attempt as number) ?? prev.attempts;
          const backoffMs = Math.pow(2, attempts - 1) * 1000; // 1s, 2s, 4s, 8s, 16s
          states.set(key, {
            ...prev,
            status: "failed",
            attempts,
            nextRetryAt: Date.now() + backoffMs,
          });
        }
        break;
      }
      case "DeliveryAbandoned": {
        if (!key) break;
        const prev = states.get(key);
        if (prev) {
          states.set(key, { ...prev, status: "abandoned", nextRetryAt: null });
        }
        break;
      }
    }
  }

  return Array.from(states.values());
}

function projectSubscribers(upToSeq?: number): ReadonlyArray<Subscriber> {
  const subs = new Map<string, Subscriber>();
  for (const entry of log) {
    if (upToSeq !== undefined && entry.seq > upToSeq) break;
    if (entry.type === "SubscriberRegistered") {
      subs.set(entry.payload.id as string, {
        id: entry.payload.id as string,
        url: entry.payload.url as string,
        secret: entry.payload.secret as string,
      });
    }
  }
  return Array.from(subs.values());
}

// ---------------------------------------------------------------------------
// HMAC signature
// ---------------------------------------------------------------------------

function sign(payload: string, secret: string): string {
  return createHmac("sha256", secret).update(payload).digest("hex");
}

// ---------------------------------------------------------------------------
// Delivery processor
// ---------------------------------------------------------------------------

const MAX_RETRIES = 5;
const delivering = new Set<string>(); // prevent concurrent delivery of same pair

async function processDeliveries(): Promise<void> {
  const states = projectDeliveryStates();
  const subscribers = projectSubscribers();
  const subMap = new Map(subscribers.map((s) => [s.id, s]));
  const now = Date.now();

  const deliverable = states.filter(
    (s) =>
      (s.status === "pending" || s.status === "failed") &&
      s.attempts < MAX_RETRIES &&
      s.nextRetryAt !== null &&
      s.nextRetryAt <= now &&
      !delivering.has(`${s.eventId}::${s.subscriberId}`),
  );

  const tasks = deliverable.map(async (state) => {
    const sub = subMap.get(state.subscriberId);
    if (!sub) return;

    const pairKey = `${state.eventId}::${state.subscriberId}`;
    delivering.add(pairKey);

    const attempt = state.attempts + 1;

    // Find the original event payload
    const originalEvent = log.find(
      (e) => e.type === "EventReceived" && e.payload.id === state.eventId,
    );
    if (!originalEvent) {
      delivering.delete(pairKey);
      return;
    }

    const body = JSON.stringify(originalEvent.payload);
    const signature = sign(body, sub.secret);

    appendEvent("DeliveryAttempted", {
      eventId: state.eventId,
      subscriberId: sub.id,
      attempt,
    });

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);

      const res = await fetch(sub.url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Webhook-Signature": signature,
          "X-Event-Id": state.eventId,
        },
        body,
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (res.ok) {
        appendEvent("DeliverySucceeded", {
          eventId: state.eventId,
          subscriberId: sub.id,
          attempt,
          statusCode: res.status,
        });
      } else {
        appendEvent("DeliveryFailed", {
          eventId: state.eventId,
          subscriberId: sub.id,
          attempt,
          statusCode: res.status,
        });
        if (attempt >= MAX_RETRIES) {
          appendEvent("DeliveryAbandoned", {
            eventId: state.eventId,
            subscriberId: sub.id,
            reason: `Failed after ${MAX_RETRIES} attempts`,
          });
        }
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      appendEvent("DeliveryFailed", {
        eventId: state.eventId,
        subscriberId: sub.id,
        attempt,
        error: message,
      });
      if (attempt >= MAX_RETRIES) {
        appendEvent("DeliveryAbandoned", {
          eventId: state.eventId,
          subscriberId: sub.id,
          reason: `Failed after ${MAX_RETRIES} attempts: ${message}`,
        });
      }
    } finally {
      delivering.delete(pairKey);
    }
  });

  await Promise.allSettled(tasks);
}

// ---------------------------------------------------------------------------
// HTTP helpers
// ---------------------------------------------------------------------------

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c: Buffer) => chunks.push(c));
    req.on("end", () => resolve(Buffer.concat(chunks).toString()));
    req.on("error", reject);
  });
}

function json(res: ServerResponse, status: number, data: unknown): void {
  const body = JSON.stringify(data, null, 2);
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(body);
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

const server = createServer(async (req, res) => {
  const url = new URL(
    req.url ?? "/",
    `http://${req.headers.host ?? "localhost"}`,
  );
  const method = req.method ?? "GET";

  try {
    // POST /subscribers -- register a webhook subscriber
    if (method === "POST" && url.pathname === "/subscribers") {
      const body = JSON.parse(await readBody(req));
      if (!body.url) {
        return json(res, 400, { error: "url is required" });
      }
      const id = randomUUID();
      const secret = randomUUID();
      appendEvent("SubscriberRegistered", { id, url: body.url, secret });
      return json(res, 201, { id, secret, url: body.url });
    }

    // GET /subscribers -- list subscribers
    if (method === "GET" && url.pathname === "/subscribers") {
      const subs = projectSubscribers().map(({ id, url }) => ({ id, url }));
      return json(res, 200, subs);
    }

    // POST /events -- submit a new event
    if (method === "POST" && url.pathname === "/events") {
      const body = JSON.parse(await readBody(req));
      const event = {
        id: randomUUID(),
        type: body.type ?? "generic",
        data: body.data ?? {},
        timestamp: new Date().toISOString(),
      };
      appendEvent("EventReceived", event);
      return json(res, 201, { eventId: event.id, status: "received" });
    }

    // GET /events/:id -- derived state for an event
    const eventMatch = url.pathname.match(/^\/events\/([^/]+)$/);
    if (method === "GET" && eventMatch) {
      const eventId = eventMatch[1];
      const states = projectDeliveryStates().filter(
        (s) => s.eventId === eventId,
      );
      if (states.length === 0) {
        return json(res, 404, { error: "event not found or no subscribers" });
      }
      return json(res, 200, { eventId, deliveries: states });
    }

    // GET /log -- full event log, optionally filtered
    if (method === "GET" && url.pathname === "/log") {
      const eventId = url.searchParams.get("event_id");
      const filtered = eventId
        ? log.filter(
            (e) => e.payload.id === eventId || e.payload.eventId === eventId,
          )
        : log;
      return json(res, 200, filtered);
    }

    // GET /health
    if (method === "GET" && url.pathname === "/health") {
      return json(res, 200, {
        status: "ok",
        logSize: log.length,
        seq: seqCounter,
      });
    }

    json(res, 404, { error: "not found" });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    json(res, 500, { error: message });
  }
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

const PORT = parseInt(process.env.PORT ?? "3003", 10);

server.listen(PORT, () => {
  console.log(`[event-sourced webhook] listening on http://localhost:${PORT}`);
  console.log("Endpoints:");
  console.log("  POST /subscribers        - register subscriber {url}");
  console.log("  GET  /subscribers        - list subscribers");
  console.log("  POST /events             - submit event {type, data}");
  console.log("  GET  /events/:id         - derived delivery state");
  console.log("  GET  /log                - full event log");
  console.log("  GET  /log?event_id=X     - event-specific log");
  console.log("  GET  /health             - health check");
});

// Delivery processor on 1s interval
const deliveryInterval = setInterval(processDeliveries, 1000);

process.on("SIGINT", () => {
  clearInterval(deliveryInterval);
  server.close();
  console.log("\nShutdown complete.");
  process.exit(0);
});
