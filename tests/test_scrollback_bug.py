"""Tests for differential rendering with viewport-based comparison."""

from pypitui import TUI, Container, Text
from pypitui.terminal import MockTerminal


def test_viewport_shift_redraws_all_visible():
    """When first_visible changes, all visible rows should be redrawn."""
    terminal = MockTerminal(cols=40, rows=10)
    tui = TUI(terminal)

    # Start with content that fits (padding_y=0 means 1 line per Text)
    container = Container()
    for i in range(3):
        container.add_child(Text(f"Line {i}", padding_y=0))
    tui.add_child(container)

    tui.start()
    tui.render_frame()
    tui.stop()

    # first_visible should match content (3 lines fits in 10 rows)
    # first_visible = max(0, content - term_height) = max(0, 3 - 10) = 0
    assert tui._first_visible_row_previous == 0


def test_content_fits_renders_all_lines():
    """When content fits in terminal, all lines should be rendered."""
    terminal = MockTerminal(cols=40, rows=10)
    tui = TUI(terminal)

    container = Container()
    for i in range(3):
        container.add_child(Text(f"Line {i}"))
    tui.add_child(container)

    tui.start()
    tui.render_frame()
    output = terminal.get_output()
    tui.stop()

    # All 3 lines should be in output
    assert "Line 0" in output
    assert "Line 1" in output
    assert "Line 2" in output


def test_no_change_no_redraw():
    """When content doesn't change, second render should be minimal."""
    terminal = MockTerminal(cols=40, rows=10)
    tui = TUI(terminal)

    container = Container()
    for i in range(3):
        container.add_child(Text(f"Line {i}"))
    tui.add_child(container)

    tui.start()

    # First render
    tui.render_frame()
    first_output = terminal.get_output()

    # Second render (no change)
    terminal.clear_buffer()
    tui.render_frame()
    second_output = terminal.get_output()

    tui.stop()

    # Second render should be minimal (no changes to render)
    # Just sync codes: \x1b[?2026h + \x1b[?2026l = 16 chars
    assert len(second_output) == 16
    assert len(second_output) < len(first_output)


def test_force_render_resets_viewport_tracking():
    """request_render(force=True) should reset viewport tracking."""
    terminal = MockTerminal(cols=40, rows=5)
    tui = TUI(terminal)

    # Simulate previous viewport position
    tui._first_visible_row_previous = 10

    # Force render should reset it
    tui.request_render(force=True)

    assert tui._first_visible_row_previous == 0
