"""Tests for GUI action dispatch."""

from dronerl.actions import dispatch
from dronerl.gui import GUI


def test_primary_action_maps_all_main_states(pygame_ready, ui_config):
    gui = GUI(ui_config)

    dispatch(gui, "primary")
    assert gui.editor.active is False
    assert gui.paused is False
    assert gui.fast_mode is True

    gui.logic.demo_mode = True
    dispatch(gui, "primary")
    assert gui.logic.demo_mode is False
    assert gui.paused is True

    dispatch(gui, "primary")
    assert gui.paused is False

    dispatch(gui, "primary")
    assert gui.paused is True


def test_toggle_actions_editor_and_demo_controls(pygame_ready, ui_config):
    gui = GUI(ui_config)
    gui.editor.active = False
    gui.paused = False

    dispatch(gui, "toggle_fast")
    dispatch(gui, "toggle_heatmap")
    dispatch(gui, "toggle_arrows")
    dispatch(gui, "open_editor")

    assert gui.fast_mode is True
    assert gui.show_heatmap is True
    assert gui.show_arrows is True
    assert gui.editor.active is True
    assert gui.paused is True

    current_type = gui.editor.selected_type
    dispatch(gui, "cycle_type")
    assert gui.editor.selected_type != current_type

    dispatch(gui, "start_demo")
    assert gui.logic.demo_mode is False
    gui.logic.episode = 3
    dispatch(gui, "start_demo")
    assert gui.logic.demo_mode is True

    dispatch(gui, "continue_training")
    assert gui.logic.demo_mode is False
    assert gui.paused is False
    assert gui.fast_mode is True


def test_save_load_and_reset_paths(pygame_ready, ui_config, tmp_path):
    gui = GUI(ui_config)
    gui.brain_path = str(tmp_path / "brain.npy")
    gui.editor.active = False

    gui.agent.q_table[0, 0, 0] = 12.5
    dispatch(gui, "save")
    gui.agent.q_table[0, 0, 0] = 0.0
    dispatch(gui, "load")
    assert gui.agent.q_table[0, 0, 0] == 12.5

    old_agent = gui.agent
    old_env = gui.env
    dispatch(gui, "reset")
    assert gui.agent is not old_agent
    assert gui.env is not old_env
    assert gui.paused is True
    assert gui.editor.active is True
    assert gui.fast_mode is False
    assert gui.show_heatmap is False
    assert gui.show_arrows is False


def test_load_without_file_is_a_no_op(pygame_ready, ui_config, tmp_path):
    gui = GUI(ui_config)
    gui.brain_path = str(tmp_path / "missing.npy")
    snapshot = gui.agent.q_table.copy()

    dispatch(gui, "load")

    assert (gui.agent.q_table == snapshot).all()


def test_use_q_learning_switches_algorithm(pygame_ready, ui_config):
    gui = GUI(ui_config)
    dispatch(gui, "use_q_learning")
    assert gui.cfg.algorithm.name == "q_learning"
    assert gui.agent.algorithm_name == "Q-Learning"


def test_use_double_q_switches_algorithm(pygame_ready, ui_config):
    gui = GUI(ui_config)
    dispatch(gui, "use_double_q")
    assert gui.cfg.algorithm.name == "double_q"
    assert gui.agent.algorithm_name == "Double Q-Learning"


def test_use_bellman_switches_back(pygame_ready, ui_config):
    gui = GUI(ui_config)
    dispatch(gui, "use_q_learning")
    dispatch(gui, "use_bellman")
    assert gui.cfg.algorithm.name == "bellman"
    assert gui.agent.algorithm_name == "Bellman"


def test_regenerate_hazards_modifies_grid(pygame_ready, ui_config):
    gui = GUI(ui_config)
    gui.hazards.set_density(0.3)
    gui.hazards.set_difficulty(1.0)
    before = gui.env.grid.copy()
    dispatch(gui, "regenerate_hazards")
    assert (gui.env.grid != before).any()
