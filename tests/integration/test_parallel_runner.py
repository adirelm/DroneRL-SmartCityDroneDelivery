"""Integration test: parallel `train_cells` matches serial bit-for-bit.

The §15 audit added `multiprocessing.Pool` parallelism to the analysis
sweeps. Determinism is the load-bearing claim: each worker reseeds via
`train_run`, so output must be independent of process scheduling.
This test proves that.
"""

from __future__ import annotations

import os

import pytest

from analysis._runner import base_raw_config, resolve_workers, train_cells

EPISODES = 50  # tiny — keeps the test under a second
ALGOS = ("bellman", "q_learning")  # 2 algos × 2 seeds = 4 cells, fits on any CPU
SEEDS = (3, 11)


def _cells() -> list:
    raw = base_raw_config()
    raw["dynamic_board"]["enabled"] = True
    board = {"noise_level": 0.5, "hazard_density": 0.1, "difficulty": 0.3}
    return [(raw, algo, seed, EPISODES, board) for algo in ALGOS for seed in SEEDS]


def test_serial_run_produces_per_cell_results():
    results = train_cells(_cells(), n_workers=1)
    assert len(results) == len(ALGOS) * len(SEEDS)
    for algo, seed, rewards, steps in results:
        assert algo in ALGOS
        assert seed in SEEDS
        assert len(rewards) == EPISODES
        assert len(steps) == EPISODES


@pytest.mark.skipif(
    (os.cpu_count() or 1) < 2, reason="needs ≥2 CPU cores for a parallel run"
)
def test_parallel_matches_serial():
    serial = {(algo, seed): (rewards, steps)
              for algo, seed, rewards, steps in train_cells(_cells(), n_workers=1)}
    parallel = {(algo, seed): (rewards, steps)
                for algo, seed, rewards, steps in train_cells(_cells(), n_workers=2)}
    assert serial.keys() == parallel.keys()
    for key in serial:
        s_rewards, s_steps = serial[key]
        p_rewards, p_steps = parallel[key]
        assert s_rewards == p_rewards, f"reward mismatch for {key}"
        assert s_steps == p_steps, f"steps mismatch for {key}"


def test_resolve_workers_clamps_and_defaults(monkeypatch):
    monkeypatch.delenv("DRONERL_PARALLEL", raising=False)
    assert resolve_workers() == 1                 # default = serial
    assert resolve_workers(0) == 1                # clamps to ≥ 1
    assert resolve_workers(2) == min(2, os.cpu_count() or 1)
    monkeypatch.setenv("DRONERL_PARALLEL", "3")
    assert resolve_workers() == min(3, os.cpu_count() or 1)
