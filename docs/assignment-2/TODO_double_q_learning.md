# TODO — Double Q-Learning (Assignment 2)

## Conventions

Per `software_submission_guidelines-V3.pdf` §2.2.c.

**Status legend.** `[x] = done · [ ] = open`. Every task here is `[x]`.
**Priorities.** Tasks are in implementation order; earlier tasks gate
later ones. **Responsibility.** Single-author (Adir Elmakais).

| Phase gate | Definition-of-Done |
|------------|--------------------|
| `DoubleQAgent` | two tables QA / QB; coin-flip update uses argmax from one table and value from the other; `q_table` property returns `QA + QB` |
| Factory registration | `create_agent(config)` with `algorithm.name = "double_q"` returns a `DoubleQAgent` |
| Comparison runner | `SDK.run_comparison()` trains all three algorithms on the same board snapshot |
| Chart generation | `results/comparison/scenario2_hard.png` shows Double-Q's σ on the last 200 episodes is the smallest of the three |
| GUI integration | algorithm selector buttons + keyboard shortcuts switch agents without resetting the board |
| Tests | `tests/test_double_q_agent.py` asserts the cross-table evaluation and coin-flip mechanics |

---

## DoubleQAgent file setup
- [x] Task 1: Create src/dronerl/double_q_agent.py file
- [x] Task 2: Add module-level docstring describing DoubleQAgent
- [x] Task 3: Import numpy as np
- [x] Task 4: Import random module for 50/50 selection
- [x] Task 5: Import BaseAgent from dronerl.base_agent
- [x] Task 6: Import load_config helper from dronerl.config
- [x] Task 7: Add type hints import from typing
- [x] Task 8: Add Tuple and Optional type imports
- [x] Task 9: Keep file under 150 line limit
- [x] Task 10: Add module-level constants placeholder
- [x] Task 11: Ensure no hardcoded values in file
- [x] Task 12: Place file next to base_agent.py in src
- [x] Task 13: Confirm file is discoverable by factory
- [x] Task 14: Run ruff on empty file
- [x] Task 15: Commit initial empty file skeleton

## DoubleQAgent class definition
- [x] Task 16: Declare class DoubleQAgent(BaseAgent)
- [x] Task 17: Add class docstring describing dual Q-tables
- [x] Task 18: Set algorithm_name = "Double Q-Learning"
- [x] Task 19: Document cross-table evaluation strategy
- [x] Task 20: Document decaying alpha requirement
- [x] Task 21: Document 50/50 table selection
- [x] Task 22: Add class attribute for algorithm key
- [x] Task 23: Confirm inheritance chain is valid
- [x] Task 24: Ensure class compiles without errors
- [x] Task 25: Ensure ruff passes on class skeleton
- [x] Task 26: Add class to module __all__ list
- [x] Task 27: Verify class name matches factory registration
- [x] Task 28: Confirm class exposes algorithm_name publicly
- [x] Task 29: Add reference to PRD_double_q_learning.md
- [x] Task 30: Add reference to PLAN_double_q_learning.md

## DoubleQAgent __init__ with two tables
- [x] Task 31: Define __init__ accepting state_size and action_size
- [x] Task 32: Accept optional config argument
- [x] Task 33: Call super().__init__() first
- [x] Task 34: Load double_q section from config
- [x] Task 35: Read alpha_start from config.double_q
- [x] Task 36: Read alpha_end from config.double_q
- [x] Task 37: Read alpha_decay from config.double_q
- [x] Task 38: Initialize self.alpha from alpha_start
- [x] Task 39: Store self.alpha_end
- [x] Task 40: Store self.alpha_decay
- [x] Task 41: Allocate q_table_a as NumPy zeros array
- [x] Task 42: Allocate q_table_b as NumPy zeros array
- [x] Task 43: Use same shape for QA and QB
- [x] Task 44: Shape must be (rows, cols, num_actions)
- [x] Task 45: Use float64 dtype for QA and QB
- [x] Task 46: Record state_size as instance attribute
- [x] Task 47: Record action_size as instance attribute
- [x] Task 48: Seed random module if config seed provided
- [x] Task 49: Store original alpha_start for resets
- [x] Task 50: Ensure no base class init overwrites QA/QB
- [x] Task 51: Raise ValueError for negative alpha values
- [x] Task 52: Raise ValueError for alpha_decay > 1
- [x] Task 53: Raise ValueError for alpha_end > alpha_start
- [x] Task 54: Log initialization parameters at debug level
- [x] Task 55: Confirm __init__ completes under 30 lines
- [x] Task 56: Confirm no hardcoded shapes
- [x] Task 57: Confirm q_table_a distinct from q_table_b
- [x] Task 58: Assert tables have identical shape post-init
- [x] Task 59: Expose shape via helper method
- [x] Task 60: Ensure __init__ is idempotent for reset

