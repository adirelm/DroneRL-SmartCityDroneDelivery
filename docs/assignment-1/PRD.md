# Product Requirements Document (PRD)

## DroneRL — Smart City Drone Delivery

---

## 1. Project Overview & Background

DroneRL is an educational reinforcement learning (RL) game built in Python using Pygame. The goal is to teach users the fundamentals of **Tabular Q-Learning** by visualizing the learning process of an autonomous drone navigating a smart city grid.

The drone must deliver packages from a **start point** to a **destination** while:
- Avoiding buildings (impassable walls)
- Avoiding traps/no-fly zones
- Navigating stochastic wind zones
- Optimizing its path through reward-based learning

The project demonstrates core RL concepts such as the **Bellman equation**, **Epsilon-Greedy exploration**, **reward shaping**, and **backwards ripple effect of value propagation**.

### 1.1 Target Audience

Primary: **Bar-Ilan University RL students** in the Vibe Coding Workshop and adjacent ML courses. Secondary: educators preparing tabular-RL teaching materials, and self-learners coming to RL from a software-engineering background who want a runnable reference implementation rather than just slides or papers.

### 1.2 Market Analysis

The classroom-RL space is dominated by three patterns, each with a gap DroneRL is sized to fill:

- **OpenAI Gym / Gymnasium environments** (CartPole, FrozenLake, …) are the textbook default. They give a clean Python API but no visual training experience — the policy is invisible until you write your own renderer. DroneRL's GUI shows the Q-table heatmap and policy arrows updating live, which is exactly the part students need to *see*.
- **Jupyter notebook tutorials** (Sutton & Barto, Hasselt's Double-Q paper reproductions). Excellent theory, but the code is fragmented across cells, has no tests, and degrades the moment a student tries to extend it. DroneRL ships a full project with 97 % test coverage, a build-system, and a clean extension recipe (one-line algorithm registry).
- **Commercial RL libraries** (Stable-Baselines3, RLlib). Production-grade but optimised for deep RL and large compute — overkill for a tabular-Q teaching tool, and their abstractions hide the very Bellman / α-decay / dual-table mechanics the assignment is asking the student to internalise.

DroneRL's differentiator is **playable, visual, professionally-tested tabular RL** with three deliberately-distinct algorithms (Bellman / Q-Learning / Double-Q) on the same 12×12 grid — the comparison surface is the lesson.

### 1.3 Key Performance Indicators (KPIs)

| KPI | Target | Verification |
|---|---|---|
| Learning convergence | Agent reaches goal in ≤ 3 000 episodes on the medium-difficulty board | `analysis/multi_seed_robustness.py` measured runs |
| Test coverage | ≥ 85 % line coverage | `pytest --cov-fail-under=85` (current: 97.48 %) |
| File-size discipline | All `.py` files ≤ 150 *code* lines | `scripts/check_file_sizes.sh` (pre-commit + CI gate) |
| Lint cleanliness | 0 ruff violations | `uv run ruff check src/ tests/ analysis/ scripts/ main.py` |
| GUI smoothness | 30 FPS sustained during training render | Pygame clock, exercised by manual screenshot capture |
| Reproducibility | `uv sync --dev` + one shell command regenerates every chart in `results/` | Documented in `docs/shared/FINAL_CHECKLIST.md` |

---

## 2. Objectives & Success Metrics

- **Educational Value**: Users can visually see the Q-table updating in real-time via a Value Heatmap and Policy Arrows.
- **Performance**: The engine must be capable of running thousands of episodes per second without GUI, and smoothly at 60 FPS with GUI.
- **Code Quality**: Strict adherence to OOP, modularity (max 150 lines per file), 85%+ test coverage, and no hardcoded values.

### Success Metrics
- Agent successfully learns the optimal path in a 12x12 grid within 3000 episodes.
- GUI accurately reflects the Q-values and policy.
- Code passes all linting and unit tests.

---

## 3. Functional Requirements

### 3.1 Core RL Engine

- **Q-Table**: A 3D NumPy array `(rows, cols, actions)` storing expected rewards.
- **Agent**: Implements the Bellman equation for Q-value updates.
- **Exploration**: Epsilon-Greedy mechanism with configurable decay.
- **State Space**: Discrete grid coordinates `(row, col)`.
- **Action Space**: 4 discrete actions (`UP`, `DOWN`, `LEFT`, `RIGHT`).

### 3.2 Environment (Smart City)

- **Grid**: Configurable size (e.g., 12x12).
- **Obstacles**: Buildings act as impassable walls.
- **Traps**: No-fly zones that terminate the episode with a massive penalty.
- **Wind Zones**: Stochastic areas where `P(s'|s,a) < 1`. Attempting to move in one direction might result in moving in another.
- **Rewards**:
  - Step penalty: -1 (time penalty)
  - Goal reward: +100
  - Trap penalty: -50
  - Wind penalty: -2
  - Wall collision: -5

### 3.3 GUI & Visualization

- **Pygame Engine**: Renders the grid, drone, buildings, traps, and goal.
- **Value Heatmap**: Overlay coloring cells based on `max(Q(s,a))`.
- **Policy Arrows**: Overlay showing the best action `argmax(Q(s,a))` for each cell.
- **Dashboard**: Real-time display showing:
  - Episode number
  - Total reward
  - Epsilon value
  - Steps count
  - Goal rate percentage
  - Reward history graph (last 100 episodes)
  - Legend for cell types
- **Level Editor**: Interactive mode allowing users to place buildings, traps, and wind zones.
- **Keyboard Controls**:
  - `SPACE` — Pause/Resume
  - `F` — Fast mode
  - `H` — Toggle heatmap
  - `A` — Toggle arrows
  - `E` — Toggle editor
  - `S` — Save brain
  - `L` — Load brain
  - `R` — Hard reset

### 3.4 Architecture & SDK

- **SDK Layer**: All business logic must be accessible via a central SDK class.
- **Configuration**: All parameters loaded from a YAML file.
- **Logging**: Centralized logging system.

---

## 4. Non-Functional Requirements

- **Language**: Python 3.11+
- **Libraries**: Pygame, NumPy, PyYAML, Matplotlib (for static analysis), Pytest.
- **Modularity**: No file exceeds 150 lines of code.
- **Documentation**: Comprehensive docstrings and README.

---

## 5. Assumptions & Constraints

- The state space is small enough to fit in memory (Tabular RL).
- The environment is fully observable.
- The project is designed to run on a standard CPU (e.g., i5) without requiring a GPU.

---

## 6. Timeline & Milestones

| Phase | Deliverable |
|-------|------------|
| 1 | Project setup, config, environment |
| 2 | Core RL engine (Q-table, agent, training loop) |
| 3 | Pygame GUI (grid rendering, heatmap, arrows) |
| 4 | Dashboard panel |
| 5 | Level editor |
| 6 | SDK layer integration |
| 7 | Tests (85%+ coverage) |
| 8 | Documentation & README |
