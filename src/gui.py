"""Main GUI orchestrator for the DroneRL project."""

import pygame

from src.actions import dispatch
from src.agent_factory import create_agent
from src.config_loader import Config
from src.dashboard import Dashboard
from src.editor import Editor
from src.environment import CellType, Environment
from src.game_logic import GameLogic
from src.hazard_generator import HazardGenerator
from src.overlays import Overlays
from src.renderer import Renderer
from src.sliders import SliderPanel


class GUI:
    """Top-level orchestrator: event loop, rendering, and action dispatch."""

    def __init__(self, config: Config):
        """Initialise window, components, and state from config."""
        pygame.init()
        self.cfg, gui = config, config.gui
        self.width, self.height = gui.window_width, gui.window_height
        self.brain_path = config.paths.brain
        self.fast_step_batch = gui.fast_mode_episodes_per_frame
        self.status_bar_height = gui.status_bar_height
        self.status_font_size = gui.status_bar_font_size
        self.font_name = gui.font_name
        c = config.colors
        self.c_status_bg, self.c_status_text = tuple(c.dashboard_bg), tuple(c.status_text)
        self.c_status_dim = tuple(c.status_dim)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("DroneRL \u2014 Smart City Drone Delivery")
        self.clock, self.fps = pygame.time.Clock(), gui.fps
        self.env, self.agent = Environment(config), create_agent(config)
        self.logic = GameLogic(self.agent, self.env, config)
        self.renderer, self.overlays = Renderer(config), Overlays(config)
        self.dashboard, self.editor = Dashboard(config), Editor(config)
        self.hazards = HazardGenerator(config)
        sx, sy = gui.grid_area_width + 16, self.height - self.status_bar_height - 130
        self.sliders = SliderPanel(config, sx, sy, gui.dashboard_width - 32)
        self.paused, self.editor.active = True, True
        self.fast_mode = self.show_heatmap = self.show_arrows = False
        self.status_font = None
        if getattr(config.dynamic_board, "randomize_per_episode", False):
            self.logic.on_episode_end = lambda: (
                self.hazards.apply(self.env),
                self.env.set_wind_drift(self.hazards.effective_drift()),
            )

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
                elif self.editor.active and self.sliders.handle_event(ev):
                    self._on_slider_change()
                elif ev.type == pygame.KEYDOWN:
                    self._on_key(ev.key)
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    self._on_click(ev.pos)
            if self.logic.demo_mode:
                self.logic.demo_step(self.fps)
            elif not self.paused and not self.editor.active:
                for _ in range(self.fast_step_batch if self.fast_mode else 1):
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
                new = CellType.EMPTY if cur == r[2] else r[2]
                self.env.set_cell(r[0], r[1], new, editor=True)

    def _on_key(self, key):
        km = {pygame.K_SPACE: "primary", pygame.K_f: "toggle_fast",
              pygame.K_h: "toggle_heatmap", pygame.K_a: "toggle_arrows",
              pygame.K_e: "open_editor", pygame.K_d: "start_demo",
              pygame.K_s: "save", pygame.K_l: "load",
              pygame.K_r: "reset", pygame.K_t: "cycle_type",
              pygame.K_1: "use_bellman", pygame.K_2: "use_q_learning",
              pygame.K_3: "use_double_q", pygame.K_g: "regenerate_hazards",
              pygame.K_c: "run_comparison"}
        if key in km:
            dispatch(self, km[key])

    def _on_slider_change(self):
        s = self.sliders
        self.hazards.set_noise(s.get("noise"))
        self.hazards.set_density(s.get("density"))
        self.hazards.set_difficulty(s.get("difficulty"))
        self.env.set_wind_drift(self.hazards.effective_drift())

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
            self.sliders.draw(self.screen)
        self._status_bar()
        pygame.display.flip()

    def _status_bar(self):
        """Render the mode indicator and keyboard shortcuts bar."""
        if not self.status_font:
            self.status_font = pygame.font.SysFont(self.font_name, self.status_font_size)
        mode = "EDIT" if self.editor.active else "DEMO" if self.logic.demo_mode else "TRAINING"
        flags = (["PAUSED"] if self.paused else []) + (["FAST"] if self.fast_mode else [])
        state = f"Mode: {mode}  Algo: {self.agent.algorithm_name}"
        state += f" [{' | '.join(flags)}]" if flags else ""
        shortcuts = ("SPACE Play/Pause  F Fast  H Heatmap  A Arrows  E Editor  "
                     "T Tool  D Demo  S Save  L Load  R Reset  "
                     "1 Bellman  2 Q-Learn  3 DoubleQ  G Hazards  C Compare")
        y = self.height - self.status_bar_height
        pygame.draw.rect(self.screen, self.c_status_bg, (0, y, self.width, self.status_bar_height))
        self.screen.blit(self.status_font.render(state, True, self.c_status_text), (10, y + 6))
        self.screen.blit(self.status_font.render(shortcuts, True, self.c_status_dim), (10, y + 22))
