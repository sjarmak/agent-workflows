Dependent co-design of coupled subsystems. Spawns one agent PER SUBSYSTEM in isolated worktrees, all sharing a single evolving interface contract file. A coordinator merges contract proposals and broadcasts updates. Agents iterate until the contract stabilizes. Produces N co-designed subsystems plus the negotiated contract.

## Arguments

$ARGUMENTS — format: `[rounds] subsystem1 subsystem2 [subsystem3...] [path/to/requirements.md]` where rounds is optional max iteration count (default: 3, min 2, max 5) and subsystems are named components of the coupled system (min 2, max 5)

## Parse Arguments

Extract:

- **max_rounds**: optional leading integer (default 3, min 2, max 5)
- **subsystems**: 2-5 named subsystems (e.g., `api client`, `schema migration query-layer`, `frontend backend data-model`)
- **requirements_path**: optional trailing path to a requirements doc, PRD, or design brief

Validate:

- At least 2 subsystems are provided
- No more than 5 subsystems
- Subsystem names are distinct

## Phase 1: Define the Contract

**If a requirements path is provided**: read it and extract the interfaces, data flows, and coupling points between the named subsystems.

**If no requirements path**: ask the user to describe:

- What does each subsystem do?
- How do the subsystems communicate? (API calls, shared database, message queue, function calls, etc.)
- What are the hard constraints? (tech stack, protocols, existing code)
- What is the desired end state?

From this, draft the **initial contract file** — a structured document that defines the interface between all subsystems. The contract format:

```markdown
# Interface Contract v0

## Status: DRAFT

## Subsystems

- {subsystem_1}: {one-line purpose}
- {subsystem_2}: {one-line purpose}
  ...

## Shared Types

{Data types, schemas, or models that cross subsystem boundaries}

## Interfaces

### {subsystem_1} -> {subsystem_2}

- Endpoint/method: ...
- Input: ...
- Output: ...
- Error cases: ...

### {subsystem_2} -> {subsystem_1}

- Endpoint/method: ...
- Input: ...
- Output: ...
- Error cases: ...

{Repeat for every directional interface between subsystems}

## Constraints

- {Protocol, format, auth, versioning, or other cross-cutting rules}

## Open Questions

- {Unresolved interface decisions}
```

Save the initial contract to the working directory as `contract_{slugified_topic}.md`.

Present the contract to the user and get confirmation before proceeding. The contract is the seed — agents will evolve it.

## Phase 2: Spawn Subsystem Agents (Round 1)

Launch **all subsystem agents in parallel** using the Agent tool. Each agent MUST:

1. Use `isolation: "worktree"` — each gets its own copy of the repo
2. Use `subagent_type: "general-purpose"`
3. Receive the full initial contract plus their assigned subsystem
4. Be instructed to:
   - Implement their subsystem according to the contract
   - Where the contract is ambiguous or incomplete, make a decision and document it
   - Produce a `CONTRACT_PROPOSAL.md` in the repo root with any changes they need to the contract — additions, modifications, or clarifications
   - Produce an `ENTANGLE_NOTES.md` in the repo root documenting their implementation decisions
   - Commit their work with a descriptive message

Agent prompt template:

```
You are a subsystem agent designing and implementing one part of a coupled system.

## Interface Contract (Current Version)
{contract_content}

## Your Subsystem: {subsystem_name}
{subsystem_description}

## Requirements
{requirements_or_context}

Design and implement your subsystem according to the interface contract.

## Instructions
1. Read the interface contract carefully — it defines how you connect to other subsystems
2. Implement your subsystem: create and modify files as needed
3. Where the contract is ambiguous or incomplete for your needs, make the best decision you can
4. If you need the contract to change, write CONTRACT_PROPOSAL.md with your requested changes:
   - What interface or type you want changed
   - What the current definition is
   - What you propose instead
   - Why you need the change (what breaks or is awkward without it)
   - Impact: which other subsystems would be affected
5. Write ENTANGLE_NOTES.md in the repo root with:
   - Implementation approach summary
   - Key design decisions and trade-offs
   - Assumptions made about other subsystems
   - Where your implementation depends on contract details being exactly right
   - What would break if the contract changed (your fragile points)
   - Self-assessed completeness [1-5]
6. Stage and commit all changes with message: "entangle round {round}: {subsystem_name}"

Do NOT:
- Implement other subsystems — stay in your lane
- Assume you know how other subsystems are built internally
- Ignore contract ambiguities — surface them in your proposal
- Over-engineer — implement what the contract requires, not what you imagine it might require later
```

