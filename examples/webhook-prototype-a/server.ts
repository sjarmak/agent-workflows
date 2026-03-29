import { createServer, IncomingMessage, ServerResponse } from "node:http";
import { createHmac, randomUUID } from "node:crypto";

// ── Types ──────────────────────────────────────────────────────────────────

interface WebhookEvent {
  readonly id: string;
  readonly type: string;
  readonly data: Record<string, unknown>;
  readonly timestamp: string;
}

type DeliveryStatus = "pending" | "delivering" | "delivered" | "failed";

interface DeliveryRecord {
  readonly eventId: string;
  readonly subscriberUrl: string;
  readonly status: DeliveryStatus;
  readonly attempts: number;
  readonly lastError?: string;
}

interface DeadLetterEntry {
  readonly event: WebhookEvent;
  readonly subscriberUrl: string;
  readonly error: string;
  readonly failedAt: string;
}

// ── Stores (immutable update pattern) ──────────────────────────────────────

const SIGNING_SECRET = process.env.WEBHOOK_SECRET ?? "dev-secret-change-me";
const MAX_RETRIES = 3;
const BASE_DELAY_MS = 1000;
const PORT = Number(process.env.PORT ?? 3000);

let events: ReadonlyArray<WebhookEvent> = [];
let subscribers: ReadonlyArray<string> = [];
let deliveries: ReadonlyArray<DeliveryRecord> = [];
let deadLetters: ReadonlyArray<DeadLetterEntry> = [];

// ── Helpers ────────────────────────────────────────────────────────────────

function signPayload(body: string): string {
  return createHmac("sha256", SIGNING_SECRET).update(body).digest("hex");
}

function findEvent(id: string): WebhookEvent | undefined {
  return events.find((e) => e.id === id);
}

function getDeliveries(eventId: string): ReadonlyArray<DeliveryRecord> {
  return deliveries.filter((d) => d.eventId === eventId);
}

function upsertDelivery(record: DeliveryRecord): void {
  const idx = deliveries.findIndex(
    (d) =>
      d.eventId === record.eventId && d.subscriberUrl === record.subscriberUrl,
  );
  if (idx === -1) {
    deliveries = [...deliveries, record];
  } else {
    deliveries = deliveries.map((d, i) => (i === idx ? record : d));
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c: Buffer) => chunks.push(c));
    req.on("end", () => resolve(Buffer.concat(chunks).toString()));
    req.on("error", reject);
  });
}

function json(res: ServerResponse, status: number, body: unknown): void {
  const payload = JSON.stringify(body);
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(payload);
}

// ── Delivery Engine ────────────────────────────────────────────────────────

async function deliverToSubscriber(
  event: WebhookEvent,
  url: string,
): Promise<void> {
  const body = JSON.stringify(event);
  const signature = signPayload(body);

  upsertDelivery({
    eventId: event.id,
    subscriberUrl: url,
    status: "delivering",
    attempts: 0,
  });

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Webhook-Signature": signature,
          "X-Webhook-Event-Id": event.id,
        },
        body,
        signal: AbortSignal.timeout(5000),
      });

      if (response.ok) {
        upsertDelivery({
          eventId: event.id,
          subscriberUrl: url,
          status: "delivered",
          attempts: attempt,
        });
        console.log(
          `[delivered] event=${event.id} url=${url} attempt=${attempt}`,
        );
        return;
      }

      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.log(
        `[retry] event=${event.id} url=${url} attempt=${attempt} error=${message}`,
      );

      upsertDelivery({
        eventId: event.id,
        subscriberUrl: url,
        status: attempt === MAX_RETRIES ? "failed" : "delivering",
        attempts: attempt,
        lastError: message,
      });

      if (attempt < MAX_RETRIES) {
        const delay = BASE_DELAY_MS * Math.pow(2, attempt - 1); // 1s, 2s, 4s
        await sleep(delay);
      }
    }
  }

  // Exhausted retries — dead letter
  const lastRecord = deliveries.find(
    (d) => d.eventId === event.id && d.subscriberUrl === url,
  );
  deadLetters = [
    ...deadLetters,
    {
      event,
      subscriberUrl: url,
      error: lastRecord?.lastError ?? "unknown",
      failedAt: new Date().toISOString(),
    },
  ];
  console.log(`[dead-letter] event=${event.id} url=${url}`);
}

