# Replicate

Independent verification by reimplementation. Spawns N agents in isolated worktrees to implement the SAME specification independently, with no knowledge of each other's code. Compares outputs to produce a convergence/divergence map that reveals spec quality.

## When to Use

- You want to verify that a specification is clear and complete enough to hand off for implementation
- You have written a spec and want to find its ambiguities before anyone starts building
- You need to assess whether a contract or API definition is sufficiently precise

## Usage

```
/replicate [N] [path/to/spec.md or inline specification]
```

**Examples:**

```
/replicate spec_user_api.md
/replicate 4 "A function that takes a list of transactions and returns the running balance after each one"
```

N sets the agent count (default: 3, range: 2-5).

## How It Works

1. **Frame** -- Present the spec as-is. Deliberately do NOT fill in gaps or resolve ambiguities -- agents must encounter them naturally.
2. **Spawn** -- Launch N agents in parallel with identical instructions. No strategy differentiation. Each implements the spec and documents every assumption, ambiguity, and decision in `IMPLEMENTATION_NOTES.md`.
3. **Compare** -- Build convergence map (agents agreed = spec is clear), divergence map (agents disagreed = spec is ambiguous), and spec gap report (what agents wished the spec had said).
4. **Score** -- Rate spec quality by convergence rate: Clear (>80%), Mostly Clear (60-80%), Ambiguous (40-60%), Underspecified (<40%).

## Output

- A spec quality report with convergence/divergence maps saved to `replicate_<slugified_topic>.md`
- N implementation branches in git worktrees

## Pipeline Connections

- **Before:** `/contract` to generate a spec from examples, `/converge` to refine a spec
- **After:** Revise the spec and re-run `/replicate`, or proceed to `/diverge-prototype` with confidence

## Tips

- The divergence map is the primary output, not the code. Where agents diverge, the spec has gaps. This is the skill's core value.
- Unlike `/diverge-prototype`, agents receive NO strategy differentiation. All divergence must emerge naturally from spec ambiguity.
