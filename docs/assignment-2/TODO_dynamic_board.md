# DroneRL — Dynamic Board Task Breakdown

> All tasks marked as completed. Total: 570 granular tasks covering every aspect of the dynamic board feature.

---

## 1. CellType.PIT Enum Addition (~45 tasks)

### 1.1 PIT Enum Value Setup

- [x] Task 1: Open `src/environment.py` for editing
- [x] Task 2: Locate the `CellType` IntEnum class definition
- [x] Task 3: Identify the last enum value (WIND = 4)
- [x] Task 4: Add `PIT = 5` as a new member of the CellType IntEnum
- [x] Task 5: Verify PIT = 5 does not conflict with existing enum values
- [x] Task 6: Add inline comment `# terminal hazard — hole in the ground` next to PIT
- [x] Task 7: Update the CellType docstring to mention PIT
- [x] Task 8: Verify CellType members are in sequential order (0-5)
- [x] Task 9: Save `src/environment.py` after PIT enum addition
- [x] Task 10: Verify `CellType.PIT.value == 5` via quick test

### 1.2 Config — PIT Cell Type Entry

- [x] Task 11: Open `config/config.yaml` for editing
- [x] Task 12: Locate the `cell_types` section in config.yaml
- [x] Task 13: Add `pit: 5` under the `cell_types` section
- [x] Task 14: Add comment `# new hazard type for Assignment 2` above pit entry
- [x] Task 15: Verify pit value matches CellType.PIT = 5
- [x] Task 16: Save config.yaml after cell_types update

### 1.3 Config — PIT Reward

- [x] Task 17: Locate the `rewards` section in config.yaml
- [x] Task 18: Add `pit_penalty: -75` under the rewards section
- [x] Task 19: Add comment explaining pit_penalty is for PIT cell type
- [x] Task 20: Verify pit_penalty is between trap_penalty and goal_reward in magnitude
- [x] Task 21: Save config.yaml after rewards update

### 1.4 Config — PIT Colors

- [x] Task 22: Locate the `colors` section in config.yaml
- [x] Task 23: Add `pit: [120, 40, 160]` to the colors section
- [x] Task 24: Add `pit_accent: [160, 60, 200]` to the colors section
- [x] Task 25: Add comment `# dark purple tones for pit cells` above pit color entries
- [x] Task 26: Verify pit color RGB values are valid (0-255 range)
- [x] Task 27: Verify pit_accent color RGB values are valid (0-255 range)
- [x] Task 28: Save config.yaml after colors update

### 1.5 Config Loader — PIT Access Verification

- [x] Task 29: Verify `config.cell_types.pit` returns 5 after loading config
- [x] Task 30: Verify `config.rewards.pit_penalty` returns -75 after loading config
- [x] Task 31: Verify `config.colors.pit` returns [120, 40, 160] after loading config
- [x] Task 32: Verify `config.colors.pit_accent` returns [160, 60, 200] after loading config

### 1.6 Tests — PIT Enum

- [x] Task 33: Open `tests/test_environment.py` for editing
- [x] Task 34: Add test: `CellType.PIT` exists in the enum
- [x] Task 35: Add test: `CellType.PIT.value == 5`
- [x] Task 36: Add test: PIT is a valid member of CellType IntEnum
- [x] Task 37: Add test: PIT is distinct from EMPTY, BUILDING, TRAP, GOAL, WIND
- [x] Task 38: Add test: CellType has exactly 6 members (EMPTY through PIT)
- [x] Task 39: Add test: PIT can be created from integer `CellType(5)`
- [x] Task 40: Add test: PIT string representation includes "PIT"
- [x] Task 41: Run PIT enum tests and verify all pass
- [x] Task 42: Verify no existing tests are broken by PIT addition
- [x] Task 43: Run full test suite to confirm backward compatibility
- [x] Task 44: Verify ruff check passes on environment.py
- [x] Task 45: Verify ruff check passes on config.yaml changes

---

## 2. PIT Handling in environment.step() (~55 tasks)

### 2.1 Step Method — PIT Detection

- [x] Task 46: Open `src/environment.py` and locate the `step()` method
- [x] Task 47: Identify where TRAP handling occurs in step()
- [x] Task 48: Identify the pattern used for terminal cell detection
- [x] Task 49: Add PIT cell type check after TRAP check in step()
- [x] Task 50: Add condition: `if cell_type == CellType.PIT`
- [x] Task 51: Set reward to `self.pit_penalty` when drone lands on PIT
- [x] Task 52: Set `done = True` when drone lands on PIT
- [x] Task 53: Set `info["event"] = "pit"` when drone lands on PIT
- [x] Task 54: Return `(state, pit_penalty, True, info)` for PIT cell
- [x] Task 55: Verify PIT handling follows same pattern as TRAP handling
- [x] Task 56: Verify PIT penalty comes from config (not hardcoded)

### 2.2 Environment __init__ — PIT Penalty Loading

- [x] Task 57: Locate `__init__` method in Environment class
- [x] Task 58: Identify where trap_penalty is loaded from config
- [x] Task 59: Add `self.pit_penalty = config.rewards.pit_penalty` in __init__
- [x] Task 60: Verify pit_penalty is loaded alongside other reward values
- [x] Task 61: Verify pit_penalty is a negative float value
- [x] Task 62: Add pit_penalty to any reward-related logging if present

### 2.3 Environment __init__ — _editor_cells Tracking Set

- [x] Task 63: Add `self._editor_cells: set[tuple[int, int]] = set()` in __init__
- [x] Task 64: Initialize _editor_cells as empty set
- [x] Task 65: Add type hint for _editor_cells as `set[tuple[int, int]]`
- [x] Task 66: Verify _editor_cells is initialized before any cell placement
- [x] Task 67: Add comment explaining _editor_cells tracks manually-placed cells

### 2.4 Environment — set_cell() Editor Tracking

- [x] Task 68: Locate the `set_cell()` method in Environment
- [x] Task 69: Add `editor: bool = False` parameter to set_cell() signature
- [x] Task 70: Add condition: if editor is True, add coordinates to _editor_cells
- [x] Task 71: Implement: `if editor: self._editor_cells.add((row, col))`
- [x] Task 72: Verify existing set_cell calls are unaffected (editor defaults to False)
- [x] Task 73: Verify editor calls from editor.py pass `editor=True`

### 2.5 Environment — set_wind_drift() Method

