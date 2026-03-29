# Agent Workflows

Experimental multi-agent workflow patterns for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Four skills that orchestrate parallel agents to research, brainstorm, prototype, and debate.

## Skills

### [brainstorm](skills/brainstorm/)
Structured ideation with shape-uniqueness enforcement. Researches prior art, then generates N ideas where each one is structurally distinct from all others. Use when exploring solution spaces, designing features, or making architecture decisions.

### [diverge](skills/diverge/)
Multi-perspective research. Spawns N independent agents with different lenses (technical, UX, risk) to explore a question. Synthesizes findings into a PRD. Use before building, when you need to understand trade-offs.

### [diverge-prototype](skills/diverge-prototype/)
Parallel prototyping. Spawns N agents in isolated git worktrees to build different implementations of a PRD, then compares results. Use for architecture spikes and implementation exploration.

### [converge](skills/converge/)
Structured debate. Takes divergent findings and runs moderated rounds where agents advocate positions, challenge each other, and propose compromises. Use when resolving tensions or making architectural decisions.

## The Diverge-Converge Pipeline

These skills chain together into a research-to-implementation pipeline:

```
/diverge  >  /converge  >  /diverge-prototype  >  pick winner
 research      debate        build prototypes       ship
```

See `examples/` for walkthroughs of how to use them together:
- [Full pipeline](examples/diverge-converge-pipeline.md)
- [Standalone ideation session](examples/brainstorm-solo.md)
- [Fast debate on known options](examples/quick-decision.md)

## Installation

Copy the skills you want into your Claude Code configuration:

```bash
# Global (available in all projects)
cp -r skills/brainstorm ~/.claude/skills/brainstorm
cp -r skills/diverge/SKILL.md ~/.claude/commands/diverge.md
cp -r skills/diverge-prototype/SKILL.md ~/.claude/commands/diverge-prototype.md
cp -r skills/converge/SKILL.md ~/.claude/commands/converge.md

# Project-scoped (one project only)
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

## Design Principles

1.** Diverge before you converge.** The first idea is rarely the best. Force volume and variety before evaluating.
2.** Independence produces insight.** Agents that do not share context produce different findings from varied perspectives. 
3.**Disagreement is signal.** When agents conflict, the conflict reveals something about the ambiguity of the problem.
4.**Prototypes beat debates.** At some point, stop talking and build multiple versions. Let code argue.
5.**Composition over monoliths.** Each skill does one thing. Chain them for complex workflows.

## License

MIT
