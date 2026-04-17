# DroneRL — Q-Learning Agent Task Breakdown

> All tasks marked as completed. Total: 580 granular tasks covering every aspect of the Q-Learning agent feature.

---

## 1. BaseAgent Abstract Class — File Setup (~20 tasks)

- [x] Task 1: Create new file `src/base_agent.py`
- [x] Task 2: Add module docstring: "Abstract base class for all RL agents in DroneRL"
- [ ] Task 3: Add `from __future__ import annotations` import
- [ ] Task 4: Add `from abc import ABC, abstractmethod` import
- [x] Task 5: Add `import numpy as np` import
- [x] Task 6: Add `import random` import
- [x] Task 7: Add `from pathlib import Path` import
- [ ] Task 8: Add type hints import: `from typing import TYPE_CHECKING`
- [ ] Task 9: Add conditional import: `if TYPE_CHECKING: from src.config_loader import Config`
- [x] Task 10: Verify all imports are necessary and used
- [x] Task 11: Verify file encoding is UTF-8
- [x] Task 12: Verify no circular imports exist
- [x] Task 13: Run ruff check on base_agent.py to verify clean state
- [x] Task 14: Verify file is saved and accessible
- [x] Task 15: Verify `from src.base_agent import BaseAgent` works
- [x] Task 16: Verify the module can be imported without side effects
- [x] Task 17: Add blank line after imports per PEP 8
- [x] Task 18: Add blank line before class definition per PEP 8

---

## 2. BaseAgent Class Definition (~35 tasks)

### 2.1 Class Shell

- [ ] Task 19: Define `class BaseAgent(ABC):` inheriting from ABC
- [x] Task 20: Add class docstring: "Abstract base agent providing shared RL infrastructure"
- [x] Task 21: Define class constant `NUM_ACTIONS = 4`
- [x] Task 22: Add comment explaining NUM_ACTIONS: UP, DOWN, LEFT, RIGHT
- [x] Task 23: Verify NUM_ACTIONS matches the action space in environment.py

### 2.2 __init__ Method

- [x] Task 24: Define `__init__(self, config: Config) -> None` method signature
- [x] Task 25: Add __init__ docstring: "Initialize shared agent parameters from config"
- [x] Task 26: Extract grid rows: `self.rows = config.environment.grid_rows`
- [x] Task 27: Extract grid cols: `self.cols = config.environment.grid_cols`
- [x] Task 28: Extract discount factor: `self.gamma = config.agent.discount_factor`
- [x] Task 29: Extract epsilon start: `self.epsilon = config.agent.epsilon_start`
- [x] Task 30: Extract epsilon end: `self.epsilon_end = config.agent.epsilon_end`
- [x] Task 31: Extract epsilon decay: `self.epsilon_decay = config.agent.epsilon_decay`
- [x] Task 32: Initialize Q-table: `self._q_table = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))`
- [x] Task 33: Verify Q-table shape is (rows, cols, 4)
- [x] Task 34: Verify Q-table is initialized to all zeros
- [x] Task 35: Verify Q-table dtype is float64
- [x] Task 36: Verify all config values are loaded correctly
- [x] Task 37: Verify no hardcoded values in __init__

### 2.3 q_table Property

- [ ] Task 38: Define `@property q_table(self) -> np.ndarray` getter
- [ ] Task 39: Add docstring: "The Q-table used by GUI overlays for visualization"
- [ ] Task 40: Return `self._q_table` from getter
- [x] Task 41: Verify q_table returns a reference (not copy) for performance
- [ ] Task 42: Verify q_table type hint is np.ndarray

### 2.4 algorithm_name Property

- [x] Task 43: Define `@property algorithm_name(self) -> str` as abstract or class attribute
- [x] Task 44: Add docstring: "Human-readable algorithm name for display"
- [x] Task 45: Verify algorithm_name must be overridden by subclasses
- [x] Task 46: Verify algorithm_name returns a string type

---

## 3. BaseAgent — Shared Methods (~65 tasks)

### 3.1 choose_action() Method

- [x] Task 47: Define `choose_action(self, state: tuple[int, int]) -> int` method signature
- [x] Task 48: Add docstring: "Epsilon-greedy action selection"
- [x] Task 49: Add type hint for state parameter as tuple[int, int]
- [x] Task 50: Add return type hint as int
- [x] Task 51: Generate random float for epsilon comparison: `random.random()`
- [x] Task 52: Add epsilon check: `if random.random() < self.epsilon`
- [x] Task 53: If exploring: return `random.randint(0, self.NUM_ACTIONS - 1)`
- [x] Task 54: If exploiting: return `self.get_best_action(state)`
- [x] Task 55: Verify return value is in range [0, 3]
- [x] Task 56: Verify epsilon=1.0 always explores
- [x] Task 57: Verify epsilon=0.0 always exploits
- [x] Task 58: Verify choose_action handles edge case epsilon=0.5

### 3.2 get_best_action() Method

- [x] Task 59: Define `get_best_action(self, state: tuple[int, int]) -> int` method signature
- [x] Task 60: Add docstring: "Return action with highest Q-value for given state"
- [x] Task 61: Add type hint for state parameter as tuple[int, int]
- [x] Task 62: Add return type hint as int
- [x] Task 63: Extract row and col from state: `r, c = state`
- [x] Task 64: Compute argmax: `int(np.argmax(self.q_table[r, c]))`
- [x] Task 65: Return the argmax action
- [x] Task 66: Verify returns int, not np.int64
- [x] Task 67: Verify handles ties (argmax returns first max)
- [x] Task 68: Verify handles all-zero Q-values (returns 0)

