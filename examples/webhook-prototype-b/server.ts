import http from "node:http";
import crypto from "node:crypto";

// ── Types ──────────────────────────────────────────────────────────────────

interface Subscriber {
  id: string;
  url: string;
  secret: string;
  consecutiveFailures: number;
  pausedUntil: number | null;
}

interface WebhookEvent {
  id: string;
  type: string;
  data: Record<string, unknown>;
  timestamp: string;
}

interface QueueItem {
  eventId: string;
  subscriberId: string;
  attempt: number;
  nextAttemptAt: number;
}

type DeliveryStatus = "queued" | "delivering" | "delivered" | "dead-lettered";

interface DeliveryRecord {
  eventId: string;
  subscriberId: string;
  status: DeliveryStatus;
  attempts: number;
  lastError?: string;
}

// ── Configuration ──────────────────────────────────────────────────────────

const PORT = Number(process.env.PORT ?? 3001);
const MAX_RETRIES = 4;
const BACKOFF_BASE_MS = 1000;
const WORKER_INTERVAL_MS = 500;
const CIRCUIT_BREAKER_THRESHOLD = 3;
const CIRCUIT_BREAKER_PAUSE_MS = 30_000;
const DELIVERY_TIMEOUT_MS = 5_000;

// ── State ──────────────────────────────────────────────────────────────────

const subscribers = new Map<string, Subscriber>();
const events = new Map<string, WebhookEvent>();
const deliveryQueue: QueueItem[] = [];
const deadLetterQueue: QueueItem[] = [];
const deliveryRecords = new Map<string, DeliveryRecord>(); // key: eventId:subscriberId

let totalDelivered = 0;
let totalDeadLettered = 0;

// ── Helpers ────────────────────────────────────────────────────────────────

const uuid = (): string => crypto.randomUUID();

const sign = (payload: string, secret: string): string =>
  crypto.createHmac("sha256", secret).update(payload).digest("hex");

const recordKey = (eventId: string, subId: string): string =>
  `${eventId}:${subId}`;

const backoffMs = (attempt: number): number =>
  BACKOFF_BASE_MS * Math.pow(2, attempt - 1);

const readBody = (req: http.IncomingMessage): Promise<string> =>
  new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c: Buffer) => chunks.push(c));
    req.on("end", () => resolve(Buffer.concat(chunks).toString()));
    req.on("error", reject);
  });

const json = (
  res: http.ServerResponse,
  status: number,
  body: unknown,
): void => {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(body));
};

// ── Queue operations (sorted by nextAttemptAt) ─────────────────────────────

const enqueue = (item: QueueItem): void => {
  const idx = deliveryQueue.findIndex(
    (q) => q.nextAttemptAt > item.nextAttemptAt,
  );
  if (idx === -1) {
    deliveryQueue.push(item);
  } else {
    deliveryQueue.splice(idx, 0, item);
  }
};

// ── Delivery ───────────────────────────────────────────────────────────────

const deliver = async (item: QueueItem): Promise<void> => {
  const subscriber = subscribers.get(item.subscriberId);
  const event = events.get(item.eventId);
  if (!subscriber || !event) return;

  // Circuit breaker — skip if subscriber is paused
  if (subscriber.pausedUntil !== null && Date.now() < subscriber.pausedUntil) {
    enqueue({ ...item, nextAttemptAt: subscriber.pausedUntil });
    return;
  }

  const key = recordKey(item.eventId, item.subscriberId);
  const record: DeliveryRecord = deliveryRecords.get(key) ?? {
    eventId: item.eventId,
    subscriberId: item.subscriberId,
    status: "queued",
    attempts: 0,
  };
  record.status = "delivering";
  record.attempts = item.attempt;
  deliveryRecords.set(key, record);

  const payload = JSON.stringify(event);
  const signature = sign(payload, subscriber.secret);

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), DELIVERY_TIMEOUT_MS);

    const response = await fetch(subscriber.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Webhook-Event-Id": event.id,
      },
      body: payload,
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    // Success
    record.status = "delivered";
    deliveryRecords.set(key, record);
    totalDelivered++;

    // Reset circuit breaker on success
    subscribers.set(subscriber.id, {
      ...subscriber,
      consecutiveFailures: 0,
      pausedUntil: null,
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Unknown error";
    record.lastError = errorMsg;

    // Update circuit breaker state
    const failures = subscriber.consecutiveFailures + 1;
    const paused =
      failures >= CIRCUIT_BREAKER_THRESHOLD
        ? Date.now() + CIRCUIT_BREAKER_PAUSE_MS
        : subscriber.pausedUntil;

    subscribers.set(subscriber.id, {
      ...subscriber,
      consecutiveFailures: failures,
      pausedUntil: paused,
    });

    if (item.attempt >= MAX_RETRIES) {
      // Dead letter
      record.status = "dead-lettered";
      deliveryRecords.set(key, record);
      deadLetterQueue.push(item);
      totalDeadLettered++;
      console.log(
        `[DLQ] event=${item.eventId} subscriber=${item.subscriberId} error=${errorMsg}`,
      );
    } else {
      // Re-queue with backoff
      record.status = "queued";
      deliveryRecords.set(key, record);
      const delay = backoffMs(item.attempt);
      enqueue({
        ...item,
        attempt: item.attempt + 1,
        nextAttemptAt: Date.now() + delay,
      });
      console.log(
        `[RETRY] event=${item.eventId} attempt=${item.attempt + 1} in ${delay}ms`,
      );
    }
  }
};

