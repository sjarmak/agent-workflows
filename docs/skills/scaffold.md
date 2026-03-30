# Scaffold

Build-order planning via competing sequencing strategies. Takes a chosen design and spawns N independent agents, each proposing a different build-order strategy with milestones, dependencies, and risk assessment.

## When to Use

- You have a design or architecture decision and need to plan the implementation sequence
- The build has enough components that sequencing matters (wrong order leads to wasted work or blocked teams)
- You want to compare strategies like "riskiest first" vs. "demo-able first" vs. "vertical slice"

## Usage

```
/scaffold [N] [path/to/design.md or inline description]
```

**Examples:**

```
/scaffold chosen_prototype/PROTOTYPE_NOTES.md
/scaffold 5 "Build a notification system with email, push, and in-app channels"
```

N sets the strategy count (default: 4, range: 2-6).

## How It Works

1. **Understand** -- Extract components, dependencies, integrations, testing needs, and deployment requirements from the design.
2. **Spawn** -- Launch N agents, each with a unique sequencing strategy: riskiest-first, demo-able first, dependency-topological, vertical slice, test infrastructure first, or parallel tracks.
3. **Compare** -- Build a comparison table covering first thing built, time to demo, risk front-loading, parallelism potential, and integration risk.
4. **Recommend** -- Synthesize a recommended build plan combining the best insights from all strategies.

## Output

- A build plan and comparison analysis saved to `scaffold_<slugified_topic>.md`

## Pipeline Connections

- **Before:** `/diverge-prototype` or `/crossbreed` for choosing a design, `/stress-test` for validation
- **After:** Begin implementation following the recommended phase sequence

## Tips

- Plans change. The value is not predicting the future perfectly but having thought through the trade-offs so you can adapt faster when reality diverges.
- If three or more strategies put the same component early, that is a strong signal -- build it first.
