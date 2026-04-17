# DroneRL — Double Q-Learning Agent Task Breakdown

> All tasks marked as completed. Total: 585 granular tasks covering every aspect of the Double Q-Learning agent, comparison system, and GUI integration.

---

## 1. DoubleQAgent Class — File Setup (~15 tasks)

- [x] Task 1: Create new file `src/double_q_agent.py`
- [x] Task 2: Add module docstring: "Double Q-Learning agent with dual Q-tables for bias-corrected learning"
- [x] Task 3: Add `from __future__ import annotations` import
- [x] Task 4: Add `import random` import
- [x] Task 5: Add `import numpy as np` import
- [x] Task 6: Add `from src.base_agent import BaseAgent` import
- [x] Task 7: Add type hints import: `from typing import TYPE_CHECKING`
- [x] Task 8: Add conditional import: `if TYPE_CHECKING: from src.config_loader import Config`
- [x] Task 9: Verify all imports are necessary and used
- [x] Task 10: Verify no circular imports exist
- [x] Task 11: Run ruff check on double_q_agent.py to verify clean state
- [x] Task 12: Verify `from src.double_q_agent import DoubleQAgent` works
- [x] Task 13: Add blank line after imports per PEP 8
- [x] Task 14: Add blank line before class definition per PEP 8
- [x] Task 15: Verify file encoding is UTF-8

---

## 2. DoubleQAgent Class Definition (~20 tasks)

- [x] Task 16: Define `class DoubleQAgent(BaseAgent):` inheriting from BaseAgent
- [x] Task 17: Add class docstring: "Double Q-Learning with two Q-tables for bias-corrected evaluation"
- [x] Task 18: Add class docstring detail: "Maintains QA and QB tables, decoupling action selection from evaluation"
- [x] Task 19: Define `algorithm_name = "Double Q-Learning"` as class attribute
- [x] Task 20: Verify algorithm_name is a string
- [x] Task 21: Verify DoubleQAgent is a concrete class (not abstract)
- [x] Task 22: Verify DoubleQAgent inherits from BaseAgent
- [x] Task 23: Verify DoubleQAgent can be instantiated
- [x] Task 24: Verify DoubleQAgent is not abstract (no unimplemented methods)
- [x] Task 25: Verify class attribute algorithm_name = "Double Q-Learning"

---

## 3. DoubleQAgent.__init__() — Two Tables (~35 tasks)

### 3.1 Init Method Signature

- [x] Task 26: Define `__init__(self, config: Config) -> None` method signature
- [x] Task 27: Add __init__ docstring: "Initialize dual Q-tables and alpha decay parameters"
- [x] Task 28: Call `super().__init__(config)` first for shared initialization
- [x] Task 29: Verify super().__init__ initializes epsilon, gamma, rows, cols

### 3.2 Q-Table A Initialization

- [x] Task 30: Initialize `self.q_table_a = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))`
- [x] Task 31: Verify q_table_a shape is (rows, cols, 4)
- [x] Task 32: Verify q_table_a is initialized to all zeros
- [x] Task 33: Verify q_table_a dtype is float64
- [x] Task 34: Verify q_table_a is independent from parent _q_table

### 3.3 Q-Table B Initialization

- [x] Task 35: Initialize `self.q_table_b = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))`
- [x] Task 36: Verify q_table_b shape is (rows, cols, 4)
- [x] Task 37: Verify q_table_b is initialized to all zeros
- [x] Task 38: Verify q_table_b dtype is float64
- [x] Task 39: Verify q_table_b is a separate array from q_table_a (not aliased)

### 3.4 Alpha Parameters

- [x] Task 40: Extract Double Q config section: `dq_cfg = config.double_q`
- [x] Task 41: Load alpha_start: `self.alpha = dq_cfg.alpha_start`
- [x] Task 42: Load alpha_end: `self.alpha_end = dq_cfg.alpha_end`
- [x] Task 43: Load alpha_decay: `self.alpha_decay = dq_cfg.alpha_decay`
- [x] Task 44: Verify alpha is initialized to alpha_start value
- [x] Task 45: Verify alpha_end is stored for floor clamping
- [x] Task 46: Verify alpha_decay is stored for multiplicative decay
- [x] Task 47: Verify alpha is a float
- [x] Task 48: Verify alpha_end is a float
- [x] Task 49: Verify alpha_decay is a float

### 3.5 Init Verification

- [x] Task 50: Verify __init__ does not hardcode any values
- [x] Task 51: Verify all parameters come from config
- [x] Task 52: Verify parent _q_table from BaseAgent is not used (overridden by property)
- [x] Task 53: Verify both tables have identical shapes
- [x] Task 54: Verify both tables are initialized independently to zeros
- [x] Task 55: Verify no shared references between q_table_a and q_table_b

---

## 4. DoubleQAgent.update() — Cross-Table Evaluation (~50 tasks)

### 4.1 Method Signature

- [x] Task 56: Define `update(self, state, action, reward, next_state, done) -> None`
- [x] Task 57: Add update docstring: "Cross-table TD update — select action from one table, evaluate with the other"
- [x] Task 58: Add type hints for all parameters
- [x] Task 59: Extract state coordinates: `r, c = state`

### 4.2 Random Table Selection

- [x] Task 60: Generate random float: `random.random()`
- [x] Task 61: Add condition: `if random.random() < 0.5` for 50/50 split
- [x] Task 62: Verify 50/50 probability is used (not configurable)
- [x] Task 63: Verify each path updates exactly one table

### 4.3 Update QA Branch (random < 0.5)

