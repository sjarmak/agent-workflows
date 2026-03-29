# Best Practices

How to get the most out of these workflow skills, based on patterns from the Claude Code team and power users.

## Plan First, Then Execute

The single highest-leverage pattern: **start every workflow in Plan mode**, iterate on the plan with Claude, then switch to auto-accept for execution.

1. Press `Shift+Tab` twice to enter Plan mode
2. Invoke your skill (e.g., `/premortem path/to/design.md`)
3. Review the plan — Claude will show you the agents it wants to spawn, their prompts, and the synthesis strategy
4. Go back and forth until the plan looks right
5. Switch to auto-accept (`Shift+Tab` once) and let Claude execute

This works because a good plan lets Claude one-shot the execution. The cost of planning is low; the cost of re-running a 5-agent workflow because the framing was wrong is high.

## Verify Everything

> The most important thing to get great results: give Claude a way to verify its work. If Claude has that feedback loop, it will 2-3x the quality of the final result.

Every workflow skill should end with verification. Some patterns:

### Stop Hook — Automatic Verification

Add a Stop hook that spawns a verification agent when Claude finishes. This catches issues before you even look at the output.

Add to `.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify the work just completed. Check that: (1) all output files exist and are well-formed, (2) any code changes pass linting and tests, (3) the output addresses the original request. If verification fails, explain what needs fixing.",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

### Background Verification Agent

For long-running workflows, prompt Claude to spawn a background verification agent when done:

```
Run /stress-test on the auth module. When you're done, spawn a background agent to verify all findings by running the actual test suite.
```

### Manual Verification Step

At minimum, every workflow output should include a "how to verify" section. The skills in this repo include this in their final phase.

## Simplify After Every Workflow

After any workflow that produces code (e.g., `/diverge-prototype`, `/crossbreed`), run simplification:

```
/simplify
```

This is a [bundled Claude Code skill](https://code.claude.com/docs/en/skills) that spawns three parallel review agents to check for:
- Code reuse opportunities
- Quality issues
- Efficiency improvements

Then it applies fixes automatically. Think of it as the "clean up" pass after the creative work.

You can also create a custom simplification subagent. Save to `~/.claude/agents/code-simplifier.md`:

```markdown
---
name: code-simplifier
description: Simplify and clean up code after generation. Use proactively after writing or modifying code.
tools: Read, Edit, Write, Grep, Glob, Bash
model: inherit
---

You are a code simplifier. After code has been written or modified:

1. Run git diff to see what changed
2. Look for:
   - Unnecessary complexity (can this be simpler?)
   - Duplicated code (extract shared logic)
   - Dead code (unused imports, unreachable branches)
   - Over-engineering (abstractions that aren't needed yet)
   - Missing error handling at system boundaries
3. Apply fixes directly — don't just report issues
4. Run tests after changes to verify nothing broke

Prefer deletion over addition. The best code is code that doesn't exist.
```

## Scope Skills to Changed Files

Multi-agent workflows are expensive. Don't analyze the whole codebase when you only changed three files. A `UserPromptSubmit` hook injects the list of changed files into context before any skill runs, so `/stress-test` and `/premortem` automatically focus on what you actually touched.

Add to `.claude/settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Changed files since last commit:\n$(git diff --name-only HEAD 2>/dev/null)\n\nUntracked files:\n$(git ls-files --others --exclude-standard 2>/dev/null)\""
          }
        ]
      }
    ]
  }
}
```

Every skill invocation now starts with awareness of what changed. Agents scope their analysis to relevant files instead of scanning the entire repo.

## Isolate Skill Output with context:fork

Workflow skills that spawn multiple agents produce massive output. A `/diverge` with 5 research agents can consume half your context window, leaving little room for the synthesis and next steps.

Run verbose skills in a forked subagent context. Add `context: fork` to the skill's frontmatter:

```yaml
---
name: diverge
description: Multi-perspective research
context: fork
---
```

Only the final synthesis returns to your main conversation. The full agent outputs live in the subagent transcript (viewable at `~/.claude/projects/{project}/{session}/subagents/`). This keeps your main context clean for the next skill in the pipeline.

Use `context: fork` on: `/diverge`, `/stress-test`, `/premortem`, `/brainstorm` — any skill where the intermediate output is much larger than the final result.

## Chain Skills into Pipelines

Instead of manually running `/diverge` then `/converge` then `/premortem` and copy-pasting between them, create a pipeline agent that chains them in one invocation.

Save to `.claude/agents/full-pipeline.md`:
```markdown
---
name: full-pipeline
description: Run the full diverge-converge-premortem pipeline
initialPrompt: |
  Run the following workflow skills in sequence, passing outputs between them:
  1. /diverge $ARGUMENTS
  2. Wait for the PRD to be generated, then run /converge on it
  3. Run /premortem on the converged PRD
  Present the final risk-annotated PRD when done.
