# Implementation Plan

## Dynamic Board — Stochastic Environment Extension

---

## Architecture Strategy

The dynamic board system introduces a **runtime-configurable hazard layer** on top of the existing static grid. The key architectural decisions are:

1. **HazardGenerator as a standalone service** — A new `src/hazard_generator.py` class that operates on the Environment without subclassing it. The generator reads density/noise/difficulty parameters and places hazards on eligible empty cells, preserving editor-placed obstacles via an `_editor_cells` tracking set inside Environment.

2. **PIT as a new CellType** — `CellType.PIT = 5` extends the existing IntEnum. The PIT integrates into the same step/render/overlay pipeline as TRAP (terminal, negative reward, skipped in heatmap).

3. **SliderPanel as a reusable GUI widget** — A new `src/sliders.py` module provides a self-contained slider widget with track, fill, and draggable handle. Three sliders (noise, density, difficulty) live in the editor bar area and only render when editor mode is active.

4. **Separation of concerns** — The data flow is: `Sliders -> SDK -> HazardGenerator -> Environment`. The GUI never directly mutates environment state; it calls SDK methods that delegate to the generator.

```
SliderPanel (src/sliders.py)
      |
      v
  SDK.set_dynamic_params()
      |
      v
HazardGenerator.set_params() + .apply()
      |
      v
Environment (grid mutation, _editor_cells preservation)
      |
      v
Renderer (PIT visual) + Overlays (skip PIT in heatmap)
```

---

## Development Approach: TDD

1. **Write tests first** for HazardGenerator: apply/clear/set_params, density correlation, editor cell preservation, hazard type distribution.
2. **Write tests first** for PIT handling: step returns pit_penalty + done=True, renderer/overlay skip logic, editor cycle includes PIT.
3. **Implement** each module to pass its tests.
4. **Integration test**: sliders -> SDK -> generator -> environment round-trip.

---

## Phase 1: CellType.PIT Integration

Add the new PIT cell type to all existing modules that handle cell types.

### 1.1 Environment — PIT Cell Type and Handling (~10 lines added)

**File**: `src/environment.py` (currently 110 lines -> ~125 lines)

- Add `PIT = 5` to `CellType` IntEnum
- Add `_editor_cells: set[tuple[int, int]]` initialized to empty set in `__init__`
- Add PIT handling in `step()`: if cell is PIT, return `(state, pit_penalty, True, {"event": "pit"})`
- Add `set_wind_drift(probability: float)` method for runtime drift override
- Add `clear_dynamic_cells(editor_cells: set)` method to reset non-editor cells to EMPTY
- Modify `set_cell()` to optionally track editor-placed cells via an `editor=False` parameter

### 1.2 Renderer — PIT Visual (~15 lines added)

**File**: `src/renderer.py` (currently 135 lines -> ~150 lines)

- Add PIT color attributes (`c_pit`, `c_pit_acc`) from config in `__init__`
- Add `_draw_pit(surf, x, y)` method: dark purple cell with a circular hole/void visual
- Register `CellType.PIT: self._draw_pit` in the `draw` dict inside `draw_grid()`

### 1.3 Overlays — Skip PIT in Heatmap (~2 lines changed)

**File**: `src/overlays.py` (currently 130 lines -> ~131 lines)

- Add `CellType.PIT` to `_SKIP_HEAT` set (line 10)

### 1.4 Editor — PIT in Editable Types (~3 lines changed)

**File**: `src/editor.py` (currently 128 lines -> ~135 lines)

- Add `CellType.PIT` to `EDITABLE_TYPES` list
- Add `CellType.PIT: "Pit"` to `TYPE_NAMES` dict
- Add `CellType.PIT: tuple(colors.pit)` to `self.type_colors` dict

### 1.5 Config — PIT Reward and Colors (~5 lines added)

**File**: `config/config.yaml` (currently 121 lines -> ~130 lines)

- Add `pit_penalty: -75` under `rewards`
- Add `pit: 5` under `cell_types`
- Add `pit: [120, 40, 160]` and `pit_accent: [160, 60, 200]` under `colors`

### 1.6 Tests — PIT Behavior

**File**: `tests/test_environment.py` (add ~20 lines)

