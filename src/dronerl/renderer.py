"""Grid renderer for the DroneRL Pygame GUI."""

import math

import pygame

from dronerl.config_loader import Config
from dronerl.environment import CellType


class Renderer:
    """Polished grid, cell, and drone renderer for the Pygame surface.

    Input:  ``draw_grid(surface, grid_array)`` — a `pygame.Surface` and the
            ``Environment.grid`` ndarray of `int`-coded :class:`CellType`
            values. ``draw_drone(surface, (row, col))`` accepts the drone's
            current cell position. ``draw_grid_lines(surface)`` overlays
            the grid mesh.
    Output: side-effects on the passed `pygame.Surface` (no return value).
            Frame-counter ``self.frame`` is incremented on each draw to
            drive the drone's pulse animation.
    Setup:  ``Config`` — reads ``environment.grid_rows/grid_cols``,
            ``gui.cell_size``, and the full `colors.*` palette
            (`empty`, `building` + `building_accent`, `trap` + `trap_accent`,
            `goal` + `goal_accent`, `wind` + `wind_accent`, `pit` +
            `pit_accent`, `drone` + `drone_glow`, `grid_line`,
            `start_marker`, `white`). Each cell-type colour pair is read
            once at construction and cached on the instance.
    """

    def __init__(self, config: Config):
        gui = config.gui
        c = config.colors
        self.rows = config.environment.grid_rows
        self.cols = config.environment.grid_cols
        self.cs = gui.cell_size
        self.frame = 0
        self.c_empty = tuple(c.empty)
        self.c_building = tuple(c.building)
        self.c_building_acc = tuple(c.building_accent)
        self.c_trap = tuple(c.trap)
        self.c_trap_acc = tuple(c.trap_accent)
        self.c_goal = tuple(c.goal)
        self.c_goal_acc = tuple(c.goal_accent)
        self.c_wind = tuple(c.wind)
        self.c_wind_acc = tuple(c.wind_accent)
        self.c_pit = tuple(c.pit)
        self.c_pit_acc = tuple(c.pit_accent)
        self.c_drone = tuple(c.drone)
        self.c_drone_glow = tuple(c.drone_glow)
        self.c_grid = tuple(c.grid_line)
        self.c_start = tuple(c.start_marker)
        self.c_white = tuple(c.white)

    def _draw_empty(self, surf, x, y):
        s = self.cs
        pygame.draw.rect(surf, self.c_empty, (x, y, s, s))
        hi = pygame.Surface((s, 4), pygame.SRCALPHA)
        hi.fill((*[min(c + 20, 255) for c in self.c_empty], 60))
        surf.blit(hi, (x, y))
        lo = pygame.Surface((s, 4), pygame.SRCALPHA)
        lo.fill((0, 0, 0, 40))
        surf.blit(lo, (x, y + s - 4))

    def _draw_building(self, surf, x, y):
        s = self.cs
        pygame.draw.rect(surf, self.c_building, (x, y, s, s))
        pygame.draw.rect(surf, self.c_building_acc, (x, y, s, 6))
        shadow = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 35), (2, 2, s - 2, s - 2))
        surf.blit(shadow, (x, y))

    def _draw_trap(self, surf, x, y):
        s = self.cs
        pygame.draw.rect(surf, self.c_trap, (x, y, s, s))
        m, p = 8, s - 8
        pygame.draw.line(surf, self.c_trap_acc, (x + m, y + m), (x + p, y + p), 3)
        pygame.draw.line(surf, self.c_trap_acc, (x + p, y + m), (x + m, y + p), 3)

    def _draw_goal(self, surf, x, y):
        s = self.cs
        pulse = 0.5 + 0.5 * math.sin(self.frame * 0.08)
        br = [min(int(g + pulse * (a - g)), 255) for g, a in
              zip(self.c_goal, self.c_goal_acc, strict=False)]
        pygame.draw.rect(surf, tuple(br), (x, y, s, s))
        glow = pygame.Surface((s, s), pygame.SRCALPHA)
        glow_a = int(40 + 35 * pulse)
        pygame.draw.circle(glow, (*self.c_goal_acc, glow_a), (s // 2, s // 2), s // 2)
        surf.blit(glow, (x, y))
        cx, cy = x + s // 2, y + s // 2
        for r in (s // 5, s // 9):
            pygame.draw.circle(surf, self.c_goal_acc, (cx, cy), r, 2)
        pygame.draw.circle(surf, self.c_white, (cx, cy), 2)

    def _draw_wind(self, surf, x, y):
        s = self.cs
        pygame.draw.rect(surf, self.c_wind, (x, y, s, s))
        _cx, cy = x + s // 2, y + s // 2
        for dy in (-s // 5, 0, s // 5):
            pts = []
            for i in range(8):
                px = x + s * 0.2 + i * s * 0.075
                py = cy + dy + math.sin(i * 1.2 + self.frame * 0.1) * 3
                pts.append((px, py))
            if len(pts) > 1:
                pygame.draw.lines(surf, self.c_wind_acc, False, pts, 2)

    def _draw_pit(self, surf, x, y):
        s = self.cs
        pygame.draw.rect(surf, self.c_pit, (x, y, s, s))
        cx, cy = x + s // 2, y + s // 2
        for r in (s // 2, s // 3, s // 5):
            pygame.draw.circle(surf, self.c_pit_acc, (cx, cy), r, 1)

    def draw_grid(self, surface: pygame.Surface, grid) -> None:
        """Draw all grid cells with their visual styles."""
        self.frame += 1
        draw = {CellType.EMPTY: self._draw_empty, CellType.BUILDING: self._draw_building,
                CellType.TRAP: self._draw_trap, CellType.GOAL: self._draw_goal,
                CellType.WIND: self._draw_wind, CellType.PIT: self._draw_pit}
        for row in range(self.rows):
            for col in range(self.cols):
                ct = CellType(int(grid[row, col]))
                x, y = col * self.cs, row * self.cs
                draw.get(ct, self._draw_empty)(surface, x, y)
    def draw_drone(self, surface: pygame.Surface, position: tuple) -> None:
        """Draw the drone with 4 rotors and a glow."""
        row, col = position
        cx = col * self.cs + self.cs // 2
        cy = row * self.cs + self.cs // 2
        s = self.cs
        glow = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.c_drone_glow, 50), (s // 2, s // 2), s // 3)
        surface.blit(glow, (cx - s // 2, cy - s // 2))
        arm = s // 4
        pygame.draw.line(surface, self.c_drone, (cx - arm, cy - arm), (cx + arm, cy + arm), 3)
        pygame.draw.line(surface, self.c_drone, (cx + arm, cy - arm), (cx - arm, cy + arm), 3)
        pygame.draw.circle(surface, self.c_drone, (cx, cy), s // 8)
        pygame.draw.circle(surface, self.c_white, (cx, cy), s // 8, 1)
        rr = s // 7
        for dx, dy in [(-arm, -arm), (arm, -arm), (-arm, arm), (arm, arm)]:
            pygame.draw.circle(surface, self.c_white, (cx + dx, cy + dy), rr, 2)
            pygame.draw.circle(surface, self.c_drone, (cx + dx, cy + dy), rr - 2)

    def draw_grid_lines(self, surface: pygame.Surface) -> None:
        """Draw subtle grid lines with brighter intersections."""
        gw = self.cols * self.cs
        gh = self.rows * self.cs
        for r in range(self.rows + 1):
            y = r * self.cs
            pygame.draw.line(surface, self.c_grid, (0, y), (gw, y))
        for c in range(self.cols + 1):
            x = c * self.cs
            pygame.draw.line(surface, self.c_grid, (x, 0), (x, gh))
        bright = tuple(min(v + 25, 255) for v in self.c_grid)
        for r in range(self.rows + 1):
            for c in range(self.cols + 1):
                pygame.draw.circle(surface, bright, (c * self.cs, r * self.cs), 1)
