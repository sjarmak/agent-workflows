Constraint Inversion — What-If Removal. Takes a design with stated constraints and spawns N agents, each removing or inverting ONE constraint to explore what becomes possible without it, then synthesizes findings into a constraint dependency map that reveals which constraints are truly load-bearing vs merely assumed.

## Arguments

$ARGUMENTS — format: `[N] [path/to/design.md or inline description]` where N is optional constraint-removal agent count (default: 5, min 3, max 7)

## Parse Arguments

Extract:

- **agent_count**: the optional leading integer (default 5, min 3, max 7)
- **input**: path to a design document, architecture doc, PRD, or project plan — or an inline description of the design and its constraints

If the input is missing or unclear, ask the user to clarify before proceeding.

## Phase 1: Extract and Confirm Constraints

**If a file path is given**: read it and extract every stated or implied constraint — technical, organizational, temporal, financial, compatibility, and operational.

**If inline**: parse the description for the same.

Prepare a **design brief** that includes:

- What is being built (one paragraph summary)
- Key design decisions already made
- Dependencies (internal and external)

Then prepare a **constraint inventory** — a numbered list of every constraint found. For each constraint:

- **Name**: short label (e.g., "Backward compatibility with v2 API")
- **Type**: one of Technical, Organizational, Financial, Temporal, Compatibility, Operational, Regulatory
- **Source**: where the constraint comes from (explicit requirement, assumed convention, inherited from prior decision, regulatory, etc.)
- **Current impact**: how this constraint shapes the design today

Present the design brief and constraint inventory to the user. Ask:

- Are any constraints missing from this list?
- Are any listed constraints actually already relaxed or negotiable?
- Which N constraints should agents remove? (Or let the skill auto-select the N most design-shaping ones.)

Adjust based on user feedback. Select exactly N constraints for inversion — one per agent. Prefer constraints that appear to have the largest design impact or that the user flagged as interesting.

## Phase 2: Spawn Constraint Inversion Agents

Launch **all N agents in parallel** using the Agent tool. Each agent gets the same design brief and the full constraint inventory, but is assigned ONE specific constraint to remove. The agent explores the design space that opens up without that constraint.

Each agent MUST:

1. Use `subagent_type: "general-purpose"` (they may need web search for alternative architectures, prior art, etc.)
2. Receive the design brief and full constraint inventory so they understand the complete picture
3. Be assigned exactly ONE constraint to remove — clearly identified by name and number from the inventory
4. NOT be told which constraints other agents are removing
5. Explore in depth: what design changes become possible, what simplifications emerge, what new capabilities open up
6. Assess whether the constraint is load-bearing (its removal would fundamentally change the system) or assumed (its removal changes little or reveals it was never truly necessary)
7. Identify any other constraints that depend on the removed one (constraint dependencies)

Agent prompt template (customize the constraint per agent):

```
You are a design analyst performing a constraint inversion exercise.

## Design Brief
{design_brief}

## Full Constraint Inventory
{numbered_constraint_inventory}

## Your Assignment: Remove Constraint #{n} — {constraint_name}
{constraint_description}

## Instructions
Imagine this constraint no longer exists. It has been fully removed — not relaxed, not reduced, but gone. Explore what becomes possible.

Work through these questions systematically:

1. **What changes immediately?** Which design decisions were directly forced by this constraint? What alternatives open up?
2. **What simplifies?** Which complexity in the current design existed solely to satisfy this constraint? What components, abstractions, or workarounds become unnecessary?
3. **What new capabilities emerge?** Are there features, architectures, or approaches that were off the table but are now viable?
4. **What breaks?** Does removing this constraint destabilize other parts of the design? Do other constraints become unsatisfiable?
5. **Constraint dependencies**: Which other constraints in the inventory depend on this one? Which ones become irrelevant if this one is removed?
6. **Load-bearing assessment**: Is this constraint load-bearing (its removal fundamentally reshapes the system) or assumed (the design barely changes without it)?
7. **Removal cost vs. removal value**: If the team could negotiate away this constraint, would it be worth it? What would they gain vs. what would they risk?

Be SPECIFIC. Reference actual components, decisions, and constraints from the design brief. Do not write generic observations — write about THIS design.

## Output Format
### Constraint Removed: #{n} — {constraint_name}

#### What Becomes Possible
[2-3 paragraphs describing the design space that opens up. Be concrete — name specific alternative architectures, components, or approaches.]

#### What Simplifies
- [Specific complexity that disappears]
- [Components or abstractions that become unnecessary]
- ...

#### New Capabilities Unlocked
- [Features or approaches now viable]
- ...

#### What Breaks
- [Other parts of the design that depend on this constraint]
- [Constraints that become unsatisfiable]
- ...

#### Constraint Dependencies
- Depends on this constraint: [list constraint numbers/names that rely on this one]
- This constraint depends on: [list constraint numbers/names this one relies on]
- Becomes irrelevant without this: [constraints that lose their purpose if this one is gone]

#### Load-Bearing Assessment
- **Classification:** [Load-bearing / Assumed / Partially load-bearing]
- **Confidence:** [High / Medium / Low]
- **Rationale:** [1-2 sentences explaining the classification]

#### Surprise Findings
- [Anything unexpected — a constraint that turned out not to matter, a hidden coupling revealed, or an unexpectedly powerful simplification]
```

