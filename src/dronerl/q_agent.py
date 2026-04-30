"""Q-Learning agent with decaying alpha (learning rate)."""

from dronerl.base_agent import BaseAgent
from dronerl.config_loader import Config


class QLearningAgent(BaseAgent):
    """Q-Learning agent where α decays per episode for stable convergence under noise.

    Input/Output: inherits the ``BaseAgent`` contract.
    Setup: adds ``config.q_learning.alpha_start`` (initial α),
        ``config.q_learning.alpha_end`` (floor), ``config.q_learning.alpha_decay``
        (geometric decay applied each ``decay_epsilon`` call —
        ``α ← max(alpha_end, α · alpha_decay)``).
    """

    algorithm_name = "Q-Learning"

    def __init__(self, config: Config):
        super().__init__(config)
        q_cfg = config.q_learning
        self.alpha = q_cfg.alpha_start
        self.alpha_end = q_cfg.alpha_end
        self.alpha_decay = q_cfg.alpha_decay

    def update(
        self,
        state: tuple[int, int],
        action: int,
        reward: float,
        next_state: tuple[int, int],
        done: bool,
    ) -> None:
        """Update Q-value using decaying alpha."""
        current_q = self.q_table[state[0], state[1], action]
        next_max_q = 0.0 if done else self.get_max_q(next_state)
        target = reward + self.gamma * next_max_q
        self.q_table[state[0], state[1], action] += self.alpha * (target - current_q)

    def decay_alpha(self) -> None:
        """Decay alpha by the decay rate, clamped to alpha_end."""
        self.alpha = max(self.alpha_end, self.alpha * self.alpha_decay)

    def decay_epsilon(self) -> None:
        """Decay both epsilon and alpha per episode."""
        super().decay_epsilon()
        self.decay_alpha()
