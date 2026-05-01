"""Unit tests for ``dronerl.constants`` — preserve the action-space contract.

Closes the §6.2 / Pass-3 "1:1 module ↔ unit test" mapping gap by giving
``constants.py`` a dedicated test file. The module is small and
contract-level, but a regression test here pins the
agent ↔ environment movement convention so a future refactor can't
silently swap UP/DOWN or change the action count.
"""

from dronerl.constants import ACTION_DELTAS, NUM_ACTIONS


class TestNumActions:
    def test_is_four(self):
        """Four cardinal directions — changing this number changes the API."""
        assert NUM_ACTIONS == 4

    def test_matches_deltas_length(self):
        assert len(ACTION_DELTAS) == NUM_ACTIONS


class TestActionDeltas:
    def test_is_dict_indexed_zero_through_num_actions(self):
        assert set(ACTION_DELTAS.keys()) == set(range(NUM_ACTIONS))

    def test_up_is_negative_row(self):
        """Action 0 = UP: row -1, col unchanged."""
        assert ACTION_DELTAS[0] == (-1, 0)

    def test_down_is_positive_row(self):
        """Action 1 = DOWN: row +1, col unchanged."""
        assert ACTION_DELTAS[1] == (1, 0)

    def test_left_is_negative_col(self):
        """Action 2 = LEFT: row unchanged, col -1."""
        assert ACTION_DELTAS[2] == (0, -1)

    def test_right_is_positive_col(self):
        """Action 3 = RIGHT: row unchanged, col +1."""
        assert ACTION_DELTAS[3] == (0, 1)

    def test_each_delta_is_unit_step(self):
        """Every action moves exactly one cell in some direction (no diagonals, no stays)."""
        for delta in ACTION_DELTAS.values():
            assert sum(abs(d) for d in delta) == 1

    def test_deltas_sum_to_zero(self):
        """Opposite directions cancel — a structural sanity check on the cardinal set."""
        total_row = sum(dr for dr, _ in ACTION_DELTAS.values())
        total_col = sum(dc for _, dc in ACTION_DELTAS.values())
        assert (total_row, total_col) == (0, 0)