async function deliverEvent(event: WebhookEvent): Promise<void> {
  // Synchronous: deliver to each subscriber sequentially (sync-first design)
  for (const url of subscribers) {
    await deliverToSubscriber(event, url);
  }
}

// ── Router ─────────────────────────────────────────────────────────────────

async function handleRequest(
  req: IncomingMessage,
  res: ServerResponse,
): Promise<void> {
  const method = req.method ?? "GET";
  const url = req.url ?? "/";

  // POST /subscribers — register a webhook URL
  if (method === "POST" && url === "/subscribers") {
    const body = JSON.parse(await readBody(req));
    const subscriberUrl = body?.url;
    if (
      typeof subscriberUrl !== "string" ||
      !subscriberUrl.startsWith("http")
    ) {
      return json(res, 400, { error: "Field 'url' must be a valid HTTP URL" });
    }
    if (subscribers.includes(subscriberUrl)) {
      return json(res, 409, { error: "Subscriber already registered" });
    }
    subscribers = [...subscribers, subscriberUrl];
    console.log(`[subscriber] registered ${subscriberUrl}`);
    return json(res, 201, { url: subscriberUrl });
  }

  // GET /subscribers — list all subscribers
  if (method === "GET" && url === "/subscribers") {
    return json(res, 200, { subscribers });
  }

  // POST /events — submit a new event (triggers synchronous delivery)
  if (method === "POST" && url === "/events") {
    const body = JSON.parse(await readBody(req));
    const event: WebhookEvent = {
      id: randomUUID(),
      type: body?.type ?? "unknown",
      data: body?.data ?? {},
      timestamp: new Date().toISOString(),
    };
    events = [...events, event];

    // Initialize pending deliveries for all current subscribers
    for (const subUrl of subscribers) {
      upsertDelivery({
        eventId: event.id,
        subscriberUrl: subUrl,
        status: "pending",
        attempts: 0,
      });
    }

    console.log(
      `[event] id=${event.id} type=${event.type} subscribers=${subscribers.length}`,
    );

    // Synchronous delivery — blocks until all deliveries complete or fail
    await deliverEvent(event);

    const records = getDeliveries(event.id);
    return json(res, 201, { event, deliveries: records });
  }

  // GET /events/:id — event status with delivery details
  const eventMatch = url.match(/^\/events\/([a-f0-9-]+)$/);
  if (method === "GET" && eventMatch) {
    const event = findEvent(eventMatch[1]);
    if (!event) {
      return json(res, 404, { error: "Event not found" });
    }
    return json(res, 200, { event, deliveries: getDeliveries(event.id) });
  }

  // GET /dead-letters — view failed deliveries
  if (method === "GET" && url === "/dead-letters") {
    return json(res, 200, { deadLetters });
  }

  // GET / — health check
  if (method === "GET" && url === "/") {
    return json(res, 200, {
      status: "ok",
      subscribers: subscribers.length,
      events: events.length,
      deadLetters: deadLetters.length,
    });
  }

  json(res, 404, { error: "Not found" });
}

// ── Server ─────────────────────────────────────────────────────────────────

const server = createServer((req, res) => {
  handleRequest(req, res).catch((err) => {
    console.error("[error]", err);
    json(res, 500, { error: "Internal server error" });
  });
});

server.listen(PORT, () => {
  console.log(
    `Webhook server (sync-first) listening on http://localhost:${PORT}`,
  );
  console.log(`Secret: ${SIGNING_SECRET}`);
  console.log(`Max retries: ${MAX_RETRIES}, backoff: ${BASE_DELAY_MS}ms base`);
});
