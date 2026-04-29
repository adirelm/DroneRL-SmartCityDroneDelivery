"""Heatmap, arrows, trail, and label overlays for the DroneRL GUI."""

import numpy as np
import pygame

from dronerl.config_loader import Config
from dronerl.environment import CellType

# Cells to skip for heatmap
_SKIP_HEAT = {CellType.BUILDING, CellType.TRAP, CellType.GOAL, CellType.PIT}


class Overlays:
    """Draws Q-value heatmap and best-action arrows on the grid."""

    def __init__(self, config: Config):
        """Initialise overlay settings and colors from config."""
        gui = config.gui
        colors = config.colors
        self.rows = config.environment.grid_rows
        self.cols = config.environment.grid_cols
        self.cs = gui.cell_size
        self.font_name = gui.font_name
        self.start = tuple(config.environment.start_position)
        self.goal = tuple(config.environment.goal_position)
        self.c_start = tuple(colors.start_marker)
        self.c_white = tuple(colors.white)
        self.c_arrow = tuple(colors.arrow_fill)
        self.c_trail_glow = tuple(colors.trail_glow)
        self.c_trail_line = tuple(colors.trail_line)
        self.c_trail_dot = tuple(colors.trail_dot)
        self._label_font = None

        self.low = np.array(colors.heatmap_low, dtype=float)
        self.mid = np.array(colors.heatmap_mid, dtype=float)
        self.high = np.array(colors.heatmap_high, dtype=float)

    def _heat_color(self, t: float):
        """Map 0..1 to blue -> yellow -> red."""
        if t < 0.5:
            s = t * 2.0
            c = self.low + s * (self.mid - self.low)
        else:
            s = (t - 0.5) * 2.0
            c = self.mid + s * (self.high - self.mid)
        return tuple(np.clip(c, 0, 255).astype(int))

    def draw_heatmap(self, surface: pygame.Surface, q_table, grid) -> None:
        """Color each cell by max Q-value using a 3-color gradient."""
        max_q = np.max(q_table, axis=2)
        mask = np.ones((self.rows, self.cols), dtype=bool)
        for ct in _SKIP_HEAT:
            mask &= (grid != ct)

        vals = max_q[mask]
        if vals.size == 0:
            return

        q_min, q_max = vals.min(), vals.max()
        q_range = q_max - q_min if q_max != q_min else 1.0

        overlay = pygame.Surface((self.cs, self.cs), pygame.SRCALPHA)

        for row in range(self.rows):
            for col in range(self.cols):
                ct = CellType(int(grid[row, col]))
                if ct in _SKIP_HEAT:
                    continue
                t = float(np.clip((max_q[row, col] - q_min) / q_range, 0, 1))
                rgb = self._heat_color(t)
                overlay.fill((*rgb, 150))
                surface.blit(overlay, (col * self.cs, row * self.cs))

    def draw_arrows(self, surface: pygame.Surface, q_table, grid) -> None:
        """Draw arrow polygons pointing in the best action direction."""
        s = self.cs
        sz = int(s * 0.4)
        half = sz // 2

        arrow_surf = pygame.Surface((s, s), pygame.SRCALPHA)

        for row in range(self.rows):
            for col in range(self.cols):
                if grid[row, col] in (CellType.BUILDING, CellType.PIT):
                    continue

                best = int(np.argmax(q_table[row, col]))
                cx, cy = s // 2, s // 2

                if best == 0:    # UP
                    tri = [(cx, cy - half), (cx - half, cy + half), (cx + half, cy + half)]
                elif best == 1:  # DOWN
                    tri = [(cx, cy + half), (cx - half, cy - half), (cx + half, cy - half)]
                elif best == 2:  # LEFT
                    tri = [(cx - half, cy), (cx + half, cy - half), (cx + half, cy + half)]
                else:            # RIGHT
                    tri = [(cx + half, cy), (cx - half, cy - half), (cx - half, cy + half)]

                arrow_surf.fill((0, 0, 0, 0))
                pygame.draw.polygon(arrow_surf, (*self.c_arrow, 180), tri)
                pygame.draw.polygon(arrow_surf, (*self.c_arrow, 220), tri, 1)
                surface.blit(arrow_surf, (col * s, row * s))

    def draw_labels(self, surface: pygame.Surface) -> None:
        """Draw S and G labels on start and goal cells."""
        if self._label_font is None:
            self._label_font = pygame.font.SysFont(self.font_name, self.cs // 3, bold=True)
        s_txt = self._label_font.render("S", True, self.c_start)
        sr, sc = self.start
        sx = sc * self.cs + self.cs // 2 - s_txt.get_width() // 2
        sy = sr * self.cs + self.cs // 2 - s_txt.get_height() // 2
        surface.blit(s_txt, (sx, sy))
        gr, gc = self.goal
        g_txt = self._label_font.render("G", True, self.c_white)
        gx = gc * self.cs + self.cs // 2 - g_txt.get_width() // 2
        gy = gr * self.cs + self.cs // 2 - g_txt.get_height() // 2
        surface.blit(g_txt, (gx, gy))

    def draw_trail(self, surface: pygame.Surface, trail: list) -> None:
        """Draw the demo path trail as connected line with dots."""
        if len(trail) < 2:
            return
        cs = self.cs
        pts = [(c * cs + cs // 2, r * cs + cs // 2) for r, c in trail]
        glow = pygame.Surface((self.cols * cs, self.rows * cs), pygame.SRCALPHA)
        pygame.draw.lines(glow, (*self.c_trail_glow, 80), False, pts, 6)
        surface.blit(glow, (0, 0))
        pygame.draw.lines(surface, self.c_trail_line, False, pts, 2)
        for px, py in pts:
            pygame.draw.circle(surface, self.c_trail_dot, (px, py), 3)
