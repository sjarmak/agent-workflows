# Crossbreed

Structural recombination of existing designs. Takes 2-3 prototypes or design approaches and spawns agents to create hybrid designs, each with a different "dominant parent" whose architecture leads while grafting specific elements from the others.

## When to Use

- You have multiple promising prototypes from `/diverge-prototype` and want to combine their best elements rather than picking just one
- Two designs each excel in different areas and you suspect a hybrid would outperform either parent
- You want to discover which design elements are naturally composable and which resist combination

## Usage

```
/crossbreed [N] path1 path2 [path3]
```

**Examples:**

```
/crossbreed branch-a/PROTOTYPE_NOTES.md branch-b/PROTOTYPE_NOTES.md
/crossbreed 4 design-a.md design-b.md design-c.md
```

N defaults to one hybrid per parent. Requires 2-3 parent paths.

## How It Works

1. **Analyze Parents** -- Extract structural elements (architecture, data model, algorithms, API design, dependencies, error handling) from each parent. Identify strengths and weaknesses.
2. **Design Strategies** -- Create recombination strategies: A-dominant with B's strength grafted, B-dominant with A's strength grafted, cherry-pick best of each, etc.
3. **Spawn** -- Launch agents in isolated worktrees. Each starts from its dominant parent's codebase and grafts specified elements from others.
4. **Compare** -- Assess coherence, graft compatibility, emergent properties, and seam risk for each hybrid.

## Output

- N hybrid branches in git worktrees
- A graft compatibility map, seam risk assessment, and recommended hybrid presented inline

## Pipeline Connections

- **Before:** `/diverge-prototype` for generating parent prototypes
- **After:** `/stress-test` to find where seams break, `/scaffold` to plan the build

## Tips

- Seam locations (where parent code was spliced together) are where bugs will live. Review `CROSSBREED_NOTES.md` for documented seams.
- A low coherence score (1-2) is a valid and useful result -- it means those elements resist combination, which is valuable information.
