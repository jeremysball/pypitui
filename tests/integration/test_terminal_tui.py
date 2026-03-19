"""Integration tests for Terminal + TUI rendering pipeline."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from pypitui.component import Component, RenderedLine, Size
from pypitui.mock_terminal import MockTerminal
from pypitui.terminal import Terminal
from pypitui.tui import TUI


class SimpleTextComponent(Component):
    """Test component that renders static text."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    def measure(self, available_width: int, available_height: int) -> Size:
        return Size(available_width, len(self.lines))

    def render(self, width: int) -> list[RenderedLine]:
        return [
            RenderedLine(line[:width], [])
            for line in self.lines
        ]


class TestTerminalTUIIntegration:
    """Integration tests for Terminal + TUI pipeline."""

    def test_full_render_pipeline(self) -> None:
        """TUI can render a component through Terminal."""
        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        component = SimpleTextComponent(["Hello", "World"])
        tui.add_child(component)

        # Render component
        lines = [
            (0, "hash0", "Hello"),
            (1, "hash1", "World"),
        ]
        tui._output_diff(lines, 80)

        output = mock_buffer.getvalue()
        assert b"Hello" in output
        assert b"World" in output

    def test_render_updates_previous_lines(self) -> None:
        """Rendering updates _previous_lines for diffing."""
        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        lines = [
            (0, "hash0", "Line 1"),
            (1, "hash1", "Line 2"),
        ]
        tui._output_diff(lines, 80)

        assert tui._previous_lines[0] == "hash0"
        assert tui._previous_lines[1] == "hash1"

    def test_second_render_only_changes_diff(self) -> None:
        """Second render only outputs changed lines."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # First render
        lines1 = [
            (0, "hash0", "Line 1"),
            (1, "hash1", "Line 2"),
        ]
        tui._output_diff(lines1, 80)
        first_escapes = mock_term.get_escape_count()

        # Reset counters
        mock_term.reset_counts()

        # Second render with one change
        lines2 = [
            (0, "hash0", "Line 1"),  # unchanged
            (1, "new_hash", "Changed"),  # changed
        ]
        tui._output_diff(lines2, 80)
        second_escapes = mock_term.get_escape_count()

        # Second render should use fewer escapes
        assert second_escapes < first_escapes

    def test_viewport_scrolls_with_content(self) -> None:
        """Viewport tracks content that exceeds terminal height."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # Content shorter than terminal
        viewport_top = tui._calculate_viewport_top(10)
        assert viewport_top == 0

        # Content taller than terminal
        viewport_top = tui._calculate_viewport_top(30)
        assert viewport_top == 6  # 30 - 24 = 6

    def test_render_with_viewport_offset(self) -> None:
        """Render applies viewport offset to cursor positioning."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # Simulate scrolled viewport
        tui._viewport_top = 10

        # Render line at row 15 (should appear at row 5 on screen)
        lines = [(15, "hash", "Content")]
        tui._output_diff(lines, 80)

        # Check that cursor was positioned with offset
        output = mock_term.get_output()
        # Should have CSI 6;1H (row 6, col 1 for 1-indexed terminal)
        assert b"\x1b[6;1H" in output


class TestMockTerminalIntegration:
    """Integration tests using MockTerminal."""

    def test_mock_terminal_counts_escapes(self) -> None:
        """MockTerminal correctly counts escape sequences."""
        mock_term = MockTerminal(width=80, height=24)

        mock_term.move_cursor(0, 0)
        mock_term.clear_line()
        mock_term.write("Hello")

        assert mock_term.get_escape_count() == 2  # move + clear
        assert b"Hello" in mock_term.get_output()

    def test_mock_terminal_reset(self) -> None:
        """MockTerminal reset clears counters and buffer."""
        mock_term = MockTerminal(width=80, height=24)

        mock_term.move_cursor(0, 0)
        mock_term.write("Content")

        mock_term.reset_counts()

        assert mock_term.get_escape_count() == 0
        assert mock_term.get_write_count() == 0
        assert mock_term.get_output() == b""
