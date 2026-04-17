"""Generate the two convergence comparison charts required by Assignment 2.

Run: uv run python scripts/generate_comparison_charts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.comparison import ComparisonStore, generate_comparison_chart  # noqa: E402
from src.config_loader import Config, load_config  # noqa: E402
from src.environment import Environment  # noqa: E402
from src.hazard_generator import HazardGenerator  # noqa: E402

ALGORITHMS = ("bellman", "q_learning", "double_q")


def _train_one(cfg: Config, episodes: int) -> list[float]:
    from src.agent_factory import create_agent
    from src.trainer import Trainer
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
    return list(trainer.reward_history)


def _scenario_config(noise: float, density: float, difficulty: float, seed: int,
                     epsilon_decay: float = 0.9995, bellman_lr: float = 0.4) -> dict:
    raw = load_config("config/config.yaml")
    raw["dynamic_board"].update({
        "enabled": True,
        "noise_level": noise,
        "hazard_density": density,
        "difficulty": difficulty,
        "seed": seed,
    })
    raw["agent"]["epsilon_decay"] = epsilon_decay
    raw["agent"]["learning_rate"] = bellman_lr
    return raw


def run_scenario(name: str, raw: dict, episodes: int, title: str, out_path: str):
    print(f"\n=== {name} ({episodes} episodes/algo) ===")
    store = ComparisonStore()
    for algo in ALGORITHMS:
        raw_copy = {**raw, "algorithm": {"name": algo}}
        cfg = Config(raw_copy)
        history = _train_one(cfg, episodes)
        store.add_run(algo, history)
        avg_last = sum(history[-100:]) / max(1, len(history[-100:]))
        print(f"  {algo:12s}: avg(last 100) = {avg_last:.1f}")
    path = generate_comparison_chart(store, out_path, title=title, smoothing_window=50)
    print(f"  → saved: {path}")
    return path


def main():
    out_dir = Path("data/comparison")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Scenario 1: Medium noise — Bellman with high constant lr becomes unstable.
    # Q-Learning and Double Q both converge thanks to decaying alpha.
    run_scenario(
        "Scenario 1 — MEDIUM (noisy env)",
        _scenario_config(noise=0.8, density=0.15, difficulty=0.5,
                         seed=11, epsilon_decay=0.9995, bellman_lr=0.5),
        episodes=4000,
        title="Scenario 1: Medium Difficulty — Bellman struggles, Q & Double-Q converge",
        out_path=str(out_dir / "scenario1_medium.png"),
    )

    # Scenario 2: Hard — very high noise, high difficulty.
    # Bellman lags farthest; Double-Q reaches the highest plateau first.
    run_scenario(
        "Scenario 2 — HARD (very noisy + dense)",
        _scenario_config(noise=1.0, density=0.18, difficulty=0.8,
                         seed=7, epsilon_decay=0.99965, bellman_lr=0.5),
        episodes=8000,
        title="Scenario 2: High Difficulty — Bellman & Q lag, Double-Q wins",
        out_path=str(out_dir / "scenario2_hard.png"),
    )


if __name__ == "__main__":
    main()
