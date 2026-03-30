"""Tests for the Agent module."""

import numpy as np
import pytest

from src.agent import Agent
from src.config_loader import Config, load_config

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


@pytest.fixture
def agent(config):
    return Agent(config)


class TestInit:
    def test_q_table_shape(self, agent):
        assert agent.q_table.shape == (12, 12, 4)

    def test_q_table_all_zeros(self, agent):
        assert np.all(agent.q_table == 0.0)

    def test_hyperparams(self, agent):
        assert agent.lr == 0.1
        assert agent.gamma == 0.95
        assert agent.epsilon == 1.0


class TestChooseAction:
    def test_greedy_when_epsilon_zero(self, agent):
        agent.epsilon = 0.0
        agent.q_table[0, 0, 2] = 10.0  # action 2 is best
        action = agent.choose_action((0, 0))
        assert action == 2

    def test_random_when_epsilon_one(self, agent):
        agent.epsilon = 1.0
        actions = {agent.choose_action((0, 0)) for _ in range(200)}
        # With 200 tries at full random, should see multiple actions
        assert len(actions) > 1

    def test_action_in_valid_range(self, agent):
        for _ in range(50):
            a = agent.choose_action((5, 5))
            assert 0 <= a <= 3


class TestUpdate:
    def test_bellman_non_terminal(self, agent):
        state, action, reward, next_state = (0, 0), 1, -1.0, (1, 0)
        agent.q_table[1, 0, 3] = 5.0  # max Q at next_state
        agent.update(state, action, reward, next_state, done=False)
        expected = 0.0 + 0.1 * (-1.0 + 0.95 * 5.0 - 0.0)
        assert pytest.approx(agent.q_table[0, 0, 1], abs=1e-9) == expected

    def test_bellman_terminal(self, agent):
        state, action, reward, next_state = (0, 0), 0, 100.0, (0, 0)
        agent.update(state, action, reward, next_state, done=True)
        expected = 0.0 + 0.1 * (100.0 + 0.0 - 0.0)
        assert pytest.approx(agent.q_table[0, 0, 0], abs=1e-9) == expected

    def test_update_changes_value(self, agent):
        agent.update((3, 3), 2, 10.0, (3, 2), done=False)
        assert agent.q_table[3, 3, 2] != 0.0


class TestDecayEpsilon:
    def test_epsilon_decays(self, agent):
        old = agent.epsilon
        agent.decay_epsilon()
        assert agent.epsilon < old

    def test_epsilon_clamps_at_end(self, agent):
        agent.epsilon = 0.005
        agent.decay_epsilon()
        assert agent.epsilon == agent.epsilon_end


class TestSaveLoad:
    def test_save_and_load(self, agent, tmp_path):
        agent.q_table[2, 3, 1] = 42.0
        path = str(tmp_path / "q_table.npy")
        agent.save(path)
        agent.q_table[2, 3, 1] = 0.0
        agent.load(path)
        assert agent.q_table[2, 3, 1] == 42.0

    def test_save_creates_missing_parent_directory(self, agent, tmp_path):
        path = tmp_path / "nested" / "brain.npy"
        agent.save(str(path))
        assert path.exists()


class TestHelpers:
    def test_get_best_action(self, agent):
        agent.q_table[1, 1, 3] = 99.0
        assert agent.get_best_action((1, 1)) == 3

    def test_get_max_q(self, agent):
        agent.q_table[4, 4, 0] = 7.5
        assert agent.get_max_q((4, 4)) == 7.5

    def test_get_best_action_tie_breaks_first(self, agent):
        # numpy argmax returns first occurrence
        agent.q_table[0, 0] = [5.0, 5.0, 5.0, 5.0]
        assert agent.get_best_action((0, 0)) == 0
