# DroneRL -- Architecture Overview

This document is the **single navigation entry point for the project**. If
you're a human grader, an automated evaluator, or an AI agent reviewing
this codebase, start here — it indexes every claim made elsewhere and
points to the file that backs it up.

## Where to find what (navigation index)

| If you want to verify... | Go to |
|---|---|
| **The three RL algorithms work correctly** | [src/base_agent.py](../../src/base_agent.py), [src/agent.py](../../src/agent.py), [src/q_agent.py](../../src/q_agent.py), [src/double_q_agent.py](../../src/double_q_agent.py); tests in [tests/test_base_agent.py](../../tests/test_base_agent.py), [tests/test_q_agent.py](../../tests/test_q_agent.py), [tests/test_double_q_agent.py](../../tests/test_double_q_agent.py) |
| **The algorithm registry (one-line extension claim)** | [src/algorithms.py](../../src/algorithms.py) — `AlgorithmSpec` + `ALGORITHM_REGISTRY` is the single source of truth; [src/agent_factory.py](../../src/agent_factory.py) is a thin wrapper |
| **Experimental / research evidence** | Scripts: [analysis/multi_seed_robustness.py](../../analysis/multi_seed_robustness.py), [analysis/alpha_decay_sweep.py](../../analysis/alpha_decay_sweep.py); charts: [data/analysis/multi_seed_robustness.png](../../data/analysis/multi_seed_robustness.png), [data/analysis/alpha_decay_sweep.png](../../data/analysis/alpha_decay_sweep.png); write-up: [docs/assignment-2/EXPERIMENTS.md](../assignment-2/EXPERIMENTS.md) |
| **Cost / resource analysis** | Profiler: [analysis/cost_profile.py](../../analysis/cost_profile.py); raw output: [data/analysis/cost_profile.json](../../data/analysis/cost_profile.json); write-up: [docs/assignment-2/COST_ANALYSIS.md](../assignment-2/COST_ANALYSIS.md) (includes a development-cost section on AI-assisted workflow) |
| **The 2-scenario comparison required by the assignment** | [scripts/generate_comparison_charts.py](../../scripts/generate_comparison_charts.py); charts in [data/comparison/](../../data/comparison/) |
| **Quality automation (CI, pre-commit, Dependabot)** | [.github/workflows/ci.yml](../../.github/workflows/ci.yml), [.pre-commit-config.yaml](../../.pre-commit-config.yaml), [.github/dependabot.yml](../../.github/dependabot.yml), [scripts/check_file_sizes.sh](../../scripts/check_file_sizes.sh) |
| **Project planning trail (PRD → PLAN → TODO)** | [docs/assignment-1/](../assignment-1/) (PRD/PLAN/TODO), [docs/assignment-2/PRD_*.md](../assignment-2/), [docs/assignment-2/PLAN_*.md](../assignment-2/), [docs/assignment-2/TODO_*.md](../assignment-2/) |
| **AI-assisted development workflow** | [docs/shared/PROMPTS.md](PROMPTS.md) — original development + post-feedback iteration log |
| **Coding standards (the rules this project enforces)** | [CLAUDE.md](../../CLAUDE.md) — 150-line file limit, ≥85% coverage, no magic numbers, ruff zero violations, UV-only |
| **How to run / install** | [README.md](../../README.md) §Installation, §Running |
| **License** | [LICENSE](../../LICENSE) — MIT |

### Reproducing the artifacts

```bash
uv sync --dev                                          # install dependencies
uv run pytest tests/                                   # 284 tests, 97.59% coverage
uv run ruff check src/ tests/ analysis/ scripts/ main.py
uv run python scripts/generate_comparison_charts.py    # regenerate scenario PNGs
uv run python -m analysis.multi_seed_robustness        # 5 seeds × 1500 ep × 3 algos
uv run python -m analysis.alpha_decay_sweep            # 6 decays × 3 seeds × 2 algos
uv run python -m analysis.cost_profile                 # measured timings + Q-table memory
uv run main.py                                         # launch the Pygame GUI
```

---

## Layered Architecture

