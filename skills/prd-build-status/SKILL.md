---
name: prd-build-status
description: "Show PRD build orchestration status"
argument-hint: ""
allowed-tools: ["Read"]
---

# PRD Build Status

Read the state file and present a clear status report.

```!
if [ -f .claude/prd-build.state.json ]; then
  cat .claude/prd-build.state.json
else
  echo "NO_STATE_FILE"
fi
```

If NO_STATE_FILE: tell the user there's no active PRD build run. Suggest `/prd-build <prd-path>` to start one.

Otherwise, also read `.claude/prd-build-artifacts/dag.json` with the Read tool to get unit-level detail.

## Status Report Format

```
PRD Build Status: <status>
Pass: <current>/<max> | Started: <time>

Progress:
  Layer 0: [landed] unit-a, [landed] unit-b
  Layer 1: [active] unit-c (implement), [pending] unit-d
  Layer 2: [pending] unit-e

Summary: X/Y units landed | Z active | W pending | E evicted
```

Use status indicators:

- `landed` — merged to integration branch
- `active` — agent currently working (show pipeline stage if available)
- `passed` — done, waiting in merge queue
- `pending` — not yet started
- `evicted` — merge failed, awaiting retry
- `failed` — permanently failed

Also read and show the last 10 lines of `.claude/prd-build.log.md` as recent activity.
