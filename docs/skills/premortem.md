# Premortem

Prospective failure narratives. Spawns N independent agents, each writing a story from 6 months in the future where the project FAILED for a different root cause. Synthesizes all failure narratives into a structured risk registry.

Based on Gary Klein's premortem technique: imagining an event has already occurred increases the ability to identify reasons for future outcomes by approximately 30%.

## When to Use

- Before implementing any architecture change touching more than 3 files
- Before any design that will be hard to reverse (database schema, public API, auth system)
- When you want to stress-test a plan for risks that optimism bias normally hides

## Usage

```
/premortem [N] [path/to/design.md or inline description]
```

**Examples:**

```
/premortem prd_realtime_collab.md
/premortem 7 "Migration from PostgreSQL to CockroachDB for our payments service"
```

N sets the failure-lens count (default: 5, range: 3-7).

## How It Works

1. **Frame** -- Extract key decisions, dependencies, assumptions, and constraints from the project input.
2. **Spawn** -- Launch N agents in parallel, each assigned a unique failure lens (technical architecture, integration, operational, scope, team/process, security, scale). Each writes a prose narrative of how and why the project failed.
3. **Synthesize** -- Build a risk registry table (severity x likelihood), identify cross-cutting themes, prioritize mitigations, and recommend design modifications.

## Output

- A risk registry and full failure narratives saved to `premortem_<slugified_topic>.md`

## Pipeline Connections

- **Before:** `/converge` for decision-making, `/diverge` for research
- **After:** `/diverge-prototype` for building, `/stress-test` for deeper adversarial analysis

## Tips

- The narrative format (prose stories, not bullet lists) is intentional -- it triggers deeper causal reasoning. Do not ask for bullet-point risks instead.
- Pay special attention to cross-cutting themes: when multiple independent failure lenses identify the same vulnerability, that is a very high-confidence risk signal.
