# Implementation Plan

## DroneRL — Smart City Drone Delivery

---

## Architecture Strategy

The project follows a **layered architecture** with clear separation of concerns:

```
Configuration (YAML)
       ↓
   SDK Layer (orchestration)
       ↓
  ┌────┴────┐
  │         │
Agent    Environment
  │         │
  └────┬────┘
       ↓
  GUI / Renderer (Pygame)
       ↓
  ┌────┴────┐
  │    │    │
Grid  Dashboard  Editor
```

---

## Development Approach: TDD

1. Write tests first for each module.
2. Implement the module to pass tests.
3. Integrate and verify end-to-end.

---

## Phase 1: Foundation

### 1.1 Project Setup
- Initialize UV project with `pyproject.toml`.
- Create directory structure: `src/`, `tests/`, `config/`, `assets/`, `data/`, `docs/`.
- Create `.gitignore`.

### 1.2 Configuration System
- Create `config/config.yaml` with all parameters.
- Implement `src/dronerl/config_loader.py` to load YAML config.
- Parameters: grid size, rewards, RL hyperparameters, GUI settings, colors.

### 1.3 Logging
- Implement `src/dronerl/logger.py` with centralized logging.
- Console + optional file output.

---

## Phase 2: Core RL Engine

### 2.1 Environment (`src/dronerl/environment.py`)
- Grid class with configurable dimensions.
- Cell types: EMPTY, BUILDING, TRAP, GOAL, WIND.
- Step function: takes action, returns next_state, reward, done.
- Wind zone stochastic mechanics.
- Reset function.
- Methods to add/remove obstacles.

### 2.2 Agent (`src/dronerl/agent.py`)
- Q-Table: 3D NumPy array `[rows, cols, 4]`.
- `choose_action(state)`: Epsilon-Greedy selection.
- `update(state, action, reward, next_state)`: Bellman equation.
- Epsilon decay logic.
- Save/load Q-table to/from file.

### 2.3 Training Loop (`src/dronerl/trainer.py`)
- Episode loop: reset env → agent acts → update Q → repeat.
- Track metrics: rewards, steps, goal rate.
- Support headless (fast) and GUI modes.

---

## Phase 3: GUI & Visualization

### 3.1 Grid Renderer (`src/dronerl/renderer.py`)
- Draw grid cells with type-based colors.
- Draw drone sprite/icon.
- Draw goal indicator.

### 3.2 Overlays (`src/dronerl/overlays.py`)
- Value Heatmap: color cells by `max(Q(s,a))`.
- Policy Arrows: draw arrows for `argmax(Q(s,a))`.
- Toggle on/off.

### 3.3 Dashboard (`src/dronerl/dashboard.py`)
- Right-side panel.
- Display: episode, reward, epsilon, steps, goal rate.
- Reward history line graph.
- Legend for cell types.

### 3.4 Level Editor (`src/dronerl/editor.py`)
- Toggle edit mode.
- Click to place/remove: buildings, traps, wind zones.
- Cell type selector.

### 3.5 Main GUI (`src/dronerl/gui.py`)
- Pygame window initialization.
- Main event loop.
- Keyboard shortcut handling.
- Status bar rendering.
- Coordinate all sub-renderers.

---

## Phase 4: SDK Layer

### 4.1 SDK Class (`src/dronerl/sdk.py`)
- Central orchestrator.
- Exposes: `train_step()`, `reset()`, `get_state()`, `get_q_table()`, `save_brain()`, `load_brain()`.
- Bridges agent, environment, and GUI.
- Decouples business logic from presentation.

---

## Phase 5: Integration & Entry Point

### 5.1 Main (`main.py`)
- Parse optional CLI arguments.
- Load config.
- Initialize SDK.
- Run GUI or headless mode.

---

## Phase 6: Testing

### 6.1 Unit Tests
- `test_agent.py`: Q-value updates, epsilon decay, action selection.
- `test_environment.py`: Step function, rewards, wind zones, boundaries.
- `test_config_loader.py`: YAML loading, defaults.
- `test_sdk.py`: SDK orchestration.
- `test_trainer.py`: Episode logic, metrics tracking.

### 6.2 Coverage Target
- 85%+ overall coverage.
- Run with: `uv run pytest --cov=src --cov-report=html`

---

## Phase 7: Documentation

- `README.md`: Overview, installation, usage, screenshots.
- Docstrings in all public functions.
- `docs/ARCHITECTURE.md`: Architecture overview.

---

## File Size Constraint

Every `.py` file must stay under **150 lines**. If a module grows beyond this, split it into sub-modules.
