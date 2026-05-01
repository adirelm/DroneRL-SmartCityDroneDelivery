"""Alpha-decay sensitivity sweep.

Sweeps `alpha_decay` over a grid for Q-Learning and Double-Q-Learning, and
plots final last-200-episode mean reward (averaged over multiple seeds) vs
the decay rate. Bellman is included as a horizontal reference line because
it has no decay parameter.

The point: show whether the conclusion "decaying alpha helps" holds across a
range of decay rates, or whether it depends on a specific tuned value. A
robust conclusion should appear as a flat-ish plateau, not a sharp peak.

Parallel posture (§15): each (algo, decay, seed) cell is dispatched through
``analysis._runner.train_cells`` so a 39-cell sweep gets the same
``multiprocessing.Pool`` speed-up multi_seed_robustness has had since Pass-2.
Per-decay batching is the simplest correct re-keying pattern (within one
batch, ``(algo, seed)`` uniquely identifies a cell — across batches the
outer ``decay`` distinguishes them).

Run: ``uv run python -m analysis.alpha_decay_sweep`` (set ``DRONERL_PARALLEL=4``
to opt into a 4-worker Pool).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from analysis._runner import (  # noqa: E402
    base_raw_config,
    last_window_stats,
    resolve_workers,
    train_cells,
)
from dronerl.comparison import ALGORITHM_COLORS, ALGORITHM_LABELS  # noqa: E402

DECAY_GRID = (0.999, 0.9993, 0.9995, 0.9997, 0.9999, 1.0)
ALGOS = ("q_learning", "double_q")
SEEDS = (3, 11, 23)
EPISODES = 1500
NOISE = 0.5
DENSITY = 0.12
DIFFICULTY = 0.3
_BOARD = {"noise_level": NOISE, "hazard_density": DENSITY, "difficulty": DIFFICULTY}


def _scenario_overrides(raw: dict, decay: float, algo: str) -> dict:
    """Apply identical board overrides plus algorithm-specific decay."""
    raw = {**raw}
    raw["agent"] = {**raw["agent"], "learning_rate": 0.7}
    if algo == "q_learning":
        raw["q_learning"] = {**raw["q_learning"], "alpha_start": 0.5, "alpha_decay": decay}
    elif algo == "double_q":
        raw["double_q"] = {**raw["double_q"], "alpha_start": 0.6, "alpha_decay": decay}
    return raw


def _cells_for_decay(decay: float):
    """Build the 6 (algo, seed) cells for a given decay value, with per-cell raw config."""
    cells = []
    for algo in ALGOS:
        raw = _scenario_overrides(base_raw_config(), decay, algo)
        raw["dynamic_board"]["enabled"] = True
        cells.extend((raw, algo, seed, EPISODES, _BOARD) for seed in SEEDS)
    return cells


def run(n_workers: int | None = None) -> dict:
    """Sweep ``alpha_decay`` × algos × seeds via ``train_cells``."""
    workers = resolve_workers(n_workers)
    total = len(DECAY_GRID) * len(ALGOS) * len(SEEDS) + len(SEEDS)  # +Bellman cells
    print(f"  alpha-decay sweep: {total} cells, workers={workers}")
    results: dict[str, list[tuple[float, float, float]]] = {a: [] for a in ALGOS}
    for decay in DECAY_GRID:
        per_algo: dict[str, list[float]] = {a: [] for a in ALGOS}
        for algo, _seed, rewards, _steps in train_cells(_cells_for_decay(decay), n_workers=workers):
            per_algo[algo].append(last_window_stats(rewards)[0])
        for algo in ALGOS:
            arr = np.asarray(per_algo[algo])
            mean = float(arr.mean())
            sem = float(arr.std(ddof=1) / np.sqrt(len(arr)))
            results[algo].append((decay, mean, sem))
            print(f"  {algo:12s} decay={decay:.4f}  final-200 mean={mean:7.1f}  ±sem={sem:5.1f}")

    raw = _scenario_overrides(base_raw_config(), decay=1.0, algo="bellman")
    raw["dynamic_board"]["enabled"] = True
    bellman_cells = [(raw, "bellman", seed, EPISODES, _BOARD) for seed in SEEDS]
    bellman_finals = [last_window_stats(rewards)[0]
                      for _algo, _seed, rewards, _ in train_cells(bellman_cells, n_workers=workers)]
    bellman_ref = float(np.mean(bellman_finals))
    print(f"  bellman   reference (no decay)             {bellman_ref:7.1f}")
    return {"sweep": results, "bellman": bellman_ref}


def plot(out: dict, out_path: Path) -> str:
    """Render the sensitivity plot."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    for algo, points in out["sweep"].items():
        decays, means, sems = zip(*points, strict=True)
        ax.errorbar(decays, means, yerr=sems, marker="o", linewidth=2,
                    label=ALGORITHM_LABELS[algo], color=ALGORITHM_COLORS[algo])
    ax.axhline(out["bellman"], linestyle="--", color=ALGORITHM_COLORS["bellman"],
               label=f"{ALGORITHM_LABELS['bellman']} (no decay)")
    ax.set_xlabel("alpha_decay (closer to 1.0 = slower decay)")
    ax.set_ylabel("Last-200-episode mean reward (avg over 3 seeds)")
    ax.set_title("Sensitivity to alpha_decay: flatter line = more robust conclusion",
                 fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", framealpha=0.92)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def main() -> None:
    print(f"\n=== Alpha-decay sweep ({len(DECAY_GRID)} decays × {len(SEEDS)} seeds × {len(ALGOS)} algos) ===")
    results = run()
    out = Path("results/analysis/alpha_decay_sweep.png")
    print(f"  -> saved: {plot(results, out)}")


if __name__ == "__main__":
    main()
