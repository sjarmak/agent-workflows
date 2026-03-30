# Constraint Inversion

What-if constraint removal. Takes a design with stated constraints and spawns N agents, each removing one constraint to explore what becomes possible without it. Synthesizes findings into a constraint dependency map that reveals which constraints are load-bearing versus merely assumed.

## When to Use

- A design feels over-constrained and you suspect some constraints are assumed rather than truly necessary
- You want to validate that the constraints you are designing around are the right ones before committing
- A design is stuck and removing a constraint might reveal a path forward

## Usage

```
/constraint-inversion [N] [path/to/design.md or inline description]
```

**Examples:**

```
/constraint-inversion prd_payment_system.md
/constraint-inversion 5 "Our API must maintain backward compatibility with v2 clients"
```

N sets the agent count (default: 5, range: 3-7).

## How It Works

1. **Extract Constraints** -- Build a numbered constraint inventory from the design, classifying each by type (technical, organizational, financial, temporal, etc.) and source.
2. **Spawn** -- Launch N agents in parallel. Each removes exactly one constraint and explores what design changes become possible, what simplifies, what new capabilities emerge, and what breaks.
3. **Synthesize** -- Build a constraint dependency map (ASCII graph), classify constraints as load-bearing/assumed/partially load-bearing, summarize what becomes possible, and list actionable recommendations.

## Output

- A constraint dependency map and analysis saved to `constraint_inversion_<slugified_topic>.md`

## Pipeline Connections

- **Before:** `/brainstorm` or `/diverge` for exploration, `/converge` for initial decisions
- **After:** `/premortem` on a redesign that removes assumed constraints, `/diverge-prototype` to explore the opened design space

## Tips

- Constraints classified as "assumed" are candidates for negotiation with stakeholders -- they may yield significant design improvements at low risk.
- The dependency graph is the most actionable artifact: foundation constraints (many others depend on them) must be protected, while leaf constraints (nothing depends on them) are independently negotiable.
