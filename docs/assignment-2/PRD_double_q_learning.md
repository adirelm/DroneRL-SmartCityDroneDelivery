# Product Requirements Document (PRD)

## Double Q-Learning Algorithm — Bias-Corrected Dual-Table Learning

---

## 1. Project Overview & Background

This PRD introduces the **Double Q-Learning algorithm** as the third and most advanced RL agent in the DroneRL project. Double Q-Learning addresses the **overestimation bias** inherent in standard Q-Learning by maintaining two separate Q-tables and using one to select actions while the other evaluates them.

### Context

Standard Q-Learning (and Bellman) uses a single Q-table and computes `max(Q(s',a'))` for the TD target. This introduces a **maximization bias**: the same table that selects the best action also evaluates it, systematically overestimating Q-values — especially in noisy environments where random high values get reinforced.

**Double Q-Learning** (Hasselt, 2010) solves this by maintaining two independent Q-tables (QA and QB). On each update:
1. Randomly choose which table to update (50/50 split)
2. If updating QA: find the best action using QA, but evaluate it using QB
3. If updating QB: find the best action using QB, but evaluate it using QA

This **decouples action selection from evaluation**, eliminating the overestimation bias.

### Mathematical Formulation

With probability 0.5, update QA:
```
a* = argmax_a QA(s', a)
QA(s,a) = QA(s,a) + α * [r + γ * QB(s', a*) - QA(s,a)]
```

With probability 0.5, update QB:
```
a* = argmax_a QB(s', a)
QB(s,a) = QB(s,a) + α * [r + γ * QA(s', a*) - QB(s,a)]
```

For action selection (epsilon-greedy), use the combined table: `QA + QB`.

### Existing Codebase Reference

- `src/dronerl/base_agent.py` — BaseAgent abstract class (created in PRD_q_learning)
- `src/dronerl/q_agent.py` — QLearningAgent with decaying alpha (created in PRD_q_learning)
- `src/dronerl/agent_factory.py` — Agent factory (created in PRD_q_learning)
- `src/dronerl/overlays.py` — Reads `agent.q_table` for heatmap and arrows
- `src/dronerl/comparison.py` — Comparison system (to be created)

---

## 2. Objectives & Success Metrics

### Objectives

1. **Double Q-Learning Agent**: Implement `DoubleQAgent(BaseAgent)` with two Q-tables (QA, QB).
2. **Overestimation Prevention**: Cross-table evaluation eliminates maximization bias.
3. **Comparison System**: Store training results for all three algorithms and generate comparison charts.
4. **Algorithm Switching**: GUI allows selecting between Bellman, Q-Learning, and Double Q-Learning.
5. **Visual Proof**: Convergence graphs clearly show Double Q-Learning's advantage in noisy environments.

### Success Metrics

| Metric | Target |
|--------|--------|
| Two Q-tables initialized to zeros | Verified by test |
| Each update modifies exactly one table | Verified by test |
| Cross-table evaluation (argmax from one, value from other) | Verified by test |
| `q_table` property returns QA + QB | Verified by test |
| Double Q converges in scenarios where Q-Learning fails | Visual comparison |
| Comparison chart shows 3 distinct convergence curves | Generated PNG |
| All files ≤ 150 lines | Verified by wc -l |
| 85%+ test coverage | pytest-cov verified |

### KPIs

- On noisy grid (difficulty 0.5): Double Q-Learning converges 10-20% faster than Q-Learning
- On very noisy grid (difficulty 1.0): Double Q-Learning converges while Q-Learning oscillates
- Q-value overestimation: Double Q produces lower max Q-values than single Q on same grid

---

## 3. Functional Requirements

### 3.1 DoubleQAgent Class

A new file `src/dronerl/double_q_agent.py` containing `DoubleQAgent(BaseAgent)`:

#### Initialization

```python
self.q_table_a = np.zeros((rows, cols, NUM_ACTIONS))
self.q_table_b = np.zeros((rows, cols, NUM_ACTIONS))
```

#### Update Rule

