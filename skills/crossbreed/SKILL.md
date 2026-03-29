Structural recombination of existing designs. Takes 2-3 prototypes or design approaches and spawns N agents to create HYBRID designs, each with a different "dominant parent" whose architecture leads while grafting specific elements from the others.

## Arguments

$ARGUMENTS — format: `[N] path1 path2 [path3]` where N is optional number of hybrid agents (default: one per parent, min 2, max 5) and paths point to prototype branches, design docs, or PROTOTYPE_NOTES.md files

## Parse Arguments

Extract:
- **agent_count**: optional leading integer (default: one per parent path, min 2, max 5)
- **parent_paths**: 2-3 paths to prototype branches, design docs, or PROTOTYPE_NOTES.md files

Validate:
- At least 2 parent paths are provided
- No more than 3 parent paths
- Each path exists and contains readable design material (code, docs, or PROTOTYPE_NOTES.md)

## Phase 1: Analyze the Parents

For each parent design:

1. Read the design doc, code, or prototype notes at the given path
2. Extract **structural elements**:
   - Architecture pattern (monolith, modular, layered, event-driven, etc.)
   - Data model and state management approach
   - Key algorithms or core logic
   - API design and interface boundaries
   - Dependency choices (libraries, frameworks)
   - Error handling strategy
   - File organization and module structure
3. Identify what this parent does BEST — its distinctive strength
4. Identify what this parent does WORST or leaves incomplete

Present a **parent comparison table** to the user:

| Element | Parent A | Parent B | Parent C |
|---------|----------|----------|----------|
| Architecture | ... | ... | ... |
| Data model | ... | ... | ... |
| Key algorithm | ... | ... | ... |
| API design | ... | ... | ... |
| Dependencies | ... | ... | ... |
| Error handling | ... | ... | ... |
| Distinctive strength | ... | ... | ... |
| Weakness / gap | ... | ... | ... |

Ask the user to confirm which elements they want to see recombined before proceeding.

## Phase 2: Design Recombination Strategies

Based on the parent count, design N recombination strategies. Each strategy names a dominant parent and specifies exactly which elements to graft from the others.

**For 2 parents (A, B)**, typical strategies:
1. "A-dominant, graft B's [specific strength]" — A's architecture with B's strongest element spliced in
2. "B-dominant, graft A's [specific strength]" — B's architecture with A's strongest element spliced in
3. "Cherry-pick: A's [element] + B's [element] + new integration layer" — no single dominant parent, best elements from each with new connective tissue

**For 3 parents (A, B, C)**, add:
4. "Best-of-each: A's architecture + B's data model + C's error handling" — one element from each parent
5. "Minimal hybrid: smallest viable combination" — fewest grafting points, highest coherence

Present the strategies to the user and get confirmation before spawning agents.

## Phase 3: Spawn Recombination Agents

Launch **all N agents in parallel** using the Agent tool. Each agent MUST:

1. Use `isolation: "worktree"` — each gets its own copy of the repo
2. Use `subagent_type: "general-purpose"`
3. Receive the full analysis of ALL parents plus their assigned recombination strategy
4. Be instructed to:
   - Start from the dominant parent's codebase
   - Graft the specified elements from the other parent(s)
   - Create actual working code — this is synthesis, not planning
   - Write a `CROSSBREED_NOTES.md` in the repo root documenting:
     - What was taken from which parent and why
     - What integration challenges arose from combining
     - What had to be invented NEW to make the graft work (the "connective tissue")
     - What was deliberately dropped from non-dominant parents
     - Seam locations: exactly where parent code was spliced together
     - Self-assessed coherence: does this hybrid feel natural or forced? [1-5] with rationale
   - Commit their work with a descriptive message
   - NOT destroy or modify the original parent branches