permissionMode: acceptEdits
---

You are a pipeline orchestrator. Execute each skill in sequence, using
the output of each as input to the next. Summarize progress between steps.
```

Launch with:
```bash
claude --agent full-pipeline "How should we redesign the auth system?"
```

Create pipelines for your most common chains. A security-focused pipeline might chain `/stress-test` then `/premortem`. A design pipeline might chain `/brainstorm` then `/diverge` then `/converge`.

## Add Guard Rails per Skill

Workflow skills should have safety constraints that match their contract. `/stress-test` agents should analyze code, not modify it. `/brainstorm` agents should not execute arbitrary commands. `/bisect` agents should not push to remote.

Add skill-specific `PreToolUse` hooks to `.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_AGENT_TYPE\" | grep -qE 'stress-test|premortem'; then echo 'Blocked: analysis agents must not modify files' >&2; exit 2; fi; exit 0"
          }
        ]
      }
    ]
  }
}
```

This ensures adversarial analysis agents stay read-only. Adjust the pattern to match your workflow — the principle is that each skill's agents should only have the permissions their contract requires.

## Add Routing Rules to CLAUDE.md

Tell Claude when to suggest specific workflow skills by adding project-specific rules to your `CLAUDE.md`:

```markdown
## Workflow Rules

- For any architecture change touching more than 3 files, suggest running /premortem before implementation
- For any new public API endpoint, suggest running /stress-test with the security and edge-case vectors
- For any decision between 2+ approaches, suggest running /converge before committing
- After /diverge-prototype produces prototypes, always run /stress-test before picking a winner
- For any feature that touches the auth module, run /premortem with the security failure lens
```

These are advisory — Claude suggests the workflow, you confirm. Over time, the team builds a culture where the right analysis happens at the right moment. Update these rules whenever you catch a gap: "we should have run /premortem on that migration."

## Tune Effort Level per Phase

Different workflow phases need different reasoning depth. Parallel fan-out agents (individual `/stress-test` attack vectors, `/diverge` research agents) can run at lower effort because their value comes from diversity, not depth. Synthesis and orchestration phases need maximum reasoning.

Set `effort` in subagent definitions:
```yaml
---
name: fast-researcher
description: Quick research agent for parallel fan-out
model: sonnet
effort: medium
tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---
```

Combine with model selection for maximum cost efficiency:
- **Orchestrator**: Opus, effort high/max — deep reasoning about synthesis and decisions
- **Parallel workers**: Sonnet, effort medium — fast execution, diversity over depth
- **Lightweight tasks**: Haiku, effort low — classification, formatting, simple checks

## Front-Load Context with Bash Preprocessing

Skills can pre-compute expensive context before the prompt reaches Claude using the `` !`command` `` syntax in SKILL.md. This eliminates 3-5 tool-call round trips at the start of every invocation.

Example: a `/stress-test` skill that starts with project state already loaded:
```markdown
## Project Context
- Changed files: !`git diff --name-only HEAD~5`
- Test count: !`find . -name '*.test.*' -not -path '*/node_modules/*' | wc -l`
- Dependencies: !`cat package.json | jq '.dependencies | keys[]' 2>/dev/null | head -20`
- Recent CI status: !`gh run list --limit 3 --json conclusion,name 2>/dev/null`
```

The commands run immediately when the skill is invoked. Claude receives the actual output, not the commands. This is especially valuable for skills that need to understand project state before spawning agents.

## Set Up Worktree Environments Automatically

Skills that use git worktrees (`/diverge-prototype`, `/crossbreed`) need dependencies installed in each worktree. Without this, prototype agents waste time on `npm install` or fail on missing packages.

Add a `WorktreeCreate` hook to `.claude/settings.json`:
```json
{
  "hooks": {
    "WorktreeCreate": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$WORKTREE_PATH\" && if [ -f package.json ]; then npm install --silent 2>/dev/null; elif [ -f requirements.txt ]; then pip install -q -r requirements.txt 2>/dev/null; elif [ -f go.mod ]; then go mod download 2>/dev/null; fi"
          }
        ]
      }
    ]
  }
}
```

Every worktree starts with a working environment. Prototype agents can immediately build and test rather than spending their first 5 turns on setup.

## Format Code Automatically

Use a PostToolUse hook to auto-format every file Claude edits. This handles the last 10% of formatting and avoids CI failures.

Add to `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

