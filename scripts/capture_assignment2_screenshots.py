"""Capture Assignment 2 screenshots: algorithm selectors, sliders, Pit cell, comparison."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.agent_factory import create_agent  # noqa: E402
from src.config_loader import Config, load_config  # noqa: E402
from src.environment import CellType  # noqa: E402
from src.gui import GUI  # noqa: E402

OUT = Path("assets/assignment-2")
OUT.mkdir(parents=True, exist_ok=True)


def _build_gui() -> GUI:
    return GUI(Config(load_config("config/config.yaml")))


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
    gui.cfg.algorithm.name = name
    gui.agent = create_agent(gui.cfg)
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


def copy_comparison_charts() -> None:
    src_dir = Path("data/comparison")
    for name in ("comparison.png", "scenario1_medium.png", "scenario2_hard.png"):
        src = src_dir / name
        if src.exists():
            dst = OUT / f"06_{name}"
            shutil.copy(src, dst)
            print(f"copied {dst}")


def main() -> None:
    shot_editor_with_sliders()
    shot_pit_and_hazards()
    shot_training_bellman()
    shot_training_q_learning()
    shot_training_double_q()
    copy_comparison_charts()


if __name__ == "__main__":
    main()
