# Implementation Plan

## Q-Learning Algorithm — Agent Architecture Refactor + Temporal Difference Learning

---

## Architecture Strategy

The refactor introduces a **Strategy Pattern via inheritance** to support multiple RL algorithms while preserving full backward compatibility. The existing monolithic `Agent` class is split into a shared abstract base and algorithm-specific subclasses.

```
BaseAgent (src/base_agent.py) — abstract
    |
    ├── BellmanAgent (src/agent.py) — constant lr, existing behavior
    |
    └── QLearningAgent (src/q_agent.py) — decaying alpha
```

A **factory function** in `src/agent_factory.py` creates the correct agent based on `config.algorithm.name`. The SDK and GUI never instantiate agents directly — they always go through the factory.

Key architectural decisions:

1. **BaseAgent owns all shared logic** — Q-table initialization, epsilon-greedy action selection, `get_best_action()`, `get_max_q()`, `decay_epsilon()`, `save()`, `load()`. Subclasses only override `update()` and add algorithm-specific parameters.

2. **Backward-compatible alias** — `src/agent.py` exports `Agent = BellmanAgent` so all existing `from src.agent import Agent` imports continue to work without changes.

3. **Minimal test disruption** — The refactor preserves the exact method signatures and behavior of the existing Agent class. All 104 existing tests must pass without modification.

4. **Config-driven algorithm selection** — A new `algorithm.name` key in `config.yaml` controls which agent the factory creates. Default is `"bellman"` for backward compatibility.

```
config.yaml (algorithm.name)
      |
      v
agent_factory.create_agent(config)
      |
      ├── "bellman"   -> BellmanAgent(config)
      ├── "q_learning" -> QLearningAgent(config)
      └── "double_q"  -> DoubleQAgent(config)  [future, PRD 3]
```

---

## Development Approach: TDD

1. **Write tests for BaseAgent first** — Verify shared interface: Q-table shape, epsilon-greedy behavior, decay, save/load, `get_best_action`, `get_max_q`. These tests instantiate a concrete subclass (BellmanAgent) to test shared methods.
2. **Refactor Agent into BaseAgent + BellmanAgent** — Run existing 104 tests. All must pass. Zero modifications to test files.
3. **Write tests for QLearningAgent** — Alpha initialization, decay per episode, floor clamping, update rule with decaying alpha.
4. **Implement QLearningAgent** — Pass new tests.
5. **Write tests for agent_factory** — Correct instantiation for each algorithm name, ValueError on unknown name.
6. **Implement factory** — Pass factory tests.
7. **Integrate factory into SDK** — Verify SDK tests still pass.

---

## Phase 1: BaseAgent Extraction

### 1.1 BaseAgent Abstract Class

**File**: `src/base_agent.py` (~80 lines, new file)

```
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    NUM_ACTIONS = 4

    __init__(config)           — grid dims, gamma, epsilon params, Q-table init
    choose_action(state) -> int — epsilon-greedy (shared)
    get_best_action(state) -> int — argmax Q(s,a) (shared)
    get_max_q(state) -> float  — max Q(s,a) (shared)
    decay_epsilon()            — exponential decay, clamped (shared)
    save(path)                 — np.save Q-table (shared)
    load(path)                 — np.load Q-table (shared)

    @abstractmethod
    update(state, action, reward, next_state, done) -> None

    @property
    q_table -> np.ndarray      — the Q-table used by GUI overlays
    @property
    algorithm_name -> str      — human-readable name (abstract)
```

All shared logic currently in `src/agent.py` (lines 12-72) moves here. The `q_table` is initialized as `np.zeros((rows, cols, NUM_ACTIONS))` in `__init__`. Subclasses that need different table structures (Double Q) override `__init__` and the `q_table` property.

### 1.2 BellmanAgent Refactor

**File**: `src/agent.py` (currently 72 lines -> ~35 lines)

After extraction, `agent.py` becomes minimal:

```
from src.base_agent import BaseAgent

class BellmanAgent(BaseAgent):
    algorithm_name = "Bellman"

    def __init__(self, config):
        super().__init__(config)
        self.lr = config.agent.learning_rate

    def update(self, state, action, reward, next_state, done):
        current_q = self.q_table[state[0], state[1], action]
        next_max_q = 0.0 if done else self.get_max_q(next_state)
        target = reward + self.gamma * next_max_q
        self.q_table[state[0], state[1], action] += self.lr * (target - current_q)

# Backward compatibility alias
Agent = BellmanAgent
```

The `Agent = BellmanAgent` alias ensures all existing imports (`from src.agent import Agent`) work without changes.