```python
def update(self, state, action, reward, next_state, done):
    r, c = state
    if random.random() < 0.5:
        # Update QA using QB for evaluation
        best_a = int(np.argmax(self.q_table_a[next_state[0], next_state[1]]))
        next_val = 0.0 if done else self.q_table_b[next_state[0], next_state[1], best_a]
        target = reward + self.gamma * next_val
        self.q_table_a[r, c, action] += self.alpha * (target - self.q_table_a[r, c, action])
    else:
        # Update QB using QA for evaluation
        best_a = int(np.argmax(self.q_table_b[next_state[0], next_state[1]]))
        next_val = 0.0 if done else self.q_table_a[next_state[0], next_state[1], best_a]
        target = reward + self.gamma * next_val
        self.q_table_b[r, c, action] += self.alpha * (target - self.q_table_b[r, c, action])
```

#### Properties

| Property | Description |
|----------|-------------|
| `q_table` | Returns `self.q_table_a + self.q_table_b` — used by GUI overlays (heatmap, arrows) |
| `algorithm_name` | Returns `"Double Q-Learning"` |

#### Action Selection

- `get_best_action(state)`: Uses combined table `q_table_a + q_table_b` for argmax
- `get_max_q(state)`: Uses combined table for max value
- `choose_action(state)`: Epsilon-greedy using combined table

#### Alpha Decay

Same as QLearningAgent — decaying alpha per episode:
```python
self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)
```

#### Save/Load

- `save(path)`: Saves both tables: `{path}_a.npy` and `{path}_b.npy`
- `load(path)`: Loads both tables from the two files

### 3.2 Comparison System

A new file `src/dronerl/comparison.py`:

#### ComparisonStore Class

```python
class ComparisonStore:
    def __init__(self):
        self.results = {}  # algorithm_name -> {reward_history, metrics, episodes}

    def store(self, name, reward_history, metrics):
        """Store training results for one algorithm."""

    def has_results(self, name) -> bool:
        """Check if results exist for a specific algorithm."""

    def has_all(self) -> bool:
        """Check if all 3 algorithms have results."""

    def get_histories(self) -> dict[str, list[float]]:
        """Return reward histories keyed by algorithm name."""

    def clear(self):
        """Clear all stored results."""
```

#### Chart Generation

```python
def generate_comparison_chart(store: ComparisonStore, output_path: str, config: Config):
    """Generate matplotlib chart comparing convergence curves."""
    # Creates a figure with:
    # - 3 smoothed reward curves (moving average over 50 episodes)
    # - Color-coded: Bellman (orange), Q-Learning (green), Double Q (blue)
    # - Legend, axis labels, title
    # - Grid lines for readability
    # Saves as PNG to output_path
```

#### Configuration

```yaml
# Comparison settings
comparison:
  max_episodes: 5000
  output_dir: results/comparison
  smoothing_window: 50

# Algorithm curve colors
colors:
  algo_bellman: [255, 160, 40]
  algo_q_learning: [80, 200, 120]
  algo_double_q: [100, 140, 255]
```

### 3.3 SDK Extensions

Modifications to `src/dronerl/sdk.py`:

| Method | Description |
|--------|-------------|
| `switch_algorithm(name)` | Create new agent via factory, reset trainer, preserve environment |
| `run_comparison(episodes)` | Train all 3 algorithms sequentially, store results in ComparisonStore |
| `get_comparison_store()` | Return the ComparisonStore instance |
| `generate_comparison_chart()` | Generate and save the matplotlib comparison chart |

### 3.4 GUI Integration

#### Algorithm Selector (in dashboard buttons)

Three toggle buttons: **Bellman** / **Q-Learning** / **Double Q**
- Active algorithm is highlighted
- Switching triggers `sdk.switch_algorithm(name)` — new agent, reset training, same board
- Current algorithm name shown in status bar

#### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Select Bellman algorithm |
| `2` | Select Q-Learning algorithm |
| `3` | Select Double Q-Learning algorithm |
| `C` | Run comparison (train all 3) or show comparison chart |

