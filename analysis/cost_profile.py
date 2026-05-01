"""Cost-profiling experiment.

Measures wall-clock time, peak memory, and Q-table footprint for each
registered algorithm at a fixed episode count, then projects how the cost
behaves as grid size and episode count scale.

Run: uv run python -m analysis.cost_profile
"""

from __future__ import annotations

import json
import time
import tracemalloc
from pathlib import Path

import numpy as np

from analysis._runner import base_raw_config, train_run, with_overrides
from dronerl.algorithms import ALGORITHM_REGISTRY, ALGORITHMS

EPISODES = 1500
SEED = 11
NOISE = 0.5
DENSITY = 0.12
DIFFICULTY = 0.3


def _q_table_bytes(rows: int, cols: int, actions: int = 4, tables: int = 1) -> int:
    """Memory in bytes for `tables` float64 Q-tables of shape (rows, cols, actions)."""
    return rows * cols * actions * tables * np.dtype(np.float64).itemsize


def _profile_one(algorithm: str) -> dict:
    """Profile one algorithm: wall-time, peak-heap, Q-table footprint, last-200 stats."""
    raw = base_raw_config()
    raw["dynamic_board"]["enabled"] = True
    raw["agent"]["learning_rate"] = 0.7
    raw["q_learning"].update({"alpha_start": 0.5, "alpha_decay": 0.9995})
    raw["double_q"].update({"alpha_start": 0.6, "alpha_decay": 0.9995})
    cfg = with_overrides(
        raw, algorithm=algorithm,
        noise_level=NOISE, hazard_density=DENSITY,
        difficulty=DIFFICULTY, seed=SEED,
    )
    tracemalloc.start()
    t0 = time.perf_counter()
    rewards, steps = train_run(cfg, EPISODES, seed=SEED)
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    tables = 2 if algorithm == "double_q" else 1
    qbytes = _q_table_bytes(cfg.environment.grid_rows, cfg.environment.grid_cols, tables=tables)
    return {
        "algorithm": algorithm,
        "episodes": EPISODES,
        "elapsed_s": round(elapsed, 3),
        "episodes_per_s": round(EPISODES / elapsed, 1),
        "us_per_episode": round(elapsed / EPISODES * 1e6, 1),
        "peak_traced_kb": round(peak / 1024, 1),
        "q_table_bytes": qbytes,
        "tables": tables,
        "final_mean_200": round(float(np.mean(rewards[-200:])), 1),
        "final_std_200": round(float(np.std(rewards[-200:])), 1),
        "avg_steps_200": round(float(np.mean(steps[-200:])), 1),
    }


def _scaling_projection(per_episode_us: dict[str, float]) -> dict[str, dict]:
    """Project total cost for typical workloads using measured per-episode timings."""
    workloads = {
        "Single 1500-ep run (development)": 1500,
        "Scenario 1 in repo (3500 ep × 3 algos)": 3500 * 3,
        "Scenario 2 in repo (6000 ep × 3 algos)": 6000 * 3,
        "Multi-seed sweep (5 seeds × 1500 ep × 3 algos)": 5 * 1500 * 3,
        "Alpha-decay sweep (6 decays × 3 seeds × 1500 ep × 2 algos)": 6 * 3 * 1500 * 2,
    }
    avg_us = sum(per_episode_us.values()) / len(per_episode_us)
    out = {}
    for label, episodes in workloads.items():
        seconds = episodes * avg_us / 1e6
        out[label] = {
            "episodes": episodes,
            "estimated_seconds": round(seconds, 1),
            "estimated_minutes": round(seconds / 60, 2),
        }
    return out


def main() -> None:
    print(f"\n=== Cost profile ({EPISODES} ep × {len(ALGORITHMS)} algos, seed={SEED}) ===\n")
    profiles = []
    for spec in ALGORITHM_REGISTRY:
        info = _profile_one(spec.name)
        profiles.append(info)
        print(f"  {spec.name:12s}  {info['elapsed_s']:6.3f}s  "
              f"{info['episodes_per_s']:6.1f} ep/s  "
              f"{info['us_per_episode']:6.1f} µs/ep  "
              f"peak={info['peak_traced_kb']:7.1f} KB  "
              f"Qtable={info['q_table_bytes']:5d}B")

    projections = _scaling_projection({p["algorithm"]: p["us_per_episode"] for p in profiles})
    print("\n  Workload projections (using mean per-episode time):")
    for label, info in projections.items():
        print(f"    {label:60s}  ~{info['estimated_minutes']:6.2f} min "
              f"({info['estimated_seconds']:7.1f} s)")

    out_path = Path("results/analysis/cost_profile.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(
        {"profiles": profiles, "projections": projections}, indent=2,
    ))
    print(f"\n  -> saved: {out_path}")


if __name__ == "__main__":
    main()