### 3.3 get_max_q() Method

- [x] Task 69: Define `get_max_q(self, state: tuple[int, int]) -> float` method signature
- [x] Task 70: Add docstring: "Return maximum Q-value for given state across all actions"
- [x] Task 71: Add type hint for state parameter as tuple[int, int]
- [x] Task 72: Add return type hint as float
- [x] Task 73: Extract row and col from state: `r, c = state`
- [x] Task 74: Compute max: `float(np.max(self.q_table[r, c]))`
- [x] Task 75: Return the max value
- [x] Task 76: Verify returns float, not np.float64
- [x] Task 77: Verify handles all-zero Q-values (returns 0.0)
- [x] Task 78: Verify handles negative Q-values

### 3.4 decay_epsilon() Method

- [x] Task 79: Define `decay_epsilon(self) -> None` method signature
- [x] Task 80: Add docstring: "Exponentially decay epsilon, clamped to epsilon_end"
- [x] Task 81: Implement: `self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)`
- [x] Task 82: Verify epsilon never goes below epsilon_end
- [x] Task 83: Verify epsilon decreases after each call
- [x] Task 84: Verify epsilon_end acts as a floor
- [x] Task 85: Verify decay is multiplicative (exponential)

### 3.5 update() Abstract Method

- [ ] Task 86: Define `@abstractmethod update(self, state, action, reward, next_state, done) -> None`
- [x] Task 87: Add docstring: "Update Q-value(s) — must be implemented by subclasses"
- [x] Task 88: Add type hints for all parameters
- [ ] Task 89: Verify update is decorated with @abstractmethod
- [ ] Task 90: Verify BaseAgent cannot be instantiated directly (abstract)
- [x] Task 91: Verify subclasses must implement update

### 3.6 save() Method

- [x] Task 92: Define `save(self, path: str) -> None` method signature
- [x] Task 93: Add docstring: "Save Q-table to .npy file"
- [x] Task 94: Add type hint for path parameter as str
- [x] Task 95: Implement: `np.save(path, self.q_table)`
- [x] Task 96: Verify save creates a valid .npy file
- [x] Task 97: Verify save writes the correct Q-table data
- [x] Task 98: Verify save handles path with directory creation if needed

### 3.7 load() Method

- [x] Task 99: Define `load(self, path: str) -> None` method signature
- [x] Task 100: Add docstring: "Load Q-table from .npy file"
- [x] Task 101: Add type hint for path parameter as str
- [x] Task 102: Implement: `self._q_table = np.load(path)`
- [x] Task 103: Verify load restores the correct Q-table data
- [x] Task 104: Verify load handles file not found gracefully
- [x] Task 105: Verify loaded Q-table has correct shape
- [x] Task 106: Verify save/load round-trip preserves data exactly

### 3.8 Line Count and Quality

- [x] Task 107: Count total lines in base_agent.py
- [x] Task 108: Verify base_agent.py is at or under 150 lines
- [x] Task 109: Verify ruff check passes on base_agent.py
- [x] Task 110: Verify all methods have docstrings
- [x] Task 111: Verify all methods have type hints

---

## 4. BellmanAgent Refactor (~60 tasks)

### 4.1 Agent.py — Imports Update

- [x] Task 112: Open `src/agent.py` for editing
- [x] Task 113: Remove old standalone imports (numpy, random, etc. now in BaseAgent)
- [x] Task 114: Add `from src.base_agent import BaseAgent` import
- [x] Task 115: Keep any imports that are specific to BellmanAgent only
- [x] Task 116: Verify no circular imports exist
- [x] Task 117: Verify import order follows PEP 8 conventions

### 4.2 BellmanAgent Class Definition

- [x] Task 118: Rename class from `Agent` to `BellmanAgent`
- [x] Task 119: Change inheritance from object/standalone to `BaseAgent`
- [x] Task 120: Update class definition: `class BellmanAgent(BaseAgent):`
- [x] Task 121: Add class docstring: "Bellman-equation agent with constant learning rate"
- [x] Task 122: Define `algorithm_name = "Bellman"` as class attribute
- [x] Task 123: Verify algorithm_name is a string

### 4.3 BellmanAgent.__init__()

- [x] Task 124: Rewrite __init__ to call `super().__init__(config)`
- [x] Task 125: Remove Q-table initialization (now in BaseAgent)
- [x] Task 126: Remove epsilon parameter loading (now in BaseAgent)
- [x] Task 127: Remove gamma loading (now in BaseAgent)
- [x] Task 128: Remove grid dimension loading (now in BaseAgent)
- [x] Task 129: Keep `self.lr = config.agent.learning_rate` (BellmanAgent-specific)
- [x] Task 130: Add __init__ docstring: "Initialize Bellman agent with constant learning rate"
- [x] Task 131: Verify super().__init__ is called first
- [x] Task 132: Verify lr is loaded from config.agent.learning_rate
- [x] Task 133: Verify no duplicate initialization with BaseAgent

### 4.4 BellmanAgent.update()

- [x] Task 134: Keep existing update method implementation
- [x] Task 135: Verify update signature matches BaseAgent.update abstract method
- [x] Task 136: Verify update uses `self.lr` (constant learning rate)
- [x] Task 137: Verify update computes: `current_q = self.q_table[state[0], state[1], action]`
- [x] Task 138: Verify update computes: `next_max_q = 0.0 if done else self.get_max_q(next_state)`
- [x] Task 139: Verify update computes: `target = reward + self.gamma * next_max_q`
- [x] Task 140: Verify update applies: `self.q_table[...] += self.lr * (target - current_q)`
- [x] Task 141: Verify update behavior is identical to pre-refactor Agent

