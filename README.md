# Agent Workflows

Experimental multi-agent workflow patterns for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Ten skills that orchestrate parallel agents to research, brainstorm, prototype, debate, stress-test, and plan.

## Skills

### Ideation & Research

#### [brainstorm](skills/brainstorm/)
Structured ideation with shape-uniqueness enforcement. Researches prior art, then generates N ideas where each one is structurally distinct from all others. Use when exploring solution spaces, designing features, or making architecture decisions.

#### [diverge](skills/diverge/)
Multi-perspective research. Spawns N independent agents with different lenses (technical, UX, risk) to explore a question. Synthesizes findings into a PRD. Use before building, when you need to understand trade-offs.

### Decision & Debate

#### [converge](skills/converge/)
Structured debate. Takes divergent findings and runs moderated rounds where agents advocate positions, challenge each other, and propose compromises. Use when resolving tensions or making architectural decisions.

### Risk & Validation

#### [premortem](skills/premortem/)
Prospective failure analysis. Spawns N agents that each write a narrative from the future where the project failed, each for a different root cause. Synthesizes into a risk registry with severity ratings and mitigations. Based on Klein's premortem technique: starting from "it failed" bypasses planning fallacy and surfaces failure modes that optimism bias normally hides.

#### [stress-test](skills/stress-test/)
Parallel adversarial analysis. Spawns N agents each tasked with breaking a design or codebase from a different attack vector (security, scale, concurrency, edge cases, dependencies, data integrity, operations). Produces a vulnerability map with severity ratings and fixes.

### Prototyping & Recombination

#### [diverge-prototype](skills/diverge-prototype/)
Parallel prototyping. Spawns N agents in isolated git worktrees to build different implementations of a PRD, then compares results. Use for architecture spikes and implementation exploration.

#### [crossbreed](skills/crossbreed/)
Structural recombination. Takes 2-3 existing prototypes and spawns agents to create hybrid designs, each with a different dominant parent. Documents grafting decisions and seam risks. Use when the best solution combines elements from multiple prototypes.

### Planning & Analysis

#### [scaffold](skills/scaffold/)
Build-order planning. Spawns N agents that each propose a different sequencing strategy (riskiest-first, demo-able-first, vertical slice, dependency-order, test-infra-first). Synthesizes into a recommended build plan with milestones.

#### [distill](skills/distill/)
Progressive compression. Runs an artifact through a chain of agents, each compressing by 50%. The key insight: what gets dropped at each layer reveals the priority hierarchy. The waste product is the signal. Use on any large artifact to find what actually matters.

### Debugging

#### [bisect](skills/bisect/)
Binary search for root cause. Uses agents to perform binary search through git history, configuration space, or dependency versions to isolate a regression. Adaptive topology: each step depends on the previous result.

## The Pipeline

These skills chain together. The core pipeline runs research through implementation, with risk and validation gates:

```
                        /brainstorm
                        (ideation)
                            |
                        /diverge
                        (research)
                            |
                        /converge
                         (debate)
                            |
                       /premortem
                       (risk gate)
                            |
                    /diverge-prototype
                     (build variants)
                       /          \
                /crossbreed    /stress-test
                (recombine)    (validate)
                       \          /
                       pick winner
                            |
                        /scaffold
                       (build plan)
                            |
                      implementation
```

Not every project needs every step. Common shorter paths:

**Quick decision** (you already know the options):
```
/converge  >  /premortem  >  build
```

**Architecture spike** (you have a PRD):
```
/diverge-prototype  >  /stress-test  >  pick winner  >  /scaffold
```

**Deep exploration** (greenfield problem):
```
/brainstorm  >  /diverge  >  /converge  >  /premortem  >  /diverge-prototype  >  /stress-test  >  /scaffold
```

**Post-hoc analysis** (compress any large artifact):
```
/diverge output  >  /distill  >  priority hierarchy
```

**Debugging** (standalone):
```
bug report  >  /bisect  >  root cause + fix
```

See `examples/` for detailed walkthroughs:
- [Full pipeline](examples/diverge-converge-pipeline.md)
- [Standalone ideation session](examples/brainstorm-solo.md)
- [Fast debate on known options](examples/quick-decision.md)

## Installation

### Option 1: Plugin (recommended)

Install the whole repo as a Claude Code plugin. You get all 10 skills, 3 pipeline agents, hooks for formatting/notifications/verification/worktree setup, and diff-aware scoping — in one step.

```bash
# Clone the repo
git clone https://github.com/sjarmak/agent-workflows.git

# Load it as a plugin
claude --plugin-dir ./agent-workflows
```

Skills are available as `/agent-workflows:<skill-name>`:
```
/agent-workflows:diverge "How should we design the auth system?"
/agent-workflows:premortem path/to/design.md
/agent-workflows:stress-test src/auth/
```

Pipeline agents are available via `/agents` or directly:
```bash
claude --agent agent-workflows:full-pipeline "How should we redesign the auth system?"
claude --agent agent-workflows:security-pipeline src/api/
```

