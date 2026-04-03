# Diverge

Multi-perspective parallel research. Spawns N independent agents with uncorrelated context windows to explore a question from different angles, then synthesizes findings into a unified analysis and draft PRD.

## When to Use

- You need to research a topic thoroughly before designing or building
- The problem has multiple dimensions (technical, UX, risk, scale) that benefit from independent exploration
- You want high-confidence findings backed by convergence across independent agents

## Usage

```
/diverge [N] <research question or topic>
```

**Examples:**

```
/diverge How should we implement real-time collaboration?
/diverge 5 "What authentication system best fits our microservices architecture?"
```

N sets the agent count (default: 3, range: 2-7).

## How It Works

1. **Frame** -- Write a research brief (core question, known constraints, dimensions of exploration). Confirm with the user.
2. **Spawn** -- Launch N agents in parallel, each with a unique research lens (e.g., prior art, first-principles design, failure modes, scale, contrarian). Agents do not share context.
3. **Synthesize** -- Merge all findings: convergence points (high confidence), divergence points (tensions), unique insights, and consolidated recommendations.
4. **Draft PRD** -- Produce a mini-PRD with problem statement, goals/non-goals, requirements with verifiable acceptance criteria, and open questions. Saved as `prd_<topic>.md`.

## Output

- A unified synthesis presented inline
- A PRD file at `prd_<slugified_topic>.md` in the working directory

## Pipeline Connections

- **Before:** `/brainstorm` for initial ideation, `/fracture` for problem decomposition
- **After:** `/converge` for structured debate, `/diverge-prototype` for parallel prototyping, `/premortem` for risk assessment

## Tips

- Assign lenses that are as uncorrelated as possible. A "prior art" lens and a "first-principles" lens will produce more diverse findings than two similar technical lenses.
- Use the PRD output directly as input to `/diverge-prototype` or `/premortem`.
