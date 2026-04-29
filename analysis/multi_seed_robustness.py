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

from analysis._runner import ALGORITHMS, base_raw_config, train_run, with_overrides
from src.comparison import ALGORITHM_COLORS, ALGORITHM_LABELS, smooth

SEEDS = (3, 7, 11, 17, 23)
EPISODES = 1500
SMOOTHING = 50
NOISE = 0.5
DENSITY = 0.12
DIFFICULTY = 0.3


def _ci_band(stack: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (mean, low, high) 95% CI from a (n_seeds, n_episodes) matrix."""
    mean = stack.mean(axis=0)
    se = stack.std(axis=0, ddof=1) / np.sqrt(stack.shape[0])
    return mean, mean - 1.96 * se, mean + 1.96 * se


def run() -> dict[str, np.ndarray]:
    """Train each algorithm across SEEDS; return smoothed reward stacks."""
    raw = base_raw_config()
    raw["dynamic_board"]["enabled"] = True
    raw["agent"]["learning_rate"] = 0.7
    raw["q_learning"].update({"alpha_start": 0.5, "alpha_decay": 0.9995})
    raw["double_q"].update({"alpha_start": 0.6, "alpha_decay": 0.9995})

    stacks: dict[str, np.ndarray] = {}
    for algo in ALGORITHMS:
        rows = []
        for seed in SEEDS:
            cfg = with_overrides(
                raw, algorithm=algo,
                noise_level=NOISE, hazard_density=DENSITY,
                difficulty=DIFFICULTY, seed=seed,
            )
            rewards, _ = train_run(cfg, EPISODES, seed=seed)
            rows.append(np.asarray(smooth(rewards, SMOOTHING)))
        stacks[algo] = np.vstack(rows)
        last_means = stacks[algo][:, -200:].mean(axis=1)
        print(f"  {algo:12s}: per-seed last-200 means = "
              f"{[f'{m:6.1f}' for m in last_means]}  "
              f"(spread = {last_means.max() - last_means.min():5.1f})")
    return stacks


def plot(stacks: dict[str, np.ndarray], out_path: Path) -> str:
    """Render mean ± 95% CI band per algorithm."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for algo, mat in stacks.items():
        mean, low, high = _ci_band(mat)
        x = np.arange(len(mean))
        color = ALGORITHM_COLORS[algo]
        ax.fill_between(x, low, high, color=color, alpha=0.20)
        ax.plot(x, mean, label=ALGORITHM_LABELS[algo], color=color, linewidth=2)
    ax.set_xlabel("Episode")
    ax.set_ylabel(f"Total Reward (smoothed w={SMOOTHING}; mean ± 95% CI over {len(SEEDS)} seeds)")
    ax.set_title(
        f"Multi-Seed Robustness ({len(SEEDS)} seeds): "
        "narrower band = result less seed-dependent",
        fontsize=11, fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", framealpha=0.92)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def main():
    print(f"\n=== Multi-seed robustness ({len(SEEDS)} seeds × {EPISODES} ep × 3 algos) ===")
    stacks = run()
    out = Path("data/analysis/multi_seed_robustness.png")
    print(f"  -> saved: {plot(stacks, out)}")


if __name__ == "__main__":
    main()
