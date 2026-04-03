# PRD Build

Automated PRD-to-implementation orchestrator. Decomposes a PRD into dependency-ordered work units, dispatches parallel agents in isolated worktrees to implement and review each unit, and merges passing work onto an integration branch.

## When to Use

- You have a finalized PRD and want to implement it with parallel agents
- The project has multiple independent components that can be built concurrently
- You want automated implement-review loops with verifiable acceptance criteria
- You want to go from PRD to working code without manual orchestration

## Usage

```
/prd-build <path/to/prd.md> [--max-passes N] [--max-parallel N] [--dry-run]
```

**Examples:**

```
/prd-build prd_auth_redesign.md
/prd-build prd_notifications.md --max-parallel 3 --dry-run
/prd-build prd_api_v2.md --max-passes 5
```

## How It Works

1. **Decompose** -- Read the PRD and break it into 5-10 work units with verifiable acceptance criteria. Organize into dependency layers.
2. **Execute** -- For each layer, dispatch parallel agents in isolated worktrees to implement. Each agent receives only its unit description, scoped files, and acceptance criteria. After implementation, separate review agents verify each criterion.
3. **Land** -- Merge passing units onto the integration branch via rebase. If merge fails, evict with context for retry.
4. **Verify** -- After all layers, run the full test suite. Retry evicted units up to max_passes. Report final status.

## Key Concepts

**Work unit tiers** determine the agent pipeline:

- **Trivial** (<30 lines): implement + test
- **Small** (single-file): implement + test + self-review
- **Medium** (multi-file): research + plan + implement + test + review
- **Large** (cross-cutting): medium + separate reviewer agent

**Implement-Review loop**: Every unit is reviewed by a separate agent that did NOT write the code. If review fails, the implement agent gets feedback and retries (max 3 rounds).

**Layers**: Units are organized by dependency. Layer 0 units have no dependencies and run in parallel. Layer N units depend only on layers < N.

## Output

- Implemented code on an integration branch
- Work plan and artifacts in `.claude/prd-build-artifacts/`
- Final summary: units landed/total, passes used, integration branch name

## Companion Commands

- `/prd-build-status` -- Show current progress (layers, units, merge queue)
- `/prd-build-cancel` -- Pause or cancel an active run
- `/prd-build-resume` -- Resume from where a previous run left off

## Pipeline Connections

- **Before:** `/research-project` to produce a risk-annotated PRD, or `/scaffold` for build-order planning
- **After:** Manual review of the integration branch and merge to main

## Tips

- Use `--dry-run` first to review the decomposition before committing to execution.
- Keep PRD acceptance criteria specific and testable — vague criteria lead to vague implementations.
- For projects where build order matters more than parallelism, use `/scaffold` then `/focus` instead.
