# Agent Workflows

This repo contains multi-agent workflow skills for Claude Code.

## Workflow Routing Rules

Apply these when working with users on this codebase or any project using these skills.

### Entry point: where is the user?

| Starting point                            | Recommended path                                                                 |
| ----------------------------------------- | -------------------------------------------------------------------------------- |
| Know what to build, just need to execute  | `/focus` (handles decomposition inline for small/medium work)                    |
| Clear requirements, need a build plan     | `/scaffold` → `/focus`                                                           |
| 2+ viable approaches, need to pick one    | `/converge` → `/premortem` → `/scaffold` → `/focus`                              |
| Have a PRD, need to spike implementations | `/diverge-prototype` → `/stress-test` → pick winner → `/scaffold` → `/focus`     |
| Greenfield, vague idea                    | `/brainstorm` → `/diverge` → `/converge` → `/premortem` → `/scaffold` → `/focus` |
| Unsure which skills to use                | `/compose` to design the pipeline                                                |

### Execution rules

- For any implementation session, prefer `/focus` over ad-hoc coding to maintain context across sessions via Beads
- After `/scaffold` produces a build order, it seeds beads automatically — then use `/focus` to work through them
- `/focus` enforces: plan → execute → simplify → review → close, one bead at a time

### Design & validation triggers

- For any architecture decision with 2+ viable approaches, suggest `/diverge` then `/converge`
- For any design that will be hard to reverse (database schema, public API, auth system), suggest `/premortem` before implementation
- For any architecture change touching more than 3 files, suggest `/premortem`
- For any new public API endpoint, suggest `/stress-test` with security and edge-case vectors
- After `/diverge-prototype` produces prototypes, always suggest `/stress-test` before picking a winner
- For any feature that touches authentication or authorization, suggest `/premortem` with the security failure lens

### Exploration triggers

- When exploring a large or ambiguous problem space, suggest `/brainstorm` before `/diverge`
- For a complex problem that could be framed multiple ways, suggest `/fracture` before `/diverge`
- When a design has many stated constraints, suggest `/constraint-inversion` to find which are load-bearing

### Specialized triggers

- For any large artifact (research output, design doc, meeting notes), suggest `/distill`
- When a regression is reported with no obvious cause, suggest `/bisect`
- For coupled subsystems (API + client, frontend + backend), suggest `/entangle`
- For system migrations (old to new), suggest `/migrate`
- When you have examples but no spec, suggest `/contract`
- To validate a spec before building, suggest `/replicate`
- Before shipping a significant change, suggest `/diffuse` to map blast radius

## ZFC Compliance

This project is AI-orchestration code — ZFC applies at two levels:

1. **L2 (tooling):** workflow skills must not use heuristics for semantic judgment
2. **L3 (product):** patterns embedded in workflow outputs shape how users approach their own AI-mediated work

### Compliant

- `skills/converge/` — synthesis delegated to model judgment, no scoring formula
- `skills/diverge/` — convergence/divergence detected by model reading all findings
- `skills/diverge-prototype/` — prototype comparison by model, not by metric formula
- `skills/premortem/` — agents assign severity/likelihood (semantic), multiplication is mechanical
- `skills/contract/` — divergence map IS the output, no heuristic resolution
- All synthesis phases — model reads agent outputs and makes judgment calls

### Known violations

None currently. The architecture is naturally ZFC-compliant because the core pattern (spawn independent agents → model synthesizes) delegates all reasoning by design.

### Justified exceptions

- `skills/brainstorm/scripts/similarity.py` — multi-layer duplicate detection (Jaccard, cosine, FTS5, code structural). This is mechanical comparison with calibrated thresholds, not semantic judgment. The `--force` flag provides escape hatch. Domain: "is string A similar to string B?" not "is idea A good?"
- `skills/premortem/SKILL.md:108-111` — Risk Score = Severity x Likelihood. Agents provide the semantic inputs; multiplication is deterministic math.
- `skills/focus/SKILL.md:22-57` — task readiness detection via `bd ready`. Pure status-field logic, no semantic judgment.

### When to update this section

Update ZFC compliance notes when: a new skill adds heuristic/scoring logic, an existing skill's synthesis phase changes from model judgment to coded logic, or a new justified exception is added.

## Development Conventions

- Skills are plain markdown files at `skills/<name>/SKILL.md`
- Skills use `$ARGUMENTS` for input, not YAML frontmatter arguments
- Skills follow a phased structure: setup, agent spawn, synthesis, presentation
- Agent prompt templates go in fenced code blocks within the skill
- Every skill has a Rules section and a Pipeline Position section
- The brainstorm skill has a Python backend in `skills/brainstorm/scripts/`
- Output artifacts use the convention `<skill>_<slugified_topic>.md`
- This repo uses Beads (`bd`) for task tracking — see AGENTS.md for commands
- Implementation context lives in bead notes, not floating markdown files
- Use `bd ready` to find available work, `bd update --claim` to start, `bd close` to finish
