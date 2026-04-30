"""Smart City grid environment for drone navigation."""

import random
from enum import IntEnum

import numpy as np

from dronerl.config_loader import Config
from dronerl.constants import ACTION_DELTAS


class CellType(IntEnum):
    """Grid cell types with integer encoding for the NumPy grid."""

    EMPTY = 0
    BUILDING = 1
    TRAP = 2
    GOAL = 3
    WIND = 4
    PIT = 5


__all__ = ["ACTION_DELTAS", "CellType", "Environment"]


class Environment:
    """Smart City grid world the drone navigates — the RL environment side of the loop.

    Input:  ``step(action: int)`` where action is 0..3 (UP/RIGHT/DOWN/LEFT, see
            ``ACTION_DELTAS``). ``reset() -> tuple[int, int]`` returns the start cell.
    Output: ``step()`` returns ``(next_state, reward, done)``. ``grid`` (NumPy array)
            holds the current ``CellType`` per cell. Edge cases: hitting a wall is a
            no-op move with the wall-collision reward; reaching the goal sets
            ``done=True``; trap / pit cells terminate with their respective penalties.
    Setup:  Config — uses ``environment.grid_rows`` / ``grid_cols`` /
            ``start_position`` / ``goal_position``, all reward magnitudes from
            ``rewards.*``, and ``wind.drift_probability`` for stochastic drift.
    """

    def __init__(self, config: Config):
        env_cfg = config.environment
        self.rows = env_cfg.grid_rows
        self.cols = env_cfg.grid_cols
        self.start = tuple(env_cfg.start_position)
        self.goal = tuple(env_cfg.goal_position)

        self.rewards = config.rewards
        self.drift_probability = config.wind.drift_probability

        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        self.grid[self.goal[0], self.goal[1]] = CellType.GOAL

        # Config-defined obstacles are seeded first; the editor / hazard generator
        # later overrides them, but start and goal cells are always preserved.
        obstacles = getattr(env_cfg, 'obstacles', None)
        if obstacles:
            for obs in obstacles:
                r, c, t = int(obs[0]), int(obs[1]), int(obs[2])
                if (r, c) != self.start and (r, c) != self.goal:
                    self.grid[r, c] = t

        self.drone_pos = self.start
        self._editor_cells: set[tuple[int, int]] = set()

    def reset(self) -> tuple[int, int]:
        """Reset drone to start position and return initial state."""
        self.drone_pos = self.start
        return self.drone_pos

    def is_protected_cell(self, row: int, col: int) -> bool:
        """Return True when the cell is reserved for start or goal."""
        return (row, col) in {self.start, self.goal}

    @property
    def editor_cells(self) -> frozenset[tuple[int, int]]:
        """Read-only snapshot of user-placed cells."""
        return frozenset(self._editor_cells)

    def restore_editor_cells(self, cells) -> None:
        """Replace the editor-cell set from any iterable of (row, col)."""
        self._editor_cells = {tuple(c) for c in cells}

    def step(self, action: int) -> tuple[tuple[int, int], float, bool, dict]:
        """Execute an action and return (next_state, reward, done, info).

        Args:
            action: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT
        """
        info = {"event": "move"}

        # Wind cells override the chosen action with a uniform-random one — this
        # is the noise source the §13 / §15 stochasticity story rests on, and the
        # reason α-decay matters in noisy regimes.
        current_cell = self.grid[self.drone_pos[0], self.drone_pos[1]]
        if current_cell == CellType.WIND and random.random() < self.drift_probability:
            action = random.randint(0, 3)
            info["event"] = "wind_drift"

        dr, dc = ACTION_DELTAS[action]
        new_row = self.drone_pos[0] + dr
        new_col = self.drone_pos[1] + dc

        # Out-of-bounds is a no-op move with the wall-collision penalty: this
        # keeps the state space finite (no off-grid cells) without ever raising.
        if not (0 <= new_row < self.rows and 0 <= new_col < self.cols):
            info["event"] = "wall_collision"
            return self.drone_pos, self.rewards.wall_collision, False, info

        if self.grid[new_row, new_col] == CellType.BUILDING:
            info["event"] = "wall_collision"
            return self.drone_pos, self.rewards.wall_collision, False, info

        self.drone_pos = (new_row, new_col)
        cell = self.grid[new_row, new_col]

        if cell == CellType.GOAL:
            return self.drone_pos, self.rewards.goal_reward, True, {"event": "goal"}

        if cell == CellType.TRAP:
            return self.drone_pos, self.rewards.trap_penalty, True, {"event": "trap"}

        if cell == CellType.PIT:
            return self.drone_pos, self.rewards.pit_penalty, True, {"event": "pit"}

        if cell == CellType.WIND:
            return self.drone_pos, self.rewards.wind_penalty, False, info

        return self.drone_pos, self.rewards.step_penalty, False, info

    def set_cell(self, row: int, col: int, cell_type: CellType, editor: bool = True) -> None:
        """Set the cell type; `editor=True` tracks it as user-placed."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        if self.is_protected_cell(row, col):
            return
        self.grid[row, col] = int(cell_type)
        pos = (row, col)
        if editor and cell_type != CellType.EMPTY:
            self._editor_cells.add(pos)
        elif editor and cell_type == CellType.EMPTY:
            self._editor_cells.discard(pos)

    def get_cell(self, row: int, col: int) -> CellType:
        """Get the type of a grid cell."""
        return CellType(self.grid[row, col])

    def set_wind_drift(self, value: float) -> None:
        """Clamp and set the wind drift probability (0..1)."""
        self.drift_probability = max(0.0, min(1.0, float(value)))

    def clear_dynamic_cells(self) -> None:
        """Reset all non-editor, non-protected cells back to EMPTY."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.is_protected_cell(r, c) or (r, c) in self._editor_cells:
                    continue
                self.grid[r, c] = int(CellType.EMPTY)
