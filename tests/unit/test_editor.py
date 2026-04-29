"""Tests for ``dronerl.editor.Editor`` (in-place obstacle editor)."""

from dronerl.editor import EDITABLE_TYPES, TYPE_NAMES, Editor
from dronerl.environment import CellType


def test_editor_draw_and_click_flow(ui_config, ui_surface):
    editor = Editor(ui_config)
    editor.draw_ui(ui_surface, (10, 10))
    assert editor.btn_rects
    assert editor.handle_click((10, 10)) == (0, 0, editor.selected_type)

    rect, index = editor.btn_rects[-1]
    editor.handle_click(rect.center)
    assert editor.selected_type == EDITABLE_TYPES[index]

    current = editor.selected_type
    editor.next_type()
    assert editor.selected_type != current
    assert editor.handle_click((9999, 9999)) is None


def test_editor_pit_metadata_and_placement_tracking(ui_config, ui_env):
    """PIT is editable, has a label and color, cycles in rotation, and tracks in editor_cells."""
    editor = Editor(ui_config)
    assert CellType.PIT in EDITABLE_TYPES
    assert TYPE_NAMES[CellType.PIT] == "Pit"
    assert CellType.PIT in editor.type_colors
    assert editor.type_colors[CellType.PIT] == tuple(ui_config.colors.pit)

    # Cycling eventually hits PIT.
    seen = set()
    for _ in range(len(EDITABLE_TYPES)):
        seen.add(editor.selected_type)
        editor.next_type()
    assert CellType.PIT in seen

    # Placing PIT via environment.set_cell tracks it in editor_cells.
    ui_env.set_cell(0, 1, CellType.PIT, editor=True)
    assert (0, 1) in ui_env.editor_cells
    assert int(ui_env.grid[0, 1]) == int(CellType.PIT)


def test_editor_draws_pit_button_with_pit_color(ui_config, ui_surface):
    """draw_ui renders a button for the PIT type using its config color."""
    editor = Editor(ui_config)
    editor.draw_ui(ui_surface, (0, 0))
    assert editor.btn_rects
    pit_idx = EDITABLE_TYPES.index(CellType.PIT)
    indexes = [idx for _rect, idx in editor.btn_rects]
    assert pit_idx in indexes
    assert editor.type_colors[CellType.PIT] == tuple(ui_config.colors.pit)
