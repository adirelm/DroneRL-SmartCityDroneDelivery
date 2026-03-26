"""Central SDK for DroneRL - ties all components together."""


import numpy as np

from src.agent import Agent
from src.config_loader import Config, load_config
from src.environment import CellType, Environment
from src.logger import setup_logger
from src.trainer import Trainer


class DroneRLSDK:
    """High-level interface for the DroneRL system."""

    def __init__(self, config_path: str = "config/config.yaml"):
        raw_config = load_config(config_path)
        self.config = Config(raw_config)
        self.logger = setup_logger("DroneRL", self.config.logging.level)

        self.agent = Agent(self.config)
        self.environment = Environment(self.config)
        self.trainer = Trainer(self.agent, self.environment, self.config)

        self.logger.info("DroneRL SDK initialized")

    def train_step(self) -> dict:
        """Run one training episode and return metrics."""
        reward, steps, goal = self.trainer.run_episode()
        return {"reward": reward, "steps": steps, "reached_goal": goal}

    def train_batch(self, n: int) -> list[dict]:
        """Run n training episodes and return list of per-episode results."""
        results = []
        for _ in range(n):
            results.append(self.train_step())
        return results

    def reset(self) -> None:
        """Reset agent, environment, and trainer to initial state."""
        self.agent = Agent(self.config)
        self.environment = Environment(self.config)
        self.trainer = Trainer(self.agent, self.environment, self.config)
        self.logger.info("SDK reset complete")

    def get_q_table(self) -> np.ndarray:
        """Return the current Q-table."""
        return self.agent.q_table

    def get_grid(self) -> np.ndarray:
        """Return the current environment grid."""
        return self.environment.grid

    def get_metrics(self) -> dict:
        """Return current training metrics."""
        return self.trainer.get_metrics()

    def save_brain(self, path: str) -> None:
        """Save the agent's Q-table to file."""
        self.agent.save(path)
        self.logger.info(f"Q-table saved to {path}")

    def load_brain(self, path: str) -> None:
        """Load a Q-table from file."""
        self.agent.load(path)
        self.logger.info(f"Q-table loaded from {path}")

    def set_cell(self, row: int, col: int, cell_type: CellType) -> None:
        """Modify a cell in the environment grid."""
        self.environment.set_cell(row, col, cell_type)

    @property
    def episode_count(self) -> int:
        return self.trainer.episode_count

    @property
    def epsilon(self) -> float:
        return self.agent.epsilon

    @property
    def drone_position(self):
        return self.environment.drone_pos

    @property
    def goal_rate(self) -> float:
        return self.trainer.goal_rate

    @property
    def reward_history(self) -> list[float]:
        return self.trainer.reward_history
