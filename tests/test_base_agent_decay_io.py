"""Decay-epsilon and save/load tests for BaseAgent shared behaviour."""

import numpy as np
import pytest

from src.agent import BellmanAgent
from src.config_loader import Config, load_config

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


@pytest.fixture
def agent(config):
    return BellmanAgent(config)


class TestDecayEpsilon:
    def test_epsilon_decreases(self, agent):
        before = agent.epsilon
        agent.decay_epsilon()
        assert agent.epsilon < before

    def test_epsilon_end_is_floor(self, agent):
        agent.epsilon = 0.005
        agent.decay_epsilon()
        assert agent.epsilon == agent.epsilon_end

    def test_multiplicative(self, agent):
        agent.epsilon = 1.0
        agent.epsilon_decay = 0.5
        agent.epsilon_end = 0.0
        agent.decay_epsilon()
        assert agent.epsilon == pytest.approx(0.5)

    def test_reaches_floor_after_many(self, agent):
        for _ in range(10_000):
            agent.decay_epsilon()
        assert agent.epsilon == agent.epsilon_end

    def test_stays_at_floor(self, agent):
        agent.epsilon = agent.epsilon_end
        agent.decay_epsilon()
        assert agent.epsilon == agent.epsilon_end


class TestSaveLoad:
    def test_save_creates_file(self, agent, tmp_path):
        path = tmp_path / "q.npy"
        agent.save(str(path))
        assert path.exists()

    def test_save_writes_data(self, agent, tmp_path):
        agent.q_table[1, 2, 3] = 4.2
        path = str(tmp_path / "q.npy")
        agent.save(path)
        loaded = np.load(path)
        assert loaded[1, 2, 3] == 4.2

    def test_load_restores_data(self, agent, tmp_path):
        agent.q_table[5, 5, 0] = 9.9
        path = str(tmp_path / "q.npy")
        agent.save(path)
        agent.q_table[5, 5, 0] = 0.0
        agent.load(path)
        assert agent.q_table[5, 5, 0] == 9.9

    def test_round_trip_preserves_all(self, agent, tmp_path):
        rng = np.random.default_rng(0)
        agent.q_table = rng.normal(size=agent.q_table.shape)
        original = agent.q_table.copy()
        path = str(tmp_path / "q.npy")
        agent.save(path)
        agent.q_table = np.zeros_like(original)
        agent.load(path)
        np.testing.assert_array_equal(agent.q_table, original)

    def test_load_nonexistent_raises(self, agent, tmp_path):
        with pytest.raises(FileNotFoundError):
            agent.load(str(tmp_path / "missing.npy"))
