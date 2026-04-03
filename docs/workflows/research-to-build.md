# Research-to-Build Workflow

The complete idea-to-implementation pipeline. Use `/research-project` to produce a risk-annotated PRD through multi-perspective research, structured debate, and failure analysis, then `/prd-build` to decompose and implement it with parallel agents.

## When to Use This Workflow

- Building a non-trivial feature where getting the design wrong would be expensive
- You want thorough research and risk assessment before writing code
- The implementation has multiple independent components that benefit from parallel execution
- You want end-to-end automation from idea to working code

## The Pipeline

```
/research-project  ──>  /prd-build  ──>  integration branch
   (research)           (implement)        (ready for review)
       |                     |
   diverge              decompose
   converge             dispatch agents
   premortem            review + merge
       |                     |
  risk-annotated PRD    working code
```

## Step-by-Step

1. **`/research-project`** -- Runs three phases in sequence:
   - **Diverge**: N independent agents research the topic from different perspectives (technical, UX, risk, prior art, first principles). Produces a draft PRD.
   - **Converge**: Structured debate resolves tensions and refines trade-offs. Updates the PRD.
   - **Premortem**: N agents write failure narratives. Annotates the PRD with a risk registry and mitigations.
   - Output: risk-annotated PRD file.

2. **`/prd-build`** -- Takes the PRD and automates implementation:
   - **Decompose**: Breaks the PRD into 5-10 work units with verifiable acceptance criteria, organized by dependency into layers.
   - **Execute**: Dispatches parallel agents in isolated worktrees, one per work unit. Each agent implements and tests. Separate review agents verify acceptance criteria.
   - **Land**: Merges passing work onto an integration branch. Retries evicted units.
   - **Verify**: Runs full test suite. Reports final status.
   - Output: integration branch with implemented code.

3. **Manual review** -- Review the integration branch diff, run any additional validation, and merge to main.

## Example Invocation

```
/research-project "Real-time collaboration for our editor"
# ... produces prd_realtime_collab.md

/prd-build prd_realtime_collab.md
# ... decomposes into units, dispatches agents, merges work

# Review the integration branch
git diff main...integration/prd-build-realtime-collab
```

## Variant: With Prototyping

For high-uncertainty projects, insert prototyping between research and build:

```
/research-project "topic"  >  /diverge-prototype  >  /stress-test  >  /prd-build
```

This spikes multiple implementations before committing to one, which is useful when the architecture decision depends on emergent properties.

## Variant: With Manual Build Planning

If you want more control over implementation order, replace `/prd-build` with `/scaffold` + `/focus`:

```
/research-project "topic"  >  /scaffold  >  /focus (work through beads one at a time)
```

This gives you sequential, human-in-the-loop execution instead of fully automated parallel builds.

## Tips

- Use `/prd-build --dry-run` after research to review the decomposition before committing to execution.
- If the premortem surfaces critical risks, address them in the PRD before running `/prd-build`.
- For smaller features (< 5 files changed), skip this workflow and use `/focus` directly.
- The research phase takes minutes per step. Use notification hooks so you can context-switch while agents work.