#### Compare All Button

- Visible after at least one algorithm has been trained
- Trains all 3 algorithms for `comparison.max_episodes` episodes each
- Shows progress in dashboard
- On completion, opens matplotlib comparison chart
- Saves chart to `results/comparison/comparison.png`

### 3.5 Dashboard Extensions

- Show current algorithm name in metrics panel (e.g., "Algorithm: Double Q-Learning")
- Show alpha value when using Q-Learning or Double Q (e.g., "Alpha: 0.2345")

---

## 4. Non-Functional Requirements

- **GUI Compatibility**: `agent.q_table` property must return a valid 3D NumPy array for all agent types — overlays read this directly
- **Performance**: Double Q update is at most 2x slower than single Q (two table lookups)
- **Memory**: Two Q-tables for 12x12x4 = 1,152 floats total = ~9KB — negligible
- **File Sizes**: `double_q_agent.py` ≤ 150, `comparison.py` ≤ 150
- **Test Coverage**: 85%+ for all new code
- **Zero ruff violations**
- **Config-Driven**: All hyperparameters and colors from config.yaml

---

## 5. User Stories

1. **As a student**, I want to train a Double Q-Learning agent to see how it handles noisy environments better than Q-Learning.
2. **As a student**, I want to compare all three algorithms side-by-side in a convergence graph.
3. **As a student**, I want to switch between algorithms quickly using keyboard shortcuts.
4. **As a student**, I want to see the alpha value in the dashboard to understand when the agent stops learning aggressively.
5. **As a student**, I want the comparison chart saved as a PNG so I can include it in my README.

---

## 6. Assumptions & Constraints

- The combined Q-table (QA + QB) is used for action selection and GUI visualization
- Alpha decay parameters are shared between Q-Learning and Double Q-Learning (from `q_learning` and `double_q` config sections respectively)
- Comparison trains algorithms sequentially (not in parallel) to avoid memory/performance issues
- The comparison chart uses matplotlib (already a project dependency)
- The chart is saved to `results/comparison/` directory

---

## 7. Acceptance Criteria

- [ ] `DoubleQAgent` initializes two Q-tables (QA, QB) to zeros
- [ ] Each `update()` call modifies exactly one table (not both)
- [ ] Cross-table evaluation works: argmax from updating table, value from other table
- [ ] `q_table` property returns `QA + QB`
- [ ] `get_best_action` uses combined table
- [ ] Alpha decays per episode, clamped to `alpha_end`
- [ ] `save()` creates two .npy files, `load()` restores both
- [ ] `ComparisonStore` stores and retrieves results for all 3 algorithms
- [ ] `generate_comparison_chart()` creates a PNG with 3 curves
- [ ] SDK `switch_algorithm()` creates new agent and resets trainer
- [ ] SDK `run_comparison()` trains all 3 sequentially
- [ ] GUI shows algorithm name in status bar
- [ ] Keys `1/2/3` switch algorithms, `C` triggers comparison
- [ ] Comparison chart clearly shows convergence differences
- [ ] **Scenario 1 (Medium)**: difficulty=0.5 — Bellman struggles, Q converges, Double Q fastest
- [ ] **Scenario 2 (Hard)**: difficulty=0.9 — Bellman fails, Q fails, Double Q converges
- [ ] Both scenario charts saved as PNG in `results/comparison/`
- [ ] CLAUDE.md exists in project root with global constraints
- [ ] All work in same repository as assignment 1 (branch `assignment-2`)
- [ ] All files ≤ 150 lines
- [ ] 85%+ test coverage on all new code
- [ ] Zero ruff violations
- [ ] **README includes**: objectives, algorithm descriptions, comparison graphs, parameter analysis, conclusions
- [ ] README includes screenshots of the application in different modes
- [ ] README includes embedded comparison chart images

---

## 9. Comparison Scenarios (Required by Lecturer)