To load the plugin automatically for all sessions, add it to your project's `.claude/settings.json`:
```json
{
  "plugins": ["./path/to/agent-workflows"]
}
```

### Option 2: Copy individual skills

Copy just the skills you want into your Claude Code configuration:

```bash
# Global (available in all projects)
cp -r skills/brainstorm ~/.claude/skills/brainstorm
cp -r skills/diverge/SKILL.md ~/.claude/commands/diverge.md
cp -r skills/converge/SKILL.md ~/.claude/commands/converge.md
cp -r skills/premortem/SKILL.md ~/.claude/commands/premortem.md
cp -r skills/stress-test/SKILL.md ~/.claude/commands/stress-test.md
cp -r skills/diverge-prototype/SKILL.md ~/.claude/commands/diverge-prototype.md
cp -r skills/crossbreed/SKILL.md ~/.claude/commands/crossbreed.md
cp -r skills/scaffold/SKILL.md ~/.claude/commands/scaffold.md
cp -r skills/distill/SKILL.md ~/.claude/commands/distill.md
cp -r skills/bisect/SKILL.md ~/.claude/commands/bisect.md

# Project-scoped (one project only)
cp -r skills/brainstorm .claude/skills/brainstorm
cp -r skills/diverge/SKILL.md .claude/commands/diverge.md
cp -r skills/converge/SKILL.md .claude/commands/converge.md
cp -r skills/premortem/SKILL.md .claude/commands/premortem.md
cp -r skills/stress-test/SKILL.md .claude/commands/stress-test.md
cp -r skills/diverge-prototype/SKILL.md .claude/commands/diverge-prototype.md
cp -r skills/crossbreed/SKILL.md .claude/commands/crossbreed.md
cp -r skills/scaffold/SKILL.md .claude/commands/scaffold.md
cp -r skills/distill/SKILL.md .claude/commands/distill.md
cp -r skills/bisect/SKILL.md .claude/commands/bisect.md
```

### Option 3: Copy hooks and agents separately

To get the automation without the plugin:

```bash
# Copy agents to your global config
cp agents/code-simplifier.md ~/.claude/agents/
cp agents/full-pipeline.md ~/.claude/agents/
cp agents/security-pipeline.md ~/.claude/agents/

# Copy the hooks configuration to your project
# (merge with existing hooks in .claude/settings.json if you have them)
cat hooks/hooks.json
```

### Brainstorm setup

The brainstorm skill has a Python backend for tracking ideas and enforcing uniqueness:

```bash
cd skills/brainstorm/scripts
python3 -m venv .venv
source .venv/bin/activate
pip install sentence-transformers numpy
```

`sentence-transformers` is optional. Without the package, brainstorm falls back to lexical similarity only. Still functional, less precise at detecting same-shape ideas.

### Converge prerequisites

The converge skill requires Claude Code Agent Teams. Add this to your Claude Code settings:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Best Practices

See [BEST_PRACTICES.md](BEST_PRACTICES.md) for the full guide. Key points:

- **Plan first, then execute.** Start every workflow in Plan mode (`Shift+Tab` twice). Iterate on the plan, then switch to auto-accept for execution.
- **Scope to changed files.** A `UserPromptSubmit` hook injects `git diff` into context so skills auto-focus on what you actually changed.
- **Isolate with context:fork.** Run verbose skills in forked subagent context so only the synthesis returns to your main conversation.
- **Chain skills into pipelines.** Use `initialPrompt` in agent definitions to run `/diverge` then `/converge` then `/premortem` as a single invocation.
- **Add guard rails.** `PreToolUse` hooks prevent analysis agents from modifying code and brainstorm agents from executing outside sandboxes.
- **Add routing rules.** Put project-specific trigger conditions in CLAUDE.md: "For auth changes, run /premortem with security lens."
- **Front-load context.** Use `` !`command` `` syntax in skills to pre-compute git state, test counts, and dependency info before Claude starts.
- **Verify everything.** Use Stop hooks, background verification agents, or `/simplify` after code generation.
- **Set up notifications.** These skills spawn multiple agents and take minutes. Use a `Notification` hook so you can context-switch.

## Design Principles

1. **Diverge before you converge.** The first idea is rarely the best. Force volume and variety before evaluating.
2. **Independence produces insight.** Agents that do not share context produce different findings from varied perspectives.
3. **Disagreement is signal.** When agents conflict, the conflict reveals something about the ambiguity of the problem.
4. **Prototypes beat debates.** At some point, stop talking and build multiple versions. Let code argue.
5. **Composition over monoliths.** Each skill does one thing. Chain them for complex workflows.
6. **Failure is a lens.** Starting from "it failed" surfaces risks that optimism bias hides. Use premortem before committing.
7. **Adversarial pressure reveals truth.** Agents tasked with breaking a design find what cooperative agents miss.

## License

MIT
