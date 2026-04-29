# Product Requirements Document (PRD)

## Dynamic Board — Stochastic Environment Extension

---

## 1. Project Overview & Background

This PRD extends the existing DroneRL project (Assignment 1) with a **dynamic, stochastic environment** that introduces unpredictable hazards and configurable difficulty. The static 12x12 grid from Assignment 1 is enhanced with runtime-configurable obstacle generation, new hazard types, and interactive GUI sliders for controlling environment complexity.

### Context

In Assignment 1, the drone learned to navigate a **static grid** with fixed buildings, traps, and wind zones using Bellman-equation Q-value updates. While this demonstrated core RL concepts, the static environment made it too easy for any algorithm to converge given enough episodes.

Assignment 2 requires a **dynamic, noisy environment** that:
- Exposes differences between RL algorithms (Bellman vs Q-Learning vs Double Q-Learning)
- Allows the user to control complexity via GUI sliders
- Generates random hazards per-episode or on-demand
- Introduces a new hazard type: **Pits** (holes in the ground)

### Existing Codebase Reference

This PRD builds on the existing project structure. Key files to reference:
- `src/environment.py` — Current `Environment` class with `CellType` enum (EMPTY, BUILDING, TRAP, GOAL, WIND)
- `src/editor.py` — Level editor for manual obstacle placement
- `src/renderer.py` — Grid cell rendering
- `config/config.yaml` — All environment parameters
- `docs/assignment-1/PRD.md` — Original project PRD

---

## 2. Objectives & Success Metrics

### Objectives

1. **Dynamic Hazard Generation**: The environment can randomly place obstacles on empty cells based on configurable density and difficulty parameters.
2. **New Hazard Type**: Introduce PIT cells — terminal hazards (like traps) with a distinct penalty and visual representation.
3. **GUI Sliders**: Interactive sliders in the editor panel to control noise level, obstacle density, and overall difficulty in real-time.
4. **Per-Episode Randomization**: Option to re-randomize hazards at the start of each episode, creating a truly stochastic environment.
5. **Editor Compatibility**: Dynamic hazards coexist with manually-placed obstacles — editor-placed cells are preserved during randomization.

### Success Metrics

| Metric | Target |
|--------|--------|
| PIT cell handled correctly in environment step | Terminates episode, applies pit_penalty |
| Hazard density slider controls obstacle count | Linear correlation: density 0.1 → ~14 hazards on 12x12 grid |
| Noise slider controls wind drift probability | 0.0 = no drift, 1.0 = always drift |
| Difficulty slider combines density + noise | 0.0 = empty grid, 1.0 = maximum hazards + drift |
| Editor-placed cells survive randomization | 100% preservation |
| All parameters from config.yaml | Zero hardcoded values |
| HazardGenerator covered by tests | 85%+ coverage |
| All new files ≤ 150 lines | Strict enforcement |

### KPIs

- At difficulty 0.0 (easy): Bellman agent converges within 2000 episodes
- At difficulty 0.5 (medium): Bellman agent struggles, Q-Learning converges within 5000 episodes
- At difficulty 1.0 (hard): Only Double Q-Learning converges reliably within 10000 episodes

---

## 3. Functional Requirements

### 3.1 New Cell Type: PIT

- **CellType.PIT = 5** added to the existing `CellType` IntEnum in `src/environment.py`
- **Behavior**: When the drone steps onto a PIT cell, the episode terminates immediately (like TRAP)
- **Reward**: Configurable `pit_penalty` (default: -75), stored in `config.yaml` under `rewards.pit_penalty`
- **Visual**: Dark purple circle/hole rendered in `src/renderer.py`
- **Editor**: PIT is added to `EDITABLE_TYPES` in `src/editor.py`, allowing manual placement
- **Overlays**: PIT cells are skipped in heatmap rendering (like BUILDING and TRAP)
- **Info**: `step()` returns `info["event"] = "pit"` when drone falls into a pit

### 3.2 Hazard Generator

A new class `HazardGenerator` in `src/hazard_generator.py` responsible for:

