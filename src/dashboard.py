"""Right-side dashboard panel for the DroneRL GUI."""

import pygame

from src.buttons import ButtonPanel
from src.config_loader import Config


class Dashboard:
    """Renders metrics, reward graph, legend, and buttons on the dashboard."""

    def __init__(self, config: Config):
        """Initialise dashboard layout, colors, and fonts from config."""
        gui = config.gui
        self.x = gui.grid_area_width
        self.width = gui.dashboard_width
        self.height = gui.window_height
        self.history_size = gui.reward_history_size
        self.font_name = gui.font_name

        c = config.colors
        self.bg = tuple(c.dashboard_bg)
        self.text_color = tuple(c.text)
        self.dim = tuple(c.text_dim)
        self.accent = tuple(c.accent)
        self.border = tuple(c.panel_border)
        self.goal_color = tuple(c.goal)
        self.graph_bg = tuple(c.graph_bg)
        self.graph_zero = tuple(c.graph_zero)
        self.banner_bg = tuple(c.banner_bg)
        self.banner_border = tuple(c.banner_border)
        self.banner_text = tuple(c.banner_text)

        self.cell_colors = {
            "Empty": tuple(c.empty), "Building": tuple(c.building),
            "Trap": tuple(c.trap), "Goal": tuple(c.goal),
            "Wind": tuple(c.wind), "Pit": tuple(c.pit), "Drone": tuple(c.drone),
        }
        self.buttons = ButtonPanel(config)
        self.font = self.title_font = self.small_font = None

    def _ensure_fonts(self):
        if self.font is None:
            self.font = pygame.font.SysFont(self.font_name, 18)
            self.title_font = pygame.font.SysFont(self.font_name, 24, bold=True)
            self.small_font = pygame.font.SysFont(self.font_name, 14)

    def draw(self, surface: pygame.Surface, metrics: dict,
             reward_history: list, state_dict: dict = None) -> None:
        """Draw the full dashboard: title, metrics, graph, legend, buttons."""
        self._ensure_fonts()
        pygame.draw.rect(surface, self.bg, (self.x, 0, self.width, self.height))
        y = self._draw_title(surface, 14)
        y = self._draw_metrics(surface, metrics, y)
        y = self._draw_graph(surface, reward_history, y)
        y = self._draw_legend(surface, y)
        sd = state_dict or {}
        if sd.get("converged") and not sd.get("demo_mode"):
            y = self._draw_banner(surface, y)
        self.buttons.draw(surface, sd, y)

    def _draw_title(self, surface, y) -> int:
        title = self.title_font.render("DroneRL Dashboard", True, self.text_color)
        surface.blit(title, (self.x + 15, y))
        ly = y + title.get_height() + 4
        pygame.draw.line(surface, self.accent, (self.x + 15, ly),
                         (self.x + self.width - 15, ly), 2)
        return ly + 12

    def _draw_metrics(self, surface, m: dict, y) -> int:
        labels = [
            ("Episode", str(m.get("episode", 0))),
            ("Total Reward", f"{m.get('total_reward', 0):.1f}"),
            ("Epsilon", f"{m.get('epsilon', 0):.4f}"),
            ("Steps", str(m.get("steps", 0))),
            ("Goal Rate", f"{m.get('goal_rate', 0):.1f}%"),
        ]
        alpha = m.get("alpha")
        if alpha is not None:
            labels.insert(3, ("Alpha", f"{alpha:.4f}"))
        rx = self.x + self.width - 20
        for lbl, val in labels:
            lt = self.font.render(lbl, True, self.dim)
            vt = self.font.render(val, True, self.text_color)
            surface.blit(lt, (self.x + 20, y))
            surface.blit(vt, (rx - vt.get_width(), y))
            y += 24
        # Goal rate progress bar
        rate = m.get("goal_rate", 0) / 100.0
        bar_y = y
        bw = self.width - 40
        pygame.draw.rect(surface, self.border, (self.x + 20, bar_y, bw, 8), border_radius=4)
        if rate > 0:
            pygame.draw.rect(surface, self.goal_color,
                             (self.x + 20, bar_y, int(bw * min(rate, 1.0)), 8), border_radius=4)
        return bar_y + 20

    def _draw_graph(self, surface, history: list, y) -> int:
        gx, gw, gh = self.x + 15, self.width - 30, 130
        title = self.small_font.render("Reward History (last 100)", True, self.dim)
        surface.blit(title, (gx, y))
        y += 18
        pygame.draw.rect(surface, self.graph_bg, (gx, y, gw, gh), border_radius=4)
        pygame.draw.rect(surface, self.border, (gx, y, gw, gh), 1, border_radius=4)

        if len(history) >= 2:
            data = history[-self.history_size:]
            mn, mx = min(data), max(data)
            rng = mx - mn if mx != mn else 1.0
            # Zero line
            if mn < 0 < mx:
                zy = y + gh - int((0 - mn) / rng * (gh - 6)) - 3
                pygame.draw.line(surface, self.graph_zero, (gx + 2, zy), (gx + gw - 2, zy), 1)
            pts = []
            for i, v in enumerate(data):
                px = gx + 2 + int(i * (gw - 4) / (len(data) - 1))
                py = y + gh - int((v - mn) / rng * (gh - 6)) - 3
                pts.append((px, py))
            pygame.draw.lines(surface, self.goal_color, False, pts, 2)
            # Min/max labels
            mn_t = self.small_font.render(f"{mn:.0f}", True, self.dim)
            mx_t = self.small_font.render(f"{mx:.0f}", True, self.dim)
            surface.blit(mx_t, (gx + 4, y + 2))
            surface.blit(mn_t, (gx + 4, y + gh - 16))
        return y + gh + 16

    def _draw_legend(self, surface, y) -> int:
        title = self.small_font.render("Legend", True, self.dim)
        surface.blit(title, (self.x + 15, y))
        y += 20
        items = list(self.cell_colors.items())
        col_w = (self.width - 30) // 2
        for i, (name, color) in enumerate(items):
            col, row = i % 2, i // 2
            lx = self.x + 15 + col * col_w
            ly = y + row * 20
            pygame.draw.rect(surface, color, (lx, ly, 14, 14), border_radius=2)
            t = self.small_font.render(name, True, self.text_color)
            surface.blit(t, (lx + 20, ly - 1))
        return y + ((len(items) + 1) // 2) * 20 + 8

    def _draw_banner(self, surface, y) -> int:
        bx, bw, bh = self.x + 10, self.width - 20, 38
        pygame.draw.rect(surface, self.banner_bg, (bx, y, bw, bh), border_radius=6)
        pygame.draw.rect(surface, self.banner_border, (bx, y, bw, bh), 2, border_radius=6)
        txt = self.font.render("Converged! Agent found optimal path.", True,
                               self.banner_text)
        surface.blit(txt, (bx + (bw - txt.get_width()) // 2,
                           y + (bh - txt.get_height()) // 2))
        return y + bh + 8
