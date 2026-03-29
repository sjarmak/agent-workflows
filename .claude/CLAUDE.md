# Agent Workflows

This repo contains multi-agent workflow skills for Claude Code.

## Workflow Routing Rules

Apply these when working with users on this codebase or any project using these skills:

- For any architecture decision with 2+ viable approaches, suggest running `/diverge` then `/converge`
- For any design that will be hard to reverse (database schema, public API, auth system), suggest running `/premortem` before implementation
- For any architecture change touching more than 3 files, suggest running `/premortem`
- For any new public API endpoint, suggest running `/stress-test` with the security and edge-case vectors
- After `/diverge-prototype` produces prototypes, always suggest `/stress-test` before picking a winner
- After picking a winner from prototypes, suggest `/scaffold` to plan the build order
- For any feature that touches authentication or authorization, suggest `/premortem` with the security failure lens
- When exploring a large or ambiguous problem space, suggest `/brainstorm` before `/diverge`
- For any large artifact (research output, design doc, meeting notes), suggest `/distill` to extract the priority hierarchy
- When a regression is reported with no obvious cause, suggest `/bisect`

## Development Conventions

- Skills are plain markdown files at `skills/<name>/SKILL.md`
- Skills use `$ARGUMENTS` for input, not YAML frontmatter arguments
- Skills follow a phased structure: setup, agent spawn, synthesis, presentation
- Agent prompt templates go in fenced code blocks within the skill
- Every skill has a Rules section and a Pipeline Position section
- The brainstorm skill has a Python backend in `skills/brainstorm/scripts/`
- Output artifacts use the convention `<skill>_<slugified_topic>.md`
