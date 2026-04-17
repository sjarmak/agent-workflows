Single-task execution loop with structured context handoff. Enforces the discipline of plan → execute → simplify → review → close. Uses Beads (`bd`) for task tracking so context survives across sessions without artifact clutter. A new session runs `bd ready` and picks up exactly where the last one left off. Supports parallel execution of independent beads via worktree-isolated subagents.

## Arguments

$ARGUMENTS — format: `[bead-id | "new task description" | "parallel"]`

- If a bead ID is provided (e.g., `agent-workflows-a3f2`), work on that bead.
- If a quoted or unquoted description is provided, create a new bead.
- If `parallel` is provided, jump directly to parallel recommendation flow.
- If no argument is provided, run `bd ready` and let the user pick (includes parallel recommendations).

## Parse Arguments

Extract:

- **bead_id**: an existing bead ID (matches pattern `*-<hex>`)
- **task_description**: free text describing new work
- **parallel_mode**: true if argument is "parallel"

If neither is provided, proceed to Phase 0 (Select).

## Phase 0: Select

First, verify `bd` is available by running `bd status`.

If `bd` is not initialized, run `bd init` and inform the user that Beads has been set up.

Run these commands to gather full context:

```bash
bd ready --pretty
bd ready --json
bd graph --all --compact
```

### Analysis: Priority & Parallelism

With the ready beads and dependency graph in hand, perform this analysis:

1. **Sort by priority**: Group ready beads by priority level (P0 > P1 > P2 > P3). Within the same priority, prefer beads with more dependents (unblocks more work).

2. **Detect parallel sets**: Using the `bd graph --all --compact` output, identify beads that are in the same dependency layer (LAYER 0, LAYER 1, etc.). Beads in the same layer with no shared parent-child or blocking relationships can execute in parallel. Cross-reference with `bd ready --json` to check that candidate beads don't touch overlapping file paths (check descriptions and notes for file references).

3. **Classify each ready bead**:
   - **Code beads**: require writing/modifying code in the repo (need worktree isolation for parallel execution)
   - **External beads**: involve actions outside the repo (publishing, running tools against external repos, writing content) — these can run in parallel without worktree isolation

4. **Build the recommendation**:

Present findings as a structured recommendation:

```
## Ready Work (sorted by priority)

### Parallel Set A (can run simultaneously)
- [P1] bead-id-1 — title (code)
- [P1] bead-id-2 — title (external)
- [P1] bead-id-3 — title (external)

### Sequential (depends on Set A)
- [P2] bead-id-4 — title (blocked by bead-id-1)

### Recommended Action
- **Single focus**: Pick `bead-id-1` (highest impact, unblocks bead-id-4)
- **Parallel sprint**: Run bead-id-1, bead-id-2, and bead-id-3 simultaneously
  (3 independent subagents, ~Nx faster)
```

### Offering Parallel Execution

When 2+ ready beads can run in parallel, always present the parallel option:

> **Parallel execution available**: N beads can run simultaneously in isolated subagents.
> Each subagent gets its own worktree and runs the full focus protocol (plan → execute → simplify → review → close).
>
> Would you like to:
>
> 1. **Focus on one bead** — pick from the list above
> 2. **Run N beads in parallel** — I'll spin up N subagents now
> 3. **Custom selection** — pick which subset to parallelize

If the user chooses parallel, proceed to **Phase P: Parallel Dispatch** (below).
If the user chooses a single bead, proceed to Phase 1 as normal.

### Cold Start (zero beads)

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

Capture the bead ID (or set of IDs for parallel) for subsequent phases.

## Phase P: Parallel Dispatch

When the user opts for parallel execution, spin up independent subagents — one per bead. Each subagent runs the full focus protocol (Plan → Execute → Simplify → Review → Close) autonomously.

### Pre-flight

1. **Claim all beads** before dispatching to prevent collisions:

   ```bash
   bd update <id-1> --claim
   bd update <id-2> --claim
   # ... for each bead in the parallel set
   ```

2. **Gather context for each bead**: run `bd show <id> --json` for each bead to capture the full description, notes, and dependencies. This context is passed to each subagent.