```
┌─────────────────────────────────────────────┐
│   External (GUI / CLI)                      │   main.py, gui.py,
│                                             │   renderer.py, overlays.py,
│                                             │   dashboard.py, editor.py,
│                                             │   buttons.py, sliders.py
└────────────────────┬────────────────────────┘
                     │ calls
┌────────────────────▼────────────────────────┐
│              SDK Layer (sdk.py)             │   Single entry-point for
│                                             │   all business logic
└────────────────────┬────────────────────────┘
                     │ orchestrates
      ┌──────────────┼──────────────┬──────────────────┐
      │              │              │                  │
┌─────▼───────┐ ┌────▼────────┐ ┌───▼──────────┐ ┌─────▼────────┐
│   Agents    │ │ Environment │ │   Trainer    │ │  Comparison  │
│  (Strategy) │ │ + Hazards   │ │ (Episode Loop)│ │   (plots)   │
└─────┬───────┘ └────┬────────┘ └───┬──────────┘ └─────┬────────┘
      │              │              │                  │
      └──────────────┴───────┬──────┴──────────────────┘
                             │
                     ┌───────▼───────┐
                     │ Config / Log  │   config_loader.py, logger.py
                     └───────────────┘
```

## Layer Descriptions

### 1. External Layer (GUI / CLI)

The presentation tier. In GUI mode, Pygame renders the grid, overlays,
dashboard, editor, and sliders. The GUI contains **zero business logic** --
it delegates all RL and environment operations to the SDK or GameLogic.

| Module | Responsibility |
|--------|---------------|
| `main.py` | Entry point; loads config and launches the GUI |
| `src/gui.py` | Main Pygame event loop, state machine for modes (edit/train/demo/pause), algorithm switching (keys 1/2/3) |
| `src/renderer.py` | Draws grid cells (empty, building, trap, pit, goal, wind) and the drone sprite |
| `src/overlays.py` | Q-value heatmap, best-action arrows, start/goal labels, demo trail |
| `src/dashboard.py` | Right-side panel: metrics, reward graph, legend, convergence banner |
| `src/editor.py` | In-place grid editor for placing/removing obstacles |
| `src/buttons.py` | Context-aware button panel; buttons change based on application state |
| `src/sliders.py` | Pygame slider widgets for `noise_level`, `hazard_density`, and `difficulty` |
| `src/actions.py` | Action-enum and delta-vector helpers shared by agents and env |
| `src/game_logic.py` | Thin orchestrator for step-by-step training, convergence detection, demo playback |

### 2. SDK Layer

`DroneRLSDK` (`src/sdk.py`) is the **single programmatic entry-point**. It
wires Agent (via the factory), Environment, Trainer, HazardGenerator, and
ComparisonStore together and exposes a clean API:

- `train_step()` / `train_batch(n)` -- run episodes
- `switch_algorithm(name)` -- swap between Bellman / Q-Learning / Double Q at runtime
- `regenerate_hazards()` -- re-run `HazardGenerator` using current slider values
- `run_comparison()` -- train all three algorithms and emit a matplotlib PNG
- `get_q_table()` / `get_grid()` / `get_metrics()` -- read state
- `save_brain()` / `load_brain()` -- persist / restore Q-table(s)
- `set_cell()` / `reset()` -- edit grid / tear-down and rebuild

The SDK can be used headlessly (no Pygame) for scripting, testing, or
notebook integration.

### 3. Core RL Layer (Strategy Pattern)

| Module | Responsibility |
|--------|---------------|
| `src/base_agent.py` | Abstract `BaseAgent`: Q-table init, epsilon-greedy action selection, epsilon decay, save/load; subclasses must override `update()` |
| `src/agent.py` | `BellmanAgent(BaseAgent)` -- Assignment 1 baseline; constant learning rate |
| `src/q_agent.py` | `QLearningAgent(BaseAgent)` -- Assignment 2; decaying alpha per episode |
| `src/double_q_agent.py` | `DoubleQAgent(BaseAgent)` -- Assignment 2; two Q-tables (QA + QB), cross-table evaluation (Hasselt 2010); `q_table` property returns `QA + QB` for GUI compatibility |
| `src/algorithms.py` | **Algorithm registry** — single source of truth: `AlgorithmSpec` dataclass + `ALGORITHM_REGISTRY` tuple. Every consumer (factory, GUI, comparison, charts, analysis, parametrised tests) reads `ALGORITHMS` / `ALGORITHM_LABELS` / `ALGORITHM_COLORS` / `AGENT_CLASSES` from here. Adding an algorithm = one new agent file + one line in the registry |
| `src/agent_factory.py` | `create_agent(config)` -- thin validating wrapper over `AGENT_CLASSES`; raises `ValueError` listing valid names on unknown input |
| `src/environment.py` | Grid world: `CellType` enum including `PIT` (−75 terminal hazard), step dynamics, wind drift, reward assignment, `is_protected_cell()` and `editor_cells` (frozenset property) + `restore_editor_cells(iterable)` public APIs to preserve user edits when hazards regenerate |
| `src/hazard_generator.py` | Randomly populates the grid with hazards (building / trap / pit / wind) driven by the three sliders and per-hazard ratios in config |
| `src/trainer.py` | Episode runner: resets env, loops agent-environment interaction, tracks metrics (reward history, goal rate, steps) |
| `src/comparison.py` | `ComparisonStore` collects per-algorithm reward histories; matplotlib generator writes PNG charts for the two required scenarios |

