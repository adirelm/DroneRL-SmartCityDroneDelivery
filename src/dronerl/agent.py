"""Bellman-equation agent with constant learning rate (Assignment 1 baseline)."""

from dronerl.base_agent import BaseAgent
from dronerl.config_loader import Config


class BellmanAgent(BaseAgent):
    """Tabular Q-Learning agent with the Bellman update at a *constant* learning rate.

    Input/Output: inherits the ``BaseAgent`` contract.
    Setup: adds ``config.agent.learning_rate`` (the constant α used for every update).
    """

    algorithm_name = "Bellman"

    def __init__(self, config: Config):
        super().__init__(config)
        self.lr = config.agent.learning_rate

    def update(
        self,
        state: tuple[int, int],
        action: int,
        reward: float,
        next_state: tuple[int, int],
        done: bool,
    ) -> None:
        """Update Q-value using the Bellman equation with constant lr."""
        self._td_update(self.q_table, state, action, reward, next_state, done, self.lr)


# Backward compatibility alias
Agent = BellmanAgent
