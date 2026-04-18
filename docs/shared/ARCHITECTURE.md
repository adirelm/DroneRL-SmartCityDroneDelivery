# DroneRL -- Architecture Overview

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
| `src/agent_factory.py` | `create_agent(config)` -- Strategy-pattern dispatch keyed on `config.algorithm.name` ("bellman" / "q_learning" / "double_q") |
| `src/environment.py` | Grid world: `CellType` enum including `PIT` (−75 terminal hazard), step dynamics, wind drift, reward assignment, `_editor_cells` tracking to preserve user edits when hazards regenerate |
| `src/hazard_generator.py` | Randomly populates the grid with hazards (building / trap / pit / wind) driven by the three sliders and per-hazard ratios in config |
| `src/trainer.py` | Episode runner: resets env, loops agent-environment interaction, tracks metrics (reward history, goal rate, steps) |
| `src/comparison.py` | `ComparisonStore` collects per-algorithm reward histories; matplotlib generator writes PNG charts for the two required scenarios |

### 4. Infrastructure Layer

| Module | Responsibility |
|--------|---------------|
| `src/config_loader.py` | Loads `config/config.yaml` via PyYAML; wraps raw dict in a dot-access `Config` object |
| `src/logger.py` | Creates a stdlib `logging.Logger` with console handler and configurable level |

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
  ├─► agent_factory
  │     ├─► agent         (BellmanAgent)
  │     ├─► q_agent       (QLearningAgent)
  │     └─► double_q_agent(DoubleQAgent)
  │         (all inherit from base_agent.BaseAgent)
  ├─► environment
  ├─► hazard_generator
  ├─► trainer
  ├─► comparison
  └─► logger
```

## Key Design Decisions

### SDK as Single Entry Point

All business logic is accessed through `DroneRLSDK`. The GUI never directly
manipulates Q-tables or runs training loops (it uses `GameLogic`, which
mirrors SDK behaviour for frame-by-frame control). Headless usage (scripts,
tests, notebooks) is trivial.

### Strategy Pattern for Algorithms

The three RL algorithms share a single `BaseAgent` interface and differ
only in their `update()` method. `agent_factory.create_agent()` is the
only place that knows the full algorithm list, and `DroneRLSDK` uses it
to swap algorithms at runtime without reconstructing the environment.

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

| File | Description |
|------|-------------|
| `main.py` | Application entry point; loads config and starts the GUI |
| `src/sdk.py` | High-level SDK: agent factory, environment, trainer, comparison, hazards |
| `src/base_agent.py` | Abstract RL agent base class (Strategy pattern root) |
| `src/agent.py` | `BellmanAgent` -- constant-α baseline (Assignment 1) |
| `src/q_agent.py` | `QLearningAgent` -- decaying-α tabular Q-Learning |
| `src/double_q_agent.py` | `DoubleQAgent` -- dual-table Double Q-Learning (Hasselt 2010) |
| `src/agent_factory.py` | `create_agent(config)` Strategy-pattern dispatch |
| `src/environment.py` | Grid world + `CellType` (incl. `PIT`) + `_editor_cells` tracking |
| `src/hazard_generator.py` | Slider-driven random hazard placement |
| `src/sliders.py` | Pygame slider widgets (noise / density / difficulty) |
| `src/trainer.py` | Episode runner and metrics tracker for headless/SDK usage |
| `src/comparison.py` | `ComparisonStore` + matplotlib chart generator |
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
