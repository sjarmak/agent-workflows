# Change Impact Workflow

Diffuse-to-stress-test change assessment. Use this when you need to understand the full blast radius of a proposed change and validate that the change plan is safe.

## When to Use This Workflow

- A dependency, schema, API, or core module is about to change
- You need to assess risk before a large refactoring
- A change affects multiple teams or services and you need a comprehensive impact map

## The Pipeline

```
/diffuse -> /stress-test -> /scaffold -> implement change
```

## Step-by-Step

1. **`/diffuse`** -- Map the blast radius of the proposed change across all dimensions: code references, data flow, test coverage, deployment, and user experience. Output: impact heat map and dependency chain.

2. **`/stress-test`** -- Attack the change plan itself. What happens if the migration fails halfway? What edge cases does the change introduce? Output: vulnerability map for the change.

3. **`/scaffold`** -- Plan the implementation order using the dependency chain from diffuse and the risk findings from stress-test. Output: safe change sequence with rollback points.

4. **Implement Change** -- Follow the scaffold plan, verifying each phase before proceeding to the next.

## Example Invocation

```
/diffuse "Rename User.email to User.primary_email across the codebase"
/stress-test diffuse_email_rename.md
/scaffold diffuse_email_rename.md
```

## Tips

- For small, well-understood changes, `/diffuse` alone may be sufficient. Add `/stress-test` only when the blast radius is large or the change is hard to reverse.
- The dependency chain from `/diffuse` tells you the safe order: change leaves first, then work inward toward the most-depended-on components.