## Combined q_table property (QA+QB)
- [x] Task 61: Define q_table as a @property
- [x] Task 62: Return q_table_a + q_table_b
- [x] Task 63: Document sum semantics in docstring
- [x] Task 64: Ensure property returns new array not view
- [x] Task 65: Confirm dtype matches underlying tables
- [x] Task 66: Confirm shape matches underlying tables
- [x] Task 67: Benchmark property access time
- [x] Task 68: Confirm GUI uses combined table
- [x] Task 69: Confirm heatmap uses combined table
- [x] Task 70: Add test for combined sum correctness
- [x] Task 71: Add test for property immutability
- [x] Task 72: Verify property handles zero tables
- [x] Task 73: Verify property handles negative values
- [x] Task 74: Verify property after many updates
- [x] Task 75: Use property in get_best_action inheritance
- [x] Task 76: Use property in get_max_q inheritance
- [x] Task 77: Confirm no recursion via setter
- [x] Task 78: Document why sum rather than mean
- [x] Task 79: Reference original Hasselt paper in docstring
- [x] Task 80: Ensure property works during save/load

## q_table setter no-op
- [x] Task 81: Define q_table.setter as no-op
- [x] Task 82: Document reason for no-op override
- [x] Task 83: Ensure BaseAgent init does not crash
- [x] Task 84: Prevent accidental overwrite of QA/QB
- [x] Task 85: Add pass statement in setter body
- [x] Task 86: Add test that setter does not modify tables
- [x] Task 87: Add test that setter accepts any input
- [x] Task 88: Confirm setter returns None
- [x] Task 89: Confirm setter preserves QA integrity
- [x] Task 90: Confirm setter preserves QB integrity
- [x] Task 91: Add ruff noqa if needed for unused arg
- [x] Task 92: Log warning if setter called externally
- [x] Task 93: Document hack in code comments
- [x] Task 94: Ensure setter signature accepts value
- [x] Task 95: Ensure setter cannot be removed without breaking init

## update() 50/50 table selection
- [x] Task 96: Override update(state, action, reward, next_state, done)
- [x] Task 97: Call random.random() to pick table
- [x] Task 98: Branch on value < 0.5 for QA update
- [x] Task 99: Branch on value >= 0.5 for QB update
- [x] Task 100: Ensure branches are mutually exclusive
- [x] Task 101: Ensure probability is exactly 50/50
- [x] Task 102: Support reproducible RNG via config seed
- [x] Task 103: Verify selection distribution via test
- [x] Task 104: Confirm update does not shuffle tables
- [x] Task 105: Confirm update picks only one table per call
- [x] Task 106: Log selected table at debug level
- [x] Task 107: Track selection counts for diagnostics
- [x] Task 108: Ensure no table bias over long runs
- [x] Task 109: Confirm update returns None
- [x] Task 110: Keep update body under 30 lines

## Cross-table evaluation (argmax one, value other)
- [x] Task 111: For QA update compute argmax over QA[next_state]
- [x] Task 112: Use QB[next_state, best_a] as bootstrap value
- [x] Task 113: For QB update compute argmax over QB[next_state]
- [x] Task 114: Use QA[next_state, best_a] as bootstrap value
- [x] Task 115: Compute TD target = reward + gamma * bootstrap
- [x] Task 116: Zero bootstrap if done flag is True
- [x] Task 117: Compute TD error = target - current_q
- [x] Task 118: Apply alpha * td_error to selected table
- [x] Task 119: Update only the selected table cell
- [x] Task 120: Leave the other table unchanged in this step
- [x] Task 121: Confirm argmax ties broken deterministically
- [x] Task 122: Confirm cross-table reduces overestimation
- [x] Task 123: Write test for argmax-from-QA bootstrap-from-QB
- [x] Task 124: Write test for argmax-from-QB bootstrap-from-QA
- [x] Task 125: Write test for symmetric learning over N steps
- [x] Task 126: Write test showing QA != QB after updates
- [x] Task 127: Validate against hand-computed example
- [x] Task 128: Document formula in docstring
- [x] Task 129: Reference Double Q-Learning paper equation
- [x] Task 130: Verify gamma read from config.agent

## Terminal state handling
- [x] Task 131: Detect done flag in update signature
- [x] Task 132: Skip bootstrap when done is True
- [x] Task 133: Set target = reward on terminal transition
- [x] Task 134: Write test for terminal QA update
- [x] Task 135: Write test for terminal QB update
- [x] Task 136: Confirm no out-of-bounds on terminal next_state
- [x] Task 137: Allow next_state=None on terminal
- [x] Task 138: Document terminal semantics in docstring
- [x] Task 139: Ensure reward-only update does not use bootstrap
- [x] Task 140: Ensure both tables can still learn terminal values
- [x] Task 141: Add regression test for delivery-cell update
- [x] Task 142: Add regression test for crash-cell update
- [x] Task 143: Confirm alpha still applied on terminal
- [x] Task 144: Confirm td_error sign correct on terminal
- [x] Task 145: Document edge case in code comments

