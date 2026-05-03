"""Tests for ``dronerl.dashboard.Dashboard`` (right-side metrics panel)."""

from dronerl.dashboard import Dashboard


def test_dashboard_draw_handles_empty_and_populated_history(ui_config, ui_surface):
    dashboard = Dashboard(ui_config)
    dashboard.draw(
        ui_surface,
        {"episode": 0, "total_reward": 0.0, "epsilon": 1.0, "steps": 0, "goal_rate": 0.0},
        [],
        {},
    )

    history = [-5.0, 10.0, 3.0, -1.0]
    state = {"converged": True, "demo_mode": False, "paused": True}
    metrics = {"episode": 4, "total_reward": 3.0, "epsilon": 0.1, "steps": 7, "goal_rate": 75.0}
    dashboard.draw(ui_surface, metrics, history, state)

    # Pass-7 §6 — assert structural fact instead of `is not None` stub.
    assert dashboard.font.get_height() > 0
    assert dashboard.title_font.get_height() > dashboard.font.get_height()
    assert dashboard.small_font.get_height() < dashboard.font.get_height()


def test_dashboard_legend_contains_pit_with_config_color(ui_config):
    """Dashboard legend exposes a 'Pit' entry keyed to the PIT config color."""
    dashboard = Dashboard(ui_config)
    assert "Pit" in dashboard.cell_colors
    assert dashboard.cell_colors["Pit"] == tuple(ui_config.colors.pit)