## Phase 3: Coordinate (Merge Contract Proposals)

After ALL agents return for a round, the coordinator (you) does the following:

### 3a. Collect Proposals

Read each agent's `CONTRACT_PROPOSAL.md`. Categorize each proposed change:

- **Compatible**: proposals that do not conflict with any other agent's proposals
- **Conflicting**: two or more agents propose different changes to the same interface
- **One-sided**: only one agent proposes a change and no other agent's implementation depends on the current definition

### 3b. Merge the Contract

Apply changes using these rules:

1. **Compatible changes**: accept all of them. Update the contract.
2. **One-sided changes**: accept if they do not violate constraints. Update the contract.
3. **Conflicting changes**: resolve by choosing the proposal that:
   - Satisfies the most subsystems
   - Minimizes cascading changes to other interfaces
   - Preserves the simplest possible contract
   - If still tied, prefer the proposal from the subsystem that CONSUMES the interface over the one that PROVIDES it (consumer-driven contracts)
4. **Ambiguity resolutions**: if multiple agents independently resolved the same ambiguity the same way, adopt it. If they resolved it differently, pick one and document the rationale.

Update the contract version number and status:

- `v1` after Round 1 merge, `v2` after Round 2 merge, etc.
- Status: `NEGOTIATING` during iteration, `STABILIZED` when converged

### 3c. Detect Convergence

The contract has **stabilized** if ANY of these conditions is met:

- No agent proposed any changes this round (all proposals empty)
- All proposals this round are cosmetic (naming, comments, formatting only)
- The max round count has been reached

If stabilized, skip to Phase 5.

### 3d. Broadcast Updated Contract

Present the merged contract changes to the user:

- What changed from the previous version
- Which proposals were accepted, which were resolved in favor of another subsystem, and why
- What open questions remain

Ask the user if they want to:

1. **Continue iteration** — proceed to the next round with the updated contract
2. **Override a merge decision** — manually resolve a conflict differently
3. **Stop early** — accept the current contract as final

If continuing, proceed to Phase 4.

## Phase 4: Iterate (Rounds 2+)

Re-launch **all subsystem agents in parallel** with:

- The updated contract (new version)
- A summary of what changed since the last round and why
- Their previous `ENTANGLE_NOTES.md` content (so they have continuity)
- Instructions to adapt their implementation to the new contract and propose further changes if needed

Use the same agent prompt template from Phase 2, with these additions to the instructions:

```
## Contract Changes Since Last Round
{diff_summary_of_contract_changes}

## Your Previous Notes
{previous_entangle_notes_content}

## Round {N} Instructions
- Review the contract changes — some may affect your implementation
- Adapt your implementation to match the updated contract
- If you still need changes, submit a new CONTRACT_PROPOSAL.md (but only for NEW issues, not re-litigating resolved ones)
- Update your ENTANGLE_NOTES.md with what changed and why
- If the contract now fully satisfies your needs, submit an empty CONTRACT_PROPOSAL.md with only: "No changes needed."
```

After agents return, repeat Phase 3 (Coordinate). Continue until convergence or max rounds.

## Phase 5: Final Assembly

Once the contract has stabilized:

### 5a. Collect Final State

For each subsystem agent:

