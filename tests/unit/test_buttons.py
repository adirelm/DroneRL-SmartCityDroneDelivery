"""Tests for the button panel (state-dependent layout, persistent algo buttons).

Editor and dashboard tests live in tests/unit/test_editor.py and test_dashboard.py to keep each
file under the 150-line project cap.
"""

import pygame

from dronerl.buttons import Button, ButtonPanel, _brighten, _get_buttons, _overlay_btns


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
