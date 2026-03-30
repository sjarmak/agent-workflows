# Diffuse

Blast radius impact mapping. Takes a proposed change and traces its impact through call graphs, data flows, tests, deployment, and user experience. Spawns N agents to independently map impact from different dimensions, then synthesizes into a comprehensive change assessment.

## When to Use

- You are planning a change and need to understand its full blast radius before proceeding
- A dependency, schema, or API is about to change and you want to know what downstream systems are affected
- You need to assess the risk of a refactoring or migration before committing

## Usage

```
/diffuse [N] [path/to/change_description or inline description]
```

**Examples:**

```
/diffuse "Rename the User model's email field to primary_email"
/diffuse 5 "Upgrade React from v18 to v19 across the monorepo"
```

N sets the agent count (default: 5, range: 3-7).

## How It Works

1. **Identify Change** -- Parse the proposed change and build a change brief covering what is changing, why, and the initial scope.
2. **Spawn** -- Launch N agents in parallel, each tracing impact through a different dimension: call graph/code references, data flow/schema, test coverage, deployment/infrastructure, and user experience/API surface.
3. **Synthesize** -- Produce an impact heat map (which components are affected by multiple dimensions), a dependency chain (ordered list of what must change), and a risk-ranked change plan.

## Output

- An impact map and change plan saved to `diffuse_<slugified_topic>.md`

## Pipeline Connections

- **Before:** Any proposed change, refactoring, or migration
- **After:** `/stress-test` to validate the change plan, `/scaffold` to sequence the implementation

## Tips

- Components that appear across 3+ impact dimensions are the riskiest parts of the change -- they need the most careful testing and review.
- Use the dependency chain output to determine the safe order of changes: start from the leaves and work inward.
