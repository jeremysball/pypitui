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


class TestTUIViewportTracking:
    """Tests for TUI viewport tracking."""

    def test_viewport_top_calculation(self) -> None:
        """viewport_top = max(0, content_height - term_height)."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        # Test content shorter than terminal (24 lines)
        viewport_top = tui._calculate_viewport_top(10)
        assert viewport_top == 0, f"Expected 0, got {viewport_top}"

        # Test content taller than terminal
        viewport_top = tui._calculate_viewport_top(30)
        assert viewport_top == 6, f"Expected 6, got {viewport_top}"

        # Test content exactly matching terminal height
        viewport_top = tui._calculate_viewport_top(24)
        assert viewport_top == 0, f"Expected 0, got {viewport_top}"

    def test_viewport_top_zero_when_content_fits(self) -> None:
        """3 lines on 24-line terminal = 0."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        viewport_top = tui._calculate_viewport_top(3)
        assert viewport_top == 0

    def test_viewport_top_nonzero_when_content_scrolls(self) -> None:
        """30 lines on 24-line terminal = 6."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        viewport_top = tui._calculate_viewport_top(30)
        assert viewport_top == 6


class TestTUIScrollbackAwareRedraw:
    """Tests for scrollback-aware redraw (CRITICAL)."""

    def test_edit_in_scrollback_triggers_full_redraw(self) -> None:
        """first_changed < viewport_top triggers clear."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        # Set up viewport with scrollback (viewport_top = 10)
        tui._viewport_top = 10
        tui._previous_lines = {i: f"hash{i}" for i in range(20)}

        # Edit at line 5 (in scrollback, since viewport starts at 10)
        is_scrollback = tui._is_scrollback_edit(first_changed=5, viewport_top=10)
        assert is_scrollback is True

    def test_edit_in_viewport_does_not_clear(self) -> None:
        """first_changed >= viewport_top uses diff."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        # Set up viewport with scrollback
        tui._viewport_top = 10
        tui._previous_lines = {i: f"hash{i}" for i in range(20)}

        # Edit at line 12 (in viewport, since viewport starts at 10)
        is_scrollback = tui._is_scrollback_edit(first_changed=12, viewport_top=10)
        assert is_scrollback is False

    def test_scrollback_at_viewport_boundary(self) -> None:
        """first_changed == viewport_top is in viewport (not scrollback)."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        # Edit exactly at viewport top
        is_scrollback = tui._is_scrollback_edit(first_changed=10, viewport_top=10)
        assert is_scrollback is False


class TestTUIDifferentialRendering:
    """Tests for TUI differential rendering."""

    def test_find_changed_bounds_identifies_range(self) -> None:
        """Returns (first, last) changed indices."""
        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        # Set up previous state
        tui._previous_lines = {
            0: "hash0",
            1: "hash1",
            2: "hash2",
            3: "hash3",
            4: "hash4",
        }

        # New lines with changes at lines 1 and 3
        new_lines = [
            (0, "hash0"),  # unchanged
            (1, "new_hash1"),  # changed
            (2, "hash2"),  # unchanged
            (3, "new_hash3"),  # changed
            (4, "hash4"),  # unchanged
        ]

        first, last = tui._find_changed_bounds(new_lines)
        assert first == 1
        assert last == 3

    def test_output_diff_writes_changed_lines(self) -> None:
        """Only changed lines emit escape sequences."""
        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        # Set up previous state
        tui._previous_lines = {0: "hash0", 1: "hash1_old", 2: "hash2"}

        # Output lines with change at line 1
        lines = [(0, "hash0", "line0"), (1, "hash1_new", "line1_new"), (2, "hash2", "line2")]
        tui._output_diff(lines, 80)

        output = mock_buffer.getvalue()
        # Should emit escape sequences for changed line (line 1)
        assert b"line1_new" in output
        # Should have cursor positioning
        assert b"\x1b[" in output

    def test_output_diff_skips_unchanged_lines(self) -> None:
        """Unchanged lines generate no output."""
        from pypitui.terminal import Terminal
        from pypitui.tui import TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        # Set up previous state where all lines are same
        tui._previous_lines = {0: "hash0", 1: "hash1", 2: "hash2"}

        # Output lines with no changes
        lines = [(0, "hash0", "line0"), (1, "hash1", "line1"), (2, "hash2", "line2")]
        tui._output_diff(lines, 80)

        output = mock_buffer.getvalue()
        # Should generate minimal or no output for unchanged lines
        assert len(output) == 0 or b"line0" not in output
