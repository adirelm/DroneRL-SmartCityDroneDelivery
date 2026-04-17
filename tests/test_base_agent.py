"""Tests for the BaseAgent abstract class."""

import pytest

from src.base_agent import BaseAgent
from src.config_loader import Config, load_config

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


def test_base_agent_update_raises(config):
    """update() on BaseAgent must raise NotImplementedError."""
    base = BaseAgent(config)
    with pytest.raises(NotImplementedError):
        base.update((0, 0), 0, -1.0, (0, 1), done=False)


def test_base_agent_shared_shape(config):
    base = BaseAgent(config)
    assert base.q_table.shape == (12, 12, 4)


def test_base_agent_epsilon_decay(config):
    base = BaseAgent(config)
    before = base.epsilon
    base.decay_epsilon()
    assert base.epsilon < before


def test_base_agent_choose_action_greedy(config):
    base = BaseAgent(config)
    base.epsilon = 0.0
    base.q_table[0, 0, 2] = 10.0
    assert base.choose_action((0, 0)) == 2


def test_base_agent_algorithm_name(config):
    base = BaseAgent(config)
    assert base.algorithm_name == "Base"
