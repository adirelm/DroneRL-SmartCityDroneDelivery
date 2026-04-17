"""Tests for the QLearningAgent (decaying alpha)."""

import pytest

from src.config_loader import Config, load_config
from src.q_agent import QLearningAgent

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


@pytest.fixture
def agent(config):
    return QLearningAgent(config)


class TestInit:
    def test_alpha_starts_at_start(self, agent, config):
        assert agent.alpha == config.q_learning.alpha_start

    def test_alpha_end_loaded(self, agent, config):
        assert agent.alpha_end == config.q_learning.alpha_end

    def test_alpha_decay_loaded(self, agent, config):
        assert agent.alpha_decay == config.q_learning.alpha_decay

    def test_algorithm_name(self, agent):
        assert agent.algorithm_name == "Q-Learning"

    def test_q_table_shape(self, agent):
        assert agent.q_table.shape == (12, 12, 4)


class TestAlphaDecay:
    def test_alpha_decays(self, agent):
        before = agent.alpha
        agent.decay_alpha()
        assert agent.alpha < before

    def test_alpha_clamps_at_end(self, agent):
        agent.alpha = 0.001
        agent.decay_alpha()
        assert agent.alpha == agent.alpha_end

    def test_alpha_decay_uses_multiplicative_formula(self, agent):
        agent.alpha = 0.5
        agent.alpha_decay = 0.9
        agent.alpha_end = 0.01
        agent.decay_alpha()
        assert agent.alpha == pytest.approx(0.45)

    def test_decay_epsilon_also_decays_alpha(self, agent):
        alpha_before = agent.alpha
        epsilon_before = agent.epsilon
        agent.decay_epsilon()
        assert agent.alpha < alpha_before
        assert agent.epsilon < epsilon_before


class TestUpdate:
    def test_update_uses_current_alpha(self, agent):
        agent.alpha = 0.2
        agent.q_table[1, 0, 3] = 5.0
        agent.update((0, 0), 1, -1.0, (1, 0), done=False)
        expected = 0.0 + 0.2 * (-1.0 + 0.95 * 5.0 - 0.0)
        assert pytest.approx(agent.q_table[0, 0, 1], abs=1e-9) == expected

    def test_update_terminal(self, agent):
        agent.alpha = 0.5
        agent.update((0, 0), 0, 100.0, (0, 0), done=True)
        expected = 0.5 * 100.0
        assert pytest.approx(agent.q_table[0, 0, 0], abs=1e-9) == expected

    def test_update_after_decay(self, agent):
        # Simulate a few episodes worth of decay, then ensure update still works
        for _ in range(100):
            agent.decay_alpha()
        assert agent.alpha < 0.5
        agent.update((5, 5), 2, -1.0, (5, 4), done=False)
        assert agent.q_table[5, 5, 2] != 0.0


def test_save_load(agent, tmp_path):
    agent.q_table[3, 3, 1] = 7.0
    path = str(tmp_path / "q.npy")
    agent.save(path)
    agent.q_table[3, 3, 1] = 0.0
    agent.load(path)
    assert agent.q_table[3, 3, 1] == 7.0