## Phase 3: Synthesize Constraint Dependency Map

After ALL agents return, produce a unified analysis with five sections:

### 1. Constraint Dependency Map

A structured map showing relationships between constraints. For each constraint that was removed:

| Constraint Removed | Depends On | Depended On By | Becomes Irrelevant | Load-Bearing? |
| ------------------ | ---------- | -------------- | ------------------ | ------------- |

Then render the dependency relationships as an ASCII directed graph showing which constraints support which others. Identify:

- **Foundation constraints**: load-bearing constraints that many others depend on (high in-degree in the dependency graph)
- **Leaf constraints**: constraints that depend on others but nothing depends on them (candidates for removal)
- **Isolated constraints**: constraints with no dependencies in either direction (independently negotiable)

### 2. Load-Bearing vs. Assumed Classification

Group all analyzed constraints into three tiers:

**Load-Bearing** (removal fundamentally reshapes the design):

- [Constraint name] — [one-sentence rationale from agent findings]

**Partially Load-Bearing** (removal changes significant parts but the core holds):

- [Constraint name] — [one-sentence rationale]

**Assumed** (removal changes little — the constraint was not as binding as believed):

- [Constraint name] — [one-sentence rationale]

### 3. "What Becomes Possible" Summary

For each removed constraint, a one-paragraph summary of the most significant design opportunity that opens up. Rank these by potential impact (highest first). Flag any where multiple agents' findings suggest the same opportunity from different angles.

### 4. Surprise Findings

Collect all unexpected discoveries across agents:

- Constraints that turned out not to matter
- Hidden couplings between seemingly independent constraints
- Removal of one constraint that unexpectedly made another constraint easier or harder to satisfy
- Design alternatives that were hiding in plain sight behind an assumed constraint

### 5. Actionable Recommendations

Based on the full analysis, recommend:

1. **Constraints to challenge**: assumed constraints where removal or relaxation would yield significant design improvements, with low risk. These are worth negotiating with stakeholders.
2. **Constraints to protect**: load-bearing constraints that should be explicitly documented and defended — removing them would be costly or dangerous.
3. **Constraints to decompose**: partially load-bearing constraints that might be split into a strict core (keep) and a flexible periphery (relax).

For each recommendation, note which agent's findings support it and why.

Save the full output to the working directory as `constraint_inversion_{slugified_topic}.md`.

## Phase 4: Present and Suggest Next Steps

Present the constraint dependency map, classification, and recommendations to the user. Ask:

- Do any "assumed" constraints surprise you? Should we explore relaxing them?
- Are there constraints not in the original N that you now want to test?
- Should we run `/premortem` on a redesign that removes one or more assumed constraints?
- Should we run `/diverge` or `/diverge-prototype` to explore the design space opened by removing a specific constraint?

## Rules

- **Independence is critical**: agents must NOT share context. Each agent removes a different constraint independently. Do not include other agents' findings in any agent's prompt.
- **All agents launch in a single parallel batch**: use one message with N Agent tool calls.
- **One constraint per agent**: each agent removes exactly one constraint. No agent removes multiple constraints simultaneously.
- **Full inventory to all agents**: every agent sees the complete constraint inventory so they can reason about dependencies, but only one constraint is removed.
- **Specific, not generic**: every finding must reference actual components and decisions from the design brief. Generic observations about constraint removal are useless.
- **Attribute findings**: always note which constraint removal produced which insight in the synthesis.
- **Preserve all findings**: even if an agent concludes the constraint is load-bearing and removal is a bad idea, that finding is valuable signal. Do not filter or discard.
- **No advocacy**: agents explore what becomes possible, not argue for or against removal. This is analysis, not debate.
- **Be honest about confidence**: if the dependency map has gaps or uncertain edges, say so explicitly.

## Pipeline Position

Sits early in the design process, before or alongside `/premortem`, as a constraint validation step:

```
/brainstorm (explore) -> /diverge (research)
                                \
                                 -> /constraint-inversion (validate constraints)
                                /
                         /converge (decide) -> /premortem (risk check) -> /diverge-prototype (build)
```

Use `/constraint-inversion` when:

- A design feels over-constrained and the team suspects some constraints are assumed rather than real
- Before `/premortem`, to ensure the constraints being designed around are the right ones
- After `/converge`, to stress-test the constraints baked into the chosen approach
- When a design is stuck and removing a constraint might reveal a path forward
