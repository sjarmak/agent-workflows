# Full Pipeline Workflow

The complete diverge-to-scaffold pipeline for new features. Use this when building something non-trivial from scratch where you want thorough exploration, risk assessment, and build planning before writing production code.

## When to Use This Workflow

- New feature development with significant architectural decisions
- Greenfield projects where the solution space is large
- Any work where getting the design wrong would be expensive to fix

## The Pipeline

```
/brainstorm -> /diverge -> /converge -> /premortem -> /diverge-prototype -> /stress-test -> /scaffold -> build
```

## Step-by-Step

1. **`/brainstorm`** -- Generate a wide set of structurally distinct ideas. Push past the obvious first approaches. Output: ranked idea list with prototypes.

2. **`/diverge`** -- Take the top ideas and research them from multiple independent perspectives (prior art, first-principles, UX, failure modes, scale). Output: unified synthesis and draft PRD.

3. **`/converge`** -- Debate the competing approaches from the diverge output. Resolve tensions, refine trade-offs, and commit to a direction. Output: convergence report, updated PRD.

4. **`/premortem`** -- Imagine the project has failed. Independent agents write failure narratives from different lenses (technical, operational, security, scope). Output: risk registry with prioritized mitigations.

5. **`/diverge-prototype`** -- Build N parallel prototypes in isolated worktrees, each taking a different implementation strategy. Output: working prototypes with comparison matrix.

6. **`/stress-test`** -- Attack the chosen prototype from multiple adversarial angles (edge cases, scale, security, concurrency). Output: vulnerability map with prioritized fixes.

7. **`/scaffold`** -- Plan the build order with competing sequencing strategies (riskiest-first, demo-able first, vertical slice). Output: recommended build plan.

8. **Build** -- Implement following the scaffold plan.

## Example Invocation

```
/brainstorm 15 How to implement real-time collaboration for our editor
/diverge prd_realtime_collab.md
/converge diverge_realtime_collab.md
/premortem prd_realtime_collab.md
/diverge-prototype prd_realtime_collab.md
/stress-test src/collab/
/scaffold chosen_prototype/PROTOTYPE_NOTES.md
```

## Tips

- You can skip `/brainstorm` if the problem space is already well-understood and jump straight to `/diverge`.
- Insert `/crossbreed` between `/diverge-prototype` and `/stress-test` if multiple prototypes each have compelling elements worth combining.
- The pipeline is not rigid. Drop steps that do not add value for your specific situation, or use `/compose` to design a custom pipeline.