### Dispatch

Launch all subagents in a **single message** using the Agent tool, one per bead. Each agent runs in an isolated worktree so code changes don't conflict.

For **code beads** (modify files in the repo), use worktree isolation:

```
Agent(
  subagent_type="general-purpose",
  isolation="worktree",
  mode="bypassPermissions",
  name="focus-<bead-id>",
  description="Focus: <short bead title>",
  prompt="You are running the /focus protocol on bead <bead-id>.

## Bead Context
<paste full bd show output here>

## Your Task
Execute the full focus protocol phases sequentially:

### Phase 1: Plan
- Read the bead context above
- Identify files to touch by reading the codebase
- Draft a plan with: Goal, Approach, Files to touch, Tests, Risks, Out of scope
- Run: bd note <id> 'PLAN: <summary>'

### Phase 2: Execute (TDD)
- Write tests first, run them (expect RED)
- Implement minimal code to pass (GREEN)
- Run tests to confirm they pass
- Run: bd note <id> 'PROGRESS: <what was done>'

### Phase 3: Simplify
- Get the list of changed files: git diff --name-only HEAD
- Launch the code-simplifier agent:
  Agent(subagent_type='code-simplifier', prompt='Review and simplify the recently changed files. Run git diff to see what changed. Focus on: unnecessary complexity, duplicated code, dead code, over-engineering. Apply fixes directly, then run tests to verify nothing broke.')
- Run tests again after simplification to verify nothing broke

### Phase 4: Review (MANDATORY — do not skip)
Run THREE independent review agents in parallel. Wait for all to complete before proceeding.

1. **Code review agent**:
   Agent(subagent_type='code-reviewer', prompt='Review all uncommitted changes (run git diff HEAD). Focus on correctness, API consistency, error handling, naming, test quality. Report issues by severity: CRITICAL/HIGH/MEDIUM/LOW with file:line references.')

2. **Security review agent**:
   Agent(subagent_type='security-reviewer', prompt='Security review of all uncommitted changes (run git diff HEAD and read new untracked files). Focus on: secrets in logs/errors, injection vectors, auth flows, file permission issues, input validation at boundaries. Report CRITICAL/HIGH issues that must be fixed before commit.')

3. **Python review agent** (or language-appropriate reviewer):
   Agent(subagent_type='python-reviewer', prompt='Review all uncommitted changes (run git diff HEAD). Focus on PEP 8, type hints, Pythonic idioms, async correctness, and security. Report issues by severity.')

After all three complete:
- Fix any CRITICAL/HIGH issues immediately
- Fix MEDIUM issues if quick, otherwise file a new bead
- Note LOW issues on the bead for future cleanup
- Re-run tests after any fixes
- Run: bd note <id> 'REVIEW: <summary of findings from code-reviewer, security-reviewer, python-reviewer and fixes applied>'

### Phase 5: Close
- Run: bd close <id> -r 'DONE: <summary of what was implemented and key decisions>'

## Rules
- Stay within scope of THIS bead only
- If you discover unrelated work, run: bd create '<title>' --parent <parent-id> -p <priority>
- Do NOT modify files outside your bead's scope
- Tests must pass before closing
- **Review is NOT optional.** Phase 4 must run all three review agents. Skipping review is a protocol violation.
"
)
```

For **external beads** (no repo code changes — publishing, running tools, writing content), skip worktree isolation:

```
Agent(
  subagent_type="general-purpose",
  mode="bypassPermissions",
  name="focus-<bead-id>",
  description="Focus: <short bead title>",
  prompt="<same structure as above, adapted for external work>"
)
```

### Monitoring

After dispatching, inform the user:

> Dispatched N parallel agents:
>
> - `focus-<id-1>`: <title> (worktree)
> - `focus-<id-2>`: <title> (external)
> - `focus-<id-3>`: <title> (worktree)
>
> Each agent runs plan → execute → simplify → review → close independently.
> I'll report results as they complete.

Run all agents with `run_in_background: true` so the main session remains responsive.

### Convergence

As each agent completes:

1. Read the agent's result
2. Report to the user: what was done, any discoveries filed, pass/fail
3. If an agent's worktree has changes, inform the user of the worktree branch so they can review/merge

