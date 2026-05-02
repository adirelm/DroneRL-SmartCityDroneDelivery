"""Capture the GUI states the README's §10.2 audit was missing.

Renders the Pygame surface in headless mode (``SDL_VIDEODRIVER=dummy``)
so this script runs in CI / on a server without a display, then saves
PNGs to ``assets/assignment-2/``.

States captured: ``06_paused_training``, ``07_demo_mode``,
``08_fast_mode_indicator``, ``09_protected_cell_flash`` (Pass-4 §10
Nielsen #9 fix), ``10_converged_banner`` (post-converge dashboard
state). All 5 are byte-deterministic — Pass-5 §11 methodology test
relies on this.

Run: ``uv run python scripts/capture_screenshots.py``
"""

from __future__ import annotations

import os
import random
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import numpy as np  # noqa: E402
import pygame  # noqa: E402

from dronerl.environment import CellType  # noqa: E402
from dronerl.gui import GUI  # noqa: E402
from dronerl.sdk import DroneRLSDK  # noqa: E402

OUT_DIR = Path("assets/assignment-2")
CAPTURE_SEED = 42  # frozen so screenshot regression test is byte-deterministic


def _build_gui() -> GUI:
    """Construct a GUI in a deterministic state with some training applied."""
    random.seed(CAPTURE_SEED)
    np.random.seed(CAPTURE_SEED)
    sdk = DroneRLSDK("config/config.yaml")
    # HazardGenerator owns its own random.Random instance — pin it before apply.
    sdk.hazards._rng = random.Random(CAPTURE_SEED)
    sdk.hazards.apply(sdk.environment)
    sdk.environment.set_wind_drift(sdk.hazards.effective_drift())
    gui = GUI(sdk=sdk)
    gui.editor.active = False
    for _ in range(50):
        sdk.train_step()
    return gui


def _save(gui: GUI, name: str) -> Path:
    out = OUT_DIR / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    gui._draw()
    pygame.image.save(gui.screen, str(out))
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gui = _build_gui()

    # 06 — paused training: status bar shows [PAUSED] flag
    gui.paused = True
    gui.fast_mode = False
    gui.show_heatmap = gui.show_arrows = True
    print(_save(gui, "06_paused_training"))

    # 07 — demo mode: trail overlay visible
    gui.paused = False
    gui.show_heatmap = gui.show_arrows = False
    gui.logic.enter_demo()
    for _ in range(8):
        gui.logic.demo_step(gui.fps)
    print(_save(gui, "07_demo_mode"))
    gui.logic.exit_demo()

    # 08 — fast-mode indicator visible alongside training render
    gui.paused = False
    gui.fast_mode = True
    gui.show_heatmap = True
    print(_save(gui, "08_fast_mode_indicator"))
    pygame.quit()

    # 09 — Nielsen #9 protected-cell flash (Pass-4 §10 fix). Build a
    # fresh GUI in editor mode and trigger the flash via _on_click.
    sdk2 = DroneRLSDK()
    sdk2.hazards._rng = random.Random(CAPTURE_SEED)
    gui2 = GUI(sdk=sdk2)
    gui2.editor.active = True
    gui2.dashboard.buttons.handle_click = lambda pos: None
    gui2.editor.handle_click = lambda pos: (gui2.env.start[0], gui2.env.start[1], CellType.TRAP)
    gui2._on_click((10, 10))
    print(_save(gui2, "09_protected_cell_flash"))
    pygame.quit()

    # 10 — Converged dashboard banner (forces logic.converged + arrows on).
    sdk3 = DroneRLSDK()
    sdk3.hazards._rng = random.Random(CAPTURE_SEED)
    gui3 = GUI(sdk=sdk3)
    for _ in range(50):
        sdk3.train_step()
    gui3.editor.active = False
    gui3.paused = True
    gui3.show_heatmap = gui3.show_arrows = True
    gui3.logic.converged = True
    gui3.logic.episode = 1500
    print(_save(gui3, "10_converged_banner"))
    pygame.quit()


if __name__ == "__main__":
    main()