#### Parameters (all from config.yaml)

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `obstacle_density` | float | 0.0–0.5 | 0.1 | Fraction of empty cells to fill with hazards |
| `noise_level` | float | 0.0–1.0 | 0.3 | Wind drift probability override |
| `difficulty` | float | 0.0–1.0 | 0.5 | Combined scaling factor for density + noise |
| `randomize_per_episode` | bool | — | false | Re-randomize hazards at each episode start |

#### Methods

- `apply(environment)` — Clear previous dynamic hazards, calculate target count based on density × difficulty, randomly place TRAP, WIND, and PIT cells on eligible empty cells (not start, not goal, not editor-placed). Update wind drift probability based on noise_level.
- `clear(environment)` — Remove all dynamically-generated hazards, restoring cells to EMPTY.
- `set_params(density, noise_level, difficulty)` — Update parameters at runtime (called by GUI sliders).

#### Hazard Distribution

When placing hazards, the generator distributes them across types:
- 30% TRAP cells
- 40% WIND cells
- 30% PIT cells

These ratios are configurable via config.yaml under `dynamic_board.hazard_ratios`.

### 3.3 Environment Extensions

Modifications to `src/environment.py`:

- **Editor-cell tracking** — Environment maintains an internal set of editor-placed `(row, col)` coordinates updated by `set_cell(..., editor=True)`. The public surface is the `editor_cells` frozenset property (read-only snapshot) and `restore_editor_cells(iterable)` method (used by the SDK's compare-on-same-board flow). Dynamic hazards never overwrite editor cells.
- **`set_wind_drift(probability: float)`** — Allows runtime modification of the wind drift probability, called by the hazard generator when noise_level changes.
- **`clear_dynamic_cells(editor_cells: set)`** — Clears all cells NOT in the editor_cells set back to EMPTY.
- **PIT handling in `step()`** — Added alongside TRAP handling: if cell is PIT, return `(state, pit_penalty, True, {"event": "pit"})`.

### 3.4 GUI Sliders

A new `SliderPanel` widget in `src/sliders.py`:

#### Slider Widget

- **Track**: Horizontal rectangle (180px wide, 6px tall) with rounded ends
- **Fill**: Colored portion from left to current value
- **Handle**: Circular draggable handle (12px diameter) positioned at current value
- **Label**: Text above the slider showing name and current value (e.g., "Noise: 0.35")
- **Value Range**: 0.0 to 1.0, continuous

#### Panel Layout

Three sliders arranged vertically:
1. **Noise Level** — Controls wind drift probability (0.0 = no drift, 1.0 = always drift)
2. **Obstacle Density** — Controls fraction of empty cells filled with hazards (0.0 = none, 0.5 = half)
3. **Difficulty** — Master knob that scales both noise and density together

#### Interaction

- **Mouse drag**: Click and drag the handle to change value
- **Visibility**: Sliders appear in the editor bar area when editor mode is active
- **Callback**: Value changes trigger `sdk.set_dynamic_params(density, noise, difficulty)`
- **Apply button**: "Randomize" button next to sliders applies the current settings immediately

### 3.5 Configuration (config.yaml additions)

```yaml
# Dynamic board settings
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

# New reward
rewards:
  pit_penalty: -75

# New colors
colors:
  pit: [120, 40, 160]
  pit_accent: [160, 60, 200]
  slider_track: [50, 55, 80]
  slider_fill: [80, 140, 255]
  slider_handle: [200, 210, 240]
```

---

## 4. Non-Functional Requirements

- **Performance**: Hazard generation must complete in < 1ms for a 12x12 grid (144 cells)
- **Determinism**: When `randomize_per_episode` is false, the board remains stable between episodes
- **Backward Compatibility**: When `dynamic_board.enabled` is false, the environment behaves identically to Assignment 1
- **File Size**: `src/hazard_generator.py` ≤ 150 lines, `src/sliders.py` ≤ 150 lines
- **Test Coverage**: All new code must have 85%+ test coverage
- **Linting**: Zero ruff violations
- **Config-Driven**: Zero hardcoded values in source files

---

## 5. User Stories

1. **As a student**, I want to increase the noise level so I can see how stochastic environments affect Q-Learning convergence.
2. **As a student**, I want to add pits to the grid so I have more hazard variety beyond traps.
3. **As a student**, I want sliders to control difficulty so I can quickly test different environment configurations.
4. **As a student**, I want the board to randomize per episode so each training episode faces a different layout.
5. **As a student**, I want my manually-placed obstacles to be preserved when I randomize, so I can design a base layout and add noise on top.

---

## 6. Assumptions & Constraints

- The grid size remains 12x12 (144 cells total, minus start and goal = 142 eligible cells)
- Maximum density of 0.5 means at most ~71 hazard cells, leaving ~71 empty cells for navigation
- The drone always starts at (0,0) and the goal is always at (11,11)
- PIT cells are functionally similar to TRAPs but with a different penalty and visual
- Sliders only appear when the editor panel is active (to avoid cluttering the training view)

---

## 7. Acceptance Criteria

- [ ] `CellType.PIT` exists and is handled in `environment.step()`
- [ ] PIT cells render as dark purple holes in the grid
- [ ] PIT cells are editable via the level editor (cycle with T key)
- [ ] `HazardGenerator.apply()` places hazards on empty cells respecting density
- [ ] `HazardGenerator.clear()` removes all dynamic hazards
- [ ] Editor-placed cells are never overwritten by the generator
- [ ] Noise slider changes wind drift probability in real-time
- [ ] Density slider controls the number of generated hazards
- [ ] Difficulty slider scales both noise and density together
- [ ] `randomize_per_episode` flag regenerates hazards each episode when true
- [ ] All parameters come from `config/config.yaml`
- [ ] `hazard_generator.py` has 85%+ test coverage
- [ ] `sliders.py` has 85%+ test coverage
- [ ] No file exceeds 150 lines
- [ ] Zero ruff violations
- [ ] Application runs correctly with `uv run main.py`

---

## 8. Timeline & Milestones

| Phase | Deliverable |
|-------|------------|
| 1 | Add CellType.PIT to environment, renderer, editor, overlays |
| 2 | Create HazardGenerator class with apply/clear/set_params |
| 3 | Create SliderPanel widget with 3 sliders |
| 4 | Integrate sliders into editor panel in GUI |
| 5 | Wire sliders → SDK → HazardGenerator → Environment |
| 6 | Write tests for all new components |
| 7 | Update config.yaml with new sections |
| 8 | Verify backward compatibility with dynamic_board.enabled = false |

---

## Alternatives Considered

The chosen design (slider-driven `HazardGenerator` operating on a public
`Environment.editor_cells` API, with `CellType.PIT` joining the existing
hazard taxonomy) was selected from several alternatives.

| Alternative | Rejected because |
|-------------|------------------|
| **Procedural generation per episode (mazegen / Wave Function Collapse)** | Solves a different problem — "make every episode novel". The lecturer's brief is the opposite: *same* board, *configurable* difficulty (transcript: *"כל מיני סליידרים שמאפשרים להוסיף רעש, להבריד רעש"*). A user-controlled hazard density slider matches that intent better than autonomous procedural generation. |
| **Fixed scenario presets (3-5 hand-designed boards)** | Less flexible for the comparison study — every difficulty axis (noise / density / mix) becomes a separate preset, exploding the matrix. Sliders give continuous control which is what the cross-algorithm comparison needs. |
| **Subclass `Environment` for stochastic variants** | Inheritance for behavior change is the wrong tool here — the stochastic behavior is data (hazard placement) on the same Environment, not a different Environment. Composition (`HazardGenerator` operating on Environment) is cleaner. |
| **Mutate `Environment` directly from the GUI without an SDK round-trip** | Violates the SDK-as-single-entry-point principle. All slider events go through `SDK.set_dynamic_params()` so headless tests and the GUI share one code path. |
| **One slider for "difficulty," derived noise/density internally** | Loses control over which axis dominates. Decomposing into noise / density / difficulty (with `difficulty` as a master multiplier) lets the comparison experiments isolate which axis Bellman fails on (it's noise, not density — see EXPERIMENTS.md). |
| **Make `editor_cells` a public attribute (not a property)** | Earlier draft did this. Rejected during the post-feedback Pass 1 review because it leaked an internal mutable container. Replaced with a `frozenset` property + `restore_editor_cells(iterable)` method so callers can't accidentally mutate the live set. |
