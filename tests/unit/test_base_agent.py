"""Tests for the BaseAgent class (core behaviour)."""

import numpy as np
import pytest

from dronerl.agent import BellmanAgent
from dronerl.base_agent import BaseAgent
from dronerl.config_loader import Config, load_config

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


def test_load_missing_path_is_noop(agent, tmp_path):
    """§13.5 / Reliability: load() on a missing path must not crash."""
    before = agent.q_table.copy()
    agent.load(str(tmp_path / "does_not_exist.npy"))
    np.testing.assert_array_equal(agent.q_table, before)


class TestValidateConfig:
    """§16.3 — _validate_config must reject malformed Setup data with clear messages."""

    def _broken(self, config, **overrides):
        # Build an agent post-mutation by tweaking the env/agent sub-config in place.
        for path, value in overrides.items():
            sub, attr = path.split(".")
            setattr(getattr(config, sub), attr, value)

    def test_rejects_zero_grid(self, config):
        config.environment.grid_rows = 0
        with pytest.raises(ValueError, match="grid dimensions"):
            BaseAgent(config)

    def test_rejects_gamma_out_of_range(self, config):
        config.agent.discount_factor = 1.5
        with pytest.raises(ValueError, match="discount_factor"):
            BaseAgent(config)

    def test_rejects_inverted_epsilon(self, config):
        config.agent.epsilon_start = 0.1
        config.agent.epsilon_end = 0.5
        with pytest.raises(ValueError, match="epsilon range invalid"):
            BaseAgent(config)

    def test_rejects_zero_epsilon_decay(self, config):
        config.agent.epsilon_decay = 0.0
        with pytest.raises(ValueError, match="epsilon_decay"):
            BaseAgent(config)


class TestTdUpdate:
    """§6.3 — direct edge-case tests for the shared TD-update helper."""

    def test_done_true_ignores_next_state(self, agent):
        """Terminal step: target = reward (no bootstrap from next_state)."""
        agent.q_table[1, 1, 0] = 99.0  # next_state Q value that should be ignored
        agent.q_table[0, 0, 0] = 0.0
        agent._td_update(agent.q_table, (0, 0), 0, 10.0, (1, 1), done=True, step=1.0)
        # target = 10.0 + γ·0 = 10.0; q[0,0,0] += 1.0 · (10 - 0) = 10.0
        assert agent.q_table[0, 0, 0] == 10.0

    def test_done_false_bootstraps_next_state(self, agent):
        """Non-terminal step: target includes γ · max Q(next_state)."""
        agent.q_table[:] = 0.0
        agent.q_table[1, 1, 2] = 5.0  # max Q at next_state
        agent.q_table[0, 0, 0] = 0.0
        agent._td_update(agent.q_table, (0, 0), 0, 1.0, (1, 1), done=False, step=1.0)
        # target = 1.0 + γ·5.0 = 1.0 + γ·5; q[0,0,0] += 1.0 · target
        expected = 1.0 + agent.gamma * 5.0
        assert abs(agent.q_table[0, 0, 0] - expected) < 1e-9

    def test_step_size_scales_update(self, agent):
        """Step size (α or lr) scales the TD error."""
        agent.q_table[:] = 0.0
        agent._td_update(agent.q_table, (0, 0), 1, 10.0, (1, 1), done=True, step=0.1)
        # 10% of TD error = 0.1 · 10 = 1.0
        assert abs(agent.q_table[0, 0, 1] - 1.0) < 1e-9