- Test PIT cell terminates episode with pit_penalty
- Test PIT returns `info["event"] == "pit"`
- Test PIT cell is not a protected cell
- Test step on PIT sets done=True

**File**: `tests/test_editor.py` or `tests/test_ui_components.py` (add ~5 lines)

- Test PIT is in EDITABLE_TYPES
- Test editor cycles through PIT

---

## Phase 2: HazardGenerator

### 2.1 HazardGenerator Class

**File**: `src/hazard_generator.py` (~100 lines, new file)

```
class HazardGenerator:
    __init__(config)        — Load density, noise, difficulty, ratios, enabled flag from config
    apply(environment)      — Clear dynamic cells, calculate target count, randomly place hazards
    clear(environment)      — Remove all dynamic hazards (restore to EMPTY)
    set_params(density, noise, difficulty) — Update parameters at runtime
    _eligible_cells(env)    — Return list of empty cells excluding start, goal, and editor cells
    _distribute_types(count) — Split count into TRAP/WIND/PIT based on hazard_ratios
```

Key implementation details:
- `apply()` calls `env.clear_dynamic_cells(env._editor_cells)` first, then places hazards
- Target hazard count = `int(density * difficulty * eligible_cell_count)`
- After placing hazards, calls `env.set_wind_drift(noise_level * difficulty)` to adjust wind drift
- Uses `random.sample()` on eligible cells for placement (no duplicates)
- Hazard type distribution uses config ratios (default: 30% TRAP, 40% WIND, 30% PIT)

### 2.2 Config — Dynamic Board Section

**File**: `config/config.yaml` (add ~12 lines)

```yaml
dynamic_board:
  enabled: false
  obstacle_density: 0.1
  noise_level: 0.3
  difficulty: 0.5
  randomize_per_episode: false
  hazard_ratios:
    trap: 0.3
    wind: 0.4
    pit: 0.3
```

### 2.3 Tests — HazardGenerator

**File**: `tests/test_hazard_generator.py` (~120 lines, new file)

- Test `apply()` places correct number of hazards for given density/difficulty
- Test hazard count scales linearly with density (density 0.1 -> ~14 hazards on 12x12)
- Test hazard type distribution matches configured ratios (within tolerance)
- Test `clear()` restores all dynamic cells to EMPTY
- Test editor-placed cells are never overwritten during `apply()`
- Test `set_params()` updates density, noise, and difficulty
- Test start cell (0,0) and goal cell (11,11) are never overwritten
- Test with `enabled: false` — `apply()` is a no-op
- Test noise_level updates wind drift probability via `set_wind_drift()`
- Test difficulty=0 produces zero hazards
- Test difficulty=1 with density=0.5 fills half the eligible cells

---

## Phase 3: Slider Widget

### 3.1 SliderPanel Widget

**File**: `src/sliders.py` (~140 lines, new file)

```
class Slider:
    __init__(label, x, y, width, min_val, max_val, value, colors)
    draw(surface, font)     — Render track, fill, handle, and label text
    handle_event(event)     — Process MOUSEBUTTONDOWN/MOUSEMOTION/MOUSEBUTTONUP
    value (property)        — Current float value

class SliderPanel:
    __init__(config)        — Create 3 sliders: noise, density, difficulty
    draw(surface)           — Render all sliders vertically
    handle_event(event)     — Delegate to individual sliders
    get_params()            — Return (density, noise, difficulty) tuple
    set_callback(fn)        — Register callback for value changes
```

Widget specifications:
- Track: 180px wide, 6px tall, rounded ends, `slider_track` color
- Fill: left-aligned colored portion, `slider_fill` color
- Handle: 12px diameter circle, `slider_handle` color, draggable
- Label: above slider, shows name and value (e.g., "Noise: 0.35")
- Value range: 0.0 to 1.0 (density capped at 0.5)

### 3.2 Config — Slider Colors

**File**: `config/config.yaml` (add ~3 lines under `colors`)

```yaml
slider_track: [50, 55, 80]
slider_fill: [80, 140, 255]
slider_handle: [200, 210, 240]
```

### 3.3 Tests — SliderPanel

**File**: `tests/test_sliders.py` (~80 lines, new file)

