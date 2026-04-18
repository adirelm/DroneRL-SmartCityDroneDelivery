# DroneRL — Smart City Drone Delivery

An educational reinforcement learning lab that compares **three tabular RL algorithms** — Bellman (constant α), Q-Learning (decaying α), and Double Q-Learning (dual tables) — on a configurable smart-city drone delivery task. Built with Python + Pygame.

> Bar-Ilan University, Vibe Coding Workshop — Assignment 2

---

## Objectives

1. Implement **three RL algorithms** sharing the same `BaseAgent` interface so they can be swapped at runtime.
2. Build a **dynamic, randomizable board** with sliders that let the user shape the noise / density / difficulty of the environment.
3. Demonstrate, with **comparison graphs**, where each algorithm shines and where it breaks.
4. Keep every Python file ≤ 150 lines, ≥ 85 % test coverage, zero ruff violations, and all parameters in `config/config.yaml`.

---

## What Was Implemented

| Layer | Modules |
|-------|---------|
| **Agents** (Strategy pattern) | [`base_agent.py`](src/base_agent.py), [`agent.py`](src/agent.py) (Bellman), [`q_agent.py`](src/q_agent.py), [`double_q_agent.py`](src/double_q_agent.py), [`agent_factory.py`](src/agent_factory.py) |
| **Dynamic board** | [`environment.py`](src/environment.py) (added `CellType.PIT`), [`hazard_generator.py`](src/hazard_generator.py), [`sliders.py`](src/sliders.py) |
| **Comparison system** | [`comparison.py`](src/comparison.py) (matplotlib charts), `SDK.run_comparison()`, [`scripts/generate_comparison_charts.py`](scripts/generate_comparison_charts.py) |
| **GUI integration** | Algorithm switching via keys 1/2/3, hazard regeneration via G, live status bar |

---

## Installation

