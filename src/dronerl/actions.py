"""Action dispatch for DroneRL GUI — maps action strings to state changes.

§4.1: lifecycle-changing actions (reset, switch_to algorithm) delegate to the
``GUI.sdk`` instance instead of constructing ``Environment`` / ``create_agent``
locally. Read-only and presentation-only actions (toggle_fast, save, load,
open_editor) stay in this module.
"""

import os
import time

_ALGO_KEYS = {"use_bellman": "bellman",
              "use_q_learning": "q_learning",
              "use_double_q": "double_q"}

_SAVE_LOAD_DEBOUNCE_S = 1.0  # §5.3 — held S/L key shouldn't spam disk writes
_last_io_t: dict[str, float] = {}  # per-action timestamps; safe under single-threaded Pygame loop


def _io_debounced(action: str) -> bool:
    """Return True if ``action`` is allowed now; False if it's repeating within the debounce window.

    Per-action timers (so a `save` followed by `load` is fine — they are
    different operations and shouldn't gate each other).
    """
    now = time.monotonic()
    if now - _last_io_t.get(action, 0.0) < _SAVE_LOAD_DEBOUNCE_S:
        return False
    _last_io_t[action] = now
    return True


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
        if _io_debounced("save"):
            gui.sdk.save_brain(gui.brain_path)
    elif a == "load" and os.path.exists(gui.brain_path):
        if _io_debounced("load"):
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


def _resolve_output_path(gui, filename: str):
    """Resolve ``output_dir/filename`` and assert it stays inside the project root.

    §13 Security / Integrity — ``comparison.output_dir`` flows from
    ``config/config.yaml`` directly into ``Path()`` and then into the OS
    file viewer (``_open_file``). A maliciously-crafted or accidentally-set
    config (``output_dir: ../../../../etc``) could redirect the OS viewer
    to a path outside the project. This helper resolves the candidate path
    and refuses anything that escapes the project root.
    """
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[2]
    candidate = (project_root / gui.cfg.comparison.output_dir / filename).resolve()
    if project_root not in candidate.parents and candidate != project_root:
        raise ValueError(
            f"comparison.output_dir resolves to {candidate!r}, outside project root "
            f"{project_root!r} — refusing for §13 path-traversal safety."
        )
    return candidate


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
    chart = _resolve_output_path(gui, "comparison.png")
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
