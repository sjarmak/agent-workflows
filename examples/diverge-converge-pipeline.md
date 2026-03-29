# Example: The Diverge-Converge Pipeline

This walkthrough shows how the four workflow skills chain together to go from "vague idea" to "informed implementation" — with multi-agent research, structured debate, and parallel prototyping along the way.

## Scenario

You're building a caching layer for a multi-service backend. You're not sure whether to use Redis, an in-process cache, a CDN-based approach, or something else. The requirements are fuzzy and the trade-offs are real.

## Step 1: Research with `/diverge`

Start by exploring the problem space from multiple angles:

```
/diverge 4 "What caching architecture should we use for a multi-service backend with mixed read/write patterns, 50ms p99 latency target, and eventual consistency tolerance?"
```

What happens:
- Claude frames a research brief and asks you to confirm
- 4 independent agents launch in parallel, each with a different lens:
  - **Prior art**: surveys existing caching patterns (write-through, write-behind, read-aside, etc.)
  - **Technical design**: analyzes the specific constraints (50ms p99, eventual consistency)
  - **Failure modes**: explores what breaks — cache stampedes, invalidation bugs, cold start
  - **Scale & evolution**: considers how this grows as services multiply
- After all 4 return, Claude synthesizes findings and drafts a PRD

**Output**: `prd_caching_architecture.md` with requirements, trade-offs, and open questions.

## Step 2: Debate with `/converge`

The `/diverge` synthesis revealed tensions — the "prior art" agent recommended Redis, the "failure modes" agent flagged single-point-of-failure risks, and the "scale" agent suggested a tiered approach. Time to debate:

```
/converge 3 prd_caching_architecture.md
```

What happens:
- Claude extracts the key tensions from the PRD
- 3 teammates are assigned positions:
  - **Centralized cache (Redis)**: argues for simplicity, proven tooling
  - **Distributed/tiered cache**: argues for resilience, locality
  - **Hybrid approach**: argues for layered caching with fallbacks
- 2-3 rounds of structured debate with steel-manning and concessions
- Claude moderates and produces a convergence report

**Output**: Resolved consensus points, refined trade-offs, and a recommended direction (e.g., "tiered: in-process L1 + Redis L2, with circuit breaker on Redis failures").

## Step 3: Prototype with `/diverge-prototype`

Now build it multiple ways and see what the code actually looks like:

```
/diverge-prototype 3 prd_caching_architecture.md
```

What happens:
- Claude designs 3 implementation strategies based on the (now-refined) PRD:
  - **Minimal**: simple Redis wrapper, ~100 lines
  - **Tiered**: in-process LRU + Redis with fallback, ~300 lines
  - **Event-driven**: pub/sub invalidation with local caches, ~400 lines
- You confirm the strategies
- 3 agents launch in isolated git worktrees, each building a real prototype
- After all return, Claude compares: files changed, requirements met, trade-offs encountered

**Output**: comparison matrix, per-prototype highlights, recommended path forward.

## Step 4: Pick and Ship

Claude presents the comparison and asks how you want to proceed:
1. **Adopt one** — merge the best prototype's branch
2. **Cherry-pick** — combine the tiered prototype's fallback logic with the event-driven prototype's invalidation
3. **Iterate** — refine the PRD and run another round
4. **Park it** — save learnings for later

## Why This Works

Each step adds signal that the previous step couldn't:

| Step | What it adds |
|------|-------------|
| `/diverge` | Breadth — surfaces options and trade-offs you wouldn't find alone |
| `/converge` | Depth — stress-tests each option through adversarial debate |
| `/diverge-prototype` | Reality — reveals what the code actually looks like, not just what it sounds like |

The pipeline is also flexible — you can enter at any point:
- Already know the options? Skip `/diverge`, go straight to `/converge`
- Already have a PRD? Skip to `/diverge-prototype`
- Just need ideas? Use `/brainstorm` standalone

## Cost Awareness

This pipeline spawns many agents. Rough token usage:
- `/diverge` with 4 agents: ~40-80k tokens
- `/converge` with 3 debaters x 3 rounds: ~30-60k tokens
- `/diverge-prototype` with 3 agents: ~60-120k tokens (these write code)

Use fewer agents (2 instead of 4) for smaller decisions. The pipeline is most valuable for decisions that are expensive to reverse — architecture choices, API contracts, data model design.
