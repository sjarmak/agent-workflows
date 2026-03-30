# Migration Planning Workflow

Migrate-to-scaffold path for system transitions. Use this when moving between databases, frameworks, architectures, or platforms where the transition strategy matters as much as the destination.

## When to Use This Workflow

- Database migrations (e.g., MongoDB to PostgreSQL)
- Framework or platform transitions (e.g., monolith to microservices)
- Any migration where downtime, data integrity, and rollback capability are critical concerns

## The Pipeline

```
/diffuse -> /migrate -> /stress-test -> /scaffold -> execute migration
```

## Step-by-Step

1. **`/diffuse`** -- Map the full impact of the migration across code, data, tests, deployment, and UX. Understand what is affected before planning how to move. Output: impact map.

2. **`/migrate`** -- Explore different migration strategies in parallel (big-bang cutover, strangler fig, parallel run, feature-flag progressive rollout, data-first-then-code, code-first-then-data). Each agent produces a step-by-step plan with rollback strategy and risk assessment. Output: strategy comparison with recommendation.

3. **`/stress-test`** -- Attack the recommended migration strategy. What if it fails at step 3? What if data volumes are 10x what you estimated? What about the rollback path? Output: vulnerability map for the migration plan.

4. **`/scaffold`** -- Plan the detailed build order for the migration, incorporating stress-test findings. Output: sequenced migration plan with verification checkpoints.

5. **Execute Migration** -- Follow the scaffold plan phase by phase, verifying at each checkpoint.

## Example Invocation

```
/diffuse "Migrate orders service from MongoDB to PostgreSQL"
/migrate "Move from MongoDB to PostgreSQL for the orders service"
/stress-test migrate_orders_postgresql.md
/scaffold migrate_orders_postgresql.md
```

## Tips

- Never skip the `/diffuse` step for migrations. Understanding the blast radius before planning the transition prevents discovering dependencies mid-migration.
- If `/stress-test` reveals that the rollback path for the recommended strategy is weak, reconsider a more conservative migration approach even if it takes longer.
