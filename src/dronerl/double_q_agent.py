"""Double Q-Learning agent with two Q-tables to prevent overestimation bias."""

import random
from pathlib import Path

import numpy as np

from dronerl.base_agent import DecayingAlphaAgent
from dronerl.config_loader import Config


class DoubleQAgent(DecayingAlphaAgent):
    """Double Q-Learning agent (Hasselt 2010) using two Q-tables to remove TD-bias.

    Input/Output: inherits the ``BaseAgent`` contract via ``DecayingAlphaAgent``.
        Note that ``q_table`` is exposed as ``QA + QB`` for GUI / save / load
        compatibility; the internal storage is the pair ``(q_table_a, q_table_b)``.
    Setup: adds ``config.double_q.alpha_start`` / ``alpha_end`` / ``alpha_decay``,
        same decay protocol as Q-Learning (shared via ``DecayingAlphaAgent``).
    """

    algorithm_name = "Double Q-Learning"

    def __init__(self, config: Config):
        super().__init__(config)
        d_cfg = config.double_q
        self._init_decay(d_cfg.alpha_start, d_cfg.alpha_end, d_cfg.alpha_decay)
        self.update_a_probability = getattr(d_cfg, "update_a_probability", 0.5)
        self.q_table_a = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))
        self.q_table_b = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))

    @property
    def q_table(self) -> np.ndarray:
        """Combined Q-table (QA + QB) for GUI heatmap/arrows compatibility."""
        return self.q_table_a + self.q_table_b

    @q_table.setter
    def q_table(self, _value):
        """Ignore base-class zero init; we manage two tables ourselves."""

    def _cross_table_update(self, q_eval, q_target, state, action, reward, next_state, done) -> None:
        """One Hasselt half-step: pick best action from ``q_eval``, value from ``q_target``."""
        r, c = state
        nr, nc = next_state
        best_a = int(np.argmax(q_eval[nr, nc]))
        next_val = 0.0 if done else float(q_target[nr, nc, best_a])
        target = reward + self.gamma * next_val
        q_eval[r, c, action] += self.alpha * (target - q_eval[r, c, action])

    def update(
        self,
        state: tuple[int, int],
        action: int,
        reward: float,
        next_state: tuple[int, int],
        done: bool,
    ) -> None:
        """Update one Q-table using the other for evaluation (50/50 split)."""
        if random.random() < self.update_a_probability:
            self._cross_table_update(self.q_table_a, self.q_table_b,
                                     state, action, reward, next_state, done)
        else:
            self._cross_table_update(self.q_table_b, self.q_table_a,
                                     state, action, reward, next_state, done)

    def save(self, path: str) -> None:
        """Save both Q-tables to .npy files (path_a.npy and path_b.npy)."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        base = str(target.with_suffix(""))
        np.save(f"{base}_a.npy", self.q_table_a)
        np.save(f"{base}_b.npy", self.q_table_b)

    def load(self, path: str) -> None:
        """Load both Q-tables from .npy files. Missing pair is a no-op (graceful)."""
        base = str(Path(path).with_suffix(""))
        path_a, path_b = Path(f"{base}_a.npy"), Path(f"{base}_b.npy")
        if not (path_a.exists() and path_b.exists()):
            return
        self.q_table_a = np.load(path_a)
        self.q_table_b = np.load(path_b)
