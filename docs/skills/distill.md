# Distill

Essence extraction via progressive compression. Takes a large artifact and runs it through a chain of compression agents, each compressing the previous output by roughly 50%. The key insight: what each agent chose to DROP reveals the priority hierarchy.

## When to Use

- You have a large research output, design doc, or meeting notes and need to extract the core priorities
- You want to understand what is truly load-bearing in a document versus what is supporting context
- You need an "elevator pitch" version of a complex artifact

## Usage

```
/distill [path/to/artifact.md or inline text]
```

**Examples:**

```
/distill diverge_auth_system.md
/distill premortem_database_migration.md
```

## How It Works

1. **Ingest** -- Read the artifact, measure its size, and confirm with the user.
2. **Compress** -- Run 4 sequential compression agents. Each compresses to roughly 50% of the previous output and explicitly lists what it dropped and why.
   - Agent 1: Original to ~50%
   - Agent 2: ~50% to ~25%
   - Agent 3: ~25% to ~12%
   - Agent 4: ~12% to ~6% (the "elevator pitch")
3. **Analyze** -- Classify every piece of content by how many rounds it survived:
   - Tier 1 (Core): survived all 4 compressions
   - Tier 2-5: progressively less essential
4. **Present** -- Show the essence, priority hierarchy, hardest cuts, and restoration order.

## Output

- A priority hierarchy and analysis saved to `distill_<slugified_topic>.md`

## Pipeline Connections

- **Before:** Any skill that produces a large artifact -- `/diverge`, `/converge`, `/premortem`
- **After:** Use the priority hierarchy to guide `/scaffold` or inform design decisions

## Tips

- Works best on substantial artifacts (500+ words). Short documents are already concise enough.
- The "hardest cuts" at each stage reveal where priority is ambiguous -- these are the most interesting boundaries to discuss with stakeholders.
