## BaseAgent File Setup

- [x] Task 1: Create src/base_agent.py module file
- [x] Task 2: Add module docstring describing BaseAgent purpose
- [x] Task 3: Import numpy as np in base_agent.py
- [x] Task 4: Import Path from pathlib for save/load
- [x] Task 5: Import Tuple type hint for coordinates
- [x] Task 6: Import Optional type hint for config
- [x] Task 7: Import config loader from src.config_loader
- [x] Task 8: Add UTF-8 encoding comment if needed
- [x] Task 9: Ensure file stays under 150 lines
- [x] Task 10: Add ruff-compatible imports ordering
- [x] Task 11: Remove unused imports from base_agent.py
- [x] Task 12: Add __all__ export list with BaseAgent
- [x] Task 13: Verify no circular imports with config_loader
- [x] Task 14: Ensure base_agent.py is discoverable by src package
- [x] Task 15: Add base_agent.py to src/__init__.py if needed

## BaseAgent Class Definition

- [x] Task 16: Define class BaseAgent with no inheritance
- [x] Task 17: Add NUM_ACTIONS class constant equal to 4
- [x] Task 18: Add algorithm_name class attribute set to Base
- [x] Task 19: Add class-level docstring explaining role
- [x] Task 20: Document NUM_ACTIONS represents up/down/left/right
- [x] Task 21: Document algorithm_name overridden by subclasses
- [x] Task 22: Document class as abstract-like base
- [x] Task 23: Do NOT use ABC or abstractmethod decorators
- [x] Task 24: Enforce abstract behavior via NotImplementedError
- [x] Task 25: Document design choice to avoid ABC
- [x] Task 26: Keep class attribute naming consistent
- [x] Task 27: Expose NUM_ACTIONS as public constant
- [x] Task 28: Ensure class is importable from src.base_agent
- [x] Task 29: Add type hints on all class attributes
- [x] Task 30: Confirm algorithm_name appears in __repr__

## BaseAgent __init__ From Config

- [x] Task 31: Define __init__ with optional config parameter
- [x] Task 32: Load config via get_config() when config is None
- [x] Task 33: Store self.config reference for later use
- [x] Task 34: Read grid_width from config.environment.grid_width
- [x] Task 35: Read grid_height from config.environment.grid_height
- [x] Task 36: Store self.grid_width attribute
- [x] Task 37: Store self.grid_height attribute
- [x] Task 38: Read discount factor from config.agent.discount_factor
- [x] Task 39: Store self.gamma attribute
- [x] Task 40: Read epsilon_start from config.agent.epsilon_start
- [x] Task 41: Store self.epsilon attribute
- [x] Task 42: Read epsilon_end from config.agent.epsilon_end
- [x] Task 43: Store self.epsilon_end attribute
- [x] Task 44: Read epsilon_decay from config.agent.epsilon_decay
- [x] Task 45: Store self.epsilon_decay attribute
- [x] Task 46: Initialize Q-table via initialize_q_table helper
- [x] Task 47: Store shape (W, H, NUM_ACTIONS) for Q-table
- [x] Task 48: Validate grid dimensions are positive integers
- [x] Task 49: Validate discount_factor is in [0, 1]
- [x] Task 50: Validate epsilon_start is in [0, 1]
- [x] Task 51: Validate epsilon_end is in [0, 1]
- [x] Task 52: Validate epsilon_decay is in (0, 1]
- [x] Task 53: Seed numpy RNG via configured random_seed
- [x] Task 54: Keep __init__ under 30 lines
- [x] Task 55: Extract config reading into helper if needed

## BaseAgent Q-Table Initialization

- [x] Task 56: Use np.zeros for Q-table initialization
- [x] Task 57: Use dtype=np.float32 for Q-table
- [x] Task 58: Store as self.q_table attribute
- [x] Task 59: Ensure Q-table shape matches (W, H, NUM_ACTIONS)
- [x] Task 60: Expose Q-table as numpy ndarray
- [x] Task 61: Allow external reset of Q-table to zeros
- [x] Task 62: Document Q-table axis meanings in docstring
- [x] Task 63: Avoid Python lists for Q-table performance
- [x] Task 64: Ensure Q-table is mutable in-place
- [x] Task 65: Keep Q-table private enough for subclasses

## BaseAgent choose_action Epsilon-Greedy

