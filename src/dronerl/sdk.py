"""Central SDK for DroneRL - ties all components together."""

from pathlib import Path

import numpy as np

from dronerl.agent_factory import create_agent
from dronerl.algorithms import ALGORITHMS
from dronerl.comparison import ComparisonStore, generate_comparison_chart
from dronerl.config_loader import Config, assert_in_project, load_config, package_relative
from dronerl.environment import CellType, Environment
from dronerl.hazard_generator import HazardGenerator
from dronerl.logger import setup_logger
from dronerl.trainer import Trainer


class DroneRLSDK:
    """High-level orchestration entry point — composes config, env, agent, trainer.

    Input:  ``config_path: str`` (default ``"config/config.yaml"``) at construction
            *or* keyword-only ``config: Config`` to share a pre-loaded instance
            (the GUI path — skips a YAML re-read so SDK + GUI see the same Config
            object). Post-construction methods: ``train_step()``,
            ``train_batch(n)``, ``reset()``, ``switch_algorithm(name)``,
            ``run_comparison(episodes)``, ``save_brain(path)`` /
            ``load_brain(path)``, ``set_dynamic_params(...)``.
    Output: ``train_step()`` returns ``{"reward": float, "steps": int,
            "reached_goal": bool}``; ``train_batch(n)`` returns a list of those
            dicts. ``run_comparison()`` returns ``{algo_name: reward_history}``
            and populates ``self.comparison`` with steps history too.
            ``generate_chart()`` writes a PNG to ``results/comparison/`` and
            returns its path. ``load_brain`` is a no-op on a missing file.
    Setup:  YAML at ``config_path`` — must contain the full schema validated by
            ``config_loader._validate_version`` (algorithm choice, hyperparameters,
            board dimensions, reward magnitudes, ``analysis.max_parallel_workers``).
    """

    def __init__(self, config_path: str | None = None, *, config: Config | None = None):
        """Construct from a YAML path *or* a pre-loaded ``Config`` (GUI uses the latter so SDK + GUI share one ``Config``); ``None`` resolves to the package-relative default (§14.3)."""
        self.config = config if config is not None else Config(load_config(config_path) if config_path else load_config())
        self.logger = setup_logger("DroneRL", self.config.logging.level)
        self.agent = create_agent(self.config)
        self.environment = Environment(self.config)
        self.hazards = HazardGenerator(self.config)
        self.trainer = self._new_trainer()
        self.comparison = ComparisonStore()
        self.logger.info("DroneRL SDK initialized (algorithm=%s)", self.config.algorithm.name)

    def _new_trainer(self) -> Trainer:
        """Create a trainer wired to optional per-episode board randomization."""
        trainer = Trainer(self.agent, self.environment, self.config)
        if getattr(self.config.dynamic_board, "randomize_per_episode", False):
            trainer.on_episode_start = self.regenerate_hazards
        return trainer

    def train_step(self) -> dict:
        """Run one training episode and return metrics."""
        reward, steps, goal = self.trainer.run_episode()
        return {"reward": reward, "steps": steps, "reached_goal": goal}

    def train_batch(self, n: int) -> list[dict]:
        """Run n training episodes and return list of per-episode results."""
        return [self.train_step() for _ in range(n)]

    def reset(self) -> None:
        """Reset agent + environment + trainer; preserve hazard-generator slider state across resets."""
        self.agent = create_agent(self.config)
        self.environment = Environment(self.config)
        self.trainer = self._new_trainer()
        self.logger.info("SDK reset complete")

    def switch_algorithm(self, name: str) -> None:
        """Swap algorithms and reset training state while preserving the board."""
        self.config.algorithm.name = name
        self.agent = create_agent(self.config)
        self.trainer = self._new_trainer()
        self.logger.info("Switched algorithm to %s", name)

    def run_comparison(self, episodes: int | None = None) -> dict[str, list[float]]:
        """Train each algorithm for `episodes` on the SAME board; return histories."""
        n = episodes or self.config.comparison.max_episodes
        original = self.config.algorithm.name
        # Snapshot the current board so all algorithms train on identical hazards
        shared_grid = self.environment.grid.copy()
        shared_editor = self.environment.editor_cells
        shared_drift = self.environment.drift_probability
        self.comparison.clear()
        for algo in ALGORITHMS:
            self.switch_algorithm(algo)
            self.environment.grid[:] = shared_grid
            self.environment.restore_editor_cells(shared_editor)
            self.environment.drift_probability = shared_drift
            self.train_batch(n)
            self.comparison.add_run(algo, self.trainer.reward_history, self.trainer.steps_history)
        self.switch_algorithm(original)
        self.environment.grid[:] = shared_grid
        self.environment.restore_editor_cells(shared_editor)
        self.environment.drift_probability = shared_drift
        return dict(self.comparison.runs)

    def generate_chart(self, output_path: str | None = None, title: str = "") -> str:
        """Generate the comparison chart; relative paths anchor to project root (§14.3)."""
        out = package_relative(output_path or str(Path(self.config.comparison.output_dir) / "comparison.png"))
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
        """Return the agent's current Q-table (combined QA+QB for Double-Q)."""
        return self.agent.q_table

    def get_grid(self) -> np.ndarray:
        """Return the environment's current cell-type grid."""
        return self.environment.grid

    def get_metrics(self) -> dict:
        """Return a dict of training metrics (episode count, goal rate, reward stats)."""
        return self.trainer.get_metrics()

    def save_brain(self, path: str) -> None:
        """Persist the agent's Q-table(s) to disk; refuses paths escaping project root (§13 / Pass-7)."""
        self.agent.save(assert_in_project(path))
        self.logger.info("Q-table saved to %s", path)

    def load_brain(self, path: str) -> None:
        """Restore Q-table(s) from a saved file; refuses paths escaping project root (§13 / Pass-7)."""
        self.agent.load(assert_in_project(path))
        self.logger.info("Q-table loaded from %s", path)

    def set_cell(self, row: int, col: int, cell_type: CellType, *, editor: bool = False) -> None:
        """Place ``cell_type`` at ``(row, col)``; ``editor=True`` marks it as user-placed (survives hazard regen)."""
        self.environment.set_cell(row, col, cell_type, editor=editor)

    @property
    def episode_count(self) -> int:
        """Number of completed training episodes."""
        return self.trainer.episode_count

    @property
    def epsilon(self) -> float:
        """Current exploration rate (decays over training)."""
        return self.agent.epsilon

    @property
    def drone_position(self):
        """Current ``(row, col)`` position of the drone in the environment."""
        return self.environment.drone_pos

    @property
    def goal_rate(self) -> float:
        """Fraction of recent episodes that reached the goal (0.0–1.0)."""
        return self.trainer.goal_rate

    @property
    def reward_history(self) -> list[float]:
        """Total reward per episode for every completed episode."""
        return self.trainer.reward_history
