"""Bellman-equation agent with constant learning rate (Assignment 1 baseline)."""

from src.base_agent import BaseAgent
from src.config_loader import Config


class BellmanAgent(BaseAgent):
    """Tabular Q-Learning agent using Bellman update with constant learning rate."""

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
        current_q = self.q_table[state[0], state[1], action]
        next_max_q = 0.0 if done else self.get_max_q(next_state)
        target = reward + self.gamma * next_max_q
        self.q_table[state[0], state[1], action] += self.lr * (target - current_q)


# Backward compatibility alias
Agent = BellmanAgent
