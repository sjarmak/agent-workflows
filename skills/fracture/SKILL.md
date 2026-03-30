Competitive Problem Decomposition. Spawns N independent agents, each proposing a DIFFERENT decomposition of a problem into subproblems using a distinct structural lens. One decomposes by user journey, another by data flow, another by failure domain, another by team boundary, another by deployment unit. Synthesizes into a comparison of decomposition strategies with convergence analysis and a recommended framing.

## Arguments

$ARGUMENTS — format: `[N] [path/to/problem.md or inline description]` where N is optional decomposition-lens count (default: 5, min 3, max 7)

## Parse Arguments

Extract:

- **agent_count**: the optional leading integer (default 5, min 3, max 7)
- **input**: path to a problem description, design document, PRD, or feature spec — or an inline problem description

If the input is missing or unclear, ask the user to clarify before proceeding.

## Phase 1: Frame the Problem

**If a file path is given**: read it and extract the key goals, constraints, stakeholders, technical context, and scope.

**If inline**: parse the problem description.

Prepare a **problem brief** that includes:

- What the problem is (1-2 sentences)
- Who the stakeholders are
- Known constraints (technical, organizational, timeline)
- Current assumptions
- Scale expectations (users, data volume, team size)
- What "solved" looks like (success criteria)

Present the problem brief to the user and confirm before proceeding. Adjust if the user gives feedback.

## Phase 2: Spawn Decomposition Agents

Launch **all N agents in parallel** using the Agent tool. Each agent gets the same problem brief and a unique **decomposition lens** — a structural perspective through which to break the problem apart.

### Standard Decomposition Lenses

Select N from the following (rotate starting selection across invocations to avoid bias; always include a mix of user-facing and system-facing lenses):

1. **User Journey Decomposition** — break the problem along the paths users take. Each subproblem corresponds to a distinct user goal, workflow, or interaction sequence. Boundaries fall where the user's mental model shifts.
2. **Data Flow Decomposition** — break the problem along how data moves. Each subproblem owns a stage: ingestion, transformation, storage, retrieval, presentation. Boundaries fall where data changes shape or crosses a trust boundary.
3. **Failure Domain Decomposition** — break the problem along what can break independently. Each subproblem is a blast radius — a component whose failure should not cascade. Boundaries fall where you want isolation.
4. **Team Boundary Decomposition** — break the problem along who owns what. Each subproblem maps to a team or role with clear ownership, interface contracts, and independent release cycles. Boundaries fall where communication overhead should be minimized.
5. **Deployment Unit Decomposition** — break the problem along what ships independently. Each subproblem is a deployable artifact with its own lifecycle, scaling profile, and rollback boundary. Boundaries fall where release cadences differ.
6. **API Surface Decomposition** — break the problem along the contracts between components. Each subproblem is defined by the interfaces it exposes and consumes. Boundaries fall where you want stability and backward compatibility.
7. **Temporal/Lifecycle Decomposition** — break the problem along when things happen. Each subproblem owns a phase: setup, steady-state, migration, scaling, deprecation. Boundaries fall where the system's behavior fundamentally changes over time.

Each agent MUST produce:

1. A **complete decomposition tree** — not just top-level splits, but 2-3 levels deep. Each node has a name, a one-sentence description, and its children.
2. **Rationale** — why this lens is appropriate for this specific problem (not generic arguments for the lens)
3. **Dependencies between subproblems** — which subproblems must be solved before others, and which can proceed in parallel
4. **What this decomposition makes easy** — which questions, decisions, and implementation tasks become straightforward under this framing
5. **What this decomposition makes hard** — which concerns get scattered across multiple subproblems or fall between the cracks
6. **Blind spots** — what this decomposition systematically hides or de-emphasizes
7. Use `subagent_type: "general-purpose"` (they may need web search or codebase exploration for context)
8. NOT be told what other agents are exploring

Agent prompt template (customize the lens per agent):

```
You are a systems analyst decomposing a problem using a specific structural lens.

## Problem Brief
{problem_brief}

## Your Decomposition Lens: {lens_name}
{lens_description}

## Instructions
Decompose the problem using ONLY your assigned lens. Your output must be a complete decomposition tree — not a list of topics, but a structured breakdown where every node has children and every leaf is a concrete, actionable subproblem.

Be SPECIFIC. Reference actual components, stakeholders, and constraints from the problem brief. Do not produce a generic decomposition that could apply to any problem.

## Output Format
### Decomposition: {lens_name}

#### Rationale
[2-3 sentences: why this lens is a good fit for THIS specific problem]

#### Decomposition Tree
- **[Subproblem 1 Name]**: [one-sentence description]
  - **[1.1 Name]**: [description]
    - **[1.1.1 Name]**: [description]
  - **[1.2 Name]**: [description]
    - **[1.2.1 Name]**: [description]
- **[Subproblem 2 Name]**: [one-sentence description]
  - **[2.1 Name]**: [description]
  - ...
[Continue for all top-level subproblems. Go 2-3 levels deep.]

#### Dependency Map
- [Subproblem X] must precede [Subproblem Y] because [reason]
- [Subproblem A] and [Subproblem B] can proceed in parallel because [reason]
[List all critical ordering constraints]

#### What This Decomposition Makes Easy
- [Specific question or task that becomes straightforward]
- ...

#### What This Decomposition Makes Hard
- [Specific concern that gets scattered or buried]
- ...

#### Blind Spots
- [What this decomposition systematically hides or under-weights]
- ...
```

