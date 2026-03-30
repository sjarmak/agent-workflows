# Stress Test

Parallel adversarial attack surface analysis. Spawns N independent agents, each tasked with BREAKING a system from a different attack angle. Synthesizes findings into a vulnerability map with severity ratings.

## When to Use

- After prototyping, to validate a design or implementation before shipping
- For any new public API endpoint (test security, edge cases, and scale vectors)
- When you want a systematic adversarial review of an existing system or component

## Usage

```
/stress-test [N] [path/to/code_or_design or inline description]
```

**Examples:**

```
/stress-test src/auth/
/stress-test 7 "Our new rate-limiting middleware"
```

N sets the attack agent count (default: 5, range: 3-7).

## How It Works

1. **Identify Target** -- Analyze the system to understand components, data flows, trust boundaries, and deployment model.
2. **Spawn** -- Launch N agents in parallel with unique attack vectors: edge cases/input boundaries, scale/resource exhaustion, security/access control, dependency failure, concurrency/state, data integrity, deployment/operations.
3. **Synthesize** -- Produce a vulnerability summary table, heat map (components appearing across multiple vectors), critical path (worst-case attack chain), and prioritized fix list.

## Output

- A vulnerability report saved to `stress_test_<slugified_topic>.md`

## Pipeline Connections

- **Before:** `/diverge-prototype` for building prototypes, `/crossbreed` for hybrid designs
- **After:** Fix critical issues, then optionally re-run to verify fixes hold

## Tips

- For code targets, agents read the actual code and reference specific files, functions, and line numbers. Point the skill at a directory for best results.
- Components that appear in 3+ independent attack vectors are the most dangerous spots -- prioritize those fixes first.
