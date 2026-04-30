"""Capture the GUI states the README's §10.2 audit was missing.

Renders the Pygame surface in headless mode (``SDL_VIDEODRIVER=dummy``)
so this script runs in CI / on a server without a display, then saves
PNGs to ``assets/assignment-2/``.

States captured: 06_paused_training, 07_demo_mode, 08_fast_mode_indicator.

Run: ``uv run python scripts/capture_screenshots.py``
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from dronerl.gui import GUI  # noqa: E402
from dronerl.sdk import DroneRLSDK  # noqa: E402

OUT_DIR = Path("assets/assignment-2")


def _build_gui() -> GUI:
    """Construct a GUI in a deterministic state with some training applied."""
    sdk = DroneRLSDK("config/config.yaml")
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


if __name__ == "__main__":
    main()