## DoubleQAgent decay_alpha
- [x] Task 146: Override decay_alpha method
- [x] Task 147: Compute new_alpha = alpha * alpha_decay
- [x] Task 148: Clip to alpha_end floor
- [x] Task 149: Assign self.alpha to new value
- [x] Task 150: Return new alpha value
- [x] Task 151: Call decay_alpha at end of each episode
- [x] Task 152: Write test for single decay step
- [x] Task 153: Write test for decay floor enforcement
- [x] Task 154: Write test that decay never produces negative alpha
- [x] Task 155: Write test that decay is monotonic non-increasing
- [x] Task 156: Log alpha value every N episodes
- [x] Task 157: Confirm no hardcoded constants in decay_alpha
- [x] Task 158: Document decay formula in method docstring
- [x] Task 159: Confirm decay_alpha is called by SDK train loop
- [x] Task 160: Confirm decay_alpha is called by CLI run loop

## DoubleQAgent override decay_epsilon
- [x] Task 161: Override decay_epsilon method
- [x] Task 162: Compute new_eps = epsilon * epsilon_decay
- [x] Task 163: Clip to epsilon_end floor
- [x] Task 164: Assign self.epsilon to new value
- [x] Task 165: Return new epsilon value
- [x] Task 166: Reuse base formula but allow override
- [x] Task 167: Write test for epsilon decay step
- [x] Task 168: Write test for epsilon floor
- [x] Task 169: Confirm epsilon decays each episode
- [x] Task 170: Confirm epsilon used in choose_action
- [x] Task 171: Log epsilon value at debug
- [x] Task 172: Ensure epsilon_start from config.agent
- [x] Task 173: Ensure epsilon_end from config.agent
- [x] Task 174: Ensure epsilon_decay from config.agent
- [x] Task 175: Confirm no hardcoded epsilon values

## DoubleQAgent save (dual files)
- [x] Task 176: Override save(path) method
- [x] Task 177: Derive path_a by inserting _a before .npy
- [x] Task 178: Derive path_b by inserting _b before .npy
- [x] Task 179: Call np.save(path_a, q_table_a)
- [x] Task 180: Call np.save(path_b, q_table_b)
- [x] Task 181: Create parent directory if missing
- [x] Task 182: Log save paths at info level
- [x] Task 183: Write test that save creates both files
- [x] Task 184: Write test that file shapes match QA/QB
- [x] Task 185: Write test using tmp_path fixture
- [x] Task 186: Handle write errors with clear exception
- [x] Task 187: Return list of written paths
- [x] Task 188: Document dual-file format in docstring
- [x] Task 189: Ensure save works with custom extension
- [x] Task 190: Ensure save preserves dtype

## DoubleQAgent load (dual files)
- [x] Task 191: Override load(path) method
- [x] Task 192: Derive path_a and path_b from base path
- [x] Task 193: Call np.load(path_a) into q_table_a
- [x] Task 194: Call np.load(path_b) into q_table_b
- [x] Task 195: Validate loaded shapes match expected
- [x] Task 196: Raise FileNotFoundError if either file missing
- [x] Task 197: Log load paths at info level
- [x] Task 198: Write test round-trip save then load
- [x] Task 199: Write test for missing file error
- [x] Task 200: Write test for shape mismatch error
- [x] Task 201: Ensure dtype preserved on load
- [x] Task 202: Ensure combined q_table still valid after load
- [x] Task 203: Document dual-file load semantics
- [x] Task 204: Preserve alpha/epsilon on load
- [x] Task 205: Confirm load does not reset decay state

## Factory registration of double_q
- [x] Task 206: Open src/dronerl/algorithms.py
- [x] Task 207: Import DoubleQAgent
- [x] Task 208: Append AlgorithmSpec("double_q", "Double Q-Learning", color, DoubleQAgent) to ALGORITHM_REGISTRY
- [x] Task 209: Confirm AGENT_CLASSES["double_q"] resolves to DoubleQAgent
- [x] Task 210: Ensure create_agent dispatches double_q via the registry
- [x] Task 211: Raise ValueError with the valid-algorithm list when name is unknown
- [x] Task 212: Write test that factory returns DoubleQAgent
- [x] Task 213: Write test that double_q key is case-sensitive
- [x] Task 214: Confirm factory supports bellman, q_learning, double_q
- [x] Task 215: Document factory extension pattern
- [x] Task 216: Confirm factory used by SDK
- [x] Task 217: Confirm factory used by CLI
- [x] Task 218: Confirm factory used by tests
- [x] Task 219: Expose registry keys via helper function
- [x] Task 220: Ensure ruff passes on factory module

