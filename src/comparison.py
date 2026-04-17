"""Comparison store and chart generator for the 3 RL algorithms."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ALGORITHM_LABELS = {
    "bellman": "Bellman (constant α)",
    "q_learning": "Q-Learning (decaying α)",
    "double_q": "Double Q-Learning",
}
ALGORITHM_COLORS = {
    "bellman": "#d35400",
    "q_learning": "#2980b9",
    "double_q": "#27ae60",
}


class ComparisonStore:
    """Collects per-algorithm reward histories for plotting."""

    def __init__(self):
        self.runs: dict[str, list[float]] = {}

    def add_run(self, algorithm: str, reward_history: list[float]) -> None:
        """Store a reward history for an algorithm."""
        self.runs[algorithm] = list(reward_history)

    def clear(self) -> None:
        """Remove all stored runs."""
        self.runs.clear()

    def algorithms(self) -> list[str]:
        """Return list of algorithms with stored runs."""
        return list(self.runs)


def smooth(values: list[float], window: int) -> list[float]:
    """Apply a moving-average smoothing of the given window size."""
    if len(values) < 2 or window <= 1:
        return list(values)
    arr = np.asarray(values, dtype=float)
    eff = min(window, len(arr))
    kernel = np.ones(eff) / eff
    return list(np.convolve(arr, kernel, mode="valid"))


def generate_comparison_chart(
    store: ComparisonStore,
    output_path: str,
    title: str = "Convergence Comparison",
    smoothing_window: int = 50,
) -> str:
    """Render a convergence comparison chart and save as PNG. Returns the path."""
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    for algo in ("bellman", "q_learning", "double_q"):
        history = store.runs.get(algo)
        if not history:
            continue
        smoothed = smooth(history, smoothing_window)
        x = np.arange(len(smoothed)) + (len(history) - len(smoothed))
        ax.plot(
            x, smoothed,
            label=ALGORITHM_LABELS[algo],
            color=ALGORITHM_COLORS[algo],
            linewidth=2,
        )
    ax.set_xlabel("Episode")
    ax.set_ylabel(f"Total Reward (smoothed, window={smoothing_window})")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(target, dpi=120)
    plt.close(fig)
    return str(target)
