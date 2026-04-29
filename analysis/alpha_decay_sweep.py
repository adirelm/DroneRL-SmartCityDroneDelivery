"""Alpha-decay sensitivity sweep.

Sweeps `alpha_decay` over a grid for Q-Learning and Double-Q-Learning, and
plots final last-200-episode mean reward (averaged over multiple seeds) vs
the decay rate. Bellman is included as a horizontal reference line because
it has no decay parameter.

The point: show whether the conclusion "decaying alpha helps" holds across a
range of decay rates, or whether it depends on a specific tuned value. A
robust conclusion should appear as a flat-ish plateau, not a sharp peak.

Run: uv run python analysis/alpha_decay_sweep.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from analysis._runner import (
    base_raw_config,
    last_window_stats,
    train_run,
    with_overrides,
)
from src.comparison import ALGORITHM_COLORS, ALGORITHM_LABELS

DECAY_GRID = (0.999, 0.9993, 0.9995, 0.9997, 0.9999, 1.0)
SEEDS = (3, 11, 23)
EPISODES = 1500
NOISE = 0.5
DENSITY = 0.12
DIFFICULTY = 0.3


def _scenario_overrides(raw: dict, decay: float, algo: str) -> dict:
    """Apply identical board overrides plus algorithm-specific decay."""
    raw = {**raw}
    raw["agent"] = {**raw["agent"], "learning_rate": 0.7}
    if algo == "q_learning":
        raw["q_learning"] = {**raw["q_learning"], "alpha_start": 0.5, "alpha_decay": decay}
    elif algo == "double_q":
        raw["double_q"] = {**raw["double_q"], "alpha_start": 0.6, "alpha_decay": decay}
    return raw


def _mean_final_reward(algo: str, decay: float) -> tuple[float, float]:
    """Train one algorithm at a given decay across SEEDS; return (mean, sem)."""
    raw = _scenario_overrides(base_raw_config(), decay, algo)
    raw["dynamic_board"]["enabled"] = True
    finals = []
    for seed in SEEDS:
        cfg = with_overrides(
            raw, algorithm=algo,
            noise_level=NOISE, hazard_density=DENSITY,
            difficulty=DIFFICULTY, seed=seed,
        )
        rewards, _ = train_run(cfg, EPISODES, seed=seed)
        mean, _ = last_window_stats(rewards)
        finals.append(mean)
    arr = np.asarray(finals)
    return float(arr.mean()), float(arr.std(ddof=1) / np.sqrt(len(arr)))


def _bellman_reference() -> float:
    """Return Bellman's averaged final reward across seeds (no decay parameter)."""
    raw = _scenario_overrides(base_raw_config(), decay=1.0, algo="bellman")
    raw["dynamic_board"]["enabled"] = True
    finals = []
    for seed in SEEDS:
        cfg = with_overrides(
            raw, algorithm="bellman",
            noise_level=NOISE, hazard_density=DENSITY,
            difficulty=DIFFICULTY, seed=seed,
        )
        rewards, _ = train_run(cfg, EPISODES, seed=seed)
        finals.append(last_window_stats(rewards)[0])
    return float(np.mean(finals))


def run() -> dict:
    """Run the full sweep; return per-algo lists of (decay, mean, sem)."""
    results: dict[str, list[tuple[float, float, float]]] = {"q_learning": [], "double_q": []}
    for algo in results:
        for decay in DECAY_GRID:
            mean, sem = _mean_final_reward(algo, decay)
            results[algo].append((decay, mean, sem))
            print(f"  {algo:12s} decay={decay:.4f}  final-200 mean={mean:7.1f}  ±sem={sem:5.1f}")
    bellman_ref = _bellman_reference()
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


def main():
    print(f"\n=== Alpha-decay sweep ({len(DECAY_GRID)} decays × {len(SEEDS)} seeds × 2 algos) ===")
    results = run()
    out = Path("data/analysis/alpha_decay_sweep.png")
    print(f"  -> saved: {plot(results, out)}")


if __name__ == "__main__":
    main()
