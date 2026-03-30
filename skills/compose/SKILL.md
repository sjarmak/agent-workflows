Workflow Pipeline Builder. A meta-workflow that takes a goal and designs which existing workflow skills to chain together, in what order, with what parameters. Spawns agents to independently propose different workflow compositions for the same goal. The only workflow that operates on the WORKFLOW LAYER rather than the problem layer. Produces a recommended pipeline with rationale.

## Arguments

$ARGUMENTS — format: `[N] "goal description"` where N is optional pipeline-proposal count (default: 3, min 2, max 5)

## Parse Arguments

Extract:

- **agent_count**: the optional leading integer (default 3, min 2, max 5)
- **goal**: the quoted or unquoted goal description — what the user wants to achieve end-to-end

If the goal is missing or unclear, ask the user to clarify before proceeding.

## Phase 1: Analyze the Goal

Before spawning agents, classify the goal along five dimensions. For each dimension, assign a rating and a one-sentence justification:

| Dimension         | Rating                          | Justification                                                  |
| ----------------- | ------------------------------- | -------------------------------------------------------------- |
| **Novelty**       | Low / Medium / High             | How much prior art exists for this kind of problem?            |
| **Urgency**       | Low / Medium / High             | How time-sensitive is delivery?                                |
| **Risk Level**    | Low / Medium / High             | What is the blast radius if the solution is wrong?             |
| **Team Size**     | Solo / Small (2-4) / Large (5+) | How many people will execute?                                  |
| **Reversibility** | Easy / Moderate / Hard          | How costly is it to undo decisions made during implementation? |

Prepare a **goal analysis brief** that includes:

- The goal restated in one sentence
- The dimension ratings table above
- Key constraints or context from the conversation
- What "done" looks like for this goal

Present the goal analysis to the user and confirm before proceeding. Adjust if the user gives feedback.

## Phase 2: Spawn Pipeline Architects

Launch **all N agents in parallel** using the Agent tool. Each agent receives the goal analysis brief plus a unique **optimization stance** — the lens through which they design their pipeline. Assign stances 1 through N from this pool:

1. **"Speed-Optimized"** — Minimize time to working solution. Cut any skill that does not directly accelerate delivery. Motto: "ship it, then harden it."
2. **"Risk-Optimized"** — Minimize the chance of building the wrong thing or building it wrong. Front-load validation and failure analysis. Motto: "measure twice, cut once."
3. **"Thoroughness-Optimized"** — Maximize solution quality and coverage. Include every skill that adds signal, even at the cost of calendar time. Motto: "leave no stone unturned."
4. **"Creativity-Optimized"** — Maximize the chance of finding a non-obvious or breakthrough approach. Prioritize divergent exploration and recombination. Motto: "the best solution is one nobody proposed first."
5. **"Simplicity-Optimized"** — Minimize pipeline complexity. Use the fewest skills that still produce a sound result. Motto: "the best process is the one you actually follow."

Each agent MUST receive the full skill catalog (below) and use ONLY skills from this list:

```
SKILL CATALOG (18 skills):

brainstorm        — Constrained divergent ideation with shape-uniqueness enforcement
diverge           — Multi-perspective parallel research from independent angles
converge          — Structured debate and refinement via agent teams
premortem         — Prospective failure narratives to surface risks before building
stress-test       — Parallel adversarial attack surface analysis
diverge-prototype — Parallel prototyping in isolated worktrees
crossbreed        — Structural recombination of existing prototypes or designs
scaffold          — Build-order planning via competing sequencing strategies
distill           — Progressive compression and essence extraction from large artifacts
bisect            — Binary search for root cause of a regression or failure
entangle          — Dependent co-design of coupled systems
constraint-inversion — What-if constraint removal to find hidden possibilities
fracture          — Competitive problem decomposition into subproblems
replicate         — Independent verification by reimplementation
contract          — Specification generation from examples
diffuse           — Blast radius impact mapping for changes
migrate           — Parallel migration strategy exploration
compose           — (this skill) Recursive pipeline composition for sub-goals
```

Each agent MUST produce:

- **Pipeline name** — a short descriptive label
- **Optimization stance** — which stance they were assigned and what it optimizes for
- **Ordered skill sequence** — each step as:
  - Step number
  - Skill name (must be from the catalog)
  - Arguments/parameters to pass to the skill
  - What this step produces (its output artifact)
  - Why this step is at this position in the sequence
- **What this pipeline optimizes for** — the primary benefit of this ordering
- **What this pipeline sacrifices** — what is traded away for the optimization
- **Goal dimension fit** — how this pipeline accounts for the goal's novelty, urgency, risk, team size, and reversibility ratings
- **Estimated total pipeline duration** — rough calendar-time estimate in ranges

Agent prompt template (customize the stance per agent):

