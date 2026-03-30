Independent Verification by Reimplementation. Spawns N agents in isolated worktrees to implement the SAME specification independently, with no knowledge of each other's code. Compares outputs to produce a convergence/divergence map that reveals where the spec is clear, where it is ambiguous, and what it fails to specify at all.

This is NOT prototyping. Agents implement the same spec, not different strategies. The value is in the convergence/divergence analysis, not in picking a winner. Where implementations converge, the spec is unambiguous. Where they diverge, the spec has gaps or hidden assumptions. The divergence map IS the output.

## Arguments

$ARGUMENTS — format: `[N] [path/to/spec.md or inline specification]` where N is optional (default: 3, min 2, max 5)

## Parse Arguments

Extract:

- **agent_count**: optional leading integer (default 3, min 2, max 5)
- **spec_input**: path to an existing specification file, or an inline specification string

If the spec input is missing or unclear, ask the user to provide a specification before proceeding. The spec should describe WHAT to build, not HOW — the whole point is to see how independent agents interpret the "how."

## Phase 1: Frame the Specification

**If a file path is given**: read it and extract the full specification content.

**If inline**: parse the specification description.

Prepare a **specification brief** that includes:

- What is being specified (the deliverable)
- Functional requirements (what it must do)
- Non-functional requirements (performance, compatibility, constraints)
- Interface contracts (inputs, outputs, APIs if specified)
- Explicit constraints (tech stack, file structure, naming conventions)
- What the spec does NOT specify (note any obvious gaps without filling them — gaps are part of what we are measuring)

Present the specification brief to the user and confirm before proceeding. Do NOT fill in gaps or resolve ambiguities — present the spec as-is. If you notice potential ambiguities, note them privately but do not hint at them to the user or the agents. The agents must encounter ambiguities naturally.

## Phase 2: Spawn Implementation Agents

Launch **all N agents in parallel** using the Agent tool. Every agent receives the **exact same specification brief** with **no strategy assignment, no hints, and no differentiation**. Each agent MUST:

1. Use `isolation: "worktree"` — each gets its own copy of the repo
2. Use `subagent_type: "general-purpose"`
3. Receive the identical specification brief (no variation between agents)
4. Be instructed to:
   - Implement the full specification to the best of their ability
   - Make their own decisions wherever the spec is silent or ambiguous
   - Write an `IMPLEMENTATION_NOTES.md` in the repo root documenting:
     - Every assumption made where the spec was unclear or silent
     - Every ambiguity encountered and how they resolved it
     - Design decisions made and the reasoning behind each
     - Anything they wished the spec had specified but did not
   - Commit all work with a descriptive commit message
   - NOT attempt to guess what other agents might do
   - NOT try to be "different" — just implement the spec as they understand it

Agent prompt template (identical for all agents):

```
You are an implementation agent. Your job is to implement the following specification independently.

## Specification
{specification_brief}

## Instructions
1. Read any relevant existing code in the repo to understand the current codebase
2. Implement the specification fully — create and modify files as needed
3. Where the spec is silent or ambiguous, make your own best judgment call
4. Document EVERY assumption and decision in IMPLEMENTATION_NOTES.md (see format below)
5. Stage and commit all changes with message: "replicate: implement spec"

## IMPLEMENTATION_NOTES.md Format
Write this file in the repo root with the following sections:

### Assumptions Made
For each assumption:
- What the spec did not specify
- What you assumed
- Why you chose this interpretation

### Ambiguities Encountered
For each ambiguity:
- The ambiguous requirement
- How you interpreted it
- What alternative interpretations exist

### Design Decisions
For each significant decision:
- What you decided
- Why
- What alternatives you considered

### Spec Gaps
- Requirements the spec should have included but did not
- Information you needed but had to guess

Be thorough in your notes. The notes are as important as the code — they reveal what the spec actually communicates vs. what it leaves open to interpretation.

Do NOT:
- Try to be creative or novel — just implement the spec as you understand it
- Guess what other implementers might do
- Over-engineer beyond what the spec requires
```

## Phase 3: Compare All Implementations

After ALL agents return, perform a systematic comparison:

### Step 1: Collect Artifacts

For each agent's worktree:

1. Read `IMPLEMENTATION_NOTES.md`
2. Run `git diff --stat` from base to see files changed
3. Read the key implementation files

### Step 2: Build the Convergence Map

Identify every decision point where ALL agents made the **same choice**. For each convergence point:

- What the decision was
- What the agents all chose
- Why this signals that the spec is clear on this point

### Step 3: Build the Divergence Map

