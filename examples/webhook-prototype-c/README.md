# Prototype C: Event-Sourced Webhook Delivery

An event-sourced webhook delivery system where every state change is an immutable event appended to an in-memory log. Current state is never stored directly -- it is always derived by replaying the log.

## Architecture

All state is derived from six event types in an append-only log:

| Event Type             | Meaning                                                 |
| ---------------------- | ------------------------------------------------------- |
| `SubscriberRegistered` | A webhook endpoint was registered                       |
| `EventReceived`        | An inbound event was submitted for delivery             |
| `DeliveryAttempted`    | The system started a delivery attempt                   |
| `DeliverySucceeded`    | Delivery got an HTTP 2xx response                       |
| `DeliveryFailed`       | Delivery failed (non-2xx or network error)              |
| `DeliveryAbandoned`    | Retries exhausted (5 attempts with exponential backoff) |

The **state projector** folds over the log to compute current delivery status on demand. The **delivery processor** runs every 1 second, reads projected state, and attempts delivery for any pending or failed items whose backoff window has elapsed.

Each delivery carries an HMAC-SHA256 signature in the `X-Webhook-Signature` header so subscribers can verify authenticity.

## Running

```bash
npx tsx server.ts
```

Server starts on port 3003 (override with `PORT` env var).

## Usage with curl

```bash
# 1. Register a subscriber
curl -s -X POST http://localhost:3003/subscribers \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/post"}' | jq .

# 2. Submit an event
curl -s -X POST http://localhost:3003/events \
  -H "Content-Type: application/json" \
  -d '{"type": "order.created", "data": {"orderId": 42}}' | jq .

# 3. Check derived delivery state (use the eventId from step 2)
curl -s http://localhost:3003/events/<EVENT_ID> | jq .

# 4. View the full event log
curl -s http://localhost:3003/log | jq .

# 5. View log filtered to one event
curl -s "http://localhost:3003/log?event_id=<EVENT_ID>" | jq .

# 6. Health check
curl -s http://localhost:3003/health | jq .
```

## Tradeoffs

**Strengths:**

- Full audit trail -- every state change is recorded and queryable
- Replayability -- state can be rebuilt from scratch at any time
- Debugging is trivial -- inspect the log to see exactly what happened and when
- No mutable state means no inconsistency bugs
- Natural fit for retry logic -- failed deliveries are just events that trigger future processing

**Weaknesses:**

- Projection cost grows linearly with log size (O(n) per query in this in-memory version)
- Memory grows without bound (production systems need log compaction or snapshots)
- More complex mental model than direct state mutation
- Delivery ordering depends on projection accuracy
- In-memory log is lost on restart (production needs durable storage like Kafka or a database)

## API Reference

| Method | Path              | Description                                                  |
| ------ | ----------------- | ------------------------------------------------------------ |
| POST   | `/subscribers`    | Register a subscriber `{url}` -- returns `{id, secret, url}` |
| GET    | `/subscribers`    | List all subscribers                                         |
| POST   | `/events`         | Submit an event `{type, data}` -- returns `{eventId}`        |
| GET    | `/events/:id`     | Derived delivery state for an event                          |
| GET    | `/log`            | Full append-only event log                                   |
| GET    | `/log?event_id=X` | Log entries related to a specific event                      |
| GET    | `/health`         | Health check with log size                                   |