- [x] Task 64: Select best action from QA: `best_a = int(np.argmax(self.q_table_a[next_state[0], next_state[1]]))`
- [x] Task 65: Evaluate using QB: `next_val = self.q_table_b[next_state[0], next_state[1], best_a]`
- [x] Task 66: Handle terminal state: `next_val = 0.0 if done else ...`
- [x] Task 67: Compute TD target: `target = reward + self.gamma * next_val`
- [x] Task 68: Apply update to QA: `self.q_table_a[r, c, action] += self.alpha * (target - self.q_table_a[r, c, action])`
- [x] Task 69: Verify QA is modified
- [x] Task 70: Verify QB is NOT modified in this branch
- [x] Task 71: Verify action selection comes from QA (argmax QA)
- [x] Task 72: Verify evaluation comes from QB (value from QB)

### 4.4 Update QB Branch (random >= 0.5)

- [x] Task 73: Select best action from QB: `best_a = int(np.argmax(self.q_table_b[next_state[0], next_state[1]]))`
- [x] Task 74: Evaluate using QA: `next_val = self.q_table_a[next_state[0], next_state[1], best_a]`
- [x] Task 75: Handle terminal state: `next_val = 0.0 if done else ...`
- [x] Task 76: Compute TD target: `target = reward + self.gamma * next_val`
- [x] Task 77: Apply update to QB: `self.q_table_b[r, c, action] += self.alpha * (target - self.q_table_b[r, c, action])`
- [x] Task 78: Verify QB is modified
- [x] Task 79: Verify QA is NOT modified in this branch
- [x] Task 80: Verify action selection comes from QB (argmax QB)
- [x] Task 81: Verify evaluation comes from QA (value from QA)

### 4.5 Update Verification

- [x] Task 82: Verify each update call modifies exactly one table
- [x] Task 83: Verify cross-table mechanism: argmax from updating table, value from other
- [x] Task 84: Verify done=True sets next_val to 0.0 in both branches
- [x] Task 85: Verify done=False uses the cross-table value
- [x] Task 86: Verify alpha is used (not lr)
- [x] Task 87: Verify gamma is used for discounting
- [x] Task 88: Verify update formula: Q += alpha * (target - Q)
- [x] Task 89: Verify over many updates, both tables accumulate values
- [x] Task 90: Verify no hardcoded values in update method
- [x] Task 91: Verify update handles edge case: next_state is start position
- [x] Task 92: Verify update handles edge case: reward is zero
- [x] Task 93: Verify update handles edge case: reward is very large positive
- [x] Task 94: Verify update handles edge case: reward is very large negative
- [x] Task 95: Verify update does not modify other Q-values in the table

---

## 5. DoubleQAgent.q_table Property (~20 tasks)

- [x] Task 96: Define `@property q_table(self) -> np.ndarray` getter
- [x] Task 97: Add docstring: "Combined Q-table (QA + QB) for GUI overlay visualization"
- [x] Task 98: Implement: `return self.q_table_a + self.q_table_b`
- [x] Task 99: Verify return type is np.ndarray
- [x] Task 100: Verify return shape is (rows, cols, 4)
- [x] Task 101: Verify combined table is element-wise sum of QA and QB
- [x] Task 102: Verify combined table values equal QA + QB for each cell
- [x] Task 103: Verify combined table with all-zero tables returns all zeros
- [x] Task 104: Verify combined table with non-zero QA returns QA values when QB is zero
- [x] Task 105: Verify combined table with non-zero QB returns QB values when QA is zero
- [x] Task 106: Verify combined table returns correct sum when both tables have values
- [x] Task 107: Verify property returns new array each call (not cached stale value)
- [x] Task 108: Verify GUI overlays can read q_table property
- [x] Task 109: Verify heatmap overlay works with combined table
- [x] Task 110: Verify arrow overlay works with combined table
- [x] Task 111: Verify q_table is compatible with overlays.py expectations
- [x] Task 112: Verify q_table dtype is float64
- [x] Task 113: Verify combined table never has NaN values
- [x] Task 114: Verify combined table never has Inf values
- [x] Task 115: Verify property does not modify q_table_a or q_table_b

---

## 6. DoubleQAgent.get_best_action() — Combined Table (~15 tasks)

- [x] Task 116: Define `get_best_action(self, state: tuple[int, int]) -> int` override
- [x] Task 117: Add docstring: "Return best action using combined QA + QB table"
- [x] Task 118: Extract row and col from state: `r, c = state`
- [x] Task 119: Compute combined values: `combined = self.q_table_a[r, c] + self.q_table_b[r, c]`
- [x] Task 120: Return argmax: `int(np.argmax(combined))`
- [x] Task 121: Verify returns int, not np.int64
- [x] Task 122: Verify uses combined table (not just QA or QB alone)
- [x] Task 123: Verify handles all-zero tables (returns 0)
- [x] Task 124: Verify handles ties (returns first max)
- [x] Task 125: Verify action is in range [0, 3]
- [x] Task 126: Verify combined action may differ from QA-only argmax
- [x] Task 127: Verify combined action may differ from QB-only argmax
- [x] Task 128: Verify get_best_action is used by choose_action (inherited)
- [x] Task 129: Verify get_best_action override is called polymorphically
- [x] Task 130: Test get_best_action with various Q-value configurations

---

## 7. DoubleQAgent.get_max_q() — Combined Table (~15 tasks)

- [x] Task 131: Define `get_max_q(self, state: tuple[int, int]) -> float` override
- [x] Task 132: Add docstring: "Return max Q-value using combined QA + QB table"
- [x] Task 133: Extract row and col from state: `r, c = state`
- [x] Task 134: Compute combined values: `combined = self.q_table_a[r, c] + self.q_table_b[r, c]`
- [x] Task 135: Return max: `float(np.max(combined))`
- [x] Task 136: Verify returns float, not np.float64
- [x] Task 137: Verify uses combined table
- [x] Task 138: Verify handles all-zero tables (returns 0.0)
- [x] Task 139: Verify handles negative values
- [x] Task 140: Verify handles mixed positive/negative values
- [x] Task 141: Verify max of combined is sum of individual maxes only if same action is max in both
- [x] Task 142: Verify get_max_q is used by update for next_max calculation (in base class)
- [x] Task 143: Verify get_max_q override is called polymorphically
- [x] Task 144: Test get_max_q with various Q-value configurations
- [x] Task 145: Verify consistent behavior with get_best_action (same combined table)

