# Contract

Specification generation from examples. Takes a set of examples (API calls, test cases, I/O pairs, user stories) and spawns N agents to independently infer the specification that would produce those examples. Bottom-up spec generation: examples to spec instead of spec to code.

## When to Use

- You have behavioral examples (test cases, API call logs, input/output pairs) but no formal specification
- You want to formalize implicit behavior into an explicit, reviewable spec
- You need to discover ambiguities in existing behavior before writing a spec from scratch

## Usage

```
/contract [N] [path/to/examples or inline examples]
```

**Examples:**

```
/contract tests/api/user_tests.py
/contract 4 "POST /users {name: 'Alice'} -> 201; POST /users {} -> 400; GET /users/1 -> {name: 'Alice'}"
```

N sets the agent count (default: 3, range: 2-5).

## How It Works

1. **Ingest** -- Classify examples by type (API calls, test cases, I/O pairs, state transitions, error cases). Summarize the example set.
2. **Spawn** -- Launch N agents with different inference methodologies: rule extraction, constraint mining, generalization/abstraction, gap analysis/edge probing, behavioral state machine.
3. **Synthesize** -- Compare inferences: consensus rules (all agents agree, high confidence), contested rules (agents disagree, examples are ambiguous), unique inferences (one agent only, needs verification), and gap analysis (what examples don't cover).
4. **Draft Spec** -- Compile a specification with confidence annotations: high-confidence requirements, `[AMBIGUOUS]` contested items, `[UNVERIFIED]` unique inferences, `[UNSPECIFIED]` gaps.

## Output

- A draft specification with confidence annotations saved to `contract_<slugified_topic>.md`

## Pipeline Connections

- **Before:** Any source of behavioral examples -- existing tests, API logs, user stories
- **After:** `/replicate` to validate the generated spec by independent reimplementation

## Tips

- The more diverse your examples (happy paths, error cases, edge cases), the higher quality the inferred spec will be.
- Feed the output directly into `/replicate` to close the spec quality loop: contract generates the spec, replicate tests its clarity.