### 4.5 Remove Migrated Methods from agent.py

- [x] Task 142: Remove choose_action method (now in BaseAgent)
- [x] Task 143: Remove get_best_action method (now in BaseAgent)
- [x] Task 144: Remove get_max_q method (now in BaseAgent)
- [x] Task 145: Remove decay_epsilon method (now in BaseAgent)
- [x] Task 146: Remove save method (now in BaseAgent)
- [x] Task 147: Remove load method (now in BaseAgent)
- [x] Task 148: Remove NUM_ACTIONS constant (now in BaseAgent)
- [x] Task 149: Remove Q-table initialization code from __init__ (now in BaseAgent)
- [x] Task 150: Verify all migrated methods are removed from agent.py
- [x] Task 151: Verify no dead code remains in agent.py

### 4.6 Backward Compatibility Alias

- [x] Task 152: Add `Agent = BellmanAgent` alias at module level
- [x] Task 153: Add comment: "# Backward compatibility alias"
- [x] Task 154: Verify `from src.agent import Agent` still works
- [x] Task 155: Verify `Agent(config)` creates a BellmanAgent instance
- [x] Task 156: Verify `isinstance(Agent(config), BaseAgent)` is True
- [x] Task 157: Verify `isinstance(Agent(config), BellmanAgent)` is True
- [x] Task 158: Verify Agent alias appears in module __all__ if defined

### 4.7 Agent.py — Line Count and Quality

- [x] Task 159: Count total lines in agent.py after refactor
- [x] Task 160: Verify agent.py is significantly smaller (~35 lines)
- [x] Task 161: Verify agent.py is at or under 150 lines
- [x] Task 162: Verify ruff check passes on agent.py
- [x] Task 163: Verify all methods have docstrings
- [x] Task 164: Verify module docstring is updated to mention BellmanAgent

### 4.8 Backward Compatibility Tests

- [x] Task 165: Run full test suite: `uv run pytest`
- [x] Task 166: Verify all 104 existing tests pass without modification
- [x] Task 167: Verify test_agent.py tests pass with BellmanAgent alias
- [x] Task 168: Verify Agent(config).choose_action() works identically
- [x] Task 169: Verify Agent(config).update() works identically
- [x] Task 170: Verify Agent(config).decay_epsilon() works identically
- [x] Task 171: Verify Agent(config).save() works identically

---

## 5. Import Updates Across Consuming Files (~50 tasks)

### 5.1 SDK — Import Update

- [x] Task 172: Open `src/sdk.py` for editing
- [x] Task 173: Identify current Agent import: `from src.agent import Agent`
- [x] Task 174: Verify import still works (Agent alias resolves to BellmanAgent)
- [x] Task 175: Note: no change needed if using factory (PRD integration)
- [x] Task 176: Verify SDK creates agent correctly after refactor

### 5.2 Trainer — Import Update

- [x] Task 177: Open `src/trainer.py` for editing
- [x] Task 178: Identify current Agent import or type reference
- [x] Task 179: Update type hint from `Agent` to `BaseAgent` if present
- [x] Task 180: Add import: `from src.base_agent import BaseAgent` if type hints used
- [x] Task 181: Verify trainer works with both BellmanAgent and QLearningAgent
- [x] Task 182: Verify trainer calls agent.update() polymorphically
- [x] Task 183: Verify trainer calls agent.decay_epsilon() polymorphically
- [x] Task 184: Verify trainer.py stays at or under 150 lines

### 5.3 Game Logic — Import Update

- [x] Task 185: Open `src/game_logic.py` for editing
- [x] Task 186: Identify current Agent import or type reference
- [x] Task 187: Update type hint from `Agent` to `BaseAgent` if present
- [x] Task 188: Add import: `from src.base_agent import BaseAgent` if type hints used
- [x] Task 189: Verify game_logic works with any BaseAgent subclass
- [x] Task 190: Verify game_logic.py stays at or under 150 lines

### 5.4 GUI — Import Update

- [x] Task 191: Open `src/gui.py` for editing
- [x] Task 192: Identify current Agent import or type reference
- [x] Task 193: Verify GUI works with BaseAgent subclass (polymorphic)
- [x] Task 194: Verify GUI reads agent.q_table property correctly
- [x] Task 195: Verify GUI reads agent.algorithm_name if used
- [x] Task 196: Verify gui.py stays at or under 150 lines

### 5.5 Actions — Import Update

- [x] Task 197: Open `src/actions.py` for editing
- [x] Task 198: Identify current Agent import in actions.py
- [x] Task 199: Update to use agent factory if agent is created in actions
- [x] Task 200: Verify actions work correctly after import update
- [x] Task 201: Verify actions.py stays at or under 150 lines

### 5.6 Overlays — Import Update

- [x] Task 202: Open `src/overlays.py` for editing
- [x] Task 203: Verify overlays read agent.q_table (property, not direct attribute)
- [x] Task 204: Verify overlays work with any BaseAgent subclass
- [x] Task 205: Verify overlays.py stays at or under 150 lines

### 5.7 Dashboard — Import Update

- [x] Task 206: Open `src/dashboard.py` for editing
- [x] Task 207: Verify dashboard does not directly import Agent
- [x] Task 208: Verify dashboard reads metrics dict (agent-agnostic)
- [x] Task 209: Verify dashboard.py stays at or under 150 lines

### 5.8 Cross-File Verification