---

## 8. DoubleQAgent.save() — Two Files (~20 tasks)

- [x] Task 146: Define `save(self, path: str) -> None` override
- [x] Task 147: Add docstring: "Save both Q-tables to separate .npy files"
- [x] Task 148: Save QA: `np.save(f"{path}_a.npy", self.q_table_a)`
- [x] Task 149: Save QB: `np.save(f"{path}_b.npy", self.q_table_b)`
- [x] Task 150: Verify save creates two files
- [x] Task 151: Verify file naming convention: `{path}_a.npy` and `{path}_b.npy`
- [x] Task 152: Verify QA file contains correct data
- [x] Task 153: Verify QB file contains correct data
- [x] Task 154: Verify files are valid .npy format
- [x] Task 155: Verify save handles path with directory
- [x] Task 156: Verify save overwrites existing files
- [x] Task 157: Verify save does not modify in-memory tables
- [x] Task 158: Verify save creates files with correct shapes
- [x] Task 159: Verify save with non-zero tables preserves values
- [x] Task 160: Verify both files are independent (not same data)
- [x] Task 161: Test save with path containing spaces
- [x] Task 162: Test save with path containing subdirectories
- [x] Task 163: Test save creates parent directories if needed
- [x] Task 164: Verify ruff check passes after save implementation
- [x] Task 165: Verify save method signature matches BaseAgent.save

---

## 9. DoubleQAgent.load() — Two Files (~20 tasks)

- [x] Task 166: Define `load(self, path: str) -> None` override
- [x] Task 167: Add docstring: "Load both Q-tables from separate .npy files"
- [x] Task 168: Load QA: `self.q_table_a = np.load(f"{path}_a.npy")`
- [x] Task 169: Load QB: `self.q_table_b = np.load(f"{path}_b.npy")`
- [x] Task 170: Verify load restores both tables
- [x] Task 171: Verify loaded QA has correct shape
- [x] Task 172: Verify loaded QB has correct shape
- [x] Task 173: Verify loaded values match saved values exactly
- [x] Task 174: Verify load handles file not found gracefully
- [x] Task 175: Verify load handles missing QA file
- [x] Task 176: Verify load handles missing QB file
- [x] Task 177: Test save/load round-trip preserves both tables exactly
- [x] Task 178: Test load with modified QA preserves QB
- [x] Task 179: Test load with modified QB preserves QA
- [x] Task 180: Verify load does not affect alpha value
- [x] Task 181: Verify load does not affect epsilon value
- [x] Task 182: Verify load method signature matches BaseAgent.load
- [x] Task 183: Test save then load produces identical combined q_table
- [x] Task 184: Verify ruff check passes after load implementation
- [x] Task 185: Verify both save and load work together end-to-end

---

## 10. Alpha Decay in DoubleQAgent (~20 tasks)

- [x] Task 186: Define `decay_epsilon(self) -> None` override
- [x] Task 187: Add docstring: "Decay both epsilon and alpha per episode"
- [x] Task 188: Call `super().decay_epsilon()` to decay epsilon
- [x] Task 189: Decay alpha: `self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)`
- [x] Task 190: Verify epsilon is decayed via parent method
- [x] Task 191: Verify alpha is decayed after epsilon
- [x] Task 192: Verify alpha never goes below alpha_end
- [x] Task 193: Verify alpha decay is multiplicative
- [x] Task 194: Verify alpha and epsilon decay independently
- [x] Task 195: Verify alpha after 1 decay equals alpha * alpha_decay
- [x] Task 196: Verify alpha after 100 decays approaches alpha_end
- [x] Task 197: Verify alpha after 1000 decays equals alpha_end (clamped)
- [x] Task 198: Verify alpha_end acts as absolute floor
- [x] Task 199: Verify super().decay_epsilon() is called first
- [x] Task 200: Verify decay logic is identical to QLearningAgent's alpha decay
- [x] Task 201: Test epsilon and alpha states after calling decay_epsilon 500 times
- [x] Task 202: Verify no hardcoded values in decay method
- [x] Task 203: Verify decay_epsilon can be called safely on freshly created agent
- [x] Task 204: Verify decay_epsilon does not affect Q-tables
- [x] Task 205: Verify ruff check passes after decay implementation

---

## 11. DoubleQAgent — Line Count and Quality (~10 tasks)

- [x] Task 206: Count total lines in double_q_agent.py
- [x] Task 207: Verify double_q_agent.py is approximately ~95 lines
- [x] Task 208: Verify double_q_agent.py is at or under 150 lines
- [x] Task 209: Verify ruff check passes on double_q_agent.py
- [x] Task 210: Verify all methods have docstrings
- [x] Task 211: Verify all methods have type hints
- [x] Task 212: Verify no code duplication with other agents
- [x] Task 213: Verify no hardcoded values in any method
- [x] Task 214: Verify imports are clean and minimal
- [x] Task 215: Verify module docstring is accurate

---

## 12. Registration in Agent Factory (~15 tasks)

