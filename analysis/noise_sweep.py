"""Noise-level OAT sweep — directly tests the H1 prediction.

EXPERIMENTS.md §H1 says "noise breaks Bellman" *but* qualifies the
claim: it depends on noise level. Pass-1 multi-seed only ran at
noise=0.5 (medium); Pass-2 alpha-decay sweep varied α but kept noise
fixed. This script sweeps the noise dimension explicitly to find the
crossover where Bellman's constant-α actually starts to lose ground
to Q-Learning's decaying α.

Methodology (One-At-a-Time / OAT):
    Vary `noise_level ∈ {0.0, 0.25, 0.5, 0.75, 0.95}` while holding
    everything else constant (3 seeds × 2 algorithms × 1500 episodes).
    Report the per-noise-level mean ± SEM of last-200-episode reward
    for Bellman vs Q-Learning, and identify the noise level (if any)
    where Q-Learning pulls ahead.

Run: ``uv run python -m analysis.noise_sweep``
Output: ``results/analysis/noise_sweep.png`` + console table.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from analysis._runner import base_raw_config, resolve_workers, train_cells  # noqa: E402
from dronerl.comparison import ALGORITHM_COLORS, ALGORITHM_LABELS  # noqa: E402

NOISE_LEVELS = (0.0, 0.25, 0.5, 0.75, 0.95)
ALGOS = ("bellman", "q_learning")
SEEDS = (3, 11, 23)
EPISODES = 1500
DENSITY = 0.12
DIFFICULTY = 0.3


def run(n_workers: int | None = None) -> dict:
    """Sweep noise; return ``{(algo, noise): {"mean": ..., "sem": ...}}``."""
    raw = base_raw_config()
    raw["dynamic_board"]["enabled"] = True
    raw["agent"]["learning_rate"] = 0.7
    raw["q_learning"].update({"alpha_start": 0.5, "alpha_decay": 0.9995})

    # Dispatch one batch per noise level. Within a single batch, (algo, seed)
    # uniquely identifies a cell so we can re-key safely from
    # ``train_cells``'s completion-order output. Batching across noise levels
    # would break this invariant: the same (algo, seed) tuple appears in
    # every batch, so a single all-cells dispatch would mis-key results
    # under ``n_workers > 1`` (Pool.imap_unordered returns in completion
    # order, not submission order).
    workers = resolve_workers(n_workers)
    total_cells = len(NOISE_LEVELS) * len(ALGOS) * len(SEEDS)
    print(f"  noise sweep: {total_cells} cells, workers={workers}")
    by_cell: dict[tuple[str, float, int], list[float]] = {}
    for noise in NOISE_LEVELS:
        board = {"noise_level": noise, "hazard_density": DENSITY, "difficulty": DIFFICULTY}
        cells = [(raw, algo, seed, EPISODES, board) for algo in ALGOS for seed in SEEDS]
        for algo, seed, rewards, _ in train_cells(cells, n_workers=workers):
            by_cell[(algo, noise, seed)] = rewards

    summary: dict[tuple[str, float], dict[str, float]] = {}
    for noise in NOISE_LEVELS:
        for algo in ALGOS:
            tails = [by_cell[(algo, noise, s)][-200:] for s in SEEDS]
            means = [float(np.mean(t)) for t in tails]
            mean = float(np.mean(means))
            sem = float(np.std(means, ddof=1) / np.sqrt(len(means)))
            summary[(algo, noise)] = {"mean": mean, "sem": sem}
    return summary


def plot(summary: dict, out_path: Path) -> str:
    """Render mean ± SEM line chart, one line per algorithm across noise."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for algo in ALGOS:
        means = [summary[(algo, n)]["mean"] for n in NOISE_LEVELS]
        sems = [summary[(algo, n)]["sem"] for n in NOISE_LEVELS]
        color = ALGORITHM_COLORS[algo]
        ax.errorbar(NOISE_LEVELS, means, yerr=sems, label=ALGORITHM_LABELS[algo],
                    color=color, marker="o", markersize=8, linewidth=2, capsize=4)
    ax.set_xlabel("Noise level (wind drift probability multiplier)")
    ax.set_ylabel("Last-200-episode mean reward")
    ax.set_title(f"H1 noise-level sweep (3 seeds × {EPISODES} ep / cell)\n"
                 "Bellman vs Q-Learning: where does decaying α matter?")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", framealpha=0.92)
    ax.axhline(0, color="#888", linestyle=":", linewidth=1, alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def main() -> None:
    print(f"\n=== Noise sweep ({len(NOISE_LEVELS)} levels × {len(ALGOS)} algos × {len(SEEDS)} seeds × {EPISODES} ep) ===")
    summary = run()
    print(f"\n  {'noise':>6}  {'Bellman':>14}  {'Q-Learning':>14}  delta")
    for n in NOISE_LEVELS:
        b, q = summary[("bellman", n)], summary[("q_learning", n)]
        delta = q["mean"] - b["mean"]
        print(f"  {n:6.2f}  {b['mean']:7.1f} ± {b['sem']:4.1f}  "
              f"{q['mean']:7.1f} ± {q['sem']:4.1f}  {delta:+6.1f}")
    out = Path("results/analysis/noise_sweep.png")
    print(f"\n  -> saved: {plot(summary, out)}")


if __name__ == "__main__":
    main()
