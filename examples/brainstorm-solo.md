# Example: Brainstorm — Structured Ideation

The brainstorm skill forces you past the obvious ideas by requiring every new idea to be structurally distinct from all previous ones. It's like having a creative partner who never lets you repeat yourself.

## Scenario

You need to design a notification system for a developer platform. The obvious approaches (email, Slack webhook, in-app toast) come to mind immediately — but are they the best?

## Starting a Session

```
/brainstorm 15 How should we notify developers about build failures, deployment status, and security alerts in our platform?
```

The `15` sets the target to 15 ideas (default is 30). Claude will:

1. **Initialize** the session with a unique ID
2. **Research** existing notification patterns (Phase 2)
3. **Catalog prior art** — email, Slack, SMS, push notifications, etc. become "banned territory"
4. **Begin divergence** — now you generate 15 ideas that are structurally different from all prior art AND from each other

## What a Session Looks Like

### Research Phase

Claude searches for existing notification approaches and catalogs them:

```
[x] Email notifications (traditional async delivery)
[x] Slack/Teams webhooks (channel-based real-time)
[x] Push notifications (mobile/desktop OS-level)
[x] In-app notification center (feed/inbox pattern)
[x] SMS/pager (high-urgency escalation)
[x] RSS/Atom feeds (pull-based subscription)

6 prior art entries total — all banned during brainstorming.
```

### Divergence Phase

Now you (and Claude, as a brainstorming partner) generate ideas. Each one goes through a uniqueness gate:

```
> Idea: "Ambient dashboard that changes color based on system health"

#01  Ambient dashboard that changes color based on system health
     [████████░░░░░░░░░░░░] 1/15  14 to go
```

If you propose something too similar to an existing idea:

```
> Idea: "Dashboard with status indicators"

  Too close to #01 "Ambient dashboard that changes color...".
  The shape needs to change, not just the surface.

  Consider: What if the solution had to work without any visual UI at all?
```

The system provides varied nudges and constraint-shifting questions to push you into new territory.

### Convergence Phase

After hitting 15 ideas, rate each on Feasibility, Novelty, and Impact (1-5):

```
/brainstorm rate <session> 7 4 5 3
#07  Git-blame-aware alerts that only notify the person whose code broke
     F=4  N=5  I=3  total=12/15
```

Generate the final report to see rankings, hidden gems, and quick wins.

## Key Mechanics

### Shape Uniqueness

The core innovation. "Shape" means the structural approach — not surface details. Two ideas that would produce the same flowchart are the same shape, even if they use different technologies.

The system enforces this with multiple layers:
- **Lexical**: word and bigram overlap detection
- **Semantic**: embedding-based similarity (requires `sentence-transformers`)
- **Structural**: FTS5 keyword boosting for borderline cases
- **Code**: if you prototype ideas in sandboxes, code structure is also compared

### Prototype Sandboxes

For each idea, you can create a sandbox to build a minimal prototype:

```bash
sandbox.sh create <session> <idea-number>
```

Then run `check-code` to verify the prototype is structurally different from other prototypes. This catches ideas that sound different in English but produce identical code.

### Prior Art as Exclusion Zones

Prior art isn't just documentation — it actively shapes the brainstorm. By mapping existing approaches and banning them, you force yourself into genuinely new territory. The research phase isn't busywork; it's building the boundaries that make divergence productive.

## Tips

- **Start with a high target** (20-30) if you're exploring a wide problem. You'll be surprised how creative you get once the obvious ideas are exhausted.
- **Let Claude propose ideas too.** It's a brainstorming partner, not a scribe.
- **Don't filter during divergence.** Bad ideas at position 8 often inspire good ideas at position 12.
- **Use the constraint questions.** When the system asks "What if you only had 1 GB of memory?", take it seriously — constraints unlock new solution shapes.