### 1.3 Tests — Verify Backward Compatibility

**Action**: Run full test suite (`uv run pytest`). All 104 tests must pass.

**File**: `tests/test_agent.py` — No modifications needed. Tests import `Agent` from `src.agent`, which now resolves to `BellmanAgent`. All method signatures and behavior are identical.

### 1.4 Tests — BaseAgent Shared Interface

**File**: `tests/test_base_agent.py` (~60 lines, new file)

- Test Q-table shape is `(rows, cols, 4)`
- Test `choose_action()` returns valid action in range [0, 3]
- Test `choose_action()` is random when epsilon=1.0
- Test `choose_action()` is greedy when epsilon=0.0
- Test `get_best_action()` returns argmax
- Test `get_max_q()` returns max value
- Test `decay_epsilon()` reduces epsilon
- Test `decay_epsilon()` clamps to `epsilon_end`
- Test `save()` and `load()` round-trip Q-table
- Test `algorithm_name` property returns a string
- Test `q_table` property returns ndarray

---

## Phase 2: QLearningAgent

### 2.1 QLearningAgent Class

**File**: `src/q_agent.py` (~55 lines, new file)

```
from src.base_agent import BaseAgent

class QLearningAgent(BaseAgent):
    algorithm_name = "Q-Learning"

    def __init__(self, config):
        super().__init__(config)
        q_cfg = config.q_learning
        self.alpha = q_cfg.alpha_start
        self.alpha_end = q_cfg.alpha_end
        self.alpha_decay = q_cfg.alpha_decay

    def update(self, state, action, reward, next_state, done):
        current_q = self.q_table[state[0], state[1], action]
        next_max_q = 0.0 if done else self.get_max_q(next_state)
        target = reward + self.gamma * next_max_q
        self.q_table[state[0], state[1], action] += self.alpha * (target - current_q)

    def decay_epsilon(self):
        super().decay_epsilon()
        self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)
```

Key differences from BellmanAgent:
- Uses `self.alpha` (decaying) instead of `self.lr` (constant)
- `decay_epsilon()` also decays alpha
- Alpha is clamped to `alpha_end` floor

### 2.2 Config — Q-Learning Hyperparameters

**File**: `config/config.yaml` (add ~10 lines)

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

### 2.3 Tests — QLearningAgent

**File**: `tests/test_q_agent.py` (~90 lines, new file)

- Test alpha initializes to `alpha_start` from config
- Test alpha decays after `decay_epsilon()` call
- Test alpha never goes below `alpha_end`
- Test alpha decay formula: `alpha *= alpha_decay`
- Test `update()` uses `self.alpha` not `self.lr`
- Test Q-value changes correctly after single update
- Test `algorithm_name` returns `"Q-Learning"`
- Test `q_table` property returns valid ndarray
- Test `save()` and `load()` preserve Q-table
- Test alpha is independent of epsilon (both decay, but separately)
- Test alpha after 1000 decay steps approaches `alpha_end`

---

## Phase 3: Agent Factory

### 3.1 Factory Function

**File**: `src/agent_factory.py` (~30 lines, new file)

```
from src.base_agent import BaseAgent
from src.config_loader import Config

def create_agent(config: Config) -> BaseAgent:
    name = config.algorithm.name
    if name == "bellman":
        from src.agent import BellmanAgent
        return BellmanAgent(config)
    elif name == "q_learning":
        from src.q_agent import QLearningAgent
        return QLearningAgent(config)
    elif name == "double_q":
        from src.double_q_agent import DoubleQAgent
        return DoubleQAgent(config)
    raise ValueError(f"Unknown algorithm: {name}")
```

Lazy imports inside the function avoid circular dependencies and keep the file minimal. The `double_q` branch is included for forward compatibility with PRD 3.

### 3.2 Tests — Agent Factory

**File**: `tests/test_agent_factory.py` (~50 lines, new file)

- Test `create_agent(config)` with `algorithm.name = "bellman"` returns `BellmanAgent`
- Test `create_agent(config)` with `algorithm.name = "q_learning"` returns `QLearningAgent`
- Test `create_agent(config)` with unknown name raises `ValueError`
- Test returned agent has `q_table` property
- Test returned agent has `update()` method
- Test returned agent has `algorithm_name` property

---

## Phase 4: SDK and GUI Integration

### 4.1 SDK — Use Agent Factory

**File**: `src/sdk.py` (currently 90 lines -> ~100 lines)

