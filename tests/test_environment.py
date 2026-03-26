"""Tests for the Environment module."""

import pytest

from src.config_loader import Config, load_config
from src.environment import CellType, Environment

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


@pytest.fixture
def env(config):
    return Environment(config)


class TestGridInit:
    def test_grid_shape(self, env):
        assert env.grid.shape == (12, 12)

    def test_goal_cell_set(self, env):
        assert env.grid[11, 11] == CellType.GOAL

    def test_start_position(self, env):
        assert env.drone_pos == (0, 0)


class TestReset:
    def test_reset_returns_start(self, env):
        env.drone_pos = (5, 5)
        pos = env.reset()
        assert pos == (0, 0)

    def test_reset_updates_drone_pos(self, env):
        env.drone_pos = (3, 4)
        env.reset()
        assert env.drone_pos == (0, 0)


class TestStep:
    def test_step_down(self, env):
        state, reward, done, info = env.step(1)  # DOWN
        assert state == (1, 0)
        assert done is False

    def test_step_right(self, env):
        state, reward, done, info = env.step(3)  # RIGHT
        assert state == (0, 1)

    def test_step_up_at_origin_wall(self, env):
        state, reward, done, info = env.step(0)  # UP from (0,0)
        assert state == (0, 0)
        assert reward == -5
        assert info["event"] == "wall_collision"

    def test_step_left_at_origin_wall(self, env):
        state, reward, done, info = env.step(2)  # LEFT from (0,0)
        assert state == (0, 0)
        assert reward == -5

    def test_building_collision(self, env):
        env.set_cell(1, 0, CellType.BUILDING)
        state, reward, done, info = env.step(1)  # DOWN into building
        assert state == (0, 0)
        assert reward == -5
        assert info["event"] == "wall_collision"

    def test_trap_terminates(self, env):
        env.set_cell(1, 0, CellType.TRAP)
        state, reward, done, info = env.step(1)  # DOWN into trap
        assert state == (1, 0)
        assert reward == -50
        assert done is True
        assert info["event"] == "trap"

    def test_goal_terminates(self, env):
        env.drone_pos = (10, 11)
        state, reward, done, info = env.step(1)  # DOWN into goal at (11,11)
        assert state == (11, 11)
        assert reward == 100
        assert done is True
        assert info["event"] == "goal"

    def test_empty_step_penalty(self, env):
        state, reward, done, info = env.step(1)
        assert reward == -1

    def test_bottom_boundary(self, env):
        env.drone_pos = (11, 0)
        state, reward, done, info = env.step(1)  # DOWN past bottom
        assert state == (11, 0)
        assert info["event"] == "wall_collision"


class TestWindZone:
    def test_wind_cell_reward(self, env):
        env.set_cell(1, 0, CellType.WIND)
        env.drone_pos = (2, 0)  # not on wind, move into wind
        state, reward, done, info = env.step(0)  # UP into wind cell
        assert reward == -2

    def test_wind_drift_event(self, env, monkeypatch):
        env.set_cell(0, 0, CellType.WIND)
        # Force drift: random() returns 0.0 < 0.3, randint returns 1 (DOWN)
        monkeypatch.setattr("src.environment.random.random", lambda: 0.0)
        monkeypatch.setattr("src.environment.random.randint", lambda a, b: 1)
        state, reward, done, info = env.step(3)  # intended RIGHT, drifted DOWN
        assert info["event"] == "wind_drift"
        assert state == (1, 0)  # moved DOWN, not RIGHT


class TestSetGetCell:
    def test_set_cell(self, env):
        env.set_cell(5, 5, CellType.BUILDING)
        assert env.grid[5, 5] == CellType.BUILDING

    def test_get_cell(self, env):
        env.set_cell(3, 3, CellType.TRAP)
        assert env.get_cell(3, 3) == CellType.TRAP

    def test_set_cell_out_of_bounds_ignored(self, env):
        env.set_cell(99, 99, CellType.BUILDING)  # should not raise

    def test_get_cell_empty(self, env):
        assert env.get_cell(0, 0) == CellType.EMPTY