Identify every decision point where agents made **different choices**. For each divergence point:

- What the decision point was (e.g., "error handling strategy," "data structure for X," "API response format")
- What each agent chose (Agent 1 did X, Agent 2 did Y, Agent 3 did Z)
- What was ambiguous in the spec that caused the divergence
- Which interpretation seems most reasonable and why
- How the spec could be clarified to eliminate this divergence

### Step 4: Spec Gap Analysis

Aggregate all "Spec Gaps" entries from the agents' `IMPLEMENTATION_NOTES.md` files:

- Gaps identified by multiple agents (high priority — the spec is clearly missing something)
- Gaps identified by only one agent (worth reviewing — may indicate an edge case the spec should address)
- Requirements the agents invented that the spec never mentioned (the spec may need to either include or explicitly exclude these)

### Step 5: Structural Comparison

Compare the implementations at the structural level:

- File organization: did agents create similar or different file structures?
- Code volume: how much code did each agent write? Large variance suggests spec ambiguity about scope
- Shared patterns: what patterns did agents independently converge on? These are likely the "natural" implementation
- Architectural divergence: where did agents take fundamentally different approaches?

## Phase 4: Present Findings

### 1. Specification Quality Score

Rate the spec on a simple scale:

| Rating         | Meaning                                  | Convergence Rate    |
| -------------- | ---------------------------------------- | ------------------- |
| Clear          | Agents converged on nearly everything    | >80% of decisions   |
| Mostly Clear   | Some divergence on secondary concerns    | 60-80% of decisions |
| Ambiguous      | Significant divergence on core decisions | 40-60% of decisions |
| Underspecified | Agents built materially different things | <40% of decisions   |

### 2. Convergence Map

Full list of decision points where all agents agreed, grouped by category. These are the spec's strengths.

### 3. Divergence Map

Full list of decision points where agents disagreed, with:

- The ambiguous spec language (or gap)
- Each agent's interpretation
- Recommended clarification

### 4. Spec Gap Report

All missing specifications, prioritized by:

- How many agents flagged it
- Impact on implementation correctness
- Recommended addition to the spec

### 5. Recommended Spec Revisions

A concrete list of changes to the specification that would eliminate the discovered ambiguities and fill the identified gaps. For each revision:

- What to add or change
- Which divergence or gap it addresses
- Suggested wording

Save the full output to `replicate_{slugified_topic}.md` in the working directory.

### 6. Next Steps

Ask the user:

1. **Revise the spec** — update the specification with the recommended clarifications and run `/replicate` again to verify
2. **Pick an implementation** — if one agent's choices best match intent, adopt that worktree
3. **Merge the best** — cherry-pick the strongest decisions from each agent into a combined implementation
4. **Proceed with awareness** — accept the ambiguities as documented and move to implementation with the divergence map as a reference

## Rules

- **Independence is CRITICAL**: this is the entire point of the skill. Agents must NOT share context, see each other's code, or receive any differentiated instructions. Every agent gets the exact same prompt. Any contamination between agents invalidates the analysis.
- **All agents launch in a single parallel batch**: use one message with N Agent tool calls.
- **Worktree isolation is mandatory**: every agent MUST use `isolation: "worktree"`. Agents implementing in the same working directory would contaminate each other.
- **No strategy assignment**: unlike `/diverge-prototype`, agents are NOT given different strategies. They all implement the same spec with the same instructions. Divergence must emerge naturally from spec ambiguity, not from assigned differences.
- **Do not filter divergences**: every divergence point is signal. Even minor divergences (naming conventions, file organization) reveal what the spec leaves implicit. Include all of them.
- **Do not fill spec gaps before spawning**: if you notice the spec is ambiguous, do NOT clarify it. The agents must encounter the ambiguity themselves. Filling gaps before spawning defeats the purpose.
- **Attribute findings**: always note which agents converged or diverged on each point.
- **IMPLEMENTATION_NOTES.md is mandatory**: agents that skip their notes produce less useful analysis. The notes are as valuable as the code.
- **The divergence map is the primary output**: the code itself is secondary. The skill's value is in revealing what the spec actually says vs. what people assume.

## Pipeline Position

Sits after spec writing and before implementation, as a specification quality gate:

```
/diverge (research) -> /converge (spec) -> /replicate (spec quality gate) -> /diverge-prototype (build)
```

Use `/replicate` when you want to verify that a specification is clear and complete enough to hand off for implementation. If the divergence map reveals significant ambiguity, revise the spec and run `/replicate` again before proceeding to `/diverge-prototype` or direct implementation.
