# Implementation Plan

## Double Q-Learning — Bias-Corrected Dual-Table Learning + Comparison System

---

## Architecture Strategy

Double Q-Learning is the third agent in the inheritance hierarchy established by PRD 2 (Q-Learning). It introduces a **dual-table architecture** that decouples action selection from evaluation, eliminating the maximization bias inherent in standard Q-Learning.

The comparison system is a separate concern: a **ComparisonStore** collects training results from all three algorithms, and a chart generator uses matplotlib to produce convergence comparison plots.

```
BaseAgent (src/base_agent.py) — abstract
    |
    ├── BellmanAgent (src/agent.py)
    |
    ├── QLearningAgent (src/q_agent.py)
    |
    └── DoubleQAgent (src/double_q_agent.py)
              |
              ├── q_table_a: np.ndarray  — first Q-table
              ├── q_table_b: np.ndarray  — second Q-table
              └── q_table (property)     — returns q_table_a + q_table_b

ComparisonStore (src/comparison.py)
    |
    ├── store(name, history, metrics) — save results per algorithm
    ├── get_histories() -> dict       — all reward histories
    └── generate_comparison_chart()   — matplotlib PNG output
```

Key architectural decisions:

1. **DoubleQAgent inherits from BaseAgent, not QLearningAgent** — Although both share alpha decay, inheriting from QLearningAgent would create a confusing inheritance chain. Instead, DoubleQAgent duplicates the alpha decay logic (~3 lines) for clarity. The alternative (a mixin) adds unnecessary complexity for such a small amount of shared code.

2. **`q_table` property returns `QA + QB`** — The GUI overlays (`overlays.py`) read `agent.q_table` to render heatmaps and arrows. By exposing the combined table as a property, DoubleQAgent is fully compatible with all existing GUI code without any modifications to overlays, renderer, or dashboard.

3. **Action selection uses combined table** — `get_best_action()` and `get_max_q()` are overridden to use `q_table_a + q_table_b`, matching the Double Q-Learning specification where epsilon-greedy selection uses the sum of both tables.

4. **ComparisonStore is stateless and SDK-owned** — The SDK holds a single `ComparisonStore` instance. After training each algorithm, results are stored. The chart generator is a standalone function that reads from the store, keeping concerns separated.

5. **Algorithm switching preserves the environment** — When the user switches algorithms, only the agent and trainer are recreated. The environment grid (including any editor placements and dynamic hazards) remains unchanged, enabling fair comparisons.

```
GUI (keys 1/2/3/C)
      |
      v
SDK.switch_algorithm(name)        SDK.run_comparison(episodes)
      |                                  |
      v                                  v
agent_factory.create_agent()      Train all 3, store in ComparisonStore
      |                                  |
      v                                  v
New agent, reset trainer          generate_comparison_chart() -> PNG
(environment preserved)
```

---

## Development Approach: TDD

1. **Write tests for DoubleQAgent** — Two tables initialized to zeros, each update modifies exactly one table, cross-table evaluation, `q_table` property returns sum, alpha decay.
2. **Implement DoubleQAgent** — Pass all tests.
3. **Register in factory** — Verify factory returns DoubleQAgent for `"double_q"`.
4. **Write tests for ComparisonStore** — Store/retrieve results, `has_all()`, `clear()`, `get_histories()`.
5. **Implement ComparisonStore** — Pass tests.
6. **Write tests for chart generation** — Output file exists, correct format, handles missing data gracefully.
7. **Implement chart generator** — Pass tests.
8. **Integrate into SDK** — `switch_algorithm()`, `run_comparison()`.
9. **Add GUI controls** — Keyboard shortcuts, algorithm buttons, status bar.

---

## Phase 1: DoubleQAgent

### 1.1 DoubleQAgent Class

**File**: `src/double_q_agent.py` (~95 lines, new file)

