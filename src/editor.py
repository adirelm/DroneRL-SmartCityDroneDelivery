"""Level editor for placing and removing grid obstacles."""

import pygame

from src.config_loader import Config
from src.environment import CellType

EDITABLE_TYPES = [CellType.BUILDING, CellType.TRAP, CellType.WIND, CellType.PIT]
TYPE_NAMES = {
    CellType.BUILDING: "Building",
    CellType.TRAP: "Trap",
    CellType.WIND: "Wind",
    CellType.PIT: "Pit",
}


class Editor:
    """Handles grid editing via mouse clicks in the GUI."""

    def __init__(self, config: Config):
        """Initialise editor layout and colors from config."""
        gui = config.gui
        colors = config.colors
        self.rows = config.environment.grid_rows
        self.cols = config.environment.grid_cols
        self.cell_size = gui.cell_size
        self.dashboard_x = gui.grid_area_width
        self.dashboard_w = gui.dashboard_width
        self.font_name = gui.font_name
        self.active = False
        self._type_index = 0
        self.type_colors = {
            CellType.BUILDING: tuple(colors.building),
            CellType.TRAP: tuple(colors.trap),
            CellType.WIND: tuple(colors.wind),
            CellType.PIT: tuple(colors.pit),
        }
        self.c_white = tuple(colors.white)
        self.c_bar_bg = tuple(colors.editor_bar_bg)
        self.c_border = tuple(colors.panel_border)
        self.c_dim = tuple(colors.status_dim)
        self.c_unsel = tuple(colors.editor_unselected)
        self.c_unsel_border = tuple(colors.editor_unselected_border)
        self.c_label = tuple(colors.editor_label)
        self.c_hint = tuple(colors.editor_hint)
        self.font = self.btn_font = None
        self.btn_rects = []

    @property
    def selected_type(self) -> CellType:
        """Return the currently selected editable cell type."""
        return EDITABLE_TYPES[self._type_index]

    def next_type(self) -> None:
        """Cycle to the next editable cell type."""
        self._type_index = (self._type_index + 1) % len(EDITABLE_TYPES)

    def handle_click(self, pos: tuple):
        """Process a click: select type button or return grid cell to toggle."""
        mx, my = pos
        for rect, idx in self.btn_rects:
            if rect.collidepoint(mx, my):
                self._type_index = idx
                return None
        col = mx // self.cell_size
        row = my // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col, self.selected_type)
        return None

    def draw_ui(self, surface: pygame.Surface, mouse_pos: tuple) -> None:
        """Draw editor cursor overlay and type-selector buttons."""
        if self.font is None:
            self.font = pygame.font.SysFont(self.font_name, 13)
            self.btn_font = pygame.font.SysFont(self.font_name, 15, bold=True)
        self._draw_cursor(surface, mouse_pos)
        self._draw_type_buttons(surface)

    def _draw_cursor(self, surface, mouse_pos):
        mx, my = mouse_pos
        col, row = mx // self.cell_size, my // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            color = self.type_colors[self.selected_type]
            ov = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            ov.fill((*color, 140))
            surface.blit(ov, (col * self.cell_size, row * self.cell_size))
            # White border on hovered cell
            r = pygame.Rect(col * self.cell_size, row * self.cell_size,
                            self.cell_size, self.cell_size)
            pygame.draw.rect(surface, self.c_white, r, 2)

    def _draw_type_buttons(self, surface):
        """Draw type selector in a horizontal bar below the grid."""
        self.btn_rects.clear()
        grid_h = self.rows * self.cell_size
        bar_y = grid_h + 4
        bar_h = 40

        # Background bar across grid area
        pygame.draw.rect(surface, self.c_bar_bg,
                         (0, bar_y, self.dashboard_x, bar_h))
        pygame.draw.line(surface, self.c_border,
                         (0, bar_y), (self.dashboard_x, bar_y))

        # Title
        title = self.font.render("Place:", True, self.c_dim)
        surface.blit(title, (10, bar_y + 12))

        # Type buttons side by side
        bx = 60
        bw, bh = 120, 30
        for i, cell_type in enumerate(EDITABLE_TYPES):
            rect = pygame.Rect(bx + i * (bw + 8), bar_y + 5, bw, bh)
            color = self.type_colors[cell_type]
            selected = i == self._type_index

            bg = color if selected else self.c_unsel
            pygame.draw.rect(surface, bg, rect, border_radius=4)
            border = self.c_white if selected else self.c_unsel_border
            pygame.draw.rect(surface, border, rect, 2, border_radius=4)

            # Color dot + label
            pygame.draw.circle(surface, color,
                               (rect.x + 14, rect.y + bh // 2), 6)
            lbl = self.btn_font.render(TYPE_NAMES[cell_type], True, self.c_label)
            surface.blit(lbl, (rect.x + 26, rect.y + 6))
            self.btn_rects.append((rect, i))

        hint = self.font.render("Click grid to place / remove", True, self.c_hint)
        surface.blit(hint, (bx + len(EDITABLE_TYPES) * (bw + 8) + 12, bar_y + 12))