- Test slider value defaults to config value
- Test slider value clamps to [min_val, max_val]
- Test `get_params()` returns correct tuple
- Test value change triggers callback
- Test density slider max is 0.5

---

## Phase 4: Integration

### 4.1 SDK — Dynamic Board Methods (~15 lines added)

**File**: `src/sdk.py` (currently 90 lines -> ~110 lines)

- Import and instantiate `HazardGenerator` in `__init__`
- Add `set_dynamic_params(density, noise, difficulty)` — delegates to generator
- Add `randomize_board()` — calls `generator.apply(self.environment)`
- Modify `train_step()` — if `randomize_per_episode` is true, call `generator.apply()` before episode

### 4.2 GUI — Slider Integration (~15 lines added)

**File**: `src/gui.py` (currently 129 lines -> ~145 lines)

- Import `SliderPanel` in GUI
- Create slider panel in `__init__`, set callback to `sdk.set_dynamic_params`
- In `_draw()`: render slider panel when editor is active
- In `run()`: pass mouse events to slider panel when editor is active
- Add "Randomize" button via editor panel or keyboard shortcut

### 4.3 Editor — Randomize Button (~5 lines added)

**File**: `src/editor.py` (after Phase 1: ~135 lines -> ~140 lines)

- Add a "Randomize" button in the type button bar
- Clicking it triggers `sdk.randomize_board()` action via the action dispatch system

### 4.4 Actions — New Dispatch Entries (~5 lines added)

**File**: `src/actions.py` (currently 56 lines -> ~62 lines)

- Add `"randomize"` action that calls `gui.sdk.randomize_board()` (if SDK is wired)
- The randomize action is dispatched from editor "Randomize" button click

### 4.5 Trainer — Per-Episode Randomization (~5 lines added)

**File**: `src/trainer.py` (currently 83 lines -> ~90 lines)

- Accept optional `hazard_generator` parameter in `__init__`
- In `run_episode()`, if generator exists and `randomize_per_episode` is true, call `generator.apply(env)` before resetting

### 4.6 Integration Tests

**File**: `tests/test_sdk.py` (add ~15 lines)

- Test `set_dynamic_params()` updates generator parameters
- Test `randomize_board()` places hazards on the environment grid
- Test per-episode randomization changes the grid between episodes

---

## Phase 5: Dashboard Updates

### 5.1 Dashboard — PIT in Legend (~3 lines added)

**File**: `src/dashboard.py` (currently 147 lines -> ~150 lines)

- Add `"Pit": tuple(c.pit)` to `self.cell_colors` dict in `__init__`

---

## File Size Constraint

Every `.py` file must stay under **150 lines**. Estimated final line counts:

| File | Current | After Changes | Status |
|------|---------|---------------|--------|
| `src/environment.py` | 110 | ~125 | OK |
| `src/renderer.py` | 135 | ~150 | At limit |
| `src/overlays.py` | 130 | ~131 | OK |
| `src/editor.py` | 128 | ~140 | OK |
| `src/hazard_generator.py` | 0 (new) | ~100 | OK |
| `src/sliders.py` | 0 (new) | ~140 | OK |
| `src/sdk.py` | 90 | ~110 | OK |
| `src/gui.py` | 129 | ~145 | OK |
| `src/actions.py` | 56 | ~62 | OK |
| `src/trainer.py` | 83 | ~90 | OK |
| `src/dashboard.py` | 147 | ~150 | At limit |
| `config/config.yaml` | 121 | ~145 | OK |
| `tests/test_hazard_generator.py` | 0 (new) | ~120 | OK |
| `tests/test_sliders.py` | 0 (new) | ~80 | OK |

**Risk mitigation**: If `renderer.py` exceeds 150 lines after adding PIT rendering, extract all `_draw_*` cell methods into a helper module `src/cell_drawers.py`. If `dashboard.py` exceeds 150 lines, the legend can be extracted into a small helper.

---

## Backward Compatibility

When `dynamic_board.enabled` is `false` (default):
- `HazardGenerator.apply()` returns immediately (no-op)
- No sliders are rendered in the editor panel
- Environment behaves identically to Assignment 1
- All 104 existing tests pass without modification
