# Brainstorm

Constrained divergent ideation with shape-uniqueness enforcement. Forces volume and structural novelty by rejecting ideas that share the same shape as prior art or any previously accepted idea.

## When to Use

- You are exploring solutions to a problem and want to go far beyond the obvious first ideas
- The problem space is well-known enough that existing approaches should be mapped before ideating
- You need a large volume of structurally distinct ideas before evaluating any of them

## Usage

```
/brainstorm [count] <problem statement>
```

**Examples:**

```
/brainstorm How to reduce API latency below 50ms
/brainstorm 15 Ways to handle offline-first sync in a mobile app
```

The optional count sets the idea target (default: 30).

## How It Works

1. **Setup** -- Parse the problem statement and initialize a session with a target idea count.
2. **Research** -- Search for existing approaches, algorithms, and known solutions. Record 5-10 structurally distinct families as prior art (these become the exclusion zone).
3. **Diverge** -- Generate ideas one at a time. Each idea passes through a text uniqueness gate and a code prototype uniqueness gate. Rejected ideas must change shape, not just surface details.
4. **Converge** -- Rate all ideas on feasibility, novelty, and impact (1-5 each). Cluster, select top candidates, and generate a convergence report.

Each accepted idea gets a minimal prototype (20-50 lines) in a sandbox to prove it is computationally distinct from all others.

## Output

- A convergence report at `.brainstorm/<session-id>/report.md`
- Individual idea files at `.brainstorm/<session-id>/ideas/NNN.md`
- Prototype sandboxes at `.brainstorm/<session-id>/sandboxes/`

## Pipeline Connections

- **Before:** Use when starting from scratch on an open problem
- **After:** Feed top ideas into `/diverge` for deeper research, or `/diverge-prototype` for implementation exploration

## Tips

- Do not evaluate ideas during the diverge phase. "That won't work" is banned until convergence. Volume before quality.
- If momentum stalls, check which structural territory has not been covered yet using the `phase` command.
