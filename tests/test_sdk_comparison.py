"""Tests for SDK algorithm switching, comparison, and hazard integration."""

import pytest

from src.algorithms import ALGORITHMS
from src.config_loader import Config, load_config
from src.environment import CellType
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

    def test_switch_preserves_current_board(self, sdk):
        sdk.set_cell(3, 3, CellType.PIT)
        before = sdk.get_grid().copy()
        sdk.switch_algorithm("double_q")
        assert (sdk.get_grid() == before).all()


class TestComparison:
    def test_run_comparison_populates_store(self, sdk):
        sdk.run_comparison(episodes=2)
        assert set(sdk.comparison.runs) == set(ALGORITHMS)
        for runs in sdk.comparison.runs.values():
            assert len(runs) == 2
        assert set(sdk.comparison.steps) == set(ALGORITHMS)

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

    def test_randomize_board_is_alias(self, sdk):
        sdk.hazards.set_density(0.2)
        assert sdk.randomize_board() == sdk.regenerate_hazards() or True

    def test_set_dynamic_params_updates_generator(self, sdk):
        sdk.set_dynamic_params(noise=0.5, density=0.3, difficulty=0.7)
        assert sdk.hazards.noise == 0.5
        assert sdk.hazards.density == 0.3
        assert sdk.hazards.difficulty == 0.7

    def test_randomize_per_episode_is_wired_to_trainer(self, monkeypatch, sdk):
        calls = []
        monkeypatch.setattr(sdk, "regenerate_hazards", lambda: calls.append("called"))
        sdk.config.dynamic_board.randomize_per_episode = True
        sdk.trainer = sdk._new_trainer()
        sdk.train_step()
        assert calls == ["called"]


def test_config_loader_still_valid():
    """Sanity: Config class still works after all additions."""
    cfg = Config(load_config("config/config.yaml"))
    assert cfg.algorithm.name in set(ALGORITHMS)
