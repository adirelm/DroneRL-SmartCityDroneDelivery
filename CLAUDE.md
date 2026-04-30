# CLAUDE.md — Global Coding Standards for DroneRL

## Project Context

DroneRL is a reinforcement learning project comparing three algorithms:
Bellman (constant LR), Q-Learning (decaying alpha), and Double Q-Learning (dual tables).
Built with Pygame GUI. Assignment for Bar-Ilan University Vibe Coding Workshop.

## Human ↔ AI Responsibility Contract (§1.4)

§1.4 of the submission guidelines frames the developer as **architect**,
the AI as **implementer**. This file is the contract that boundary makes
explicit. Each row says **who decides** before any code is generated.

| Concern | Human-decided (non-delegable) | AI-delegated |
|---|---|---|
| Requirements (PRD, scope, success criteria, KPIs) | ✅ | — |
| Architecture (ADRs, layer boundaries, public API shape) | ✅ | — |
| Test acceptance criteria + the assertions that must hold | ✅ | — |
| Final code-review sign-off + commit message intent | ✅ | — |
| Self-score / grade claim against the rubric | ✅ | — |
| Cost-budget envelope (what we're willing to spend) | ✅ | — |
| Code generation against an approved spec | — | ✅ |
| Refactoring within an existing public API | — | ✅ |
| Test scaffolding + boilerplate from a written spec | — | ✅ |
| Docstring drafts (human edits before commit) | — | ✅ |
| Routine doc maintenance (link fixes, freshness sweeps) | — | ✅ |
| Lint / format auto-fixes | — | ✅ |

**Operating rule.** If any AI-generated change would alter a human-decided
column above (e.g. add a new public SDK method, change a test assertion,
weaken a quality gate, choose between two architectures), the human must
sign off explicitly *before* the code lands — typically by approving the
PRD/PLAN edit first, *then* letting the AI execute against it.

This contract is also evidenced in `docs/shared/PROMPTS.md` (the literal
prompts used) and in the per-section commit messages that name the §
of the submission guidelines being addressed.

## Hard Constraints (Apply to ALL Files)

### 1. File Size Limit — 150 Lines Maximum
Every Python file (.py) must not exceed 150 lines of code.
If a file approaches 150 lines, split into separate modules.

### 2. Test-Driven Development (TDD)
Write tests BEFORE implementation. RED → GREEN → REFACTOR.
All new code must achieve 85%+ test coverage.
Run: `uv run pytest tests/ --cov=src --cov-report=term-missing`

### 3. Object-Oriented Programming (OOP)
Use inheritance (BaseAgent → BellmanAgent / QLearningAgent / DoubleQAgent).
No code duplication — shared logic in base classes.
SDK is the single entry point for all business logic.

### 4. No Hardcoded Values
ALL **algorithm-relevant** parameters, colors, rewards, and thresholds
live in `config/config.yaml` and are accessed via the config loader.
This covers: RL hyperparameters, reward magnitudes, board dimensions,
hazard ratios, training durations, seeds, and the colour palette.

Local UI-styling literals (button pixel dimensions, dashboard line
offsets, matplotlib `alpha` / `fontsize` / `dpi` values) stay in their
rendering modules — they are part of the visual design, not tunable
parameters. The test for "should this be in config" is: *"would I
expect a grader, contributor, or future-me to ever want to change this
without editing source?"* If yes → config. If no → keep it local.

### 5. No Code Duplication (DRY)
Extract common logic into shared methods/classes.
If a pattern appears twice, create a utility or base class method.

### 6. Linting — Zero Ruff Violations
Run: `uv run ruff check src/ tests/ main.py`
Must produce zero errors before every commit.

### 7. Package Manager — UV Only
Use `uv` exclusively. No pip, no conda.
Run app: `uv run main.py`
Install deps: `uv sync --dev`

## Algorithm Requirements

### Bellman Agent (Assignment 1)
- Constant learning rate (lr = 0.1)
- Single Q-table
- Baseline for comparison

### Q-Learning Agent (Assignment 2)
- **Alpha MUST decay over time** — non-negotiable
- `alpha = max(alpha_end, alpha * alpha_decay)` per episode
- Constant alpha causes divergence in noisy environments

### Double Q-Learning Agent (Assignment 2)
- Two Q-tables: QA and QB
- Cross-table evaluation: argmax from one, value from other
- `q_table` property returns QA + QB for GUI compatibility
- Decaying alpha (same as Q-Learning)

## Comparison Requirements

Generate TWO comparison scenarios:
1. Medium difficulty: Bellman struggles most, Q-Learning and Double Q converge.
2. High difficulty: All three eventually solve; Double Q is the most consistent.

Save charts as PNG in `results/comparison/`.

## Version Control

- Same repository as Assignment 1
- Branch: `assignment-2`
- Version: 1.1.1

## Config Structure

All config in `config/config.yaml`:
- environment, rewards, agent, training, wind
- dynamic_board (density, noise, difficulty)
- algorithm (name selection)
- q_learning (alpha_start, alpha_end, alpha_decay)
- double_q (alpha_start, alpha_end, alpha_decay)
- comparison (max_episodes, output_dir)
- gui, colors, logging, paths

## Pre-Submission Review Methodology

Before any submission (or whenever the user asks "is this ready?"),
walk the methodology in `instructions/review_methodology/` (gitignored,
local only). It is a 9-phase iterative pre-submission audit with
explicit self-critique prompts at every step.

- Start with `instructions/review_methodology/00_README.md`.
- The most important file in the framework is
  `instructions/review_methodology/10_self_critique_prompts.md` —
  read it before claiming any phase is done.
- Per-assignment progress trackers live in
  `instructions/<assignment>/final_review_progress.md`.
- Lecturer feedback (verbatim) is in
  `instructions/<assignment>/lecturer_feedback.md`.

The methodology is reusable across assignments. Update the phase
files only when the *process* improves, not when the assignment
content changes.
