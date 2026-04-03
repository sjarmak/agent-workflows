---
name: research-project
description: "Run diverge → converge → premortem pipeline to produce a risk-annotated PRD"
argument-hint: '[N] "topic or feature description"'
allowed-tools: ["Agent", "Read", "Write", "Glob", "Grep"]
---

Run the complete PRD creation pipeline as a single invocation. Chains three skills in sequence — diverge (multi-perspective research), converge (structured debate), premortem (failure analysis) — passing file outputs between them. Produces a risk-annotated PRD ready for `/prd-build` or `/scaffold`.

## Arguments

$ARGUMENTS — format: `[N] "research question or topic"` where N is optional agent count (default: 3)

## Parse Arguments

Extract:

- **agent_count**: the optional leading integer (default 3, min 2, max 6)
- **topic**: the research question, feature description, or problem statement

If the topic is missing or unclear, ask the user to clarify before proceeding.

## Phase 1: Diverge

Invoke the `/diverge` skill with the provided arguments. This spawns N independent research agents — each with a different lens (technical feasibility, user experience, risk/failure modes, prior art, first principles) — to explore the topic from uncorrelated perspectives.

Wait for the PRD file to be created (format: `prd_{slugified_topic}.md`).

The diverge output is a synthesis of all agent findings plus a draft PRD. Do NOT proceed until the file exists.

## Phase 2: Converge

Invoke the `/converge` skill, passing the PRD file path from Phase 1.

This runs a structured debate: agents advocate competing positions from the diverge output, challenge each other's assumptions, propose compromises, and reach consensus. The result is a refined PRD with tensions resolved and trade-offs made explicit.

Wait for the convergence report and updated PRD.

## Phase 3: Premortem

Invoke the `/premortem` skill, passing the refined PRD from Phase 2.

This spawns N agents who each write a narrative from the future where the project has failed — each for a different root cause (technical, operational, security, scope, organizational). Synthesizes into a risk registry with severity ratings and mitigations, then annotates the PRD with the top risks.

Wait for the risk-annotated PRD.

## Phase 4: Present Results

Present the final risk-annotated PRD path and a brief summary:

- Key decisions from convergence (what was debated, what was chosen, and why)
- Top 3 risks from premortem (with severity and recommended mitigations)
- Recommended next step (usually `/prd-build <prd-path>` for parallel implementation, or `/scaffold <prd-path>` for build-order planning)

## Rules

- Do NOT ask questions between phases — flow continuously
- Do NOT skip phases — all three must run
- If a phase fails, report the error and stop (do not proceed with incomplete input)
- Each phase produces files — pass file paths between phases, not inline content
- The three phases MUST run in sequence (each depends on the previous output)

## Pipeline Position

- **Before:** `/brainstorm` for ideation when the problem space is vague, or start here when you have a clear question
- **After:** `/prd-build` to decompose the PRD into parallel work units and implement, or `/scaffold` for build-order planning, or `/diverge-prototype` to spike implementations before committing
