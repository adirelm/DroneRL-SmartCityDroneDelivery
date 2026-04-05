"""Tests for dashboard, button panel, and editor UI components."""

import pygame

from src.buttons import Button, ButtonPanel, _brighten, _get_buttons, _overlay_btns
from src.dashboard import Dashboard
from src.editor import EDITABLE_TYPES, Editor


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
