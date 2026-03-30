# Diverge Prototype

Divergent prototyping. Spawns N independent agents in isolated git worktrees to explore different implementation approaches for a PRD, then synthesizes results into a comparison.

## When to Use

- You have a PRD or clear requirements and want to explore multiple implementation strategies before committing
- The trade-off space is large (simplicity vs. flexibility, speed vs. correctness) and you want concrete prototypes to compare
- You want to discover emergent properties that only appear when you actually build something

## Usage

```
/diverge-prototype [N] [path/to/prd.md]
```

**Examples:**

```
/diverge-prototype prd_caching_layer.md
/diverge-prototype 4 prd_notification_system.md
```

N sets the agent count (default: 3, range: 2-7). A PRD is required -- the skill will help create one if none exists.

## How It Works

1. **Validate PRD** -- Read and validate the PRD. If none provided, offer to run `/diverge` or draft one interactively.
2. **Design Strategies** -- Create N distinct implementation strategies (e.g., minimal viable, framework-heavy, performance-first, extensibility-first). User confirms before spawning.
3. **Spawn** -- Launch all agents in parallel, each in an isolated worktree with their assigned strategy. Agents create real files and commit working prototypes.
4. **Compare** -- Read each agent's `PROTOTYPE_NOTES.md`, run diff stats, and build a comparison matrix covering approach, complexity, requirements met, and production readiness.

## Output

- N prototype branches in git worktrees
- A comparison matrix and recommended path forward presented inline

## Pipeline Connections

- **Before:** `/diverge` + `/converge` for research and decisions, `/premortem` for risk assessment
- **After:** `/crossbreed` to combine best elements, `/stress-test` to validate, `/scaffold` to plan the build

## Tips

- Each prototype agent creates a `PROTOTYPE_NOTES.md` with self-assessed quality and effort-to-production estimates. Read these before deciding.
- Even "failed" prototypes contain insights. Always extract learnings from every approach before discarding.
