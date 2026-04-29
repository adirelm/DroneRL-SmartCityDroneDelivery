"""Tests for ``dronerl.renderer.Renderer``."""

import numpy as np

from dronerl.environment import CellType
from dronerl.renderer import Renderer


def test_renderer_draws_all_cell_types_drone_and_grid(ui_config, ui_surface):
    renderer = Renderer(ui_config)
    grid = np.zeros((ui_config.environment.grid_rows, ui_config.environment.grid_cols), dtype=int)
    grid[0, 1] = CellType.BUILDING
    grid[0, 2] = CellType.TRAP
    grid[0, 3] = CellType.GOAL
    grid[0, 4] = CellType.WIND

    renderer.draw_grid(ui_surface, grid)
    renderer.draw_drone(ui_surface, (1, 1))
    renderer.draw_grid_lines(ui_surface)

    assert renderer.frame == 1


def test_renderer_draws_pit_cells_with_config_colors(ui_config, ui_surface):
    """Cover _draw_pit directly and via draw_grid for the PIT cell type."""
    renderer = Renderer(ui_config)
    expected_pit = tuple(ui_config.colors.pit)
    expected_accent = tuple(ui_config.colors.pit_accent)
    # Colors on renderer come from config (no hardcoded RGB in _draw_pit).
    assert renderer.c_pit == expected_pit
    assert renderer.c_pit_acc == expected_accent

    # Direct _draw_pit call at explicit (x, y) paints the pit color on surface.
    renderer._draw_pit(ui_surface, 0, 0)
    assert tuple(ui_surface.get_at((2, 2)))[:3] == expected_pit

    # draw_grid dispatches PIT to _draw_pit without raising.
    grid = np.zeros((ui_config.environment.grid_rows, ui_config.environment.grid_cols), dtype=int)
    grid[0, 0] = CellType.PIT
    grid[1, 1] = CellType.BUILDING
    grid[2, 2] = CellType.TRAP
    renderer.draw_grid(ui_surface, grid)


def test_renderer_pit_visually_distinct_from_trap_and_building(ui_config, ui_surface):
    """PIT uses different base color than TRAP and BUILDING so it's distinguishable."""
    renderer = Renderer(ui_config)
    assert renderer.c_pit != renderer.c_trap
    assert renderer.c_pit != renderer.c_building


def test_renderer_draws_all_six_cell_types_including_pit(ui_config, ui_surface):
    """draw_grid handles grids that include every CellType (EMPTY..PIT)."""
    renderer = Renderer(ui_config)
    grid = np.zeros((ui_config.environment.grid_rows, ui_config.environment.grid_cols), dtype=int)
    grid[0, 0] = CellType.EMPTY
    grid[0, 1] = CellType.BUILDING
    grid[0, 2] = CellType.TRAP
    grid[0, 3] = CellType.GOAL
    grid[0, 4] = CellType.WIND
    grid[0, 5] = CellType.PIT
    renderer.draw_grid(ui_surface, grid)
    assert renderer.frame >= 1