```
You are a workflow architect. Given a goal, you design which workflow skills to chain together, in what order, with what parameters.

## Goal Analysis
{goal_analysis_brief}

## Your Optimization Stance: {stance_name}
{stance_description}
Motto: "{motto}"

## Skill Catalog
{skill_catalog}

Design a complete workflow pipeline for this goal using your assigned optimization stance. Select skills ONLY from the catalog above. Order them to best serve your stance given this goal's characteristics (novelty, urgency, risk, team size, reversibility).

IMPORTANT:
- You may use any subset of skills — you do NOT need to use all of them.
- You may use the same skill more than once if it serves different purposes at different pipeline stages.
- You may use "compose" recursively if the goal has a sub-goal that itself needs pipeline planning.
- Every skill you include must have a clear justification for its position in the sequence.

## Output Format
Return your pipeline in this exact structure:

### Pipeline: {pipeline_name}
**Optimization stance:** {stance_name} — "{motto}"

#### Ordered Skill Sequence
| Step | Skill | Arguments | Output Artifact | Why Here |
|------|-------|-----------|-----------------|----------|
| 1 | {skill} | {args} | {output} | {rationale} |
| 2 | ... | ... | ... | ... |

#### What This Pipeline Optimizes For
{1-2 sentences}

#### What This Pipeline Sacrifices
{1-2 sentences}

#### Goal Dimension Fit
- Novelty ({rating}): {how pipeline handles it}
- Urgency ({rating}): {how pipeline handles it}
- Risk ({rating}): {how pipeline handles it}
- Team Size ({rating}): {how pipeline handles it}
- Reversibility ({rating}): {how pipeline handles it}

#### Estimated Duration
{range estimate with assumptions}
```

Use `subagent_type: "general-purpose"` and do NOT use worktrees (pipeline design only, no code).

## Phase 3: Compare Pipelines

After ALL agents return, produce a unified comparison:

### 1. Pipeline Comparison Table

| Dimension                              | Pipeline A | Pipeline B | Pipeline C | ... |
| -------------------------------------- | ---------- | ---------- | ---------- | --- |
| Total skills used                      | ...        | ...        | ...        |     |
| Estimated duration                     | ...        | ...        | ...        |     |
| First skill                            | ...        | ...        | ...        |     |
| Last skill before implementation       | ...        | ...        | ...        |     |
| Risk mitigation steps                  | ...        | ...        | ...        |     |
| Divergent exploration steps            | ...        | ...        | ...        |     |
| Unique skills (not in other pipelines) | ...        | ...        | ...        |     |

### 2. Consensus Skills

Skills that appear in ALL proposed pipelines. These are high-confidence inclusions — every optimization stance agreed they are necessary for this goal. For each consensus skill:

- The skill name
- The position range across pipelines (e.g., "step 1-2 in all pipelines" or "step 3-5, varies by stance")
- Why all stances converged on including it

### 3. Contested Skills

Skills that appear in SOME but not all pipelines. For each:

- Which pipelines include it and which exclude it
- The argument FOR inclusion (from pipelines that include it)
- The argument AGAINST inclusion (from pipelines that exclude it)
- The trade-off in concrete terms

### 4. Unique Skills

Skills that appear in ONLY ONE pipeline. For each:

- Which pipeline proposed it and why
- Whether the insight is valuable enough to adopt into the recommended pipeline

### 5. Recommended Pipeline

Synthesize a recommended pipeline that combines the best insights from all proposals. For each step in the recommended pipeline:

| Step | Skill   | Arguments | Rationale                         | Source                                   |
| ---- | ------- | --------- | --------------------------------- | ---------------------------------------- |
| 1    | {skill} | {args}    | {why this skill at this position} | {which pipeline(s) informed this choice} |
| 2    | ...     | ...       | ...                               | ...                                      |

Include:

- **What the recommended pipeline optimizes for** — the primary trade-off it makes
- **What it sacrifices** — what was deliberately excluded and why
- **Confidence level** — High (strong consensus), Medium (reasonable synthesis), or Low (significant disagreement, user judgment needed)
- **Alternative paths** — if the user's priorities differ, which pipeline to fall back to

Save the full analysis to the working directory as `compose_{slugified_topic}.md`.

## Phase 4: Present and Execute

Present the recommended pipeline and comparison analysis to the user. Then ask:

- Does this pipeline match your priorities? If urgency matters more than thoroughness (or vice versa), I can adjust.
- Are there constraints I missed that would change the ordering?
- Ready to execute? I can run the first skill in the pipeline now.

If the user confirms, begin executing the recommended pipeline by invoking the first skill with its proposed arguments.

## Rules

- **Independence is critical**: agents must NOT share context. Do not include other agents' pipelines in any agent's prompt.
- **All agents launch in a single parallel batch**: use one message with N Agent tool calls.
- **Real skills only**: agents may ONLY reference skills from the catalog. If an agent invents a skill that does not exist, flag it in the synthesis and substitute the closest real skill.
- **No empty steps**: every skill in a pipeline must have a concrete purpose and output artifact. No skill is included "just in case."
- **No filtering**: include all proposed pipelines in the comparison, even if one seems obviously weaker. The contrast reveals trade-offs.
- **Attribute insights**: when the recommended pipeline borrows from a specific proposal, name it.
- **Be honest about confidence**: if there is no clear winner among the proposals, say so and explain what user input would resolve the ambiguity.
- **Recursive compose is valid**: if a goal has a sub-goal complex enough to warrant its own pipeline, using compose recursively is legitimate — but flag the recursion explicitly.
- **The pipeline is not the territory**: remind the user that the recommended pipeline is a starting point. Skills may be added, removed, or reordered as the work progresses and new information surfaces.

## Pipeline Position

This skill operates at the **meta-level**, above all other skills. It sits before any other skill as a routing and planning layer:

```
goal → /compose (design the pipeline) → /skill-1 → /skill-2 → ... → done
```

It is the only skill that reasons about WHICH skills to use rather than solving the problem directly. It can be invoked at the start of any non-trivial project, or mid-project when the remaining work needs re-planning.
