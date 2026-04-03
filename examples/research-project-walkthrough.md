# Full Pipeline Walkthrough: Webhook Delivery System

This walkthrough shows the complete 10-skill pipeline running end-to-end on a single problem: **designing and prototyping a webhook delivery system**. Every skill was actually executed (not simulated), with parallel agents producing independent results at each phase.

## The Problem

You're building a webhook delivery service — the kind that Stripe, GitHub, and Slack use to notify subscriber endpoints about events. The requirements seem simple (accept events, deliver them to URLs) but the design space is rich: delivery guarantees, retry strategies, failure handling, and observability all have competing approaches with real tradeoffs.

## Phase 1: Diverge — Multi-Perspective Research

```
/diverge 4 "What example project would best showcase multi-agent workflow skills?"
```

Four independent agents explored the problem from different lenses:

| Lens               | Key Finding                                                                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prior art**      | CrewAI/LangChain examples succeed when they pick "relatable complexity" — not toy, not enterprise. Webhook delivery is universally understood by API developers.  |
| **Developer UX**   | The "aha moment" comes from showing decisions developers already make badly. Delivery guarantees (at-least-once vs exactly-once) are a genuinely contested space. |
| **Skill coverage** | A workflow engine scored 9.5/10 on skill coverage, but exceeds the line budget. Webhook delivery scores 8.5/10 and fits in 300-500 lines.                         |
| **Contrarian**     | Avoid TODO apps, chatbots, generic REST APIs. The example must be something where multi-perspective analysis provides 10x value over single-perspective.          |

The agents converged on webhook delivery, rate limiter, and auth system as the top candidates — each for different reasons.

## Phase 2: Brainstorm — Push Past the Obvious

```
/brainstorm 10 What example project would best showcase all 10 multi-agent workflow skills?
```

The 7 ideas from diverge were logged as prior art (banned territory). Then 10 structurally unique ideas were generated:

| Rank | Idea                          | Score |
| ---- | ----------------------------- | ----- |
| 1    | API Contract Negotiator       | 12/15 |
| 2    | Auth System Designer          | 12/15 |
| 3    | Schema Migration Planner      | 11/15 |
| 4    | Incident Postmortem Simulator | 11/15 |
| 5    | Error Budget Allocator        | 10/15 |

The brainstorm surfaced ideas the diverge agents missed — particularly the API Contract Negotiator (constraint satisfaction across competing stakeholders) and Auth System Designer (RBAC vs ABAC vs ReBAC as genuinely different architectures).

## Phase 3: Converge — Structured Debate

```
/converge 3 "Rate Limiter vs Auth System vs Webhook Delivery"
```

Three advocates debated the top candidates:

**Rate Limiter advocate** argued: universal relatability, clean algorithmic divergence, self-contained prototype. Conceded: bisect is weak, scaffold has little to do, problem space is narrow.

**Auth System advocate** argued: highest stakes (every app needs auth), RBAC/ABAC/ReBAC are genuinely different architectures, premortem feels urgent. Conceded: bisect is weakest fit, 300-500 line budget is tight, crossbreed produces an obvious hybrid.

**Webhook Delivery advocate** argued: richest failure modes (retry storms, poison pills, DDoS-your-customer), natural bisect scenario, 5-6 components for scaffold. Conceded: external dependency hand-waving, less immediately interactive.

**Resolved consensus**: Webhook delivery edges ahead on failure richness and natural skill fit. Rate limiter is better as a quick-start tutorial. Auth system is a strong advanced example.

## Phase 4: Premortem — Risk Gate

```
/premortem 3 "Webhook Delivery System as flagship example"
```

Both finalists were risk-checked. The premortems surfaced nearly identical structural risks:

| Risk                                              | Severity | Mitigation                                           |
| ------------------------------------------------- | -------- | ---------------------------------------------------- |
| Domain complexity overshadows skill learning      | HIGH     | Add a simple warm-up covering 3-5 skills first       |
| Bisect feels contrived without organic regression | MEDIUM   | Show bisect separately with pre-seeded git history   |
| No immediate "aha" moment in 10-skill pipeline    | HIGH     | Create standalone single-skill demos                 |
| "Enterprise" framing repels individual developers | MEDIUM   | Frame as "learn the workflow" not "build the system" |

Key insight: these risks are structural — they apply to ANY complex example, not just these two. The mitigations (stopping points, standalone demos) apply universally.

**Decision: Webhook delivery system**, with the premortem mitigations incorporated.

## Phase 5: Diverge-Prototype — Three Competing Implementations

```
/diverge-prototype 3 "Webhook delivery system"
```

Three agents built working prototypes in parallel, each with a different architecture:

### Prototype A: Sync-First (255 lines)

```
POST /events → deliver to all subscribers inline → retry with backoff → 201 response
```

- Simplest possible approach — blocks until all deliveries complete
- Caller gets delivery status in the response (no polling)
- **Breaks when**: slow subscribers block all subsequent deliveries

### Prototype B: Queue-Based (341 lines)

```
POST /events → 202 Accepted → background worker polls queue → deliver with retries
```

- Decouples ingestion from delivery
- Circuit breaker (3 failures → 30s pause per subscriber)
- Dead letter queue for permanently failed deliveries
- **Breaks when**: in-memory queue lost on restart, no audit trail