### 4. Infrastructure Layer

| Module | Responsibility |
|--------|---------------|
| `src/config_loader.py` | Loads `config/config.yaml` via PyYAML; wraps raw dict in a dot-access `Config` object |
| `src/logger.py` | Creates a stdlib `logging.Logger` with console handler and configurable level |

### 5. Research & Analysis Layer

Headless, reproducible experiments that exercise the SDK from the outside.
Each script is independently runnable via `uv run python -m analysis.<name>`.

| Module | Responsibility |
|--------|---------------|
| `analysis/_runner.py` | Shared training helpers (`train_run`, `with_overrides`, `last_window_stats`) so every experiment uses identical config plumbing |
| `analysis/multi_seed_robustness.py` | 5 seeds × 1500 ep × 3 algos; emits a 95%-CI band chart. Reveals that Double-Q is highly seed-dependent at short training budgets |
| `analysis/alpha_decay_sweep.py` | 6 decays × 3 seeds × 2 algos; shows Q-Learning is essentially flat across the entire `alpha_decay` grid at this difficulty |
| `analysis/cost_profile.py` | Measures wall time, peak heap, and Q-table bytes per algorithm; emits `data/analysis/cost_profile.json` for machine consumption |
| `data/analysis/*.png` / `.json` | Chart and JSON artifacts produced by the scripts above; checked into the repo so the claims are auditable without rerunning |
| `data/comparison/*.png` | The required two-scenario comparison charts produced by `scripts/generate_comparison_charts.py` |
| `docs/assignment-2/EXPERIMENTS.md` | Hypothesis-driven write-up of the analysis runs, including the two findings that contradicted the original README narrative |
| `docs/assignment-2/COST_ANALYSIS.md` | Measured runtime costs + a section on AI-assisted *development* cost (token usage, subscription outlay, rework tax, why the 150-line + 85% coverage rules are verification-cost optimizations) |

### 6. Tooling and Automation

Quality is enforced by automation, not manual review. Every gate fails
the build (locally and in CI) when violated.

| Surface | What it does |
|---------|--------------|
| `.github/workflows/ci.yml` | GitHub Actions CI on Python 3.11/3.12/3.13 matrix: ruff, pytest with `--cov-fail-under=85`, file-size limit, on every push/PR to `main`/`assignment-1`/`assignment-2` |
| `.pre-commit-config.yaml` | Local pre-commit hooks: trailing-whitespace, end-of-file, YAML/TOML/large-file checks, ruff `--fix`, file-size limit; pytest on `pre-push` stage |
| `.github/dependabot.yml` | Weekly dependency updates for GitHub Actions and pip, grouped by family |
| `scripts/check_file_sizes.sh` | Shared script enforcing the 150-line `.py` limit, used by both CI and pre-commit |
| `pyproject.toml` `[tool.pytest.ini_options]` | `addopts = ["--cov=src", "--cov-fail-under=85", "--strict-markers", "--strict-config", "-ra"]` — the coverage gate is on every plain `uv run pytest`, not only in CI |

## Data Flow

```
config.yaml
    │
    ▼
ConfigLoader  ──►  Config object
    │                   │
    │    ┌──────────────┼──────────────┬─────────────────┐
    ▼    ▼              ▼              ▼                 ▼
  AgentFactory    Environment     HazardGenerator    GUI / SDK
    │ create()      │              │                     │
    ▼               │              │                     │
  BaseAgent        step()          populate()            │
  (Bellman /        │              │                     │
   Q-Learning /     │              │                     │
   Double Q)        │              │                     │
    │               │              │                     │
    │◄──────────────┤              │                     │
    │ update(...)   │              │                     │
    ├──────────────►│              │                     │
    │               │              │                     │
    │               │              │     Trainer metrics │
    │               │              ├────────────────────►│
    │               │              │                     │  render
    │               │              │                     ├────► Pygame
```

