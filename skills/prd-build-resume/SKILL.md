---
name: prd-build-resume
description: "Resume a paused or interrupted PRD build run"
argument-hint: ""
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Agent"]
---

# PRD Build Resume

Load existing state:

```!
if [ -f .claude/prd-build.state.json ]; then
  cat .claude/prd-build.state.json
else
  echo "NO_STATE_FILE"
fi
```

If NO_STATE_FILE: tell the user there's no run to resume. Suggest `/prd-build <prd-path>` to start one.

Otherwise, follow this recovery procedure:

## 1. Assess State

Read `.claude/prd-build.state.json` and `.claude/prd-build-artifacts/dag.json`. Determine:

- What phase was the run in? (decomposing, executing, landing, verifying, paused)
- Which units are landed, active, pending, evicted, failed?
- What pass number are we on?

## 2. Recover Interrupted Units

Any units with status "active" were interrupted mid-execution. Read `dag.json`, update those units' status to `"pending"` and clear their `pipeline_stage` to `null`, then write the file back.

## 3. Resume Execution

Update `.claude/prd-build.state.json` status to `"executing"`. Append to `.claude/prd-build.log.md`: "Resumed from checkpoint".

## 4. Continue from Current Layer

Find the lowest layer number that still has non-landed units. Resume Phase 2 (EXECUTE) from that layer.

Follow the exact same orchestration logic as the main `/prd-build` command's Phase 2, 3, and 4. The key difference: you already have the work plan — skip decomposition and go straight to execution.

Read the PRD for context:

```bash
# The PRD path is stored in the state file — read it from the JSON printed above
cat "$(cat .claude/prd-build.state.json | python3 -c 'import sys,json; print(json.load(sys.stdin)["prd_path"])')"
```

Then read that file to understand what's being built, and continue orchestrating.
