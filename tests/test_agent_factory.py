"""Tests for the agent factory."""

import pytest

from src.agent import BellmanAgent
from src.agent_factory import create_agent
from src.algorithms import ALGORITHMS
from src.base_agent import BaseAgent
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


def test_factory_returns_base_agent_subclass():
    for name in ALGORITHMS:
        agent = create_agent(_make_config(name))
        assert isinstance(agent, BaseAgent)


def test_factory_unknown_raises():
    with pytest.raises(ValueError, match="Unknown algorithm"):
        create_agent(_make_config("nonexistent"))


def test_factory_error_lists_valid_algorithms():
    with pytest.raises(ValueError, match="bellman.*double_q.*q_learning"):
        create_agent(_make_config("bad"))


def test_factory_error_contains_unknown_name():
    with pytest.raises(ValueError, match="foobar"):
        create_agent(_make_config("foobar"))


def test_factory_empty_string_raises():
    with pytest.raises(ValueError, match="Unknown algorithm"):
        create_agent(_make_config(""))


def test_factory_case_sensitive():
    with pytest.raises(ValueError, match="Unknown algorithm"):
        create_agent(_make_config("BELLMAN"))


def test_factory_none_raises():
    with pytest.raises((ValueError, TypeError)):
        create_agent(_make_config(None))


class TestFactoryAgentApi:
    @pytest.fixture(params=list(ALGORITHMS))
    def agent(self, request):
        return create_agent(_make_config(request.param))

    def test_has_q_table(self, agent):
        assert hasattr(agent, "q_table")
        assert agent.q_table.shape == (12, 12, 4)

    def test_has_update(self, agent):
        agent.update((0, 0), 0, -1.0, (0, 1), done=False)

    def test_has_choose_action(self, agent):
        a = agent.choose_action((0, 0))
        assert 0 <= a <= 3

    def test_has_decay_epsilon(self, agent):
        before = agent.epsilon
        agent.decay_epsilon()
        assert agent.epsilon <= before

    def test_save_and_load(self, agent, tmp_path):
        path = str(tmp_path / "q.npy")
        # Seed a nonzero Q-value on the underlying storage
        if hasattr(agent, "q_table_a"):
            agent.q_table_a[0, 0, 0] = 1.5
        else:
            agent.q_table[0, 0, 0] = 1.5
        before = float(agent.q_table[0, 0, 0])
        agent.save(path)
        # Zero out then reload
        if hasattr(agent, "q_table_a"):
            agent.q_table_a[:] = 0.0
            agent.q_table_b[:] = 0.0
        else:
            agent.q_table[0, 0, 0] = 0.0
        agent.load(path)
        assert float(agent.q_table[0, 0, 0]) == before