1. **Config** is loaded once at startup and injected into every component.
2. **AgentFactory** builds the concrete agent requested by `algorithm.name`.
3. **Trainer** (or GameLogic in GUI mode) runs the episode loop:
   Agent picks an action --> Environment returns (next_state, reward, done)
   --> Agent updates its Q-table(s) --> repeat.
4. **Metrics** flow from Trainer/GameLogic to the Dashboard for real-time
   display; `ComparisonStore` captures them for PNG generation.
5. **GUI** reads the grid and `agent.q_table` each frame to render heatmap,
   arrows, and the drone position.

## Module Dependency Diagram

```
main.py
  └─► config_loader
  └─► gui
        ├─► sdk
        ├─► config_loader (Config)
        ├─► renderer / overlays / dashboard / buttons / editor / sliders
        ├─► game_logic
        │     ├─► agent_factory ─► {agent, q_agent, double_q_agent} ─► base_agent
        │     ├─► environment (CellType, PIT)
        │     └─► hazard_generator
        └─► actions

sdk.py
  ├─► config_loader
  ├─► algorithms        (ALGORITHMS, ALGORITHM_REGISTRY, AGENT_CLASSES)
  ├─► agent_factory     (validating wrapper over algorithms.AGENT_CLASSES)
  │     ├─► agent         (BellmanAgent)
  │     ├─► q_agent       (QLearningAgent)
  │     └─► double_q_agent(DoubleQAgent)
  │         (all inherit from base_agent.BaseAgent)
  ├─► environment
  ├─► hazard_generator
  ├─► trainer
  ├─► comparison        (also imports ALGORITHM_LABELS / ALGORITHM_COLORS)
  └─► logger
```

## Key Design Decisions

### SDK as Single Entry Point

All business logic is accessed through `DroneRLSDK`. The GUI never directly
manipulates Q-tables or runs training loops (it uses `GameLogic`, which
mirrors SDK behaviour for frame-by-frame control). Headless usage (scripts,
tests, notebooks) is trivial.

### Strategy Pattern for Algorithms + Centralised Registry

The three RL algorithms share a single `BaseAgent` interface and differ
only in their `update()` method. `src/algorithms.py` holds an
`AlgorithmSpec`-based registry that is the *single* source of truth for
the algorithm enumeration; `agent_factory.create_agent()` is a thin
wrapper over the registry's `AGENT_CLASSES` map. `DroneRLSDK` uses it
to swap algorithms at runtime without reconstructing the environment.

**Why a registry, not a hardcoded tuple in 13 places**: the original
design duplicated the `("bellman", "q_learning", "double_q")` tuple
across nine files (factory, comparison runner, chart code, GUI key
bindings, analysis runner, parametrised tests, etc.). Adding a fourth
algorithm meant updating all of them. The registry collapses that to a
one-line change. See [docs/shared/PROMPTS.md → Extensibility](PROMPTS.md)
for the post-feedback refactor that introduced it.

### GUI Has No Business Logic

The GUI layer is strictly presentation. Swapping Pygame for another
frontend would not require touching any RL code.

### Configuration-Driven Behaviour

All runtime parameters -- grid dimensions, hyperparameters, reward values,
colours, dynamic-board (noise / density / difficulty), `algorithm.name`,
per-algorithm sections (`q_learning`, `double_q`), and comparison settings
-- live in `config/config.yaml`.

### OOP with Single Responsibility per Class

Each class has one clear job:

| Class | Single Responsibility |
|-------|----------------------|
| `BaseAgent` | Shared RL state (Q-table, epsilon, save/load) + abstract `update()` |
| `BellmanAgent` | Constant-α Bellman update |
| `QLearningAgent` | Decaying-α Q-Learning update |
| `DoubleQAgent` | Two Q-tables with cross-table evaluation |
| `Environment` | Grid state (incl. `PIT`), step dynamics, editor-cell tracking |
| `HazardGenerator` | Random hazard placement driven by sliders |
| `Trainer` | Orchestrate training loop and collect metrics |
| `ComparisonStore` | Aggregate reward histories and emit matplotlib chart |
| `DroneRLSDK` | Wire components, expose public API, algorithm switching |
| `GameLogic` | Frame-level training/demo control for the GUI |
| `Slider` | Single-value draggable Pygame widget |
| `Renderer` / `Overlays` / `Dashboard` / `Editor` / `ButtonPanel` | Pygame drawing only |
| `Config` | Dot-access to YAML config |

## File Listing

### Source

