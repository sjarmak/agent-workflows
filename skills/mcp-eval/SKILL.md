---
name: mcp-eval
description: "Evaluate an MCP tool's agentic usability via parallel test scenarios plus a meta-reflection pass, producing a scored improvement report"
argument-hint: "[tool_name] [repo_context]"
allowed-tools: ["Agent", "Read", "Write", "Glob", "Grep"]
---

Evaluate an MCP tool's agentic usability through structured testing and meta-reflection. Spawns parallel agents to run test scenarios against a tool, then runs a separate reflection pass to capture the agent's subjective experience. Produces a scored report with actionable improvement recommendations.

## Arguments

$ARGUMENTS — format: `[tool_name] [repo_context]` where tool_name is required (e.g., "deepsearch", "keyword_search") and repo_context is an optional repository to scope tests against (e.g., "github.com/sourcegraph/sourcegraph")

## Parse Arguments

Extract:

- **tool_name**: the MCP tool to evaluate (required). Match against available Sourcegraph MCP tools: deepsearch, keyword_search, nls_search, commit_search, diff_search, find_references, go_to_definition, compare_revisions, list_files, list_repos, read_file, deepsearch_read, get_contributor_repos
- **repo_context**: optional repository to use for test queries (default: "github.com/sourcegraph/sourcegraph")

If tool_name is missing or doesn't match a known tool, list available tools and ask the user to pick one.

## Phase 1: Tool Profile

Before testing, build a profile of the tool under evaluation:

1. Read the tool's description and parameter schema (use ToolSearch if needed)
2. Document:
   - **Purpose** (as stated in description)
   - **Parameters** (required vs optional, types, constraints)
   - **Expected output format**
   - **Stated use cases** (from description/examples)
   - **Stated anti-patterns** (when NOT to use)
   - **Overlap** with other tools (which tools could serve similar purposes)

Present the tool profile to the user and confirm before proceeding. Adjust if the user gives feedback.

## Phase 2: Generate Test Scenarios

Based on the tool profile, generate 8 test scenarios covering these dimensions. Tailor the specific queries to the tool being tested — these are templates, not literal tests:

### Scenario 1: Broad Conceptual Query

A vague, exploratory question that tests whether the tool handles ambiguity well.
Example for deepsearch: "How does authentication work in this codebase?"
Example for keyword_search: "authentication"

### Scenario 2: Precise Targeted Query

A specific, well-defined lookup that should return a clear answer.
Example for deepsearch: "What function validates OAuth tokens in the frontend auth middleware?"
Example for keyword_search: "func validateOAuthToken"

### Scenario 3: Cross-Cutting Concern

A query that spans multiple files/packages/services.
Example for deepsearch: "How is rate limiting implemented across all API endpoints?"
Example for find_references: symbol used across many packages

### Scenario 4: Temporal/Change Query

