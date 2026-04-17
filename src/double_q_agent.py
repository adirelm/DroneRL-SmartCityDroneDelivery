"""Double Q-Learning agent with two Q-tables to prevent overestimation bias."""

import random
from pathlib import Path

import numpy as np

from src.base_agent import BaseAgent
from src.config_loader import Config


class DoubleQAgent(BaseAgent):
    """Double Q-Learning agent with QA and QB tables (Hasselt 2010)."""

    algorithm_name = "Double Q-Learning"

    def __init__(self, config: Config):
        super().__init__(config)
        d_cfg = config.double_q
        self.alpha = d_cfg.alpha_start
        self.alpha_end = d_cfg.alpha_end
        self.alpha_decay = d_cfg.alpha_decay
        self.q_table_a = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))
        self.q_table_b = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))

    @property
    def q_table(self) -> np.ndarray:
        """Combined Q-table (QA + QB) for GUI heatmap/arrows compatibility."""
        return self.q_table_a + self.q_table_b

    @q_table.setter
    def q_table(self, _value):
        """Ignore base-class zero init; we manage two tables ourselves."""

    def update(
        self,
        state: tuple[int, int],
        action: int,
        reward: float,
        next_state: tuple[int, int],
        done: bool,
    ) -> None:
        """Update one Q-table using the other for evaluation (50/50 split)."""
        r, c = state
        nr, nc = next_state
        if random.random() < 0.5:
            best_a = int(np.argmax(self.q_table_a[nr, nc]))
            next_val = 0.0 if done else float(self.q_table_b[nr, nc, best_a])
            target = reward + self.gamma * next_val
            self.q_table_a[r, c, action] += self.alpha * (target - self.q_table_a[r, c, action])
        else:
            best_a = int(np.argmax(self.q_table_b[nr, nc]))
            next_val = 0.0 if done else float(self.q_table_a[nr, nc, best_a])
            target = reward + self.gamma * next_val
            self.q_table_b[r, c, action] += self.alpha * (target - self.q_table_b[r, c, action])

    def decay_alpha(self) -> None:
        """Decay alpha by the decay rate, clamped to alpha_end."""
        self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)

    def decay_epsilon(self) -> None:
        """Decay both epsilon and alpha per episode."""
        super().decay_epsilon()
        self.decay_alpha()

    def save(self, path: str) -> None:
        """Save both Q-tables to .npy files (path_a.npy and path_b.npy)."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        base = str(target.with_suffix(""))
        np.save(f"{base}_a.npy", self.q_table_a)
        np.save(f"{base}_b.npy", self.q_table_b)

    def load(self, path: str) -> None:
        """Load both Q-tables from .npy files."""
        base = str(Path(path).with_suffix(""))
        self.q_table_a = np.load(f"{base}_a.npy")
        self.q_table_b = np.load(f"{base}_b.npy")
