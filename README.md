# Agent Workflows

Experimental patterns for multi-agent workflows in [Claude Code](https://docs.anthropic.com/en/docs/claude-code). These skills orchestrate parallel agents to research, brainstorm, prototype, and debate — turning Claude Code into a collaborative thinking tool, not just a code generator.

## Skills

| Skill | What it does | When to use it |
|-------|-------------|----------------|
| **[brainstorm](skills/brainstorm/)** | Structured ideation with shape-uniqueness enforcement. Researches prior art, then generates N ideas that must each be structurally distinct. | Exploring solution spaces, feature design, architecture decisions |
| **[diverge](skills/diverge/)** | Multi-perspective research. Spawns N independent agents with different lenses (technical, UX, risk, etc.) to explore a question, then synthesizes findings into a PRD. | Deep research before building, understanding trade-offs |
| **[diverge-prototype](skills/diverge-prototype/)** | Divergent prototyping. Spawns N agents in isolated git worktrees to build different implementations of a PRD, then compares results. | Exploring implementation approaches, architecture spikes |
| **[converge](skills/converge/)** | Structured debate. Takes divergent findings and runs moderated rounds where agents advocate positions, challenge each other, and propose compromises. | Resolving tensions from research, making architectural decisions |

## The Diverge-Converge Pipeline

These skills compose into a full research-to-implementation pipeline:

```
/diverge  →  /converge  →  /diverge-prototype  →  pick winner
 research     debate         build prototypes       ship
```

See [examples/](examples/) for walkthroughs of how to use them together.

## Installation

Copy the skills you want into your Claude Code configuration:

```bash
# Option 1: Install as global skills (available in all projects)
cp -r skills/brainstorm ~/.claude/skills/brainstorm
cp -r skills/diverge ~/.claude/commands/diverge.md      # or ~/.claude/skills/diverge/
cp -r skills/diverge-prototype ~/.claude/commands/diverge-prototype.md
cp -r skills/converge ~/.claude/commands/converge.md

# Option 2: Install as project skills (available in one project)
cp -r skills/brainstorm .claude/skills/brainstorm
cp -r skills/diverge/SKILL.md .claude/commands/diverge.md
cp -r skills/diverge-prototype/SKILL.md .claude/commands/diverge-prototype.md
cp -r skills/converge/SKILL.md .claude/commands/converge.md
```

### Brainstorm setup

The brainstorm skill has a Python backend for tracking ideas and enforcing uniqueness:

```bash
cd skills/brainstorm/scripts
python3 -m venv .venv
source .venv/bin/activate
pip install sentence-transformers numpy  # optional: enables semantic similarity
```

Without `sentence-transformers`, brainstorm falls back to lexical similarity only — still useful, just less precise at detecting same-shape ideas.

### Converge prerequisites

The converge skill requires Claude Code Agent Teams:

```json
// In your Claude Code settings
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Philosophy

These workflows are built on a few core beliefs:

1. **Diverge before you converge.** The first idea is almost never the best. Force volume and variety before evaluating.
2. **Independence produces insight.** Agents that don't share context will find different things. That's the point.
3. **Tension is signal.** When agents disagree, the disagreement itself reveals something about the problem.
4. **Prototypes beat debates.** At some point, stop talking and build multiple versions. Let code be the argument.
5. **Composition over monoliths.** Each skill does one thing. Chain them for complex workflows.

## Contributing

This is an evolving collection. Ideas welcome — open an issue or PR if you have a workflow pattern that works well with multi-agent orchestration.

## License

MIT
