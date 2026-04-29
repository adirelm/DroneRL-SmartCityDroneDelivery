"""Tests for the comparison store and chart generator."""


from dronerl.algorithms import ALGORITHMS
from dronerl.comparison import (
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

    def test_has_results(self):
        store = ComparisonStore()
        assert store.has_results("bellman") is False
        store.add_run("bellman", [1.0])
        assert store.has_results("bellman") is True
        store.add_run("q_learning", [])
        assert store.has_results("q_learning") is False

    def test_has_all(self):
        store = ComparisonStore()
        for algo in ALGORITHMS:
            assert store.has_all() is False
            store.add_run(algo, [1.0])
        assert store.has_all() is True

    def test_has_all_false_with_two(self):
        store = ComparisonStore()
        store.add_run("bellman", [1.0])
        store.add_run("q_learning", [1.0])
        assert store.has_all() is False

    def test_get_histories(self):
        store = ComparisonStore()
        store.add_run("bellman", [1.0, 2.0])
        h = store.get_histories()
        assert h == {"bellman": [1.0, 2.0]}

    def test_get_histories_empty_when_no_results(self):
        assert ComparisonStore().get_histories() == {}

    def test_clear_resets_has_all_and_has_results(self):
        store = ComparisonStore()
        for algo in ALGORITHMS:
            store.add_run(algo, [1.0])
        store.clear()
        assert store.has_all() is False
        assert store.has_results("bellman") is False
        assert store.get_histories() == {}

    def test_add_run_overwrites_same_algo(self):
        store = ComparisonStore()
        store.add_run("bellman", [1.0, 2.0])
        store.add_run("bellman", [9.0])
        assert store.runs["bellman"] == [9.0]

    def test_add_run_preserves_other_algos(self):
        store = ComparisonStore()
        store.add_run("bellman", [1.0])
        store.add_run("q_learning", [2.0])
        store.add_run("bellman", [3.0])
        assert store.runs["q_learning"] == [2.0]


class TestSmooth:
    def test_smooth_identity_when_short(self):
        assert smooth([1.0], 50) == [1.0]

    def test_smooth_identity_when_window_one(self):
        assert smooth([1.0, 2.0, 3.0], 1) == [1.0, 2.0, 3.0]

    def test_smooth_output_length_equals_input(self):
        result = smooth([1.0, 2.0, 3.0, 4.0], 2)
        assert len(result) == 4

    def test_smooth_preserves_order_of_magnitude(self):
        result = smooth([1.0, 2.0, 3.0], 10)
        # Every output should be within the min/max of the input
        assert min(result) >= 0.0 and max(result) <= 3.0


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
