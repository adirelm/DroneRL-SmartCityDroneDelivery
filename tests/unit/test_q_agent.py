"""Tests for the QLearningAgent (decaying alpha)."""

import pytest

from dronerl.base_agent import BaseAgent
from dronerl.config_loader import Config, load_config
from dronerl.q_agent import QLearningAgent

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

    def test_alpha_is_float(self, agent):
        assert isinstance(agent.alpha, float)

    def test_default_alpha_start(self, agent):
        assert agent.alpha == 0.5

    def test_default_alpha_end(self, agent):
        assert agent.alpha_end == 0.05

    def test_default_alpha_decay(self, agent):
        assert agent.alpha_decay == 0.9995

    def test_inherits_from_base_agent(self, agent):
        assert isinstance(agent, BaseAgent)


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

    def test_alpha_after_ten_decays(self, agent):
        agent.alpha = 0.5
        agent.alpha_decay = 0.9
        agent.alpha_end = 0.0
        for _ in range(10):
            agent.decay_alpha()
        assert agent.alpha == pytest.approx(0.5 * (0.9 ** 10))

    def test_alpha_reaches_floor_after_many(self, agent):
        for _ in range(100_000):
            agent.decay_alpha()
        assert agent.alpha == agent.alpha_end

    def test_alpha_and_epsilon_independent(self, agent):
        # Setting alpha to its floor should not move epsilon, and vice-versa.
        agent.alpha = agent.alpha_end
        eps_before = agent.epsilon
        agent.decay_epsilon()  # decays both, but alpha is pinned
        assert agent.alpha == agent.alpha_end
        assert agent.epsilon < eps_before


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
        for _ in range(100):
            agent.decay_alpha()
        assert agent.alpha < 0.5
        agent.update((5, 5), 2, -1.0, (5, 4), done=False)
        assert agent.q_table[5, 5, 2] != 0.0

    def test_update_negative_reward(self, agent):
        agent.update((2, 2), 1, -10.0, (2, 3), done=True)
        assert agent.q_table[2, 2, 1] < 0.0

    def test_update_does_not_modify_other_cells(self, agent):
        agent.update((3, 3), 2, 5.0, (3, 4), done=False)
        assert agent.q_table[3, 3, 0] == 0.0
        assert agent.q_table[3, 3, 1] == 0.0
        assert agent.q_table[3, 3, 3] == 0.0
        assert agent.q_table[4, 4, 0] == 0.0


def test_save_load(agent, tmp_path):
    agent.q_table[3, 3, 1] = 7.0
    path = str(tmp_path / "q.npy")
    agent.save(path)
    agent.q_table[3, 3, 1] = 0.0
    agent.load(path)
    assert agent.q_table[3, 3, 1] == 7.0


def test_save_load_does_not_persist_alpha(agent, tmp_path):
    """``save``/``load`` round-trip the Q-table only — α is in-memory training state.

    Documents the actual contract: after ``load`` on a fresh agent (or any
    instance whose α has drifted), α is whatever the most recent ``save`` /
    ``_init_decay`` set it to in *memory*. The .npy file does not record α.
    A future "include α in checkpoint" feature would change this test.
    """
    agent.alpha = 0.1234
    path = str(tmp_path / "q.npy")
    agent.save(path)
    # Drift α to a different value before load — load() must NOT restore the
    # previous α (since alpha was never serialised).
    agent.alpha = 0.5
    agent.load(path)
    assert agent.alpha == 0.5, (
        "α must be unchanged by load() — save/load only round-trip the Q-table"
    )
