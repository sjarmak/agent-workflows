# Quick Decision Workflow

Fast converge-to-build path for time-sensitive decisions. Use this when you have competing approaches and need to pick a direction quickly without full pipeline overhead.

## When to Use This Workflow

- Time-sensitive decisions where speed matters more than exhaustive exploration
- The options are already known and you need structured evaluation, not more research
- Low-to-medium risk decisions where the cost of being wrong is manageable

## The Pipeline

```
/converge -> /premortem -> build
```

## Step-by-Step

1. **`/converge`** -- Frame the competing approaches as debate positions. Run 2-3 rounds of structured debate to surface trade-offs and reach a recommendation. Output: convergence report with recommended path.

2. **`/premortem`** -- Quick risk check on the chosen approach. Use 3 agents (minimum) with the most relevant failure lenses for your context. Output: risk registry. If no critical risks surface, proceed to build.

3. **Build** -- Implement the chosen approach. Use the premortem mitigations as a checklist during implementation.

## Example Invocation

```
/converge 3 "REST vs GraphQL for our internal service mesh"
/premortem 3 "GraphQL internal API with schema federation"
```

## Tips

- Skip `/premortem` entirely for truly low-risk decisions (e.g., library choice for a non-critical utility). Go straight from `/converge` to build.
- If the converge debate surfaces deep uncertainty, escalate to the full pipeline rather than forcing a premature decision.