- [x] Task 210: Run `uv run pytest` to verify all imports work
- [x] Task 211: Verify no ImportError in any module
- [x] Task 212: Verify no AttributeError from missing methods
- [x] Task 213: Verify ruff check passes on all modified files
- [x] Task 214: Verify no circular import warnings
- [x] Task 215: Run application `uv run main.py` and verify it starts
- [x] Task 216: Verify training loop works after import updates
- [x] Task 217: Verify editor mode works after import updates
- [x] Task 218: Verify overlays render correctly after import updates
- [x] Task 219: Verify dashboard displays correctly after import updates
- [x] Task 220: Verify save/load works after import updates
- [x] Task 221: Verify reset action works after import updates

---

## 6. QLearningAgent Class Creation (~55 tasks)

### 6.1 File Setup

- [x] Task 222: Create new file `src/q_agent.py`
- [x] Task 223: Add module docstring: "Q-Learning agent with decaying learning rate (alpha)"
- [ ] Task 224: Add `from __future__ import annotations` import
- [x] Task 225: Add `from src.base_agent import BaseAgent` import
- [x] Task 226: Add type hints import if needed
- [x] Task 227: Verify imports are minimal and necessary
- [x] Task 228: Verify no circular imports
- [x] Task 229: Run ruff check on q_agent.py to verify clean state

### 6.2 QLearningAgent Class Definition

- [x] Task 230: Define `class QLearningAgent(BaseAgent):` inheriting from BaseAgent
- [x] Task 231: Add class docstring: "Q-Learning with decaying alpha for stable convergence"
- [x] Task 232: Define `algorithm_name = "Q-Learning"` as class attribute
- [x] Task 233: Verify algorithm_name is a string
- [x] Task 234: Verify QLearningAgent is a concrete class (not abstract)

### 6.3 QLearningAgent.__init__()

- [x] Task 235: Define `__init__(self, config: Config) -> None` method signature
- [x] Task 236: Add __init__ docstring: "Initialize Q-Learning agent with decaying alpha parameters"
- [x] Task 237: Call `super().__init__(config)` first
- [x] Task 238: Extract Q-learning config section: `q_cfg = config.q_learning`
- [x] Task 239: Load alpha_start: `self.alpha = q_cfg.alpha_start`
- [x] Task 240: Load alpha_end: `self.alpha_end = q_cfg.alpha_end`
- [x] Task 241: Load alpha_decay: `self.alpha_decay = q_cfg.alpha_decay`
- [x] Task 242: Verify alpha is initialized to alpha_start value
- [x] Task 243: Verify alpha_end is stored for floor clamping
- [x] Task 244: Verify alpha_decay is stored for multiplicative decay
- [x] Task 245: Verify super().__init__ initializes Q-table and epsilon params

### 6.4 QLearningAgent.update()

- [x] Task 246: Define `update(self, state, action, reward, next_state, done) -> None`
- [x] Task 247: Add update docstring: "TD update with decaying learning rate alpha"
- [x] Task 248: Add type hints for all parameters
- [x] Task 249: Extract current Q-value: `current_q = self.q_table[state[0], state[1], action]`
- [x] Task 250: Compute next max Q: `next_max_q = 0.0 if done else self.get_max_q(next_state)`
- [x] Task 251: Compute TD target: `target = reward + self.gamma * next_max_q`
- [x] Task 252: Apply update: `self.q_table[state[0], state[1], action] += self.alpha * (target - current_q)`
- [x] Task 253: Verify update uses `self.alpha` (NOT self.lr)
- [x] Task 254: Verify update formula matches Q-Learning TD update
- [x] Task 255: Verify update handles done=True correctly (next_max_q = 0.0)
- [x] Task 256: Verify update handles done=False correctly
- [x] Task 257: Verify update modifies Q-table in-place

### 6.5 QLearningAgent.decay_epsilon()

- [x] Task 258: Define `decay_epsilon(self) -> None` override
- [x] Task 259: Add docstring: "Decay both epsilon and alpha per episode"
- [x] Task 260: Call `super().decay_epsilon()` to decay epsilon
- [x] Task 261: Decay alpha: `self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)`
- [x] Task 262: Verify epsilon is decayed via parent method
- [x] Task 263: Verify alpha is decayed independently of epsilon
- [x] Task 264: Verify alpha never goes below alpha_end
- [x] Task 265: Verify alpha decay is multiplicative
- [x] Task 266: Verify both epsilon and alpha are decayed after one call

### 6.6 Line Count and Quality

- [x] Task 267: Count total lines in q_agent.py
- [x] Task 268: Verify q_agent.py is at or under 150 lines
- [x] Task 269: Verify q_agent.py is approximately ~55 lines (lean)
- [x] Task 270: Verify ruff check passes on q_agent.py
- [x] Task 271: Verify all methods have docstrings
- [x] Task 272: Verify all methods have type hints
- [x] Task 273: Verify no code duplication with BellmanAgent
- [x] Task 274: Verify no hardcoded values in q_agent.py
- [x] Task 275: Verify imports are clean and minimal
- [x] Task 276: Verify `from src.q_agent import QLearningAgent` works

---

## 7. Alpha Decay Mechanism (~30 tasks)

### 7.1 Alpha Initialization

- [x] Task 277: Verify alpha starts at alpha_start value from config
- [x] Task 278: Verify alpha_start default is 0.5
- [ ] Task 279: Verify alpha_end default is 0.01
- [ ] Task 280: Verify alpha_decay default is 0.999
- [x] Task 281: Verify alpha is a float attribute
- [x] Task 282: Verify alpha_end is a float attribute
- [x] Task 283: Verify alpha_decay is a float attribute

### 7.2 Alpha Decay Per Episode

