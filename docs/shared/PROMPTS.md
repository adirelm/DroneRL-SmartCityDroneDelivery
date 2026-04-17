# PROMPTS -- Prompt Engineering Log

## Overview

DroneRL was built using **Claude AI** with a **vibe coding** methodology.
Rather than writing every line by hand, the development process followed
a structured prompt-driven workflow where Claude generated the PRD,
implementation plan, task list, and code -- with the developer guiding
direction, validating outputs, and iterating on design.

## Workflow

The project followed a five-stage pipeline:

```
PRD  -->  PLAN  -->  TODO (800+)  -->  Validate  -->  Execute
```

1. **PRD** -- A Product Requirements Document was generated from a
   high-level description of the desired system.
2. **PLAN** -- The PRD was converted into a detailed implementation plan
   with architecture decisions, module breakdown, and data flow.
3. **TODO** -- Over 800 granular tasks with checkboxes were generated
   from the plan, covering every function, class, test, and config value.
4. **Validate** -- The TODO list was cross-referenced against the PRD to
   ensure full coverage of all requirements.
5. **Execute** -- Tasks were implemented following TDD (Test-Driven
   Development) principles, with Claude generating code and the
   developer reviewing and testing.

## Key Prompts Used

### 1. Initial System Description

> "Create a drone RL simulation with Q-Learning on a grid with
> buildings, traps, wind zones. The drone should learn to navigate from
> a start position to a goal position. Include a Pygame GUI with a
> dashboard showing training metrics, a grid editor, and demo mode."

This prompt established the core requirements: Q-Learning algorithm,
grid-based environment with obstacle types, and a visual interface.

### 2. PRD Generation

> "Generate a PRD (Product Requirements Document) from these
> requirements. Include functional requirements, non-functional
> requirements, architecture overview, and success criteria."

Claude produced a structured PRD covering the RL algorithm, environment
specification, GUI components, configuration system, and convergence
criteria.

### 3. Implementation Plan

> "From the PRD, create a detailed implementation plan. Break it into
> modules with clear responsibilities. Define the class hierarchy, data
> flow, and file structure."

This yielded the layered architecture (Config -> SDK -> Agent/Environment
-> Trainer -> GUI) and the single-responsibility class design.

### 4. Task Generation

> "Generate 800+ tasks with checkboxes covering every aspect of the
> implementation. Include setup, config, core RL, environment, GUI
> rendering, editor, dashboard, overlays, testing, and documentation."

The massive task list served as a living checklist during development,
ensuring no feature or edge case was overlooked.

### 5. Validation

> "Validate that the TODO list covers all PRD requirements. Flag any
> gaps or missing items."

Cross-referencing revealed a few gaps (e.g., wind drift probability
configuration, convergence banner in the dashboard) that were added
before implementation began.

### 6. Implementation

> "Implement following TDD approach. Start with config_loader and
> logger, then agent, environment, trainer, SDK, and finally GUI
> components."

Code was generated bottom-up: infrastructure first (config, logging),
then core RL (agent, environment, trainer), then the SDK facade, and
finally the GUI layer. Each module was tested before building the next.

## Iterations and Refinements

### Editor Improvements

The initial editor was a simple click-to-toggle system. Iterative
prompts refined it to include:
- Type selector buttons (Building, Trap, Wind) displayed below the grid
- Hover preview with semi-transparent color overlay
- Click-to-place / click-again-to-remove toggle behavior
- Keyboard shortcut (T) to cycle through cell types

### Convergence Logic

Early convergence detection was too simple (just checking goal rate).
Iterations added:
- Minimum episode threshold to prevent false positives
- Epsilon floor requirement to ensure the agent is exploiting
- Rolling window calculation over the last 100 episodes
- Auto-pause and overlay activation on convergence

### UI/UX Refinements

Multiple rounds of prompts improved the visual experience:
- Context-aware button panel that shows different buttons based on
  application state (editing, training, paused, converged, demo)
- Reward history graph with min/max labels and zero-line
- Goal rate progress bar in the metrics panel
- Demo mode with trail visualization and 3-second pause at goal
- Pulsing goal cell animation and wind zone wave effects
- Status bar showing current mode and primary action hint

### Reward Tuning

The reward structure went through several iterations to achieve
consistent convergence:
- Initial values caused the agent to avoid traps but wander aimlessly
- Step penalty was tuned to -1 to encourage shortest paths
- Wind penalty was set to -2 (between step and wall) to make wind zones
  mildly aversive without creating impassable barriers
- Goal reward of +100 was chosen to create strong gradient propagation

## Tools Used

| Tool | Purpose |
|------|---------|
| **Claude Code CLI** | Primary development tool; AI-assisted code generation, refactoring, and debugging |
| **UV** | Python package management; fast dependency resolution and virtual environment handling |
| **Pygame** | GUI framework for grid rendering, animations, and user interaction |
| **NumPy** | Q-table storage and array operations for the RL algorithm |
| **PyYAML** | Configuration file parsing |
| **Python 3.x** | Runtime language |

## Lessons Learned

1. **Structured prompting beats open-ended requests.** The PRD -> PLAN ->
   TODO pipeline ensured nothing was forgotten and every feature had a
   clear specification before coding began.

2. **Validation is essential.** Cross-referencing the TODO against the
   PRD caught gaps that would have been discovered much later in a
   traditional workflow.

3. **Iterative refinement works well for UI.** The editor and dashboard
   went through 3-4 rounds of improvement, each guided by specific
   feedback on what looked wrong or felt clunky.

4. **Configuration-first design pays off.** Having all parameters in
   YAML from the start made tuning hyperparameters and colors trivial --
   no code changes required for experimentation.

5. **Separation of concerns enables parallel development.** Because the
   SDK/core RL was decoupled from the GUI, both could be developed and
   tested independently.
