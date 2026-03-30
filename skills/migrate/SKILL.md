Parallel Strategy for System Transitions. Spawns N independent agents in isolated worktrees, each implementing a DIFFERENT migration strategy for the same old-system-to-new-system transition. The path is the variable, not the destination — all agents implement the same end state but via different transition paths. Each agent prototypes the critical path (the riskiest step) of their strategy, not the full migration. A lead agent then synthesizes all strategies into a comparison across rollback safety, data integrity, downtime, and coordination cost.

## Arguments

$ARGUMENTS — format: `[N] [path/to/migration_plan.md or inline description of old → new]` where N is optional (default: 4, min 2, max 6)

## Parse Arguments

Extract:

- **agent_count**: optional leading integer (default 4, min 2, max 6)
- **migration_input**: a file path to a migration plan, design doc, or architecture doc — or an inline description of the old system and new system

If the migration input is missing or unclear, ask the user to clarify. At minimum you need: what is the old system, what is the new system, and what direction the migration goes.

## Phase 1: Understand the Migration

**If a file path is given**: read it and extract the migration context.

**If inline**: parse the description.

Prepare a **migration brief** that includes:

- **Old system** — what exists today, its architecture, data stores, interfaces
- **New system** — what the target state looks like
- **State to preserve** — data, configurations, user sessions, external contracts, SLAs that must survive the transition
- **Constraints** — downtime budget (zero? maintenance window?), team size, rollback requirements, compliance needs
- **Integration surface** — what external systems depend on the old system (APIs, message queues, cron jobs, downstream consumers)
- **Data characteristics** — volume, velocity, schema differences between old and new
- **Critical invariants** — things that must NEVER break during migration (e.g., "no duplicate transactions", "no lost orders", "auth must never be down")

Present the migration brief to the user and confirm before proceeding. Adjust if the user gives feedback.

## Phase 2: Spawn Migration Strategy Agents

Launch **all N agents in parallel** using the Agent tool. Each agent gets the same migration brief and a unique **migration strategy** drawn from this pool (assign strategies 1 through N):

1. **Big-Bang Cutover** — Prepare everything in the background, then switch all traffic from old to new in a single coordinated moment. Critical path: the cutover itself — the switchover procedure, the verification checks, and the rollback trigger.
2. **Strangler Fig** — Incrementally replace the old system piece by piece. New requests route to new code; old code handles legacy paths until nothing remains. Critical path: the routing layer that decides which system handles which request, and the first module migrated.
3. **Parallel Run** — Run both old and new systems simultaneously, feeding identical inputs to both and comparing outputs. Gain confidence before switching. Critical path: the comparison/reconciliation mechanism that detects divergence between old and new system outputs.
4. **Feature-Flag Progressive Rollout** — Deploy new system behind feature flags. Gradually increase the percentage of traffic routed to the new system. Critical path: the flag evaluation and traffic splitting logic, plus the per-user state management during partial rollout.
5. **Data-First-Then-Code** — Migrate data to the new schema/store first while old code still runs. Then swap the code layer to use the new data store. Critical path: the data synchronization layer that keeps old and new stores consistent during the transition period.
6. **Code-First-Then-Data** — Deploy new code that can read from both old and new data stores. Then migrate data incrementally while the new code adapts. Critical path: the dual-read abstraction layer and the incremental data migration pipeline.

Each agent MUST:

1. Use `isolation: "worktree"` — each gets its own copy of the repo
2. Use `subagent_type: "general-purpose"`
3. Receive the full migration brief plus their assigned strategy
4. Prototype the **critical path only** — the single riskiest step of their strategy, not the full migration
5. Create/modify actual files to implement the critical path prototype
6. Write a `MIGRATION_NOTES.md` in the repo root documenting:
   - Strategy name and description
   - What the critical path is and why it is the riskiest step
   - What was prototyped (the specific code/config implemented)
   - Rollback plan — how to undo this step if it goes wrong
   - Data integrity approach — how data consistency is maintained
   - Estimated downtime — for the critical path step specifically, and for the full strategy
   - Coordination requirements — what teams/people/systems need to be involved
   - Assumptions made during prototyping
   - Self-assessed confidence: [1-5] with rationale
7. Commit their work with a descriptive message
8. NOT implement the full migration — only the critical path

Agent prompt template (customize the strategy per agent):

```
You are a migration strategy agent. You prototype the critical path of a specific migration strategy.

## Migration Brief
{migration_brief}

## Your Strategy: {strategy_name}
{strategy_description}

## Critical Path
{critical_path_description}

## Instructions
1. Read the relevant existing code to understand the current system
2. Prototype ONLY the critical path of your strategy — the single riskiest step
3. Create/modify actual files to make the critical path concrete
4. Focus on proving feasibility and exposing risks, not on polish
5. Write MIGRATION_NOTES.md in the repo root with:
   - Strategy: {strategy_name}
   - Critical path: what it is and why it is the riskiest step
   - What was prototyped: the specific implementation
   - Rollback plan: how to undo this step if it goes wrong
   - Data integrity: how data consistency is maintained during this step
   - Estimated downtime: for this step, and for the full strategy
   - Coordination requirements: teams, people, systems involved
   - Assumptions: what you assumed that should be verified
   - Confidence: [1-5] with rationale
6. Stage and commit all changes with message: "migrate: {strategy_name} — critical path prototype"

Do NOT:
- Implement the full migration — only the critical path
- Over-engineer — this is a prototype to expose risk, not production code
- Ignore rollback — every step must be reversible
- Assume zero-downtime unless the migration brief explicitly allows it
- Gloss over data integrity — be explicit about how data stays consistent
```

