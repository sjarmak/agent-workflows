---
name: prd-queue
description: "Run /prd-build over multiple PRDs with full worktree lifecycle (create, dispatch, FF-merge, cleanup). Single-command dispatch from one session — sequential or parallel."
argument-hint: "<prd1.md> [<prd2.md> ...] [--parallel | --max-parallel N]"
allowed-tools: ["Read", "Bash"]
---

Multi-PRD queue supervisor. Each PRD runs in its own ephemeral worktree via a fresh background `claude -p "/prd-build ..."` session. This skill manages the worktree lifecycle (create → dispatch → wait → FF-merge → teardown) so the user can dispatch many PRDs from one terminal and walk away.

You are the queue supervisor. You do NOT decompose PRDs. You do NOT modify code. You DELEGATE each PRD to a fresh `claude -p` instance and orchestrate their lifecycle with `scripts/prd_queue_lifecycle.sh`.

## Arguments

`$ARGUMENTS` — format: `<prd1> [<prd2> ...] [--parallel] [--max-parallel N]`

- One or more PRD paths (relative to repo root, e.g. `docs/prd/prd_foo.md`)
- `--parallel` — dispatch all PRDs concurrently (caps at `--max-parallel` if set)
- `--max-parallel N` — limit concurrent jobs (default: unbounded if `--parallel`, else 1)
- Default: **sequential** (one PRD at a time, in arg order)

## Pre-flight (fail fast before any worktree creation)

1. Resolve each PRD path. If any file is missing, print `MISSING: <path>` for each and stop. Do not create any worktrees.
2. Check `git -C <primary-repo> status --porcelain` is clean (ignore the `ads_metadata_by_year_picard` symlink and any `.claude/prd-build*` line). If dirty, refuse with: "primary repo has uncommitted changes; commit or stash before running /prd-queue."
3. Verify `scripts/prd_queue_lifecycle.sh` exists and is executable.
4. Verify `claude` is on PATH (`which claude` succeeds).
5. Print the queue plan (PRD list + mode + max_parallel) before starting.

## Per-PRD lifecycle

For each PRD (in order for sequential; all-at-once-up-to-N for parallel):

### 1. Setup
```bash
scripts/prd_queue_lifecycle.sh setup <prd-path>
```
Captures stdout: `<slug>\t<worktree_path>\t<branch_name>`. Parse into variables. Save to your in-skill state table.

### 2. Dispatch (background bash)

Use the Bash tool with `run_in_background=true`:
```bash
cd <worktree_path> && \
  claude -p "/prd-build <prd-path>" \
  > /tmp/prd-queue-<slug>.log 2>&1
```

Capture the task ID returned by Bash. Record `{slug, prd, worktree_path, branch_name, task_id, log_path, started_at}` in your state table.

### 3. Wait for notification

The Bash background job will trigger a completion notification when `claude -p` exits. Do NOT poll the log. Do NOT use `sleep`. End your turn after dispatching all the jobs you intend to dispatch in this round; the harness will resume you when each notification arrives.

### 4. On notification (per slug)

When a task-completion notification arrives for a slug:

a. Read the last ~60 lines of `/tmp/prd-queue-<slug>.log`.
b. Determine outcome:
   - **Success**: log shows `PRD build complete`, `Build DONE`, or all units landed cleanly. No tracebacks in the tail. `claude -p` exited 0.
   - **Failure**: traceback, `FAILURE:`, `blocked`, `evicted`, or non-zero exit. Also: log empty or shows only "Async agent launched" with nothing further.
c. Get the integration branch's commit count vs main: `git -C <primary> rev-list --count main..<branch>`.
d. Run teardown:
   - Success → `scripts/prd_queue_lifecycle.sh teardown <slug>` (FF merges, removes worktree, deletes branch)
   - Failure → `scripts/prd_queue_lifecycle.sh keep <slug>` (leaves worktree intact; user inspects manually)
e. Update your in-skill state table with `{result, commits, wt_action, finished_at}`.

### 5. Sequential mode: dispatch the next PRD

After teardown of PRD #N, immediately go to step 1 for PRD #N+1.

### 6. Parallel mode: replenish the queue

If `--max-parallel N` was set and there are more PRDs queued, dispatch the next one now (back to step 1). Otherwise wait for remaining notifications.

## Final summary

When all PRDs have completed (or failed-and-kept), print a markdown table:

```
| PRD                                   | slug                | result | commits | duration | wt action       |
| ------------------------------------- | ------------------- | ------ | ------: | -------- | --------------- |
| prd_section_embeddings_mcp...         | section-embeddi...  | PASS   |       7 |    32m   | removed         |
| prd_nanopub_claim_extraction          | nanopub-claim-e...  | FAIL   |       2 |    14m   | kept @ /path... |
| prd_chunk_embeddings_build            | chunk-embeddings... | PASS   |       9 |    47m   | removed         |
```

Then briefly note any kept worktrees and the next steps for inspecting them.

## Failure modes & escalations

- **`claude -p` doesn't honor slash-command invocation**: First PRD's log shows the slash command treated as literal prompt input or no decomposition output. STOP the queue, print "claude -p does not invoke skills in this environment; falling back to sequential interactive runs is required." Do not attempt remaining PRDs.
- **All worktree branches diverged**: teardown returns non-zero for "diverged from main." Print which slugs need manual merge resolution. Continue with remaining queue but flag the issue prominently.
- **Bash background job hangs >2hr**: a `/prd-build` taking that long is a real problem. The user can /prd-build-cancel from a separate session against the worktree. The queue continues waiting for the notification — do NOT kill the bash job from this skill.
- **Notification fires before log file flushes**: re-read after a 2s sleep; if still empty, mark as inconclusive and `keep` the worktree.

## Hard rules

- NEVER skip teardown for a successful PRD.
- NEVER teardown a failed PRD's worktree (it has the inspection state).
- NEVER FF-merge a diverged branch — the lifecycle script enforces this; respect its non-zero exit.
- NEVER touch the primary repo's working tree mid-orchestration.
- NEVER cancel a running background `claude -p` job — let it complete naturally or be cancelled out-of-band.
- NEVER set `run_in_background=false` for the `claude -p` dispatch — that would block for hours past the bash 10-minute timeout.
- NEVER `sleep` or poll instead of waiting for notifications.

## Implementation notes

- `claude -p` produces verbose output to stderr and JSON/text to stdout depending on `--output-format`. Default is fine; the log file captures both via `2>&1`.
- Each `claude -p` is a fresh session with a fresh context — the inner /prd-build orchestration cannot see this queue's state. That's the design.
- Worktree branches are named `prd-build/<slug>` per the lifecycle script. They appear briefly during the build and are removed on successful teardown.
- The lifecycle script handles the case where `/prd-build`'s harness FF-merged commits to main during the build — teardown detects this and skips the merge, just removes the worktree.