1. Read the final `ENTANGLE_NOTES.md` from each worktree
2. Run a diff summary (`git diff --stat` from base) per worktree
3. Read the final contract version

### 5b. Integration Assessment

Produce an integration report:

**1. Final Contract Summary**
The stabilized contract with version number and a changelog showing how it evolved from v0.

**2. Subsystem Status Table**

| Dimension           | Subsystem A | Subsystem B | Subsystem C |
| ------------------- | ----------- | ----------- | ----------- |
| Completeness        | ...         | ...         | ...         |
| Contract compliance | ...         | ...         | ...         |
| Proposals submitted | ...         | ...         | ...         |
| Proposals accepted  | ...         | ...         | ...         |
| Files changed       | ...         | ...         | ...         |
| Fragile points      | ...         | ...         | ...         |

**3. Negotiation History**
For each round:

- What was proposed
- What was merged
- What conflicts were resolved and how
- Whether the resolution held or was re-opened in a later round

**4. Integration Risk Map**
For each interface in the contract:

- How many times it was revised during negotiation
- Which subsystems depend on it
- Stability assessment: `stable` (unchanged since v0), `settled` (changed then stabilized), `volatile` (changed every round)
- Volatile interfaces are the most likely integration failure points

**5. Contract Fitness Assessment**

- Does the final contract cover all inter-subsystem communication?
- Are there implicit dependencies that are not captured in the contract?
- Are there interfaces that feel over-specified or under-specified?

Save the full report to the working directory as `entangle_{slugified_topic}.md`.

## Phase 6: Next Steps

Present the final contract, the integration report, and ask the user how to proceed:

1. **Integrate** — merge all worktree branches and run integration tests against the contract
2. **Stress-test the contract** — run `/stress-test` targeting the interface boundaries
3. **Iterate further** — increase max rounds and continue negotiation on volatile interfaces
4. **Adopt subsystems selectively** — merge some subsystems, re-do others
5. **Park it** — save findings and contract for later

Remind the user: the contract is the primary artifact. Even if the prototype code is thrown away, the negotiated contract captures hard-won interface decisions that should survive into production.

## Rules

- **Agents are coupled, not independent**: unlike other skills, entangle agents share a mutable contract. This is the defining feature. But agents still cannot see each other's CODE — only the shared contract.
- **All agents launch in a single parallel batch** per round.
- **Worktree isolation is mandatory**: every subsystem agent MUST use `isolation: "worktree"`.
- **The coordinator never implements**: the coordinator (you) merges contracts and resolves conflicts. You do not write subsystem code.
- **Consumer-driven contract resolution**: when proposals conflict, prefer the consuming subsystem's needs over the providing subsystem's convenience.
- **No re-litigation**: once a conflict is resolved in round N, agents must not re-propose the same change in round N+1. They can propose NEW changes that build on the resolution.
- **Surface ambiguity, don't hide it**: agents must flag every contract ambiguity they encounter, even if they can work around it. Hidden ambiguities become integration bugs.
- **Cap iteration at max_rounds**: negotiation has diminishing returns. If the contract has not stabilized by the max round, accept the current version with volatile interfaces flagged.
- **User confirms each round**: never auto-launch the next iteration round. The user may want to override a merge decision or stop early.
- **Preserve all negotiation history**: every proposal, merge decision, and override is recorded. The negotiation trail is as valuable as the final contract.
- **Don't discard failed proposals**: rejected proposals reveal real subsystem needs that the contract could not accommodate. Flag these as technical debt or future work.

## Pipeline Position

This skill is used when the problem involves tightly coupled subsystems that must be co-designed:

```
/brainstorm or /diverge (explore the problem) -> /entangle (co-design coupled subsystems) -> /stress-test (attack the interfaces) -> /scaffold (plan the build) -> implementation
```

Use `/entangle` instead of `/diverge-prototype` when subsystems CANNOT be designed independently — when interface decisions in one subsystem constrain or break another. If subsystems are truly independent, use `/diverge-prototype` instead.
