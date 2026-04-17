"""Tests for the DroneRL SDK module."""

import numpy as np
import pytest

from src.environment import CellType
from src.sdk import DroneRLSDK

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def sdk():
    return DroneRLSDK(CONFIG_PATH)


class TestInit:
    def test_sdk_creates_components(self, sdk):
        assert sdk.agent is not None
        assert sdk.environment is not None
        assert sdk.trainer is not None

    def test_initial_episode_count(self, sdk):
        assert sdk.episode_count == 0

    def test_initial_epsilon(self, sdk):
        assert sdk.epsilon == 1.0


class TestTrainStep:
    def test_returns_dict(self, sdk):
        result = sdk.train_step()
        assert isinstance(result, dict)

    def test_dict_keys(self, sdk):
        result = sdk.train_step()
        assert "reward" in result
        assert "steps" in result
        assert "reached_goal" in result

    def test_increments_count(self, sdk):
        sdk.train_step()
        assert sdk.episode_count == 1


class TestTrainBatch:
    def test_returns_list(self, sdk):
        results = sdk.train_batch(3)
        assert isinstance(results, list)
        assert len(results) == 3

    def test_each_result_is_dict(self, sdk):
        results = sdk.train_batch(2)
        for r in results:
            assert isinstance(r, dict)

    def test_episode_count_after_batch(self, sdk):
        sdk.train_batch(5)
        assert sdk.episode_count == 5


class TestReset:
    def test_reset_clears_episodes(self, sdk):
        sdk.train_batch(3)
        sdk.reset()
        assert sdk.episode_count == 0

    def test_reset_restores_epsilon(self, sdk):
        sdk.train_batch(10)
        sdk.reset()
        assert sdk.epsilon == 1.0

    def test_reset_clears_reward_history(self, sdk):
        sdk.train_batch(5)
        sdk.reset()
        assert sdk.reward_history == []


class TestGetters:
    def test_get_q_table_is_ndarray(self, sdk):
        q = sdk.get_q_table()
        assert isinstance(q, np.ndarray)
        assert q.shape == (12, 12, 4)

    def test_get_grid_is_ndarray(self, sdk):
        g = sdk.get_grid()
        assert isinstance(g, np.ndarray)
        assert g.shape == (12, 12)

    def test_get_metrics_returns_dict(self, sdk):
        m = sdk.get_metrics()
        assert isinstance(m, dict)


class TestSaveLoadBrain:
    def test_save_and_load(self, sdk, tmp_path):
        sdk.train_batch(5)
        path = str(tmp_path / "brain.npy")
        sdk.save_brain(path)
        original_q = sdk.get_q_table().copy()
        sdk.reset()
        sdk.load_brain(path)
        np.testing.assert_array_equal(sdk.get_q_table(), original_q)


class TestSetCell:
    def test_set_cell_modifies_grid(self, sdk):
        sdk.set_cell(5, 5, CellType.BUILDING)
        assert sdk.get_grid()[5, 5] == CellType.BUILDING

    def test_drone_position_property(self, sdk):
        assert sdk.drone_position == (0, 0)

    def test_goal_rate_property(self, sdk):
        assert sdk.goal_rate == 0.0


class TestSwitchAlgorithm:
    def test_switch_changes_algorithm_name(self, sdk):
        sdk.switch_algorithm("q_learning")
        assert sdk.config.algorithm.name == "q_learning"
        assert sdk.agent.algorithm_name == "Q-Learning"

    def test_switch_to_double_q(self, sdk):
        sdk.switch_algorithm("double_q")
        assert sdk.agent.algorithm_name == "Double Q-Learning"

    def test_switch_resets_training_state(self, sdk):
        sdk.train_step()
        assert sdk.episode_count == 1
        sdk.switch_algorithm("q_learning")
        assert sdk.episode_count == 0


class TestComparison:
    def test_run_comparison_populates_store(self, sdk):
        sdk.run_comparison(episodes=2)
        assert set(sdk.comparison.runs) == {"bellman", "q_learning", "double_q"}
        for runs in sdk.comparison.runs.values():
            assert len(runs) == 2

    def test_run_comparison_restores_original_algorithm(self, sdk):
        original = sdk.config.algorithm.name
        original_agent_class = type(sdk.agent)
        sdk.run_comparison(episodes=2)
        assert sdk.config.algorithm.name == original
        assert isinstance(sdk.agent, original_agent_class)

    def test_generate_chart_produces_file(self, sdk, tmp_path):
        sdk.run_comparison(episodes=2)
        out = tmp_path / "chart.png"
        path = sdk.generate_chart(str(out))
        assert path == str(out)
        assert out.exists()


class TestHazardIntegration:
    def test_regenerate_hazards_returns_count(self, sdk):
        sdk.config.dynamic_board.hazard_density = 0.2
        sdk.config.dynamic_board.difficulty = 0.5
        sdk.hazards = type(sdk.hazards)(sdk.config)
        placed = sdk.regenerate_hazards()
        assert placed >= 0
