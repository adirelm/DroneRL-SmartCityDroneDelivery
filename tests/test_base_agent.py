"""Tests for the BaseAgent class (core behaviour)."""

import numpy as np
import pytest

from src.agent import BellmanAgent
from src.base_agent import BaseAgent
from src.config_loader import Config, load_config

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


@pytest.fixture
def agent(config):
    """Concrete BellmanAgent used to exercise shared BaseAgent behaviour."""
    return BellmanAgent(config)


def test_base_agent_update_raises(config):
    """update() on BaseAgent must raise NotImplementedError."""
    base = BaseAgent(config)
    with pytest.raises(NotImplementedError):
        base.update((0, 0), 0, -1.0, (0, 1), done=False)


def test_base_agent_shared_shape(config):
    base = BaseAgent(config)
    assert base.q_table.shape == (12, 12, 4)


def test_base_agent_algorithm_name(config):
    base = BaseAgent(config)
    assert base.algorithm_name == "Base"


def test_concrete_subclass_instantiates(config):
    assert BellmanAgent(config) is not None


class TestQTable:
    def test_q_table_is_ndarray(self, agent):
        assert isinstance(agent.q_table, np.ndarray)

    def test_q_table_initial_zeros(self, agent):
        assert np.all(agent.q_table == 0.0)

    def test_q_table_dtype_float(self, agent):
        assert agent.q_table.dtype == np.float64

    def test_q_table_element_count(self, agent):
        assert agent.q_table.size == 12 * 12 * 4


class TestChooseAction:
    def test_returns_int(self, agent):
        agent.epsilon = 0.0
        assert isinstance(agent.choose_action((0, 0)), int)

    def test_in_range(self, agent):
        for _ in range(50):
            a = agent.choose_action((3, 3))
            assert 0 <= a <= 3

    def test_exploit_when_epsilon_zero(self, agent):
        agent.epsilon = 0.0
        agent.q_table[0, 0, 2] = 10.0
        assert agent.choose_action((0, 0)) == 2

    def test_explores_when_epsilon_one(self, agent):
        agent.epsilon = 1.0
        seen = {agent.choose_action((0, 0)) for _ in range(300)}
        assert len(seen) > 1

    def test_partially_trained_table(self, agent):
        agent.epsilon = 0.0
        agent.q_table[2, 2, 1] = 1.0
        assert agent.choose_action((2, 2)) == 1


class TestGetBestAction:
    def test_returns_int(self, agent):
        assert isinstance(agent.get_best_action((0, 0)), int)

    def test_returns_argmax(self, agent):
        agent.q_table[1, 1, 3] = 5.0
        assert agent.get_best_action((1, 1)) == 3

    def test_all_zero_returns_zero(self, agent):
        assert agent.get_best_action((0, 0)) == 0

    def test_single_nonzero_value(self, agent):
        agent.q_table[2, 2, 2] = 0.1
        assert agent.get_best_action((2, 2)) == 2

    def test_multiple_nonzero_values(self, agent):
        agent.q_table[1, 1] = [1.0, 2.0, 3.0, 2.5]
        assert agent.get_best_action((1, 1)) == 2

    def test_first_max_on_ties(self, agent):
        agent.q_table[0, 0] = [5.0, 5.0, 5.0, 5.0]
        assert agent.get_best_action((0, 0)) == 0


class TestGetMaxQ:
    def test_returns_float(self, agent):
        assert isinstance(agent.get_max_q((0, 0)), float)

    def test_all_zero_returns_zero(self, agent):
        assert agent.get_max_q((0, 0)) == 0.0

    def test_positive_values(self, agent):
        agent.q_table[3, 3, 1] = 7.5
        assert agent.get_max_q((3, 3)) == 7.5

    def test_negative_values(self, agent):
        agent.q_table[0, 0] = [-1.0, -2.0, -3.0, -4.0]
        assert agent.get_max_q((0, 0)) == -1.0

    def test_mixed_values(self, agent):
        agent.q_table[4, 4] = [-1.0, 2.5, -3.0, 1.0]
        assert agent.get_max_q((4, 4)) == 2.5


class TestAlgorithmName:
    def test_returns_string(self, agent):
        assert isinstance(agent.algorithm_name, str)

    def test_not_empty(self, agent):
        assert agent.algorithm_name

    def test_bellman_algorithm_name(self, agent):
        assert agent.algorithm_name == "Bellman"