After all agents complete:

1. Show a summary table:
   ```
   | Bead | Status | Key Changes | New Beads Filed |
   |------|--------|-------------|-----------------|
   ```
2. **Run convergence review gate (MANDATORY).** Even though subagents run their own Phase 4, the main session must run a consolidated review across the merged changes from all agents:

   Launch these review agents in parallel against the combined diff:
   - `code-reviewer`: `git diff HEAD` across all changes from the wave
   - `security-reviewer`: security-focused review of all changes, especially cross-cutting concerns that individual subagents may miss (e.g., auth token passed between modules)

   Fix any CRITICAL/HIGH findings before proceeding. This catches integration issues that isolated per-bead reviews miss — e.g., two beads both modifying the same module's imports, or one bead's auth refactor breaking another bead's caller pattern.

3. Run `bd ready --pretty` to show what's next
4. If any agent failed or filed discovery beads, highlight those for the user

### Parallel Limits

- **Max 4 parallel agents** to avoid resource exhaustion. If more beads are parallelizable, batch them in waves of 4.
- **Code beads sharing the same files** cannot run in parallel even if they're in the same dependency layer. Check bead descriptions/notes for file overlap before dispatching.
- **Beads database is shared** — `bd note`, `bd close`, and `bd create` commands from parallel agents may interleave, but this is safe since each agent operates on its own bead ID.

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

6. **Run an adversarial plan review before presenting.** Invoke the `architect` agent to pressure-test the plan:

   ```
   Agent(subagent_type="architect", prompt="Adversarial review of the plan attached to bead <id> (run: bd show <id>, the plan is in the PLAN note). Pressure-test: is the approach right, are risks complete, is the files-to-touch list accurate, is the test strategy sufficient, are the out-of-scope boundaries correct? Report CRITICAL/HIGH concerns with specific file:line or acceptance-criterion references.")
   ```

   Wait for the agent's findings. Fold any CRITICAL/HIGH concerns into a revised plan and re-note the bead:

   ```bash
   bd note <id> "PLAN-REVIEW: <findings summary and changes made>"
   ```

7. **Present the plan to the user and wait for confirmation.** Do not proceed until the user approves or adjusts the plan.

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
2. **Run a review of the tests before running them.** Stage the test files (`git add <test-files>`) and invoke the `code-reviewer` agent:

   ```
   Agent(subagent_type="code-reviewer", prompt="Review the staged test files (run git diff --cached). Focus on: coverage of the plan's acceptance criteria, test correctness, fixture realism, assertion strength, and whether the tests would actually catch the bug the plan describes. Report CRITICAL/HIGH findings with file:line references.")
   ```

   Address CRITICAL/HIGH findings before proceeding. Note the outcome:

   ```bash
   bd note <id> "TEST-REVIEW: <findings summary and changes made>"
   ```

3. **Run tests** — confirm they fail (RED).
4. **Implement** — write the minimal code to pass tests (GREEN).
5. **Run tests** — confirm they pass.
6. **Note progress** on the bead as you go:
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

## Phase 4: Review (MANDATORY — do not skip)

Run **three independent review agents in parallel**. These catch different classes of issues — all three are required.

1. **Code review agent**:

   ```
   Agent(subagent_type="code-reviewer", prompt="Review all uncommitted changes (run git diff HEAD and read new untracked files via git ls-files --others --exclude-standard). Focus on correctness, API consistency, error handling, naming, test quality. Report issues by severity: CRITICAL/HIGH/MEDIUM/LOW with file:line references.")
   ```

2. **Security review agent**:

   ```
   Agent(subagent_type="security-reviewer", prompt="Security review of all uncommitted changes (run git diff HEAD and read new untracked files). Focus on: secrets in logs/errors, injection vectors, auth flows, file permission issues, input validation at boundaries. Report CRITICAL/HIGH issues that must be fixed before commit.")
   ```

3. **Python review agent** (or language-appropriate reviewer):
   ```
   Agent(subagent_type="python-reviewer", prompt="Review all uncommitted changes (run git diff HEAD). Focus on PEP 8, type hints, Pythonic idioms, async correctness, and security. Report issues by severity.")
   ```

