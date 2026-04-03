Comprehensive code review of uncommitted or recently committed changes. Reviews for security, quality, and maintainability, then reports findings by severity.

## Arguments

$ARGUMENTS — format: `[file path | glob pattern | PR number | blank]`

- If a file path or glob is provided, scope the review to those files.
- If a PR number is provided, review that pull request via `gh pr diff`.
- If no argument is provided, review all uncommitted changes.

## Parse Arguments

Extract:

- **scope**: a file path, glob pattern, PR number (digits only), or empty

## Phase 1: Gather Changes

1. **Uncommitted changes** (default): run `git diff --staged` and `git diff` to capture all changes.
2. **File/glob scope**: read the specified files and their diffs.
3. **PR scope**: run `gh pr diff <number>` to get the full diff.
4. If no changes are found, check `git log --oneline -5` and offer to review the last commit.

For each changed file, also read surrounding code — don't review changes in isolation.

## Phase 2: Review

Launch 3 parallel review agents, each focused on a different severity tier:

### Agent 1: Security (CRITICAL)

```
Review ONLY for security issues. Flag these if found:

- Hardcoded credentials (API keys, passwords, tokens, connection strings)
- SQL injection (string concatenation in queries)
- XSS vulnerabilities (unescaped user input in HTML/JSX)
- Path traversal (user-controlled file paths without sanitization)
- CSRF vulnerabilities (state-changing endpoints without protection)
- Authentication bypasses (missing auth checks on protected routes)
- Exposed secrets in logs (logging tokens, passwords, PII)
- Insecure deserialization or command injection

For each issue, report: file path, line number, what's wrong, and how to fix it.
Only report issues you are >80% confident are real problems, not pre-existing issues.
```

### Agent 2: Code Quality (HIGH)

```
Review for code quality issues. Flag these if found:

- Functions over 50 lines
- Files over 800 lines
- Nesting depth over 4 levels
- Missing error handling (unhandled rejections, empty catch blocks)
- Mutation patterns where immutable operations should be used
- Debug logging left in (console.log, print statements)
- Dead code (commented-out code, unused imports, unreachable branches)
- Missing tests for new code paths

Consolidate similar issues (e.g., "5 functions missing error handling" not 5 separate findings).
Only report issues in changed code. Skip stylistic preferences unless they violate project conventions.
```

### Agent 3: Performance & Best Practices (MEDIUM/LOW)

```
Review for performance and best practice issues:

- Inefficient algorithms (O(n^2) when O(n) or O(n log n) is possible)
- Missing caching for repeated expensive computations
- Large bundle imports when tree-shakeable alternatives exist
- N+1 query patterns
- Unbounded queries without LIMIT
- Missing timeouts on external calls
- TODO/FIXME without issue references
- Magic numbers without explanation

Only flag issues that materially affect the code. Skip minor nitpicks.
```

## Phase 3: Score and Filter

For each finding from Phase 2, assess confidence (0-100):

- **0-25**: Likely false positive or pre-existing issue — drop it.
- **25-50**: Might be real but could be a nitpick — drop it.
- **50-75**: Real issue but low impact — include only if CRITICAL/HIGH.
- **75-100**: Confirmed real issue with practical impact — always include.

Filter out findings below 75 confidence.

## Phase 4: Report

Present findings grouped by severity:

```
[CRITICAL] Description
File: path/to/file.ts:42
Issue: What's wrong and why it matters
Fix: Specific fix recommendation

[HIGH] Description
File: path/to/file.ts:88
Issue: What's wrong
Fix: How to fix it
```

End with a summary table:

```
## Review Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 0     | pass   |
| HIGH     | 2     | warn   |
| MEDIUM   | 1     | info   |
| LOW      | 0     | —      |

Verdict: APPROVE / WARNING / BLOCK
```

- **APPROVE**: No CRITICAL or HIGH issues
- **WARNING**: HIGH issues only (can proceed with caution)
- **BLOCK**: CRITICAL issues found — must fix before proceeding

## Rules

- **Confidence filtering**: only report issues with >75% confidence. No noise.
- **Changed code only**: don't flag issues in unchanged code unless they are CRITICAL security issues.
- **Consolidate**: group similar issues rather than listing each instance separately.
- **No cosmetic complaints**: skip stylistic preferences unless they violate explicit project conventions.
- **Actionable fixes**: every finding must include a specific fix, not just a complaint.
- **Adapt to project**: check for CLAUDE.md, project rules, and established patterns. Match the codebase.

## Pipeline Position

- Runs after simplify, before commit.
- In `/focus`, this is the review phase between simplify and close.
- Can be used standalone on any codebase, branch, or PR.
