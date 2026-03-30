# Converge

Structured debate and refinement using Agent Teams. Takes divergent findings and spawns a team where teammates advocate for different positions, debate trade-offs, and converge on a refined synthesis.

## When to Use

- You have multiple competing approaches from `/diverge` or independent research and need to pick a direction
- A decision has real trade-offs and you want the strongest arguments for each side before committing
- A PRD has open tensions that need resolution through structured debate

## Usage

```
/converge [N] [path/to/diverge_output.md or inline topic]
```

**Examples:**

```
/converge prd_authentication.md
/converge 4 "REST vs GraphQL vs gRPC for our internal API"
```

N sets the number of debaters (default: 3, range: 2-5). Requires Agent Teams to be enabled.

## How It Works

1. **Frame** -- Extract competing positions from input. Prepare a debate brief with the core question, positions, shared constraints, and evaluation criteria.
2. **Spawn Team** -- Create an agent team with one teammate per position. You (the lead) moderate.
3. **Debate Rounds** (2-3 rounds):
   - Round 1: Opening positions
   - Round 2: Challenges and responses
   - Round 3: Synthesis proposals (if still divergent)
4. **Synthesize** -- Produce a convergence report with resolved points, refined trade-offs, emerged positions, and a recommended path.
5. **Update Artifacts** -- If based on a PRD, update it with refined requirements.

## Output

- A convergence report presented inline
- Updated PRD file (if one was provided as input)

## Pipeline Connections

- **Before:** `/diverge` for parallel research, `/brainstorm` for initial ideation
- **After:** `/premortem` for risk assessment, `/diverge-prototype` for implementation

## Tips

- Teammates are instructed to steel-man competing positions, not straw-man them. If you notice weak engagement, the debate brief may need sharper position definitions.
- Keep debates to 2-3 rounds. Diminishing returns set in quickly and teams are expensive.
