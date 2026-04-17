"""Dynamic hazard generator for the DroneRL environment."""

import random

from src.config_loader import Config
from src.environment import CellType, Environment

HAZARD_TYPES = (CellType.BUILDING, CellType.TRAP, CellType.PIT, CellType.WIND)


class HazardGenerator:
    """Populates the grid with random hazards based on sliders + config."""

    def __init__(self, config: Config):
        cfg = config.dynamic_board
        self.noise = cfg.noise_level
        self.density = cfg.hazard_density
        self.difficulty = cfg.difficulty
        self.ratios = {
            CellType.BUILDING: cfg.building_ratio,
            CellType.TRAP: cfg.trap_ratio,
            CellType.PIT: cfg.pit_ratio,
            CellType.WIND: cfg.wind_ratio,
        }
        self._rng = random.Random(cfg.seed) if cfg.seed is not None else random.Random()
        self._base_drift = config.wind.drift_probability

    def set_noise(self, value: float) -> None:
        """Update noise slider (0..1)."""
        self.noise = max(0.0, min(1.0, float(value)))

    def set_density(self, value: float) -> None:
        """Update density slider (0..0.5)."""
        self.density = max(0.0, min(0.5, float(value)))

    def set_difficulty(self, value: float) -> None:
        """Update difficulty slider (0..1)."""
        self.difficulty = max(0.0, min(1.0, float(value)))

    def effective_density(self) -> float:
        """Density multiplied by difficulty, clamped to 0.5."""
        return min(0.5, self.density * (0.5 + self.difficulty))

    def effective_drift(self) -> float:
        """Base wind drift * noise slider * (1 + difficulty)."""
        drift = self._base_drift * self.noise * (1.0 + self.difficulty)
        return max(0.0, min(1.0, drift))

    def apply(self, env: Environment) -> int:
        """Clear auto-hazards then place new ones. Returns number placed."""
        self._clear_hazards(env)
        eligible = [
            (r, c) for r in range(env.rows) for c in range(env.cols)
            if env.grid[r, c] == CellType.EMPTY
            and not env._is_protected_cell(r, c)
            and (r, c) not in env._editor_cells
        ]
        target = int(len(eligible) * self.effective_density())
        target = min(target, len(eligible))
        if target == 0:
            return 0
        self._rng.shuffle(eligible)
        placed = 0
        for (r, c), cell_type in zip(eligible[:target], self._sample_types(target), strict=False):
            env.grid[r, c] = int(cell_type)
            placed += 1
        return placed

    def _clear_hazards(self, env: Environment) -> None:
        """Reset auto-placed hazards but preserve protected and editor cells."""
        for r in range(env.rows):
            for c in range(env.cols):
                if env._is_protected_cell(r, c) or (r, c) in env._editor_cells:
                    continue
                if env.grid[r, c] in [int(t) for t in HAZARD_TYPES]:
                    env.grid[r, c] = int(CellType.EMPTY)

    def _sample_types(self, n: int) -> list[CellType]:
        """Sample n hazard types according to configured ratios."""
        total = sum(self.ratios.values()) or 1.0
        weights = [self.ratios[t] / total for t in HAZARD_TYPES]
        return self._rng.choices(HAZARD_TYPES, weights=weights, k=n)