### Scenario 1: Medium Difficulty — Bellman Fails, Q and Double Q Succeed
- **Config**: difficulty=0.5, obstacle_density=0.2, noise_level=0.5, max_episodes=5000
- **Expected**: Bellman fails (oscillates/low reward), Q-Learning converges, Double Q converges fastest
- **Output**: `results/comparison/scenario1_medium.png`

### Scenario 2: High Difficulty — Only Double Q Succeeds
- **Config**: difficulty=0.9, obstacle_density=0.35, noise_level=0.8, max_episodes=10000
- **Expected**: Bellman fails (diverges), Q-Learning fails (oscillates), Double Q converges reliably
- **Output**: `results/comparison/scenario2_hard.png`

Both charts must use:
- Consistent axis scales, moving average smoothing (50 episodes)
- Color-coded curves: Bellman (orange), Q-Learning (green), Double Q (blue)
- Legend, title, axis labels

---

## 10. README Requirements (Impressive README)

The README must include:
1. **Objectives** — What this project teaches about RL algorithm comparison
2. **Algorithm Descriptions** — Bellman, Q-Learning, Double Q-Learning with formulas
3. **What is Overestimation Bias** — Why Double Q-Learning exists
4. **Why Alpha Must Decay** — Stability in noisy environments
5. **Comparison Graphs** — Embedded scenario1 and scenario2 PNG images
6. **Parameter Analysis** — Table showing how noise/density/difficulty affect each algorithm
7. **Conclusions** — Which algorithm works best and when
8. **Screenshots** — Application in training, heatmap, comparison, editor modes

---

## 11. Timeline & Milestones

| Phase | Deliverable |
|-------|------------|
| 1 | Create `src/dronerl/double_q_agent.py` with two Q-tables and cross-table update |
| 2 | Add `double_q` section to config.yaml |
| 3 | Register in agent factory |
| 4 | Write comprehensive tests |
| 5 | Create `src/dronerl/comparison.py` with store + chart generation |
| 6 | Extend SDK with comparison and algorithm switching |
| 7 | Add algorithm selector buttons and keyboard shortcuts to GUI |
| 8 | Generate comparison scenarios and tune parameters |
| 9 | Save comparison charts, embed in README |

---

## Alternatives Considered

The chosen design (Hasselt-2010 Double Q-Learning with `QA + QB`
combined into a virtual `q_table` property for GUI compatibility) was
selected from several alternatives.

| Alternative | Rejected because |
|-------------|------------------|
| **Skip Double-Q entirely; deliver only Q-Learning** | The assignment brief explicitly names *both* Q-Learning *and* Double Q-Learning as required deliverables (lecture transcript: *"PRD של Double Q-Learning, זה שהיא עם ה-QA ועם ה-QB"*). Not delivering would lose grade. |
| **Two completely independent agents (one for QA, one for QB)** | Would double the I/O (two separate Q-tables in the GUI), break the heatmap which expects a single Q-array, and require a separate save/load path. The chosen approach — one `DoubleQAgent` owning both tables internally — keeps the GUI contract identical to the other agents. |
| **Average `(QA + QB) / 2` for the `q_table` property** | Smaller magnitudes, slightly muddier policy arrows. Sum (`QA + QB`) preserves the action-ranking that arg-max depends on without a divisor that shrinks the heatmap dynamic range. |
| **Always use the same table for argmax and value (which is just Q-Learning again)** | Defeats the entire bias-correction purpose — Hasselt's whole point is decorrelating action selection (one table) from value evaluation (the other). The "flip a coin → update one table using the other's value at the chosen argmax" mechanism is the core algorithm. |
| **Twin networks (TD3-style) generalising Double-Q to deep RL** | Out-of-scope for tabular. Useful future direction (see [EXPERIMENTS.md](EXPERIMENTS.md) "What I'd do next"), but the assignment is tabular. |
| **Defer baseline comparison to the next assignment** | The assignment-2 spec requires showing convergence speed AND final values for *all three* algorithms (transcript: *"בעל הזה צריכים להראות את המהירות התכנסות של כל אחד מהם ולאיזה ערכים הגעתם"*). The comparison must ship now. |
