"""Tests for ``dronerl.overlays.Overlays``."""

import numpy as np

from dronerl.environment import CellType
from dronerl.overlays import _SKIP_HEAT, Overlays


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


def test_overlays_skip_pit_in_heatmap_and_arrows(ui_config, ui_surface):
    """PIT cells are skipped by both heatmap and arrow overlays; PIT is in _SKIP_HEAT."""
    assert CellType.PIT in _SKIP_HEAT

    overlays = Overlays(ui_config)
    rows = ui_config.environment.grid_rows
    cols = ui_config.environment.grid_cols
    q_table = np.ones((rows, cols, 4))
    # PIT everywhere - heatmap should early-return without error.
    pit_grid = np.full((rows, cols), CellType.PIT)
    overlays.draw_heatmap(ui_surface, q_table, pit_grid)
    overlays.draw_arrows(ui_surface, q_table, pit_grid)

    # Mixed grid with some PIT cells should also render without crashing.
    mixed_grid = np.zeros((rows, cols), dtype=int)
    mixed_grid[0, 0] = CellType.PIT
    mixed_grid[1, 1] = CellType.PIT
    mixed_grid[2, 2] = CellType.TRAP
    overlays.draw_heatmap(ui_surface, q_table, mixed_grid)
    overlays.draw_arrows(ui_surface, q_table, mixed_grid)
