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


class TestTUILineOverflow:
    """Tests for line overflow protection."""

    def test_line_overflow_raises_error(self) -> None:
        """Line exceeding width raises LineOverflowError."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        from pypitui.terminal import Terminal
        from pypitui.tui import LineOverflowError, TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        # Try to render a line wider than allowed
        lines = [
            (0, "hash0", "This line is way too long for the width"),
        ]

        with pytest.raises(LineOverflowError):
            tui._output_diff(lines, width=10)

    def test_line_overflow_includes_context(self) -> None:
        """Error shows row, width, content length."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        from pypitui.terminal import Terminal
        from pypitui.tui import LineOverflowError, TUI

        mock_buffer = BytesIO()
        mock_buffer.fileno = MagicMock(return_value=1)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=1, buffer=mock_buffer)
                    tui = TUI(term)

        lines = [
            (5, "hash5", "x" * 50),  # 50 chars, max width 20
        ]

        with pytest.raises(LineOverflowError) as exc_info:
            tui._output_diff(lines, width=20)

        error_msg = str(exc_info.value)
        assert "5" in error_msg  # row
        assert "20" in error_msg  # width
        assert "50" in error_msg  # content length


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

    def test_scrollback_edit_clears_screen(self) -> None:
        """Scrollback edit triggers clear_screen()."""
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

        # Scrollback edit (line 5 < viewport_top 10)
        lines = [
            (5, "new_hash5", "Changed line 5"),  # in scrollback
            (10, "hash10", "Line 10"),
            (11, "hash11", "Line 11"),
        ]
        tui._output_diff(lines, 80)

        output = mock_buffer.getvalue()
        # Should have clear screen sequence
        assert b"\x1b[2J" in output

    def test_scrollback_edit_redraws_all_lines(self) -> None:
        """All visible lines redrawn after scrollback clear."""
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

        # Scrollback edit - should redraw all visible lines
        lines = [
            (5, "new_hash5", "Changed line 5"),  # in scrollback
            (10, "hash10", "Line 10"),
            (11, "hash11", "Line 11"),
        ]
        tui._output_diff(lines, 80)

        output = mock_buffer.getvalue()
        # All lines should be in output
        assert b"Changed line 5" in output
        assert b"Line 10" in output
        assert b"Line 11" in output

    def test_mixed_scrollback_edit_and_append_triggers_full_redraw(self) -> None:
        """Full redraw takes precedence over append optimization."""
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

        # Mixed scenario: scrollback edit (line 5) AND append (lines 20-21)
        # Scrollback should win - full redraw
        lines = [
            (5, "new_hash5", "Changed line 5"),  # scrollback edit
            (20, "hash20", "Line 20"),  # new line (append)
            (21, "hash21", "Line 21"),  # new line (append)
        ]
        tui._output_diff(lines, 80)

        output = mock_buffer.getvalue()
        # Should have clear screen (full redraw, not append)
        assert b"\x1b[2J" in output
        # All lines should be redrawn
        assert b"Changed line 5" in output
        assert b"Line 20" in output
        assert b"Line 21" in output


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
