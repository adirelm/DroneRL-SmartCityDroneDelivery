# DroneRL — Smart City Drone Delivery

An educational reinforcement learning application that visualizes a drone learning to navigate a smart city grid using **Tabular Q-Learning**. Built with Python and Pygame.

## What It Does

A drone agent learns the optimal path from a start position to a goal on a 12x12 grid, while avoiding:
- **Buildings** — impassable walls
- **Traps** — no-fly zones that end the episode with a penalty
- **Wind Zones** — stochastic areas that may push the drone off course

The GUI displays the learning process in real-time with:
- **Value Heatmap** — cells colored by their Q-values (blue=low, red=high)
- **Policy Arrows** — arrows showing the best action per cell
- **Dashboard** — episode count, reward, epsilon, goal rate, and a reward history graph
- **Level Editor** — interactively place/remove obstacles

## Installation

Requires **Python 3.11+** and **UV**.

```bash
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repo-url>
cd dronerl

# Install runtime + validation tooling (recommended for the assignment)
uv sync --dev
```

## Running

```bash
uv run main.py
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| `SPACE` | Pause / Resume training |
| `F` | Toggle fast mode (100 episodes/frame) |
| `H` | Toggle value heatmap |
| `A` | Toggle policy arrows |
| `E` | Toggle level editor |
| `T` | Cycle editor tool (Building/Trap/Wind) |
| `S` | Save Q-table (brain) |
| `L` | Load Q-table (brain) |
| `R` | Hard reset |

## Project Structure

```
├── src/
│   ├── agent.py            # Q-Learning agent (Bellman equation, epsilon-greedy)
│   ├── config_loader.py    # YAML configuration loader
│   ├── dashboard.py        # Dashboard panel rendering
│   ├── editor.py           # Level editor
│   ├── environment.py      # Smart city grid environment
│   ├── gui.py              # Main Pygame GUI orchestrator
│   ├── logger.py           # Centralized logging
│   ├── overlays.py         # Heatmap and policy arrow overlays
│   ├── renderer.py         # Grid renderer
│   ├── sdk.py              # Central SDK class
│   └── trainer.py          # Training orchestration
├── tests/                  # Unit tests (80 tests, 98% total coverage)
├── config/
│   └── config.yaml         # All parameters (grid, rewards, RL hyperparams)
├── data/                   # Saved Q-tables
├── docs/
│   ├── PRD.md              # Product Requirements Document
│   ├── PLAN.md             # Implementation plan
│   └── TODO.md             # Task list (1114 tasks, all completed)
├── main.py                 # Entry point
└── pyproject.toml          # UV project configuration
```

## Configuration

The main tunable parameters are in `config/config.yaml`. Includes:
- Grid size, start/goal positions
- Reward values (step, goal, trap, wind, wall collision)
- RL hyperparameters (learning rate, discount factor, epsilon settings)
- GUI settings (window size, colors, FPS, demo speed, fast mode batch size)
- Save/load path for persisted Q-tables

## Running Tests

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=src --cov-report=term-missing
```

## Tech Stack

- **Python 3.11+**
- **Pygame** — GUI rendering
- **NumPy** — Q-table and grid operations
- **PyYAML** — configuration loading
- **Pytest** — unit testing
- **UV** — package management and virtual environment

## How It Works

The agent uses **Q-Learning** (a model-free RL algorithm) to learn optimal navigation:

1. The agent starts with an empty Q-table (all zeros)
2. Each episode: the drone takes actions using **epsilon-greedy** exploration
3. After each action, Q-values are updated via the **Bellman equation**:
   ```
   Q(s,a) = Q(s,a) + α × [r + γ × max(Q(s',a')) - Q(s,a)]
   ```
4. Epsilon decays over time, shifting from exploration to exploitation
5. The agent converges to the optimal policy within ~3000 episodes
