"""Tests for renderer and overlays."""

import numpy as np

from src.environment import CellType
from src.overlays import Overlays
from src.renderer import Renderer


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


def test_overlays_draw_heatmap_arrows_labels_and_trail(ui_config, ui_surface):
    overlays = Overlays(ui_config)
    q_table = np.zeros((ui_config.environment.grid_rows, ui_config.environment.grid_cols, 4))
    q_table[0, 0] = [1.0, 2.0, 3.0, 4.0]
    q_table[0, 1] = [4.0, 3.0, 2.0, 1.0]
    q_table[1, 0] = [0.0, 5.0, 1.0, 2.0]
    q_table[1, 1] = [0.0, 0.0, 6.0, 1.0]

    grid = np.zeros((ui_config.environment.grid_rows, ui_config.environment.grid_cols), dtype=int)
    grid[0, 2] = CellType.BUILDING
    grid[0, 3] = CellType.TRAP
    grid[0, 4] = CellType.GOAL

    overlays.draw_heatmap(ui_surface, q_table, grid)
    overlays.draw_arrows(ui_surface, q_table, grid)
    overlays.draw_labels(ui_surface)
    overlays.draw_trail(ui_surface, [(0, 0), (0, 1), (1, 1)])

    assert overlays._heat_color(0.0) != overlays._heat_color(1.0)


def test_overlays_handle_empty_trail_and_all_skipped_heatmap(ui_config, ui_surface):
    overlays = Overlays(ui_config)
    q_table = np.zeros((ui_config.environment.grid_rows, ui_config.environment.grid_cols, 4))
    grid = np.full((ui_config.environment.grid_rows, ui_config.environment.grid_cols), CellType.GOAL)

    overlays.draw_heatmap(ui_surface, q_table, grid)
    overlays.draw_trail(ui_surface, [(0, 0)])
