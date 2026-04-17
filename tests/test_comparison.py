"""Tests for the comparison store and chart generator."""

import pytest

from src.comparison import (
    ALGORITHM_LABELS,
    ComparisonStore,
    generate_comparison_chart,
    smooth,
)


class TestComparisonStore:
    def test_empty_store(self):
        store = ComparisonStore()
        assert store.runs == {}
        assert store.algorithms() == []

    def test_add_run(self):
        store = ComparisonStore()
        store.add_run("bellman", [1.0, 2.0, 3.0])
        assert store.runs["bellman"] == [1.0, 2.0, 3.0]
        assert "bellman" in store.algorithms()

    def test_add_run_copies_history(self):
        store = ComparisonStore()
        history = [1.0, 2.0]
        store.add_run("bellman", history)
        history.append(3.0)
        assert store.runs["bellman"] == [1.0, 2.0]

    def test_clear(self):
        store = ComparisonStore()
        store.add_run("q_learning", [1.0])
        store.clear()
        assert store.runs == {}


class TestSmooth:
    def test_smooth_identity_when_short(self):
        assert smooth([1.0], 50) == [1.0]

    def test_smooth_identity_when_window_one(self):
        assert smooth([1.0, 2.0, 3.0], 1) == [1.0, 2.0, 3.0]

    def test_smooth_moving_average(self):
        result = smooth([1.0, 2.0, 3.0, 4.0], 2)
        assert result == pytest.approx([1.5, 2.5, 3.5])

    def test_smooth_window_larger_than_data(self):
        result = smooth([1.0, 2.0, 3.0], 10)
        assert result == pytest.approx([2.0])  # avg of [1,2,3]


class TestChartGeneration:
    def test_generate_chart_creates_file(self, tmp_path):
        store = ComparisonStore()
        store.add_run("bellman", [-100.0 + i for i in range(200)])
        store.add_run("q_learning", [-80.0 + i for i in range(200)])
        store.add_run("double_q", [-60.0 + i for i in range(200)])
        out = tmp_path / "subdir" / "comparison.png"
        path = generate_comparison_chart(store, str(out), title="Test")
        assert out.exists()
        assert path == str(out)

    def test_generate_chart_skips_missing_algos(self, tmp_path):
        store = ComparisonStore()
        store.add_run("bellman", [1.0] * 100)
        out = tmp_path / "single.png"
        generate_comparison_chart(store, str(out))
        assert out.exists()

    def test_algorithm_labels_present(self):
        assert "bellman" in ALGORITHM_LABELS
        assert "q_learning" in ALGORITHM_LABELS
        assert "double_q" in ALGORITHM_LABELS