- [x] Task 74: Define `set_wind_drift(self, probability: float) -> None` method
- [x] Task 75: Add docstring: "Override wind drift probability at runtime"
- [x] Task 76: Add type hint for probability parameter as float
- [x] Task 77: Implement: `self.wind_drift = probability`
- [x] Task 78: Add validation: clamp probability to [0.0, 1.0]
- [x] Task 79: Verify set_wind_drift updates the drift probability used in step()
- [x] Task 80: Add test for set_wind_drift with value 0.0
- [x] Task 81: Add test for set_wind_drift with value 1.0
- [x] Task 82: Add test for set_wind_drift with value 0.5

### 2.6 Environment — clear_dynamic_cells() Method

- [x] Task 83: Define `clear_dynamic_cells(self, editor_cells: set) -> None` method
- [x] Task 84: Add docstring: "Reset all non-editor cells to EMPTY"
- [x] Task 85: Add type hint for editor_cells parameter as `set[tuple[int, int]]`
- [x] Task 86: Iterate over all grid cells (row, col)
- [x] Task 87: Skip cells that are in the editor_cells set
- [x] Task 88: Skip the start position cell
- [x] Task 89: Skip the goal position cell
- [x] Task 90: Set remaining cells to CellType.EMPTY
- [x] Task 91: Verify clear_dynamic_cells preserves editor-placed cells
- [x] Task 92: Verify clear_dynamic_cells preserves start cell
- [x] Task 93: Verify clear_dynamic_cells preserves goal cell
- [x] Task 94: Verify clear_dynamic_cells resets TRAP cells to EMPTY
- [x] Task 95: Verify clear_dynamic_cells resets WIND cells to EMPTY
- [x] Task 96: Verify clear_dynamic_cells resets PIT cells to EMPTY

### 2.7 Tests — PIT Step Handling

- [x] Task 97: Add test: step onto PIT cell returns done=True
- [x] Task 98: Add test: step onto PIT cell returns pit_penalty reward
- [x] Task 99: Add test: step onto PIT cell returns info["event"] == "pit"
- [x] Task 100: Add test: PIT cell terminates the episode

---

## 3. PIT Rendering in renderer.py (~60 tasks)

### 3.1 Renderer __init__ — PIT Color Loading

- [x] Task 101: Open `src/renderer.py` for editing
- [x] Task 102: Locate the `__init__` method in Renderer class
- [x] Task 103: Identify where existing cell colors are loaded from config
- [x] Task 104: Add `self.c_pit = tuple(config.colors.pit)` in __init__
- [x] Task 105: Add `self.c_pit_acc = tuple(config.colors.pit_accent)` in __init__
- [x] Task 106: Verify c_pit is a tuple of 3 integers (RGB)
- [x] Task 107: Verify c_pit_acc is a tuple of 3 integers (RGB)
- [x] Task 108: Verify color loading follows existing pattern for other cell types

### 3.2 Renderer — _draw_pit() Method