- [x] Task 66: Define choose_action(state) method
- [x] Task 67: Accept state as Tuple[int, int]
- [x] Task 68: Return integer action in [0, NUM_ACTIONS)
- [x] Task 69: Draw random float via np.random.rand
- [x] Task 70: If rand < epsilon return np.random.randint
- [x] Task 71: Otherwise return get_best_action(state)
- [x] Task 72: Ensure choose_action never raises on valid state
- [x] Task 73: Handle edge state at grid corner
- [x] Task 74: Clip state into grid bounds if out-of-range
- [x] Task 75: Document exploration vs exploitation behavior
- [x] Task 76: Avoid hardcoded action counts use NUM_ACTIONS
- [x] Task 77: Type-hint return as int
- [x] Task 78: Keep choose_action under 15 lines
- [x] Task 79: Make choose_action fully deterministic when seed set
- [x] Task 80: Expose choose_action as public API

## BaseAgent get_best_action Argmax

- [x] Task 81: Define get_best_action(state) method
- [x] Task 82: Accept state as Tuple[int, int]
- [x] Task 83: Extract row, col from state
- [x] Task 84: Read self.q_table[row, col] action vector
- [x] Task 85: Call np.argmax on action vector
- [x] Task 86: Cast argmax result to int
- [x] Task 87: Return integer action
- [x] Task 88: Document ties broken by first-max rule
- [x] Task 89: Ensure method returns int not np.int64
- [x] Task 90: Keep method under 10 lines

## BaseAgent get_max_q

- [x] Task 91: Define get_max_q(state) method
- [x] Task 92: Accept state as Tuple[int, int]
- [x] Task 93: Extract row, col from state
- [x] Task 94: Read self.q_table[row, col] action vector
- [x] Task 95: Call np.max on action vector
- [x] Task 96: Cast result to float
- [x] Task 97: Return float max Q-value
- [x] Task 98: Document get_max_q used by update rule
- [x] Task 99: Ensure numerical stability with float32
- [x] Task 100: Keep method under 10 lines

## BaseAgent update Raises NotImplementedError

- [x] Task 101: Define update method on BaseAgent
- [x] Task 102: Accept state, action, reward, next_state, done
- [x] Task 103: Raise NotImplementedError inside method body
- [x] Task 104: Include helpful error message naming subclass
- [x] Task 105: Do NOT use @abstractmethod decorator
- [x] Task 106: Document that subclasses must override update
- [x] Task 107: Ensure signature matches subclass update
- [x] Task 108: Type-hint state as Tuple[int, int]
- [x] Task 109: Type-hint action as int
- [x] Task 110: Type-hint reward as float
- [x] Task 111: Type-hint next_state as Tuple[int, int]
- [x] Task 112: Type-hint done as bool
- [x] Task 113: Return type hint None
- [x] Task 114: Reference subclass requirement in docstring
- [x] Task 115: Keep stub under 10 lines

## BaseAgent decay_epsilon

- [x] Task 116: Define decay_epsilon method
- [x] Task 117: Multiply self.epsilon by self.epsilon_decay
- [x] Task 118: Floor epsilon at self.epsilon_end via max
- [x] Task 119: Store updated epsilon back to attribute
- [x] Task 120: Document decay called once per episode
- [x] Task 121: Ensure epsilon never goes below epsilon_end
- [x] Task 122: Ensure epsilon never exceeds epsilon_start
- [x] Task 123: Avoid hardcoded decay constants
- [x] Task 124: Keep method under 5 lines
- [x] Task 125: Add return type None

## BaseAgent save/load With Path.mkdir

- [x] Task 126: Define save(path) method on BaseAgent
- [x] Task 127: Convert path string to Path object
- [x] Task 128: Call Path.mkdir(parents=True, exist_ok=True) on parent
- [x] Task 129: Use np.save to persist Q-table
- [x] Task 130: Define load(path) method on BaseAgent
- [x] Task 131: Convert path string to Path object in load
- [x] Task 132: Use np.load to retrieve Q-table
- [x] Task 133: Assign loaded array to self.q_table
- [x] Task 134: Raise FileNotFoundError when path missing
- [x] Task 135: Keep save under 10 lines
- [x] Task 136: Keep load under 10 lines
- [x] Task 137: Document save/load format as .npy
- [x] Task 138: Ensure load validates shape matches grid
- [x] Task 139: Allow save path without extension
- [x] Task 140: Default save to config.paths.models when needed

## BellmanAgent Refactor From Original Agent

