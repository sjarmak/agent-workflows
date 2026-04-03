Review changed code for reuse, quality, and efficiency, then fix any issues found.

## Arguments

$ARGUMENTS — format: `[file path | glob pattern | blank]`

- If a file path or glob is provided, scope the review to those files.
- If no argument is provided, review all uncommitted changes via `git diff`.

## Parse Arguments

Extract:

- **scope**: a file path, glob pattern, or empty (defaults to uncommitted changes)

## Phase 1: Identify Changes

1. If scope is empty, run `git diff --name-only` to list changed files. If there are no uncommitted changes, check `git diff --name-only HEAD~1` for the last commit.
2. If scope is a path or pattern, resolve matching files.
3. For each file, run `git diff` (or `git diff HEAD~1` if already committed) to get the actual changes.
4. Present the scope to the user: file count, total lines changed, and a one-line summary per file.

## Phase 2: Analyze

For each changed file, look for:

- **Unnecessary complexity** — can this be simpler without losing clarity?
- **Duplicated code** — shared logic that should be extracted
- **Dead code** — unused imports, unreachable branches, commented-out code
- **Over-engineering** — abstractions that aren't needed yet
- **Missing error handling** — at system boundaries only (user input, external APIs)

## Phase 3: Apply Fixes

Apply fixes directly — don't just report issues. For each fix:

1. Make the change
2. Verify the file still parses / compiles
3. If tests exist, run them after all changes to confirm nothing broke

## Rules

- **Scope discipline**: only refine recently modified code unless the user explicitly asks for broader review.
- **Preserve functionality**: never change what the code does, only how it does it.
- **Prefer deletion over addition**: the best code is code that doesn't exist.
- **Clarity over brevity**: explicit code is often better than compact code. Avoid:
  - Overly clever solutions that are hard to understand
  - Combining too many concerns into single functions
  - Removing helpful abstractions that improve code organization
  - Dense one-liners or nested ternaries that sacrifice readability
  - Changes that make the code harder to debug or extend
- **No cosmetic drift**: don't reformat code you didn't change for functional reasons.
- **Run tests**: always verify after changes.

## Pipeline Position

- Runs after implementation, before code review and commit.
- In `/focus`, this is the simplify phase between execute and review.
- Can be used standalone on any codebase at any time.
