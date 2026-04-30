"""Abstract base class for all RL agents."""

import random
from pathlib import Path

import numpy as np

from dronerl.config_loader import Config
from dronerl.constants import NUM_ACTIONS


class BaseAgent:
    """Abstract base for RL agents. Subclasses must override ``update``.

    Input:  state (tuple[int, int]) — (row, col), 0 ≤ row < grid_rows, 0 ≤ col < grid_cols;
            action (int 0..NUM_ACTIONS-1); reward (float); next_state (tuple[int, int]);
            done (bool).
    Output: ``choose_action(state) -> int`` (action 0..3);
            ``update(...) -> None`` (mutates ``self.q_table`` in place);
            ``save(path) -> None`` / ``load(path) -> None`` (writes/reads a ``.npy`` file).
    Setup:  Config — uses ``environment.grid_rows`` / ``grid_cols`` and
            ``agent.discount_factor``, ``agent.epsilon_start``, ``agent.epsilon_end``,
            ``agent.epsilon_decay``. Subclasses add their own algorithm-specific keys.
    """

    #: Class-level alias of :data:`dronerl.constants.NUM_ACTIONS` so existing
    #: subclass code that reads ``self.NUM_ACTIONS`` continues to work.
    NUM_ACTIONS = NUM_ACTIONS
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

        self._validate_config()
        self.q_table = np.zeros((self.rows, self.cols, self.NUM_ACTIONS))

    def _validate_config(self) -> None:
        """§16.3 — fail fast on malformed Setup data, with clear messages."""
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError(f"grid dimensions must be positive: got {self.rows}x{self.cols}")
        if not 0.0 <= self.gamma <= 1.0:
            raise ValueError(f"discount_factor must be in [0, 1]: got {self.gamma}")
        if not 0.0 <= self.epsilon_end <= self.epsilon <= 1.0:
            raise ValueError(
                f"epsilon range invalid: start={self.epsilon}, end={self.epsilon_end} "
                "(require 0 ≤ end ≤ start ≤ 1)"
            )
        if not 0.0 < self.epsilon_decay <= 1.0:
            raise ValueError(f"epsilon_decay must be in (0, 1]: got {self.epsilon_decay}")

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

    def _td_update(self, q, state, action, reward, next_state, done, step) -> None:
        """In-place Bellman TD update: ``q[s,a] += step · (r + γ·max q[s'] − q[s,a])``."""
        r, c = state
        nr, nc = next_state
        next_max = 0.0 if done else float(np.max(q[nr, nc]))
        target = reward + self.gamma * next_max
        q[r, c, action] += step * (target - q[r, c, action])

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
        """Load Q-table from a numpy file. Missing path is a no-op (graceful)."""
        if not Path(path).exists():
            return
        self.q_table = np.load(path)


class DecayingAlphaAgent(BaseAgent):
    """``BaseAgent`` + geometric α decay. Shared base for Q-Learning + Double-Q.

    Input/Output: inherits the ``BaseAgent`` contract. Adds ``self.alpha``
        (float, mutable) as per-episode state — read by subclass ``update``
        bodies and decayed by ``decay_epsilon`` on every episode boundary.
    Setup: subclasses must call :meth:`_init_decay` *after* their
        ``super().__init__(config)`` line, passing the algorithm-specific
        triple ``(alpha_start, alpha_end, alpha_decay)`` from their own
        config sub-block (``config.q_learning`` or ``config.double_q``).
        Decay protocol: ``α ← max(alpha_end, α · alpha_decay)`` per episode.
    """

    def _init_decay(self, alpha_start: float, alpha_end: float, alpha_decay: float) -> None:
        """Bind the per-algorithm α-decay schedule onto ``self``."""
        self.alpha = alpha_start
        self.alpha_end = alpha_end
        self.alpha_decay = alpha_decay

    def decay_alpha(self) -> None:
        """Geometric decay of α each episode, clamped to ``alpha_end``."""
        self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)

    def decay_epsilon(self) -> None:
        """Decay ε (via ``BaseAgent``) and α together per episode."""
        super().decay_epsilon()
        self.decay_alpha()
