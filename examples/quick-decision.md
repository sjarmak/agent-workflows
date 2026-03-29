# Example: Quick Decision — Converge Without Diverge

You don't always need the full pipeline. If you already know the options, skip straight to `/converge` for a structured debate.

## Scenario

Your team is split on state management for a new React app: Redux Toolkit vs Zustand vs React Query + Context. Everyone has opinions. You want a structured way to evaluate the trade-offs.

## Running the Debate

```
/converge 3 "We need to pick a state management approach for our new React dashboard. Options: (1) Redux Toolkit — the team knows it, but it's verbose. (2) Zustand — minimal boilerplate, but less ecosystem. (3) React Query + Context — server state in RQ, minimal client state in Context."
```

What happens:
1. Claude frames the debate with evaluation criteria (learning curve, boilerplate, performance, ecosystem, testing)
2. Three teammates are assigned:
   - **Redux advocate**: argues for familiarity, middleware ecosystem, devtools
   - **Zustand advocate**: argues for simplicity, bundle size, less boilerplate
   - **RQ + Context advocate**: argues for separation of concerns, cache management
3. Two rounds of debate where each advocate steel-mans their position AND concedes genuine weaknesses
4. Synthesis with resolved points, remaining tensions, and a recommendation

## Sample Output (abbreviated)

### Resolved Points
- All three approaches handle the core requirements. This is a trade-off decision, not a capability decision.
- Server state should be managed by React Query regardless of choice (Redux advocate conceded this in Round 2).

### Refined Trade-offs
- **Familiarity vs learning curve**: Redux has team knowledge but Zustand is learnable in a day. Trade-off is real but small.
- **Ecosystem vs simplicity**: Redux middleware ecosystem matters IF you need sagas/thunks for complex flows. If most state is server-derived, it's unnecessary complexity.

### Recommended Path
Zustand for client state + React Query for server state. The team's Redux knowledge transfers easily, the dashboard is primarily server-data-driven (favoring RQ), and Zustand handles the small amount of client state without boilerplate overhead.

## When to Use This Pattern

- **Architecture decisions** with 2-4 clear options
- **Technology choices** where the team has differing preferences
- **Design trade-offs** where both sides have merit
- **Post-mortem analysis** where you want to evaluate what went wrong from multiple angles

The key insight: `/converge` forces steel-manning. Each advocate must acknowledge what the other positions get right, which produces better analysis than a simple pros/cons list.
