"""Tests for the slider widgets."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from dronerl.config_loader import Config, load_config  # noqa: E402
from dronerl.sliders import Slider, SliderPanel  # noqa: E402

CONFIG_PATH = "config/config.yaml"


@pytest.fixture(autouse=True, scope="module")
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def config():
    return Config(load_config(CONFIG_PATH))


class _Event:
    def __init__(self, type_, pos=(0, 0), button=1):
        self.type = type_
        self.pos = pos
        self.button = button


class TestSlider:
    def test_initial_value(self):
        s = Slider("Noise", 0, 0, 100, 10, 0.3, 1.0)
        assert s.value == 0.3
        assert s.fraction == pytest.approx(0.3)

    def test_click_sets_value(self):
        s = Slider("x", 0, 0, 100, 10, 0.0, 1.0)
        changed = s.handle_event(_Event(pygame.MOUSEBUTTONDOWN, pos=(50, 5)))
        assert changed is True
        assert s.value == pytest.approx(0.5)

    def test_drag_updates(self):
        s = Slider("x", 0, 0, 100, 10, 0.0, 1.0)
        s.handle_event(_Event(pygame.MOUSEBUTTONDOWN, pos=(25, 5)))
        s.handle_event(_Event(pygame.MOUSEMOTION, pos=(75, 5)))
        assert s.value == pytest.approx(0.75)

    def test_release_stops_drag(self):
        s = Slider("x", 0, 0, 100, 10, 0.0, 1.0)
        s.handle_event(_Event(pygame.MOUSEBUTTONDOWN, pos=(10, 5)))
        s.handle_event(_Event(pygame.MOUSEBUTTONUP, pos=(10, 5)))
        changed = s.handle_event(_Event(pygame.MOUSEMOTION, pos=(90, 5)))
        assert changed is False


class TestSliderPanel:
    def test_three_sliders(self, config):
        panel = SliderPanel(config, 0, 0, 200)
        assert set(panel.sliders) == {"noise", "density", "difficulty"}

    def test_handle_event_returns_name(self, config):
        panel = SliderPanel(config, 0, 0, 200)
        noise = panel.sliders["noise"]
        evt = _Event(pygame.MOUSEBUTTONDOWN, pos=(noise.rect.x + 100, noise.rect.y + 5))
        name = panel.handle_event(evt)
        assert name == "noise"

    def test_get_value(self, config):
        panel = SliderPanel(config, 0, 0, 200)
        panel.sliders["density"].value = 0.25
        assert panel.get("density") == 0.25

    def test_draw_no_exception(self, config):
        panel = SliderPanel(config, 0, 0, 200)
        surface = pygame.Surface((400, 200))
        panel.draw(surface)
