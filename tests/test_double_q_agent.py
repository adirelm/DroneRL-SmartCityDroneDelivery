"""Tests for the DoubleQAgent (two Q-tables, cross-table evaluation)."""

import numpy as np
import pytest

from src.config_loader import Config, load_config
from src.double_q_agent import DoubleQAgent

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


@pytest.fixture
def agent(config):
    return DoubleQAgent(config)


class TestInit:
    def test_two_tables_initialized(self, agent):
        assert agent.q_table_a.shape == (12, 12, 4)
        assert agent.q_table_b.shape == (12, 12, 4)
        assert np.all(agent.q_table_a == 0.0)
        assert np.all(agent.q_table_b == 0.0)

    def test_algorithm_name(self, agent):
        assert agent.algorithm_name == "Double Q-Learning"

    def test_alpha_loaded(self, agent, config):
        assert agent.alpha == config.double_q.alpha_start


class TestCombinedQTable:
    def test_q_table_returns_sum(self, agent):
        agent.q_table_a[1, 1, 0] = 3.0
        agent.q_table_b[1, 1, 0] = 4.0
        assert agent.q_table[1, 1, 0] == 7.0


class TestUpdate:
    def test_update_modifies_only_one_table(self, agent, monkeypatch):
        # Force QA update (random.random < 0.5)
        monkeypatch.setattr("src.double_q_agent.random.random", lambda: 0.1)
        agent.q_table_b[1, 0, 3] = 5.0
        before_b = agent.q_table_b.copy()
        agent.update((0, 0), 1, -1.0, (1, 0), done=False)
        # QA should be modified, QB must be untouched
        assert agent.q_table_a[0, 0, 1] != 0.0
        assert np.array_equal(agent.q_table_b, before_b)

    def test_cross_table_evaluation(self, agent, monkeypatch):
        """When updating QA, value should come from QB."""
        monkeypatch.setattr("src.double_q_agent.random.random", lambda: 0.1)
        # Set QA to prefer action 0 at next state
        agent.q_table_a[1, 0, 0] = 100.0
        agent.q_table_a[1, 0, 1] = 50.0
        # QB should be queried at that argmax index (action 0)
        agent.q_table_b[1, 0, 0] = 7.0
        agent.q_table_b[1, 0, 1] = 999.0  # should NOT be used
        agent.alpha = 1.0
        agent.update((0, 0), 1, 0.0, (1, 0), done=False)
        # Expected target = 0 + 0.95 * QB[1,0,0] = 6.65
        assert pytest.approx(agent.q_table_a[0, 0, 1], abs=1e-6) == 0.95 * 7.0

    def test_terminal_ignores_next(self, agent, monkeypatch):
        monkeypatch.setattr("src.double_q_agent.random.random", lambda: 0.1)
        agent.alpha = 1.0
        agent.update((0, 0), 0, 100.0, (0, 0), done=True)
        assert pytest.approx(agent.q_table_a[0, 0, 0], abs=1e-9) == 100.0


class TestDecay:
    def test_alpha_decays(self, agent):
        before = agent.alpha
        agent.decay_alpha()
        assert agent.alpha < before

    def test_decay_epsilon_also_decays_alpha(self, agent):
        a_before, e_before = agent.alpha, agent.epsilon
        agent.decay_epsilon()
        assert agent.alpha < a_before
        assert agent.epsilon < e_before


class TestSaveLoad:
    def test_save_and_load_preserves_both_tables(self, agent, tmp_path):
        agent.q_table_a[2, 3, 1] = 42.0
        agent.q_table_b[5, 5, 2] = 99.0
        path = str(tmp_path / "double.npy")
        agent.save(path)
        agent.q_table_a[:] = 0.0
        agent.q_table_b[:] = 0.0
        agent.load(path)
        assert agent.q_table_a[2, 3, 1] == 42.0
        assert agent.q_table_b[5, 5, 2] == 99.0

    def test_save_creates_parent_directory(self, agent, tmp_path):
        path = tmp_path / "nested" / "double.npy"
        agent.save(str(path))
        assert (tmp_path / "nested" / "double_a.npy").exists()
        assert (tmp_path / "nested" / "double_b.npy").exists()


class TestBestAction:
    def test_best_action_uses_combined(self, agent):
        agent.q_table_a[0, 0] = [1, 0, 0, 0]
        agent.q_table_b[0, 0] = [0, 5, 0, 0]
        # Combined: [1, 5, 0, 0] → action 1
        assert agent.get_best_action((0, 0)) == 1
