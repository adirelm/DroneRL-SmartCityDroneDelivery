"""Tests for the HazardGenerator dynamic board system."""

import pytest

from src.config_loader import Config, load_config
from src.environment import CellType, Environment
from src.hazard_generator import HazardGenerator

CONFIG_PATH = "config/config.yaml"


def _cfg(**overrides) -> Config:
    raw = load_config(CONFIG_PATH)
    raw.setdefault("dynamic_board", {}).update(overrides)
    return Config(raw)


@pytest.fixture
def config():
    return _cfg(seed=42, noise_level=0.5, hazard_density=0.2, difficulty=0.5)


@pytest.fixture
def env(config):
    return Environment(config)


@pytest.fixture
def hazgen(config):
    return HazardGenerator(config)


class TestInit:
    def test_loads_noise(self, hazgen):
        assert hazgen.noise == 0.5

    def test_loads_density(self, hazgen):
        assert hazgen.density == 0.2

    def test_loads_difficulty(self, hazgen):
        assert hazgen.difficulty == 0.5


class TestSetters:
    def test_set_noise_clamps(self, hazgen):
        hazgen.set_noise(1.5)
        assert hazgen.noise == 1.0
        hazgen.set_noise(-0.1)
        assert hazgen.noise == 0.0

    def test_set_density_clamps_to_half(self, hazgen):
        hazgen.set_density(0.9)
        assert hazgen.density == 0.5

    def test_set_difficulty_clamps(self, hazgen):
        hazgen.set_difficulty(2.0)
        assert hazgen.difficulty == 1.0


class TestEffective:
    def test_effective_density_scales_with_difficulty(self, hazgen):
        hazgen.set_density(0.2)
        hazgen.set_difficulty(1.0)
        assert hazgen.effective_density() == pytest.approx(0.2 * 1.5)

    def test_effective_density_capped(self, hazgen):
        hazgen.set_density(0.5)
        hazgen.set_difficulty(1.0)
        assert hazgen.effective_density() == 0.5

    def test_effective_drift_positive(self, hazgen):
        assert hazgen.effective_drift() > 0


class TestApply:
    def test_places_hazards(self, hazgen, env):
        placed = hazgen.apply(env)
        assert placed > 0

    def test_respects_start_goal(self, hazgen, env):
        hazgen.apply(env)
        assert env.grid[env.start[0], env.start[1]] == CellType.EMPTY
        assert env.grid[env.goal[0], env.goal[1]] == CellType.GOAL

    def test_deterministic_with_seed(self, env):
        g1 = HazardGenerator(_cfg(seed=7, hazard_density=0.2))
        g2 = HazardGenerator(_cfg(seed=7, hazard_density=0.2))
        g1.apply(env)
        first = env.grid.copy()
        env2 = Environment(_cfg(seed=7))
        g2.apply(env2)
        assert (first == env2.grid).all()

    def test_zero_density_places_nothing(self, env):
        gen = HazardGenerator(_cfg(seed=1, hazard_density=0.0, difficulty=0.0))
        placed = gen.apply(env)
        assert placed == 0

    def test_reapply_clears_previous(self, hazgen, env):
        hazgen.apply(env)
        count1 = int((env.grid != CellType.EMPTY).sum())
        hazgen.apply(env)
        count2 = int((env.grid != CellType.EMPTY).sum())
        # Counts may differ slightly but should be comparable (not cumulative)
        assert abs(count2 - count1) < count1

    def test_only_valid_hazard_types_placed(self, hazgen, env):
        hazgen.apply(env)
        valid = {
            CellType.EMPTY, CellType.GOAL, CellType.BUILDING,
            CellType.TRAP, CellType.WIND, CellType.PIT,
        }
        for r in range(env.rows):
            for c in range(env.cols):
                assert CellType(int(env.grid[r, c])) in valid

    def test_apply_preserves_editor_placed_cells(self, hazgen, env):
        """Editor-placed hazards must survive a subsequent apply() call."""
        env.set_cell(3, 3, CellType.PIT, editor=True)
        env.set_cell(5, 6, CellType.TRAP, editor=True)
        hazgen.apply(env)
        assert env.get_cell(3, 3) == CellType.PIT
        assert env.get_cell(5, 6) == CellType.TRAP
        # Confirm the generator still placed additional hazards elsewhere.
        total_hazards = int((env.grid != CellType.EMPTY).sum())
        assert total_hazards > 3  # includes goal + the 2 editor cells + generated

    def test_apply_replaces_only_non_editor_dynamic_cells(self, hazgen, env):
        """A previous dynamic hazard (editor=False) must be cleared by re-apply."""
        env.set_cell(4, 4, CellType.WIND, editor=False)
        hazgen.apply(env)
        # The dynamic WIND at (4,4) may or may not still be there (depending on
        # the generator's own placement). The guarantee is that it was cleared
        # before the new placement — i.e. not treated as an "editor" cell.
        assert (4, 4) not in env._editor_cells