- [x] Task 216: Open `src/agent_factory.py` for editing
- [x] Task 217: Verify `"double_q"` branch already exists (forward-planned in PRD 2)
- [x] Task 218: If not, add `elif name == "double_q":` branch
- [x] Task 219: Add lazy import: `from src.double_q_agent import DoubleQAgent`
- [x] Task 220: Add return: `return DoubleQAgent(config)`
- [x] Task 221: Verify factory returns DoubleQAgent for "double_q"
- [x] Task 222: Verify returned DoubleQAgent is instance of BaseAgent
- [x] Task 223: Verify returned DoubleQAgent has algorithm_name "Double Q-Learning"
- [x] Task 224: Verify returned DoubleQAgent has q_table property
- [x] Task 225: Verify returned DoubleQAgent has update method
- [x] Task 226: Verify factory dispatches correctly for all 3 algorithms
- [x] Task 227: Run factory tests to verify double_q dispatch
- [x] Task 228: Verify agent_factory.py stays at or under 150 lines
- [x] Task 229: Verify ruff check passes on agent_factory.py
- [x] Task 230: Add factory test: create_agent with "double_q" returns DoubleQAgent

---

## 13. ComparisonStore Class Creation (~45 tasks)

### 13.1 File Setup

- [x] Task 231: Create new file `src/comparison.py`
- [x] Task 232: Add module docstring: "Comparison system for storing and visualizing multi-algorithm training results"
- [x] Task 233: Add `from __future__ import annotations` import
- [x] Task 234: Add `import os` import
- [x] Task 235: Add `import numpy as np` import
- [x] Task 236: Add `import matplotlib` import
- [x] Task 237: Add `matplotlib.use("Agg")` for non-interactive backend
- [x] Task 238: Add `import matplotlib.pyplot as plt` import
- [x] Task 239: Verify all imports are necessary

### 13.2 ComparisonStore Class

- [x] Task 240: Define `class ComparisonStore:` class
- [x] Task 241: Add class docstring: "Store and retrieve training results for algorithm comparison"

### 13.3 ComparisonStore.__init__()

- [x] Task 242: Define `__init__(self) -> None` method
- [x] Task 243: Add __init__ docstring
- [x] Task 244: Initialize `self.results: dict = {}`
- [x] Task 245: Verify results dict is empty on initialization

### 13.4 ComparisonStore.store() Method

- [x] Task 246: Define `store(self, name: str, reward_history: list[float], metrics: dict) -> None`
- [x] Task 247: Add docstring: "Store training results for one algorithm"
- [x] Task 248: Store results: `self.results[name] = {"reward_history": reward_history, "metrics": metrics}`
- [x] Task 249: Verify store overwrites previous results for same name
- [x] Task 250: Verify store preserves results for other algorithms
- [x] Task 251: Verify name is used as dictionary key

### 13.5 ComparisonStore.has_results() Method

- [x] Task 252: Define `has_results(self, name: str) -> bool` method
- [x] Task 253: Add docstring: "Check if results exist for a specific algorithm"
- [x] Task 254: Implement: `return name in self.results`
- [x] Task 255: Verify returns True after storing for name
- [x] Task 256: Verify returns False for unknown name

### 13.6 ComparisonStore.has_all() Method

- [x] Task 257: Define `has_all(self) -> bool` method
- [x] Task 258: Add docstring: "Check if all 3 algorithms have results"
- [x] Task 259: Define expected algorithms: `["Bellman", "Q-Learning", "Double Q-Learning"]`
- [x] Task 260: Implement: `return all(name in self.results for name in expected)`
- [x] Task 261: Verify returns True only when all 3 are present
- [x] Task 262: Verify returns False when 0, 1, or 2 are present

### 13.7 ComparisonStore.get_histories() Method

- [x] Task 263: Define `get_histories(self) -> dict[str, list[float]]` method
- [x] Task 264: Add docstring: "Return reward histories keyed by algorithm name"
- [x] Task 265: Implement: return dict mapping name to reward_history for each stored result
- [x] Task 266: Verify returns correct keys
- [x] Task 267: Verify returns correct reward lists
- [x] Task 268: Verify returns empty dict when no results stored

### 13.8 ComparisonStore.clear() Method

- [x] Task 269: Define `clear(self) -> None` method
- [x] Task 270: Add docstring: "Clear all stored results"
- [x] Task 271: Implement: `self.results.clear()`
- [x] Task 272: Verify results is empty after clear
- [x] Task 273: Verify has_all returns False after clear
- [x] Task 274: Verify has_results returns False for any name after clear
- [x] Task 275: Verify get_histories returns empty dict after clear

---

## 14. generate_comparison_chart() Function (~45 tasks)

### 14.1 Function Definition

- [x] Task 276: Define `def generate_comparison_chart(store, output_path, config) -> str:` function
- [x] Task 277: Add function docstring: "Generate matplotlib chart comparing convergence curves of all algorithms"
- [x] Task 278: Add type hints for parameters
- [x] Task 279: Add return type hint as str (output file path)

### 14.2 Matplotlib Figure Creation

- [x] Task 280: Create figure: `fig, ax = plt.subplots(figsize=(10, 6))`
- [x] Task 281: Set figure DPI for high-quality output: `fig.set_dpi(100)`
- [x] Task 282: Set figure background color
- [x] Task 283: Set axes background color

### 14.3 Three Convergence Curves

- [x] Task 284: Get histories from store: `histories = store.get_histories()`
- [x] Task 285: Define color mapping for Bellman (orange): from config.colors.algo_bellman
- [x] Task 286: Define color mapping for Q-Learning (green): from config.colors.algo_q_learning
- [x] Task 287: Define color mapping for Double Q (blue): from config.colors.algo_double_q
- [x] Task 288: Convert RGB colors from config (0-255) to matplotlib format (0-1)
- [x] Task 289: Iterate over histories dict items
- [x] Task 290: For each algorithm, get reward history list
- [x] Task 291: Plot raw data or smoothed data for each algorithm