## Config double_q section
- [x] Task 221: Open config/config.yaml
- [x] Task 222: Add double_q top-level section
- [x] Task 223: Add alpha_start: 0.5 under double_q
- [x] Task 224: Add alpha_end: 0.05 under double_q
- [x] Task 225: Add alpha_decay: 0.9995 under double_q
- [x] Task 226: Document each key with a YAML comment
- [x] Task 227: Add algorithm key at top level accepting double_q
- [x] Task 228: Ensure config loader reads double_q section
- [x] Task 229: Ensure config schema validates double_q types
- [x] Task 230: Add default fallback if section missing
- [x] Task 231: Write test for loading double_q values
- [x] Task 232: Write test for algorithm key selection
- [x] Task 233: Confirm values appear in BaseAgent init
- [x] Task 234: Confirm values appear in comparison runs
- [x] Task 235: Document tuning guidance in PRD

## ComparisonStore class
- [x] Task 236: Create or open src/dronerl/comparison.py
- [x] Task 237: Define class ComparisonStore
- [x] Task 238: Add docstring describing role
- [x] Task 239: Define __init__ storing runs dict
- [x] Task 240: Ensure runs keys are algorithm names
- [x] Task 241: Ensure runs values are reward histories
- [x] Task 242: Add type hints on all attributes
- [x] Task 243: Add type hints on all methods
- [x] Task 244: Ensure class fits within 150-line file limit
- [x] Task 245: Ensure single responsibility for storage
- [x] Task 246: Add __repr__ for debugging
- [x] Task 247: Add __len__ returning number of runs
- [x] Task 248: Keep class attribute-free where possible
- [x] Task 249: Ensure ruff passes
- [x] Task 250: Register class in module __all__

## ComparisonStore add_run / clear / algorithms
- [x] Task 251: Implement add_run(name, history)
- [x] Task 252: Validate name is a string
- [x] Task 253: Validate history is a sequence of numbers
- [x] Task 254: Store history under runs[name]
- [x] Task 255: Overwrite existing entry if same name
- [x] Task 256: Implement clear() method
- [x] Task 257: clear() resets runs dict to empty
- [x] Task 258: Implement algorithms() method
- [x] Task 259: algorithms() returns sorted key list
- [x] Task 260: Write test for add_run single entry
- [x] Task 261: Write test for add_run overwrite
- [x] Task 262: Write test for clear empties runs
- [x] Task 263: Write test for algorithms() ordering
- [x] Task 264: Write test for algorithms() empty state
- [x] Task 265: Document methods in docstrings

## ComparisonStore has_results / has_all / get_histories
- [x] Task 266: Implement has_results(name) returning bool
- [x] Task 267: Implement has_all(names) returning bool
- [x] Task 268: has_all accepts iterable of names
- [x] Task 269: has_all returns True only if every name present
- [x] Task 270: Implement get_histories(names) returning dict
- [x] Task 271: get_histories returns shallow copy
- [x] Task 272: Raise KeyError for missing names in get_histories
- [x] Task 273: Write test for has_results true path
- [x] Task 274: Write test for has_results false path
- [x] Task 275: Write test for has_all partial match
- [x] Task 276: Write test for has_all full match
- [x] Task 277: Write test for get_histories returns copy
- [x] Task 278: Write test for get_histories key ordering
- [x] Task 279: Ensure methods do not mutate state
- [x] Task 280: Document query API in docstrings

## smooth() moving average
- [x] Task 281: Define smooth(values, window) function
- [x] Task 282: Accept list or np.ndarray as values
- [x] Task 283: Validate window is positive integer
- [x] Task 284: Clamp window to len(values) if larger
- [x] Task 285: Use np.convolve with ones/window kernel
- [x] Task 286: Pass mode="same" to np.convolve
- [x] Task 287: Return np.ndarray of same length as input
- [x] Task 288: Handle empty input gracefully
- [x] Task 289: Handle window=1 as identity
- [x] Task 290: Write test for simple constant sequence
- [x] Task 291: Write test for linear sequence smoothing
- [x] Task 292: Write test for edge window larger than data
- [x] Task 293: Write test for output length equality
- [x] Task 294: Document function behavior in docstring
- [x] Task 295: Ensure no hardcoded window default

## generate_comparison_chart (matplotlib)
- [x] Task 296: Import matplotlib and set Agg backend before pyplot
- [x] Task 297: Define generate_comparison_chart function
- [x] Task 298: Accept store, output_path, smoothing_window args
- [x] Task 299: Accept title and ylabel arguments
- [x] Task 300: Create figure with configured size
- [x] Task 301: Create axes via subplots
- [x] Task 302: Iterate over store.algorithms()
- [x] Task 303: Apply smooth() to each history
- [x] Task 304: Plot each smoothed history as a line
- [x] Task 305: Use ALGORITHM_LABELS for line labels
- [x] Task 306: Use ALGORITHM_COLORS for line colors
- [x] Task 307: Add legend at best location
- [x] Task 308: Add x-axis label Episode
- [x] Task 309: Add y-axis label Reward
- [x] Task 310: Add chart title from argument
- [x] Task 311: Enable grid with subtle alpha
- [x] Task 312: Tight layout before save
- [x] Task 313: Save PNG to output_path
- [x] Task 314: Close figure after save to free memory
- [x] Task 315: Return output_path from function
- [x] Task 316: Create parent directory if missing
- [x] Task 317: Write test that PNG file is created
- [x] Task 318: Write test with mocked plt.savefig
- [x] Task 319: Write test for missing algorithms raises
- [x] Task 320: Ensure Agg backend chosen before pyplot import

