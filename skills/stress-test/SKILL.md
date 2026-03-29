Parallel Adversarial Attack Surface Analysis. Spawns N independent agents, each tasked with BREAKING a system from a different attack angle. No agent sees others' findings. Synthesizes into a vulnerability map with severity ratings.

## Arguments

$ARGUMENTS — format: `[N] [path/to/code_or_design or inline description]` where N is optional (default: 5, min 3, max 7)

## Parse Arguments

Extract:
- **agent_count**: the optional leading integer (default 5, min 3, max 7)
- **attack_target**: the file path, directory path, or inline description of the system to analyze

If the target is missing or unclear, ask the user to clarify before proceeding.

## Phase 1: Identify the Target

Determine the target type and build a comprehensive understanding:

- **If a file or directory path is given**: read and explore it to understand the system — its structure, components, dependencies, data flows, trust boundaries, and deployment model
- **If an inline description is given**: parse it for the same information

Prepare a **target brief** covering:
- What the system does (purpose, scope)
- Components and their responsibilities
- Dependencies (internal and external)
- Data flows (input sources, processing, storage, output)
- Trust boundaries (authenticated vs unauthenticated, internal vs external, admin vs user)
- Deployment model (where it runs, how it scales)

Present the target brief to the user and confirm before proceeding. Adjust if the user gives feedback.

## Phase 2: Spawn Attack Agents

Launch **all N agents in parallel** using the Agent tool. Each agent gets the target brief plus a unique **attack vector** selected from this list (assign sequentially, wrapping if N < 7):

### Attack Vector 1: Edge Cases & Input Boundaries
Malformed input, boundary values, type confusion, unicode edge cases, empty/null/huge payloads, concurrent conflicting inputs, format string attacks, deserialization of untrusted data.

### Attack Vector 2: Scale & Resource Exhaustion
What happens at 100x load, memory leaks under sustained use, unbounded growth (queues, logs, caches), connection pool exhaustion, hot spots, thundering herd, algorithmic complexity attacks (ReDoS, hash collision).

### Attack Vector 3: Security & Access Control
Injection (SQL, XSS, command), authentication bypass, privilege escalation, data leakage, insecure defaults, SSRF, secret exposure, IDOR, missing rate limiting, broken session management.

### Attack Vector 4: Dependency & Integration Failure
What if an API returns 500, what if a dependency is slow/down/returns unexpected data, version incompatibility, certificate expiry, DNS failure, retry storms, cascading failures, poison pill messages.

### Attack Vector 5: Concurrency & State
Race conditions, deadlocks, stale reads, lost updates, session corruption, distributed state inconsistency, clock skew, TOCTOU vulnerabilities, phantom reads, non-atomic check-then-act sequences.

### Attack Vector 6: Data Integrity & Recovery
Data corruption scenarios, backup/restore gaps, migration failures, partial writes, orphaned records, audit trail gaps, silent data loss, schema drift, referential integrity violations.

### Attack Vector 7: Deployment & Operations
Config drift, rollback failures, health check blind spots, log noise drowning signal, monitoring gaps, certificate/secret rotation, environment parity issues, blue-green/canary failure modes.

Each agent MUST:

1. Use `subagent_type: "general-purpose"` (needs file access, possibly web search for known vulnerability patterns)
2. Actively TRY to construct specific attack scenarios against the target (not just list generic categories)
3. For code targets: read the actual code and identify specific lines/functions that are vulnerable
4. For design targets: identify specific component interactions that break
5. Produce findings in the structured format below

Do NOT include other agents' findings or vector assignments in any agent's prompt.

Agent prompt template (customize the vector per agent):
```
You are a security/reliability engineer conducting adversarial analysis.

## Target
{target_brief}

## Your Attack Vector: {vector_name}
{vector_description}

## Instructions
Your job is to BREAK this system through your assigned attack vector. Be specific and constructive — vague warnings are useless. For each vulnerability you find:

1. **Describe the vulnerability** — what exactly is wrong
2. **Attack scenario** — step-by-step how an attacker/situation would exploit this
3. **Evidence** — point to specific code, components, or design decisions
4. **Severity**: Critical (data loss/security breach), High (service down), Medium (degraded), Low (cosmetic/minor)
5. **Exploitability**: Easy (automated/script-kiddie), Medium (requires expertise), Hard (requires insider access)
6. **Fix** — concrete change to prevent this

Find as many real vulnerabilities as you can through your lens. Quality > quantity, but don't stop at the first one.

For code targets: READ the actual code. Reference specific files, functions, and line numbers. Do not reason abstractly when concrete evidence is available.

For design targets: identify specific component interactions, API contracts, or architectural decisions that break under your attack vector.

If an area is untestable without actually running the code, say so explicitly — do not offer false reassurance.

## Output Format
### Attack Vector: {vector_name}

#### Vulnerability 1: [name]
- **Description:** ...
- **Attack scenario:** 1. ... 2. ... 3. ...
- **Evidence:** [specific code reference or component]
- **Severity:** [Critical/High/Medium/Low]
- **Exploitability:** [Easy/Medium/Hard]
- **Risk Score:** [Severity x Exploitability]
- **Fix:** ...

[repeat for each vulnerability found]

#### Summary
- Vulnerabilities found: N
- Critical: N, High: N, Medium: N, Low: N
```

## Phase 3: Synthesize Vulnerability Map

After ALL agents return, produce a unified analysis with five sections:

### 1. Vulnerability Summary Table

All findings sorted by risk score (highest first):

| # | Vulnerability | Vector | Severity | Exploitability | Risk | Fix |
|---|--------------|--------|----------|---------------|------|-----|

### 2. Heat Map

Which components or areas appear across multiple attack vectors? List each component with the vectors that flagged it. Components appearing in 3+ vectors are the most dangerous spots.

### 3. Critical Path

The sequence of vulnerabilities that, if chained together, would cause the worst outcome. Describe the chain step-by-step: which vulnerability enables the next, what the attacker gains at each step, and what the final impact is.

### 4. Prioritized Fix List

Mitigations ranked by three factors:
- **Risk reduction** — how much total risk the fix eliminates
- **Implementation effort** — how hard the fix is to implement (Easy/Medium/Hard)
- **Breadth** — how many vulnerabilities the fix addresses

Present as a numbered list with rationale for the ordering.

### 5. Clean Areas

Components or areas that no agent found issues with. These are tentative "safe" zones — note that absence of findings is not proof of safety, especially for areas that are hard to analyze statically.

Save the full report to the working directory as `stress_test_{slugified_topic}.md`.

## Phase 4: Next Steps

Present the report to the user and ask:
- Should we fix the Critical and High items now?
- Run `/premortem` on the areas identified as most risky?
- Re-run `/stress-test` after fixes to verify they hold?

## Rules

- **Independence is critical**: agents must NOT share findings. Do not include other agents' findings or vector assignments in any agent's prompt.
- **All agents launch in a single parallel batch**: use one message with N Agent tool calls.
- **Specific, not generic**: every vulnerability must reference the actual target — its code, components, or design decisions. Generic security checklists are useless.
- **Constructive**: every finding must include a concrete fix.
- **For code targets**: agents must READ the actual code, not just reason abstractly. Reference specific files, functions, and lines.
- **No false reassurance**: if an area is untestable without running code, say so explicitly.
- **No filtering**: include all agent findings in the synthesis, even overlapping ones. Overlap across independent agents is a strong signal.
- **Attribute findings**: always note which attack vector produced which finding.

## Pipeline Position

Sits after `/diverge-prototype` as a validation gate:
```
/diverge-prototype (build) -> /stress-test (validate) -> pick winner
```
