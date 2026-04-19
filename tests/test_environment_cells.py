"""Tests for Environment cell mutation, editor tracking, and dynamic cell clearing.

Split from test_environment.py to keep each test file under the 150-line cap.
"""

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

    def test_set_cell_does_not_override_start(self, env):
        env.set_cell(0, 0, CellType.TRAP)
        assert env.get_cell(0, 0) == CellType.EMPTY

    def test_set_cell_does_not_override_goal(self, env):
        env.set_cell(11, 11, CellType.TRAP)
        assert env.get_cell(11, 11) == CellType.GOAL

    def test_editor_flag_tracks_user_cells(self, env):
        env.set_cell(3, 3, CellType.TRAP, editor=True)
        assert (3, 3) in env._editor_cells

    def test_editor_flag_false_does_not_track(self, env):
        env.set_cell(3, 3, CellType.TRAP, editor=False)
        assert (3, 3) not in env._editor_cells

    def test_set_cell_empty_removes_from_editor_set(self, env):
        env.set_cell(2, 2, CellType.TRAP, editor=True)
        env.set_cell(2, 2, CellType.EMPTY, editor=True)
        assert (2, 2) not in env._editor_cells

    def test_set_wind_drift_clamps(self, env):
        env.set_wind_drift(1.5)
        assert env.drift_probability == 1.0
        env.set_wind_drift(-0.1)
        assert env.drift_probability == 0.0

    def test_clear_dynamic_cells_preserves_editor(self, env):
        env.set_cell(3, 3, CellType.TRAP, editor=True)
        env.set_cell(4, 4, CellType.WIND, editor=False)
        env.clear_dynamic_cells()
        assert env.get_cell(3, 3) == CellType.TRAP
        assert env.get_cell(4, 4) == CellType.EMPTY
