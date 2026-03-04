"""Tests for scrollback rendering - visible portion rendered correctly."""

from pypitui import TUI, BorderedBox, MockTerminal, Text


class TestScrollbackRenderBug:
    """Tests for visible portion rendering when content exceeds terminal.

    When content exceeds terminal height, only the visible portion is
    rendered. Lines that scroll into the terminal's native scrollback
    buffer are not addressable by ANSI codes.
    """

    def test_visible_portion_rendered(self):
        """When content exceeds terminal, visible portion is rendered."""
        terminal = MockTerminal(cols=80, rows=10)
        tui = TUI(terminal)

        # Add content that exceeds terminal height
        box = BorderedBox(title="Test")
        for i in range(15):  # 15 lines + borders = more than 10
            box.add_child(Text(f"Line {i}"))
        tui.add_child(box)

        tui.start()
        tui.render_frame()
        output = "".join(terminal._buffer)
        tui.stop()

        # Bottom border should be visible (it's at the bottom of content)
        assert "└" in output, "Bottom border should be rendered"

    def test_content_fits_all_visible(self):
        """When content fits, all lines are visible."""
        terminal = MockTerminal(cols=80, rows=24)
        tui = TUI(terminal)

        box = BorderedBox(title="Test")
        for i in range(5):
            box.add_child(Text(f"Line {i}"))
        tui.add_child(box)

        tui.start()
        tui.render_frame()
        output = "".join(terminal._buffer)
        tui.stop()

        # Both borders should be visible
        assert "┌" in output, "Top border should be rendered"
        assert "└" in output, "Bottom border should be rendered"

    def test_growing_content_updates_visible(self):
        """When content grows, visible portion updates correctly."""
        terminal = MockTerminal(cols=80, rows=10)
        tui = TUI(terminal)

        # Start with small content
        box = BorderedBox(title="Test")
        box.add_child(Text("Single line"))
        tui.add_child(box)

        tui.start()
        tui.render_frame()
        terminal._buffer.clear()

        # Add more content
        for i in range(10):
            box.add_child(Text(f"New line {i}"))

        tui.request_render()
        tui.render_frame()
        output = "".join(terminal._buffer)
        tui.stop()

        # Should have rendered something
        assert len(output) > 0
