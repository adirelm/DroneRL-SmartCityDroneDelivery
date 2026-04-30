"""Q-Learning agent with decaying alpha (learning rate)."""

from dronerl.base_agent import DecayingAlphaAgent
from dronerl.config_loader import Config


class QLearningAgent(DecayingAlphaAgent):
    """Q-Learning agent where α decays per episode for stable convergence under noise.

    Input/Output: inherits the ``BaseAgent`` contract via ``DecayingAlphaAgent``.
    Setup: adds ``config.q_learning.alpha_start`` (initial α),
        ``config.q_learning.alpha_end`` (floor), ``config.q_learning.alpha_decay``
        (geometric decay applied each ``decay_epsilon`` call —
        ``α ← max(alpha_end, α · alpha_decay)``).
    """

    algorithm_name = "Q-Learning"

    def __init__(self, config: Config):
        super().__init__(config)
        q_cfg = config.q_learning
        self._init_decay(q_cfg.alpha_start, q_cfg.alpha_end, q_cfg.alpha_decay)

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
