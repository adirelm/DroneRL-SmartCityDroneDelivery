# Product Requirements Document (PRD)

## Q-Learning Algorithm — Temporal Difference Learning with Decaying Alpha

---

## 1. Project Overview & Background

This PRD introduces the **Q-Learning algorithm** as the second RL agent in the DroneRL project, complementing the existing Bellman-equation baseline from Assignment 1. The key distinction is that Q-Learning uses a **decaying learning rate (alpha)** that decreases over time, unlike the Bellman baseline which uses a constant learning rate.

### Context

The existing `Agent` class in `src/agent.py` implements a Q-value update using a **constant learning rate** (`lr = 0.1`):

```
Q(s,a) = Q(s,a) + lr * [r + γ * max(Q(s',a')) - Q(s,a)]
```

This is the **Bellman baseline**. While it converges on simple grids, a constant learning rate can cause instability in noisy or dynamic environments because the agent never stops making large updates — even after it has learned good values.

**Q-Learning with decaying alpha** addresses this by starting with a high learning rate (for fast initial learning) and gradually reducing it (for stable convergence):

```
Q(s,a) = Q(s,a) + α_t * [r + γ * max(Q(s',a')) - Q(s,a)]
α_t+1 = max(α_min, α_t * α_decay)
```

### Existing Codebase Reference

- `src/agent.py` — Current `Agent` class (72 lines), to be refactored into `BellmanAgent(BaseAgent)`
- `src/trainer.py` — Training loop that calls `agent.update()` and `agent.decay_epsilon()`
- `src/sdk.py` — SDK orchestrator that creates Agent instance
- `config/config.yaml` — Agent hyperparameters section
- `docs/assignment-1/PRD_q_learning.md` — Assignment 1 Q-Learning PRD (algorithm description)

---

## 2. Objectives & Success Metrics

### Objectives

1. **Agent Architecture Refactor**: Extract a `BaseAgent` abstract class from the existing `Agent`, enabling multiple algorithm implementations via inheritance (Strategy Pattern).
2. **Q-Learning Agent**: Implement `QLearningAgent(BaseAgent)` with decaying alpha.
3. **Agent Factory**: Create a factory function that instantiates the correct agent based on config.
4. **Convergence Comparison**: Q-Learning should demonstrate faster and more stable convergence than Bellman in noisy environments.

### Success Metrics

| Metric | Target |
|--------|--------|
| Alpha decays from `alpha_start` to `alpha_end` over training | Verified by test |
| Alpha never goes below `alpha_end` floor | Verified by test |
| Q-Learning converges in noisy environments where Bellman struggles | Visual comparison |
| All existing 104 tests still pass after refactor | 100% pass rate |
| New agent tests achieve 85%+ coverage | pytest-cov verified |
| All new files ≤ 150 lines | Verified by wc -l |
| Zero ruff violations | Verified by ruff check |
| Backward compatibility maintained | `Agent = BellmanAgent` alias works |

### KPIs

- On static grid (difficulty 0.0): Both Bellman and Q-Learning converge at similar speeds
- On noisy grid (difficulty 0.5): Q-Learning converges 20-40% faster than Bellman
- On very noisy grid (difficulty 1.0): Q-Learning converges while Bellman oscillates

---

## 3. Functional Requirements

### 3.1 BaseAgent Abstract Class

A new file `src/base_agent.py` containing the abstract base class:

#### Shared Interface (inherited by all agents)

| Method | Description |
|--------|-------------|
| `__init__(config)` | Initialize grid dimensions, gamma, epsilon params, Q-table(s) |
| `choose_action(state) -> int` | Epsilon-greedy action selection |
| `get_best_action(state) -> int` | Return argmax Q-value action |
| `get_max_q(state) -> float` | Return max Q-value for state |
| `decay_epsilon()` | Exponential epsilon decay, clamped to epsilon_end |
| `update(state, action, reward, next_state, done)` | **Abstract** — must be overridden by subclasses |
| `save(path)` | Save Q-table(s) to .npy file(s) |
| `load(path)` | Load Q-table(s) from .npy file(s) |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `q_table` | np.ndarray | The Q-table (or combined table for Double Q) used by GUI overlays |
| `algorithm_name` | str | Human-readable name (e.g., "Bellman", "Q-Learning", "Double Q") |

### 3.2 BellmanAgent (Refactored from existing Agent)

Modifications to `src/agent.py`:

- Rename `Agent` to `BellmanAgent`, inheriting from `BaseAgent`
- Move shared methods to `BaseAgent`
- Keep only `__init__` (calling `super().__init__`) and `update()` (constant-lr Bellman)
- Add backward-compatible alias: `Agent = BellmanAgent`
- `algorithm_name` property returns `"Bellman"`

The `update` method remains unchanged:
```python
def update(self, state, action, reward, next_state, done):
    current_q = self.q_table[state[0], state[1], action]
    next_max_q = 0.0 if done else self.get_max_q(next_state)
    target = reward + self.gamma * next_max_q
    self.q_table[state[0], state[1], action] += self.lr * (target - current_q)
```

### 3.3 QLearningAgent

A new file `src/q_agent.py` containing `QLearningAgent(BaseAgent)`:

#### Alpha Decay Mechanism

| Parameter | Config Key | Default | Description |
|-----------|-----------|---------|-------------|
| `alpha_start` | `q_learning.alpha_start` | 0.5 | Initial learning rate |
| `alpha_end` | `q_learning.alpha_end` | 0.01 | Minimum learning rate floor |
| `alpha_decay` | `q_learning.alpha_decay` | 0.999 | Multiplicative decay factor per episode |

#### Update Rule

Identical to Bellman, but uses decaying `self.alpha` instead of constant `self.lr`:

