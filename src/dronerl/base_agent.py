"""Abstract base class for all RL agents."""

import random
from pathlib import Path

import numpy as np

from dronerl.config_loader import Config


class BaseAgent:
    """Abstract base for RL agents. Subclasses must override `update`."""

    # Actions: UP=0, DOWN=1, LEFT=2, RIGHT=3
    NUM_ACTIONS = 4
    algorithm_name: str = "Base"

    def __init__(self, config: Config):
        env_cfg = config.environment
        agent_cfg = config.agent

        self.rows = env_cfg.grid_rows
        self.cols = env_cfg.grid_cols

        self.gamma = agent_cfg.discount_factor
        self.epsilon = agent_cfg.epsilon_start
        self.epsilon_end = agent_cfg.epsilon_end
        self.epsilon_decay = agent_cfg.epsilon_decay

        self.q_table = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))

    def choose_action(self, state: tuple[int, int]) -> int:
        """Select action using epsilon-greedy policy."""
        if random.random() < self.epsilon:
            return random.randint(0, self.NUM_ACTIONS - 1)
        return self.get_best_action(state)

    def get_best_action(self, state: tuple[int, int]) -> int:
        """Return the action with highest Q-value for the given state."""
        return int(np.argmax(self.q_table[state[0], state[1]]))

    def get_max_q(self, state: tuple[int, int]) -> float:
        """Return the maximum Q-value for the given state."""
        return float(np.max(self.q_table[state[0], state[1]]))

    def update(
        self,
        state: tuple[int, int],
        action: int,
        reward: float,
        next_state: tuple[int, int],
        done: bool,
    ) -> None:
        """Update Q-value(s). Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement update()")

    def decay_epsilon(self) -> None:
        """Decay epsilon by the decay rate, clamped to epsilon_end."""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def save(self, path: str) -> None:
        """Save Q-table to a numpy file."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, self.q_table)

    def load(self, path: str) -> None:
        """Load Q-table from a numpy file."""
        self.q_table = np.load(path)