## ALGORITHM_LABELS and COLORS constants
- [x] Task 321: Define ALGORITHM_LABELS at module top
- [x] Task 322: Map bellman to human-readable label
- [x] Task 323: Map q_learning to human-readable label
- [x] Task 324: Map double_q to human-readable label
- [x] Task 325: Define ALGORITHM_COLORS at module top
- [x] Task 326: Pick distinct color for bellman
- [x] Task 327: Pick distinct color for q_learning
- [x] Task 328: Pick distinct color for double_q
- [x] Task 329: Source colors from config.colors where possible
- [x] Task 330: Fallback to sensible defaults
- [x] Task 331: Add test that keys align across maps
- [x] Task 332: Add test that labels are non-empty strings
- [x] Task 333: Add test that colors are valid hex or names
- [x] Task 334: Document constants in module docstring
- [x] Task 335: Ensure constants are immutable by convention

## SDK switch_algorithm
- [x] Task 336: Open src/dronerl/sdk.py
- [x] Task 337: Add switch_algorithm(name) method to SDK class
- [x] Task 338: Validate name is a known algorithm key
- [x] Task 339: Update config.algorithm to name
- [x] Task 340: Reset agent using factory with new name
- [x] Task 341: Reset reward history tracker
- [x] Task 342: Reset episode counter
- [x] Task 343: Keep environment and grid intact
- [x] Task 344: Emit change event to GUI observer
- [x] Task 345: Log algorithm switch at info level
- [x] Task 346: Return new agent reference
- [x] Task 347: Write test switching bellman to q_learning
- [x] Task 348: Write test switching q_learning to double_q
- [x] Task 349: Write test switching to invalid name raises
- [x] Task 350: Document method in SDK docstring

## SDK run_comparison (same board)
- [x] Task 351: Add run_comparison(episodes) method to SDK
- [x] Task 352: Snapshot current grid layout
- [x] Task 353: Snapshot goal and start positions
- [x] Task 354: Snapshot wind and dynamic_board state
- [x] Task 355: Save original algorithm name
- [x] Task 356: Loop over ["bellman", "q_learning", "double_q"]
- [x] Task 357: Switch algorithm via switch_algorithm
- [x] Task 358: Restore grid snapshot before each run
- [x] Task 359: Train agent for given episode count
- [x] Task 360: Capture reward history per algorithm
- [x] Task 361: Add history to ComparisonStore
- [x] Task 362: Restore original algorithm after loop
- [x] Task 363: Restore original grid state after loop
- [x] Task 364: Return ComparisonStore instance
- [x] Task 365: Log per-algorithm runtime
- [x] Task 366: Write test that all three algos run
- [x] Task 367: Write test that grid is restored after
- [x] Task 368: Write test that histories length equals episodes
- [x] Task 369: Ensure deterministic seed propagation
- [x] Task 370: Document method in SDK docstring

## SDK generate_chart
- [x] Task 371: Add generate_chart(store, path) method to SDK
- [x] Task 372: Delegate to comparison.generate_comparison_chart
- [x] Task 373: Use config.comparison.smoothing_window
- [x] Task 374: Use config.comparison.output_dir as default
- [x] Task 375: Resolve absolute output path
- [x] Task 376: Create output directory if missing
- [x] Task 377: Log generated chart path at info
- [x] Task 378: Return path from method
- [x] Task 379: Write test that chart file exists
- [x] Task 380: Write test that method uses configured window
- [x] Task 381: Handle empty store with clear error
- [x] Task 382: Handle missing algorithm with clear error
- [x] Task 383: Document method in SDK docstring
- [x] Task 384: Ensure no hardcoded paths
- [x] Task 385: Ensure no hardcoded window size

## Config comparison section
- [x] Task 386: Add comparison section to config.yaml
- [x] Task 387: Add max_episodes: 5000
- [x] Task 388: Add smoothing_window: 50
- [x] Task 389: Add output_dir: results/comparison
- [x] Task 390: Document each key with comment
- [x] Task 391: Ensure config loader exposes section
- [x] Task 392: Add default fallback if section missing
- [x] Task 393: Write test for loading comparison keys
- [x] Task 394: Confirm values consumed by SDK
- [x] Task 395: Confirm values consumed by script
- [x] Task 396: Validate max_episodes is positive int
- [x] Task 397: Validate smoothing_window is positive int
- [x] Task 398: Validate output_dir is string path
- [x] Task 399: Ensure path works cross-platform
- [x] Task 400: Document tuning guidance for smoothing_window

