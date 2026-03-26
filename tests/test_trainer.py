"""Tests for the Trainer module."""

import pytest

from src.agent import Agent
from src.config_loader import Config, load_config
from src.environment import Environment
from src.trainer import Trainer

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


@pytest.fixture
def env(config):
    return Environment(config)


@pytest.fixture
def agent(config):
    return Agent(config)


@pytest.fixture
def trainer(agent, env, config):
    return Trainer(agent, env, config)


class TestRunEpisode:
    def test_returns_tuple(self, trainer):
        result = trainer.run_episode()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_return_types(self, trainer):
        reward, steps, goal = trainer.run_episode()
        assert isinstance(reward, float)
        assert isinstance(steps, int)
        assert isinstance(goal, bool)


class TestEpisodeCount:
    def test_starts_at_zero(self, trainer):
        assert trainer.episode_count == 0

    def test_increments(self, trainer):
        trainer.run_episode()
        assert trainer.episode_count == 1
        trainer.run_episode()
        assert trainer.episode_count == 2


class TestGoalRate:
    def test_zero_when_no_episodes(self, trainer):
        assert trainer.goal_rate == 0.0

    def test_goal_rate_after_episodes(self, trainer):
        # Run some episodes; rate must be between 0 and 1
        for _ in range(5):
            trainer.run_episode()
        assert 0.0 <= trainer.goal_rate <= 1.0


class TestRewardHistory:
    def test_empty_initially(self, trainer):
        assert trainer.reward_history == []

    def test_grows_with_episodes(self, trainer):
        trainer.run_episode()
        trainer.run_episode()
        assert len(trainer.reward_history) == 2

    def test_values_are_floats(self, trainer):
        trainer.run_episode()
        assert isinstance(trainer.reward_history[0], float)


class TestGetMetrics:
    def test_keys(self, trainer):
        trainer.run_episode()
        m = trainer.get_metrics()
        expected_keys = {
            "episode_count",
            "goal_rate",
            "total_goals",
            "epsilon",
            "avg_reward",
            "last_reward",
            "avg_steps",
        }
        assert set(m.keys()) == expected_keys

    def test_metrics_before_training(self, trainer):
        m = trainer.get_metrics()
        assert m["episode_count"] == 0
        assert m["avg_reward"] == 0.0
        assert m["last_reward"] == 0.0

    def test_episode_count_matches(self, trainer):
        for _ in range(3):
            trainer.run_episode()
        m = trainer.get_metrics()
        assert m["episode_count"] == 3

    def test_epsilon_decreases(self, trainer):
        initial_eps = trainer.agent.epsilon
        trainer.run_episode()
        m = trainer.get_metrics()
        assert m["epsilon"] < initial_eps
