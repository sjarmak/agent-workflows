Single-task execution loop with structured context handoff. Enforces the discipline of plan → execute → simplify → review → close, one bead at a time. Uses Beads (`bd`) for task tracking so context survives across sessions without artifact clutter. A new session runs `bd ready` and picks up exactly where the last one left off.

## Arguments

$ARGUMENTS — format: `[bead-id | "new task description"]`

- If a bead ID is provided (e.g., `agent-workflows-a3f2`), work on that bead.
- If a quoted or unquoted description is provided, create a new bead.
- If no argument is provided, run `bd ready` and let the user pick.

## Parse Arguments

Extract:

- **bead_id**: an existing bead ID (matches pattern `*-<hex>`)
- **task_description**: free text describing new work

If neither is provided, proceed to Phase 0 (Select).

## Phase 0: Select

First, verify `bd` is available by running `bd status`.

If `bd` is not initialized, run `bd init` and inform the user that Beads has been set up.

Run `bd ready --pretty` to show available work.

**If there are ready beads**: ask the user which bead to focus on, or if they want to describe new work.

**If there are zero beads in the entire database** (`bd status` shows Total Issues: 0): this is a cold start. Ask the user:

> No beads exist yet. Would you like to:
>
> 1. **Describe a single task** to work on now
> 2. **Describe an epic** and I'll break it down into tasks
> 3. **Run `/scaffold`** first to plan a full build order (recommended for multi-session projects)

For option 1, create a single bead:

```bash
bd create "<title>" -p <priority> -t <type> -d "<one-line description>"
```

For option 2, create an epic and decompose it into child tasks:

```bash
bd create "<epic title>" -t epic -p 1 -d "<summary>"
bd create "<task 1>" --parent <epic-id> -p <priority> -d "<description>"
bd create "<task 2>" --parent <epic-id> -p <priority> -d "<description>"
bd dep add <task-2-id> <task-1-id>  # if ordering matters
```

Then run `bd ready --pretty` and pick the first ready task.

For option 3, suggest the user run `/scaffold` which will seed beads automatically, then return to `/focus`.

**If there are beads but none are ready** (all blocked or in-progress): run `bd list` to show the full picture and help the user unblock or reprioritize.

Capture the bead ID for subsequent phases.

## Phase 1: Plan

**Enter plan mode.** This phase produces the context bridge — a written plan attached to the bead that any future session can read to resume work.

1. **Read the bead**: `bd show <id>` to get full context, history, parent/child relationships, and any notes from prior sessions.

2. **Understand the scope**:
   - If the bead has a parent epic, run `bd show <parent-id>` to understand the broader initiative.
   - If the bead has dependencies, run `bd graph <id>` to see what's blocked/blocking.
   - Read any files referenced in the bead description or notes.

3. **Draft the plan** with these sections:
   - **Goal**: one sentence — what "done" looks like
   - **Approach**: the implementation strategy (2-5 bullets)
   - **Files to touch**: list specific files that will change
   - **Tests**: what tests to write or update
   - **Risks**: anything that could go wrong (0-3 bullets)
   - **Out of scope**: what this bead does NOT include

4. **Attach the plan to the bead**:

   ```bash
   bd note <id> "PLAN: <plan summary>"
   ```

5. **Claim the bead**:

   ```bash
   bd update <id> --claim
   ```

6. **Present the plan to the user and wait for confirmation.** Do not proceed until the user approves or adjusts the plan.

### Decomposition

If during planning the task is too large for a single focused session (more than ~3 files changing, or multiple independent concerns), suggest decomposing:

```bash
bd create "<subtask-1>" --parent <id> -p <priority>
bd create "<subtask-2>" --parent <id> -p <priority>
bd dep add <subtask-2> <subtask-1>  # if ordering matters
```

Then focus on the first subtask. The parent bead tracks the epic.

## Phase 2: Execute

**Exit plan mode.** Implement the plan using TDD:

1. **Write tests first** — cover the expected behavior from the plan.
2. **Run tests** — confirm they fail (RED).
3. **Implement** — write the minimal code to pass tests (GREEN).
4. **Run tests** — confirm they pass.
5. **Note progress** on the bead as you go:
   ```bash
   bd note <id> "PROGRESS: <what was done>"
   ```

If you discover something unexpected during execution (a dependency, a larger scope, a bug), do NOT silently expand scope. Instead:

```bash
bd create "<discovered work>" --parent <parent-id-or-current-id> -p <priority>
bd note <id> "DISCOVERY: <what was found>, filed as <new-bead-id>"
```

Stay focused on the original bead.

## Phase 3: Simplify

After code is written and tests pass, run the **code-simplifier** agent on all changed files:

1. Get the list of changed files: `git diff --name-only HEAD`
2. Launch the code-simplifier agent:
   ```
   Agent(subagent_type="code-simplifier", prompt="Review and simplify the recently changed files. Run git diff to see what changed. Focus on: unnecessary complexity, duplicated code, dead code, over-engineering. Apply fixes directly, then run tests to verify nothing broke.")
   ```
3. Run tests again after simplification to verify nothing broke.

## Phase 4: Review

Launch the **code-reviewer** agent on the changes:

```
Agent(subagent_type="code-reviewer", prompt="Review all staged and unstaged changes (git diff). Check for: correctness, security issues, error handling, naming, test coverage. Report issues by severity: CRITICAL, HIGH, MEDIUM, LOW.")
```

- **CRITICAL/HIGH** issues: fix them now, re-run tests.
- **MEDIUM** issues: fix if quick, otherwise file a new bead.
- **LOW** issues: note on the bead for future cleanup.

After addressing review findings, note the outcome:

```bash
bd note <id> "REVIEW: <summary of findings and fixes>"
```

## Phase 5: Close

1. **Run session-cleanup** to remove ephemeral artifacts:

   ```
   Skill(skill="session-cleanup")
   ```

2. **Close the bead** with a summary of what was done:

   ```bash
   bd close <id> -r "DONE: <what was implemented, key decisions made, anything the next session should know>"
   ```

3. **Show what's next**:

   ```bash
   bd ready --pretty
   ```

4. Present the user with:
   - What was completed
   - Any new beads filed during execution (discoveries, deferred work)
   - What's ready to work on next

## Rules

- **One bead at a time.** Do not work on multiple beads in a single focus session. If work naturally splits, decompose into child beads and focus on one.
- **Plan mode is mandatory.** Never skip Phase 1. The plan is the context bridge for future sessions.
- **Claim before executing.** Always `bd update --claim` before writing code so parallel agents don't collide.
- **Discoveries become beads, not scope creep.** Anything found during execution that's outside the plan gets filed as a new bead, not silently added to the current work.
- **Simplify before review.** The code-simplifier runs before the code-reviewer so the reviewer sees clean code.
- **Close with context.** The close reason should give a future session enough context to understand what happened without reading the full history.
- **No floating artifacts.** Do not save `prd_*.md`, `plan_*.md`, or similar files to the working directory. All context lives in bead notes and descriptions. If a skill like `/diverge` produces an artifact, reference its content in a bead note rather than leaving the file.
- **Tests must pass at every phase boundary.** After execute, after simplify, and after review — tests must be green before proceeding.

## Pipeline Position

Entry point for focused implementation work. Sits after ideation/design skills and before git operations:

```
/brainstorm or /diverge → /converge → /premortem → bd create (epic + tasks)
                                                          ↓
                                                     /focus <bead-id>
                                                          ↓
                                                   plan → execute → simplify → review → close
                                                          ↓
                                                     /focus <next-bead-id>
```

Works naturally with Beads hierarchy:

- Epics from `/scaffold` become parent beads
- Each scaffold step becomes a child bead
- `/focus` works through them one at a time
- `bd ready` always shows what's next