| File | Description |
|------|-------------|
| `main.py` | Application entry point; loads config and starts the GUI |
| `src/sdk.py` | High-level SDK: agent factory, environment, trainer, comparison, hazards |
| `src/base_agent.py` | Abstract RL agent base class (Strategy pattern root) |
| `src/agent.py` | `BellmanAgent` -- constant-α baseline (Assignment 1) |
| `src/q_agent.py` | `QLearningAgent` -- decaying-α tabular Q-Learning |
| `src/double_q_agent.py` | `DoubleQAgent` -- dual-table Double Q-Learning (Hasselt 2010) |
| `src/algorithms.py` | **Algorithm registry** (`AlgorithmSpec`, `ALGORITHM_REGISTRY`, derived `ALGORITHMS` / `ALGORITHM_LABELS` / `ALGORITHM_COLORS` / `AGENT_CLASSES`) |
| `src/agent_factory.py` | `create_agent(config)` -- thin validating wrapper over `algorithms.AGENT_CLASSES` |
| `src/environment.py` | Grid world + `CellType` (incl. `PIT`) + public `editor_cells` / `restore_editor_cells` / `is_protected_cell` API |
| `src/hazard_generator.py` | Slider-driven random hazard placement |
| `src/sliders.py` | Pygame slider widgets (noise / density / difficulty) |
| `src/trainer.py` | Episode runner and metrics tracker for headless/SDK usage |
| `src/comparison.py` | `ComparisonStore` + matplotlib chart generator (re-exports `ALGORITHMS`/`LABELS`/`COLORS` from registry) |
| `src/game_logic.py` | Frame-level training, convergence detection, and demo playback |
| `src/gui.py` | Pygame main loop, event handling, algorithm switching |
| `src/renderer.py` | Grid cell and drone rendering |
| `src/overlays.py` | Q-value heatmap, arrows, labels, demo trail |
| `src/dashboard.py` | Right-side metrics panel, reward graph, legend, banner |
| `src/editor.py` | In-place obstacle editor with type selection |
| `src/buttons.py` | Context-aware button panel |
| `src/actions.py` | Action enum and delta-vector helpers |
| `src/config_loader.py` | YAML config loader with dot-access wrapper |
| `src/logger.py` | Centralised logging setup |
| `config/config.yaml` | Single source of truth for all parameters and colours |

### Research, scripts, and analysis

| File | Description |
|------|-------------|
| `analysis/_runner.py` | Shared training helpers used by every analysis script |
| `analysis/multi_seed_robustness.py` | Multi-seed CI experiment |
| `analysis/alpha_decay_sweep.py` | Hyperparameter sensitivity sweep |
| `analysis/cost_profile.py` | Wall-time / memory / Q-table profiler |
| `scripts/generate_comparison_charts.py` | Required two-scenario comparison runner |
| `scripts/capture_assignment2_screenshots.py` | Headless GUI screenshot capture |
| `scripts/check_file_sizes.sh` | 150-line file-size enforcement (CI + pre-commit) |
| `data/comparison/*.png` | Required Scenario 1 / Scenario 2 charts |
| `data/analysis/*.png` / `*.json` | Multi-seed, sweep, and cost-profile artifacts |

### Documentation

| File | Description |
|------|-------------|
| `README.md` | Public-facing overview, run/install, comparison results, conclusions |
| `CLAUDE.md` | Coding standards (file-size, TDD, OOP, no magic numbers, ruff, UV) |
| `LICENSE` | MIT |
| `docs/shared/ARCHITECTURE.md` | This file — navigation entry point |
| `docs/shared/PROMPTS.md` | Original prompts log + post-feedback iteration log |
| `docs/assignment-1/{PRD,PLAN,TODO}.md` | Assignment 1 planning trail |
| `docs/assignment-2/PRD_*.md` | Assignment 2 PRDs (q_learning, double_q_learning, dynamic_board) |
| `docs/assignment-2/PLAN_*.md` | Assignment 2 implementation plans (matching PRDs) |
| `docs/assignment-2/TODO_*.md` | Assignment 2 task lists (~2400 tasks total, all checked) |
| `docs/assignment-2/EXPERIMENTS.md` | Research log: hypotheses, methods, results, limitations |
| `docs/assignment-2/COST_ANALYSIS.md` | Runtime + AI-development cost analysis |

### CI / quality

| File | Description |
|------|-------------|
| `.github/workflows/ci.yml` | Lint + test + coverage + file-size on Python 3.11/3.12/3.13 matrix |
| `.github/dependabot.yml` | Weekly dependency updates |
| `.pre-commit-config.yaml` | Local commit/push hooks |
| `pyproject.toml` | Package metadata, ruff config, pytest+coverage gate, dev dependencies |