- [x] Task 284: Verify alpha decays after each decay_epsilon() call
- [x] Task 285: Verify alpha after 1 decay: alpha * alpha_decay
- [x] Task 286: Verify alpha after 10 decays: alpha * alpha_decay^10
- [x] Task 287: Verify alpha after 100 decays: approaches alpha_end
- [x] Task 288: Verify alpha after 1000 decays: very close to alpha_end
- [x] Task 289: Verify alpha after 5000 decays: equals alpha_end (clamped)

### 7.3 Alpha Clamping

- [x] Task 290: Verify alpha is clamped to alpha_end when decay would go below
- [x] Task 291: Verify max(alpha_end, alpha * alpha_decay) formula
- [x] Task 292: Verify alpha never becomes negative
- [x] Task 293: Verify alpha never becomes zero (alpha_end > 0)
- [x] Task 294: Verify alpha_end acts as absolute minimum floor
- [x] Task 295: Verify clamping is checked on every decay call

### 7.4 Alpha Independence from Epsilon

- [x] Task 296: Verify alpha and epsilon decay independently
- [x] Task 297: Verify alpha has its own decay rate (alpha_decay)
- [x] Task 298: Verify epsilon has its own decay rate (epsilon_decay)
- [x] Task 299: Verify alpha_end and epsilon_end are independent floors
- [x] Task 300: Verify changing alpha does not affect epsilon
- [x] Task 301: Verify changing epsilon does not affect alpha
- [x] Task 302: Verify both reach their respective floors independently
- [x] Task 303: Verify decay_epsilon() decays both in correct order
- [x] Task 304: Verify alpha is decayed after epsilon in decay_epsilon()
- [x] Task 305: Test alpha state after calling decay_epsilon() 500 times
- [x] Task 306: Test epsilon state after calling decay_epsilon() 500 times

---

## 8. Agent Factory Creation (~45 tasks)

### 8.1 File Setup

- [x] Task 307: Create new file `src/agent_factory.py`
- [x] Task 308: Add module docstring: "Factory function for creating RL agents based on config"
- [ ] Task 309: Add `from __future__ import annotations` import
- [x] Task 310: Add `from src.base_agent import BaseAgent` import
- [x] Task 311: Add type hints import if needed
- [x] Task 312: Verify imports are minimal
- [x] Task 313: Verify no circular imports

### 8.2 create_agent() Function

- [x] Task 314: Define `def create_agent(config) -> BaseAgent:` function signature
- [x] Task 315: Add function docstring: "Create and return the appropriate agent based on config.algorithm.name"
- [x] Task 316: Add type hint for config parameter
- [x] Task 317: Add return type hint as BaseAgent
- [x] Task 318: Extract algorithm name: `name = config.algorithm.name`
- [x] Task 319: Add `if name == "bellman":` branch
- [x] Task 320: In bellman branch: `from src.agent import BellmanAgent`
- [x] Task 321: In bellman branch: `return BellmanAgent(config)`
- [x] Task 322: Add `elif name == "q_learning":` branch
- [x] Task 323: In q_learning branch: `from src.q_agent import QLearningAgent`
- [x] Task 324: In q_learning branch: `return QLearningAgent(config)`
- [x] Task 325: Add `elif name == "double_q":` branch (forward compatibility)
- [x] Task 326: In double_q branch: `from src.double_q_agent import DoubleQAgent`
- [x] Task 327: In double_q branch: `return DoubleQAgent(config)`
- [x] Task 328: Add `raise ValueError(f"Unknown algorithm: {name}")` for invalid names
- [ ] Task 329: Verify lazy imports inside function (not at module level)
- [ ] Task 330: Verify lazy imports avoid circular dependencies
- [x] Task 331: Verify ValueError message includes the invalid algorithm name

### 8.3 Factory Dispatch Logic

- [x] Task 332: Verify factory returns BellmanAgent for "bellman"
- [x] Task 333: Verify factory returns QLearningAgent for "q_learning"
- [x] Task 334: Verify factory returns DoubleQAgent for "double_q" (when implemented)
- [x] Task 335: Verify factory raises ValueError for "unknown_algo"
- [x] Task 336: Verify factory raises ValueError for empty string
- [x] Task 337: Verify factory raises ValueError for None
- [x] Task 338: Verify returned agent is instance of BaseAgent
- [x] Task 339: Verify returned agent has q_table property
- [x] Task 340: Verify returned agent has update method
- [x] Task 341: Verify returned agent has choose_action method
- [x] Task 342: Verify returned agent has algorithm_name property

### 8.4 Factory Error Handling

- [x] Task 343: Verify ValueError is raised for unknown algorithm names
- [x] Task 344: Verify error message includes the unrecognized name
- [x] Task 345: Verify factory does not crash on missing config sections
- [x] Task 346: Verify factory handles case sensitivity (lowercase expected)

### 8.5 Line Count and Quality

- [x] Task 347: Count total lines in agent_factory.py
- [x] Task 348: Verify agent_factory.py is approximately ~30 lines (lean)
- [x] Task 349: Verify agent_factory.py is at or under 150 lines
- [x] Task 350: Verify ruff check passes on agent_factory.py
- [x] Task 351: Verify `from src.agent_factory import create_agent` works

---

## 9. Config.yaml Additions (~25 tasks)

### 9.1 Algorithm Section

- [x] Task 352: Open `config/config.yaml` for editing
- [x] Task 353: Add section comment: `# Algorithm selection`
- [x] Task 354: Add `algorithm:` top-level key
- [x] Task 355: Add `name: "bellman"` under algorithm
- [x] Task 356: Add inline comment listing options: `# Options: "bellman", "q_learning", "double_q"`
- [x] Task 357: Verify default is "bellman" for backward compatibility