```python
def update(self, state, action, reward, next_state, done):
    current_q = self.q_table[state[0], state[1], action]
    next_max_q = 0.0 if done else self.get_max_q(next_state)
    target = reward + self.gamma * next_max_q
    self.q_table[state[0], state[1], action] += self.alpha * (target - current_q)
```

#### Alpha Decay

Called after each episode via overridden `decay_epsilon()`:

```python
def decay_epsilon(self):
    super().decay_epsilon()  # decay epsilon as usual
    self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)
```

#### Properties

- `algorithm_name` returns `"Q-Learning"`
- `q_table` same as Bellman (single 3D array)

### 3.4 Agent Factory and Registry

The factory in `src/agent_factory.py` is a thin validating wrapper around an
algorithm registry in `src/algorithms.py`. The registry is the single source
of truth for "which algorithms exist" — every consumer (factory, GUI,
comparison runner, charts, analysis scripts, parametrised tests) reads from
it, so adding a new algorithm means adding one `AlgorithmSpec` line.

```python
# src/algorithms.py
@dataclass(frozen=True)
class AlgorithmSpec:
    name: str
    label: str
    color: str
    agent_class: type[BaseAgent]

ALGORITHM_REGISTRY = (
    AlgorithmSpec("bellman", "Bellman (constant α)", "#d35400", BellmanAgent),
    AlgorithmSpec("q_learning", "Q-Learning (decaying α)", "#2980b9", QLearningAgent),
    AlgorithmSpec("double_q", "Double Q-Learning", "#27ae60", DoubleQAgent),
)
AGENT_CLASSES = {spec.name: spec.agent_class for spec in ALGORITHM_REGISTRY}

# src/agent_factory.py
def create_agent(config: Config) -> BaseAgent:
    name = config.algorithm.name
    if name not in AGENT_CLASSES:
        raise ValueError(f"Unknown algorithm: '{name}'. Valid: {sorted(ALGORITHMS)}")
    return AGENT_CLASSES[name](config)
```

The factory is used by `DroneRLSDK` in `src/sdk.py` to create the agent based
on the `algorithm.name` config value.

### 3.5 Configuration (config.yaml additions)

```yaml
# Algorithm selection
algorithm:
  name: "bellman"  # Options: "bellman", "q_learning", "double_q"

# Q-Learning specific hyperparameters
q_learning:
  alpha_start: 0.5
  alpha_end: 0.01
  alpha_decay: 0.999
```

---

## 4. Non-Functional Requirements

- **Backward Compatibility**: `from src.agent import Agent` must still work (alias to BellmanAgent)
- **All existing tests must pass** without modification (or with minimal import updates)
- **OOP Inheritance**: Clean single-inheritance hierarchy: `BaseAgent` → `BellmanAgent` / `QLearningAgent`
- **No Code Duplication**: Shared logic lives in `BaseAgent`, not duplicated across subclasses
- **File Sizes**: `base_agent.py` ≤ 150, `agent.py` ≤ 150, `q_agent.py` ≤ 150, `agent_factory.py` ≤ 150
- **DRY**: The update formula logic is NOT duplicated — each subclass only contains its unique update method

---

## 5. User Stories

1. **As a student**, I want to select Q-Learning as the training algorithm so I can compare its convergence with Bellman.
2. **As a student**, I want to see alpha decaying in the dashboard so I understand how the learning rate changes.
3. **As a student**, I want to switch between algorithms without restarting the application.
4. **As a student**, I want the Q-Learning agent to use the same GUI overlays (heatmap, arrows) as Bellman.

---

## 6. Assumptions & Constraints

- The Q-table structure (3D NumPy array) is identical for Bellman and Q-Learning — only the update rule differs
- Alpha decay is per-episode (not per-step) to match epsilon decay frequency
- The factory pattern is sufficient — no need for a plugin/registry system
- GUI overlays read `agent.q_table` — all agents must expose this as a 3D NumPy array

---

## 7. Acceptance Criteria

- [ ] **Alpha MUST decay per episode** — non-negotiable (constant alpha causes divergence)
- [ ] Alpha decays from `alpha_start` toward `alpha_end` with decay factor `alpha_decay`
- [ ] Alpha never goes below `alpha_end` floor
- [ ] All 104 existing tests pass after refactor with ZERO modifications
- [ ] `BaseAgent` abstract class exists with shared interface
- [ ] `BellmanAgent` inherits from `BaseAgent` and passes all existing tests
- [ ] `Agent = BellmanAgent` alias works for backward compatibility
- [ ] `QLearningAgent` implements update with decaying alpha
- [ ] Alpha starts at `alpha_start` and decays toward `alpha_end`
- [ ] Alpha never goes below `alpha_end`
- [ ] `create_agent(config)` returns correct agent type based on `algorithm.name`
- [ ] Unknown algorithm name raises `ValueError`
- [ ] All 104 existing tests still pass
- [ ] New tests cover BaseAgent, QLearningAgent, and factory with 85%+ coverage
- [ ] No file exceeds 150 lines
- [ ] Zero ruff violations
- [ ] Q-Learning shows faster convergence than Bellman on noisy grids

---

## 8. Timeline & Milestones

| Phase | Deliverable |
|-------|------------|
| 1 | Create `src/base_agent.py` with shared interface |
| 2 | Refactor `src/agent.py` to `BellmanAgent(BaseAgent)` |
| 3 | Create `src/agent_factory.py` |
| 4 | Verify all existing tests pass |
| 5 | Create `src/q_agent.py` with decaying alpha |
| 6 | Add `algorithm` and `q_learning` sections to config.yaml |
| 7 | Write tests for BaseAgent, QLearningAgent, factory |
| 8 | Integrate factory into SDK |
