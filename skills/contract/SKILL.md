Specification Generation from Examples. Takes a set of examples (API calls, test cases, user stories, input/output pairs) and spawns N agents to independently INFER the specification that would produce those examples. Each agent works bottom-up: what rules, constraints, invariants, and edge cases does this behavior imply? Agents don't see each other's inferences. Synthesize by comparing: where agents infer the same rule, it's likely correct; where they diverge, the examples are ambiguous or underconstrained. Output is a draft specification with confidence annotations.

## Arguments

$ARGUMENTS — format: `[N] [path/to/examples or inline examples]` where N is optional agent count (default: 3, min 2, max 5)

## Parse Arguments

Extract:

- **agent_count**: the optional leading integer (default 3, min 2, max 5)
- **input**: a file path containing examples, or inline examples provided directly in the argument

If the input is a file path (contains `/` or ends in a common extension), read the file. Otherwise, treat the entire remaining argument as inline examples.

If no input is provided, ask the user to provide examples before proceeding.

## Phase 1: Ingest and Classify Examples

1. Read the file or parse inline examples
2. Classify each example into one or more categories:
   - **API calls** -- request/response pairs, endpoint definitions
   - **Test cases** -- assertions, expected behaviors, setup/teardown
   - **Input/output pairs** -- transformation examples, function mappings
   - **User stories** -- behavioral descriptions, acceptance criteria
   - **State transitions** -- before/after snapshots, event sequences
   - **Error cases** -- invalid inputs, expected failures, boundary violations
   - **Mixed** -- examples that span multiple categories
3. Count and summarize the example set:
   - Total number of examples
   - Breakdown by category
   - Apparent domain or system being specified
   - Observable patterns (e.g., "all examples involve user authentication", "inputs are always JSON objects")
4. Present the classification summary to the user and confirm before proceeding. Adjust if the user gives feedback.

## Phase 2: Spawn Inference Agents

Launch **all N agents in parallel** using the Agent tool. Each agent receives the same example set and a unique **inference methodology** -- a distinct approach to extracting specifications from behavior.

### Inference Methodologies

Assign each agent a different methodology. Select N from the following (fill slots in order):

1. **Rule Extraction** -- identify the explicit rules: for every input X, output Y. Build a rule table. Look for patterns, formulas, mappings. Focus on what IS specified.
2. **Constraint Mining** -- identify the boundaries and invariants: what values are never produced? What inputs are never accepted? What relationships always hold? Focus on what CANNOT happen.
3. **Generalization & Abstraction** -- abstract from specific examples to general principles. Group similar examples, find the underlying pattern, propose the general rule that would produce all observed examples as special cases.
4. **Gap Analysis & Edge Probing** -- focus on what the examples DON'T cover. Identify boundary cases implied but not shown. Ask: what happens at zero? At max? With empty input? With concurrent access? With malformed data?
5. **Behavioral State Machine** -- model the examples as state transitions. What states exist? What triggers transitions? What are the invariants that hold across all states? What sequences are implied?

Each agent MUST:

1. Work strictly bottom-up from the examples -- infer, do not invent
2. Distinguish between **observed** (directly shown in examples) and **inferred** (logically implied by examples)
3. Flag any inference that requires assumptions beyond what the examples show
4. Produce output in the structured format below
5. Use `subagent_type: "general-purpose"` (they may need web search for domain knowledge)
6. NOT be told what other agents are exploring or inferring

Agent prompt template (customize the methodology per agent):

```
You are a specification inference agent. Your job is to reverse-engineer a specification from a set of examples.

## Examples
{classified_examples}

## Your Methodology: {methodology_name}
{methodology_description}

## Instructions
Study these examples carefully. Your goal is to infer the SPECIFICATION that would produce this behavior. Work bottom-up: start from what you observe, then generalize.

Critical distinction:
- OBSERVED: directly demonstrated by an example
- INFERRED: logically implied by the examples but not directly shown
- ASSUMED: requires an assumption beyond what examples support (flag these clearly)

Do NOT invent requirements that the examples don't support. If the examples are ambiguous on a point, say so explicitly rather than guessing.

## Output Format

### Inference Report: {methodology_name}

#### Inferred Rules / Invariants
For each rule:
- **Rule**: [statement of the rule]
- **Evidence**: [which examples support this]
- **Status**: Observed / Inferred / Assumed
- **Confidence**: High / Medium / Low

#### Inferred Constraints / Boundaries
- [What values, states, or behaviors are forbidden or limited]
- [Evidence and confidence for each]

#### Edge Cases Implied
- [Boundary conditions the examples hint at but don't fully cover]
- [What behavior would you EXPECT at these edges based on the patterns]

#### Gaps: What the Examples Don't Cover
- [Areas where the examples are silent]
- [Questions that cannot be answered from these examples alone]
- [Specific examples that SHOULD be added to resolve ambiguity]

#### Draft Spec Fragment
Write a structured specification fragment covering everything you inferred:
- Use declarative language ("The system SHALL...", "When X, the system MUST...")
- Mark each requirement with its confidence level
- Group by functional area
```