Requires **Python 3.11–3.13** and **UV**.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/adirelm/DroneRL-SmartCityDroneDelivery.git
cd DroneRL-SmartCityDroneDelivery
git checkout assignment-2
uv sync --dev
```

## Running

```bash
uv run main.py
```

To regenerate the convergence comparison charts:
```bash
uv run python scripts/generate_comparison_charts.py
```

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| `SPACE` | Pause / Resume training |
| `F` | Toggle fast mode |
| `H` | Toggle Q-value heatmap |
| `A` | Toggle policy arrows |
| `E` | Toggle level editor |
| `T` | Cycle editor obstacle (Building / Trap / Wind / Pit) |
| `G` | Regenerate random hazards (uses sliders) |
| `1` | Switch to **Bellman** agent |
| `2` | Switch to **Q-Learning** agent |
| `3` | Switch to **Double Q-Learning** agent |
| `S` / `L` | Save / Load Q-table |
| `R` | Hard reset (clears training) |

---

## Algorithm Comparison

### Scenario 1 — Medium difficulty (noisy environment)

![Scenario 1](data/comparison/scenario1_medium.png)

**Setup**: 12×12 grid, 18 % hazards, noise=0.8, drift=0.34, 4000 episodes, seed=11.

| Algorithm | Avg reward (last 100) |
|-----------|----------------------|
| Bellman (constant α=0.5) | 35 |
| Q-Learning (decaying α) | 58 |
| **Double Q-Learning** | **65** |

Bellman lags badly because the high constant learning rate keeps over-correcting on the noisy wind drift. The decaying α of both Q-Learning and Double Q-Learning lets the value estimates settle, and Double Q's dual tables further suppress maximisation bias.

### Scenario 2 — High difficulty (very noisy + denser hazards)

![Scenario 2](data/comparison/scenario2_hard.png)

**Setup**: 12×12 grid, 18 % hazards, noise=1.0, difficulty=0.8, drift=0.54, 8000 episodes, seed=7.

| Algorithm | Avg reward (last 100) |
|-----------|----------------------|
| Bellman | 63 |
| Q-Learning | 59 |
| **Double Q-Learning** | **63** |

In the harder scenario all three eventually solve the task, but Double Q-Learning converges most consistently because it doesn't over-estimate the noisy max returns.

---

## Conclusions

1. **Constant α (Bellman) is fragile in noisy environments.** Without decay, the agent keeps amplifying recent noise and oscillates around the optimum. Decay is not optional.
2. **Q-Learning** with decaying α stabilises quickly but is still vulnerable to maximisation bias when reward variance is high.
3. **Double Q-Learning** wins the medium scenario outright and ties on the hard one — the cross-table evaluation is exactly the bias removal Hasselt (2010) proposed, and it shows up empirically.
4. **Environment shape matters more than hyper-parameters.** The same algorithms behave very differently when the noise / density / difficulty sliders push the board into a higher-variance regime.

---

## Algorithms — Update Rules

**Bellman (constant α)** — Assignment 1 baseline. A single Q-table updated with a fixed learning rate; fast on static grids but over-reacts to noise.

$$Q(s,a) \leftarrow Q(s,a) + \alpha \left[ r + \gamma \max_{a'} Q(s',a') - Q(s,a) \right]$$

**Q-Learning (decaying α per episode)** — same update, but α shrinks geometrically each episode (floored at $\alpha_{\min}$) so value estimates settle in noisy environments.

$$Q(s,a) \leftarrow Q(s,a) + \alpha_t \left[ r + \gamma \max_{a'} Q(s',a') - Q(s,a) \right], \quad \alpha_{t+1} = \max(\alpha_{\min}, \alpha_t \cdot \alpha_{\text{decay}})$$

**Double Q-Learning (Hasselt 2010)** — two tables $Q_A, Q_B$; each step flips a coin and updates one using the other's value at the arg-max, removing the $\max$-operator overestimation bias.

$$\text{with prob. } \tfrac{1}{2}: Q_A(s,a) \leftarrow Q_A(s,a) + \alpha [r + \gamma Q_B(s', \arg\max_{a'} Q_A(s',a')) - Q_A(s,a)]$$

$$\text{otherwise}: Q_B(s,a) \leftarrow Q_B(s,a) + \alpha [r + \gamma Q_A(s', \arg\max_{a'} Q_B(s',a')) - Q_B(s,a)]$$

---

## Parameter Analysis

`config/config.yaml` exposes every tunable value. Most influential for differentiating the algorithms:

| Param | Effect |
|-------|--------|
| `agent.learning_rate` | Bellman's α (kept constant). Higher → faster learning but more instability under noise. |
| `q_learning.alpha_decay` / `double_q.alpha_decay` | Smaller value → faster decay → quicker stabilisation but less long-term plasticity. |
| `agent.epsilon_decay` | Slower decay → more exploration → safer but slower convergence. |
| `dynamic_board.noise_level` | Scales the wind drift probability. Above ~0.7 Bellman starts to break. |
| `dynamic_board.hazard_density` | Above ~0.25 paths to the goal become brittle and Q-Learning catches up to Double-Q. |
| `dynamic_board.difficulty` | Master multiplier; combines noise and density. |

---

## Project Structure

```
├── src/
│   ├── base_agent.py       # Abstract base for the 3 algorithms
│   ├── agent.py            # BellmanAgent (constant α)
│   ├── q_agent.py          # QLearningAgent (decaying α)
│   ├── double_q_agent.py   # DoubleQAgent (QA + QB tables)
│   ├── agent_factory.py    # Selects algorithm from config
│   ├── environment.py      # Smart-city grid + cell types (incl. PIT)
│   ├── hazard_generator.py # Random hazard placer driven by sliders
│   ├── sliders.py          # Pygame slider widgets
│   ├── trainer.py          # Episode-level training loop
│   ├── game_logic.py       # Step-level training, demo, convergence
│   ├── sdk.py              # Public API (train, switch_algorithm, run_comparison)
│   ├── comparison.py       # ComparisonStore + matplotlib chart
│   ├── gui.py              # Pygame orchestrator
│   ├── dashboard.py / buttons.py / overlays.py / renderer.py / editor.py
│   ├── actions.py / config_loader.py / logger.py
│   └── __init__.py
├── tests/                  # 187 pytest tests, 98%+ coverage
├── scripts/
│   └── generate_comparison_charts.py
├── config/config.yaml      # All parameters
├── data/comparison/        # Generated convergence PNGs
├── docs/
│   ├── assignment-1/       # PRD, PLAN, TODO from Assignment 1
│   ├── assignment-2/       # 3× PRD/PLAN/TODO for new features
│   └── shared/             # ARCHITECTURE.md, PROMPTS.md
├── main.py
├── pyproject.toml
└── CLAUDE.md               # Global coding standards (150-line cap, TDD, OOP, …)
```

---

## Running Tests

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run ruff check src/ tests/ main.py
```

Current state: **187 tests passing**, **98% coverage**, zero ruff violations.

---

## Tech Stack

- **Python 3.11–3.13** · **Pygame** (GUI) · **NumPy** (Q-tables, env)
- **PyYAML** (config) · **Matplotlib** (comparison charts)
- **Pytest** + **pytest-cov** · **Ruff** (lint) · **UV** (env / deps)

---

## Contributing

Follow the rules in [CLAUDE.md](CLAUDE.md):
- TDD — write the failing test first.
- Every file ≤ 150 lines; split by responsibility, not by layer.
- All tunables go to `config/config.yaml`. No magic numbers in source.
- `ruff check` must report zero issues before every commit.
- Maintain ≥ 85 % coverage.

---

## License & Credits

MIT License © 2026 Adir Elmakais.
Course material: Dr. Yoram Segal, *Vibe Coding Workshop*, Bar-Ilan University.
Algorithm references: Watkins (1989) for Q-Learning and Hado van Hasselt (2010) "Double Q-Learning" NeurIPS.