## GUI keyboard 1/2/3 algorithm switching
- [x] Task 401: Open src/dronerl/gui.py
- [x] Task 402: Handle pygame KEYDOWN event
- [x] Task 403: Map key 1 to switch_algorithm bellman
- [x] Task 404: Map key 2 to switch_algorithm q_learning
- [x] Task 405: Map key 3 to switch_algorithm double_q
- [x] Task 406: Use action dispatcher not direct SDK calls
- [x] Task 407: Ignore keys when input focused elsewhere
- [x] Task 408: Debounce rapid key presses
- [x] Task 409: Log chosen algorithm to console
- [x] Task 410: Update status bar on switch
- [x] Task 411: Redraw heatmap using combined q_table
- [x] Task 412: Redraw agent state on switch
- [x] Task 413: Write test for key 1 dispatch
- [x] Task 414: Write test for key 2 dispatch
- [x] Task 415: Write test for key 3 dispatch

## GUI keyboard C run comparison
- [x] Task 416: Map key C to run_comparison action
- [x] Task 417: Show busy indicator during run
- [x] Task 418: Disable inputs while running
- [x] Task 419: Spawn comparison in background thread
- [x] Task 420: Poll completion from main loop
- [x] Task 421: Hide busy indicator on completion
- [x] Task 422: Open generated chart via OS default viewer
- [x] Task 423: Log run duration to console
- [x] Task 424: Show toast on success
- [x] Task 425: Show toast on failure
- [x] Task 426: Write test for key C dispatch
- [x] Task 427: Write test for busy indicator toggle
- [x] Task 428: Write test that run uses configured episodes
- [x] Task 429: Ensure key C not triggered during input focus
- [x] Task 430: Document keyboard shortcuts in README

## Actions use_bellman/q_learning/double_q
- [x] Task 431: Open src/dronerl/actions.py
- [x] Task 432: Define use_bellman action function
- [x] Task 433: Define use_q_learning action function
- [x] Task 434: Define use_double_q action function
- [x] Task 435: Each action calls sdk.switch_algorithm
- [x] Task 436: Each action updates status bar
- [x] Task 437: Each action logs selection
- [x] Task 438: Register actions in dispatcher map
- [x] Task 439: Write test for use_bellman
- [x] Task 440: Write test for use_q_learning
- [x] Task 441: Write test for use_double_q
- [x] Task 442: Ensure actions are idempotent
- [x] Task 443: Ensure actions handle missing SDK gracefully
- [x] Task 444: Document action contracts in module docstring
- [x] Task 445: Confirm ruff passes on actions module

## Actions run_comparison subprocess
- [x] Task 446: Define run_comparison action
- [x] Task 447: Build subprocess command for comparison script
- [x] Task 448: Pass episodes argument from config
- [x] Task 449: Pass output_dir argument from config
- [x] Task 450: Launch via subprocess.Popen
- [x] Task 451: Capture stdout and stderr streams
- [x] Task 452: Stream child logs to main logger
- [x] Task 453: Return process handle to caller
- [x] Task 454: Handle non-zero exit codes
- [x] Task 455: Kill process on GUI close
- [x] Task 456: Write test with mocked subprocess
- [x] Task 457: Write test for exit code propagation
- [x] Task 458: Write test for argument construction
- [x] Task 459: Ensure subprocess uses uv run
- [x] Task 460: Document subprocess lifecycle

## Status bar algorithm display
- [x] Task 461: Identify status bar component in GUI
- [x] Task 462: Add Algorithm: <name> segment
- [x] Task 463: Read name from sdk.agent.algorithm_name
- [x] Task 464: Use ALGORITHM_LABELS for display text
- [x] Task 465: Update segment on algorithm switch
- [x] Task 466: Use configured color for segment text
- [x] Task 467: Use configured font from config.gui
- [x] Task 468: Handle long names with ellipsis
- [x] Task 469: Write test for initial algorithm display
- [x] Task 470: Write test for update on switch
- [x] Task 471: Ensure status bar within 150-line file limit
- [x] Task 472: Ensure no hardcoded labels
- [x] Task 473: Ensure no hardcoded fonts
- [x] Task 474: Document status bar segments in code
- [x] Task 475: Render segment each frame

## Dashboard alpha display
- [x] Task 476: Open src/dronerl/dashboard.py
- [x] Task 477: Detect if agent has alpha attribute
- [x] Task 478: Add Alpha: value line to dashboard
- [x] Task 479: Format alpha with configured decimals
- [x] Task 480: Hide Alpha line when attribute missing
- [x] Task 481: Update Alpha value each frame
- [x] Task 482: Use configured font for dashboard
- [x] Task 483: Use configured color for dashboard text
- [x] Task 484: Write test that bellman hides alpha
- [x] Task 485: Write test that q_learning shows alpha
- [x] Task 486: Write test that double_q shows alpha
- [x] Task 487: Write test for alpha format precision
- [x] Task 488: Ensure dashboard file under 150 lines
- [x] Task 489: Document alpha semantics in module
- [x] Task 490: Ensure no hardcoded decimal count