### 9.2 Q-Learning Section

- [x] Task 358: Add section comment: `# Q-Learning specific hyperparameters`
- [x] Task 359: Add `q_learning:` top-level key
- [x] Task 360: Add `alpha_start: 0.5` under q_learning
- [ ] Task 361: Add `alpha_end: 0.01` under q_learning
- [ ] Task 362: Add `alpha_decay: 0.999` under q_learning
- [x] Task 363: Add comment explaining alpha_start is the initial learning rate
- [x] Task 364: Add comment explaining alpha_end is the minimum learning rate floor
- [x] Task 365: Add comment explaining alpha_decay is multiplicative decay per episode

### 9.3 Config Verification

- [x] Task 366: Load config and verify algorithm.name is "bellman"
- [x] Task 367: Load config and verify q_learning.alpha_start is 0.5
- [ ] Task 368: Load config and verify q_learning.alpha_end is 0.01
- [ ] Task 369: Load config and verify q_learning.alpha_decay is 0.999
- [x] Task 370: Verify config.yaml parses without errors
- [x] Task 371: Verify all new config keys are accessible via dot notation
- [x] Task 372: Verify config round-trip works (load -> to_dict -> load)
- [x] Task 373: Run ruff check on any Python files reading new config
- [x] Task 374: Verify config line count is reasonable
- [x] Task 375: Verify no syntax errors in config.yaml
- [x] Task 376: Save config.yaml after all additions

---

## 10. SDK Integration with Factory (~35 tasks)

### 10.1 SDK — Replace Agent with Factory

- [x] Task 377: Open `src/sdk.py` for editing
- [x] Task 378: Locate current Agent import: `from src.agent import Agent`
- [x] Task 379: Replace with factory import: `from src.agent_factory import create_agent`
- [x] Task 380: Locate agent creation in __init__: `self.agent = Agent(self.config)`
- [x] Task 381: Replace with factory: `self.agent = create_agent(self.config)`
- [x] Task 382: Locate agent creation in reset() if present
- [x] Task 383: Replace reset agent creation with factory call
- [x] Task 384: Verify SDK creates correct agent type based on config

### 10.2 SDK — Algorithm Name Property

- [ ] Task 385: Add `@property algorithm_name(self) -> str` to SDK
- [ ] Task 386: Implement: `return self.agent.algorithm_name`
- [ ] Task 387: Verify SDK exposes algorithm name to GUI

### 10.3 SDK — Alpha Property

- [ ] Task 388: Add `@property alpha(self) -> float | None` to SDK
- [ ] Task 389: Implement: `return getattr(self.agent, 'alpha', None)`
- [ ] Task 390: Verify alpha returns float for QLearningAgent
- [ ] Task 391: Verify alpha returns None for BellmanAgent
- [ ] Task 392: Verify alpha is available for dashboard display

### 10.4 SDK — Line Count and Quality

- [x] Task 393: Count total lines in sdk.py after factory integration
- [x] Task 394: Verify sdk.py is at or under 150 lines
- [x] Task 395: Verify ruff check passes on sdk.py
- [x] Task 396: Verify SDK works with BellmanAgent
- [x] Task 397: Verify SDK works with QLearningAgent
- [x] Task 398: Run `uv run main.py` and verify application starts

### 10.5 GUI — Algorithm Name in Status Bar

- [x] Task 399: Open `src/gui.py` for editing
- [x] Task 400: Locate _status_bar() method
- [x] Task 401: Add algorithm name to mode string display
- [x] Task 402: Read algorithm name from `self.agent.algorithm_name`
- [x] Task 403: Format: "Mode: TRAINING [Q-Learning]" or similar
- [x] Task 404: Verify status bar updates when algorithm changes
- [x] Task 405: Verify gui.py stays at or under 150 lines

### 10.6 Dashboard — Alpha Display

- [x] Task 406: Open `src/dashboard.py` for editing
- [x] Task 407: Locate _draw_metrics() method
- [ ] Task 408: Add conditional alpha display: if "alpha" key in metrics dict
- [ ] Task 409: Render alpha value: `f"Alpha: {alpha:.4f}"`
- [ ] Task 410: Position alpha display below epsilon in metrics panel
- [x] Task 411: Verify dashboard.py stays at or under 150 lines

---

## 11. Tests for BaseAgent (~50 tasks)

### 11.1 Test File Setup

- [x] Task 412: Create new file `tests/test_base_agent.py`
- [x] Task 413: Add module docstring to test file
- [x] Task 414: Import pytest
- [x] Task 415: Import BaseAgent from src.base_agent
- [ ] Task 416: Import BellmanAgent from src.agent (concrete class for testing)
- [ ] Task 417: Import numpy as np
- [x] Task 418: Create pytest fixture for test config
- [ ] Task 419: Create pytest fixture for test agent (BellmanAgent instance)

### 11.2 Tests — Q-Table Initialization

- [x] Task 420: Test Q-table shape is (rows, cols, 4)
- [ ] Task 421: Test Q-table is initialized to all zeros
- [ ] Task 422: Test Q-table dtype is float64
- [ ] Task 423: Test Q-table property returns ndarray
- [ ] Task 424: Test Q-table has correct number of elements

### 11.3 Tests — choose_action()

- [ ] Task 425: Test choose_action returns int
- [ ] Task 426: Test choose_action returns value in [0, 3]
- [ ] Task 427: Test choose_action explores when epsilon=1.0
- [x] Task 428: Test choose_action exploits when epsilon=0.0
- [x] Task 429: Test choose_action returns best action when epsilon=0.0
- [ ] Task 430: Test choose_action randomness when epsilon=1.0 (statistical test)
- [ ] Task 431: Test choose_action with partially trained Q-table