- [x] Task 141: Move Agent class from src/agent.py to src/agent.py
- [x] Task 142: Rename Agent class to BellmanAgent
- [x] Task 143: Inherit BellmanAgent from BaseAgent
- [x] Task 144: Remove Q-table init from BellmanAgent __init__
- [x] Task 145: Remove epsilon logic from BellmanAgent __init__
- [x] Task 146: Call super().__init__ from BellmanAgent __init__
- [x] Task 147: Remove duplicated choose_action from BellmanAgent
- [x] Task 148: Remove duplicated get_best_action from BellmanAgent
- [x] Task 149: Remove duplicated get_max_q from BellmanAgent
- [x] Task 150: Remove duplicated decay_epsilon from BellmanAgent
- [x] Task 151: Remove duplicated save from BellmanAgent
- [x] Task 152: Remove duplicated load from BellmanAgent
- [x] Task 153: Ensure BellmanAgent file remains under 150 lines
- [x] Task 154: Reorganize imports in src/agent.py
- [x] Task 155: Remove now-unused imports in src/agent.py

## BellmanAgent Constant Learning Rate

- [x] Task 156: Set algorithm_name="Bellman" on BellmanAgent
- [x] Task 157: Read learning_rate from config.agent.learning_rate
- [x] Task 158: Store self.lr attribute in BellmanAgent
- [x] Task 159: Document lr as constant not decaying
- [x] Task 160: Validate lr is positive float
- [x] Task 161: Validate lr is less than or equal to 1
- [x] Task 162: Default lr to 0.1 in config
- [x] Task 163: Keep lr attribute immutable after init
- [x] Task 164: Do NOT expose decay_alpha on BellmanAgent
- [x] Task 165: Confirm BellmanAgent.decay_epsilon only decays epsilon

## BellmanAgent Update Formula

- [x] Task 166: Override update method in BellmanAgent
- [x] Task 167: Compute current_q = q_table[row, col, action]
- [x] Task 168: Compute max_next_q via get_max_q(next_state)
- [x] Task 169: Compute target = reward + gamma * max_next_q
- [x] Task 170: Zero target when done is True
- [x] Task 171: Compute td_error = target - current_q
- [x] Task 172: Update q_table[row, col, action] += lr * td_error
- [x] Task 173: Use self.lr not hardcoded learning rate
- [x] Task 174: Use self.gamma from base class
- [x] Task 175: Ensure update handles terminal states correctly
- [x] Task 176: Confirm update signature matches BaseAgent
- [x] Task 177: Add update method docstring referencing Bellman eq
- [x] Task 178: Keep update method under 15 lines
- [x] Task 179: Return None from update method
- [x] Task 180: Ensure update does not call decay_epsilon

## BellmanAgent Backward-Compat Agent Alias

- [x] Task 181: Add line Agent = BellmanAgent at module scope
- [x] Task 182: Place alias after BellmanAgent definition
- [x] Task 183: Export Agent via __all__ list
- [x] Task 184: Document alias for Assignment 1 backward compat
- [x] Task 185: Verify Agent import still works in main.py
- [x] Task 186: Verify Agent import still works in sdk.py
- [x] Task 187: Verify Agent import still works in tests
- [x] Task 188: Ensure from src.agent import Agent passes
- [x] Task 189: Ensure from src.agent import BellmanAgent passes
- [x] Task 190: Keep alias close to class for discoverability

## QLearningAgent File Setup

- [x] Task 191: Create src/q_agent.py module file
- [x] Task 192: Add module docstring explaining Q-Learning
- [x] Task 193: Import numpy as np in q_agent.py
- [x] Task 194: Import BaseAgent from src.base_agent
- [x] Task 195: Import Optional for config type hint
- [x] Task 196: Import Tuple for state type hint
- [x] Task 197: Add __all__ list containing QLearningAgent
- [x] Task 198: Ensure file under 150 lines
- [x] Task 199: Keep imports sorted per ruff rules
- [x] Task 200: Add q_agent module to src package

## QLearningAgent Class With Decaying Alpha

- [x] Task 201: Define class QLearningAgent(BaseAgent)
- [x] Task 202: Set algorithm_name="Q-Learning"
- [x] Task 203: Override __init__ to accept optional config
- [x] Task 204: Call super().__init__(config) in first line
- [x] Task 205: Document decaying alpha requirement
- [x] Task 206: Document divergence risk if alpha constant
- [x] Task 207: Ensure class is importable as QLearningAgent
- [x] Task 208: Keep class under 100 lines
- [x] Task 209: Document Q-Learning off-policy update rule
- [x] Task 210: Mark class as concrete implementation

## QLearningAgent alpha_start/end/decay Loading

