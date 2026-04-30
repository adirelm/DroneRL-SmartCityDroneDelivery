"""Action dispatch for DroneRL GUI — maps action strings to state changes.

§4.1: lifecycle-changing actions (reset, switch_to algorithm) delegate to the
``GUI.sdk`` instance instead of constructing ``Environment`` / ``create_agent``
locally. Read-only and presentation-only actions (toggle_fast, save, load,
open_editor) stay in this module.
"""

import os

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
        gui.sdk.save_brain(gui.brain_path)
    elif a == "load" and os.path.exists(gui.brain_path):
        gui.sdk.load_brain(gui.brain_path)
    elif a == "reset":
        gui.sdk.reset()
        gui.sdk.environment.drift_probability = gui.sdk.hazards.effective_drift()
        gui.logic.reset(gui.sdk.agent, gui.sdk.environment)
        gui.paused = gui.editor.active = True
        gui.fast_mode = gui.show_heatmap = gui.show_arrows = False
    elif a == "cycle_type":
        gui.editor.next_type()
    elif a in _ALGO_KEYS:
        gui.sdk.switch_algorithm(_ALGO_KEYS[a])
        gui.logic.reset(gui.sdk.agent, gui.sdk.environment)
        gui.paused = True
        gui.show_heatmap = gui.show_arrows = False
    elif a == "regenerate_hazards":
        gui.sdk.regenerate_hazards()
    elif a == "run_comparison":
        _run_comparison_scripts(gui)


_comparison_proc = None  # module-level handle for double-spawn guard (§5.3)


def _run_comparison_scripts(gui) -> None:
    """Open the existing comparison chart; regenerate in the background if missing.

    §5.3 — guards against multiple rapid GUI clicks spawning duplicate
    Python subprocesses. The module-level ``_comparison_proc`` reference is
    consulted before each spawn; if a previous chart-generation process is
    still running, we skip rather than stack a second one.

    Thread safety: the read-modify-write on ``_comparison_proc`` is safe only
    because Pygame's event loop is single-threaded and ``dispatch`` is the
    only caller. If a future change moves dispatch into a thread or async
    context, replace this sentinel with a ``threading.Lock``.
    """
    global _comparison_proc
    import subprocess
    import sys
    from pathlib import Path
    chart = Path(gui.cfg.comparison.output_dir) / "comparison.png"
    if chart.exists():
        _open_file(str(chart))
    elif _comparison_proc is None or _comparison_proc.poll() is not None:
        _comparison_proc = subprocess.Popen(
            [sys.executable, "scripts/generate_comparison_charts.py"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    gui.paused = True


def _open_file(path: str) -> None:
    """Open a file with the OS's default viewer (macOS / Linux / Windows)."""
    import subprocess
    import sys
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
    elif sys.platform == "win32":
        subprocess.Popen(["explorer", path])
    else:
        subprocess.Popen(["xdg-open", path])
