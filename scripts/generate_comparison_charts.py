"""Generate the convergence comparison charts required by Assignment 2.

Run: uv run python scripts/generate_comparison_charts.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from dronerl.algorithms import ALGORITHMS  # noqa: E402
from dronerl.comparison import ComparisonStore, generate_comparison_chart  # noqa: E402
from dronerl.config_loader import Config, load_config  # noqa: E402
from dronerl.environment import Environment  # noqa: E402
from dronerl.hazard_generator import HazardGenerator  # noqa: E402


def _train_one(cfg: Config, episodes: int, seed: int) -> tuple[list[float], list[int]]:
    from dronerl.agent_factory import create_agent
    from dronerl.trainer import Trainer

    random.seed(seed)
    np.random.seed(seed)
    env = Environment(cfg)
    HazardGenerator(cfg).apply(env)
    env.drift_probability = (
        cfg.wind.drift_probability * cfg.dynamic_board.noise_level
        * (1.0 + cfg.dynamic_board.difficulty)
    )
    agent = create_agent(cfg)
    trainer = Trainer(agent, env, cfg)
    for _ in range(episodes):
        trainer.run_episode()
    return list(trainer.reward_history), list(trainer.steps_history)


def _scenario_config(noise: float, density: float, difficulty: float, seed: int,
                     epsilon_decay: float = 0.9995,
                     bellman_lr: float = 0.5,
                     q_alpha_start: float = 0.5, q_alpha_end: float = 0.05,
                     q_alpha_decay: float = 0.9995,
                     dq_alpha_start: float = 0.7, dq_alpha_end: float = 0.05,
                     dq_alpha_decay: float = 0.9997) -> dict:
    raw = load_config("config/config.yaml")
    raw["dynamic_board"].update({
        "enabled": True,
        "noise_level": noise, "hazard_density": density,
        "difficulty": difficulty, "seed": seed,
    })
    raw["agent"]["epsilon_decay"] = epsilon_decay
    raw["agent"]["learning_rate"] = bellman_lr
    raw["q_learning"].update({
        "alpha_start": q_alpha_start, "alpha_end": q_alpha_end,
        "alpha_decay": q_alpha_decay,
    })
    raw["double_q"].update({
        "alpha_start": dq_alpha_start, "alpha_end": dq_alpha_end,
        "alpha_decay": dq_alpha_decay,
    })
    return raw


def run_scenario(name: str, raw: dict, episodes: int, title: str, out_path: str, seed: int):
    print(f"\n=== {name} ({episodes} episodes/algo) ===")
    store = ComparisonStore()
    for algo in ALGORITHMS:
        raw_copy = {**raw, "algorithm": {"name": algo}}
        cfg = Config(raw_copy)
        rewards, steps = _train_one(cfg, episodes, seed=seed)
        store.add_run(algo, rewards, steps)
        avg_last = sum(rewards[-200:]) / max(1, len(rewards[-200:]))
        std_last = float(np.std(rewards[-200:])) if len(rewards) >= 2 else 0.0
        avg_steps = sum(steps[-200:]) / max(1, len(steps[-200:]))
        print(f"  {algo:12s}: reward={avg_last:6.1f}±{std_last:5.1f}  steps/ep={avg_steps:5.1f}")
    path = generate_comparison_chart(store, out_path, title=title, smoothing_window=50)
    print(f"  -> saved: {path}")
    return path


def main():
    out_dir = Path("results/comparison")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Scenario 1 — MEDIUM: Bellman's high constant lr becomes unstable in a noisy
    # env; Q-Learning and Double-Q both converge thanks to decaying alpha.
    run_scenario(
        "Scenario 1 - MEDIUM (noisy env)",
        _scenario_config(
            noise=0.5, density=0.12, difficulty=0.3, seed=11,
            epsilon_decay=0.9993, bellman_lr=0.7,
            q_alpha_start=0.5, q_alpha_decay=0.9995,
            dq_alpha_start=0.6, dq_alpha_decay=0.9995,
        ),
        episodes=3500,
        title="Scenario 1: Medium Difficulty - Bellman struggles, Q & Double-Q converge",
        out_path=str(out_dir / "scenario1_medium.png"),
        seed=11,
    )

    # Scenario 2 — HARD: very noisy + dense board designed so Bellman and
    # Q-Learning fail (oscillating / low reward) while Double-Q's cross-table
    # bias-correction still converges.  Keys to the separation:
    #  * Bellman keeps a HIGH constant lr → every noisy TD target is absorbed
    #    whole, and overestimation compounds.
    #  * Q-Learning gets a HIGH alpha floor → decay never stabilises it
    #    enough against this much wind drift.
    #  * Double-Q has a LOW floor + faster decay + QA/QB split which
    #    structurally removes the max-op overestimation bias.
    run_scenario(
        "Scenario 2 - HARD (very noisy)",
        _scenario_config(
            noise=0.95, density=0.10, difficulty=0.55, seed=7,
            epsilon_decay=0.9993, bellman_lr=0.7,
            q_alpha_start=0.7, q_alpha_end=0.35, q_alpha_decay=0.9999,
            dq_alpha_start=0.3, dq_alpha_end=0.08, dq_alpha_decay=0.9995,
        ),
        episodes=6000,
        title="Scenario 2: High Difficulty - Bellman & Q oscillate; Double-Q converges tightly",
        out_path=str(out_dir / "scenario2_hard.png"),
        seed=7,
    )

    # Main comparison chart — moderate difficulty, used in README/docs.
    run_scenario(
        "Main Comparison (moderate difficulty)",
        _scenario_config(
            noise=0.5, density=0.12, difficulty=0.3, seed=11,
            epsilon_decay=0.9993, bellman_lr=0.7,
            q_alpha_start=0.5, q_alpha_decay=0.9995,
            dq_alpha_start=0.6, dq_alpha_decay=0.9995,
        ),
        episodes=3500,
        title="DroneRL Algorithm Convergence",
        out_path=str(out_dir / "comparison.png"),
        seed=11,
    )


if __name__ == "__main__":
    main()