Agent prompt template:
```
You are a crossbreed agent creating a hybrid design from multiple parent prototypes.

## Parent Analysis
{full_analysis_of_all_parents}

## Your Strategy: {strategy_name}
{strategy_description}

## Dominant Parent
{dominant_parent_path_and_summary}

## Elements to Graft
{specific_elements_from_other_parents}

Create a working hybrid implementation following your recombination strategy.

## Instructions
1. Read the dominant parent's code to understand its architecture
2. Read the other parent(s) to understand the elements you need to graft
3. Start from the dominant parent's structure
4. Graft the specified elements — adapt them to fit the dominant architecture
5. Build any connective tissue needed to make the grafts work together
6. Write CROSSBREED_NOTES.md in the repo root with:
   - What was taken from which parent and why
   - Integration challenges encountered
   - New code invented to connect the grafts ("connective tissue")
   - What was lost from non-dominant parents
   - Seam locations: where parent code was spliced (these are where bugs will live)
   - Self-assessed coherence [1-5] with rationale
   - Estimated effort to production-ready [hours/days]
7. Stage and commit all changes with message: "crossbreed: {strategy_name}"

Do NOT:
- Destroy or modify the original parent branches
- Ignore incompatibilities — document them honestly
- Force a combination that does not work — flag it as low coherence instead
- Over-polish — working hybrid > perfect hybrid
```

## Phase 4: Collect and Compare

After ALL agents return, for each hybrid:

1. Read the `CROSSBREED_NOTES.md` from each worktree/branch
2. Run a quick diff summary (`git diff --stat` from base)
3. Check which elements from each parent survived the recombination

### Comparison Structure

**1. Hybrid Comparison Table**

| Dimension | Hybrid 1 | Hybrid 2 | Hybrid 3 |
|-----------|----------|----------|----------|
| Dominant parent | ... | ... | ... |
| Elements grafted | ... | ... | ... |
| New connective tissue needed | ... | ... | ... |
| Self-assessed coherence | ... | ... | ... |
| Strengths inherited | ... | ... | ... |
| Trade-offs made | ... | ... | ... |
| Files changed | ... | ... | ... |

**2. Graft Compatibility Map**
For each pair of elements from different parents, report whether they:
- Combined cleanly (no friction)
- Required adaptation (moderate connective tissue)
- Fought each other (significant rework needed)
- Were incompatible (one had to yield)

This map reveals which design elements are naturally composable and which resist combination.

**3. Emergent Properties**
Identify any hybrid behaviors that were NOT present in ANY individual parent — cases where the combination produced something the parts did not. These are the most valuable findings.

**4. Seam Risk Assessment**
For each hybrid, list the grafting points (seams) and assess their risk:
- Where exactly in the code were parents spliced?
- How much connective tissue was needed at each seam?
- Which seams are most likely to harbor bugs?

**5. Recommended Hybrid**
Based on coherence, requirement coverage, and seam quality:
- Which combination best serves the original requirements?
- Why this hybrid over the others?
- What would need attention before production use?

**6. Per-Hybrid Highlights**
For each hybrid, a 2-3 sentence summary of its most distinctive contribution and biggest risk.

## Phase 5: Next Steps

Ask the user how they want to proceed:
1. **Adopt a hybrid** — merge that worktree branch, continue development
2. **Stress-test the chosen hybrid** — run `/stress-test` to find where the seams break
3. **Iterate with different grafting strategies** — try new element combinations
4. **Go back to parents** — the recombination revealed that one parent was already best
5. **Park it** — save findings for later, clean up worktrees

## Rules

- **Independence is critical**: hybrid agents must NOT share context or see each other's work.
- **All agents launch in a single parallel batch**.
- **Worktree isolation is mandatory**: every hybrid agent MUST use `isolation: "worktree"`.
- **Document the seams**: grafting points are where bugs will live. Every seam must be documented in CROSSBREED_NOTES.md.
- **Honest about coherence**: agents must flag when a combination feels forced. A coherence score of 1-2 means "this graft does not work well" and that is a valid, useful result.
- **Preserve parent branches**: never destroy or modify the original prototypes.
- **User confirms strategies before spawning**: never auto-launch expensive hybrid agents.
- **Don't discard failed hybrids**: even low-coherence combinations reveal which elements are incompatible — that is valuable information for the compatibility map.

## Pipeline Position

This skill sits between divergent exploration and final implementation:

```
/brainstorm (ideas) -> /diverge-prototype (N prototypes) -> /crossbreed (hybrids) -> /stress-test -> ship
```

Use `/crossbreed` when you have multiple promising prototypes and want to find the best combination rather than just picking one winner.
