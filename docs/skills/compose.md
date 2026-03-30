# Compose

Meta-workflow that designs which skills to chain for a given goal. The only skill that operates on the workflow layer rather than the problem layer. Spawns agents to propose different pipeline compositions optimized for different stances (speed, risk, thoroughness, creativity, simplicity).

## When to Use

- You have a complex goal and are unsure which skills to run in what order
- You want to compare workflow strategies (fast vs. thorough, safe vs. creative) before committing
- A project needs re-planning mid-stream and you want a fresh pipeline design

## Usage

```
/compose [N] "goal description"
```

**Examples:**

```
/compose "Design and build a real-time notification system"
/compose 4 "Migrate our monolith auth service to microservices"
```

N sets the pipeline-proposal count (default: 3, range: 2-5).

## How It Works

1. **Analyze Goal** -- Classify the goal along five dimensions: novelty, urgency, risk level, team size, and reversibility.
2. **Spawn** -- Launch N agents, each with a unique optimization stance (speed-optimized, risk-optimized, thoroughness-optimized, creativity-optimized, simplicity-optimized). Each designs a complete pipeline using only skills from the 18-skill catalog.
3. **Compare** -- Identify consensus skills (appear in all pipelines), contested skills (some include, some exclude), and unique skills (one pipeline only).
4. **Recommend** -- Synthesize a recommended pipeline with rationale for each step, confidence level, and alternative paths.

## Output

- A pipeline comparison and recommendation saved to `compose_<slugified_topic>.md`

## Pipeline Connections

- **Before:** Start of any non-trivial project, or mid-project when remaining work needs re-planning
- **After:** Execute the recommended pipeline by invoking the first skill

## Tips

- Compose can reference itself recursively if a sub-goal is complex enough to warrant its own pipeline design.
- The recommended pipeline is a starting point, not a commitment. Skills can be added, removed, or reordered as work progresses and new information surfaces.
