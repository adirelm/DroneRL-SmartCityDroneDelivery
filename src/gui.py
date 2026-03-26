"""Main GUI orchestrator for the DroneRL project."""

import pygame

from src.actions import dispatch
from src.agent import Agent
from src.config_loader import Config
from src.dashboard import Dashboard
from src.editor import Editor
from src.environment import CellType, Environment
from src.game_logic import GameLogic
from src.overlays import Overlays
from src.renderer import Renderer


class GUI:
    """Top-level orchestrator: event loop, rendering, and action dispatch."""

    BRAIN_PATH = "data/brain.npy"

    def __init__(self, config: Config):
        pygame.init()
        self.cfg, gui = config, config.gui
        self.width, self.height = gui.window_width, gui.window_height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("DroneRL \u2014 Smart City Drone Delivery")
        self.clock, self.fps = pygame.time.Clock(), gui.fps
        self.env, self.agent = Environment(config), Agent(config)
        self.logic = GameLogic(self.agent, self.env, config)
        self.renderer, self.overlays = Renderer(config), Overlays(config)
        self.dashboard, self.editor = Dashboard(config), Editor(config)
        self.paused, self.editor.active = True, True
        self.fast_mode = self.show_heatmap = self.show_arrows = False
        self.status_font = None

    def _state(self):
        return {"paused": self.paused, "fast_mode": self.fast_mode,
                "show_heatmap": self.show_heatmap, "show_arrows": self.show_arrows,
                "editor_active": self.editor.active, "demo_mode": self.logic.demo_mode,
                "has_trained": self.logic.episode > 0,
                "converged": self.logic.converged}

    def run(self):
        """Run the main Pygame event loop."""
        running = True
        while running:
            self.dashboard.buttons.handle_hover(pygame.mouse.get_pos())
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    self._on_key(ev.key)
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    self._on_click(ev.pos)
            if self.logic.demo_mode:
                self.logic.demo_step(self.fps)
            elif not self.paused and not self.editor.active:
                for _ in range(100 if self.fast_mode else 1):
                    self.logic.training_step()
                if self.logic.check_convergence():
                    self.paused = True
                    self.show_heatmap = self.show_arrows = True
            self._draw()
            self.clock.tick(self.fps)
        pygame.quit()

    def _on_click(self, pos):
        act = self.dashboard.buttons.handle_click(pos)
        if act:
            return dispatch(self, act)
        if self.editor.active:
            r = self.editor.handle_click(pos)
            if r:
                cur = self.env.get_cell(r[0], r[1])
                self.env.set_cell(r[0], r[1], CellType.EMPTY if cur == r[2] else r[2])

    def _on_key(self, key):
        km = {pygame.K_SPACE: "primary", pygame.K_f: "toggle_fast",
              pygame.K_h: "toggle_heatmap", pygame.K_a: "toggle_arrows",
              pygame.K_e: "open_editor", pygame.K_d: "start_demo",
              pygame.K_s: "save", pygame.K_l: "load",
              pygame.K_r: "reset", pygame.K_t: "cycle_type"}
        if key in km:
            dispatch(self, km[key])

    def _draw(self):
        self.screen.fill(tuple(self.cfg.colors.background))
        self.renderer.draw_grid(self.screen, self.env.grid)
        if self.show_heatmap:
            self.overlays.draw_heatmap(self.screen, self.agent.q_table, self.env.grid)
        if self.show_arrows:
            self.overlays.draw_arrows(self.screen, self.agent.q_table, self.env.grid)
        self.renderer.draw_grid_lines(self.screen)
        self.overlays.draw_labels(self.screen)
        if self.logic.demo_mode and self.logic.demo_trail:
            self.overlays.draw_trail(self.screen, self.logic.demo_trail)
        self.renderer.draw_drone(self.screen, self.env.drone_pos)
        self.dashboard.draw(self.screen, self.logic.get_metrics(),
                            self.logic.reward_history, self._state())
        if self.editor.active:
            self.editor.draw_ui(self.screen, pygame.mouse.get_pos())
        self._status_bar()
        pygame.display.flip()

    def _status_bar(self):
        if not self.status_font:
            self.status_font = pygame.font.SysFont("arial", 13)
        modes = {"EDIT": self.editor.active, "DEMO": self.logic.demo_mode,
                 "PAUSED": self.paused, "FAST TRAINING": self.fast_mode}
        mode = next((m for m, v in modes.items() if v), "TRAINING")
        y = self.height - 24
        pygame.draw.rect(self.screen, (12, 14, 28), (0, y, self.width, 24))
        self.screen.blit(self.status_font.render(
            f"  [{mode}]  SPACE: primary action", True, (160, 165, 190)), (4, y + 4))
