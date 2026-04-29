"""Immutable project-wide constants.

Per the course-wide submission guidelines (§7.3), values that are
genuine constants (mathematical / structural / definitional) live
here, not in ``config/config.yaml``. The config file is for *tunable*
parameters; this module is for facts about the problem itself that
no user, grader, or experiment will ever want to change.

Anything tunable (rewards, hyperparameters, GUI dimensions, the
colour palette) lives in ``config/config.yaml`` per CLAUDE.md rule #4.
"""

from __future__ import annotations

# --- Action space --------------------------------------------------------

#: Number of discrete actions a drone can take in this environment.
#: The four actions correspond to the four cardinal directions defined
#: by ``ACTION_DELTAS``. Changing this number requires a full redesign
#: of the agent / environment contract.
NUM_ACTIONS: int = 4

#: Mapping from action index to ``(row_delta, col_delta)`` movement.
#: Action 0 = UP, 1 = DOWN, 2 = LEFT, 3 = RIGHT. The dict ordering is
#: contract-level — agents and the environment both rely on it.
ACTION_DELTAS: dict[int, tuple[int, int]] = {
    0: (-1, 0),  # UP
    1: (1, 0),   # DOWN
    2: (0, -1),  # LEFT
    3: (0, 1),   # RIGHT
}

__all__ = ["ACTION_DELTAS", "NUM_ACTIONS"]
