---
name: prd-build
description: "Decompose a PRD into parallel work units and build them with independent agents"
argument-hint: "<path/to/prd.md> [--max-passes N] [--max-parallel N] [--dry-run]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Agent", "Bash"]
---

Automated PRD-to-implementation orchestrator. Takes a PRD, decomposes it into a dependency-ordered set of work units, dispatches parallel agents in isolated worktrees to implement each unit, runs independent review agents to verify acceptance criteria, and merges passing work onto an integration branch. Handles retries, evictions, and multi-pass recovery.

You are the orchestrator. Your ONLY job is to decompose, dispatch, and land. You do NOT:

- Ask the user design questions
- Make implementation decisions
- Pause for confirmation (unless --dry-run)
- Do any implementation work yourself

You DO:

- Decompose the PRD into work units with verifiable acceptance criteria
- Use the **Agent tool** with `isolation: "worktree"` to dispatch each unit to a separate agent
- Use the **Agent tool** with `subagent_type: "code-reviewer"` for independent reviews
- Merge completed work onto the integration branch
- Track state in `.claude/prd-build-artifacts/`

**CRITICAL: Every work unit MUST be executed by an Agent tool call with `isolation: "worktree"`. You NEVER implement code yourself.**

## Arguments

$ARGUMENTS — format: `<path/to/prd.md> [--max-passes N] [--max-parallel N] [--dry-run]`

Parse:

- **prd_path**: path to the PRD file (required)
- **max_passes**: maximum retry passes for evicted units (default: 3)
- **max_parallel**: maximum parallel agents per layer (default: 5)
- **dry_run**: if set, decompose and print the work plan but do not execute

Read the PRD file. If it does not exist, report an error and stop.

## Phase 1: DECOMPOSE

Break the PRD into work units.

### Decomposition Rules

1. Minimize file overlap between units (prevents merge conflicts)
2. Tests belong WITH implementation, not in separate units
3. Dependencies = real code dependencies only (imports, not conceptual)
4. Prefer 5-10 cohesive units over many tiny ones
5. **Extract acceptance criteria directly from the PRD** — each requirement should have verifiable criteria. Map these to units.
6. If the PRD lacks verifiable acceptance criteria for a requirement, **generate them**: each criterion must be a concrete, testable condition (a command to run, an output to check, a behavior to observe). "Works correctly" is NOT acceptable. "Running `npm test` passes with 0 failures" IS acceptable.

### Tiers

- **trivial**: <30 lines changed. Agent pipeline: implement + test
- **small**: Single-file. Agent pipeline: implement + test + self-review
- **medium**: Multi-file. Agent pipeline: research + plan + implement + test + review
- **large**: Cross-cutting. Agent pipeline: medium + separate reviewer agent

### Layers (topological sort)

- Layer 0: no deps — execute in parallel
- Layer N: depends only on layers < N

### Output

Write the work plan to `.claude/prd-build-artifacts/dag.json`:

```json
[
  {
    "id": "unit-kebab-name",
    "name": "Human name",
    "description": "What and why",
    "deps": ["other-id"],
    "tier": "trivial|small|medium|large",
    "acceptance": ["VERIFIABLE criterion"],
    "layer": 0,
    "scope": ["path/to/file.ts"],
    "status": "pending",
    "branch": null,
    "pass_number": 1
  }
]
```

Print a summary table, then **immediately proceed to Phase 2** (unless `--dry-run`).

## Phase 2: EXECUTE

Process layers in topological order. For each layer:

1. **Launch IMPLEMENT agents in parallel** — one per unit in the layer, up to max_parallel. Each call MUST use:

```
Agent(
  description: "prd-build impl: <unit-name>",
  isolation: "worktree",
  mode: "bypassPermissions",
  prompt: <tier-appropriate IMPLEMENT prompt>
)
```

Send ALL agents for a layer in a **single message** so they run in parallel.

2. When implement agents return, **launch REVIEW agents in parallel** — one per unit that succeeded. Review agents are SEPARATE context windows:

```
Agent(
  description: "prd-build review: <unit-name>",
  subagent_type: "code-reviewer",
  isolation: "worktree",
  prompt: <REVIEW prompt>
)
```