## scripts/generate_comparison_charts.py
- [x] Task 491: Create scripts/generate_comparison_charts.py
- [x] Task 492: Add shebang and uv-compatible header
- [x] Task 493: Import SDK and comparison module
- [x] Task 494: Import config loader
- [x] Task 495: Parse CLI args for scenario name
- [x] Task 496: Parse CLI args for output_dir override
- [x] Task 497: Load config via loader
- [x] Task 498: Instantiate SDK with config
- [x] Task 499: Run scenario 1 medium noise
- [x] Task 500: Run scenario 2 hard noise
- [x] Task 501: Save scenario1_medium.png
- [x] Task 502: Save scenario2_hard.png
- [x] Task 503: Print generated paths to stdout
- [x] Task 504: Exit with 0 on success
- [x] Task 505: Exit with 1 on failure
- [x] Task 506: Handle Ctrl+C cleanly
- [x] Task 507: Ensure script under 150 lines
- [x] Task 508: Ensure no hardcoded paths
- [x] Task 509: Document script usage in module docstring
- [x] Task 510: Add smoke test for script via subprocess

## Two scenarios (medium, hard)
- [x] Task 511: Define scenario1 medium config profile
- [x] Task 512: Set medium noise level from config
- [x] Task 513: Set medium obstacle density from config
- [x] Task 514: Use configured max_episodes for scenario1
- [x] Task 515: Define scenario2 hard config profile
- [x] Task 516: Set high noise level from config
- [x] Task 517: Set high obstacle density from config
- [x] Task 518: Use configured max_episodes for scenario2
- [x] Task 519: Run all three algorithms per scenario
- [x] Task 520: Store histories in ComparisonStore per scenario
- [x] Task 521: Generate chart per scenario
- [x] Task 522: Write chart under results/comparison
- [x] Task 523: Commit generated PNGs to repo
- [x] Task 524: Verify medium shows Bellman converging slower
- [x] Task 525: Verify hard shows Bellman failing
- [x] Task 526: Verify hard shows Q-Learning failing
- [x] Task 527: Verify hard shows Double Q converging
- [x] Task 528: Document scenarios in README
- [x] Task 529: Document scenarios in PRD
- [x] Task 530: Document scenarios in PLAN

## README comparison section
- [x] Task 531: Open README.md
- [x] Task 532: Add Algorithm Comparison section
- [x] Task 533: Embed scenario1_medium.png image
- [x] Task 534: Embed scenario2_hard.png image
- [x] Task 535: Add caption under each image
- [x] Task 536: Describe methodology briefly
- [x] Task 537: Describe hyperparameters used
- [x] Task 538: Describe seed handling
- [x] Task 539: Describe smoothing window
- [x] Task 540: Link to comparison script
- [x] Task 541: Link to PRD and PLAN docs
- [x] Task 542: Link to config section
- [x] Task 543: Verify images render on GitHub
- [x] Task 544: Verify relative paths correct
- [x] Task 545: Keep section concise and scannable

## README conclusions
- [x] Task 546: Add Conclusions subsection
- [x] Task 547: State Bellman fails under high noise
- [x] Task 548: State Q-Learning converges with alpha decay
- [x] Task 549: State Double Q-Learning fastest and most stable
- [x] Task 550: Reference cross-table reduction of overestimation
- [x] Task 551: Add Parameter Analysis subsection
- [x] Task 552: Discuss alpha_start effects
- [x] Task 553: Discuss alpha_end effects
- [x] Task 554: Discuss alpha_decay effects
- [x] Task 555: Discuss epsilon decay effects
- [x] Task 556: Discuss gamma effects
- [x] Task 557: Discuss noise level effects
- [x] Task 558: Discuss density effects
- [x] Task 559: Discuss smoothing_window effects
- [x] Task 560: Discuss max_episodes effects
- [x] Task 561: Reference charts to support claims
- [x] Task 562: Keep conclusions within one screen
- [x] Task 563: Verify conclusions match chart trends
- [x] Task 564: Proofread grammar and clarity
- [x] Task 565: Commit README updates