```
from src.base_agent import BaseAgent

class DoubleQAgent(BaseAgent):
    algorithm_name = "Double Q-Learning"

    __init__(config)
        — super().__init__(config) for shared params
        — self.q_table_a = np.zeros((rows, cols, NUM_ACTIONS))
        — self.q_table_b = np.zeros((rows, cols, NUM_ACTIONS))
        — Load alpha_start, alpha_end, alpha_decay from config.double_q
        — self.alpha = alpha_start

    @property
    q_table -> np.ndarray
        — return self.q_table_a + self.q_table_b

    get_best_action(state) -> int
        — override: argmax of combined table (q_table_a + q_table_b)

    get_max_q(state) -> float
        — override: max of combined table

    update(state, action, reward, next_state, done)
        — With probability 0.5, update QA:
            a* = argmax(QA[s'])
            QA[s,a] += alpha * (r + gamma * QB[s', a*] - QA[s,a])
        — Otherwise, update QB:
            a* = argmax(QB[s'])
            QB[s,a] += alpha * (r + gamma * QA[s', a*] - QB[s,a])

    decay_epsilon()
        — super().decay_epsilon()
        — self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)

    save(path)
        — np.save(f"{path}_a.npy", self.q_table_a)
        — np.save(f"{path}_b.npy", self.q_table_b)

    load(path)
        — self.q_table_a = np.load(f"{path}_a.npy")
        — self.q_table_b = np.load(f"{path}_b.npy")
```

Key implementation detail for the `update()` cross-table mechanism:

- When updating QA: select best action from QA (`argmax(QA[s'])`), but evaluate that action using QB (`QB[s', a*]`). This decouples selection from evaluation.
- When updating QB: select best action from QB (`argmax(QB[s'])`), but evaluate using QA (`QA[s', a*]`).
- The 50/50 random split uses `random.random() < 0.5`.

### 1.2 Config — Double Q-Learning Hyperparameters

**File**: `config/config.yaml` (add ~5 lines)

```yaml
# Double Q-Learning specific hyperparameters
double_q:
  alpha_start: 0.5
  alpha_end: 0.01
  alpha_decay: 0.999
```

### 1.3 Agent Factory — Register Double Q

**File**: `src/agent_factory.py` (no line count change — `double_q` branch already planned in PRD 2)

- Verify the `"double_q"` branch imports and returns `DoubleQAgent`

### 1.4 Tests — DoubleQAgent

**File**: `tests/test_double_q_agent.py` (~130 lines, new file)

- Test QA and QB are initialized to zeros with shape `(rows, cols, 4)`
- Test `q_table` property returns `QA + QB`
- Test `q_table` shape is `(rows, cols, 4)`
- Test `get_best_action()` uses combined table, not QA or QB alone
- Test `get_max_q()` uses combined table
- Test single `update()` call modifies exactly one table (not both)
- Test cross-table evaluation: argmax from updating table, value from other table
- Test over many updates, both tables accumulate values (not just one)
- Test alpha initializes to `alpha_start`
- Test alpha decays after `decay_epsilon()`
- Test alpha never goes below `alpha_end`
- Test `algorithm_name` returns `"Double Q-Learning"`
- Test `save()` creates two .npy files (`_a.npy` and `_b.npy`)
- Test `load()` restores both tables correctly
- Test `choose_action()` works (inherited from BaseAgent, uses combined table)
- Test update with `done=True` uses `next_val = 0.0`

---

## Phase 2: Comparison System

### 2.1 ComparisonStore Class

**File**: `src/comparison.py` (~120 lines, new file)

```
class ComparisonStore:
    __init__()
        — self.results = {}  # algorithm_name -> ResultEntry

    store(name, reward_history, metrics)
        — Store training results for one algorithm run

    has_results(name) -> bool
        — Check if results exist for a specific algorithm

    has_all() -> bool
        — Check if all 3 algorithms (Bellman, Q-Learning, Double Q) have results

    get_histories() -> dict[str, list[float]]
        — Return reward histories keyed by algorithm name

    clear()
        — Clear all stored results


def generate_comparison_chart(store, output_path, config):
    — Create matplotlib figure with 3 convergence curves
    — Apply moving average smoothing (window from config.comparison.smoothing_window)
    — Color-code: Bellman (orange), Q-Learning (green), Double Q (blue)
    — Add legend, axis labels ("Episode", "Reward (smoothed)"), title
    — Add grid lines for readability
    — Save as PNG to output_path
    — Close figure to free memory
```

Chart generation details:
- Uses `matplotlib.pyplot` (already a project dependency or easily added)
- Smoothing via rolling mean with configurable window size (default: 50 episodes)
- Colors from config: `colors.algo_bellman`, `colors.algo_q_learning`, `colors.algo_double_q`
- Output directory: `data/comparison/` (created automatically via `os.makedirs`)
- Filename: `comparison.png`

### 2.2 Config — Comparison Settings

**File**: `config/config.yaml` (add ~10 lines)