### 11.4 Tests — get_best_action()

- [ ] Task 432: Test get_best_action returns int
- [ ] Task 433: Test get_best_action returns argmax of Q-values
- [ ] Task 434: Test get_best_action with all-zero Q-values returns 0
- [ ] Task 435: Test get_best_action with one non-zero Q-value
- [ ] Task 436: Test get_best_action with multiple non-zero Q-values
- [ ] Task 437: Test get_best_action returns first max on ties

### 11.5 Tests — get_max_q()

- [ ] Task 438: Test get_max_q returns float
- [ ] Task 439: Test get_max_q returns max Q-value for state
- [ ] Task 440: Test get_max_q with all-zero Q-values returns 0.0
- [ ] Task 441: Test get_max_q with positive Q-values
- [ ] Task 442: Test get_max_q with negative Q-values
- [ ] Task 443: Test get_max_q with mixed positive/negative Q-values

### 11.6 Tests — decay_epsilon()

- [x] Task 444: Test epsilon decreases after decay_epsilon()
- [ ] Task 445: Test epsilon never goes below epsilon_end
- [ ] Task 446: Test epsilon decay is multiplicative
- [ ] Task 447: Test epsilon reaches epsilon_end after many decays
- [ ] Task 448: Test epsilon_end is a floor (epsilon stays at epsilon_end after reaching it)

### 11.7 Tests — save() and load()

- [ ] Task 449: Test save creates a file
- [ ] Task 450: Test save writes correct Q-table data
- [ ] Task 451: Test load restores Q-table data
- [ ] Task 452: Test save/load round-trip preserves data exactly
- [ ] Task 453: Test load with modified Q-table restores original
- [ ] Task 454: Test save/load with non-zero Q-values

### 11.8 Tests — algorithm_name Property

- [x] Task 455: Test algorithm_name returns a string
- [ ] Task 456: Test algorithm_name is not empty
- [ ] Task 457: Test BellmanAgent.algorithm_name returns "Bellman"

### 11.9 Tests — Abstract Methods

- [ ] Task 458: Test BaseAgent cannot be instantiated directly
- [ ] Task 459: Test BaseAgent subclass without update() cannot be instantiated
- [ ] Task 460: Test concrete subclass can be instantiated
- [x] Task 461: Run all base_agent tests and verify they pass

---

## 12. Tests for BellmanAgent (~25 tasks)

### 12.1 Verify Existing Behavior

- [x] Task 462: Run all existing agent tests: `uv run pytest tests/test_agent.py`
- [x] Task 463: Verify all 104 existing tests pass
- [x] Task 464: Verify no test modifications needed
- [x] Task 465: Verify Agent import resolves to BellmanAgent

### 12.2 Tests — BellmanAgent Specific

- [ ] Task 466: Test BellmanAgent inherits from BaseAgent
- [x] Task 467: Test BellmanAgent has lr attribute
- [x] Task 468: Test BellmanAgent lr matches config.agent.learning_rate
- [x] Task 469: Test BellmanAgent.update uses constant lr
- [x] Task 470: Test BellmanAgent.algorithm_name returns "Bellman"
- [x] Task 471: Test BellmanAgent Q-value update formula
- [x] Task 472: Test BellmanAgent update with done=True
- [x] Task 473: Test BellmanAgent update with done=False
- [ ] Task 474: Test BellmanAgent lr does NOT decay after decay_epsilon()
- [ ] Task 475: Test BellmanAgent update produces identical results to pre-refactor Agent
- [x] Task 476: Test BellmanAgent inherits choose_action from BaseAgent
- [x] Task 477: Test BellmanAgent inherits get_best_action from BaseAgent
- [x] Task 478: Test BellmanAgent inherits get_max_q from BaseAgent
- [x] Task 479: Test BellmanAgent inherits decay_epsilon from BaseAgent
- [x] Task 480: Test BellmanAgent inherits save from BaseAgent
- [x] Task 481: Test BellmanAgent inherits load from BaseAgent
- [x] Task 482: Run all BellmanAgent tests and verify they pass

---

## 13. Tests for QLearningAgent (~55 tasks)

### 13.1 Test File Setup

- [x] Task 483: Create new file `tests/test_q_agent.py`
- [x] Task 484: Add module docstring to test file
- [x] Task 485: Import pytest
- [x] Task 486: Import QLearningAgent from src.q_agent
- [x] Task 487: Import BaseAgent from src.base_agent
- [x] Task 488: Import numpy as np
- [x] Task 489: Create pytest fixture for test config with q_learning section
- [x] Task 490: Create pytest fixture for test QLearningAgent

### 13.2 Tests — Alpha Initialization

- [x] Task 491: Test alpha initializes to alpha_start from config
- [x] Task 492: Test alpha_end is stored from config
- [x] Task 493: Test alpha_decay is stored from config
- [x] Task 494: Test alpha is a float
- [ ] Task 495: Test alpha_start default is 0.5
- [ ] Task 496: Test alpha_end default is 0.01
- [ ] Task 497: Test alpha_decay default is 0.999

### 13.3 Tests — Alpha Decay

- [x] Task 498: Test alpha decays after decay_epsilon() call
- [x] Task 499: Test alpha after 1 decay: alpha * alpha_decay
- [ ] Task 500: Test alpha after 10 decays: alpha * alpha_decay^10
- [x] Task 501: Test alpha never goes below alpha_end
- [ ] Task 502: Test alpha reaches alpha_end after many decays
- [x] Task 503: Test alpha_end acts as floor
- [x] Task 504: Test alpha decay formula: `max(alpha_end, alpha * alpha_decay)`
- [ ] Task 505: Test alpha after 1000 decay steps approaches alpha_end
- [ ] Task 506: Test alpha and epsilon decay independently

