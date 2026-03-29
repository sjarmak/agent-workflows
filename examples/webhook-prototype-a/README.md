# Prototype A: Sync-First Webhook Delivery

Simplest possible webhook delivery system. When an event is submitted, the server delivers it to every subscriber synchronously before returning the HTTP response. Failed deliveries retry inline with exponential backoff (1s, 2s, 4s). After 3 attempts, failures go to a dead letter store.

## Architecture

```
POST /events
  │
  ├─► subscriber 1 ──► retry loop (up to 3x) ──► delivered / dead-letter
  ├─► subscriber 2 ──► retry loop (up to 3x) ──► delivered / dead-letter
  └─► subscriber N ──► ...
  │
  ◄── 201 response (after ALL deliveries complete)
```

All state is in-memory. Every delivery is signed with HMAC-SHA256 so subscribers can verify authenticity.

## Running

```bash
npx tsx server.ts
```

Server starts on port 3000 (override with `PORT` env var).

## Demo with curl

### 1. Register subscribers

```bash
# Register a real endpoint (use a local server, httpbin, etc.)
curl -s -X POST http://localhost:3000/subscribers \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://httpbin.org/post"}' | jq

# Register a second subscriber that will fail (to demo dead-lettering)
curl -s -X POST http://localhost:3000/subscribers \
  -H 'Content-Type: application/json' \
  -d '{"url": "http://localhost:9999/nope"}' | jq
```

### 2. Submit an event

```bash
curl -s -X POST http://localhost:3000/events \
  -H 'Content-Type: application/json' \
  -d '{"type": "order.created", "data": {"orderId": 42, "total": 99.95}}' | jq
```

The response blocks until all deliveries (and retries) complete, then returns the event with per-subscriber delivery status.

### 3. Check event status

```bash
curl -s http://localhost:3000/events/<EVENT_ID> | jq
```

### 4. View dead letters

```bash
curl -s http://localhost:3000/dead-letters | jq
```

### 5. Health check

```bash
curl -s http://localhost:3000/ | jq
```

## Verifying signatures (subscriber side)

Subscribers receive a `X-Webhook-Signature` header. To verify:

```bash
echo -n '<raw JSON body>' | openssl dgst -sha256 -hmac "dev-secret-change-me"
```

Set the secret via `WEBHOOK_SECRET` env var.

## API Reference

| Method | Path            | Description                                                             |
| ------ | --------------- | ----------------------------------------------------------------------- |
| GET    | `/`             | Health check                                                            |
| POST   | `/subscribers`  | Register a webhook URL (`{"url": "..."}`)                               |
| GET    | `/subscribers`  | List all subscribers                                                    |
| POST   | `/events`       | Submit event, triggers sync delivery (`{"type": "...", "data": {...}}`) |
| GET    | `/events/:id`   | Event status with per-subscriber delivery details                       |
| GET    | `/dead-letters` | View all failed deliveries                                              |

## Tradeoffs

**Strengths:**

- Dead simple — single file, no dependencies, easy to reason about
- Caller gets delivery status in the response (no polling needed)
- Deterministic: the response tells you exactly what happened
- Easy to debug: linear execution, no background jobs

**Weaknesses:**

- Response time scales with subscriber count and retry delays (worst case: N subscribers x 3 retries x 7s backoff = very slow)
- One slow/down subscriber blocks delivery to all subsequent subscribers
- Not suitable for high throughput — each request ties up a connection for the full delivery cycle
- No persistence — server restart loses all state
- No concurrency — subscribers are delivered to sequentially, not in parallel
