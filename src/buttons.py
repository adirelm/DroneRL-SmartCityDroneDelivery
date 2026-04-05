"""Context-aware button panel for the DroneRL dashboard."""

import pygame


class Button:
    """A single clickable button with label, action, and hover state."""
    def __init__(self, label, action, primary=False, color=None):
        """Initialise a button with display label, action key, and style."""
        self.label = label
        self.action = action
        self.primary = primary
        self.color = color  # optional override color
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hovered = False

    def draw(self, surface, font, colors):
        """Render the button onto the given surface."""
        if self.color:
            bg = _brighten(self.color, 20) if self.hovered else self.color
            border = _brighten(self.color, 50)
        elif self.primary:
            bg = colors["primary_hover"] if self.hovered else colors["primary"]
            border = colors["primary_border"]
        elif self.hovered:
            bg, border = colors["btn_hover"], colors["border"]
        else:
            bg, border = colors["btn_bg"], colors["border"]
        pygame.draw.rect(surface, bg, self.rect, border_radius=5)
        pygame.draw.rect(surface, border, self.rect, 1, border_radius=5)
        txt = font.render(self.label, True, colors["text"])
        tx = self.rect.x + (self.rect.w - txt.get_width()) // 2
        ty = self.rect.y + (self.rect.h - txt.get_height()) // 2
        surface.blit(txt, (tx, ty))


def _brighten(color, amount):
    """Return a brighter version of an RGB tuple."""
    return tuple(min(255, c + amount) for c in color)


def _overlay_btns(hmap, arrows):
    """Return heatmap/arrows toggle buttons."""
    return [Button(f"Heatmap: {'ON' if hmap else 'OFF'}", "toggle_heatmap"),
            Button(f"Arrows: {'ON' if arrows else 'OFF'}", "toggle_arrows")]

def _get_buttons(s, c_demo, c_primary):
    """Return buttons for current state using config colors."""
    editing, demo, paused = s.get("editor_active"), s.get("demo_mode"), s.get("paused")
    converged, fast = s.get("converged"), s.get("fast_mode")
    hmap, arrows, trained = s.get("show_heatmap"), s.get("show_arrows"), s.get("has_trained")
    btn = Button
    ov = _overlay_btns(hmap, arrows)

    if converged and paused and not demo and not editing:
        return [btn("Watch Optimal Path", "start_demo", True, c_demo),
                btn("Continue Training", "resume", color=c_primary),
                *ov, btn("Edit Map", "open_editor"),
                btn("Save Brain", "save"), btn("Reset", "reset")]
    if demo:
        return [btn("Stop Demo", "stop_demo", True),
                btn("Continue Training", "continue_training", color=c_primary),
                *ov, btn("Edit Map", "open_editor"),
                btn("Save Brain", "save"), btn("Reset", "reset")]
    if editing:
        return [btn("Train", "start_training", True), *ov,
                btn("Load Brain", "load"), btn("Reset", "reset")]
    if paused:
        btns = [btn("Resume", "resume", True),
                btn(f"Fast: {'ON' if fast else 'OFF'}", "toggle_fast"), *ov,
                btn("Edit Map", "open_editor")]
        if trained:
            btns += [btn("Demo", "start_demo"), btn("Save Brain", "save")]
        return btns + [btn("Load Brain", "load"), btn("Reset", "reset")]
    return [btn("Pause", "pause", True),
            btn(f"Fast: {'ON' if fast else 'OFF'}", "toggle_fast"), *ov,
            btn("Edit Map", "open_editor"), btn("Save Brain", "save"), btn("Reset", "reset")]


class ButtonPanel:
    """Manages layout, drawing, and click handling for a set of buttons."""
    def __init__(self, config):
        """Initialise button panel layout and colors from config."""
        gui = config.gui
        c = config.colors
        self.colors = {
            "btn_bg": tuple(c.btn_bg), "btn_hover": tuple(c.btn_hover),
            "primary": tuple(c.primary_btn), "primary_hover": tuple(c.primary_btn_hover),
            "primary_border": tuple(c.primary_btn_border),
            "text": tuple(c.text), "border": tuple(c.panel_border),
        }
        self.c_demo = tuple(c.demo_btn)
        self.c_primary = tuple(c.primary_btn)
        self.font_name = gui.font_name
        self.ox = gui.grid_area_width + 15
        self.panel_w = gui.dashboard_width - 30
        self.bw = (self.panel_w - 8) // 2
        self.bh, self.gap = 30, 6
        self.font = None
        self.buttons = []

    def _ensure_font(self):
        """Lazily initialise the button font."""
        if self.font is None:
            self.font = pygame.font.SysFont(self.font_name, 13)

    def draw(self, surface, state_dict, y_start):
        """Draw all context-aware buttons and return the next y position."""
        self._ensure_font()
        self.buttons = _get_buttons(state_dict, self.c_demo, self.c_primary)
        y = y_start
        for i, btn in enumerate(self.buttons):
            if i == 0:
                btn.rect = pygame.Rect(self.ox, y, self.panel_w, self.bh + 4)
                y += self.bh + 4 + self.gap
            else:
                col = (i - 1) % 2
                if col == 0 and i > 1:
                    y += self.bh + self.gap
                btn.rect = pygame.Rect(
                    self.ox + col * (self.bw + self.gap + 2), y,
                    self.bw, self.bh)
            btn.draw(surface, self.font, self.colors)
        return y + self.bh + self.gap

    def handle_click(self, pos):
        """Return the action string of the clicked button, or None."""
        for btn in self.buttons:
            if btn.rect.collidepoint(pos):
                return btn.action
        return None

    def handle_hover(self, pos):
        """Update hover state for all buttons based on mouse position."""
        for btn in self.buttons:
            btn.hovered = btn.rect.collidepoint(pos)
