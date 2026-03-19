"""Unit tests for TUI rendering engine."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest


class TestTUIInit:
    """Tests for TUI initialization."""

    def test_tui_init_caches_previous_lines(self) -> None:
        """_previous_lines is empty dict row->content_hash."""
        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        assert isinstance(tui._previous_lines, dict)
        assert len(tui._previous_lines) == 0

    def test_tui_init_tracks_max_lines(self) -> None:
        """_max_lines_rendered starts at 0."""
        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        assert tui._max_lines_rendered == 0

    def test_tui_init_tracks_viewport_top(self) -> None:
        """_viewport_top starts at 0."""
        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        assert tui._viewport_top == 0

    def test_tui_init_hardware_cursor(self) -> None:
        """_hardware_cursor_row and _hardware_cursor_col tracked."""
        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        assert tui._hardware_cursor_row == 0
        assert tui._hardware_cursor_col == 0


class TestTUIAddChild:
    """Tests for TUI add_child."""

    def test_tui_add_child_sets_root(self) -> None:
        """add_child stores component."""
        from pypitui.component import Component
        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        class MockComponent(Component):
            def measure(self, available_width: int, available_height: int):
                from pypitui.component import Size
                return Size(10, 1)

            def render(self, width: int):
                from pypitui.component import RenderedLine, StyleSpan
                return [RenderedLine("test", [])]

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        mock_comp = MockComponent()
        tui.add_child(mock_comp)

        assert tui._root is mock_comp
