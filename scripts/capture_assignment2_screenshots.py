"""Capture Assignment 2 screenshots: algorithm selectors, sliders, Pit cell, comparison.

Seeded for reproducibility — every run produces byte-identical PNGs at
the cost of a frozen hazard layout. Methodology phase 11 (visual
regression) relies on this determinism: an unseeded capture would
produce ~13–48 % pixel drift between runs purely from RNG noise.
"""

from __future__ import annotations

import os
import random
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import numpy as np  # noqa: E402
import pygame  # noqa: E402

from dronerl.config_loader import Config, load_config  # noqa: E402
from dronerl.environment import CellType  # noqa: E402
from dronerl.gui import GUI  # noqa: E402

CAPTURE_SEED = 42  # frozen so screenshot regression test is byte-deterministic

OUT = Path("assets/assignment-2")
OUT.mkdir(parents=True, exist_ok=True)


def _build_gui() -> GUI:
    random.seed(CAPTURE_SEED)
    np.random.seed(CAPTURE_SEED)
    gui = GUI(Config(load_config("config/config.yaml")))
    # HazardGenerator owns its own random.Random instance (`_rng`) — global
    # `random.seed()` doesn't reach it. Pin it explicitly so the hazard
    # layout is byte-deterministic across capture runs.
    gui.hazards._rng = random.Random(CAPTURE_SEED)
    return gui


def _save(gui: GUI, name: str) -> None:
    gui._draw()
    pygame.image.save(gui.screen, str(OUT / name))
    print(f"wrote {OUT / name}")


def _train_episodes(gui: GUI, n: int) -> None:
    gui.paused = False
    gui.editor.active = False
    gui.fast_mode = True
    for _ in range(n):
        gui.logic.training_step()


def shot_editor_with_sliders() -> None:
    gui = _build_gui()
    gui.editor.active = True
    gui.paused = True
    gui.sliders.sliders["noise"].value = 0.4
    gui.sliders.sliders["density"].value = 0.25
    gui.sliders.sliders["difficulty"].value = 0.7
    gui.hazards.apply(gui.env)
    gui.env.set_wind_drift(gui.hazards.effective_drift())
    _save(gui, "01_editor_sliders_and_algo_buttons.png")


def shot_pit_and_hazards() -> None:
    gui = _build_gui()
    gui.editor.active = True
    gui.paused = True
    gui.env.set_cell(3, 4, CellType.PIT, editor=True)
    gui.env.set_cell(7, 8, CellType.PIT, editor=True)
    gui.sliders.sliders["noise"].value = 0.6
    gui.sliders.sliders["density"].value = 0.35
    gui.sliders.sliders["difficulty"].value = 0.9
    gui.hazards.apply(gui.env)
    _save(gui, "02_dynamic_board_with_pits.png")


def _train_algo(name: str, episodes: int, filename: str) -> None:
    gui = _build_gui()
    gui.sdk.switch_algorithm(name)  # `gui.agent` is a property — go through the SDK orchestration surface
    gui.logic.reset(gui.agent, gui.env)
    _train_episodes(gui, episodes)
    gui.paused = True
    gui.show_heatmap = True
    gui.show_arrows = True
    _save(gui, filename)


def shot_training_bellman() -> None:
    _train_algo("bellman", 400, "03_training_bellman.png")


def shot_training_q_learning() -> None:
    _train_algo("q_learning", 400, "04_training_q_learning.png")


def shot_training_double_q() -> None:
    _train_algo("double_q", 400, "05_training_double_q.png")


def main() -> None:
    shot_editor_with_sliders()
    shot_pit_and_hazards()
    shot_training_bellman()
    shot_training_q_learning()
    shot_training_double_q()


if __name__ == "__main__":
    main()