## Phase 3: Compare and Synthesize

After ALL agents return, compare inferred specifications across all agents. Produce the following synthesis:

### 1. Consensus Rules (High Confidence)

Rules or invariants that **all agents independently inferred**. These are the most reliable parts of the specification.

For each consensus rule:

- The rule statement
- Which agents inferred it and from which methodology
- The supporting examples
- Confidence: **High** (multiple independent confirmations)

### 2. Contested Rules (Ambiguous)

Rules where **agents disagreed** -- different agents inferred different or conflicting specifications for the same behavior. These indicate that the examples are ambiguous or underconstrained.

For each contested rule:

- What each agent inferred (with their reasoning)
- Why the examples are ambiguous on this point
- What additional example(s) would resolve the ambiguity
- Confidence: **Low** (needs clarification)

### 3. Unique Inferences (Needs Verification)

Rules that **only one agent caught**. These may be genuine insights from that methodology, or they may be over-inferences.

For each unique inference:

- The rule and which agent/methodology produced it
- Why other methodologies might have missed it
- How to verify: what example would confirm or refute this rule
- Confidence: **Medium** (plausible but unconfirmed)

### 4. Gap Analysis

Aggregate all gaps identified by all agents:

- Areas where NO agent could infer a rule (the examples simply don't cover this)
- Suggested examples to add, prioritized by:
  - How many contested rules the example would resolve
  - How critical the gap is to a complete specification
  - How easy the example is to produce

### 5. Draft Specification

Compile the final draft specification:

- Merge all consensus rules as definitive requirements
- Include contested rules with **[AMBIGUOUS]** annotations and the conflicting interpretations
- Include unique inferences with **[UNVERIFIED]** annotations
- Mark gaps with **[UNSPECIFIED]** annotations
- Use declarative requirement language (SHALL/MUST/SHOULD)
- Group by functional area
- Include a confidence summary: X% high-confidence, Y% ambiguous, Z% unspecified

Save the full output to `contract_{slugified_topic}.md` in the working directory.

## Phase 4: Present and Recommend

Present the draft specification to the user. Then:

1. **Highlight the top 3-5 ambiguities** -- the contested rules that most need resolution
2. **Suggest specific examples to add** -- for each ambiguity, propose a concrete example (input/output pair, test case, etc.) that would resolve it
3. **Show the confidence breakdown** -- what percentage of the spec is high-confidence vs. ambiguous vs. unspecified
4. Ask the user:
   - Do any of the inferred rules feel wrong or surprising?
   - Can you provide the suggested examples to resolve ambiguities?
   - Should we iterate with additional examples, or is this draft sufficient?
   - Would you like to feed this spec into `/replicate` for validation?

## Rules

- **Independence is critical**: agents must NOT share context. Each inference methodology explores independently. Do not include other agents' inferences in any agent's prompt.
- **All agents launch in a single parallel batch**: use one message with N Agent tool calls.
- **Bottom-up reasoning only**: agents must infer from examples, not invent requirements. Every rule must trace back to specific examples.
- **No filtering**: include all agent findings in the synthesis, even contradictory ones. Disagreement between agents is the primary signal — it reveals where examples are ambiguous.
- **Attribute findings**: always note which methodology produced which inference in the synthesis.
- **Distinguish observed vs. inferred vs. assumed**: this three-tier classification is essential. Agents must not conflate what they saw with what they guessed.
- **Be honest about confidence**: if the examples are sparse or the specification is weak in an area, say so. A confident "we don't know" is more valuable than a shaky guess.
- **Preserve ambiguity**: do not resolve contested rules by picking a winner. Present both sides and let the user decide (or provide more examples).

## Pipeline Position

Sits before `/replicate` as a spec-generation step:

```
examples -> /contract (infer spec) -> draft spec -> /replicate (validate spec) -> validated spec
```

Use `/contract` when you have behavior examples but no formal specification. Use `/replicate` after `/contract` to validate the generated spec by having agents implement it independently and checking for convergence.

Can also follow `/brainstorm` or `/diverge` when those workflows produce example-heavy output that needs to be formalized into a specification.
