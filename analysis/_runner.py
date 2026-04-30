"""Shared training helpers for the analysis experiments.

Kept deliberately minimal: a single `train_run` that trains one algorithm
on one (config, seed) and returns reward + steps histories. The analysis
scripts compose this into multi-seed sweeps and parameter sweeps.
"""

from __future__ import annotations

import logging
import multiprocessing as mp
import os
import random
from copy import deepcopy

import numpy as np

from dronerl.agent_factory import create_agent
from dronerl.algorithms import ALGORITHMS  # noqa: F401
from dronerl.config_loader import Config, load_config
from dronerl.environment import Environment
from dronerl.hazard_generator import HazardGenerator
from dronerl.trainer import Trainer

_log = logging.getLogger(__name__)

CellArgs = tuple[dict, str, int, int, dict]
CellResult = tuple[str, int, list[float], list[int]]


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


def _train_cell(args: CellArgs) -> CellResult:
    """Worker: train one (algorithm, seed) cell. Top-level so it pickles."""
    raw, algo, seed, episodes, board = args
    cfg = with_overrides(raw, algorithm=algo, seed=seed, **board)
    rewards, steps = train_run(cfg, episodes, seed=seed)
    return algo, seed, rewards, steps


def _config_max_workers() -> int:
    """Read ``analysis.max_parallel_workers`` from config; fall back to cpu_count.

    Keeps the rate-limit policy in ``config/config.yaml`` per §5.2 instead of
    silently using ``os.cpu_count()`` as the implicit ceiling. The fallback
    branches log a warning so a stripped-config deploy doesn't silently abandon
    the configured limit.
    """
    cpu_default = os.cpu_count() or 1
    try:
        raw = load_config()
        val = raw.get("analysis", {}).get("max_parallel_workers")
        if val is None:
            _log.warning("analysis.max_parallel_workers absent from config; using cpu_count=%d", cpu_default)
            return cpu_default
        return int(val)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        _log.warning("config unreachable for max_parallel_workers (%s); using cpu_count=%d", exc, cpu_default)
        return cpu_default


def resolve_workers(requested: int | None = None) -> int:
    """Resolve worker count from arg, ``DRONERL_PARALLEL`` env, or default 1.

    Returns 1 (serial) unless explicitly opted in. The hard ceiling is
    ``min(config.analysis.max_parallel_workers, os.cpu_count())`` — the config
    value lets §5.2 hold (rate limit lives in config, not hard-coded).
    """
    n = requested if requested is not None else int(os.environ.get("DRONERL_PARALLEL", "1") or "1")
    ceiling = min(_config_max_workers(), os.cpu_count() or 1)
    return max(1, min(n, ceiling))


def train_cells(cells: list[CellArgs], n_workers: int = 1) -> list[CellResult]:
    """Train a batch of cells, optionally in parallel via ``multiprocessing.Pool``.

    Determinism: each cell is seeded inside the worker via :func:`train_run`'s
    ``random.seed(seed)`` / ``np.random.seed(seed)`` calls, so results are
    independent of worker scheduling order.
    """
    if n_workers <= 1:
        return [_train_cell(c) for c in cells]
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=n_workers) as pool:
        return list(pool.imap_unordered(_train_cell, cells))
