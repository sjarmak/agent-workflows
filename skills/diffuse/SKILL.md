Blast Radius Impact Mapping. Takes a proposed change (diff, migration, dependency upgrade, config change) and spawns N independent agents, each tracing impact through a different propagation path. No agent sees others' findings. Synthesizes into a combined blast radius map showing first-order, second-order, and third-order effects radiating outward from the change point.

## Arguments

$ARGUMENTS — format: `[N] [path/to/diff or file or inline change description]` where N is optional (default: 5, min 3, max 7)

## Parse Arguments

Extract:

- **agent_count**: the optional leading integer (default 5, min 3, max 7)
- **change_target**: a diff file path, source file path, directory path, branch name, or inline description of the proposed change

If the target is missing or unclear, ask the user to clarify before proceeding.

## Phase 1: Understand the Change

Determine the target type and build a precise understanding of what is changing:

- **If a diff or patch file**: read it and identify every modified file, function, type, and config key
- **If a source file or directory**: read it and ask the user what change is being made (or check for uncommitted changes via `git diff`)
- **If a branch name**: run `git diff main...<branch>` (or the appropriate base) to extract the full changeset
- **If an inline description**: parse it for the affected components

Prepare a **change summary** covering:

- What is changing (the precise modification)
- Where the change originates (files, functions, lines, config keys)
- What type of change this is (code logic, schema migration, dependency upgrade, config change, API contract change, infrastructure change)
- The stated intent of the change (why it is being made)

Present the change summary to the user and confirm before proceeding. Adjust if the user gives feedback.

## Phase 2: Spawn Propagation Agents

Launch **all N agents in parallel** using the Agent tool. Each agent gets the change summary plus a unique **propagation path** selected from this list (assign sequentially, wrapping if N < 7):

### Propagation Path 1: Call Graph

Trace the call graph outward from the change point. What functions/methods call the changed code? What does the changed code call? Follow the chain in both directions. For each hop, note whether the caller's assumptions still hold after the change, whether return types or error conditions have shifted, and whether any caller is unprepared for the new behavior.

### Propagation Path 2: Data Flow

Trace how data moves through the changed code. Where does input data originate? What transformations does it pass through? Where is it stored, cached, serialized, or sent to external systems? Identify any place where the shape, type, range, encoding, or nullability of data is altered by the change and follow that altered data to every consumer.

### Propagation Path 3: Test Coverage Gaps

Map which tests cover the changed code and its immediate callers. Identify code paths near the change that have no test coverage. Flag tests that assert on behavior that may shift. Identify integration and E2E tests that exercise the changed path. Highlight areas where a regression could hide because no test would catch it.

### Propagation Path 4: Deployment Pipeline

Trace the change through the build and release process. Does it affect build configuration, CI steps, environment variables, feature flags, database migrations, or rollback procedures? Would this change require a coordinated deploy across services? Could it cause a failed deploy, a broken rollback, or a state mismatch between old and new versions during a rolling update?

### Propagation Path 5: User-Facing Behavior

Trace the change to every user-visible surface. Does it alter API responses, UI rendering, error messages, performance characteristics, or accessibility? Consider all user types: end users, API consumers, admin users, automated clients. Identify behavioral changes that are intentional vs. unintentional side effects.

### Propagation Path 6: Configuration & Environment

Trace the change through configuration surfaces. Does it add, remove, or change the meaning of environment variables, feature flags, config files, or secrets? Does it alter defaults? Could it behave differently across environments (dev, staging, production)? Identify any config that must be updated in sync with the code change.

### Propagation Path 7: Dependency & Package

Trace upstream and downstream dependency effects. If a dependency is being added, removed, or upgraded: what transitive dependencies change? Are there known vulnerabilities or breaking changes? If the changed code is consumed by other packages or services: do their version constraints still hold? Could this change force a cascade of downstream upgrades?

Each agent MUST:

1. Use `subagent_type: "general-purpose"` (needs file access for reading actual code and tracing references)
2. READ actual source code, test files, config files, and CI definitions — do not reason abstractly when concrete evidence is available
3. Trace effects outward from the change point in three concentric rings:
   - **First-order** (direct): components that directly touch the changed code
   - **Second-order** (one hop): components that depend on first-order components
   - **Third-order** (two hops): components that depend on second-order components
4. For each affected component, state: what it is, how it connects to the change, what could break, and how confident the agent is (High / Medium / Low)
5. Produce findings in the structured output format below

Do NOT include other agents' findings or path assignments in any agent's prompt.

Agent prompt template (customize the propagation path per agent):

