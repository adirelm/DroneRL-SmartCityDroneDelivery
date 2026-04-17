"""Central SDK for DroneRL - ties all components together."""

from pathlib import Path

import numpy as np

from src.agent_factory import create_agent
from src.comparison import ComparisonStore, generate_comparison_chart
from src.config_loader import Config, load_config
from src.environment import CellType, Environment
from src.hazard_generator import HazardGenerator
from src.logger import setup_logger
from src.trainer import Trainer


class DroneRLSDK:
    """High-level interface for the DroneRL system."""

    def __init__(self, config_path: str = "config/config.yaml"):
        raw_config = load_config(config_path)
        self.config = Config(raw_config)
        self.logger = setup_logger("DroneRL", self.config.logging.level)
        self.agent = create_agent(self.config)
        self.environment = Environment(self.config)
        self.trainer = Trainer(self.agent, self.environment, self.config)
        self.hazards = HazardGenerator(self.config)
        self.comparison = ComparisonStore()
        self.logger.info("DroneRL SDK initialized (algorithm=%s)", self.config.algorithm.name)

    def train_step(self) -> dict:
        """Run one training episode and return metrics."""
        reward, steps, goal = self.trainer.run_episode()
        return {"reward": reward, "steps": steps, "reached_goal": goal}

    def train_batch(self, n: int) -> list[dict]:
        """Run n training episodes and return list of per-episode results."""
        return [self.train_step() for _ in range(n)]

    def reset(self) -> None:
        """Reset agent, environment, and trainer to initial state."""
        self.agent = create_agent(self.config)
        self.environment = Environment(self.config)
        self.trainer = Trainer(self.agent, self.environment, self.config)
        self.logger.info("SDK reset complete")

    def switch_algorithm(self, name: str) -> None:
        """Swap to a different algorithm and reset training state."""
        self.config.algorithm.name = name
        self.reset()
        self.logger.info("Switched algorithm to %s", name)

    def run_comparison(self, episodes: int | None = None) -> dict[str, list[float]]:
        """Train each algorithm for `episodes` on the SAME board; return histories."""
        n = episodes or self.config.comparison.max_episodes
        original = self.config.algorithm.name
        # Snapshot the current board so all algorithms train on identical hazards
        shared_grid = self.environment.grid.copy()
        shared_drift = self.environment.drift_probability
        self.comparison.clear()
        for algo in ("bellman", "q_learning", "double_q"):
            self.switch_algorithm(algo)
            self.environment.grid[:] = shared_grid
            self.environment.drift_probability = shared_drift
            self.train_batch(n)
            self.comparison.add_run(algo, self.trainer.reward_history)
        self.switch_algorithm(original)
        self.environment.grid[:] = shared_grid
        self.environment.drift_probability = shared_drift
        return dict(self.comparison.runs)

    def generate_chart(self, output_path: str | None = None, title: str = "") -> str:
        """Generate the comparison chart from currently stored runs."""
        out = output_path or str(Path(self.config.comparison.output_dir) / "comparison.png")
        return generate_comparison_chart(
            self.comparison, out,
            title=title or "DroneRL Algorithm Convergence",
            smoothing_window=self.config.comparison.smoothing_window,
        )

    def regenerate_hazards(self) -> int:
        """Re-run the hazard generator on the current environment."""
        placed = self.hazards.apply(self.environment)
        self.environment.set_wind_drift(self.hazards.effective_drift())
        return placed

    def randomize_board(self) -> int:
        """Alias for regenerate_hazards — re-randomises the dynamic board."""
        return self.regenerate_hazards()

    def set_dynamic_params(self, noise: float, density: float, difficulty: float) -> None:
        """Update the hazard generator sliders in one call."""
        self.hazards.set_noise(noise)
        self.hazards.set_density(density)
        self.hazards.set_difficulty(difficulty)
        self.environment.set_wind_drift(self.hazards.effective_drift())

    def get_q_table(self) -> np.ndarray:
        return self.agent.q_table

    def get_grid(self) -> np.ndarray:
        return self.environment.grid

    def get_metrics(self) -> dict:
        return self.trainer.get_metrics()

    def save_brain(self, path: str) -> None:
        self.agent.save(path)
        self.logger.info("Q-table saved to %s", path)

    def load_brain(self, path: str) -> None:
        self.agent.load(path)
        self.logger.info("Q-table loaded from %s", path)

    def set_cell(self, row: int, col: int, cell_type: CellType) -> None:
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
