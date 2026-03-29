# Prototype B: Queue-Based Webhook Delivery

A webhook delivery system that decouples event ingestion from delivery using an
in-memory priority queue and a background worker loop.

## Architecture

```
POST /events  -->  Event Store  -->  Delivery Queue  -->  Worker Loop  -->  fetch(subscriber.url)
  (202 Accepted)                      (sorted by                           |
                                       nextAttemptAt)                      +--> success: mark delivered
                                                                           +--> fail: re-queue with backoff
                                                                           +--> max retries: dead letter queue
```

**Components:**

- **Event API** -- POST /events returns 202 immediately; GET /events/:id/status shows per-subscriber delivery state
- **Subscriber registry** -- in-memory map; POST /subscribers to register, GET /subscribers to list
- **Delivery queue** -- sorted by next-attempt time; worker drains items that are due every 500ms
- **Worker loop** -- setInterval-based; processes ready items, fires deliveries concurrently
- **Dead letter queue** -- permanently failed deliveries (4 retries exhausted) stored for inspection
- **Circuit breaker** -- 3 consecutive failures pauses a subscriber for 30 seconds

## Running

Requires Node.js 18+ (for built-in `fetch`).

```bash
npx tsx server.ts
```

The server starts on port 3001 (override with `PORT` env var).

## Demo with curl

```bash
# 1. Start a receiver (in another terminal)
npx tsx -e "
import http from 'node:http';
http.createServer((req, res) => {
  let body = '';
  req.on('data', c => body += c);
  req.on('end', () => {
    console.log('Received:', body);
    console.log('Signature:', req.headers['x-webhook-signature']);
    res.writeHead(200);
    res.end('ok');
  });
}).listen(4000, () => console.log('Receiver on :4000'));
"

# 2. Register a subscriber
curl -s -X POST http://localhost:3001/subscribers \
  -H 'Content-Type: application/json' \
  -d '{"url": "http://localhost:4000/hook"}' | jq

# 3. Send an event (returns 202 immediately)
curl -s -X POST http://localhost:3001/events \
  -H 'Content-Type: application/json' \
  -d '{"type": "order.created", "data": {"orderId": 42, "total": 99.95}}' | jq

# 4. Check delivery status
curl -s http://localhost:3001/events/<EVENT_ID>/status | jq

# 5. System overview
curl -s http://localhost:3001/status | jq

# 6. Inspect dead letter queue
curl -s http://localhost:3001/dead-letter | jq
```

## API Summary

| Method | Path               | Description                      |
| ------ | ------------------ | -------------------------------- |
| POST   | /subscribers       | Register a webhook URL           |
| GET    | /subscribers       | List all subscribers             |
| POST   | /events            | Submit an event (202 Accepted)   |
| GET    | /events/:id/status | Delivery status per subscriber   |
| GET    | /status            | Queue depth, delivery counts     |
| GET    | /dead-letter       | Inspect permanently failed items |

## Tradeoffs

**Strengths:**

- Instant event acceptance (202) -- callers never block on delivery
- Natural backpressure: queue depth is observable, worker throughput is tunable
- Failed deliveries are retried automatically with exponential backoff
- Circuit breaker prevents hammering unhealthy subscribers
- Dead letter queue preserves failed items for debugging or replay
- Clean separation between ingestion and delivery makes each independently testable

**Weaknesses:**

- In-memory queue is lost on process restart (no durability)
- Single worker loop -- no parallelism control beyond concurrent async deliveries
- Priority queue uses array splice (O(n) insert); fine for demos, not for high volume
- No subscriber authentication on the management API
- No persistence layer for events or delivery records
- Queue depth is unbounded -- no backpressure on producers

**When to pick this approach:**

Best when delivery latency tolerance is moderate (seconds, not milliseconds) and you
want the operational visibility of a queue (depth metrics, dead letters, retry state).
Natural path toward a durable queue (Redis, SQS) if the prototype proves out.
