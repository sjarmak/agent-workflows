# Agent Workflows Documentation

Reference documentation for all workflow skills and pre-built workflow pipelines.

## Skills by Category

### Ideation

| Skill                              | Description                                                      |
| ---------------------------------- | ---------------------------------------------------------------- |
| [brainstorm](skills/brainstorm.md) | Constrained divergent ideation with shape-uniqueness enforcement |
| [diverge](skills/diverge.md)       | Multi-perspective parallel research from independent angles      |
| [fracture](skills/fracture.md)     | Competitive problem decomposition into subproblems               |

### Decision

| Skill                                                  | Description                                                         |
| ------------------------------------------------------ | ------------------------------------------------------------------- |
| [converge](skills/converge.md)                         | Structured debate and refinement via agent teams                    |
| [distill](skills/distill.md)                           | Progressive compression and essence extraction from large artifacts |
| [constraint-inversion](skills/constraint-inversion.md) | What-if constraint removal to find hidden design possibilities      |

### Risk

| Skill                                | Description                                                     |
| ------------------------------------ | --------------------------------------------------------------- |
| [premortem](skills/premortem.md)     | Prospective failure narratives to surface risks before building |
| [stress-test](skills/stress-test.md) | Parallel adversarial attack surface analysis                    |

### Prototyping

| Skill                                            | Description                                                   |
| ------------------------------------------------ | ------------------------------------------------------------- |
| [diverge-prototype](skills/diverge-prototype.md) | Parallel prototyping in isolated worktrees                    |
| [crossbreed](skills/crossbreed.md)               | Structural recombination of existing prototypes or designs    |
| [entangle](skills/entangle.md)                   | Dependent co-design of coupled subsystems via shared contract |

### Specification

| Skill                            | Description                                         |
| -------------------------------- | --------------------------------------------------- |
| [contract](skills/contract.md)   | Bottom-up specification generation from examples    |
| [replicate](skills/replicate.md) | Independent reimplementation to verify spec quality |

### Analysis

| Skill                          | Description                                              |
| ------------------------------ | -------------------------------------------------------- |
| [diffuse](skills/diffuse.md)   | Blast radius impact mapping for proposed changes         |
| [scaffold](skills/scaffold.md) | Build-order planning via competing sequencing strategies |
| [migrate](skills/migrate.md)   | Parallel migration strategy exploration                  |

### Debugging

| Skill                      | Description                                             |
| -------------------------- | ------------------------------------------------------- |
| [bisect](skills/bisect.md) | Binary search for root cause of a regression or failure |

### Execution

| Skill                            | Description                                                               |
| -------------------------------- | ------------------------------------------------------------------------- |
| [prd-build](skills/prd-build.md) | Automated PRD-to-implementation via parallel agents in isolated worktrees |

### Pipelines

| Skill                                          | Description                                                       |
| ---------------------------------------------- | ----------------------------------------------------------------- |
| [research-project](skills/research-project.md) | Chains diverge-converge-premortem to produce a risk-annotated PRD |

### Meta

| Skill                        | Description                                                       |
| ---------------------------- | ----------------------------------------------------------------- |
| [compose](skills/compose.md) | Meta-workflow that designs which skills to chain for a given goal |

## Workflow Guides

| Workflow                                              | Description                                                         |
| ----------------------------------------------------- | ------------------------------------------------------------------- |
| [Research Project](workflows/research-project.md)     | The complete diverge-to-scaffold pipeline for new features          |
| [Quick Decision](workflows/quick-decision.md)         | Fast converge-to-build path for time-sensitive decisions            |
| [Architecture Spike](workflows/architecture-spike.md) | Prototype, stress-test, and scaffold path for technical exploration |
| [Research-to-Build](workflows/research-to-build.md)   | End-to-end research-project then prd-build for fully automated flow |
| [Spec Validation](workflows/spec-validation.md)       | Contract-to-replicate loop for specification quality                |
| [Change Impact](workflows/change-impact.md)           | Diffuse-to-stress-test change assessment                            |
| [Migration Planning](workflows/migration-planning.md) | Migrate-to-scaffold path for system transitions                     |