- Replace `from src.agent import Agent` with `from src.agent_factory import create_agent`
- Replace `self.agent = Agent(self.config)` with `self.agent = create_agent(self.config)`
- In `reset()`, also use `create_agent(self.config)`
- Add `algorithm_name` property: `return self.agent.algorithm_name`
- Add `alpha` property: `return getattr(self.agent, 'alpha', None)` — returns alpha for Q-Learning agents, None for Bellman

### 4.2 GUI — Algorithm Name in Status Bar (~3 lines changed)

**File**: `src/gui.py` (currently 129 lines -> ~132 lines)

- Use agent factory via SDK (no direct Agent import changes needed since GUI uses `self.agent` from direct construction)
- Update `_status_bar()` to include algorithm name from `self.agent.algorithm_name` (if available)

### 4.3 Actions — Use Factory for Reset (~3 lines changed)

**File**: `src/actions.py` (currently 56 lines -> ~58 lines)

- In the `"reset"` action, replace `Agent(gui.cfg)` with `create_agent(gui.cfg)` import
- This ensures reset creates the correct agent type based on config

### 4.4 Game Logic — Accept BaseAgent Type (~2 lines changed)

**File**: `src/game_logic.py` (currently 136 lines -> ~137 lines)

- Change type hint from `Agent` to `BaseAgent` (or keep duck-typed)
- Import `BaseAgent` instead of `Agent`

### 4.5 Trainer — Accept BaseAgent Type (~2 lines changed)

**File**: `src/trainer.py` (currently 83 lines -> ~84 lines)

- Change type hint from `Agent` to `BaseAgent`
- Import `BaseAgent` instead of `Agent`

### 4.6 Dashboard — Show Alpha Value (~5 lines added)

**File**: `src/dashboard.py` (currently 147 lines -> ~150 lines)

- In `_draw_metrics()`, if `metrics` dict contains `"alpha"`, render it below epsilon
- This requires GameLogic/SDK to include alpha in the metrics dict

### 4.7 Integration Tests

**File**: `tests/test_sdk.py` (add ~10 lines)

- Test SDK creates BellmanAgent when `algorithm.name = "bellman"`
- Test SDK creates QLearningAgent when `algorithm.name = "q_learning"`
- Test `train_step()` works with QLearningAgent
- Test `reset()` preserves algorithm selection

---

## Phase 5: Verification

### 5.1 Full Test Suite

Run `uv run pytest` — all 104 existing tests plus new tests must pass.

### 5.2 Coverage Check

Run `uv run pytest --cov=src --cov-report=html` — verify 85%+ coverage on all new files:
- `src/base_agent.py` — 85%+
- `src/q_agent.py` — 85%+
- `src/agent_factory.py` — 85%+

### 5.3 Lint Check

Run `uv run ruff check src/ tests/` — zero violations.

---

## File Size Constraint

Every `.py` file must stay under **150 lines**. Estimated final line counts:

| File | Current | After Changes | Status |
|------|---------|---------------|--------|
| `src/base_agent.py` | 0 (new) | ~80 | OK |
| `src/agent.py` | 72 | ~35 | OK (smaller after extraction) |
| `src/q_agent.py` | 0 (new) | ~55 | OK |
| `src/agent_factory.py` | 0 (new) | ~30 | OK |
| `src/sdk.py` | 90 | ~100 | OK |
| `src/gui.py` | 129 | ~132 | OK |
| `src/actions.py` | 56 | ~58 | OK |
| `src/game_logic.py` | 136 | ~137 | OK |
| `src/trainer.py` | 83 | ~84 | OK |
| `src/dashboard.py` | 147 | ~150 | At limit |
| `tests/test_base_agent.py` | 0 (new) | ~60 | OK |
| `tests/test_q_agent.py` | 0 (new) | ~90 | OK |
| `tests/test_agent_factory.py` | 0 (new) | ~50 | OK |

**Risk mitigation**: If `dashboard.py` exceeds 150 lines when adding alpha display, extract the `_draw_metrics()` method into a helper or simplify the metric rendering logic.

---

## Backward Compatibility Strategy

The refactor is designed so that **zero existing tests need modification**:

1. `from src.agent import Agent` still works (alias to BellmanAgent)
2. `Agent(config)` constructor signature unchanged
3. `agent.choose_action()`, `agent.update()`, `agent.decay_epsilon()` — same signatures
4. `agent.q_table` — same 3D ndarray shape
5. `agent.epsilon`, `agent.lr`, `agent.gamma` — same attributes
6. `agent.save()` / `agent.load()` — same file format

The only new code paths are activated when `config.algorithm.name != "bellman"`, which the existing tests never set.
