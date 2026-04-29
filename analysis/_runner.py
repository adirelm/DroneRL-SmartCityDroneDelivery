"""Shared training helpers for the analysis experiments.

Kept deliberately minimal: a single `train_run` that trains one algorithm
on one (config, seed) and returns reward + steps histories. The analysis
scripts compose this into multi-seed sweeps and parameter sweeps.
"""

from __future__ import annotations

import random
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dronerl.agent_factory import create_agent  # noqa: E402
from dronerl.algorithms import ALGORITHMS  # noqa: E402, F401
from dronerl.config_loader import Config, load_config  # noqa: E402
from dronerl.environment import Environment  # noqa: E402
from dronerl.hazard_generator import HazardGenerator  # noqa: E402
from dronerl.trainer import Trainer  # noqa: E402


def base_raw_config() -> dict:
    """Load and return a mutable copy of config/config.yaml."""
    return deepcopy(load_config("config/config.yaml"))


def with_overrides(raw: dict, *, algorithm: str, **board_overrides) -> Config:
    """Return a Config with the given algorithm and dynamic-board overrides."""
    raw = deepcopy(raw)
    raw["algorithm"] = {"name": algorithm}
    raw["dynamic_board"].update(board_overrides)
    return Config(raw)


def train_run(cfg: Config, episodes: int, seed: int) -> tuple[list[float], list[int]]:
    """Train one algorithm for `episodes` and return (reward_history, steps_history)."""
    random.seed(seed)
    np.random.seed(seed)
    env = Environment(cfg)
    HazardGenerator(cfg).apply(env)
    env.drift_probability = (
        cfg.wind.drift_probability
        * cfg.dynamic_board.noise_level
        * (1.0 + cfg.dynamic_board.difficulty)
    )
    agent = create_agent(cfg)
    trainer = Trainer(agent, env, cfg)
    for _ in range(episodes):
        trainer.run_episode()
    return list(trainer.reward_history), list(trainer.steps_history)


def last_window_stats(history: list[float], window: int = 200) -> tuple[float, float]:
    """Return (mean, std) over the last `window` entries; safe on short histories."""
    if not history:
        return 0.0, 0.0
    tail = np.asarray(history[-window:], dtype=float)
    return float(tail.mean()), float(tail.std())