## Phase 3: Synthesize

After ALL agents return, produce the following synthesis:

### 1. Decomposition Comparison Table

| Lens | Top-Level Subproblems | Depth | Parallelizable? | Strength | Weakness |
| ---- | --------------------- | ----- | --------------- | -------- | -------- |

One row per decomposition. Keep entries concise.

### 2. Convergence Points

Subproblems that appear across multiple decompositions, possibly under different names. For each convergence point:

- The subproblem (described in lens-neutral terms)
- Which decompositions surfaced it (and what they called it)
- Why this convergence is significant — it means this subproblem is structurally fundamental regardless of framing

These are the highest-confidence subproblems. They should appear in any implementation plan.

### 3. Unique Insights

Subproblems or concerns that appeared in only ONE decomposition. For each:

- The insight and which lens produced it
- Why the other lenses missed it (structural reason, not oversight)
- Whether it represents a genuine blind spot or a lens-specific artifact

### 4. Blind Spot Matrix

| Concern | User Journey | Data Flow | Failure Domain | Team Boundary | Deployment Unit | API Surface | Temporal |
| ------- | ------------ | --------- | -------------- | ------------- | --------------- | ----------- | -------- |

Mark each cell: "Addressed", "Partial", or "Blind spot". Only include columns for lenses that were actually used. This table reveals which concerns require combining lenses.

### 5. Recommended Decomposition

Based on the analysis, recommend ONE of the following:

- **Single lens**: if one decomposition clearly dominates for this problem, recommend it with rationale
- **Hybrid**: if the best framing combines elements of 2-3 lenses, describe the hybrid and which parts come from which lens
- **Layered**: if different lenses are best at different levels of abstraction, recommend a primary lens for top-level splits with a secondary lens for leaf-level refinement

For the recommendation, explain:

- Why this framing fits the problem's specific constraints
- What the recommended framing still misses (inherited blind spots)
- How to compensate for those blind spots during implementation

### 6. Per-Agent Summaries

For each decomposition, include a 2-3 sentence summary of its most distinctive contribution.

Save the full output to a file `fracture_{slugified_topic}.md` in the working directory.

## Phase 4: Present and Suggest Next Steps

Present the comparison table, convergence points, and recommended decomposition to the user. Ask:

- Does the recommended decomposition match your intuition, or does a different lens feel more natural?
- Are there convergence points that surprise you or that you expected but are missing?
- Should we proceed with the recommended framing?

Suggest next steps based on the pipeline:

- If the problem is now well-framed: suggest `/diverge` to explore solution approaches within the chosen decomposition
- If there is high uncertainty in the decomposition: suggest `/brainstorm` on the most ambiguous subproblems
- If the decomposition reveals architectural risk: suggest `/premortem` on the recommended framing before proceeding

## Rules

- **Independence is critical**: agents must NOT share context. Each decomposition lens explores independently. Do not include other agents' decompositions in any agent's prompt.
- **All agents launch in a single parallel batch**: use one message with N Agent tool calls.
- **Complete trees, not topic lists**: each agent must produce a multi-level decomposition tree, not a flat list of subproblems. Reject outputs that are only top-level splits.
- **Specific, not generic**: every decomposition must reference actual components and constraints from the problem brief. A decomposition that could apply to any problem is a failed decomposition.
- **No premature solving**: agents decompose the problem structure, they do not propose solutions. If an agent starts solutioning, the decomposition has gone too deep.
- **Preserve all decompositions**: even decompositions that feel like a poor fit contain useful signal about what the problem is NOT shaped like. Do not filter or discard any agent's output.
- **Attribute insights**: always note which lens produced which finding in the synthesis.
- **Be honest about blind spots**: every decomposition has them. An agent that claims no blind spots has not thought deeply enough.

## Pipeline Position

Sits before `/diverge` as a framing step. The question `/fracture` answers is "how should we structure this problem?" — only after that is answered should you ask "how should we solve it?"

```
/brainstorm (explore) -> /fracture (frame) -> /diverge (solve) -> /converge (decide)
```

Also useful after `/distill` when a large artifact reveals a complex problem that needs structural decomposition before action.
