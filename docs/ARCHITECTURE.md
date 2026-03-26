# DroneRL -- Architecture Overview

## Layered Architecture

```
┌──────────────────────────────┐
│   External  (GUI  /  CLI)    │   main.py, gui.py, renderer.py,
│                              │   overlays.py, dashboard.py,
│                              │   editor.py, buttons.py
└──────────────┬───────────────┘
               │  calls
┌──────────────▼───────────────┐
│        SDK Layer (sdk.py)    │   Single entry-point for all
│                              │   business logic
└──────────────┬───────────────┘
               │  orchestrates
       ┌───────┴───────┐
       │               │
┌──────▼──────┐ ┌──────▼──────┐
│    Agent    │ │ Environment │   agent.py, environment.py
│  (Q-Learn) │ │  (Grid World)│
└──────┬──────┘ └──────┬──────┘
       └───────┬───────┘
               │
       ┌───────▼───────┐
       │    Trainer     │   trainer.py
       │ (Episode Loop) │
       └───────────────┘
               │
       ┌───────▼───────┐
       │  Config / Log  │   config_loader.py, logger.py
       └───────────────┘
```

## Layer Descriptions

### 1. External Layer (GUI / CLI)

The presentation tier. In GUI mode, Pygame renders the grid, overlays,
dashboard, and editor. The GUI contains **zero business logic** -- it
delegates all RL and environment operations to the SDK or GameLogic.

| Module | Responsibility |
|--------|---------------|
| `main.py` | Entry point; loads config and launches the GUI |
| `gui.py` | Main Pygame event loop, state machine for modes (edit/train/demo/pause) |
| `renderer.py` | Draws grid cells (empty, building, trap, goal, wind) and the drone sprite |
| `overlays.py` | Q-value heatmap, best-action arrows, start/goal labels, demo trail |
| `dashboard.py` | Right-side panel: metrics, reward graph, legend, convergence banner |
| `editor.py` | In-place grid editor for placing/removing obstacles |
| `buttons.py` | Context-aware button panel; buttons change based on application state |
| `game_logic.py` | Thin orchestrator for step-by-step training, convergence detection, and demo playback inside the GUI |

### 2. SDK Layer

`DroneRLSDK` is the **single programmatic entry-point**. It wires
Agent, Environment, and Trainer together and exposes a clean API:

- `train_step()` / `train_batch(n)` -- run episodes
- `get_q_table()` / `get_grid()` / `get_metrics()` -- read state
- `save_brain()` / `load_brain()` -- persist / restore Q-table
- `set_cell()` -- modify the grid
- `reset()` -- tear down and re-create all components

The SDK can be used headlessly (no Pygame) for scripting, testing, or
notebook integration.

### 3. Core RL Layer

| Module | Responsibility |
|--------|---------------|
| `agent.py` | Tabular Q-Learning agent: Q-table init, epsilon-greedy action selection, Bellman update, epsilon decay, save/load |
| `environment.py` | Grid world: cell types (Empty, Building, Trap, Goal, Wind), step dynamics, reward assignment, wind drift |
| `trainer.py` | Episode runner: resets env, loops agent-environment interaction, tracks metrics (reward history, goal rate, steps) |

### 4. Infrastructure Layer

| Module | Responsibility |
|--------|---------------|
| `config_loader.py` | Loads `config/config.yaml` via PyYAML; wraps raw dict in a dot-access `Config` object |
| `logger.py` | Creates a stdlib `logging.Logger` with console handler and configurable level |

## Data Flow

```
config.yaml
    │
    ▼
ConfigLoader  ──►  Config object
    │                   │
    │    ┌──────────────┼──────────────┐
    ▼    ▼              ▼              ▼
  Agent    Environment    Trainer     GUI / SDK
    │         │              │           │
    │         │  step()      │           │
    │◄────────┤◄─────────────┤           │
    │ update()│              │           │
    ├────────►│              │           │
    │         │              │  metrics  │
    │         │              ├──────────►│
    │         │              │           │  render
    │         │              │           ├────► Pygame window
```