- [x] Task 211: Read alpha_start from config.q_learning.alpha_start
- [x] Task 212: Read alpha_end from config.q_learning.alpha_end
- [x] Task 213: Read alpha_decay from config.q_learning.alpha_decay
- [x] Task 214: Store self.alpha initialized to alpha_start
- [x] Task 215: Store self.alpha_start attribute
- [x] Task 216: Store self.alpha_end attribute
- [x] Task 217: Store self.alpha_decay attribute
- [x] Task 218: Validate alpha_start in (0, 1]
- [x] Task 219: Validate alpha_end in [0, 1]
- [x] Task 220: Validate alpha_decay in (0, 1]
- [x] Task 221: Ensure alpha_end less than alpha_start
- [x] Task 222: Default alpha_start to 0.5 in config
- [x] Task 223: Default alpha_end to 0.05 in config
- [x] Task 224: Default alpha_decay to 0.9995 in config
- [x] Task 225: Document alpha fields in q_learning config section

## QLearningAgent decay_alpha Method

- [x] Task 226: Define decay_alpha method on QLearningAgent
- [x] Task 227: Multiply self.alpha by self.alpha_decay
- [x] Task 228: Floor self.alpha at self.alpha_end via max
- [x] Task 229: Store updated alpha back to attribute
- [x] Task 230: Document decay_alpha called per episode
- [x] Task 231: Keep method under 5 lines
- [x] Task 232: Return None from decay_alpha
- [x] Task 233: Ensure alpha never drops below alpha_end
- [x] Task 234: Ensure alpha never exceeds alpha_start
- [x] Task 235: Expose decay_alpha as public method

## QLearningAgent Override decay_epsilon

- [x] Task 236: Override decay_epsilon on QLearningAgent
- [x] Task 237: Call super().decay_epsilon() first
- [x] Task 238: Then call self.decay_alpha()
- [x] Task 239: Ensure both decays happen per episode
- [x] Task 240: Document override reason in docstring
- [x] Task 241: Avoid duplicating epsilon decay logic
- [x] Task 242: Return None from overridden method
- [x] Task 243: Keep method under 5 lines
- [x] Task 244: Keep order super() before decay_alpha
- [x] Task 245: Test override preserves base behavior

## QLearningAgent Update Uses Current Alpha

- [x] Task 246: Override update method in QLearningAgent
- [x] Task 247: Compute current_q = q_table[row, col, action]
- [x] Task 248: Compute max_next_q via get_max_q(next_state)
- [x] Task 249: Compute target = reward + gamma * max_next_q
- [x] Task 250: Zero target when done is True
- [x] Task 251: Compute td_error = target - current_q
- [x] Task 252: Update q_table[row, col, action] += alpha * td_error
- [x] Task 253: Use self.alpha not self.lr
- [x] Task 254: Ensure alpha reflects current decayed value
- [x] Task 255: Keep update under 15 lines
- [x] Task 256: Match BaseAgent update signature exactly
- [x] Task 257: Document update rule in docstring
- [x] Task 258: Ensure update handles terminal next_state
- [x] Task 259: Return None from update
- [x] Task 260: Add update method type hints

## Agent Factory Creation

- [x] Task 261: Create src/agent_factory.py module
- [x] Task 262: Add module docstring explaining factory
- [x] Task 263: Import BellmanAgent from src.agent
- [x] Task 264: Import QLearningAgent from src.q_agent
- [x] Task 265: Import BaseAgent for return type hint
- [x] Task 266: Define create_agent(config) function
- [x] Task 267: Read config.algorithm.name from config
- [x] Task 268: Normalize algorithm name to lowercase
- [x] Task 269: Return BaseAgent subclass instance
- [x] Task 270: Pass config to constructor
- [x] Task 271: Keep file under 80 lines
- [x] Task 272: Export create_agent via __all__
- [x] Task 273: Ensure no circular imports
- [x] Task 274: Document factory usage in docstring
- [x] Task 275: Allow None config as default

## Factory Dict-Based Algorithm Registry

- [x] Task 276: Define ALGORITHM_REGISTRY (tuple of AlgorithmSpec) in src/algorithms.py
- [x] Task 277: Map key bellman to BellmanAgent class
- [x] Task 278: Map key q_learning to QLearningAgent class
- [x] Task 279: Map key double_q to DoubleQAgent class
- [x] Task 280: Import DoubleQAgent in agent_factory.py
- [x] Task 281: Keep registry as module-level constant
- [x] Task 282: Use lowercase keys only in registry
- [x] Task 283: Document registry format in module docstring
- [x] Task 284: Expose ALGORITHM_REGISTRY, ALGORITHMS, and AGENT_CLASSES for downstream consumers
- [x] Task 285: Lookup class via registry[name] in factory
- [x] Task 286: Instantiate class via cls(config)
- [x] Task 287: Return instance from factory
- [x] Task 288: Keep registry sorted alphabetically
- [x] Task 289: Avoid if/elif ladder for algorithm selection
- [x] Task 290: Allow adding new algorithms without code edits