Replace `prettier` with your project's formatter (`black` for Python, `gofmt` for Go, etc.).

## Set Up Notifications

These workflow skills spawn multiple agents and can take minutes. Set up notifications so you can switch to other work.

Add to `~/.claude/settings.json`:

**macOS:**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

**Linux:**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Claude Code needs your attention'"
          }
        ]
      }
    ]
  }
}
```

## Pre-Allow Safe Permissions

Avoid unnecessary permission prompts during multi-agent workflows. Use `/permissions` to pre-allow commands you know are safe:

```
/permissions
```

Common safe additions for workflow skills:
- `Bash(git *)` — git operations
- `Bash(npm test *)` — running tests
- `Bash(npx prettier *)` — formatting
- `Bash(python *)` — running scripts (for brainstorm backend)

These go in `.claude/settings.json` under `permissions.allow` and can be shared with the team:

```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(npm test *)",
      "Bash(npx prettier *)"
    ]
  }
}
```

Never use `--dangerously-skip-permissions` outside of a sandbox. Use `--permission-mode=dontAsk` for fully autonomous long-running sessions in sandboxed environments.

## Run Parallel Sessions

These workflow skills are designed for parallel work. Common patterns:

### Local + Web in Parallel

Run a workflow locally in your terminal while kicking off another on [claude.ai/code](https://claude.ai/code):

```bash
# Terminal: deep exploration
/brainstorm 30 ideas for the caching layer

# Web (claude.ai/code): prototype the current best candidate
/diverge-prototype path/to/prd.md
```

Use `&` to hand off a local session to the web, or `--teleport` to move sessions between environments.

### Multiple Terminal Sessions

Use git worktrees to run multiple Claude Code sessions on the same repo without conflicts:

```bash
# Session 1: main branch
cd ~/myproject
claude

# Session 2: isolated worktree
git worktree add ../myproject-exploration
cd ../myproject-exploration
claude
```

### Long-Running Autonomous Sessions

For workflows that take 10+ minutes (deep `/brainstorm`, `/diverge-prototype` with many variants):

```bash
# In a sandbox or trusted environment
claude --permission-mode=dontAsk -p "/diverge-prototype prd.md --count 5"
```

## Share Workflow Configuration With Your Team

Check these into version control so the whole team benefits:

### CLAUDE.md — Shared Project Instructions

```bash
# .claude/CLAUDE.md
# Add workflow-specific instructions
echo "After any architecture decision, run /premortem before prototyping." >> .claude/CLAUDE.md
```

Update CLAUDE.md whenever you see Claude make a mistake — this is compounding engineering. During code review, tag `@.claude` to add instructions as part of the PR (requires the [Claude Code GitHub Action](https://code.claude.com/docs/en/github-action)).

### Shared Settings

```bash
# .claude/settings.json — shared permissions and hooks
# .mcp.json — shared MCP server config (Slack, BigQuery, etc.)
```

### Shared Skills

```bash
# .claude/skills/ — project-specific workflow skills
# Copy relevant skills from this repo:
cp -r skills/premortem/SKILL.md .claude/commands/premortem.md
cp -r skills/stress-test/SKILL.md .claude/commands/stress-test.md
```

## Model Selection

Use the best model for the job:

- **Opus 4.5/4.6 with thinking** — for the main orchestrator and complex skills (brainstorm, converge, premortem). Even though it's slower, you steer less and get better tool use, so total time is often less than a faster model.
- **Sonnet** — for worker agents in parallel workflows (stress-test attack agents, diverge research agents). Set `model: sonnet` in agent definitions to save cost on parallel spawns.
- **Haiku** — for lightweight tasks (code formatting checks, simple classification in triage).

Configure per-skill model selection in agent definitions:

```markdown
---
name: fast-researcher
description: Quick research agent for parallel workflows
model: sonnet
tools: Read, Grep, Glob, Bash
---
```

## Recommended Workflow Chains

These are the most common chains for different situations. Start here and adapt:

### New Feature (High Risk)
```
Plan mode → /brainstorm → /diverge → /converge → /premortem → /diverge-prototype → /stress-test → /simplify → /scaffold
```

### New Feature (Low Risk)
```
Plan mode → /diverge → /converge → /diverge-prototype → /simplify → /scaffold
```

### Architecture Decision
```
Plan mode → /diverge → /converge → /premortem → decide
```

### Post-Implementation Review
```
/stress-test → /simplify → commit
```

### Bug Investigation
```
/bisect → fix → /stress-test on the fix
```

### Compress Research
```
/diverge → /distill → share with team
```