### Prototype C: Event-Sourced (405 lines)

```
POST /events → append EventReceived → processor reads projected state → deliver → append result
```

- Every state change is an immutable event in an append-only log
- State derived by replaying events — never stored directly
- Full audit trail, replayable, debuggable
- **Breaks when**: O(n) projection cost grows with log size

All three are self-contained TypeScript, zero dependencies, runnable with `npx tsx server.ts`.

## Phase 6: Crossbreed — Hybrid Design

```
/crossbreed 2 webhook-prototype-b webhook-prototype-c
```

Two hybrid designs were produced, each with a different dominant parent:

**B-Dominant**: Queue drives decisions, event log runs in parallel for audit (fire-and-forget). Simpler, but log can't restore live state.

**C-Dominant**: Event log is the single source of truth. Priority queue is a materialized view rebuilt from the log. Circuit breaker transitions are also events. More architecturally clean — the queue is an index, not storage.

**Winner: C-Dominant hybrid.** The "event log as truth, queue as materialized view" pattern is the more architecturally interesting insight. It teaches developers CQRS-lite — a real pattern that applies broadly.

### Hybrid Architecture

```
POST /events → Event Store (append-only log) → Projection Engine → Priority Queue (view)
                                                                  → Circuit Breaker (view)
                                                                         ↓
                                                                  Delivery Worker (500ms poll)
                                                                         ↓
                                                                  append result events → log
```

### Lineage

| Element                                     | From B (Queue) | From C (Event-Sourced) |
| ------------------------------------------- | -------------- | ---------------------- |
| 202 Accepted, worker loop, circuit breaker  | Yes            |                        |
| Append-only event log, typed events, replay |                | Yes                    |
| Priority queue as materialized view         | Hybrid         | Hybrid                 |

## Phase 7: Scaffold — Build Order

```
/scaffold 3 "C-dominant hybrid webhook delivery"
```

Three competing build strategies:

| Strategy           | Phase 1                           | First Delivery | Total Phases |
| ------------------ | --------------------------------- | -------------- | ------------ |
| Riskiest-First     | Event store + replay (80L)        | Phase 4        | 5            |
| **Vertical Slice** | **Store + queue + worker (120L)** | **Phase 1**    | **4**        |
| Demo-able First    | HTTP API + store (120L)           | Phase 2        | 4            |

**Winner: Vertical Slice.** Gets a working end-to-end delivery in Phase 1, directly addressing the premortem risk of "no immediate aha moment."

### Build Plan

1. **Phase 1 (120L)**: Event store + priority queue + delivery worker. One subscriber, one event, one delivery. Prove the core data flow.
2. **Phase 2 (80L)**: Projection engine + subscriber registry. Formalize event-to-view pipeline. Multiple subscribers.
3. **Phase 3 (80L)**: Circuit breaker + exponential backoff. Failure handling flows through the same event pipeline.
4. **Phase 4 (120L)**: HTTP API + HMAC signing. Thin shell over proven internals.

## Pipeline Summary

| Phase | Skill                | Agents         | Output                                            |
| ----- | -------------------- | -------------- | ------------------------------------------------- |
| 1     | `/diverge`           | 4 parallel     | Research from 4 lenses → top candidates           |
| 2     | `/brainstorm`        | 1 (Python CLI) | 10 unique ideas beyond diverge findings           |
| 3     | `/converge`          | 3 parallel     | Structured debate → webhook delivery selected     |
| 4     | `/premortem`         | 2 parallel     | Risk-checked 2 finalists → mitigations identified |
| 5     | `/diverge-prototype` | 3 parallel     | 3 working prototypes (sync, queue, event-sourced) |
| 6     | `/crossbreed`        | 2 parallel     | 2 hybrid designs → C-dominant winner              |
| 7     | `/scaffold`          | 3 parallel     | 3 build plans → vertical slice selected           |

Total agents spawned: **20** across 7 phases. Each phase produced artifacts that fed the next, with genuine decisions at every step — not a predetermined path.

## What Each Skill Added

- **Diverge** found the candidates and surfaced non-obvious tradeoffs (Meta's FOQS needed randomization on dequeue paths)
- **Brainstorm** pushed past the obvious — the API Contract Negotiator and Auth System Designer were genuine surprises
- **Converge** forced steel-manning — the rate limiter advocate conceded bisect weakness, the webhook advocate conceded interactivity weakness
- **Premortem** caught structural risks that applied to ALL candidates (domain complexity overshadowing skill learning)
- **Diverge-prototype** produced 3 architecturally distinct working implementations, not variations on a theme
- **Crossbreed** synthesized a hybrid (event log + materialized queue view) that neither parent had alone
- **Scaffold** chose vertical slice specifically because the premortem flagged "no aha moment" as a risk

## Try It Yourself

The three prototypes are in this repo:

```bash
# Prototype A: Sync-first (simplest)
cd examples/webhook-prototype-a && npx tsx server.ts

# Prototype B: Queue-based (production-like)
cd examples/webhook-prototype-b && npx tsx server.ts

# Prototype C: Event-sourced (most auditable)
cd examples/webhook-prototype-c && npx tsx server.ts
```

Each runs on a different port (3000, 3001, 3003) with zero dependencies.
