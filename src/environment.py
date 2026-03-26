"""Smart City grid environment for drone navigation."""

import random
from enum import IntEnum

import numpy as np

from src.config_loader import Config


class CellType(IntEnum):
    EMPTY = 0
    BUILDING = 1
    TRAP = 2
    GOAL = 3
    WIND = 4


# Action definitions: UP=0, DOWN=1, LEFT=2, RIGHT=3
ACTION_DELTAS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}


class Environment:
    """Grid world environment for the drone agent."""

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

        # Load default obstacles from config
        obstacles = getattr(env_cfg, 'obstacles', None)
        if obstacles:
            for obs in obstacles:
                r, c, t = int(obs[0]), int(obs[1]), int(obs[2])
                if (r, c) != self.start and (r, c) != self.goal:
                    self.grid[r, c] = t

        self.drone_pos = self.start

    def reset(self) -> tuple[int, int]:
        """Reset drone to start position and return initial state."""
        self.drone_pos = self.start
        return self.drone_pos

    def step(self, action: int) -> tuple[tuple[int, int], float, bool, dict]:
        """Execute an action and return (next_state, reward, done, info).

        Args:
            action: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT
        """
        info = {"event": "move"}

        # Wind drift: random direction override
        current_cell = self.grid[self.drone_pos[0], self.drone_pos[1]]
        if current_cell == CellType.WIND and random.random() < self.drift_probability:
            action = random.randint(0, 3)
            info["event"] = "wind_drift"

        dr, dc = ACTION_DELTAS[action]
        new_row = self.drone_pos[0] + dr
        new_col = self.drone_pos[1] + dc

        # Boundary check
        if not (0 <= new_row < self.rows and 0 <= new_col < self.cols):
            info["event"] = "wall_collision"
            return self.drone_pos, self.rewards.wall_collision, False, info

        # Building collision
        if self.grid[new_row, new_col] == CellType.BUILDING:
            info["event"] = "wall_collision"
            return self.drone_pos, self.rewards.wall_collision, False, info

        # Move drone
        self.drone_pos = (new_row, new_col)
        cell = self.grid[new_row, new_col]

        if cell == CellType.GOAL:
            return self.drone_pos, self.rewards.goal_reward, True, {"event": "goal"}

        if cell == CellType.TRAP:
            return self.drone_pos, self.rewards.trap_penalty, True, {"event": "trap"}

        if cell == CellType.WIND:
            return self.drone_pos, self.rewards.wind_penalty, False, info

        return self.drone_pos, self.rewards.step_penalty, False, info

    def set_cell(self, row: int, col: int, cell_type: CellType) -> None:
        """Set the type of a grid cell (used by editor)."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row, col] = int(cell_type)

    def get_cell(self, row: int, col: int) -> CellType:
        """Get the type of a grid cell."""
        return CellType(self.grid[row, col])