1. **Config** is loaded once at startup and injected into every component.
2. **Trainer** (or GameLogic in GUI mode) runs the episode loop:
   Agent picks an action --> Environment returns (next_state, reward, done)
   --> Agent updates Q-table --> repeat.
3. **Metrics** (episode count, reward history, goal rate, epsilon) flow
   from Trainer/GameLogic to the Dashboard for real-time display.
4. **GUI** reads grid and Q-table to render heatmaps, arrows, and the
   drone position each frame.

## Module Dependency Diagram

```
main.py
  └─► config_loader
  └─► gui
        ├─► config_loader (Config)
        ├─► environment
        ├─► agent
        ├─► game_logic
        │     ├─► agent
        │     └─► environment
        ├─► renderer
        │     └─► environment (CellType)
        ├─► overlays
        │     └─► environment (CellType)
        ├─► dashboard
        │     └─► buttons
        └─► editor
              └─► environment (CellType)

sdk.py
  ├─► config_loader
  ├─► agent
  ├─► environment
  ├─► trainer
  │     ├─► agent
  │     └─► environment
  └─► logger
```

## Key Design Decisions

### SDK as Single Entry Point

All business logic is accessed through `DroneRLSDK`. This means:
- The GUI never directly manipulates Q-tables or runs training loops
  (it uses `GameLogic`, which mirrors SDK behavior for frame-by-frame control).
- Headless usage (scripts, tests, notebooks) is trivial -- import the SDK,
  call `train_batch()`, inspect results.

### GUI Has No Business Logic

The GUI layer is strictly presentation. `gui.py` translates user input
(keyboard, mouse) into actions, delegates to `GameLogic` for RL operations,
and calls renderers/overlays for display. Swapping Pygame for another
frontend would not require touching any RL code.

### All Parameters from YAML Config

Every tunable value -- grid dimensions, hyperparameters, reward values,
colors, window sizes, convergence criteria -- lives in
`config/config.yaml`. No magic numbers are scattered through the code.
The `Config` class provides dot-access (`config.agent.learning_rate`)
for ergonomic use throughout the codebase.

### OOP with Single Responsibility per Class

Each class has one clear job:

| Class | Single Responsibility |
|-------|----------------------|
| `Agent` | Maintain and update the Q-table |
| `Environment` | Manage grid state and step dynamics |
| `Trainer` | Orchestrate the training loop and collect metrics |
| `DroneRLSDK` | Wire components together, expose public API |
| `GameLogic` | Frame-level training/demo control for the GUI |
| `Renderer` | Draw cells and drone |
| `Overlays` | Draw heatmap, arrows, labels, trail |
| `Dashboard` | Draw metrics panel and reward graph |
| `Editor` | Handle grid editing interactions |
| `ButtonPanel` | Render context-sensitive buttons |
| `Config` | Provide dot-access to YAML config |

## File Listing

| File | Description |
|------|-------------|
| `main.py` | Application entry point; loads config and starts the GUI |
| `src/sdk.py` | High-level SDK that ties Agent, Environment, and Trainer together |
| `src/agent.py` | Tabular Q-Learning agent with epsilon-greedy exploration |
| `src/environment.py` | Grid world environment with cell types, rewards, and wind drift |
| `src/trainer.py` | Episode runner and metrics tracker for headless/SDK usage |
| `src/game_logic.py` | Frame-level training, convergence detection, and demo playback for the GUI |
| `src/gui.py` | Pygame main loop, event handling, and rendering orchestration |
| `src/renderer.py` | Grid cell and drone rendering with visual polish |
| `src/overlays.py` | Q-value heatmap, best-action arrows, labels, and demo trail |
| `src/dashboard.py` | Right-side metrics panel, reward graph, legend, and convergence banner |
| `src/editor.py` | In-place obstacle editor with type selection buttons |
| `src/buttons.py` | Context-aware button panel that adapts to application state |
| `src/config_loader.py` | YAML config loader with dot-access wrapper |
| `src/logger.py` | Centralized logging setup with configurable level |
| `config/config.yaml` | Single source of truth for all parameters and colors |