## Tests for DoubleQAgent
- [x] Task 566: Create tests/test_double_q_agent.py
- [x] Task 567: Add test for class instantiation
- [x] Task 568: Add test for q_table_a shape
- [x] Task 569: Add test for q_table_b shape
- [x] Task 570: Add test that QA != QB after updates
- [x] Task 571: Add test for combined q_table property
- [x] Task 572: Add test for q_table setter no-op
- [x] Task 573: Add test for update 50/50 distribution
- [x] Task 574: Add test for cross-table QA update
- [x] Task 575: Add test for cross-table QB update
- [x] Task 576: Add test for terminal update QA
- [x] Task 577: Add test for terminal update QB
- [x] Task 578: Add test for decay_alpha
- [x] Task 579: Add test for alpha floor
- [x] Task 580: Add test for decay_epsilon override
- [x] Task 581: Add test for save creates two files
- [x] Task 582: Add test for load reads two files
- [x] Task 583: Add test for save/load round-trip
- [x] Task 584: Add test for factory returns DoubleQAgent
- [x] Task 585: Add test for algorithm_name string
- [x] Task 586: Add test for get_best_action using combined
- [x] Task 587: Add test for get_max_q using combined
- [x] Task 588: Add test for ValueError on bad config
- [x] Task 589: Ensure coverage for decay_alpha branches
- [x] Task 590: Ensure coverage for update branches
- [x] Task 591: Ensure 85%+ coverage in module
- [x] Task 592: Run ruff on test file
- [x] Task 593: Run pytest on test file
- [x] Task 594: Commit test file

## Tests for ComparisonStore
- [x] Task 595: Create tests/test_comparison.py
- [x] Task 596: Add test for empty store algorithms()
- [x] Task 597: Add test for add_run single
- [x] Task 598: Add test for add_run overwrite
- [x] Task 599: Add test for clear
- [x] Task 600: Add test for has_results true
- [x] Task 601: Add test for has_results false
- [x] Task 602: Add test for has_all partial
- [x] Task 603: Add test for has_all full
- [x] Task 604: Add test for get_histories returns copy
- [x] Task 605: Add test for get_histories missing name
- [x] Task 606: Add test for __len__
- [x] Task 607: Add test for __repr__
- [x] Task 608: Add test for smooth constant
- [x] Task 609: Add test for smooth linear
- [x] Task 610: Add test for smooth window clamp
- [x] Task 611: Add test for smooth empty input
- [x] Task 612: Add test for smooth window=1 identity
- [x] Task 613: Add test for ALGORITHM_LABELS keys
- [x] Task 614: Add test for ALGORITHM_COLORS keys
- [x] Task 615: Ensure 85%+ coverage in comparison.py
- [x] Task 616: Run ruff on test file
- [x] Task 617: Run pytest on test file
- [x] Task 618: Commit test file

## Tests for chart generation
- [x] Task 619: Add test generate_comparison_chart writes PNG
- [x] Task 620: Add test chart uses smoothing_window from config
- [x] Task 621: Add test chart uses ALGORITHM_LABELS
- [x] Task 622: Add test chart uses ALGORITHM_COLORS
- [x] Task 623: Add test chart has legend entry per algorithm
- [x] Task 624: Add test chart axes labeled Episode and Reward
- [x] Task 625: Add test chart title matches argument
- [x] Task 626: Add test empty store raises clear error
- [x] Task 627: Add test chart directory auto-created
- [x] Task 628: Add test Agg backend is set
- [x] Task 629: Use tmp_path fixture for outputs
- [x] Task 630: Mock plt.savefig in fast tests
- [x] Task 631: Add snapshot check for file size > 0
- [x] Task 632: Ensure tests run on headless CI
- [x] Task 633: Run ruff on chart tests
- [x] Task 634: Run pytest on chart tests
- [x] Task 635: Commit chart tests

## Tests for SDK comparison
- [x] Task 636: Create tests/test_sdk_comparison.py
- [x] Task 637: Add test switch_algorithm to bellman
- [x] Task 638: Add test switch_algorithm to q_learning
- [x] Task 639: Add test switch_algorithm to double_q
- [x] Task 640: Add test switch_algorithm unknown name raises
- [x] Task 641: Add test run_comparison returns store
- [x] Task 642: Add test run_comparison has 3 algorithms
- [x] Task 643: Add test run_comparison histories have length episodes
- [x] Task 644: Add test run_comparison restores algorithm
- [x] Task 645: Add test run_comparison restores grid snapshot
- [x] Task 646: Add test run_comparison deterministic with seed
- [x] Task 647: Add test generate_chart writes PNG
- [x] Task 648: Add test generate_chart uses configured dir
- [x] Task 649: Add test generate_chart uses configured window
- [x] Task 650: Add test generate_chart returns path
- [x] Task 651: Add test empty store raises in generate_chart
- [x] Task 652: Use tmp_path for file outputs
- [x] Task 653: Mock training loop for speed
- [x] Task 654: Ensure coverage for switch_algorithm branches
- [x] Task 655: Ensure coverage for run_comparison branches
- [x] Task 656: Ensure coverage for generate_chart branches
- [x] Task 657: Ensure 85%+ coverage in sdk.py comparison code
- [x] Task 658: Run ruff on SDK tests
- [x] Task 659: Run pytest on SDK tests
- [x] Task 660: Run full pytest suite with coverage
- [x] Task 661: Confirm zero ruff violations across project
- [x] Task 662: Commit SDK tests