## Factory ValueError With Valid Algorithms List

- [x] Task 291: Raise ValueError when name not in registry
- [x] Task 292: Include offending name in ValueError message
- [x] Task 293: Include list of valid names in message
- [x] Task 294: Format valid names as comma-separated list
- [x] Task 295: Sort valid names alphabetically in message
- [x] Task 296: Use f-string for ValueError message
- [x] Task 297: Prefix message with Unknown algorithm
- [x] Task 298: Document error behavior in factory docstring
- [x] Task 299: Test ValueError raised for empty string
- [x] Task 300: Test ValueError raised for unknown name

## Config Algorithm Section

- [x] Task 301: Add algorithm section to config/config.yaml
- [x] Task 302: Add algorithm.name key in config
- [x] Task 303: Default algorithm.name to bellman
- [x] Task 304: Document allowed values as comment
- [x] Task 305: List bellman, q_learning, double_q as valid
- [x] Task 306: Ensure config loader exposes algorithm.name
- [x] Task 307: Add default handling when section missing
- [x] Task 308: Validate algorithm.name is a string
- [x] Task 309: Lowercase algorithm.name on read
- [x] Task 310: Surface config.algorithm.name to SDK

## Config q_learning Section

- [x] Task 311: Add q_learning section to config.yaml
- [x] Task 312: Add q_learning.alpha_start key
- [x] Task 313: Add q_learning.alpha_end key
- [x] Task 314: Add q_learning.alpha_decay key
- [x] Task 315: Document each key with inline comment
- [x] Task 316: Ensure config loader exposes q_learning section
- [x] Task 317: Validate q_learning section exists on load
- [x] Task 318: Add default q_learning section if absent
- [x] Task 319: Expose q_learning via dotted access
- [x] Task 320: Keep q_learning fields as floats

## Config Defaults

- [x] Task 321: Set agent.learning_rate default to 0.1
- [x] Task 322: Set agent.discount_factor default to 0.95
- [x] Task 323: Set agent.epsilon_start default to 1.0
- [x] Task 324: Set agent.epsilon_end default to 0.01
- [x] Task 325: Set agent.epsilon_decay default to 0.995
- [x] Task 326: Set q_learning.alpha_start default to 0.5
- [x] Task 327: Set q_learning.alpha_end default to 0.05
- [x] Task 328: Set q_learning.alpha_decay default to 0.9995
- [x] Task 329: Match defaults across PRD and code
- [x] Task 330: Keep defaults consistent between algorithms
- [x] Task 331: Avoid overrides in local config files
- [x] Task 332: Validate defaults on config load
- [x] Task 333: Document defaults in README or comments
- [x] Task 334: Test defaults via unit test
- [x] Task 335: Document defaults in PRD_q_learning.md

## SDK Uses create_agent

- [x] Task 336: Import create_agent in src/sdk.py
- [x] Task 337: Replace Agent() instantiation with create_agent(config)
- [x] Task 338: Store agent as self.agent on SDK init
- [x] Task 339: Type-annotate self.agent as BaseAgent
- [x] Task 340: Call create_agent in SDK.reset()
- [x] Task 341: Ensure SDK.reset rebuilds agent from config
- [x] Task 342: Preserve existing SDK API surface
- [x] Task 343: Remove any hardcoded Agent references
- [x] Task 344: Ensure SDK works with BellmanAgent
- [x] Task 345: Ensure SDK works with QLearningAgent
- [x] Task 346: Ensure SDK works with DoubleQAgent
- [x] Task 347: Keep SDK file under 150 lines
- [x] Task 348: Add BaseAgent import in sdk.py
- [x] Task 349: Avoid double-instantiation in __init__
- [x] Task 350: Test SDK agent type matches config.algorithm.name

## SDK switch_algorithm