```yaml
# Comparison settings
comparison:
  max_episodes: 5000
  output_dir: data/comparison
  smoothing_window: 50

# Algorithm curve colors (under colors section)
colors:
  algo_bellman: [255, 160, 40]
  algo_q_learning: [80, 200, 120]
  algo_double_q: [100, 140, 255]
```

### 2.3 Tests — ComparisonStore and Chart

**File**: `tests/test_comparison.py` (~100 lines, new file)

- Test `store()` saves results under the algorithm name
- Test `has_results()` returns True after storing, False before
- Test `has_all()` returns True only when all 3 algorithms have results
- Test `has_all()` returns False when only 1 or 2 have results
- Test `get_histories()` returns dict with correct keys
- Test `get_histories()` returns correct reward lists
- Test `clear()` removes all stored results
- Test `generate_comparison_chart()` creates a PNG file at the specified path
- Test chart generation with missing algorithms raises or handles gracefully
- Test chart generation creates the output directory if it does not exist
- Test smoothing window applies correctly (verify smoothed data length)

---

## Phase 3: SDK Extensions

### 3.1 SDK — Algorithm Switching and Comparison

**File**: `src/sdk.py` (after PRD 2: ~100 lines -> ~130 lines)

New methods:

```
switch_algorithm(name: str) -> None
    — Update config.algorithm.name
    — Create new agent via factory
    — Reset trainer with new agent (same environment)
    — Log algorithm switch

run_comparison(episodes: int = None) -> None
    — For each algorithm ("bellman", "q_learning", "double_q"):
        1. switch_algorithm(name)
        2. Train for episodes (default from config.comparison.max_episodes)
        3. Store reward_history and metrics in ComparisonStore
    — Generate comparison chart

get_comparison_store() -> ComparisonStore
    — Return the store instance

generate_comparison_chart() -> str
    — Call generate_comparison_chart(store, output_path, config)
    — Return the output file path
```

New instance attributes:

```
self.comparison_store = ComparisonStore()
```

### 3.2 Tests — SDK Extensions

**File**: `tests/test_sdk.py` (add ~25 lines)

- Test `switch_algorithm("q_learning")` creates QLearningAgent
- Test `switch_algorithm("double_q")` creates DoubleQAgent
- Test `switch_algorithm()` preserves environment grid
- Test `switch_algorithm()` resets trainer episode count
- Test `run_comparison()` stores results for all 3 algorithms
- Test `get_comparison_store()` returns ComparisonStore instance
- Test `generate_comparison_chart()` creates PNG file

---

## Phase 4: GUI Integration

### 4.1 Algorithm Selector Buttons

**File**: `src/buttons.py` (currently 135 lines -> ~150 lines)

- Add algorithm selector buttons to `_get_buttons()` function
- Three toggle-style buttons: "Bellman" / "Q-Learning" / "Double Q"
- Active algorithm button is highlighted (uses `state_dict["algorithm"]` to determine which)
- Buttons dispatch actions: `"algo_bellman"`, `"algo_q_learning"`, `"algo_double_q"`
- Add "Compare All" button visible when in paused state after training

### 4.2 Keyboard Shortcuts

**File**: `src/gui.py` (after PRD 2: ~132 lines -> ~140 lines)

- Add key mappings in `_on_key()`:
  - `pygame.K_1` -> `"algo_bellman"` — switch to Bellman
  - `pygame.K_2` -> `"algo_q_learning"` — switch to Q-Learning
  - `pygame.K_3` -> `"algo_double_q"` — switch to Double Q-Learning
  - `pygame.K_c` -> `"compare"` — run comparison or show chart

### 4.3 Actions — Algorithm Switching Dispatch

**File**: `src/actions.py` (after PRD 2: ~58 lines -> ~80 lines)

Add new action handlers:

```
"algo_bellman"     -> switch to Bellman, reset training state
"algo_q_learning"  -> switch to Q-Learning, reset training state
"algo_double_q"    -> switch to Double Q-Learning, reset training state
"compare"          -> run comparison if no results, else show chart
```

Each `algo_*` action:
1. Calls `gui.sdk.switch_algorithm(name)` (if SDK is wired) or directly recreates agent via factory
2. Resets `gui.agent` and `gui.logic` with the new agent
3. Sets `gui.paused = True`, `gui.editor.active = True` (return to editor mode for review)