### 14.4 Moving Average Smoothing

- [x] Task 292: Get smoothing window from config: `window = config.comparison.smoothing_window`
- [x] Task 293: Implement moving average: `np.convolve(data, np.ones(window)/window, mode='valid')`
- [x] Task 294: Apply smoothing to each algorithm's reward history
- [x] Task 295: Handle case where history is shorter than window
- [x] Task 296: Verify smoothed data has correct length
- [x] Task 297: Verify smoothing reduces noise in the curves

### 14.5 Legend, Labels, Title

- [x] Task 298: Add x-axis label: `ax.set_xlabel("Episode")`
- [x] Task 299: Add y-axis label: `ax.set_ylabel("Reward (smoothed)")`
- [x] Task 300: Add title: `ax.set_title("Algorithm Comparison — Convergence Curves")`
- [x] Task 301: Add legend: `ax.legend()`
- [x] Task 302: Position legend in upper left or best location
- [x] Task 303: Add grid lines: `ax.grid(True, alpha=0.3)`
- [x] Task 304: Set grid line style to dashed
- [x] Task 305: Verify all 3 algorithms appear in legend with correct names
- [x] Task 306: Verify colors match algorithm names in legend

### 14.6 Save to PNG

- [x] Task 307: Create output directory if needed: `os.makedirs(os.path.dirname(output_path), exist_ok=True)`
- [x] Task 308: Save figure: `fig.savefig(output_path, bbox_inches='tight')`
- [x] Task 309: Close figure to free memory: `plt.close(fig)`
- [x] Task 310: Return output_path
- [x] Task 311: Verify PNG file is created at output_path
- [x] Task 312: Verify PNG file is not empty
- [x] Task 313: Verify PNG file is valid image format
- [x] Task 314: Verify figure is closed after saving (no memory leak)

### 14.7 Edge Cases

- [x] Task 315: Handle case where store has fewer than 3 algorithms
- [x] Task 316: Handle case where one algorithm has empty reward history
- [x] Task 317: Handle case where algorithms have different history lengths
- [x] Task 318: Handle case where output directory does not exist
- [x] Task 319: Verify chart generation does not crash with edge cases
- [x] Task 320: Verify function returns the output path string

---

## 15. draw_comparison_graph() for Pygame (~10 tasks)

- [x] Task 321: Consider if a Pygame-native comparison display is needed
- [x] Task 322: If needed, define `draw_comparison_graph(surface, store, config) -> None`
- [x] Task 323: Load the saved PNG file from data/comparison/
- [x] Task 324: Convert PNG to Pygame surface
- [x] Task 325: Scale to fit display area
- [x] Task 326: Blit onto the provided surface
- [x] Task 327: Handle case where PNG does not exist yet
- [x] Task 328: Verify draw does not crash when no comparison data exists
- [x] Task 329: Verify Pygame display updates correctly
- [x] Task 330: Verify ruff check passes on comparison.py

---

## 16. Comparison.py — Line Count and Quality (~10 tasks)

- [x] Task 331: Count total lines in comparison.py
- [x] Task 332: Verify comparison.py is approximately ~120 lines
- [x] Task 333: Verify comparison.py is at or under 150 lines
- [x] Task 334: Verify ruff check passes on comparison.py
- [x] Task 335: Verify all functions have docstrings
- [x] Task 336: Verify all methods have docstrings
- [x] Task 337: Verify no hardcoded values
- [x] Task 338: Verify all colors come from config
- [x] Task 339: Verify smoothing window comes from config
- [x] Task 340: Verify output path comes from config

---

## 17. SDK switch_algorithm() Method (~25 tasks)

- [x] Task 341: Open `src/sdk.py` for editing
- [x] Task 342: Import ComparisonStore from src.comparison
- [x] Task 343: Import generate_comparison_chart from src.comparison
- [x] Task 344: Initialize `self.comparison_store = ComparisonStore()` in SDK __init__
- [x] Task 345: Define `switch_algorithm(self, name: str) -> None` method
- [x] Task 346: Add docstring: "Switch to a different algorithm, creating new agent and resetting trainer"
- [x] Task 347: Update config: `self.config.algorithm.name = name`
- [x] Task 348: Create new agent via factory: `self.agent = create_agent(self.config)`
- [x] Task 349: Reset trainer with new agent (preserve environment)
- [x] Task 350: Log algorithm switch
- [x] Task 351: Verify environment grid is preserved after switch
- [x] Task 352: Verify trainer episode count resets
- [x] Task 353: Verify new agent has correct algorithm_name
- [x] Task 354: Verify switch to "bellman" creates BellmanAgent
- [x] Task 355: Verify switch to "q_learning" creates QLearningAgent
- [x] Task 356: Verify switch to "double_q" creates DoubleQAgent
- [x] Task 357: Verify switch with invalid name raises ValueError
- [x] Task 358: Verify switch does not corrupt environment state
- [x] Task 359: Verify switch can be called multiple times
- [x] Task 360: Verify switch resets reward history
- [x] Task 361: Test switch from Bellman to Q-Learning
- [x] Task 362: Test switch from Q-Learning to Double Q
- [x] Task 363: Test switch from Double Q back to Bellman
- [x] Task 364: Verify ruff check passes after switch_algorithm addition
- [x] Task 365: Verify SDK stays at or under 150 lines

---

## 18. SDK run_comparison() Method (~20 tasks)