- [x] Task 351: Add switch_algorithm(name) method to SDK
- [x] Task 352: Validate name via create_agent prior to set
- [x] Task 353: Update config.algorithm.name to provided value
- [x] Task 354: Call self.reset() after switching
- [x] Task 355: Ensure new agent type reflects switch
- [x] Task 356: Return new agent instance or None
- [x] Task 357: Document switch_algorithm in docstring
- [x] Task 358: Reject unknown name with ValueError
- [x] Task 359: Persist name to config in-memory only
- [x] Task 360: Keep switch_algorithm under 15 lines
- [x] Task 361: Test switch_algorithm from bellman to q_learning
- [x] Task 362: Test switch_algorithm from q_learning to double_q
- [x] Task 363: Test switch_algorithm preserves env
- [x] Task 364: Test switch_algorithm resets agent Q-table
- [x] Task 365: Expose switch_algorithm via SDK public API

## Trainer Uses BaseAgent Type Annotation

- [x] Task 366: Import BaseAgent in src/trainer.py
- [x] Task 367: Annotate trainer.agent as BaseAgent
- [x] Task 368: Replace Agent type hint with BaseAgent
- [x] Task 369: Ensure Trainer accepts any BaseAgent subclass
- [x] Task 370: Update Trainer constructor signature
- [x] Task 371: Update Trainer method signatures
- [x] Task 372: Remove legacy Agent-only assumptions
- [x] Task 373: Verify Trainer works with BellmanAgent
- [x] Task 374: Verify Trainer works with QLearningAgent
- [x] Task 375: Verify Trainer calls decay_epsilon per episode
- [x] Task 376: Trainer auto-invokes alpha decay via override
- [x] Task 377: Keep Trainer file under 150 lines
- [x] Task 378: Document Trainer agent-agnostic design
- [x] Task 379: Ensure Trainer imports do not break Assignment 1
- [x] Task 380: Keep existing Trainer tests passing

## GameLogic Uses BaseAgent Type Annotation

- [x] Task 381: Import BaseAgent in src/game_logic.py
- [x] Task 382: Annotate agent parameter as BaseAgent
- [x] Task 383: Replace Agent type hint with BaseAgent
- [x] Task 384: Ensure GameLogic accepts subclass instances
- [x] Task 385: Update GameLogic public methods signatures
- [x] Task 386: Keep GameLogic file under 150 lines
- [x] Task 387: Ensure GameLogic tests still pass
- [x] Task 388: Document GameLogic agent-agnostic design
- [x] Task 389: Remove legacy Agent-specific assumptions
- [x] Task 390: Preserve backward compat via Agent alias

## Tests For BaseAgent

- [x] Task 391: Create tests/test_base_agent.py file
- [x] Task 392: Import pytest in test_base_agent.py
- [x] Task 393: Import BaseAgent in test_base_agent.py
- [x] Task 394: Add fixture for default config
- [x] Task 395: Test BaseAgent NUM_ACTIONS equals 4
- [x] Task 396: Test BaseAgent algorithm_name equals Base
- [x] Task 397: Test __init__ loads grid_width from config
- [x] Task 398: Test __init__ loads grid_height from config
- [x] Task 399: Test __init__ initializes Q-table shape
- [x] Task 400: Test Q-table dtype is float32
- [x] Task 401: Test Q-table initially all zeros
- [x] Task 402: Test __init__ reads discount_factor
- [x] Task 403: Test __init__ reads epsilon_start
- [x] Task 404: Test __init__ reads epsilon_end
- [x] Task 405: Test __init__ reads epsilon_decay
- [x] Task 406: Test choose_action returns int in range
- [x] Task 407: Test choose_action greedy when epsilon 0
- [x] Task 408: Test choose_action random when epsilon 1
- [x] Task 409: Test choose_action uses np.random
- [x] Task 410: Test get_best_action returns argmax
- [x] Task 411: Test get_best_action returns int not numpy int
- [x] Task 412: Test get_max_q returns float
- [x] Task 413: Test get_max_q matches np.max of slice
- [x] Task 414: Test update raises NotImplementedError on BaseAgent
- [x] Task 415: Test update error message mentions subclass
- [x] Task 416: Test decay_epsilon multiplies by epsilon_decay
- [x] Task 417: Test decay_epsilon floors at epsilon_end
- [x] Task 418: Test decay_epsilon never exceeds epsilon_start
- [x] Task 419: Test save creates .npy file
- [x] Task 420: Test save creates parent directory
- [x] Task 421: Test save via Path.mkdir with parents True
- [x] Task 422: Test load restores Q-table shape
- [x] Task 423: Test load restores Q-table values
- [x] Task 424: Test load raises FileNotFoundError on missing
- [x] Task 425: Test save/load round trip preserves values
- [x] Task 426: Test BaseAgent does NOT use ABC
- [x] Task 427: Test BaseAgent cannot be trained via update
- [x] Task 428: Test BaseAgent choose_action at state 0,0
- [x] Task 429: Test BaseAgent choose_action at grid corner
- [x] Task 430: Test BaseAgent attribute types