## Phase 3: Compare Strategies

After ALL agents return, for each strategy:

1. Read the `MIGRATION_NOTES.md` from each worktree/branch
2. Run a quick diff summary (`git diff --stat` from base) to understand scope
3. Evaluate the critical path prototype for feasibility

Produce a unified analysis:

### 1. Strategy Comparison Table

| Dimension                       | Strategy A                 | Strategy B | Strategy C | Strategy D |
| ------------------------------- | -------------------------- | ---------- | ---------- | ---------- |
| Critical path prototyped        | ...                        | ...        | ...        | ...        |
| Rollback safety                 | [Safe / Risky / Dangerous] | ...        | ...        | ...        |
| Data integrity risk             | [Low / Medium / High]      | ...        | ...        | ...        |
| Estimated downtime              | ...                        | ...        | ...        | ...        |
| Team coordination cost          | [Low / Medium / High]      | ...        | ...        | ...        |
| Implementation complexity       | [Low / Medium / High]      | ...        | ...        | ...        |
| Time to complete full migration | ...                        | ...        | ...        | ...        |
| Confidence score                | [1-5]                      | ...        | ...        | ...        |
| Files changed                   | ...                        | ...        | ...        | ...        |

### 2. Risk Heat Map

For each strategy, rate the following risks on a [Low / Medium / High / Critical] scale:

- Data loss during migration
- Extended downtime
- Partial failure (stuck between old and new)
- Rollback failure (cannot revert)
- Performance degradation during transition
- External system disruption

### 3. Trade-off Analysis

For each major trade-off, articulate where each strategy falls:

- **Speed vs. Safety** — faster migration vs. more verification steps
- **Complexity vs. Rollback** — simpler approach vs. easier to undo
- **Downtime vs. Risk** — accept a maintenance window vs. live migration risk
- **Team load vs. Duration** — intense burst vs. gradual effort over time

### 4. Cross-Strategy Insights

Where did multiple strategies face the same challenge? These are inherent migration risks regardless of strategy. For each:

- What the shared challenge is
- Which strategies handle it best
- What it implies about the migration's fundamental difficulty

### 5. Recommended Strategy

Based on the comparison:

- Which strategy (or combination) best fits the constraints in the migration brief?
- What are the top 3 risks to monitor regardless of chosen strategy?
- What preparatory work is needed before starting the chosen strategy?

Save the full analysis to `migrate_{slugified_topic}.md` in the working directory.

## Phase 4: Present and Next Steps

Present the comparison table, risk heat map, and recommended strategy to the user. Then suggest:

1. **Stress-test the chosen strategy** — run `/stress-test` against the recommended approach to find edge cases
2. **Build the full migration plan** — run `/scaffold` to plan the implementation sequence for the chosen strategy
3. **Premortem the migration** — run `/premortem` to explore failure modes specific to the chosen strategy
4. **Iterate** — refine the migration brief and run another round with different strategies or constraints
5. **Deep-dive** — examine a specific strategy's worktree in detail

Remind the user: all worktrees are preserved for comparison. They can inspect any strategy's prototype directly.

## Rules

- **Independence is critical**: agents must NOT share context. Each strategy agent explores independently. Do not include other agents' strategies in any agent's prompt.
- **All agents launch in a single parallel batch**: use one message with N Agent tool calls.
- **Worktree isolation is mandatory**: every migration strategy agent MUST use `isolation: "worktree"`. Migration prototypes must not interfere with each other or the main branch.
- **Critical path only**: agents prototype the single riskiest step of their strategy, not the full migration. The goal is to expose risk and prove feasibility, not to complete the migration.
- **Honest about trade-offs**: no strategy is universally best. Every strategy has downsides. Agents must articulate trade-offs, not sell their approach.
- **Preserve all worktrees**: even strategies that seem inferior contain insights about risk. Never discard or clean up worktrees without user confirmation.
- **Data integrity is non-negotiable**: every strategy must explicitly address how data consistency is maintained. "We'll figure it out later" is not acceptable.
- **Rollback is mandatory**: every critical path prototype must include a rollback plan. If a strategy cannot be rolled back, that is a critical finding, not an omission.
- **Attribute insights**: when the recommended strategy borrows ideas from other strategies (e.g., "use Parallel Run's comparison mechanism during Big-Bang Cutover's verification"), name the source.
- **The path is the variable**: all agents implement the same end state. The strategies differ only in how they get there. If an agent starts redesigning the destination, redirect it.

## Pipeline Position

Sits after architecture decision and before implementation:

```
/converge or architecture decision -> /migrate (compare transition strategies) -> /stress-test (validate chosen strategy) -> /scaffold (plan build order)
```
