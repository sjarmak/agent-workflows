# Bisect

Binary search for root cause. Defines a search space and pass/fail oracle, then iteratively tests midpoints -- halving the space each step until the root cause is isolated.

## When to Use

- A regression was introduced and you have a known-good state and a known-bad state
- You need to find which commit, config change, or dependency upgrade broke something
- The search space is large enough that linear scanning would be impractical

## Usage

```
/bisect "description of the bug or regression"
```

**Examples:**

```
/bisect "Login endpoint returns 500 since last deploy"
/bisect "Test suite takes 3x longer than it did two weeks ago"
```

## How It Works

1. **Define Search Space** -- Establish the symptom, search dimension (git history, config, dependencies, or code modules), test oracle (how to check pass/fail), and known bounds.
2. **Binary Search Loop** -- Iteratively test midpoints. Each step spawns an agent in an isolated worktree to run the oracle and report PASS or FAIL. The space halves each iteration.
3. **Root Cause** -- Once narrowed to a single item, analyze the change and explain why it caused the failure.
4. **Report** -- Present the bisect log, analysis, and ranked fix options (immediate revert, proper patch, long-term redesign).

Supports git history bisect, configuration bisect, and dependency version bisect.

## Output

- A root cause report with bisect log, analysis, and fix options presented inline

## Pipeline Connections

- **Before:** A regression or bug report triggers the bisect
- **After:** Apply the fix, then optionally run `/stress-test` to verify no related issues

## Tips

- The test oracle must be deterministic. If tests are flaky, bisect cannot distinguish real failures from noise -- address flakiness first.
- For git bisects, the skill uses isolated worktrees and cleans up after each step. The main working tree is never modified.