## Tests For BellmanAgent

- [x] Task 431: Ensure tests/test_agent.py imports BellmanAgent
- [x] Task 432: Test BellmanAgent algorithm_name equals Bellman
- [x] Task 433: Test BellmanAgent inherits from BaseAgent
- [x] Task 434: Test BellmanAgent lr reads from config
- [x] Task 435: Test BellmanAgent lr default equals 0.1
- [x] Task 436: Test BellmanAgent lr constant across episodes
- [x] Task 437: Test BellmanAgent update modifies Q-table
- [x] Task 438: Test BellmanAgent update applies td_error
- [x] Task 439: Test BellmanAgent update uses gamma
- [x] Task 440: Test BellmanAgent update handles done True
- [x] Task 441: Test BellmanAgent update matches Bellman eq
- [x] Task 442: Test BellmanAgent does NOT decay alpha
- [x] Task 443: Test Agent alias equals BellmanAgent
- [x] Task 444: Test from src.agent import Agent works
- [x] Task 445: Test from src.agent import BellmanAgent works
- [x] Task 446: Test BellmanAgent inherits choose_action from base
- [x] Task 447: Test BellmanAgent inherits decay_epsilon from base
- [x] Task 448: Test BellmanAgent save/load works
- [x] Task 449: Test BellmanAgent Q-table shape unchanged
- [x] Task 450: Test BellmanAgent passes existing Assignment 1 tests

## Tests For QLearningAgent

- [x] Task 451: Create tests/test_q_agent.py file
- [x] Task 452: Import pytest in test_q_agent.py
- [x] Task 453: Import QLearningAgent in test_q_agent.py
- [x] Task 454: Test QLearningAgent algorithm_name equals Q-Learning
- [x] Task 455: Test QLearningAgent inherits from BaseAgent
- [x] Task 456: Test QLearningAgent alpha reads from config
- [x] Task 457: Test QLearningAgent alpha_start default 0.5
- [x] Task 458: Test QLearningAgent alpha_end default 0.05
- [x] Task 459: Test QLearningAgent alpha_decay default 0.9995
- [x] Task 460: Test QLearningAgent decay_alpha reduces alpha
- [x] Task 461: Test QLearningAgent decay_alpha floors at alpha_end
- [x] Task 462: Test QLearningAgent decay_epsilon decays both
- [x] Task 463: Test decay_epsilon calls super first
- [x] Task 464: Test decay_epsilon then calls decay_alpha
- [x] Task 465: Test QLearningAgent update uses current alpha
- [x] Task 466: Test QLearningAgent update modifies Q-table
- [x] Task 467: Test QLearningAgent update after decay uses new alpha
- [x] Task 468: Test QLearningAgent update handles done True
- [x] Task 469: Test QLearningAgent update uses gamma
- [x] Task 470: Test QLearningAgent alpha starts at alpha_start
- [x] Task 471: Test QLearningAgent alpha never below alpha_end
- [x] Task 472: Test QLearningAgent alpha monotonically decreasing
- [x] Task 473: Test QLearningAgent 10k decays reach alpha_end
- [x] Task 474: Test QLearningAgent save/load works
- [x] Task 475: Test QLearningAgent inherits choose_action
- [x] Task 476: Test QLearningAgent inherits get_best_action
- [x] Task 477: Test QLearningAgent inherits get_max_q
- [x] Task 478: Test QLearningAgent Q-table shape matches config
- [x] Task 479: Test QLearningAgent convergence on noisy env
- [x] Task 480: Test QLearningAgent outperforms Bellman in noise

## Tests For Factory

