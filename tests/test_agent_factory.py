"""Tests for the agent factory."""

import pytest

from src.agent import BellmanAgent
from src.agent_factory import create_agent
from src.config_loader import Config, load_config
from src.double_q_agent import DoubleQAgent
from src.q_agent import QLearningAgent

CONFIG_PATH = "config/config.yaml"


def _make_config(algorithm_name: str) -> Config:
    raw = load_config(CONFIG_PATH)
    raw["algorithm"] = {"name": algorithm_name}
    return Config(raw)


def test_factory_creates_bellman():
    agent = create_agent(_make_config("bellman"))
    assert isinstance(agent, BellmanAgent)
    assert agent.algorithm_name == "Bellman"


def test_factory_creates_q_learning():
    agent = create_agent(_make_config("q_learning"))
    assert isinstance(agent, QLearningAgent)
    assert agent.algorithm_name == "Q-Learning"


def test_factory_creates_double_q():
    agent = create_agent(_make_config("double_q"))
    assert isinstance(agent, DoubleQAgent)
    assert agent.algorithm_name == "Double Q-Learning"


def test_factory_unknown_raises():
    with pytest.raises(ValueError, match="Unknown algorithm"):
        create_agent(_make_config("nonexistent"))


def test_factory_error_lists_valid_algorithms():
    with pytest.raises(ValueError, match="bellman.*double_q.*q_learning"):
        create_agent(_make_config("bad"))
