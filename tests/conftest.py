"""Shared fixtures for UI and orchestration tests."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from src.agent import Agent
from src.config_loader import Config, load_config
from src.environment import Environment
from src.game_logic import GameLogic

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def pygame_ready():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def ui_config():
    return Config(load_config(CONFIG_PATH))


@pytest.fixture
def ui_surface(pygame_ready, ui_config):
    return pygame.Surface((ui_config.gui.window_width, ui_config.gui.window_height))


@pytest.fixture
def ui_agent(ui_config):
    return Agent(ui_config)


@pytest.fixture
def ui_env(ui_config):
    return Environment(ui_config)


@pytest.fixture
def ui_logic(ui_agent, ui_env, ui_config):
    return GameLogic(ui_agent, ui_env, ui_config)
