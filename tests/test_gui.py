"""Tests for top-level GUI orchestration."""

import pygame

from src.environment import CellType
from src.gui import GUI


def test_gui_state_key_and_click_handlers(pygame_ready, ui_config, monkeypatch):
    gui = GUI(ui_config)
    actions = []
    monkeypatch.setattr("src.gui.dispatch", lambda current_gui, action: actions.append(action))

    gui._on_key(pygame.K_h)
    assert actions == ["toggle_heatmap"]

    gui.dashboard.buttons.handle_click = lambda pos: "resume"
    gui._on_click((5, 5))
    assert actions[-1] == "resume"

    gui.editor.active = True
    gui.dashboard.buttons.handle_click = lambda pos: None
    gui.editor.handle_click = lambda pos: (1, 1, CellType.TRAP)
    gui._on_click((10, 10))
    assert gui.env.get_cell(1, 1) == CellType.TRAP

    state = gui._state()
    assert {"paused", "fast_mode", "show_heatmap", "show_arrows", "editor_active"} <= set(state)


def test_gui_run_covers_demo_branch_and_quit(pygame_ready, ui_config, monkeypatch):
    gui = GUI(ui_config)
    gui.logic.demo_mode = True
    called = {"demo": 0}
    monkeypatch.setattr(gui.logic, "demo_step", lambda fps: called.__setitem__("demo", called["demo"] + 1))
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])

    gui.run()

    assert called["demo"] == 1


def test_gui_run_training_branch_sets_convergence_flags(pygame_ready, ui_config, monkeypatch):
    gui = GUI(ui_config)
    gui.editor.active = False
    gui.paused = False
    gui.fast_mode = True
    calls = {"steps": 0}

    monkeypatch.setattr(gui.logic, "training_step", lambda: calls.__setitem__("steps", calls["steps"] + 1))
    monkeypatch.setattr(gui.logic, "check_convergence", lambda: True)
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])
    monkeypatch.setattr(gui, "_draw", lambda: None)

    gui.run()

    assert calls["steps"] == gui.fast_step_batch
    assert gui.paused is True
    assert gui.show_heatmap is True
    assert gui.show_arrows is True


def test_gui_draw_and_status_bar_render_without_errors(pygame_ready, ui_config):
    gui = GUI(ui_config)
    gui.show_heatmap = True
    gui.show_arrows = True
    gui.logic.demo_mode = True
    gui.logic.demo_trail = [(0, 0), (0, 1)]

    gui._draw()
    gui._status_bar()

    assert gui.status_font is not None
