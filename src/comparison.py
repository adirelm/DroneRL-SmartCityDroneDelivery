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
    """Collects per-algorithm reward + steps histories for plotting."""

    def __init__(self):
        self.runs: dict[str, list[float]] = {}
        self.steps: dict[str, list[int]] = {}

    def add_run(self, algorithm: str, reward_history: list[float],
                steps_history: list[int] | None = None) -> None:
        """Store reward (and optionally steps) history for an algorithm."""
        self.runs[algorithm] = list(reward_history)
        if steps_history is not None:
            self.steps[algorithm] = list(steps_history)

    def clear(self) -> None:
        """Remove all stored runs."""
        self.runs.clear()
        self.steps.clear()

    def algorithms(self) -> list[str]:
        """Return list of algorithms with stored runs."""
        return list(self.runs)

    def has_results(self, algorithm: str) -> bool:
        """Return True if a run is stored for the given algorithm."""
        return algorithm in self.runs and bool(self.runs[algorithm])

    def has_all(self) -> bool:
        """Return True if bellman, q_learning, and double_q are all stored."""
        return all(self.has_results(a) for a in ("bellman", "q_learning", "double_q"))

    def get_histories(self) -> dict[str, list[float]]:
        """Return a shallow copy of the stored run histories."""
        return dict(self.runs)


def smooth(values: list[float], window: int) -> list[float]:
    """Moving-average smoothing; output length == input length so x starts at 0."""
    if len(values) < 2 or window <= 1:
        return list(values)
    arr = np.asarray(values, dtype=float)
    eff = min(window, len(arr))
    kernel = np.ones(eff) / eff
    return list(np.convolve(arr, kernel, mode="same"))


def _rolling_std(values: list[float], window: int) -> np.ndarray:
    """Rolling standard deviation (same length as input)."""
    arr = np.asarray(values, dtype=float)
    if len(arr) < 2 or window <= 1:
        return np.zeros_like(arr)
    w = min(window, len(arr))
    pad = w // 2
    padded = np.pad(arr, (pad, w - pad - 1), mode="edge")
    return np.array([padded[i:i + w].std() for i in range(len(arr))])


def _plot_series(ax, store_dict, smoothing_window, ylabel, title, fmt="6.1f"):
    """Draw per-algorithm smoothed curves + ±1σ bands + stats box on a single axis."""
    summary = []
    for algo in ("bellman", "q_learning", "double_q"):
        history = store_dict.get(algo)
        if not history:
            continue
        smoothed = np.array(smooth(history, smoothing_window))
        std = _rolling_std(history, smoothing_window)
        x = np.arange(len(smoothed))
        color = ALGORITHM_COLORS[algo]
        ax.fill_between(x, smoothed - std, smoothed + std, color=color, alpha=0.15)
        ax.plot(x, smoothed, label=ALGORITHM_LABELS[algo], color=color, linewidth=2)
        tail = np.asarray(history[-200:], dtype=float)
        summary.append(f"{ALGORITHM_LABELS[algo]:<28s}  mean={tail.mean():{fmt}}  std={tail.std():{fmt}}")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", framealpha=0.92, fontsize=8)
    if summary:
        ax.text(0.015, 0.97, "Last-200-episode:\n" + "\n".join(summary),
                transform=ax.transAxes, va="top", ha="left", fontsize=8, family="monospace",
                bbox={"boxstyle": "round,pad=0.4", "facecolor": "white",
                      "edgecolor": "#888", "alpha": 0.92})


def generate_comparison_chart(
    store: ComparisonStore,
    output_path: str,
    title: str = "Convergence Comparison",
    smoothing_window: int = 50,
) -> str:
    """Render the convergence chart. If steps are stored, adds a lower subplot.

    The lecturer's Scenario 2 spec is "lower score AND longer time" — both
    dimensions are shown when steps data is available.
    """
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    has_steps = bool(store.steps) and all(store.steps.get(a) for a in store.runs)
    if has_steps:
        fig, (ax_r, ax_s) = plt.subplots(2, 1, figsize=(11, 8.5), sharex=True)
        _plot_series(ax_r, store.runs, smoothing_window,
                     f"Total Reward (smoothed w={smoothing_window}; ±1σ)", title)
        _plot_series(ax_s, store.steps, smoothing_window,
                     "Steps per Episode (lower = faster)",
                     "Episode length: failing algorithms take longer to reach the goal",
                     fmt="6.1f")
        ax_s.set_xlabel("Episode")
    else:
        fig, ax = plt.subplots(figsize=(11, 6.5))
        _plot_series(ax, store.runs, smoothing_window,
                     f"Total Reward (smoothed w={smoothing_window}; ±1σ)", title)
        ax.set_xlabel("Episode")
    fig.tight_layout()
    fig.savefig(target, dpi=120)
    plt.close(fig)
    return str(target)
