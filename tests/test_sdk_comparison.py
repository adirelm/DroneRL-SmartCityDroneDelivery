"""Tests for SDK algorithm switching, comparison, and hazard integration."""

import pytest

from src.config_loader import Config, load_config
from src.sdk import DroneRLSDK


@pytest.fixture
def sdk():
    return DroneRLSDK("config/config.yaml")


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


def test_config_loader_still_valid():
    """Sanity: Config class still works after all additions."""
    cfg = Config(load_config("config/config.yaml"))
    assert cfg.algorithm.name in {"bellman", "q_learning", "double_q"}
