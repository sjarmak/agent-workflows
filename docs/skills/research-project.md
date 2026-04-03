# Research Project

Run the full diverge-converge-premortem pipeline as a single invocation to produce a risk-annotated PRD.

## When to Use

- You have a feature idea or problem statement and want a thorough, multi-perspective PRD before building
- The problem space is complex enough that you want independent research, structured debate, and failure analysis
- You want to go from idea to risk-annotated PRD in one command

## Usage

```
/research-project [N] "topic or feature description"
```

**Examples:**

```
/research-project "How should we redesign the auth system?"
/research-project 5 "Real-time collaboration for our editor"
```

N sets the agent count per phase (default: 3, range: 2-6).

## How It Works

1. **Diverge** -- Spawn N independent research agents, each exploring the topic from a different lens (technical, UX, risk, prior art, first principles). Produces a draft PRD with synthesized findings.
2. **Converge** -- Run a structured debate where agents advocate competing positions, challenge assumptions, and reach consensus. Refines the PRD with explicit trade-offs.
3. **Premortem** -- Spawn N agents who each write a failure narrative from the future. Synthesizes into a risk registry and annotates the PRD with top risks and mitigations.

## Output

- A risk-annotated PRD file
- Summary of key convergence decisions
- Top 3 risks with mitigations
- Recommended next step

## Pipeline Connections

- **Before:** `/brainstorm` for ideation when the problem space is vague
- **After:** `/prd-build` to decompose and implement in parallel, `/scaffold` for build-order planning, or `/diverge-prototype` to spike implementations

## Tips

- Skip `/brainstorm` if the problem space is already well-understood and jump straight to `/research-project`.
- The recommended next step is usually `/prd-build <prd-path>` for automated parallel implementation.
- For smaller projects, you can skip `/research-project` and go directly to `/scaffold` or `/focus`.