- [x] Task 109: Define `_draw_pit(self, surf, x, y)` method
- [x] Task 110: Add docstring: "Render a PIT cell as a dark purple hole"
- [x] Task 111: Calculate cell rectangle from x, y coordinates and cell_size
- [x] Task 112: Fill the cell background with c_pit color
- [x] Task 113: Calculate center point of the cell for the hole circle
- [x] Task 114: Calculate hole radius as a fraction of cell_size (e.g., cell_size // 3)
- [x] Task 115: Draw outer circle with c_pit_acc color (accent ring)
- [x] Task 116: Draw inner circle with darker shade for depth effect
- [x] Task 117: Use pygame.draw.circle for the hole rendering
- [x] Task 118: Verify _draw_pit produces a visible distinct visual
- [x] Task 119: Verify _draw_pit uses only config-driven colors (no hardcoded values)

### 3.3 Renderer — Register PIT in Draw Dictionary

- [x] Task 120: Locate the draw dictionary/dispatch in `draw_grid()` method
- [x] Task 121: Identify the pattern for mapping CellType to draw methods
- [x] Task 122: Add `CellType.PIT: self._draw_pit` to the draw dictionary
- [x] Task 123: Verify PIT draw method is called when grid contains PIT cells
- [x] Task 124: Verify draw dictionary includes all 6 cell types
- [x] Task 125: Save renderer.py after PIT rendering addition

### 3.4 Renderer — Line Count Check

- [x] Task 126: Count total lines in renderer.py after PIT addition
- [x] Task 127: Verify renderer.py is at or under 150 lines
- [x] Task 128: If over 150 lines, identify extraction candidates
- [x] Task 129: If needed, plan extraction of _draw_* methods to cell_drawers.py
- [x] Task 130: Verify ruff check passes on renderer.py

### 3.5 Tests — PIT Rendering

- [ ] Task 131: Add test: PIT cell type triggers _draw_pit method
- [ ] Task 132: Add test: _draw_pit draws at correct x, y coordinates
- [ ] Task 133: Add test: _draw_pit uses c_pit color from config
- [ ] Task 134: Add test: _draw_pit uses c_pit_acc color from config
- [ ] Task 135: Add test: PIT cell is visually distinct from TRAP cell
- [ ] Task 136: Add test: PIT cell is visually distinct from BUILDING cell
- [ ] Task 137: Add test: PIT rendering does not crash with valid inputs
- [ ] Task 138: Add test: draw_grid handles grid with PIT cells without error
- [ ] Task 139: Add test: draw_grid renders all 6 cell types correctly
- [x] Task 140: Run renderer tests and verify all pass
- [x] Task 141: Verify no existing renderer tests are broken
- [x] Task 142: Verify ruff check passes on test file

### 3.6 Visual Verification

- [x] Task 143: Run application and manually place PIT cell in editor
- [x] Task 144: Verify PIT appears as a dark purple circle/hole
- [x] Task 145: Verify PIT is visually distinguishable from TRAP (red) and WIND (blue)
- [x] Task 146: Verify PIT color matches config values
- [x] Task 147: Verify PIT accent ring is visible
- [x] Task 148: Take screenshot of PIT cell rendering for documentation
- [x] Task 149: Verify PIT renders correctly at different cell sizes
- [x] Task 150: Verify PIT renders correctly adjacent to other cell types

---

## 4. PIT in Editor Editable Types (~40 tasks)

### 4.1 Editor — EDITABLE_TYPES Update

- [x] Task 151: Open `src/editor.py` for editing
- [x] Task 152: Locate the `EDITABLE_TYPES` list/tuple definition
- [x] Task 153: Add `CellType.PIT` to the EDITABLE_TYPES collection
- [x] Task 154: Verify PIT is appended after existing editable types
- [x] Task 155: Verify EDITABLE_TYPES now includes EMPTY, BUILDING, TRAP, WIND, PIT

### 4.2 Editor — TYPE_NAMES Update

- [x] Task 156: Locate the `TYPE_NAMES` dictionary in editor.py
- [x] Task 157: Add `CellType.PIT: "Pit"` to TYPE_NAMES dict
- [x] Task 158: Verify "Pit" label will display correctly in editor UI
- [x] Task 159: Verify TYPE_NAMES has entries for all editable types

### 4.3 Editor — Type Colors Update

- [x] Task 160: Locate the `type_colors` dictionary in editor.py (or __init__)
- [x] Task 161: Add `CellType.PIT: tuple(colors.pit)` to type_colors dict
- [x] Task 162: Verify PIT color in editor matches renderer PIT color
- [x] Task 163: Verify type_colors has entries for all editable types

### 4.4 Editor — Cell Cycling with PIT

- [x] Task 164: Locate the cell cycling logic (T key or click cycling)
- [x] Task 165: Verify cycling now includes PIT in the rotation
- [x] Task 166: Verify cycling order: EMPTY -> BUILDING -> TRAP -> WIND -> PIT -> EMPTY
- [x] Task 167: Verify PIT can be placed via cycling on any empty cell
- [x] Task 168: Verify PIT can be removed via cycling back to EMPTY

### 4.5 Editor — set_cell with editor=True

- [x] Task 169: Locate where editor calls environment.set_cell()
- [x] Task 170: Update editor set_cell calls to pass `editor=True`
- [x] Task 171: Verify editor-placed cells are tracked in _editor_cells set
- [x] Task 172: Verify editor-placed PIT cells are tracked
- [x] Task 173: Verify removing an editor-placed cell removes from _editor_cells

### 4.6 Editor — Line Count Check

- [x] Task 174: Count total lines in editor.py after PIT additions
- [x] Task 175: Verify editor.py is at or under 150 lines
- [x] Task 176: Verify ruff check passes on editor.py

### 4.7 Tests — PIT in Editor

- [ ] Task 177: Add test: CellType.PIT is in EDITABLE_TYPES
- [ ] Task 178: Add test: TYPE_NAMES contains "Pit" for CellType.PIT
- [ ] Task 179: Add test: type_colors has entry for CellType.PIT
- [ ] Task 180: Add test: cycling through types includes PIT
- [ ] Task 181: Add test: placing PIT via editor tracks in _editor_cells
- [ ] Task 182: Add test: editor displays PIT type button
- [ ] Task 183: Add test: PIT button uses correct color
- [x] Task 184: Run editor tests and verify all pass
- [x] Task 185: Verify no existing editor tests are broken
- [x] Task 186: Verify ruff check passes on test file

### 4.8 Visual Verification — Editor

- [x] Task 187: Run application in editor mode
- [x] Task 188: Verify PIT appears in the cell type selector
- [x] Task 189: Verify clicking PIT button selects PIT type
- [x] Task 190: Verify clicking grid cell places PIT

---

## 5. PIT in Overlays (~35 tasks)

### 5.1 Overlays — Skip PIT in Heatmap

- [x] Task 191: Open `src/overlays.py` for editing
- [x] Task 192: Locate the `_SKIP_HEAT` set or equivalent skip collection
- [x] Task 193: Identify existing skip types (BUILDING, TRAP, etc.)
- [x] Task 194: Add `CellType.PIT` to the _SKIP_HEAT set
- [x] Task 195: Verify PIT cells are excluded from heatmap value calculations
- [x] Task 196: Verify PIT cells show no heatmap gradient overlay
- [x] Task 197: Save overlays.py after skip addition

### 5.2 Overlays — Arrow Rendering with PIT

- [x] Task 198: Locate arrow overlay rendering logic
- [x] Task 199: Verify arrow overlays skip PIT cells (same logic as heatmap skip)
- [x] Task 200: Verify no arrows point into PIT cells (or if they do, that is acceptable)
- [x] Task 201: Verify arrow overlay does not crash when PIT cells exist

### 5.3 Overlays — Line Count Check

- [x] Task 202: Count total lines in overlays.py after PIT skip addition
- [x] Task 203: Verify overlays.py is at or under 150 lines
- [x] Task 204: Verify ruff check passes on overlays.py

### 5.4 Tests — PIT in Overlays

- [ ] Task 205: Add test: PIT is in _SKIP_HEAT set
- [ ] Task 206: Add test: heatmap skips PIT cells
- [ ] Task 207: Add test: heatmap value is not computed for PIT cells
- [ ] Task 208: Add test: overlay rendering handles grid with PIT cells
- [ ] Task 209: Add test: arrow overlay skips PIT cells
- [ ] Task 210: Add test: overlay does not crash on grid full of PIT cells
- [x] Task 211: Run overlay tests and verify all pass
- [x] Task 212: Verify no existing overlay tests are broken

### 5.5 Dashboard — PIT in Legend

- [x] Task 213: Open `src/dashboard.py` for editing
- [x] Task 214: Locate the cell_colors dictionary or legend rendering
- [x] Task 215: Add `"Pit": tuple(c.pit)` to the cell_colors legend dict
- [x] Task 216: Verify PIT appears in the dashboard legend
- [x] Task 217: Verify PIT legend color matches renderer color
- [x] Task 218: Verify dashboard.py stays at or under 150 lines
- [x] Task 219: Save dashboard.py after legend update
- [ ] Task 220: Add test: PIT appears in dashboard legend
- [ ] Task 221: Add test: PIT legend color is correct
- [x] Task 222: Run dashboard tests and verify all pass
- [x] Task 223: Verify ruff check passes on dashboard.py
- [x] Task 224: Verify ruff check passes on dashboard test file
- [x] Task 225: Verify no existing dashboard tests are broken

---

## 6. HazardGenerator Class Creation (~80 tasks)

### 6.1 File Setup

- [x] Task 226: Create new file `src/hazard_generator.py`
- [x] Task 227: Add module docstring: "Dynamic hazard generation for stochastic environments"
- [x] Task 228: Add `from __future__ import annotations` import
- [x] Task 229: Add `import random` import
- [x] Task 230: Add `from src.environment import CellType` import
- [x] Task 231: Add `from src.config_loader import Config` import (or type hint only)

### 6.2 HazardGenerator Class Definition

- [x] Task 232: Define `class HazardGenerator:` class
- [x] Task 233: Add class docstring explaining hazard generation purpose
- [x] Task 234: Define `__init__(self, config: Config)` method signature
- [x] Task 235: Add __init__ docstring: "Initialize from config.dynamic_board settings"
- [x] Task 236: Load `self.enabled = config.dynamic_board.enabled` in __init__
- [x] Task 237: Load `self.density = config.dynamic_board.obstacle_density` in __init__
- [x] Task 238: Load `self.noise_level = config.dynamic_board.noise_level` in __init__
- [x] Task 239: Load `self.difficulty = config.dynamic_board.difficulty` in __init__
- [x] Task 240: Load `self.randomize_per_episode = config.dynamic_board.randomize_per_episode`
- [x] Task 241: Load hazard ratios from config: `config.dynamic_board.hazard_ratios`
- [x] Task 242: Store trap ratio: `self.trap_ratio = hazard_ratios.trap`
- [x] Task 243: Store wind ratio: `self.wind_ratio = hazard_ratios.wind`
- [x] Task 244: Store pit ratio: `self.pit_ratio = hazard_ratios.pit`
- [x] Task 245: Verify ratios sum to approximately 1.0

### 6.3 HazardGenerator._eligible_cells() Method

- [x] Task 246: Define `_eligible_cells(self, env) -> list[tuple[int, int]]` method
- [x] Task 247: Add docstring: "Return cells eligible for hazard placement"
- [x] Task 248: Initialize empty list for eligible cells
- [x] Task 249: Iterate over all grid positions (row, col)
- [x] Task 250: Skip cells that are not EMPTY
- [x] Task 251: Skip the start position cell
- [x] Task 252: Skip the goal position cell
- [x] Task 253: Skip cells in env._editor_cells set
- [x] Task 254: Append eligible cells to the list
- [x] Task 255: Return the list of eligible cells
- [x] Task 256: Verify method handles empty grid correctly
- [x] Task 257: Verify method handles grid with no eligible cells

### 6.4 HazardGenerator._distribute_types() Method

- [x] Task 258: Define `_distribute_types(self, count: int) -> list[CellType]` method
- [x] Task 259: Add docstring: "Distribute count into TRAP/WIND/PIT based on ratios"
- [x] Task 260: Calculate trap count: `int(count * self.trap_ratio)`
- [x] Task 261: Calculate wind count: `int(count * self.wind_ratio)`
- [x] Task 262: Calculate pit count: `count - trap_count - wind_count` (remainder)
- [x] Task 263: Build list of CellType values: trap_count TRAPs + wind_count WINDs + pit_count PITs
- [x] Task 264: Return the distributed list
- [x] Task 265: Verify distribution handles count=0
- [x] Task 266: Verify distribution handles count=1
- [x] Task 267: Verify distribution handles large count values
- [x] Task 268: Verify distribution ratios approximately match configured ratios

### 6.5 HazardGenerator.apply() Method

- [x] Task 269: Define `apply(self, env) -> None` method
- [x] Task 270: Add docstring: "Clear dynamic hazards and place new ones based on current params"
- [x] Task 271: Add early return if `not self.enabled`
- [x] Task 272: Call `env.clear_dynamic_cells(env._editor_cells)` to clear previous hazards
- [x] Task 273: Get eligible cells via `self._eligible_cells(env)`
- [x] Task 274: Calculate target hazard count: `int(self.density * self.difficulty * len(eligible))`
- [x] Task 275: Clamp target count to length of eligible cells list
- [x] Task 276: Handle case where target count is 0: return early
- [x] Task 277: Select random cells: `random.sample(eligible, target_count)`
- [x] Task 278: Get hazard types via `self._distribute_types(target_count)`
- [x] Task 279: Iterate over selected cells and hazard types simultaneously
- [x] Task 280: Call `env.set_cell(row, col, hazard_type)` for each placement
- [x] Task 281: Update wind drift: `env.set_wind_drift(self.noise_level * self.difficulty)`
- [x] Task 282: Verify apply does not modify editor cells
- [x] Task 283: Verify apply does not modify start cell
- [x] Task 284: Verify apply does not modify goal cell

### 6.6 HazardGenerator.clear() Method

- [x] Task 285: Define `clear(self, env) -> None` method
- [x] Task 286: Add docstring: "Remove all dynamically-generated hazards"
- [x] Task 287: Call `env.clear_dynamic_cells(env._editor_cells)` to restore EMPTY
- [x] Task 288: Verify clear restores all dynamic cells to EMPTY
- [x] Task 289: Verify clear preserves editor-placed cells
- [x] Task 290: Verify clear preserves start and goal cells

### 6.7 HazardGenerator.set_params() Method

- [x] Task 291: Define `set_params(self, density: float, noise_level: float, difficulty: float) -> None`
- [x] Task 292: Add docstring: "Update hazard parameters at runtime from GUI sliders"
- [x] Task 293: Set `self.density = density`
- [x] Task 294: Set `self.noise_level = noise_level`
- [x] Task 295: Set `self.difficulty = difficulty`
- [x] Task 296: Clamp density to [0.0, 0.5] range
- [x] Task 297: Clamp noise_level to [0.0, 1.0] range
- [x] Task 298: Clamp difficulty to [0.0, 1.0] range
- [x] Task 299: Verify set_params updates internal state correctly
- [x] Task 300: Verify clamping works for out-of-range values

### 6.8 Line Count Check

- [x] Task 301: Count total lines in hazard_generator.py
- [x] Task 302: Verify hazard_generator.py is at or under 150 lines
- [x] Task 303: Verify ruff check passes on hazard_generator.py
- [x] Task 304: Verify all imports are used and necessary
- [x] Task 305: Verify no hardcoded values exist in the file

---

## 7. HazardGenerator Tests (~75 tasks)

### 7.1 Test File Setup

- [x] Task 306: Create new file `tests/test_hazard_generator.py`
- [x] Task 307: Add module docstring to test file
- [x] Task 308: Import pytest
- [x] Task 309: Import HazardGenerator from src.hazard_generator
- [x] Task 310: Import CellType from src.environment
- [x] Task 311: Import Environment from src.environment
- [x] Task 312: Import load_config or Config from src.config_loader
- [x] Task 313: Create pytest fixture for test config
- [x] Task 314: Create pytest fixture for test environment
- [x] Task 315: Create pytest fixture for test hazard generator

### 7.2 Tests — apply() Method

- [x] Task 316: Test apply places correct number of hazards for density=0.1, difficulty=1.0
- [x] Task 317: Test apply places correct number of hazards for density=0.5, difficulty=1.0
- [x] Task 318: Test apply places correct number of hazards for density=0.1, difficulty=0.5
- [x] Task 319: Test apply places zero hazards when density=0.0
- [x] Task 320: Test apply places zero hazards when difficulty=0.0
- [x] Task 321: Test apply places maximum hazards at density=0.5, difficulty=1.0
- [x] Task 322: Test hazard count scales linearly with density
- [x] Task 323: Test hazard count scales linearly with difficulty
- [x] Task 324: Test apply does not place hazards on start cell (0,0)
- [x] Task 325: Test apply does not place hazards on goal cell (11,11)
- [x] Task 326: Test apply does not overwrite editor-placed cells
- [x] Task 327: Test apply clears previous dynamic hazards before placing new ones
- [x] Task 328: Test apply is a no-op when enabled=False
- [x] Task 329: Test apply updates wind drift probability
- [x] Task 330: Test apply with density=0.1 produces approximately 14 hazards on 12x12
- [x] Task 331: Test apply with randomize_per_episode flag does not affect single call

### 7.3 Tests — Hazard Type Distribution

- [x] Task 332: Test hazard distribution follows configured ratios (30/40/30)
- [x] Task 333: Test trap count is approximately 30% of total hazards
- [x] Task 334: Test wind count is approximately 40% of total hazards
- [x] Task 335: Test pit count is approximately 30% of total hazards
- [x] Task 336: Test distribution handles count=0 (empty list)
- [x] Task 337: Test distribution handles count=1 (single hazard)
- [x] Task 338: Test distribution handles count=2
- [x] Task 339: Test distribution handles count=100 (large number)
- [x] Task 340: Test all distributed types are valid CellType values

### 7.4 Tests — clear() Method

- [x] Task 341: Test clear restores all dynamic cells to EMPTY
- [x] Task 342: Test clear preserves editor-placed BUILDING cells
- [x] Task 343: Test clear preserves editor-placed TRAP cells
- [x] Task 344: Test clear preserves editor-placed WIND cells
- [x] Task 345: Test clear preserves editor-placed PIT cells
- [x] Task 346: Test clear preserves start cell
- [x] Task 347: Test clear preserves goal cell
- [x] Task 348: Test clear on empty grid does nothing
- [x] Task 349: Test clear after apply restores grid to pre-apply state (minus editor cells)

### 7.5 Tests — set_params() Method

- [x] Task 350: Test set_params updates density
- [x] Task 351: Test set_params updates noise_level
- [x] Task 352: Test set_params updates difficulty
- [x] Task 353: Test set_params clamps density to [0.0, 0.5]
- [x] Task 354: Test set_params clamps noise_level to [0.0, 1.0]
- [x] Task 355: Test set_params clamps difficulty to [0.0, 1.0]
- [x] Task 356: Test set_params with negative density clamps to 0.0
- [x] Task 357: Test set_params with density > 0.5 clamps to 0.5
- [x] Task 358: Test set_params with noise > 1.0 clamps to 1.0
- [x] Task 359: Test set_params with difficulty > 1.0 clamps to 1.0

### 7.6 Tests — _eligible_cells() Method

- [x] Task 360: Test eligible cells excludes start position
- [x] Task 361: Test eligible cells excludes goal position
- [x] Task 362: Test eligible cells excludes editor-placed cells
- [x] Task 363: Test eligible cells excludes BUILDING cells
- [x] Task 364: Test eligible cells includes only EMPTY cells
- [x] Task 365: Test eligible cells on empty 12x12 grid returns 142 cells
- [x] Task 366: Test eligible cells on fully occupied grid returns 0 cells
- [x] Task 367: Test eligible cells count is correct after placing some obstacles

### 7.7 Tests — Edge Cases

- [x] Task 368: Test apply with no eligible cells (grid full) does not crash
- [x] Task 369: Test apply with 1 eligible cell places at most 1 hazard
- [x] Task 370: Test apply twice in a row produces consistent hazard count
- [x] Task 371: Test clear followed by apply produces correct results
- [x] Task 372: Test apply followed by clear followed by apply produces correct results
- [x] Task 373: Test hazard generator with minimum grid size (2x2)
- [x] Task 374: Test hazard generator with non-square grid
- [x] Task 375: Test concurrent apply does not corrupt grid state
- [x] Task 376: Run all hazard generator tests and verify they pass
- [x] Task 377: Run ruff check on test_hazard_generator.py
- [x] Task 378: Verify test file is at or under 150 lines
- [x] Task 379: Check test coverage for hazard_generator.py is 85%+
- [x] Task 380: Verify no other test files are broken

---

## 8. SliderPanel Widget Creation (~80 tasks)

### 8.1 File Setup

- [x] Task 381: Create new file `src/sliders.py`
- [x] Task 382: Add module docstring: "Interactive slider widgets for dynamic board parameter control"
- [x] Task 383: Add `from __future__ import annotations` import
- [x] Task 384: Add `import pygame` import
- [x] Task 385: Add type hints import if needed

### 8.2 Slider Class Definition

- [x] Task 386: Define `class Slider:` class
- [x] Task 387: Add Slider class docstring: "A single draggable slider widget"
- [x] Task 388: Define `__init__` method signature with label, x, y, width, min_val, max_val, value, colors
- [x] Task 389: Add __init__ docstring describing all parameters
- [x] Task 390: Store `self.label = label`
- [x] Task 391: Store `self.x = x`
- [x] Task 392: Store `self.y = y`
- [x] Task 393: Store `self.width = width`
- [x] Task 394: Store `self.min_val = min_val`
- [x] Task 395: Store `self.max_val = max_val`
- [x] Task 396: Store `self._value = value`
- [x] Task 397: Store `self.colors = colors` (track, fill, handle colors)
- [x] Task 398: Initialize `self.dragging = False`
- [x] Task 399: Calculate track height: `self.track_h = 6`
- [x] Task 400: Calculate handle radius: `self.handle_r = 6`
- [x] Task 401: Calculate track y position: `self.track_y = y + 20` (below label)

### 8.3 Slider — Value Property

- [x] Task 402: Define `@property value(self) -> float` getter
- [x] Task 403: Return `self._value` from getter
- [x] Task 404: Define `@value.setter` setter
- [x] Task 405: Clamp value to [min_val, max_val] in setter
- [x] Task 406: Store clamped value as `self._value`
- [x] Task 407: Verify value clamping works for values below min_val
- [x] Task 408: Verify value clamping works for values above max_val

### 8.4 Slider — draw() Method

- [x] Task 409: Define `draw(self, surface, font) -> None` method
- [x] Task 410: Add docstring: "Render the slider track, fill, handle, and label"
- [x] Task 411: Calculate the fill width based on current value proportion
- [x] Task 412: Calculate value proportion: `(value - min_val) / (max_val - min_val)`
- [x] Task 413: Calculate fill_w: `int(proportion * self.width)`
- [x] Task 414: Draw track background rectangle with track color
- [x] Task 415: Use `pygame.draw.rect` for track with rounded corners
- [x] Task 416: Draw fill rectangle from left edge to fill_w with fill color
- [x] Task 417: Use `pygame.draw.rect` for fill with rounded corners
- [x] Task 418: Calculate handle x position: `self.x + fill_w`
- [x] Task 419: Calculate handle y position: center of track
- [x] Task 420: Draw handle circle at (handle_x, handle_y) with handle color
- [x] Task 421: Use `pygame.draw.circle` for handle with handle_r radius
- [x] Task 422: Render label text: `f"{self.label}: {self._value:.2f}"`
- [x] Task 423: Use font.render for label text with text color
- [x] Task 424: Blit label text above the track at (self.x, self.y)
- [x] Task 425: Verify draw produces visible output on surface

### 8.5 Slider — handle_event() Method

- [x] Task 426: Define `handle_event(self, event) -> bool` method
- [x] Task 427: Add docstring: "Process mouse events for slider interaction"
- [x] Task 428: Handle MOUSEBUTTONDOWN event
- [x] Task 429: Check if mouse click is within handle area (circular hit test)
- [x] Task 430: If click is on handle, set `self.dragging = True`
- [x] Task 431: Also check if click is on track area (rectangular hit test)
- [x] Task 432: If click is on track, snap value to click position
- [x] Task 433: Handle MOUSEMOTION event when dragging
- [x] Task 434: Calculate new value from mouse x position relative to track
- [x] Task 435: Map mouse x to value: `(mouse_x - self.x) / self.width * (max_val - min_val) + min_val`
- [x] Task 436: Set new value using the value setter (auto-clamps)
- [x] Task 437: Handle MOUSEBUTTONUP event
- [x] Task 438: Set `self.dragging = False` on mouse up
- [x] Task 439: Return True if event was consumed, False otherwise
- [x] Task 440: Verify drag interaction updates value correctly

### 8.6 SliderPanel Class Definition

- [x] Task 441: Define `class SliderPanel:` class
- [x] Task 442: Add SliderPanel class docstring: "Panel containing 3 sliders for dynamic board control"
- [x] Task 443: Define `__init__(self, config, x, y)` method signature
- [x] Task 444: Add __init__ docstring describing parameters
- [x] Task 445: Load slider colors from config: track, fill, handle
- [x] Task 446: Calculate slider spacing: `spacing = 55` (vertical gap between sliders)
- [x] Task 447: Create noise slider: `Slider("Noise", x, y, 180, 0.0, 1.0, config.dynamic_board.noise_level, colors)`
- [x] Task 448: Create density slider: `Slider("Density", x, y+spacing, 180, 0.0, 0.5, config.dynamic_board.obstacle_density, colors)`
- [x] Task 449: Create difficulty slider: `Slider("Difficulty", x, y+2*spacing, 180, 0.0, 1.0, config.dynamic_board.difficulty, colors)`
- [x] Task 450: Store sliders in list: `self.sliders = [noise, density, difficulty]`
- [x] Task 451: Initialize callback: `self._callback = None`
- [x] Task 452: Load font for labels from config or use default
- [x] Task 453: Store `self.font` for label rendering

### 8.7 SliderPanel — draw() Method

- [x] Task 454: Define `draw(self, surface) -> None` method
- [x] Task 455: Add docstring: "Render all sliders in the panel"
- [x] Task 456: Iterate over self.sliders
- [x] Task 457: Call `slider.draw(surface, self.font)` for each slider
- [x] Task 458: Verify all 3 sliders are rendered vertically

### 8.8 SliderPanel — handle_event() Method

- [x] Task 459: Define `handle_event(self, event) -> bool` method
- [x] Task 460: Add docstring: "Delegate events to individual sliders"
- [x] Task 461: Iterate over self.sliders
- [x] Task 462: Call `slider.handle_event(event)` for each slider
- [x] Task 463: If any slider consumed the event, trigger callback
- [x] Task 464: Return True if any slider consumed the event
- [x] Task 465: Call `self._callback(self.get_params())` when values change

### 8.9 SliderPanel — get_params() Method

- [x] Task 466: Define `get_params(self) -> tuple[float, float, float]` method
- [x] Task 467: Add docstring: "Return (density, noise, difficulty) tuple"
- [x] Task 468: Return density from density slider value
- [x] Task 469: Return noise from noise slider value
- [x] Task 470: Return difficulty from difficulty slider value
- [x] Task 471: Verify return order matches SDK set_dynamic_params signature

### 8.10 SliderPanel — set_callback() Method

- [x] Task 472: Define `set_callback(self, fn) -> None` method
- [x] Task 473: Add docstring: "Register callback for value changes"
- [x] Task 474: Store `self._callback = fn`
- [x] Task 475: Verify callback is called when slider values change

### 8.11 Line Count Check

- [x] Task 476: Count total lines in sliders.py
- [x] Task 477: Verify sliders.py is at or under 150 lines
- [x] Task 478: Verify ruff check passes on sliders.py
- [x] Task 479: Verify no hardcoded values (all from config)

---

## 9. SliderPanel Tests (~40 tasks)

### 9.1 Test File Setup

- [x] Task 480: Create new file `tests/test_sliders.py`
- [x] Task 481: Add module docstring to test file
- [x] Task 482: Import pytest
- [x] Task 483: Import Slider and SliderPanel from src.sliders
- [x] Task 484: Create pytest fixture for test config
- [x] Task 485: Create pytest fixture for test slider

### 9.2 Tests — Slider Value

- [x] Task 486: Test slider value defaults to configured value
- [x] Task 487: Test slider value getter returns current value
- [x] Task 488: Test slider value setter updates value
- [x] Task 489: Test slider value clamps to min_val
- [x] Task 490: Test slider value clamps to max_val
- [x] Task 491: Test slider value clamps negative to min_val
- [x] Task 492: Test density slider max_val is 0.5

### 9.3 Tests — SliderPanel

- [x] Task 493: Test SliderPanel creates 3 sliders
- [x] Task 494: Test get_params returns correct tuple
- [x] Task 495: Test get_params returns (density, noise, difficulty) order
- [x] Task 496: Test noise slider initial value matches config
- [x] Task 497: Test density slider initial value matches config
- [x] Task 498: Test difficulty slider initial value matches config
- [x] Task 499: Test set_callback stores callback function
- [x] Task 500: Test callback is triggered on value change
- [x] Task 501: Test callback receives correct parameters

### 9.4 Tests — Slider Interaction

- [x] Task 502: Test handle_event returns False for unrelated events
- [x] Task 503: Test handle_event returns True for track click
- [x] Task 504: Test dragging updates slider value
- [x] Task 505: Test mouse up stops dragging
- [x] Task 506: Test clicking on track snaps value

### 9.5 Tests — Edge Cases

- [x] Task 507: Test slider with min_val == max_val
- [x] Task 508: Test slider with initial value out of range
- [x] Task 509: Test panel with all sliders at zero
- [x] Task 510: Test panel with all sliders at maximum
- [x] Task 511: Run all slider tests and verify they pass
- [x] Task 512: Run ruff check on test_sliders.py
- [x] Task 513: Verify test coverage for sliders.py is 85%+

---

## 10. Config.yaml Additions (~30 tasks)

### 10.1 Dynamic Board Section

- [x] Task 514: Add section comment: `# Dynamic board settings`
- [x] Task 515: Add `dynamic_board:` top-level key
- [x] Task 516: Add `enabled: false` under dynamic_board
- [x] Task 517: Add `obstacle_density: 0.1` under dynamic_board
- [x] Task 518: Add `noise_level: 0.3` under dynamic_board
- [x] Task 519: Add `difficulty: 0.5` under dynamic_board
- [x] Task 520: Add `randomize_per_episode: false` under dynamic_board
- [x] Task 521: Add `hazard_ratios:` subsection under dynamic_board
- [x] Task 522: Add `trap: 0.3` under hazard_ratios
- [x] Task 523: Add `wind: 0.4` under hazard_ratios
- [x] Task 524: Add `pit: 0.3` under hazard_ratios
- [x] Task 525: Verify hazard_ratios sum to 1.0

### 10.2 Slider Colors

- [x] Task 526: Add `slider_track: [50, 55, 80]` to colors section
- [x] Task 527: Add `slider_fill: [80, 140, 255]` to colors section
- [x] Task 528: Add `slider_handle: [200, 210, 240]` to colors section
- [x] Task 529: Verify all slider color RGB values are in 0-255 range

### 10.3 Config Verification

- [x] Task 530: Load config and verify dynamic_board.enabled is False
- [x] Task 531: Load config and verify dynamic_board.obstacle_density is 0.1
- [x] Task 532: Load config and verify dynamic_board.noise_level is 0.3
- [x] Task 533: Load config and verify dynamic_board.difficulty is 0.5
- [x] Task 534: Load config and verify dynamic_board.randomize_per_episode is False
- [x] Task 535: Load config and verify hazard_ratios.trap is 0.3
- [x] Task 536: Load config and verify hazard_ratios.wind is 0.4
- [x] Task 537: Load config and verify hazard_ratios.pit is 0.3
- [x] Task 538: Verify config.yaml parses without errors
- [x] Task 539: Verify config line count is reasonable
- [x] Task 540: Run ruff check on any Python files reading new config values

---

## 11. Integration with SDK and GUI (~45 tasks)

### 11.1 SDK — HazardGenerator Integration

- [x] Task 541: Open `src/sdk.py` for editing
- [x] Task 542: Add import for HazardGenerator from src.hazard_generator
- [x] Task 543: Instantiate HazardGenerator in SDK __init__: `self.generator = HazardGenerator(config)`
- [x] Task 544: Define `set_dynamic_params(self, density, noise, difficulty)` method in SDK
- [x] Task 545: Implement set_dynamic_params: call `self.generator.set_params(density, noise, difficulty)`
- [x] Task 546: Define `randomize_board(self)` method in SDK
- [x] Task 547: Implement randomize_board: call `self.generator.apply(self.environment)`
- [x] Task 548: Modify train_step to check randomize_per_episode flag
- [x] Task 549: If randomize_per_episode, call `self.generator.apply()` before episode
- [x] Task 550: Verify SDK stays at or under 150 lines
- [x] Task 551: Verify ruff check passes on sdk.py

### 11.2 GUI — Slider Panel Integration

- [x] Task 552: Open `src/gui.py` for editing
- [x] Task 553: Add import for SliderPanel from src.sliders
- [x] Task 554: Create SliderPanel in GUI __init__
- [x] Task 555: Set slider callback to SDK set_dynamic_params
- [x] Task 556: In _draw(), render slider panel when editor mode is active
- [x] Task 557: In run(), pass mouse events to slider panel when editor is active
- [x] Task 558: Verify slider panel only appears in editor mode
- [x] Task 559: Verify slider panel does not appear during training
- [x] Task 560: Verify GUI stays at or under 150 lines
- [x] Task 561: Verify ruff check passes on gui.py

### 11.3 Editor — Randomize Button

- [x] Task 562: Open `src/editor.py` for editing
- [ ] Task 563: Add "Randomize" button to editor type button bar
- [ ] Task 564: Wire Randomize button to dispatch "randomize" action
- [ ] Task 565: Verify Randomize button appears in editor panel
- [ ] Task 566: Verify clicking Randomize places hazards on grid
- [x] Task 567: Verify editor.py stays at or under 150 lines

### 11.4 Actions — Randomize Dispatch

- [x] Task 568: Open `src/actions.py` for editing
- [x] Task 569: Add `"randomize"` action handler
- [x] Task 570: Implement randomize action: call `gui.sdk.randomize_board()`
- [x] Task 571: Verify randomize action triggers hazard generation
- [x] Task 572: Verify actions.py stays at or under 150 lines
- [x] Task 573: Verify ruff check passes on actions.py

### 11.5 Trainer — Per-Episode Randomization

- [x] Task 574: Open `src/trainer.py` for editing
- [ ] Task 575: Add optional `hazard_generator` parameter to Trainer __init__
- [ ] Task 576: Store hazard_generator reference in trainer
- [ ] Task 577: In run_episode(), check if generator exists and randomize_per_episode is True
- [ ] Task 578: If so, call `generator.apply(env)` before episode reset
- [x] Task 579: Verify per-episode randomization changes grid between episodes
- [x] Task 580: Verify trainer.py stays at or under 150 lines
- [x] Task 581: Verify ruff check passes on trainer.py

### 11.6 Integration Tests

- [x] Task 582: Add SDK test: set_dynamic_params updates generator parameters
- [x] Task 583: Add SDK test: randomize_board places hazards on grid
- [x] Task 584: Add SDK test: per-episode randomization changes grid
- [x] Task 585: Add SDK test: randomize_board preserves editor cells

---

## 12. Final Verification (~30 tasks)

### 12.1 Full Test Suite

- [x] Task 586: Run `uv run pytest` to execute all tests
- [x] Task 587: Verify all existing 104 tests still pass
- [x] Task 588: Verify all new hazard_generator tests pass
- [x] Task 589: Verify all new slider tests pass
- [x] Task 590: Verify all new PIT tests pass
- [x] Task 591: Verify all new SDK integration tests pass
- [x] Task 592: Verify total test count is correct

### 12.2 Coverage Check

- [x] Task 593: Run `uv run pytest --cov=src --cov-report=html`
- [x] Task 594: Verify hazard_generator.py coverage is 85%+
- [x] Task 595: Verify sliders.py coverage is 85%+
- [x] Task 596: Verify environment.py coverage remains 85%+
- [x] Task 597: Verify renderer.py coverage remains 85%+
- [x] Task 598: Verify overlays.py coverage remains 85%+
- [x] Task 599: Verify editor.py coverage remains 85%+

### 12.3 Lint Check

- [x] Task 600: Run `uv run ruff check src/` with zero violations
- [x] Task 601: Run `uv run ruff check tests/` with zero violations
- [x] Task 602: Run `uv run ruff format --check src/` with zero violations
- [x] Task 603: Run `uv run ruff format --check tests/` with zero violations

### 12.4 Line Count Verification

- [x] Task 604: Verify `src/environment.py` is at or under 150 lines
- [x] Task 605: Verify `src/renderer.py` is at or under 150 lines
- [x] Task 606: Verify `src/overlays.py` is at or under 150 lines
- [x] Task 607: Verify `src/editor.py` is at or under 150 lines
- [x] Task 608: Verify `src/hazard_generator.py` is at or under 150 lines
- [x] Task 609: Verify `src/sliders.py` is at or under 150 lines
- [x] Task 610: Verify `src/sdk.py` is at or under 150 lines
- [x] Task 611: Verify `src/gui.py` is at or under 150 lines
- [x] Task 612: Verify `src/actions.py` is at or under 150 lines
- [x] Task 613: Verify `src/trainer.py` is at or under 150 lines
- [x] Task 614: Verify `src/dashboard.py` is at or under 150 lines

### 12.5 Backward Compatibility

- [x] Task 615: Verify dynamic_board.enabled=false makes apply() a no-op
- [x] Task 616: Verify no sliders render when dynamic_board.enabled=false
- [x] Task 617: Verify environment behaves identically to Assignment 1 when disabled
- [x] Task 618: Verify application runs with `uv run main.py` without errors

### 12.6 Manual Smoke Tests

- [x] Task 619: Launch application and verify editor loads
- [x] Task 620: Place PIT cells manually in editor
- [x] Task 621: Verify PIT cells render as dark purple holes
- [x] Task 622: Train agent and verify PIT cells terminate episodes
- [x] Task 623: Enable dynamic_board and test sliders
- [x] Task 624: Adjust noise slider and verify drift changes
- [x] Task 625: Adjust density slider and verify hazard count changes
- [x] Task 626: Adjust difficulty slider and verify combined effect
- [x] Task 627: Click Randomize and verify grid populates with hazards
- [x] Task 628: Verify editor-placed cells survive randomization
- [x] Task 629: Verify heatmap skips PIT cells
- [x] Task 630: Verify arrow overlay skips PIT cells

### 12.7 Documentation

- [x] Task 631: Update docstrings in environment.py for PIT handling
- [x] Task 632: Update docstrings in renderer.py for PIT rendering
- [x] Task 633: Update docstrings in editor.py for PIT editing
- [x] Task 634: Verify all new methods have docstrings
- [x] Task 635: Verify all new classes have docstrings
- [x] Task 636: Verify all new test functions have descriptive names

### 12.8 Edge Case Verification

- [x] Task 637: Test with empty grid (no obstacles)
- [x] Task 638: Test with grid full of buildings (no eligible cells)
- [x] Task 639: Test with maximum density and difficulty
- [x] Task 640: Test with minimum density and difficulty
- [x] Task 641: Test rapid slider changes
- [x] Task 642: Test multiple randomize clicks in succession
- [x] Task 643: Test switching between editor mode and training mode
- [x] Task 644: Test PIT cell at every grid boundary position
- [x] Task 645: Test PIT cell adjacent to start position
- [x] Task 646: Test PIT cell adjacent to goal position
- [x] Task 647: Test multiple PIT cells in a row
- [x] Task 648: Test PIT cells forming a wall across the grid
- [x] Task 649: Test hazard generation reproducibility with same seed
- [x] Task 650: Test hazard generation variability with different seeds

### 12.9 Performance

- [x] Task 651: Verify hazard generation completes in < 1ms for 12x12 grid
- [x] Task 652: Verify slider rendering does not drop FPS below 60
- [x] Task 653: Verify PIT rendering does not drop FPS below 60
- [x] Task 654: Profile hazard generation for large grids

### 12.10 Config Completeness

- [x] Task 655: Verify zero hardcoded values in hazard_generator.py
- [x] Task 656: Verify zero hardcoded values in sliders.py
- [x] Task 657: Verify zero hardcoded colors in renderer.py PIT code
- [x] Task 658: Verify zero hardcoded penalties in environment.py PIT code
- [x] Task 659: Verify all new config keys are documented with comments
- [x] Task 660: Final review of all changes for Assignment 2 dynamic board

---

## Summary

| Section | Tasks |
|---------|-------|
| 1. CellType.PIT Enum Addition | 45 |
| 2. PIT Handling in environment.step() | 55 |
| 3. PIT Rendering in renderer.py | 50 |
| 4. PIT in Editor Editable Types | 40 |
| 5. PIT in Overlays | 35 |
| 6. HazardGenerator Class Creation | 80 |
| 7. HazardGenerator Tests | 75 |
| 8. SliderPanel Widget Creation | 99 |
| 9. SliderPanel Tests | 34 |
| 10. Config.yaml Additions | 27 |
| 11. Integration with SDK and GUI | 45 |
| 12. Final Verification | 46 |
| **Total** | **570** |