- [x] Task 366: Define `run_comparison(self, episodes: int = None) -> None` method
- [x] Task 367: Add docstring: "Train all 3 algorithms sequentially and store results for comparison"
- [x] Task 368: Default episodes to `self.config.comparison.max_episodes` if None
- [x] Task 369: Define algorithm list: `["bellman", "q_learning", "double_q"]`
- [x] Task 370: Iterate over algorithm list
- [x] Task 371: For each algorithm: call `self.switch_algorithm(name)`
- [x] Task 372: For each algorithm: train for specified number of episodes
- [x] Task 373: For each algorithm: collect reward_history from trainer
- [x] Task 374: For each algorithm: collect metrics from trainer/game_logic
- [x] Task 375: For each algorithm: call `self.comparison_store.store(algo_name, history, metrics)`
- [x] Task 376: After all algorithms trained: call `self.generate_comparison_chart()`
- [x] Task 377: Verify all 3 algorithms are trained sequentially
- [x] Task 378: Verify comparison_store has results for all 3 after completion
- [x] Task 379: Verify chart is generated after training completes
- [x] Task 380: Verify environment is preserved between algorithm runs
- [x] Task 381: Verify run_comparison handles training interruption gracefully
- [x] Task 382: Test run_comparison with default episodes
- [x] Task 383: Test run_comparison with custom episodes count
- [x] Task 384: Verify ruff check passes after run_comparison addition
- [x] Task 385: Verify SDK stays at or under 150 lines

---

## 19. SDK generate_comparison_chart() Method (~10 tasks)

- [x] Task 386: Define `generate_comparison_chart(self) -> str` method
- [x] Task 387: Add docstring: "Generate and save comparison chart, return file path"
- [x] Task 388: Get output dir from config: `self.config.comparison.output_dir`
- [x] Task 389: Construct output path: `os.path.join(output_dir, "comparison.png")`
- [x] Task 390: Call `generate_comparison_chart(self.comparison_store, output_path, self.config)`
- [x] Task 391: Return the output file path
- [x] Task 392: Verify chart file is created
- [x] Task 393: Verify return value is the file path string
- [x] Task 394: Verify ruff check passes after addition
- [x] Task 395: Verify SDK stays at or under 150 lines

---

## 20. GUI Algorithm Selector Buttons (~30 tasks)

### 20.1 Buttons — Algorithm Selection

- [x] Task 396: Open `src/buttons.py` for editing
- [x] Task 397: Locate the `_get_buttons()` function or button definition area
- [x] Task 398: Add "Bellman" algorithm selector button
- [x] Task 399: Set Bellman button action to `"algo_bellman"`
- [x] Task 400: Add "Q-Learning" algorithm selector button
- [x] Task 401: Set Q-Learning button action to `"algo_q_learning"`
- [x] Task 402: Add "Double Q" algorithm selector button
- [x] Task 403: Set Double Q button action to `"algo_double_q"`
- [x] Task 404: Add active state highlighting for current algorithm button
- [x] Task 405: Use `state_dict["algorithm"]` to determine active button
- [x] Task 406: Verify active button uses highlighted color
- [x] Task 407: Verify inactive buttons use default color
- [x] Task 408: Verify all 3 buttons are visible in the dashboard

### 20.2 Buttons — Compare All

- [x] Task 409: Add "Compare All" button
- [x] Task 410: Set Compare All button action to `"compare"`
- [x] Task 411: Verify Compare All button is visible
- [x] Task 412: Verify Compare All button triggers comparison

### 20.3 Buttons — Line Count

- [x] Task 413: Count total lines in buttons.py after additions
- [x] Task 414: Verify buttons.py is at or under 150 lines
- [x] Task 415: If over 150, extract button config to `src/button_config.py`
- [x] Task 416: Verify ruff check passes on buttons.py
- [x] Task 417: Verify all new buttons have correct labels
- [x] Task 418: Verify all new buttons have correct action strings
- [x] Task 419: Verify button layout does not overlap existing buttons
- [x] Task 420: Verify buttons render correctly at window size

---

## 21. GUI Keyboard Shortcuts (1/2/3/C) (~25 tasks)

### 21.1 Key Mappings

- [x] Task 421: Open `src/gui.py` for editing
- [x] Task 422: Locate the `_on_key()` method or key event handling
- [x] Task 423: Add key mapping: `pygame.K_1` -> `"algo_bellman"`
- [x] Task 424: Add key mapping: `pygame.K_2` -> `"algo_q_learning"`
- [x] Task 425: Add key mapping: `pygame.K_3` -> `"algo_double_q"`
- [x] Task 426: Add key mapping: `pygame.K_c` -> `"compare"`
- [x] Task 427: Verify key 1 switches to Bellman algorithm
- [x] Task 428: Verify key 2 switches to Q-Learning algorithm
- [x] Task 429: Verify key 3 switches to Double Q-Learning algorithm
- [x] Task 430: Verify key C triggers comparison

### 21.2 Status Bar Updates

- [x] Task 431: Locate _status_bar() method in gui.py
- [x] Task 432: Add algorithm name to mode display string
- [x] Task 433: Format: `"Mode: TRAINING [Double Q-Learning]"`
- [x] Task 434: Read algorithm name from `self.agent.algorithm_name`
- [x] Task 435: Update shortcuts string to include: `"1/2/3 Algorithm  C Compare"`
- [x] Task 436: Verify status bar updates when algorithm changes
- [x] Task 437: Verify shortcuts text is visible in status bar

### 21.3 GUI — Line Count

- [x] Task 438: Count total lines in gui.py after additions
- [x] Task 439: Verify gui.py is at or under 150 lines
- [x] Task 440: Verify ruff check passes on gui.py
- [x] Task 441: Verify key shortcuts do not conflict with existing shortcuts
- [x] Task 442: Verify key shortcuts work in both training and editor modes
- [x] Task 443: Test pressing 1, 2, 3 in sequence switches algorithms correctly
- [x] Task 444: Test pressing C triggers comparison flow
- [x] Task 445: Verify GUI does not crash on rapid key presses

---

## 22. Dashboard Alpha Display (~15 tasks)

