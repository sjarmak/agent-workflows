# Migrate

Parallel migration strategy exploration. Spawns N agents to independently prototype different transition paths for moving from one system state to another. Each agent explores a different migration approach (big-bang cutover, strangler fig, parallel run, feature-flag progressive rollout, data-first-then-code, code-first-then-data).

## When to Use

- You are migrating between databases, frameworks, architectures, or platforms
- The migration has enough complexity that the transition strategy matters as much as the destination
- You want to compare approaches like big-bang cutover vs. strangler fig vs. parallel run vs. feature-flag rollout

## Usage

```
/migrate [N] [path/to/migration_brief.md or inline description]
```

**Examples:**

```
/migrate "Move from MongoDB to PostgreSQL for the orders service"
/migrate 5 "Migrate the monolith auth module into a standalone microservice"
```

N sets the strategy agent count (default: 4, range: 2-6).

## How It Works

1. **Frame** -- Analyze the current state, target state, data volumes, downtime tolerance, rollback requirements, and team constraints.
2. **Spawn** -- Launch N agents in parallel, each exploring a different migration strategy. Each produces a step-by-step migration plan, rollback strategy, risk assessment, and estimated timeline.
3. **Compare** -- Build a comparison matrix covering downtime, data risk, rollback capability, team effort, and timeline.
4. **Recommend** -- Synthesize a recommended migration path with rationale and contingency plans.

## Output

- A migration strategy comparison and recommendation saved to `migrate_<slugified_topic>.md`

## Pipeline Connections

- **Before:** `/diffuse` to understand the blast radius of the migration
- **After:** `/stress-test` to validate the chosen strategy, `/scaffold` to plan the build order

## Tips

- Pay close attention to rollback strategies in each approach. The ability to undo a migration safely is often more important than the migration speed.
- If agents converge on the same strategy from different starting points, that is a strong signal it is the right approach for your constraints.
