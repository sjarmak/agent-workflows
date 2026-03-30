# Fracture

Competitive problem decomposition. Spawns N agents, each proposing a different decomposition of the same problem using a distinct structural lens (user journey, data flow, failure domain, team boundary, deployment unit, API surface, temporal lifecycle).

## When to Use

- You have a large or ambiguous problem and need to decide how to frame it before solving it
- Different stakeholders see the problem differently and you want to surface those structural assumptions
- You want to discover blind spots that any single decomposition would hide

## Usage

```
/fracture [N] [path/to/problem.md or inline description]
```

**Examples:**

```
/fracture "Build a multi-tenant SaaS billing system"
/fracture 5 prd_notification_platform.md
```

N sets the decomposition-lens count (default: 5, range: 3-7).

## How It Works

1. **Frame** -- Prepare a problem brief with goals, stakeholders, constraints, and success criteria.
2. **Spawn** -- Launch N agents in parallel, each with a unique decomposition lens. Each produces a 2-3 level decomposition tree, dependency map, and analysis of what their framing makes easy vs. hard.
3. **Synthesize** -- Build a comparison table, identify convergence points (subproblems that appear across multiple lenses), unique insights, a blind spot matrix, and a recommended decomposition (single lens, hybrid, or layered).

## Output

- A decomposition comparison and recommendation saved to `fracture_<slugified_topic>.md`

## Pipeline Connections

- **Before:** `/brainstorm` for initial ideation, `/distill` for large artifacts needing decomposition
- **After:** `/diverge` to explore solutions within the chosen decomposition, `/premortem` if the framing reveals architectural risk

## Tips

- Convergence points (subproblems that appear across multiple lenses under different names) are structurally fundamental -- they should appear in any implementation plan regardless of framing.
- The blind spot matrix is particularly useful: it shows which concerns require combining lenses to cover.
