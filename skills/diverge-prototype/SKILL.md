Divergent prototyping. Spawns N independent agents in isolated worktrees to explore different implementation approaches for a PRD, then synthesizes results.

## Arguments

$ARGUMENTS — format: `[N] [path/to/prd.md]` where N is optional (default: 3) and PRD path is optional

## Parse Arguments

Extract:
- **agent_count**: optional leading integer (default 3, min 2, max 7)
- **prd_path**: optional path to an existing PRD markdown file

## Phase 0: Ensure PRD Exists

**If a PRD path is provided**: read and validate it. It should contain at minimum: Problem Statement, Goals, and Requirements sections. If it's missing key sections, work with the user to fill gaps.

**If no PRD path is provided**: tell the user they need a PRD first and offer two options:
1. Run `/diverge` to research the topic and generate one
2. Collaborate right now to draft a quick PRD interactively

If they choose option 2, walk through these questions:
- What problem are we solving?
- What does success look like?
- What are the must-have requirements?
- What are the constraints (tech stack, compatibility, performance)?
- What are the non-goals?

Save the resulting PRD to `prd_{topic}.md` and confirm with the user before proceeding.

## Phase 1: Design Exploration Strategies

Based on the PRD requirements, design N distinct implementation strategies. Each strategy should:
- Take a meaningfully different architectural or technical approach
- Be feasible given the constraints
- Cover different points in the trade-off space (e.g., simplicity vs flexibility, speed vs correctness)

Examples of strategy differentiation:
- "Minimal viable approach" — least code, fastest to ship
- "Framework-heavy approach" — leverage existing libraries/patterns
- "Performance-first approach" — optimize for speed/scale
- "Extensibility-first approach" — optimize for future changes
- "Unconventional approach" — novel technique or pattern

Present the strategies to the user and get confirmation before spawning agents.

## Phase 2: Spawn Prototype Agents

Launch **all N agents in parallel** using the Agent tool. Each agent MUST:

1. Use `isolation: "worktree"` — each gets its own copy of the repo
2. Use `subagent_type: "general-purpose"`
3. Receive the full PRD content plus their assigned strategy
4. Be instructed to:
   - Implement a working prototype following their strategy
   - Create/modify actual files (this is a prototyping phase, not research)
   - Write a `PROTOTYPE_NOTES.md` in the repo root summarizing:
     - Approach taken and key design decisions
     - What works and what's incomplete
     - Trade-offs encountered
     - Lines of code added/modified
     - Self-assessed quality: [1-5] with rationale
   - Focus on the must-have requirements first
   - NOT over-polish — this is exploration, not production code
   - Commit their work with a descriptive message

Agent prompt template:
```
You are a prototype agent implementing a solution based on a PRD.

## PRD
{full_prd_content}

## Your Strategy: {strategy_name}
{strategy_description}

Implement a working prototype following this strategy. Focus on must-have requirements first.

## Instructions
0. (If the project uses bd for task tracking) Run any worktree setup helper present:
   ```
   [ -f scripts/bd-worktree-redirect.sh ] && bash scripts/bd-worktree-redirect.sh || true
   ```
   You are inside a git worktree, so bd commands targeting the main repo's Dolt server need a redirect file. The helper is idempotent and a no-op if the project doesn't use bd.
1. Read the relevant existing code to understand the current state
2. Implement your approach — create and modify files as needed
3. Make it work end-to-end for the core requirements if possible
4. Write PROTOTYPE_NOTES.md in the repo root with:
   - Approach summary
   - Key design decisions and why
   - What works vs what's stubbed/incomplete
   - Trade-offs you encountered
   - Self-assessed quality [1-5]
   - Estimated effort to production-ready [hours/days]
5. Stage and commit all changes with message: "prototype: {strategy_name}"

Do NOT:
- Over-engineer or add unnecessary abstractions
- Spend time on docs/tests unless they're core to the approach
- Try to be perfect — working > polished
```

## Phase 3: Collect and Compare

After ALL agents return, for each prototype:

1. Read the `PROTOTYPE_NOTES.md` from each worktree/branch
2. Run a quick diff summary (`git diff --stat` from base)
3. Check if core requirements from the PRD are addressed

## Phase 4: Synthesize

Present a comparison matrix:

### Comparison Structure

**1. Strategy Summary Table**

| Dimension | Strategy A | Strategy B | Strategy C |
|-----------|-----------|-----------|-----------|
| Approach | ... | ... | ... |
| Files changed | ... | ... | ... |
| Complexity | ... | ... | ... |
| Requirements met | X/Y | X/Y | X/Y |
| Self-assessed quality | ... | ... | ... |
| Production readiness | ... | ... | ... |

**2. Trade-off Analysis**
For each major trade-off (complexity vs simplicity, performance vs maintainability, etc.), map where each prototype falls.

**3. Best Ideas From Each**
Identify the strongest elements from each prototype that could be combined.

**4. Recommended Path Forward**
Based on the exploration:
- Which approach (or combination) best serves the PRD goals?
- What would a "best of all worlds" implementation look like?
- What should be built next?

**5. Per-Prototype Highlights**
For each prototype, a 2-3 sentence summary of its most distinctive contribution.

## Phase 5: Next Steps

Ask the user how they want to proceed:
1. **Adopt one prototype** — merge that worktree branch, then run teardown for ALL prototypes (including the adopted one once merged).
2. **Cherry-pick and combine** — take best elements from multiple prototypes into a new implementation. Run teardown for ALL prototypes after extraction.
3. **Iterate** — refine the PRD based on learnings and run another round. Run teardown before launching the next round so worktrees don't accumulate.
4. **Park it** — save findings for later, run teardown immediately.

### Teardown (MANDATORY in all four paths)

For each prototype's worktree+branch, after the user confirms the path forward:

```bash
git worktree unlock <prototype-worktree-path> 2>/dev/null || true
git worktree remove --force <prototype-worktree-path>
git branch -D <prototype-branch-name> 2>/dev/null || true
```

The Agent tool returns the worktree path and branch name in its result — capture those when each agent completes so this teardown loop has the data it needs. Without teardown, `.claude/worktrees/agent-*` directories accumulate (~24GB+ over a few weeks of normal use).

Guard: when "Park it" is chosen for a not-yet-merged prototype, confirm with the user before deleting the branch — the work has not yet been preserved elsewhere.

## Rules

- **Independence is critical**: agents must NOT share context or see each other's strategies.
- **All agents launch in a single parallel batch**.
- **Worktree isolation is mandatory**: every prototype agent MUST use `isolation: "worktree"`.
- **PRD is the contract**: agents are evaluated against PRD requirements, not against each other.
- **Don't discard work**: even "failed" prototypes contain insights. Always extract learnings.
- **User confirms strategies before spawning**: never auto-launch expensive prototype agents.
- **Tear down all prototype worktrees in Phase 5.** Every prototype agent leaves a `.claude/worktrees/agent-*` directory and an `agent-*` branch. Phase 5 MUST run the teardown loop for every prototype (adopted, parked, or discarded) once the path forward is decided. Skipping leaks ~MB per prototype and accumulates fast across multiple `/diverge-prototype` runs.