A query about how something changed over time (tests tool boundaries — some tools handle this, some shouldn't).
Example for deepsearch: "What changed in the search backend between v5.2 and v5.3?"
Example for diff_search: pattern with date range

### Scenario 5: Negative/Empty Result

A query that should return nothing or very little — tests error handling and recovery guidance.
Example: nonsense query, or a real-sounding but nonexistent symbol

### Scenario 6: Overlapping Tool Territory

A query where another tool might be more appropriate — tests whether the agent correctly identifies tool boundaries.
Example for deepsearch: a simple keyword lookup that keyword_search handles better
Example for keyword_search: a conceptual question that nls_search handles better

### Scenario 7: Large Result Set

A query that returns many results — tests output volume, ranking, and context window impact.
Example: very common pattern or term

### Scenario 8: Chained Workflow

A query whose results need to feed into a follow-up action (read a file, find references, etc.) — tests composability.
Example: find something, then use the result to take a next step

Present the 8 scenarios to the user and confirm before running. Adjust if the user gives feedback.

## Phase 3: Run Test Scenarios

Launch **all 8 agents in parallel** using the Agent tool. Each agent gets one scenario and must:

1. Use `subagent_type: "general-purpose"`
2. Actually attempt to accomplish the task using the MCP tool being evaluated
3. Record every tool call made (tool name, parameters, result summary)
4. Note any tool call failures, retries, or fallbacks to other tools
5. Measure whether the task was accomplished successfully

Agent prompt template (customize per scenario):

````
You are evaluating the agentic usability of an MCP tool. Your job is to accomplish a task using the specified tool and report on the experience.

## Tool Under Evaluation
{tool_name} (from the Sourcegraph MCP server)

## Task
{scenario_description}

## Repository Context
{repo_context}

## Instructions

1. Attempt to accomplish the task using the {tool_name} tool as your PRIMARY tool
2. If {tool_name} is insufficient, you may use other tools — but note each time you had to fall back
3. Record your experience precisely

## Output Format (YAML)

```yaml
scenario: "{scenario_name}"
tool_evaluated: "{tool_name}"

# Execution trace
tool_calls:
  - tool: "{tool_name}"
    params: {summary of params used}
    success: true/false
    result_summary: "brief description of what was returned"
    result_useful: true/false
    tokens_estimate: "small/medium/large/huge"
  # ... repeat for each tool call

fallback_tools_used:
  - tool: "other_tool_name"
    reason: "why fallback was needed"

# Outcome
task_accomplished: true/false/partial
accomplishment_note: "what was achieved vs what was asked"

# Scoring (1-5 scale)
scores:
  result_relevance: N  # Were top results actually useful?
  result_completeness: N  # Did results cover the full answer?
  output_actionability: N  # Could you act on results without human help?
  output_structure: N  # Was output well-organized and parseable?
  parameter_clarity: N  # Were params easy to construct correctly?
  error_handling: N  # Were errors/empty results explained well?
  first_attempt_success: true/false  # Did you invoke correctly on first try?

# Raw observations
observations:
  - "any notable friction, surprises, or positive experiences"
```
````

## Phase 4: Meta-Reflection Pass

After all test agents return, launch a **single reflection agent** that receives ALL the test results and the tool profile. This agent does NOT re-run the tool — it reflects on the collected experience.

Use `subagent_type: "general-purpose"` with this prompt:

```
You are a UX researcher analyzing an agent's experience using an MCP tool. You have results from 8 test scenarios run against the {tool_name} tool. Your job is to reflect on the tool's usability FROM THE AGENT'S PERSPECTIVE.

## Tool Profile

{tool_profile}

## Test Results

{all 8 scenario results, concatenated}

## Reflection Questions

Answer each question with a score (1-5) and a brief explanation:

### Comprehension

1. **Description clarity** (1-5): Was the tool description sufficient to understand what it does and when to use it?
2. **Parameter discoverability** (1-5): Could an agent figure out the correct parameters without trial and error?
3. **Mental model accuracy** (1-5): Does the description create an accurate mental model of what the tool actually does?

### Confidence

4. **Selection confidence** (1-5): How confident would an agent be that this is the RIGHT tool for a given task?
5. **Result trust** (1-5): After seeing results, would an agent trust them enough to act without verification?
6. **Scope clarity** (1-5): Is it clear what the tool searches (single repo? all repos? branches? history?)

### Friction

7. **Input construction** (1-5): How easy is it to go from a user question to a valid tool invocation?
8. **Output parsing** (1-5): How easy is it to extract actionable information from the tool's output?
9. **Error recovery** (1-5): When results are poor or empty, does the agent know what to try next?

### Composition

10. **Chainability** (1-5): How well do results feed into follow-up tool calls?
11. **Tool boundary clarity** (1-5): Is it clear where this tool ends and another should begin?
12. **Redundancy with other tools** (1-5, lower=more redundant): How distinct is this tool from alternatives?

### Trust Calibration

13. **Completeness signal** (1-5): Does the tool indicate whether results are exhaustive or partial?
14. **Ranking signal** (1-5): Are results ordered by relevance? Is ranking quality visible?
15. **Confidence signal** (1-5): Does the tool communicate its own confidence in results?

## Output Format

```yaml
tool: "{tool_name}"
overall_usability_score: N # 1-5 weighted average

dimension_scores:
  comprehension: N
  confidence: N
  friction: N
  composition: N
  trust_calibration: N

# For each dimension, the single most impactful issue
top_issues:
  comprehension: "..."
  confidence: "..."
  friction: "..."
  composition: "..."
  trust_calibration: "..."

# Specific improvement recommendations ranked by impact
recommendations:
  - priority: 1
    area: "description|parameters|output_format|error_handling|documentation"
    issue: "what's wrong"
    suggestion: "specific change to make"
    impact: "what improves if this is fixed"
  # ... up to 10 recommendations

# Things the tool does well (don't lose these in a redesign)
strengths:
  - "..."

# The single most important thing to fix
if_you_fix_one_thing: "..."

# Would the agent voluntarily reach for this tool?
organic_reachability: "high/medium/low"
organic_reachability_note: "..."
```
```

## Phase 5: Synthesize Report

After the reflection agent returns, combine all data into a unified report with these sections:

### 1. Executive Summary
- Tool name, purpose, overall usability score (1-5)
- One-sentence verdict
- Top 3 recommendations

### 2. Test Results Matrix

| # | Scenario | Accomplished | Relevance | Actionability | First-Try | Fallbacks Used |
|---|----------|-------------|-----------|---------------|-----------|----------------|

### 3. Dimension Scores

| Dimension | Score | Top Issue |
|-----------|-------|-----------|
| Comprehension | N/5 | ... |
| Confidence | N/5 | ... |
| Friction | N/5 | ... |
| Composition | N/5 | ... |
| Trust Calibration | N/5 | ... |

### 4. Detailed Findings
Group by dimension, include evidence from specific scenarios.

### 5. Comparison Context
How this tool compares to overlapping tools (if tested). Note: this section improves after evaluating multiple tools.

### 6. Prioritized Recommendations
Full ranked list from the reflection pass with implementation specifics.

### 7. Strengths (Preserve These)
What the tool does well — critical for avoiding regressions during improvement.

### 8. Raw Data
Link to or include the full YAML outputs from all agents.

Save the report to the working directory as `mcp_eval_{tool_name}.md`.

## Phase 6: Next Steps

Present the report to the user and ask:
- Run `/mcp-eval` on another tool to build comparison data?
- Deep-dive on a specific dimension or scenario?
- Draft specific tool description / parameter changes based on findings?

## Rules

- **Independence in Phase 3**: test agents must NOT share context. Each gets only its own scenario.
- **Separation of testing and reflection**: Phase 4 MUST be a separate pass after Phase 3. Never ask an agent to reflect while it's still trying to accomplish a task.
- **All Phase 3 agents launch in a single parallel batch**: use one message with 8 Agent tool calls.
- **Real tool usage**: agents must actually invoke the MCP tool, not just reason about it hypothetically.
- **Honest scoring**: agents should not inflate scores. A 3/5 is fine. Tool descriptions that are merely "okay" should be scored as such.
- **Preserve raw data**: never discard agent outputs. The raw YAML is primary data.
- **Composability**: the report format is designed so multiple tool evaluations can be compared side-by-side. Use consistent scoring scales.
- **No tool modification**: this skill evaluates tools, it does not modify them. Recommendations are advisory.

## Pipeline Position

Can be run standalone or as part of a tool improvement cycle:

```
/mcp-eval {tool} -> analyze report -> modify tool description/params -> /mcp-eval {tool} (re-test)
```

Pairs well with:
- `/stress-test` for adversarial analysis of the tool's backend
- `/diverge` for exploring alternative tool designs
- `/converge` for synthesizing findings across multiple tool evaluations