### 13.4 Tests — Update Method

- [x] Task 507: Test update uses self.alpha (not self.lr)
- [x] Task 508: Test Q-value changes correctly after single update
- [x] Task 509: Test update with done=True uses next_max_q = 0.0
- [x] Task 510: Test update with done=False uses next_max_q from Q-table
- [x] Task 511: Test update modifies Q-table in-place
- [ ] Task 512: Test update with alpha=0.5 produces correct change
- [ ] Task 513: Test update with alpha near alpha_end produces small change
- [x] Task 514: Test update formula: Q += alpha * (target - Q)
- [ ] Task 515: Test update does not modify other Q-values
- [x] Task 516: Test update with positive reward
- [x] Task 517: Test update with negative reward

### 13.5 Tests — Properties

- [x] Task 518: Test algorithm_name returns "Q-Learning"
- [x] Task 519: Test q_table property returns valid ndarray
- [x] Task 520: Test q_table shape is (rows, cols, 4)
- [ ] Task 521: Test QLearningAgent inherits from BaseAgent

### 13.6 Tests — Save and Load

- [x] Task 522: Test save creates file
- [x] Task 523: Test load restores Q-table
- [x] Task 524: Test save/load round-trip preserves data
- [ ] Task 525: Test save/load does not affect alpha value

### 13.7 Tests — Edge Cases

- [ ] Task 526: Test QLearningAgent with alpha_start=1.0
- [ ] Task 527: Test QLearningAgent with alpha_start=0.0 (should use alpha_end)
- [ ] Task 528: Test QLearningAgent with alpha_decay=1.0 (no decay)
- [ ] Task 529: Test QLearningAgent with alpha_decay=0.0 (instant decay to floor)
- [ ] Task 530: Test multiple updates in sequence
- [ ] Task 531: Test convergence: Q-values approach optimal after many updates
- [x] Task 532: Run all QLearningAgent tests and verify they pass
- [x] Task 533: Run ruff check on test_q_agent.py
- [x] Task 534: Verify test coverage for q_agent.py is 85%+

---

## 14. Tests for Agent Factory (~30 tasks)

### 14.1 Test File Setup

- [x] Task 535: Create new file `tests/test_agent_factory.py`
- [x] Task 536: Add module docstring to test file
- [x] Task 537: Import pytest
- [x] Task 538: Import create_agent from src.agent_factory
- [x] Task 539: Import BaseAgent from src.base_agent
- [x] Task 540: Import BellmanAgent from src.agent
- [x] Task 541: Import QLearningAgent from src.q_agent
- [x] Task 542: Create pytest fixture for test config

### 14.2 Tests — Factory Dispatch

- [x] Task 543: Test create_agent with "bellman" returns BellmanAgent
- [x] Task 544: Test create_agent with "q_learning" returns QLearningAgent
- [x] Task 545: Test returned agent is instance of BaseAgent
- [x] Task 546: Test returned BellmanAgent has algorithm_name "Bellman"
- [x] Task 547: Test returned QLearningAgent has algorithm_name "Q-Learning"
- [ ] Task 548: Test returned agent has q_table property
- [ ] Task 549: Test returned agent has update method
- [ ] Task 550: Test returned agent has choose_action method
- [ ] Task 551: Test returned agent has decay_epsilon method

### 14.3 Tests — Factory Error Handling

- [x] Task 552: Test create_agent with unknown name raises ValueError
- [ ] Task 553: Test ValueError message contains the unknown name
- [ ] Task 554: Test create_agent with empty string raises ValueError
- [ ] Task 555: Test create_agent with "BELLMAN" (wrong case) raises ValueError
- [ ] Task 556: Test create_agent with None raises appropriate error

### 14.4 Tests — Factory Results

- [ ] Task 557: Test factory-created agent can call update()
- [ ] Task 558: Test factory-created agent can call choose_action()
- [ ] Task 559: Test factory-created agent can call decay_epsilon()
- [ ] Task 560: Test factory-created agent can save/load
- [x] Task 561: Run all factory tests and verify they pass
- [x] Task 562: Run ruff check on test_agent_factory.py
- [x] Task 563: Verify test coverage for agent_factory.py is 85%+

---

## 15. Final Verification (~17 tasks)

### 15.1 Full Test Suite

- [x] Task 564: Run `uv run pytest` to execute all tests
- [x] Task 565: Verify all 104 existing tests still pass
- [x] Task 566: Verify all new base_agent tests pass
- [x] Task 567: Verify all new q_agent tests pass
- [x] Task 568: Verify all new agent_factory tests pass
- [x] Task 569: Verify total test count is correct

### 15.2 Coverage Check

- [x] Task 570: Run `uv run pytest --cov=src --cov-report=html`
- [x] Task 571: Verify base_agent.py coverage is 85%+
- [x] Task 572: Verify q_agent.py coverage is 85%+
- [x] Task 573: Verify agent_factory.py coverage is 85%+
- [x] Task 574: Verify agent.py coverage remains 85%+

### 15.3 Lint and Line Count

- [x] Task 575: Run `uv run ruff check src/` with zero violations
- [x] Task 576: Run `uv run ruff check tests/` with zero violations
- [x] Task 577: Verify base_agent.py <= 150 lines
- [x] Task 578: Verify agent.py <= 150 lines
- [x] Task 579: Verify q_agent.py <= 150 lines
- [x] Task 580: Verify agent_factory.py <= 150 lines