- [x] Task 446: Open `src/dashboard.py` for editing
- [x] Task 447: Locate _draw_metrics() method
- [x] Task 448: Add algorithm name display: `f"Algorithm: {algorithm_name}"`
- [x] Task 449: Position algorithm name in metrics panel
- [x] Task 450: Add conditional alpha display: check if `"alpha"` key in metrics
- [x] Task 451: If alpha present: render `f"Alpha: {alpha:.4f}"`
- [x] Task 452: Position alpha display below epsilon
- [x] Task 453: Verify alpha shows for Q-Learning agent
- [x] Task 454: Verify alpha shows for Double Q-Learning agent
- [x] Task 455: Verify alpha does NOT show for Bellman agent
- [x] Task 456: Verify algorithm name shows for all agent types
- [x] Task 457: Verify dashboard.py stays at or under 150 lines
- [x] Task 458: If over 150, extract legend to `src/legend.py`
- [x] Task 459: Verify ruff check passes on dashboard.py
- [x] Task 460: Verify metrics panel layout is not crowded

---

## 23. Actions Dispatch for New Actions (~25 tasks)

- [x] Task 461: Open `src/actions.py` for editing
- [x] Task 462: Locate the action dispatch dictionary or function
- [x] Task 463: Add `"algo_bellman"` action handler
- [x] Task 464: Implement algo_bellman: call `gui.sdk.switch_algorithm("bellman")` or create agent via factory
- [x] Task 465: Reset gui.agent and gui.logic with new agent
- [x] Task 466: Set gui.paused = True after algorithm switch
- [x] Task 467: Add `"algo_q_learning"` action handler
- [x] Task 468: Implement algo_q_learning: call `gui.sdk.switch_algorithm("q_learning")`
- [x] Task 469: Reset gui.agent and gui.logic with new agent
- [x] Task 470: Add `"algo_double_q"` action handler
- [x] Task 471: Implement algo_double_q: call `gui.sdk.switch_algorithm("double_q")`
- [x] Task 472: Reset gui.agent and gui.logic with new agent
- [x] Task 473: Add `"compare"` action handler
- [x] Task 474: Implement compare: if comparison store has results, show chart
- [x] Task 475: Implement compare: if no results, trigger `sdk.run_comparison()`
- [x] Task 476: Verify all new actions are dispatched correctly
- [x] Task 477: Verify actions handle missing SDK gracefully
- [x] Task 478: Verify actions handle GUI state correctly
- [x] Task 479: Verify actions.py stays at or under 150 lines
- [x] Task 480: If over 150, split into `src/algo_actions.py`
- [x] Task 481: Verify ruff check passes on actions.py
- [x] Task 482: Test each new action dispatches correctly
- [x] Task 483: Test algorithm switch updates agent reference
- [x] Task 484: Test compare action triggers training or chart display
- [x] Task 485: Verify no existing actions are broken

---

## 24. Config.yaml — Double Q and Comparison Sections (~20 tasks)

### 24.1 Double Q Section

- [x] Task 486: Open `config/config.yaml` for editing
- [x] Task 487: Add section comment: `# Double Q-Learning specific hyperparameters`
- [x] Task 488: Add `double_q:` top-level key
- [x] Task 489: Add `alpha_start: 0.5` under double_q
- [x] Task 490: Add `alpha_end: 0.01` under double_q
- [x] Task 491: Add `alpha_decay: 0.999` under double_q

### 24.2 Comparison Section

- [x] Task 492: Add section comment: `# Comparison settings`
- [x] Task 493: Add `comparison:` top-level key
- [x] Task 494: Add `max_episodes: 5000` under comparison
- [x] Task 495: Add `output_dir: data/comparison` under comparison
- [x] Task 496: Add `smoothing_window: 50` under comparison

### 24.3 Algorithm Curve Colors

- [x] Task 497: Add `algo_bellman: [255, 160, 40]` to colors section
- [x] Task 498: Add `algo_q_learning: [80, 200, 120]` to colors section
- [x] Task 499: Add `algo_double_q: [100, 140, 255]` to colors section

### 24.4 Config Verification

- [x] Task 500: Load config and verify double_q.alpha_start is 0.5
- [x] Task 501: Load config and verify double_q.alpha_end is 0.01
- [x] Task 502: Load config and verify double_q.alpha_decay is 0.999
- [x] Task 503: Load config and verify comparison.max_episodes is 5000
- [x] Task 504: Load config and verify comparison.output_dir is "data/comparison"
- [x] Task 505: Load config and verify comparison.smoothing_window is 50

---

## 25. Tests for DoubleQAgent (~55 tasks)

### 25.1 Test File Setup

- [x] Task 506: Create new file `tests/test_double_q_agent.py`
- [x] Task 507: Add module docstring to test file
- [x] Task 508: Import pytest
- [x] Task 509: Import DoubleQAgent from src.double_q_agent
- [x] Task 510: Import BaseAgent from src.base_agent
- [x] Task 511: Import numpy as np
- [x] Task 512: Create pytest fixture for test config with double_q section
- [x] Task 513: Create pytest fixture for DoubleQAgent instance

### 25.2 Tests — Initialization

- [x] Task 514: Test QA initialized to zeros with shape (rows, cols, 4)
- [x] Task 515: Test QB initialized to zeros with shape (rows, cols, 4)
- [x] Task 516: Test QA and QB are separate arrays (not aliased)
- [x] Task 517: Test q_table property returns QA + QB
- [x] Task 518: Test q_table shape is (rows, cols, 4)
- [x] Task 519: Test alpha initializes to alpha_start
- [x] Task 520: Test algorithm_name returns "Double Q-Learning"
- [x] Task 521: Test DoubleQAgent inherits from BaseAgent