// ── Worker loop ────────────────────────────────────────────────────────────

const processQueue = (): void => {
  const now = Date.now();
  const ready: QueueItem[] = [];

  // Drain items that are due
  while (deliveryQueue.length > 0 && deliveryQueue[0].nextAttemptAt <= now) {
    ready.push(deliveryQueue.shift()!);
  }

  for (const item of ready) {
    deliver(item).catch((err) =>
      console.error("[WORKER] Unexpected error:", err),
    );
  }
};

// ── HTTP Router ────────────────────────────────────────────────────────────

const route = async (
  req: http.IncomingMessage,
  res: http.ServerResponse,
): Promise<void> => {
  const method = req.method ?? "GET";
  const url = req.url ?? "/";

  // POST /subscribers — register a webhook subscriber
  if (method === "POST" && url === "/subscribers") {
    const body = JSON.parse(await readBody(req));
    const id = uuid();
    const secret = body.secret ?? crypto.randomBytes(32).toString("hex");
    const subscriber: Subscriber = {
      id,
      url: body.url,
      secret,
      consecutiveFailures: 0,
      pausedUntil: null,
    };
    subscribers.set(id, subscriber);
    return json(res, 201, { id, secret });
  }

  // GET /subscribers — list all subscribers
  if (method === "GET" && url === "/subscribers") {
    return json(res, 200, [...subscribers.values()]);
  }

  // POST /events — accept an event (202 Accepted, queued)
  if (method === "POST" && url === "/events") {
    const body = JSON.parse(await readBody(req));
    const event: WebhookEvent = {
      id: uuid(),
      type: body.type,
      data: body.data ?? {},
      timestamp: new Date().toISOString(),
    };
    events.set(event.id, event);

    // Enqueue a delivery for every subscriber
    for (const sub of subscribers.values()) {
      const item: QueueItem = {
        eventId: event.id,
        subscriberId: sub.id,
        attempt: 1,
        nextAttemptAt: Date.now(),
      };
      enqueue(item);

      deliveryRecords.set(recordKey(event.id, sub.id), {
        eventId: event.id,
        subscriberId: sub.id,
        status: "queued",
        attempts: 0,
      });
    }

    return json(res, 202, { id: event.id, status: "queued" });
  }

  // GET /events/:id/status — delivery status for an event
  const statusMatch = url.match(/^\/events\/([^/]+)\/status$/);
  if (method === "GET" && statusMatch) {
    const eventId = statusMatch[1];
    if (!events.has(eventId)) {
      return json(res, 404, { error: "Event not found" });
    }
    const records = [...deliveryRecords.values()].filter(
      (r) => r.eventId === eventId,
    );
    return json(res, 200, { eventId, deliveries: records });
  }

  // GET /status — system overview
  if (method === "GET" && url === "/status") {
    return json(res, 200, {
      subscribers: subscribers.size,
      queueDepth: deliveryQueue.length,
      deadLetterCount: deadLetterQueue.length,
      totalDelivered,
      totalDeadLettered,
    });
  }

  // GET /dead-letter — inspect dead letter queue
  if (method === "GET" && url === "/dead-letter") {
    const enriched = deadLetterQueue.map((item) => ({
      ...item,
      record: deliveryRecords.get(recordKey(item.eventId, item.subscriberId)),
    }));
    return json(res, 200, enriched);
  }

  json(res, 404, { error: "Not found" });
};

// ── Server ─────────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  route(req, res).catch((err) => {
    console.error("[ERROR]", err);
    json(res, 500, { error: "Internal server error" });
  });
});

const workerTimer = setInterval(processQueue, WORKER_INTERVAL_MS);

server.listen(PORT, () => {
  console.log(`Webhook queue server listening on http://localhost:${PORT}`);
  console.log(`Worker polling every ${WORKER_INTERVAL_MS}ms`);
});

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("\nShutting down...");
  clearInterval(workerTimer);
  server.close(() => process.exit(0));
});
