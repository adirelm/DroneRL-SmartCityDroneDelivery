"""Action dispatch for DroneRL GUI — maps action strings to state changes."""

import os

from src.agent_factory import create_agent
from src.environment import Environment

_ALGO_KEYS = {"use_bellman": "bellman",
              "use_q_learning": "q_learning",
              "use_double_q": "double_q"}


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
        gui.agent.save(gui.brain_path)
    elif a == "load" and os.path.exists(gui.brain_path):
        gui.agent.load(gui.brain_path)
    elif a == "reset":
        gui.env, gui.agent = Environment(gui.cfg), create_agent(gui.cfg)
        gui.env.drift_probability = gui.hazards.effective_drift()
        gui.logic.reset(gui.agent, gui.env)
        gui.paused = gui.editor.active = True
        gui.fast_mode = gui.show_heatmap = gui.show_arrows = False
    elif a == "cycle_type":
        gui.editor.next_type()
    elif a in _ALGO_KEYS:
        gui.cfg.algorithm.name = _ALGO_KEYS[a]
        dispatch(gui, "reset")
    elif a == "regenerate_hazards":
        gui.hazards.apply(gui.env)
        gui.env.drift_probability = gui.hazards.effective_drift()
