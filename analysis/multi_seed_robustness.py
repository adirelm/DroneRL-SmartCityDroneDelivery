"""Multi-seed robustness experiment.

Runs each algorithm across multiple seeds on the same scenario configuration
and produces a chart with mean ± 95% bootstrap CI bands per algorithm.

The point: a single seed can be misleading. Reporting mean ± CI shows whether
a result reflects algorithm behavior or just one lucky/unlucky run.

Run: uv run python analysis/multi_seed_robustness.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from analysis._runner import (
    ALGORITHMS,
    base_raw_config,
    resolve_workers,
    train_cells,
)
from dronerl.comparison import ALGORITHM_COLORS, ALGORITHM_LABELS, smooth

SEEDS = (3, 7, 11, 17, 23)
EPISODES = 1500
SMOOTHING = 50
NOISE = 0.5
DENSITY = 0.12
DIFFICULTY = 0.3


def _ci_band(stack: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (mean, low, high) 95% normal-theory CI from a (n_seeds, n_episodes) matrix."""
    mean = stack.mean(axis=0)
    se = stack.std(axis=0, ddof=1) / np.sqrt(stack.shape[0])
    return mean, mean - 1.96 * se, mean + 1.96 * se


def bootstrap_ci(values: np.ndarray, n_resamples: int = 2000, alpha: float = 0.05,
                 rng_seed: int = 42) -> tuple[float, float, float]:
    """Return (mean, low, high) percentile bootstrap CI — robust to bimodal data.

    The §H1 multi-seed result is bimodal for Double-Q (some seeds converge,
    others collapse) so a normal-theory SEM ± 1.96·SE understates the
    uncertainty. Percentile bootstrap CIs make no normality assumption and
    correctly reflect the bimodal spread.
    """
    rng = np.random.default_rng(rng_seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    if n == 0:
        return 0.0, 0.0, 0.0
    resampled = rng.choice(arr, size=(n_resamples, n), replace=True).mean(axis=1)
    low = float(np.quantile(resampled, alpha / 2))
    high = float(np.quantile(resampled, 1 - alpha / 2))
    return float(arr.mean()), low, high


def run(n_workers: int | None = None) -> dict[str, np.ndarray]:
    """Train each algorithm across SEEDS; return smoothed reward stacks.

    ``n_workers`` controls multiprocessing: ``1`` (default) is serial; ``>1``
    runs ``(algo, seed)`` cells in a ``multiprocessing.Pool``. Determinism is
    preserved because each cell reseeds inside its worker.
    """
    raw = base_raw_config()
    raw["dynamic_board"]["enabled"] = True
    raw["agent"]["learning_rate"] = 0.7
    raw["q_learning"].update({"alpha_start": 0.5, "alpha_decay": 0.9995})
    raw["double_q"].update({"alpha_start": 0.6, "alpha_decay": 0.9995})

    board = {"noise_level": NOISE, "hazard_density": DENSITY, "difficulty": DIFFICULTY}
    cells = [(raw, algo, seed, EPISODES, board) for algo in ALGORITHMS for seed in SEEDS]
    workers = resolve_workers(n_workers)
    print(f"  workers: {workers} ({'parallel' if workers > 1 else 'serial'})")
    results = train_cells(cells, n_workers=workers)

    by_algo: dict[str, dict[int, list[float]]] = {algo: {} for algo in ALGORITHMS}
    for algo, seed, rewards, _ in results:
        by_algo[algo][seed] = list(smooth(rewards, SMOOTHING))

    stacks: dict[str, np.ndarray] = {}
    for algo in ALGORITHMS:
        stacks[algo] = np.vstack([by_algo[algo][s] for s in SEEDS])
        last_means = stacks[algo][:, -200:].mean(axis=1)
        boot_mean, boot_low, boot_high = bootstrap_ci(last_means)
        print(f"  {algo:12s}: per-seed last-200 means = "
              f"{[f'{m:6.1f}' for m in last_means]}  "
              f"(spread = {last_means.max() - last_means.min():5.1f}; "
              f"bootstrap 95 % CI = [{boot_low:6.1f}, {boot_high:6.1f}])")
    return stacks


def plot(stacks: dict[str, np.ndarray], out_path: Path) -> str:
    """Render mean ± 95% CI band (top) and per-seed box plot (bottom)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax_line, ax_box) = plt.subplots(2, 1, figsize=(11, 8.5))
    for algo, mat in stacks.items():
        mean, low, high = _ci_band(mat)
        x = np.arange(len(mean))
        color = ALGORITHM_COLORS[algo]
        ax_line.fill_between(x, low, high, color=color, alpha=0.20)
        ax_line.plot(x, mean, label=ALGORITHM_LABELS[algo], color=color, linewidth=2)
    ax_line.set_xlabel("Episode")
    ax_line.set_ylabel(f"Total Reward (smoothed w={SMOOTHING}; mean ± 95% CI over {len(SEEDS)} seeds)")
    ax_line.set_title(
        f"Multi-Seed Robustness ({len(SEEDS)} seeds): "
        "narrower band = result less seed-dependent",
        fontsize=11, fontweight="bold",
    )
    ax_line.grid(True, alpha=0.3)
    ax_line.legend(loc="lower right", framealpha=0.92)

    # Bottom: per-seed last-200 means as a box plot. Reveals the bimodal
    # Double-Q distribution that the line chart hides under its mean curve.
    last_200 = [stacks[algo][:, -200:].mean(axis=1) for algo in stacks]
    labels = [ALGORITHM_LABELS[algo] for algo in stacks]
    colors = [ALGORITHM_COLORS[algo] for algo in stacks]
    bp = ax_box.boxplot(last_200, tick_labels=labels, patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], colors, strict=True):
        patch.set_facecolor(color)
        patch.set_alpha(0.4)
    for whisker in bp["whiskers"]:
        whisker.set_color("#444")
    ax_box.scatter(
        [i + 1 for i, runs in enumerate(last_200) for _ in runs],
        [v for runs in last_200 for v in runs],
        s=18, c="#222", zorder=3,
    )
    ax_box.set_ylabel(f"Last-{200}-episode mean reward")
    ax_box.set_title(
        "Per-seed final-mean distribution (each dot = one seed). "
        "Tight box = robust; wide box = seed-dependent.",
        fontsize=10, fontweight="bold",
    )
    ax_box.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def main():
    print(f"\n=== Multi-seed robustness ({len(SEEDS)} seeds × {EPISODES} ep × 3 algos) ===")
    stacks = run()
    out = Path("results/analysis/multi_seed_robustness.png")
    print(f"  -> saved: {plot(stacks, out)}")


if __name__ == "__main__":
    main()
