"""Slider widgets for difficulty / noise / density control."""

import pygame

from dronerl.config_loader import Config


class Slider:
    """Horizontal slider with a label and live value display."""

    def __init__(self, label: str, x: int, y: int, w: int, h: int, value: float, maximum: float):
        self.label = label
        self.rect = pygame.Rect(x, y, w, h)
        self.maximum = float(maximum)
        self.value = float(value)
        self.dragging = False

    @property
    def fraction(self) -> float:
        """Current value normalised to [0.0, 1.0] for fill-bar / handle position."""
        return 0.0 if self.maximum == 0 else self.value / self.maximum

    def _handle_x(self) -> int:
        return self.rect.x + int(self.fraction * self.rect.w)

    def handle_event(self, event) -> bool:
        """Return True if value changed."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return self._set_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            return self._set_from_mouse(event.pos[0])
        return False

    def _set_from_mouse(self, mx: int) -> bool:
        rel = (mx - self.rect.x) / max(1, self.rect.w)
        new_value = max(0.0, min(1.0, rel)) * self.maximum
        changed = abs(new_value - self.value) > 1e-4
        self.value = new_value
        return changed

    def set_y(self, y: int) -> None:
        """Reposition this slider's row vertically."""
        self.rect.y = y

    def draw(self, surface, font, colors) -> None:
        """Render track, fill, draggable handle, and ``label: value`` text."""
        pygame.draw.rect(surface, tuple(colors.btn_bg), self.rect, border_radius=3)
        fill = pygame.Rect(self.rect.x, self.rect.y, self._handle_x() - self.rect.x, self.rect.h)
        pygame.draw.rect(surface, tuple(colors.accent), fill, border_radius=3)
        pygame.draw.circle(surface, tuple(colors.text), (self._handle_x(), self.rect.centery), 6)
        label = f"{self.label}: {self.value:.2f}"
        surface.blit(font.render(label, True, tuple(colors.text)), (self.rect.x, self.rect.y - 16))


class SliderPanel:
    """Three-slider panel: noise, density, difficulty."""

    def __init__(self, config: Config, x: int, y: int, width: int):
        self.colors = config.colors
        cfg = config.dynamic_board
        self.sliders = {
            "noise": Slider("Noise", x, y, width, 10, cfg.noise_level, 1.0),
            "density": Slider("Density", x, y + 40, width, 10, cfg.hazard_density, 0.5),
            "difficulty": Slider("Difficulty", x, y + 80, width, 10, cfg.difficulty, 1.0),
        }
        self._font: pygame.font.Font | None = None

    def _ensure_font(self) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("arial", 12)

    def handle_event(self, event) -> str | None:
        """Return the name of any slider that changed value, or None."""
        for name, slider in self.sliders.items():
            if slider.handle_event(event):
                return name
        return None

    def get(self, name: str) -> float:
        """Return the current value of the slider identified by ``name``."""
        return self.sliders[name].value

    def set_y(self, y: int) -> None:
        """Reposition sliders vertically; keeps the 40px row spacing."""
        for i, slider in enumerate(self.sliders.values()):
            slider.set_y(y + i * 40)

    def draw(self, surface) -> None:
        """Render every slider in the panel."""
        self._ensure_font()
        for slider in self.sliders.values():
            slider.draw(surface, self._font, self.colors)
