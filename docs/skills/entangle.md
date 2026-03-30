# Entangle

Dependent co-design of coupled subsystems. Spawns one agent per subsystem in isolated worktrees, all sharing a single evolving interface contract. A coordinator merges contract proposals and broadcasts updates. Agents iterate until the contract stabilizes.

## When to Use

- You are building tightly coupled subsystems that cannot be designed independently (e.g., API + client, schema + migration + query layer)
- Interface decisions in one subsystem constrain or break another
- You want to co-evolve multiple components with a negotiated, stabilized contract as the primary output

## Usage

```
/entangle [rounds] subsystem1 subsystem2 [subsystem3...] [path/to/requirements.md]
```

**Examples:**

```
/entangle api client
/entangle 4 schema migration query-layer requirements.md
/entangle frontend backend data-model
```

The optional leading integer sets max iteration rounds (default: 3, range: 2-5). Provide 2-5 subsystem names.

## How It Works

1. **Define Contract** -- Draft an initial interface contract defining shared types, endpoints, error cases, and constraints between all subsystems.
2. **Spawn (Round 1)** -- Launch all subsystem agents in parallel, each in an isolated worktree. Each implements their subsystem and submits a `CONTRACT_PROPOSAL.md` with requested interface changes.
3. **Coordinate** -- Merge proposals (compatible changes accepted, conflicts resolved by consumer-driven preference). Detect convergence.
4. **Iterate** -- Re-launch agents with the updated contract. Repeat until no agent proposes changes or max rounds reached.
5. **Final Assembly** -- Produce an integration report with contract changelog, negotiation history, and interface stability assessment.

## Output

- N subsystem implementations in git worktrees
- A stabilized interface contract
- An integration report saved to `entangle_<slugified_topic>.md`

## Pipeline Connections

- **Before:** `/brainstorm` or `/diverge` for problem exploration
- **After:** `/stress-test` targeting interface boundaries, `/scaffold` to plan integration

## Tips

- The contract is the primary artifact. Even if prototype code is discarded, the negotiated interface decisions should survive into production.
- Use `/entangle` instead of `/diverge-prototype` when subsystems truly cannot be designed independently. If subsystems are independent, `/diverge-prototype` is simpler and cheaper.