The `"compare"` action:
1. If comparison store has results, open/show the chart
2. Otherwise, trigger `sdk.run_comparison()` (trains all 3 sequentially)

### 4.4 Status Bar — Algorithm Name

**File**: `src/gui.py` (within `_status_bar()` method, ~2 lines changed)

- Add current algorithm name to the mode string:
  ```
  "Mode: TRAINING [Q-Learning]" or "Mode: EDIT [Bellman]"
  ```
- Read algorithm name from `self.agent.algorithm_name` (all agents expose this property)

### 4.5 Dashboard — Alpha and Algorithm Display

**File**: `src/dashboard.py` (after PRD 2: ~150 lines)

- Show algorithm name in metrics panel: `"Algorithm: Double Q-Learning"`
- Show alpha value when applicable: `"Alpha: 0.2345"`
- These are included in the metrics dict from GameLogic/SDK

Note: Dashboard is at the 150-line limit. To add these metrics, compress existing rendering code or extract the legend into a helper. The `_draw_metrics()` method can conditionally render alpha only when the `"alpha"` key is present in the metrics dict, adding ~3 lines.

### 4.6 Shortcuts Bar Update

**File**: `src/gui.py` (within `_status_bar()`, ~1 line changed)

- Update shortcuts string to include: `"1/2/3 Algorithm  C Compare"`

---

## Phase 5: Testing and Verification

### 5.1 Full Test Suite

Run `uv run pytest` — all existing 104 tests plus all new tests from PRDs 2 and 3 must pass.

Expected new test files and counts:

| Test File | Tests | Lines |
|-----------|-------|-------|
| `tests/test_double_q_agent.py` | ~16 | ~130 |
| `tests/test_comparison.py` | ~11 | ~100 |
| `tests/test_sdk.py` (additions) | ~7 | +25 |

### 5.2 Coverage Check

Run `uv run pytest --cov=src --cov-report=html`:
- `src/double_q_agent.py` — 85%+
- `src/comparison.py` — 85%+

### 5.3 Lint Check

Run `uv run ruff check src/ tests/` — zero violations.

### 5.4 Manual Verification

- Train Bellman on static grid, verify convergence
- Train Q-Learning on noisy grid (difficulty 0.5), compare with Bellman
- Train Double Q on very noisy grid (difficulty 1.0), verify it converges
- Run full comparison, verify chart is generated and shows 3 distinct curves
- Switch algorithms with 1/2/3 keys, verify status bar updates
- Press C to run comparison, verify chart opens/saves

---

## File Size Constraint

Every `.py` file must stay under **150 lines**. Estimated final line counts:

| File | Current | After Changes | Status |
|------|---------|---------------|--------|
| `src/double_q_agent.py` | 0 (new) | ~95 | OK |
| `src/comparison.py` | 0 (new) | ~120 | OK |
| `src/sdk.py` | ~100 (post PRD 2) | ~130 | OK |
| `src/gui.py` | ~132 (post PRD 2) | ~140 | OK |
| `src/actions.py` | ~58 (post PRD 2) | ~80 | OK |
| `src/buttons.py` | 135 | ~150 | At limit |
| `src/dashboard.py` | ~150 (post PRD 2) | ~150 | At limit |
| `src/agent_factory.py` | ~30 (from PRD 2) | ~30 | OK (no changes) |
| `tests/test_double_q_agent.py` | 0 (new) | ~130 | OK |
| `tests/test_comparison.py` | 0 (new) | ~100 | OK |

**Risk mitigation**:
- If `buttons.py` exceeds 150 lines after adding algorithm selector buttons, extract the `_get_buttons()` helper into a separate `src/button_config.py` module.
- If `actions.py` exceeds 150 lines, split algorithm-related actions into `src/algo_actions.py`.
- If `dashboard.py` cannot fit alpha display within 150 lines, extract the legend rendering into `src/legend.py`.

---

## Dependency Order

This PRD depends on PRD 2 (Q-Learning) being completed first:

1. **PRD 2 must be done** — BaseAgent, BellmanAgent, QLearningAgent, agent_factory must exist
2. **PRD 1 (Dynamic Board) is independent** — Can be done in parallel with PRD 2
3. **This PRD (Double Q) comes last** — Builds on the agent hierarchy from PRD 2 and benefits from the dynamic board from PRD 1 for meaningful comparisons

Recommended implementation order: PRD 1 and PRD 2 in parallel, then PRD 3.