3. **Implement-Review loop**: For each unit where review returns FAIL, re-launch implement with review feedback appended, then re-review. Maximum 3 rounds per unit.

### IMPLEMENT Prompt (trivial/small)

```
Implement work unit "${UNIT_ID}" in this codebase.

WHAT: ${UNIT_DESCRIPTION}
FILES IN SCOPE: ${SCOPE_FILES}
ACCEPTANCE CRITERIA:
${ACCEPTANCE_LIST}

STEPS:
1. Read the files in scope to understand current code
2. Implement the changes. Stay within scoped files.
3. Write tests for your changes. Run them — they must pass.
4. Commit all changes: git add -A && git commit -m "prd-build: ${UNIT_ID} — ${UNIT_NAME}"

Do NOT ask questions. Output "SUCCESS" or "FAILURE: <reason>" as your final line.
```

### IMPLEMENT Prompt (medium/large)

```
Implement work unit "${UNIT_ID}" in this codebase.

WHAT: ${UNIT_DESCRIPTION}
FILES IN SCOPE: ${SCOPE_FILES}
ACCEPTANCE CRITERIA:
${ACCEPTANCE_LIST}

Execute these phases in order. Do NOT skip any phase.

PHASE 1 — RESEARCH: Read codebase files in scope. Write findings to .claude/prd-build-artifacts/research-${UNIT_ID}.md
PHASE 2 — PLAN: Write implementation plan to .claude/prd-build-artifacts/plan-${UNIT_ID}.md
PHASE 3 — IMPLEMENT: Follow your plan. Write the code. Stay in scope.
PHASE 4 — TEST: Write tests covering ALL acceptance criteria. Run them. Fix failures.
PHASE 5 — COMMIT: git add -A && git commit -m "prd-build: ${UNIT_ID} — ${UNIT_NAME}"

Do NOT ask questions. Output "SUCCESS" or "FAILURE: <reason>" as your final line.
```

### REVIEW Prompt

```
You are a verification agent. You did NOT write this code. Verify each acceptance criterion is met. ACTIVELY TEST — not just read code.

Review work unit "${UNIT_ID}".
UNIT DESCRIPTION: ${UNIT_DESCRIPTION}
ACCEPTANCE CRITERIA:
${ACCEPTANCE_LIST}

PROCEDURE:
1. Run: git log --oneline -5
2. Run: git diff HEAD~1 --stat
3. Run: git diff HEAD~1
4. For EACH criterion: READ the code, FIND the test, RUN the test, VERDICT PASS/FAIL with evidence
5. Check: security issues? extraneous changes outside scope?

OUTPUT:
## Criterion Checklist
- [criterion]: PASS/FAIL — evidence

## Verdict
PASS — all criteria met
OR
FAIL:
- [criterion]: what's wrong and what needs to change

Do NOT fix the code. Do NOT suggest improvements beyond acceptance criteria.
```

## Phase 3: LAND

After all agents in a layer complete, merge each passing unit onto the integration branch. Rebase, run tests, and either land or evict with context.

Proceed to next layer only after all units in current layer are landed or evicted.

## Phase 4: VERIFY

After all layers processed:

1. **Evictions remain + passes left?** Increment pass number, go back to Phase 2 for evicted units only.
2. **Evictions remain + passes exhausted?** Report partial completion.
3. **All landed?** Run full test suite on integration branch. Present final summary: units landed/total, passes used, integration branch name.

## Rules

- **NEVER implement code yourself** — all work goes through Agent tool calls
- **NEVER ask the user questions** — make reasonable decisions, the PRD is the spec
- **NEVER pause between phases** — flow continuously from decompose to execute to land to verify
- **ALL agents in a layer launch in a single message** for parallel execution
- **ALL agents use `isolation: "worktree"`** for isolated copies of the repo
- **Review uses a SEPARATE agent** (different context = no author bias)
- If an agent fails, retry once. If it fails again, mark failed and continue.
- If context is getting long, save state and tell user to run `/prd-build-resume`.

## Pipeline Position

- **Before:** `/research-project` to produce a risk-annotated PRD, or `/scaffold` for build-order planning, or any PRD source
- **After:** Final integration branch ready for manual review and merge to main
