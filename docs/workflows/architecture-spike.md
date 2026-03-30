# Architecture Spike Workflow

Prototype, stress-test, and scaffold path for technical exploration. Use this when you need to validate a technical approach by building it and attacking it before committing.

## When to Use This Workflow

- Technical feasibility is the primary risk (will this approach actually work?)
- You need proof-of-concept code, not just analysis
- The architecture decision depends on emergent properties that only appear when you build

## The Pipeline

```
/diverge-prototype -> /stress-test -> /scaffold -> build
```

## Step-by-Step

1. **`/diverge-prototype`** -- Build N parallel prototypes exploring different implementation strategies. Each runs in an isolated worktree. Output: working prototypes with comparison matrix.

2. **`/stress-test`** -- Attack the most promising prototype(s) from multiple adversarial angles. Identify vulnerabilities in edge cases, scale, security, and concurrency. Output: vulnerability map.

3. **`/scaffold`** -- Plan the build order for the chosen approach, informed by what the stress test revealed. Output: sequenced build plan with milestones.

4. **Build** -- Implement following the scaffold plan, addressing stress-test findings as you go.

## Example Invocation

```
/diverge-prototype 3 prd_caching_layer.md
/stress-test prototype-branch-a/
/scaffold prototype-branch-a/PROTOTYPE_NOTES.md
```

## Tips

- Insert `/crossbreed` between prototype and stress-test if two prototypes each solve different parts of the problem well.
- If the stress-test reveals critical issues in all prototypes, go back to `/diverge-prototype` with updated constraints rather than pushing forward.