```
You are a change-impact analyst tracing the blast radius of a proposed change.

## Change Summary
{change_summary}

## Your Propagation Path: {path_name}
{path_description}

## Instructions
Trace the impact of this change through your assigned propagation path. Start at the change point and work outward. Be specific and evidence-based — vague speculation is useless.

For each affected component you find:

1. **Component** — what is affected (file, function, service, config key, test, UI element)
2. **Connection** — how it connects to the change (direct call, data consumer, config dependency, etc.)
3. **Impact** — what could break, change, or degrade
4. **Order** — First (direct), Second (one hop), Third (two hops)
5. **Confidence** — High (read the code and verified), Medium (inferred from structure), Low (possible but not confirmed)
6. **Risk** — Critical (breaks functionality), High (degrades behavior), Medium (cosmetic or minor), Low (negligible)

READ the actual code. Reference specific files, functions, and line numbers. Trace imports, function calls, data flows, and config references concretely. If you cannot access a file or verify a connection, say so explicitly and mark confidence as Low.

Stop at third-order effects — do not trace further. If a path dead-ends before third order, note that the blast radius is contained in that direction.

## Output Format
### Propagation Path: {path_name}

#### First-Order Effects (Direct)
| Component | Connection | Impact | Risk | Confidence |
|-----------|-----------|--------|------|------------|
| ... | ... | ... | ... | ... |

[Narrative explanation of direct effects]

#### Second-Order Effects (One Hop)
| Component | Connection | Impact | Risk | Confidence |
|-----------|-----------|--------|------|------------|
| ... | ... | ... | ... | ... |

[Narrative explanation of second-order effects]

#### Third-Order Effects (Two Hops)
| Component | Connection | Impact | Risk | Confidence |
|-----------|-----------|--------|------|------------|
| ... | ... | ... | ... | ... |

[Narrative explanation of third-order effects]

#### Path Summary
- Components affected: N (first: N, second: N, third: N)
- Highest risk: [Critical/High/Medium/Low]
- Containment assessment: [Is the blast radius bounded or does it keep expanding?]
```

## Phase 3: Synthesize Blast Radius Map

After ALL agents return, produce a unified analysis with five sections:

### 1. Combined Blast Radius Map

All affected components across all propagation paths, deduplicated and sorted by order then risk:

| #   | Component | Order | Risk | Propagation Paths | Impact Summary |
| --- | --------- | ----- | ---- | ----------------- | -------------- |

For components found by multiple agents, merge their findings and note which paths surfaced them.

### 2. Heat Map

Which components appear across multiple propagation paths? These are the highest-risk areas because they are affected through multiple independent channels.

For each hot component:

- Which propagation paths flagged it
- The combined risk assessment
- Why multi-path exposure increases the danger

Components appearing in 3+ paths are critical review targets. Components appearing in 2 paths deserve careful attention. Components in only 1 path are lower priority.

### 3. Safe Zones

Areas of the codebase that no agent found to be affected. These are tentatively outside the blast radius. Note that absence of findings is not proof of safety, especially for:

- Areas that are hard to trace statically
- Async or event-driven connections
- Runtime-only coupling (reflection, dynamic dispatch, plugin systems)

### 4. Containment Assessment

Is this change well-contained or does it ripple widely?

- How many components are affected at each order?
- Does the blast radius expand, stay constant, or contract at each hop?
- Are there natural boundaries (service borders, API contracts, database schemas) that limit propagation?
- Overall assessment: Contained / Moderate Spread / Wide Blast Radius

### 5. Review Checklist

A prioritized checklist of what to review and test before shipping this change, derived from the findings:

- [ ] **Critical**: items that must be verified (high-risk components in the heat map)
- [ ] **High**: items that should be reviewed (multi-path components, untested code paths)
- [ ] **Medium**: items worth checking (second-order effects with medium confidence)
- [ ] **Low**: items to be aware of (third-order effects, low-confidence findings)

Save the full report to the working directory as `diffuse_{slugified_topic}.md`.

## Phase 4: Present and Recommend

Present the blast radius map and review checklist to the user. Ask:

- Are there any propagation paths we missed that are specific to your system?
- Should we write tests for the coverage gaps identified?
- Should we run `/stress-test` on the hot components in the heat map?
- Should we run `/premortem` if the containment assessment shows wide blast radius?

## Rules

- **Independence is critical**: agents must NOT share findings. Do not include other agents' findings or path assignments in any agent's prompt.
- **All agents launch in a single parallel batch**: use one message with N Agent tool calls.
- **Read actual code, not abstractions**: every agent must READ source files, test files, config files, and CI definitions. Do not reason about code without reading it. Reference specific files, functions, and line numbers.
- **Specific, not generic**: every finding must reference the actual codebase — its files, functions, data structures, and config keys. Generic impact checklists are useless.
- **Three orders maximum**: trace first-order, second-order, and third-order effects. Stop there — further hops produce diminishing confidence.
- **State confidence explicitly**: every finding must include a confidence level. High means the agent read the code and verified the connection. Medium means inferred from structure. Low means possible but unconfirmed.
- **No filtering**: include all agent findings in the synthesis, even overlapping ones. Overlap across independent agents is a strong signal that a component is genuinely affected.
- **Attribute findings**: always note which propagation path produced which finding.
- **No worktrees**: this is read-only analysis. Agents read and trace but do not modify code.

## Pipeline Position

Sits before implementation or deployment as a change-impact gate. Use after a change is proposed but before it ships:

```
proposed change → /diffuse (impact map) → review / test / ship
```

Also complements `/stress-test` and `/premortem`:

- `/diffuse` answers "what does this change touch?" (forward-tracing from a specific change)
- `/stress-test` answers "how can this design break?" (adversarial probing of a design)
- `/premortem` answers "how could this project fail?" (prospective failure narratives)
