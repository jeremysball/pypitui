"""Tests for scrollback rendering - top border missing when content grows."""

from pypitui import TUI, BorderedBox, MockTerminal, Text


class TestScrollbackRenderBug:
    """Tests for scrollback lines not rendered when content grows.

    When a large component (e.g., 25+ line BorderedBox) is added to an
    empty TUI:
    - Top border lines are missing (blank instead of rendered)
    - Root cause: _handle_content_growth emits blank newlines, then
      _render_changed_lines only renders visible portion
    """

    def test_new_large_content_renders_scrollback_lines(self):
        """Top border should be rendered before scrolling into history."""
        # Setup: 24-row terminal
        terminal = MockTerminal(cols=80, rows=24)
        tui = TUI(terminal)

        # First render (empty)
        tui.start()
        tui.render_frame()
        terminal._buffer.clear()

        # Add a box with 25 lines (1 more than terminal height)
        box = BorderedBox(title="Test")
        for i in range(22):  # + title/sep/border = 25 lines total
            box.add_child(Text(f"Line {i}"))
        tui.add_child(box)

        # Render
        tui.request_render()
        tui.render_frame()

        # Check output
        output = "".join(terminal._buffer)

        tui.stop()

        # BUG: top border is missing because it scrolled into history
        # without being rendered first
        assert "┌" in output, "Top border should be rendered before scrolling"

    def test_multiple_scrollback_lines_rendered(self):
        """All lines that flow into scrollback should be rendered."""
        terminal = MockTerminal(cols=80, rows=10)
        tui = TUI(terminal)

        # First render (empty)
        tui.start()
        tui.render_frame()
        terminal._buffer.clear()

        # Add 15 lines of content (5 will go to scrollback)
        for i in range(15):
            tui.add_child(Text(f"Content line {i}", padding_y=0))

        # Render
        tui.request_render()
        tui.render_frame()

        output = "".join(terminal._buffer)

        tui.stop()

        # Lines 0-4 should be rendered before scrolling
        assert "Content line 0" in output
        assert "Content line 4" in output