- [x] Task 481: Create tests/test_agent_factory.py file
- [x] Task 482: Import pytest in test_agent_factory.py
- [x] Task 483: Import create_agent in test_agent_factory.py
- [x] Task 484: Import BellmanAgent for type assertions
- [x] Task 485: Import QLearningAgent for type assertions
- [x] Task 486: Import DoubleQAgent for type assertions
- [x] Task 487: Test create_agent with name bellman returns BellmanAgent
- [x] Task 488: Test create_agent with name q_learning returns QLearningAgent
- [x] Task 489: Test create_agent with name double_q returns DoubleQAgent
- [x] Task 490: Test create_agent raises ValueError on unknown
- [x] Task 491: Test ValueError message includes unknown name
- [x] Task 492: Test ValueError message includes valid list
- [x] Task 493: Test valid list contains bellman
- [x] Task 494: Test valid list contains q_learning
- [x] Task 495: Test valid list contains double_q
- [x] Task 496: Test create_agent handles uppercase name
- [x] Task 497: Test create_agent handles mixed-case name
- [x] Task 498: Test create_agent empty string raises ValueError
- [x] Task 499: Test ALGORITHMS exposes every registered algorithm name
- [x] Task 500: Test ALGORITHM_REGISTRY is a tuple of AlgorithmSpec entries
- [x] Task 501: Test ALGORITHM_REGISTRY entry names are lowercase identifiers
- [x] Task 502: Test registry values are class references
- [x] Task 503: Test registry values are BaseAgent subclasses
- [x] Task 504: Test create_agent passes config to constructor
- [x] Task 505: Test create_agent default config reads from loader
- [x] Task 506: Test adding new algorithm to registry works
- [x] Task 507: Test create_agent returns BaseAgent instance
- [x] Task 508: Test create_agent matches algorithm.name attribute
- [x] Task 509: Test no circular imports on factory load
- [x] Task 510: Test factory works with None config

## Tests For SDK Integration

- [x] Task 511: Update tests/test_sdk.py to use factory
- [x] Task 512: Test SDK init creates agent via create_agent
- [x] Task 513: Test SDK.agent type matches config.algorithm.name
- [x] Task 514: Test SDK.reset recreates agent from config
- [x] Task 515: Test SDK.switch_algorithm bellman to q_learning
- [x] Task 516: Test SDK.switch_algorithm q_learning to double_q
- [x] Task 517: Test SDK.switch_algorithm unknown raises ValueError
- [x] Task 518: Test SDK.switch_algorithm resets environment
- [x] Task 519: Test SDK.switch_algorithm updates config in memory
- [x] Task 520: Test SDK with BellmanAgent still passes Assignment 1
- [x] Task 521: Test SDK with QLearningAgent trains successfully
- [x] Task 522: Test SDK with DoubleQAgent trains successfully
- [x] Task 523: Test SDK agent attribute is BaseAgent subclass
- [x] Task 524: Test SDK switch preserves grid state
- [x] Task 525: Test SDK switch preserves rewards config
- [x] Task 526: Test SDK single-step works after switch
- [x] Task 527: Test SDK train episode after switch
- [x] Task 528: Test SDK exposes algorithm_name via agent
- [x] Task 529: Test SDK GUI receives correct agent type
- [x] Task 530: Test SDK saves correct agent to disk
- [x] Task 531: Test SDK load restores correct agent type
- [x] Task 532: Test SDK end-to-end Bellman run unchanged
- [x] Task 533: Test SDK end-to-end Q-Learning run works
- [x] Task 534: Test SDK end-to-end Double Q run works
- [x] Task 535: Test SDK comparison scenario medium difficulty
- [x] Task 536: Test SDK comparison scenario high difficulty
- [x] Task 537: Test SDK ruff clean after refactor
- [x] Task 538: Test SDK coverage above 85 percent
- [x] Task 539: Test SDK file remains under 150 lines
- [x] Task 540: Test SDK imports do not break main.py
- [x] Task 541: Test SDK backward-compat with Agent alias
- [x] Task 542: Test SDK config reload rebuilds agent
- [x] Task 543: Test SDK multiple switches in sequence
- [x] Task 544: Test SDK agent isolation between instances
- [x] Task 545: Test SDK save path uses config.paths.models
- [x] Task 546: Test SDK agent.algorithm_name logged correctly
- [x] Task 547: Test SDK training metrics populated for Q-Learning
- [x] Task 548: Test SDK alpha decay observable through SDK
- [x] Task 549: Test SDK epsilon decay observable through SDK
- [x] Task 550: Run uv run pytest tests/ and confirm all pass
- [x] Task 551: Run uv run ruff check src/ tests/ main.py with zero errors
- [x] Task 552: Run uv run pytest tests/ --cov=src --cov-report=term-missing
- [x] Task 553: Confirm combined coverage above 85 percent
- [x] Task 554: Confirm no file exceeds 150 lines
- [x] Task 555: Confirm no hardcoded values remain in src
- [x] Task 556: Confirm OOP inheritance chain BaseAgent to subclasses
- [x] Task 557: Confirm TDD RED to GREEN to REFACTOR followed
- [x] Task 558: Confirm uv is used for all dependency operations
- [x] Task 559: Confirm assignment-2 branch holds the changes
- [x] Task 560: Confirm version stamp consistent in pyproject.toml (currently 1.1.0)
