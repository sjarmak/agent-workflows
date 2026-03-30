# Spec Validation Workflow

Contract-to-replicate loop for specification quality. Use this when you have behavioral examples and need to produce and validate a formal specification before building.

## When to Use This Workflow

- You have examples (test cases, API logs, I/O pairs) but no formal spec
- You need to verify that a spec is unambiguous before handing it off
- Quality of the specification is critical (public API, contract between teams, regulatory requirement)

## The Pipeline

```
/contract -> /replicate -> revise spec -> /replicate (optional) -> build
```

## Step-by-Step

1. **`/contract`** -- Feed in your behavioral examples. Independent agents infer the specification using different methodologies (rule extraction, constraint mining, gap analysis). Output: draft spec with confidence annotations.

2. **`/replicate`** -- Give the draft spec to N independent agents to implement. Compare their implementations: where they converge, the spec is clear; where they diverge, it is ambiguous. Output: convergence/divergence map and spec quality score.

3. **Revise Spec** -- Use the divergence map to fix ambiguities. Add examples for contested rules. Clarify gaps.

4. **`/replicate` (optional)** -- Re-run with the revised spec to verify improvements. Repeat until convergence rate exceeds 80%.

5. **Build** -- Implement from the validated spec with confidence.

## Example Invocation

```
/contract tests/api/user_tests.py
/replicate contract_user_api.md
# ... revise spec based on divergence map ...
/replicate contract_user_api_v2.md
```

## Tips

- The contract-replicate loop is most valuable for specs that will be implemented by multiple teams or maintained long-term. For throwaway prototypes, skip this workflow.
- A spec quality score below 60% (Ambiguous) means the spec needs significant revision before anyone should start building from it.
