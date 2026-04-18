"""Tests for dashboard, button panel, and editor UI components."""

import pygame

from src.buttons import Button, ButtonPanel, _brighten, _get_buttons, _overlay_btns
from src.dashboard import Dashboard
from src.editor import EDITABLE_TYPES, TYPE_NAMES, Editor
from src.environment import CellType


def test_button_helpers_cover_all_state_variants():
    assert _brighten((250, 5, 5), 10) == (255, 15, 15)
    assert [btn.label for btn in _overlay_btns(True, False)] == ["Heatmap: ON", "Arrows: OFF"]

    states = [
        {"editor_active": False, "demo_mode": False, "paused": True, "converged": True,
         "fast_mode": False, "show_heatmap": False, "show_arrows": False, "has_trained": True},
        {"editor_active": False, "demo_mode": True, "paused": True, "converged": False,
         "fast_mode": False, "show_heatmap": False, "show_arrows": False, "has_trained": True},
        {"editor_active": True, "demo_mode": False, "paused": True, "converged": False,
         "fast_mode": False, "show_heatmap": True, "show_arrows": True, "has_trained": False},
        {"editor_active": False, "demo_mode": False, "paused": True, "converged": False,
         "fast_mode": True, "show_heatmap": False, "show_arrows": True, "has_trained": True},
        {"editor_active": False, "demo_mode": False, "paused": False, "converged": False,
         "fast_mode": True, "show_heatmap": True, "show_arrows": False, "has_trained": True},
    ]

    demo_c, primary_c = (40, 120, 180), (45, 110, 65)
    assert all(_get_buttons(state, demo_c, primary_c) for state in states)


def test_button_panel_draw_hover_click_and_custom_button(ui_config, ui_surface):
    panel = ButtonPanel(ui_config)
    state = {
        "editor_active": False, "demo_mode": False, "paused": True, "converged": False,
        "fast_mode": False, "show_heatmap": False, "show_arrows": False, "has_trained": True,
    }
    end_y = panel.draw(ui_surface, state, 20)
    assert end_y > 20
    assert panel.handle_click(panel.buttons[0].rect.center) == "resume"

    panel.handle_hover(panel.buttons[0].rect.center)
    assert panel.buttons[0].hovered is True

    font = pygame.font.SysFont("arial", 14)
    custom = Button("Accent", "noop", color=(10, 20, 30))
    custom.rect = pygame.Rect(10, 10, 100, 30)
    custom.draw(ui_surface, font, panel.colors)


def test_persistent_algo_and_control_buttons_appear_in_active_states(ui_config, ui_surface):
    """Algorithm selector + Compare + Regen Hazards show in paused/running/converged states."""
    panel = ButtonPanel(ui_config)
    state = {
        "editor_active": False, "demo_mode": False, "paused": True, "converged": False,
        "fast_mode": False, "show_heatmap": False, "show_arrows": False, "has_trained": True,
        "algo_name": "Q-Learning",
    }
    panel.draw(ui_surface, state, 20)
    actions = [b.action for b in panel.buttons]
    for expected in ("use_bellman", "use_q_learning", "use_double_q",
                     "run_comparison", "regenerate_hazards"):
        assert expected in actions

    q_btn = next(b for b in panel.buttons if b.action == "use_q_learning")
    bellman_btn = next(b for b in panel.buttons if b.action == "use_bellman")
    assert q_btn.primary is True
    assert bellman_btn.primary is False


def test_persistent_buttons_shown_in_editor_and_hidden_in_demo(ui_config, ui_surface):
    """Algo/Compare/Regen buttons visible in editor (choose before train), hidden in demo."""
    panel = ButtonPanel(ui_config)
    editor_state = {
        "editor_active": True, "demo_mode": False, "paused": True, "converged": False,
        "fast_mode": False, "show_heatmap": False, "show_arrows": False, "has_trained": False,
        "algo_name": "Bellman",
    }
    panel.draw(ui_surface, editor_state, 20)
    assert "use_q_learning" in [b.action for b in panel.buttons]

    demo_state = dict(editor_state, editor_active=False, demo_mode=True)
    panel.draw(ui_surface, demo_state, 20)
    assert "run_comparison" not in [b.action for b in panel.buttons]


def test_editor_draw_and_click_flow(ui_config, ui_surface):
    editor = Editor(ui_config)
    editor.draw_ui(ui_surface, (10, 10))
    assert editor.btn_rects
    assert editor.handle_click((10, 10)) == (0, 0, editor.selected_type)

    rect, index = editor.btn_rects[-1]
    editor.handle_click(rect.center)
    assert editor.selected_type == EDITABLE_TYPES[index]

    current = editor.selected_type
    editor.next_type()
    assert editor.selected_type != current
    assert editor.handle_click((9999, 9999)) is None


def test_editor_pit_metadata_and_placement_tracking(ui_config, ui_env):
    """PIT is editable, has a label and color, cycles in rotation, and tracks in _editor_cells."""
    editor = Editor(ui_config)
    assert CellType.PIT in EDITABLE_TYPES
    assert TYPE_NAMES[CellType.PIT] == "Pit"
    assert CellType.PIT in editor.type_colors
    assert editor.type_colors[CellType.PIT] == tuple(ui_config.colors.pit)

    # Cycling eventually hits PIT.
    seen = set()
    for _ in range(len(EDITABLE_TYPES)):
        seen.add(editor.selected_type)
        editor.next_type()
    assert CellType.PIT in seen

    # Placing PIT via environment.set_cell tracks it in _editor_cells.
    ui_env.set_cell(0, 1, CellType.PIT, editor=True)
    assert (0, 1) in ui_env._editor_cells
    assert int(ui_env.grid[0, 1]) == int(CellType.PIT)


def test_editor_draws_pit_button_with_pit_color(ui_config, ui_surface):
    """draw_ui renders a button for the PIT type using its config color."""
    editor = Editor(ui_config)
    editor.draw_ui(ui_surface, (0, 0))
    assert editor.btn_rects
    pit_idx = EDITABLE_TYPES.index(CellType.PIT)
    # The PIT button rect exists at its index.
    indexes = [idx for _rect, idx in editor.btn_rects]
    assert pit_idx in indexes
    assert editor.type_colors[CellType.PIT] == tuple(ui_config.colors.pit)


def test_dashboard_draw_handles_empty_and_populated_history(ui_config, ui_surface):
    dashboard = Dashboard(ui_config)
    dashboard.draw(ui_surface, {"episode": 0, "total_reward": 0.0, "epsilon": 1.0, "steps": 0, "goal_rate": 0.0}, [], {})

    history = [-5.0, 10.0, 3.0, -1.0]
    state = {"converged": True, "demo_mode": False, "paused": True}
    metrics = {"episode": 4, "total_reward": 3.0, "epsilon": 0.1, "steps": 7, "goal_rate": 75.0}
    dashboard.draw(ui_surface, metrics, history, state)

    assert dashboard.font is not None
    assert dashboard.title_font is not None
    assert dashboard.small_font is not None


def test_dashboard_legend_contains_pit_with_config_color(ui_config):
    """Dashboard legend exposes a 'Pit' entry keyed to the PIT config color."""
    dashboard = Dashboard(ui_config)
    assert "Pit" in dashboard.cell_colors
    assert dashboard.cell_colors["Pit"] == tuple(ui_config.colors.pit)
