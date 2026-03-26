"""Action dispatch for DroneRL GUI — maps action strings to state changes."""

import os


def dispatch(gui, a):
    """Execute the named action, mutating gui state accordingly."""
    if a == "primary":
        if gui.editor.active:
            a = "start_training"
        elif gui.logic.demo_mode:
            a = "stop_demo"
        elif gui.paused:
            a = "resume"
        else:
            a = "pause"

    if a == "start_training":
        gui.editor.active, gui.paused = False, False
        gui.fast_mode = True
    elif a == "pause":
        gui.paused = True
    elif a == "resume":
        gui.paused = False
    elif a == "stop_demo":
        gui.logic.exit_demo()
        gui.paused = True
    elif a == "continue_training":
        gui.logic.exit_demo()
        gui.paused, gui.fast_mode = False, True
    elif a == "start_demo":
        if gui.logic.episode > 0:
            gui.logic.enter_demo()
    elif a == "toggle_fast":
        gui.fast_mode = not gui.fast_mode
    elif a == "toggle_heatmap":
        gui.show_heatmap = not gui.show_heatmap
    elif a == "toggle_arrows":
        gui.show_arrows = not gui.show_arrows
    elif a == "open_editor":
        gui.editor.active = True
        gui.paused = True
        gui.logic.exit_demo()
    elif a == "save":
        gui.agent.save(gui.BRAIN_PATH)
    elif a == "load" and os.path.exists(gui.BRAIN_PATH):
        gui.agent.load(gui.BRAIN_PATH)
    elif a == "reset":
        from src.agent import Agent
        from src.environment import Environment
        gui.env, gui.agent = Environment(gui.cfg), Agent(gui.cfg)
        gui.logic.reset(gui.agent, gui.env)
        gui.paused = gui.editor.active = True
        gui.fast_mode = gui.show_heatmap = gui.show_arrows = False
    elif a == "cycle_type":
        gui.editor.next_type()
