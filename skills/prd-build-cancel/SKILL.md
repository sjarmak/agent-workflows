---
name: prd-build-cancel
description: "Cancel or pause a PRD build run"
argument-hint: "[--keep-branches]"
allowed-tools: ["Bash", "Read", "Write", "Edit"]
---

# PRD Build Cancel

Check for an active run:

```!
if [ -f .claude/prd-build.state.json ]; then
  cat .claude/prd-build.state.json
else
  echo "NO_STATE_FILE"
fi
```

If NO_STATE_FILE: tell the user there's no active run to cancel.

Otherwise, present the current status and ask the user which action they want:

1. **Pause** — Update `.claude/prd-build.state.json` status to `"paused"`. State is preserved. Resume later with `/prd-build-resume`.

   Also append a timestamped line to `.claude/prd-build.log.md`: "Run paused by user".

2. **Cancel (clean)** — Remove all worktrees, branches, and state files:

   ```bash
   # Remove worktrees
   git worktree list --porcelain | grep -oP 'worktree \K.*prd-build.*' | while read wt; do git worktree remove --force "$wt"; done
   # Remove branches
   git branch --list 'prd-build/*' | xargs -r git branch -D
   # Remove state files
   rm -rf .claude/prd-build.state.json .claude/prd-build.log.md .claude/prd-build-artifacts/
   ```

3. **Cancel (keep branches)** — Remove worktrees and state but keep git branches for manual inspection:

   ```bash
   # Remove worktrees only
   git worktree list --porcelain | grep -oP 'worktree \K.*prd-build.*' | while read wt; do git worktree remove --force "$wt"; done
   # Remove state files
   rm -rf .claude/prd-build.state.json .claude/prd-build.log.md .claude/prd-build-artifacts/
   ```

WAIT for the user to choose before taking any action.