After all three complete:

- **CRITICAL/HIGH** issues: fix them now, re-run tests.
- **MEDIUM** issues: fix if quick, otherwise file a new bead.
- **LOW** issues: note on the bead for future cleanup.

If the work involves non-trivial design tradeoffs (auth, data, concurrency, rollback, caching), also run an adversarial pass:

```
Agent(subagent_type="code-reviewer", prompt="Adversarial review: challenge the design tradeoffs in these changes (run git diff HEAD). Focus on: could the auth retry loop be exploited? Are there race conditions? Could the TOML generation be injected? What breaks under concurrent access? Report only genuine risks, not theoretical nitpicks.")
```

After addressing review findings, note the outcome:

```bash
bd note <id> "REVIEW: <summary of findings from code-reviewer, security-reviewer, python-reviewer and fixes applied>"
```

### Why direct Agent calls instead of slash commands

Every review phase in this skill (plan review, test review, Phase 4 review) is invoked via the `Agent` tool rather than via a slash command. Two reasons:

1. **Subagents cannot invoke slash commands.** When `/focus` runs in parallel mode, each subagent is itself an Agent invocation — and Agent invocations can only call other tools, not slash commands. If any review step used a slash command, it would silently skip in parallel mode.
2. **No external plugin dependency.** `code-reviewer`, `security-reviewer`, `python-reviewer`, and `architect` ship with the base harness. Skills that hardcode plugin-provided slash commands (Codex, custom review plugins, etc.) break on any machine where the plugin isn't installed.

The three-agent Phase 4 approach (code-reviewer + security-reviewer + language-reviewer) also provides diverse review perspectives — correctness, security, and language idioms — that a single reviewer would miss.

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

- **One bead per agent.** Each agent (main session or subagent) works on exactly one bead. Parallel mode dispatches multiple agents, each with one bead — it does NOT mean one agent works on multiple beads.
- **Plan mode is mandatory.** Never skip Phase 1 (or equivalent in subagent prompt). The plan is the context bridge for future sessions.
- **Claim before executing.** Always `bd update --claim` before writing code. In parallel mode, claim ALL beads before dispatching any agents.
- **Discoveries become beads, not scope creep.** Anything found during execution that's outside the plan gets filed as a new bead, not silently added to the current work.
- **Simplify before review.** The code-simplifier runs before the code-reviewer so the reviewer sees clean code.
- **Review is NOT optional.** Phase 4 must run all three review agents (code-reviewer, security-reviewer, language-reviewer). Skipping review is a protocol violation. In parallel mode, each subagent runs its own Phase 4, AND the main session runs a convergence review after all agents complete.
- **Close with context.** The close reason should give a future session enough context to understand what happened without reading the full history.
- **No floating artifacts.** Do not save `prd_*.md`, `plan_*.md`, or similar files to the working directory. All context lives in bead notes and descriptions. If a skill like `/diverge` produces an artifact, reference its content in a bead note rather than leaving the file.
- **Tests must pass at every phase boundary.** After execute, after simplify, and after review — tests must be green before proceeding.

## Pipeline Position

Entry point for focused implementation work. Sits after ideation/design skills and before git operations:

```
/brainstorm or /diverge → /converge → /premortem → bd create (epic + tasks)
                                                          ↓
                                                     /focus (or /focus parallel)
                                                          ↓
                                               ┌──────────┴──────────┐
                                          Single bead           Parallel dispatch
                                               │                     │
                                    plan → execute →         N agents in worktrees
                                    simplify → review →      each: plan → execute →
                                    close                    simplify → review → close
                                               │                     │
                                               └──────────┬──────────┘
                                                          ↓
                                                     /focus (next wave)
```

Works naturally with Beads hierarchy:

- Epics from `/scaffold` become parent beads
- Each scaffold step becomes a child bead
- `/focus` analyzes the full ready set and recommends optimal execution
- Single mode: one bead at a time in the main session
- Parallel mode: multiple beads via worktree-isolated subagents
- `bd ready` always shows what's next after each wave completes