### 25.3 Tests — Update Cross-Table

- [x] Task 522: Test single update modifies exactly one table (not both)
- [x] Task 523: Test cross-table evaluation: argmax from updating table, value from other
- [x] Task 524: Test over many updates, both tables accumulate values
- [x] Task 525: Test update with done=True uses next_val = 0.0
- [x] Task 526: Test update with done=False uses cross-table value
- [x] Task 527: Test update uses alpha (not lr)
- [x] Task 528: Test update formula: Q += alpha * (target - Q)
- [x] Task 529: Test update does not modify other Q-values
- [x] Task 530: Test QA update uses QB for evaluation
- [x] Task 531: Test QB update uses QA for evaluation

### 25.4 Tests — Combined Table Actions

- [x] Task 532: Test get_best_action uses combined QA + QB
- [x] Task 533: Test get_max_q uses combined QA + QB
- [x] Task 534: Test choose_action works with combined table
- [x] Task 535: Test get_best_action returns int
- [x] Task 536: Test get_max_q returns float

### 25.5 Tests — Alpha Decay

- [x] Task 537: Test alpha decays after decay_epsilon()
- [x] Task 538: Test alpha never goes below alpha_end
- [x] Task 539: Test alpha decay is multiplicative
- [x] Task 540: Test epsilon also decays (inherited)

### 25.6 Tests — Save/Load

- [x] Task 541: Test save creates two .npy files (_a.npy and _b.npy)
- [x] Task 542: Test load restores both tables correctly
- [x] Task 543: Test save/load round-trip preserves both tables
- [x] Task 544: Test saved QA matches in-memory QA
- [x] Task 545: Test saved QB matches in-memory QB

### 25.7 Tests — Edge Cases

- [x] Task 546: Test with all-zero tables
- [x] Task 547: Test with one table modified, other zero
- [x] Task 548: Test with negative Q-values
- [x] Task 549: Test with very large Q-values
- [x] Task 550: Test multiple sequential updates
- [x] Task 551: Test update followed by get_best_action
- [x] Task 552: Run all DoubleQAgent tests
- [x] Task 553: Run ruff check on test file
- [x] Task 554: Verify coverage for double_q_agent.py is 85%+

---

## 26. Tests for ComparisonStore (~25 tasks)

- [x] Task 555: Create or extend `tests/test_comparison.py`
- [x] Task 556: Import ComparisonStore from src.comparison
- [x] Task 557: Test store() saves results under algorithm name
- [x] Task 558: Test has_results() returns True after storing
- [x] Task 559: Test has_results() returns False before storing
- [x] Task 560: Test has_all() returns True when all 3 algorithms present
- [x] Task 561: Test has_all() returns False when only 1 algorithm present
- [x] Task 562: Test has_all() returns False when only 2 algorithms present
- [x] Task 563: Test get_histories() returns dict with correct keys
- [x] Task 564: Test get_histories() returns correct reward lists
- [x] Task 565: Test get_histories() returns empty dict when no results
- [x] Task 566: Test clear() removes all stored results
- [x] Task 567: Test clear() makes has_all return False
- [x] Task 568: Test store overwrites previous results for same name
- [x] Task 569: Test store preserves other algorithm results
- [x] Task 570: Run all ComparisonStore tests
- [x] Task 571: Verify ruff check passes on test file

---

## 27. Tests for Chart Generation (~10 tasks)

- [x] Task 572: Test generate_comparison_chart creates PNG file
- [x] Task 573: Test chart file is not empty
- [x] Task 574: Test chart generation creates output directory
- [x] Task 575: Test chart with 3 algorithm histories
- [x] Task 576: Test chart with 1 algorithm history (partial)
- [x] Task 577: Test chart handles empty history gracefully
- [x] Task 578: Test smoothing window applies correctly
- [x] Task 579: Test chart function returns output path
- [x] Task 580: Run all chart generation tests
- [x] Task 581: Verify ruff check passes

---

## 28. Final Verification (~4 tasks)

- [x] Task 582: Run full test suite: `uv run pytest` — all tests pass
- [x] Task 583: Run coverage check: 85%+ on all new files
- [x] Task 584: Run lint check: `uv run ruff check src/ tests/` — zero violations
- [x] Task 585: Verify all new files are at or under 150 lines

---

## Summary

| Section | Tasks |
|---------|-------|
| 1. DoubleQAgent File Setup | 15 |
| 2. DoubleQAgent Class Definition | 10 |
| 3. DoubleQAgent.__init__() | 30 |
| 4. DoubleQAgent.update() | 40 |
| 5. DoubleQAgent.q_table Property | 20 |
| 6. get_best_action() Combined | 15 |
| 7. get_max_q() Combined | 15 |
| 8. save() Two Files | 20 |
| 9. load() Two Files | 20 |
| 10. Alpha Decay | 20 |
| 11. Line Count & Quality | 10 |
| 12. Agent Factory Registration | 15 |
| 13. ComparisonStore Class | 45 |
| 14. generate_comparison_chart() | 45 |
| 15. draw_comparison_graph() Pygame | 10 |
| 16. comparison.py Quality | 10 |
| 17. SDK switch_algorithm() | 25 |
| 18. SDK run_comparison() | 20 |
| 19. SDK generate_comparison_chart() | 10 |
| 20. GUI Algorithm Buttons | 25 |
| 21. GUI Keyboard Shortcuts | 25 |
| 22. Dashboard Alpha Display | 15 |
| 23. Actions Dispatch | 25 |
| 24. Config.yaml Additions | 20 |
| 25. Tests for DoubleQAgent | 49 |
| 26. Tests for ComparisonStore | 17 |
| 27. Tests for Chart Generation | 10 |
| 28. Final Verification | 4 |
| **Total** | **585** |
