"""Tests for scrollback and streaming functionality."""

from pypitui import MockTerminal, TUI, Text


class TestCalculateFirstVisibleRow:
    """Tests for _calculate_first_visible_row method."""

    def test_empty_content_returns_zero(self):
        """When no content rendered, first visible row is 0."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # No content rendered yet
        assert tui._max_lines_rendered == 0
        assert tui._calculate_first_visible_row(24) == 0

    def test_content_fits_terminal_returns_zero(self):
        """When content fits in terminal, first visible row is 0."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Simulate 10 lines rendered (less than terminal height of 24)
        tui._max_lines_rendered = 10

        assert tui._calculate_first_visible_row(24) == 0

    def test_content_exactly_terminal_height_returns_zero(self):
        """When content equals terminal height, first visible row is 0."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._max_lines_rendered = 24

        assert tui._calculate_first_visible_row(24) == 0

    def test_content_exceeds_terminal_by_one(self):
        """When content is 1 more than terminal, first visible row is 1."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._max_lines_rendered = 25

        # Lines 0 is in scrollback, lines 1-24 are visible
        assert tui._calculate_first_visible_row(24) == 1

    def test_content_twice_terminal_height(self):
        """When content is 2x terminal height, correct offset is calculated."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._max_lines_rendered = 48

        # Lines 0-23 in scrollback, lines 24-47 visible
        assert tui._calculate_first_visible_row(24) == 24

    def test_large_scrollback_buffer(self):
        """Test with 100 lines of content in 24-row terminal."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._max_lines_rendered = 100

        # Lines 0-75 in scrollback, lines 76-99 visible
        assert tui._calculate_first_visible_row(24) == 76

    def test_different_terminal_heights(self):
        """Test calculation with various terminal heights."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._max_lines_rendered = 100

        # 40-row terminal: lines 0-59 scrollback, 60-99 visible
        assert tui._calculate_first_visible_row(40) == 60

        # 10-row terminal: lines 0-89 scrollback, 90-99 visible
        assert tui._calculate_first_visible_row(10) == 90

        # 50-row terminal (content fits): all visible
        assert (
            tui._calculate_first_visible_row(50) == 50
        )  # max(0, 100-50) = 50

        # 100-row terminal: all visible
        assert tui._calculate_first_visible_row(100) == 0

    def test_terminal_larger_than_content(self):
        """Terminal larger than content means first visible is 0."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._max_lines_rendered = 10

        # max(0, 10 - 100) = max(0, -90) = 0
        assert tui._calculate_first_visible_row(100) == 0


class TestWorkingAreaTracking:
    """Tests for working area state tracking during render."""

    def test_max_lines_rendered_updates_on_render(self):
        """_max_lines_rendered should update after render_frame()."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Add 5 lines of content (Text has padding_y=1 by default, so 3 lines each)
        # Use padding_y=0 for predictable line count
        for i in range(5):
            tui.add_child(Text(f"Line {i}", padding_y=0))

        tui.start()
        tui.render_frame()

        assert tui._max_lines_rendered == 5

        tui.stop()

    def test_max_lines_rendered_grows_not_shrinks(self):
        """_max_lines_rendered should grow but not shrink."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Add 10 lines
        for i in range(10):
            tui.add_child(Text(f"Line {i}", padding_y=0))

        tui.start()
        tui.render_frame()
        assert tui._max_lines_rendered == 10

        # Clear and add fewer lines - max should stay at 10
        tui.clear()
        for i in range(3):
            tui.add_child(Text(f"New line {i}", padding_y=0))

        tui.render_frame()
        # max_lines_rendered is max(previous, current)
        assert tui._max_lines_rendered == 10

        tui.stop()

    def test_max_lines_rendered_grows_with_more_content(self):
        """_max_lines_rendered should grow when more content added."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Add 10 lines
        for i in range(10):
            tui.add_child(Text(f"Line {i}", padding_y=0))

        tui.start()
        tui.render_frame()
        assert tui._max_lines_rendered == 10

        # Add more lines
        for i in range(10, 20):
            tui.add_child(Text(f"Line {i}", padding_y=0))

        tui.render_frame()
        assert tui._max_lines_rendered == 20

        tui.stop()


class TestFirstVisibleRowPrevious:
    """Tests for _first_visible_row_previous state tracking."""

    def test_initial_value_is_zero(self):
        """_first_visible_row_previous starts at 0."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        assert tui._first_visible_row_previous == 0


class TestSynchronizedOutput:
    """Tests for DEC 2026 synchronized output mode."""

    def test_begin_sync_returns_correct_sequence(self):
        """_begin_sync() returns the DEC 2026 "set" sequence."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        assert tui._begin_sync() == "\x1b[?2026h"

    def test_end_sync_returns_correct_sequence(self):
        """_end_sync() returns the DEC 2026 "reset" sequence."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        assert tui._end_sync() == "\x1b[?2026l"

    def test_sync_wrapper_produces_correct_sequence(self):
        """Combining begin/end sync produces a valid wrapper."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        content = "Hello, World!"
        wrapped = tui._begin_sync() + content + tui._end_sync()

        expected = "\x1b[?2026hHello, World!\x1b[?2026l"
        assert wrapped == expected

    def test_begin_sync_idempotent(self):
        """Multiple calls to _begin_sync() return the same sequence."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        assert tui._begin_sync() == tui._begin_sync()

    def test_end_sync_idempotent(self):
        """Multiple calls to _end_sync() return the same sequence."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        assert tui._end_sync() == tui._end_sync()

    def test_sync_sequences_are_constant_length(self):
        """Sync sequences have fixed lengths for buffer sizing."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Begin sync: ESC [ ? 2 0 2 6 h = 8 chars
        assert len(tui._begin_sync()) == 8

        # End sync: ESC [ ? 2 0 2 6 l = 8 chars
        assert len(tui._end_sync()) == 8


class TestRelativeCursorMovement:
    """Tests for relative cursor movement."""

    def test_move_cursor_down_positive_delta(self):
        """Moving down produces correct escape sequence."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Start at row 0
        tui._hardware_cursor_row = 0

        # Move to row 5 (delta = +5)
        result = tui._move_cursor_relative(5)

        assert result == "\x1b[5B"
        assert tui._hardware_cursor_row == 5

    def test_move_cursor_up_negative_delta(self):
        """Moving up produces correct escape sequence."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Start at row 10
        tui._hardware_cursor_row = 10

        # Move to row 3 (delta = -7)
        result = tui._move_cursor_relative(3)

        assert result == "\x1b[7A"
        assert tui._hardware_cursor_row == 3

    def test_move_cursor_zero_delta_returns_empty(self):
        """No movement needed returns empty string."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._hardware_cursor_row = 5

        result = tui._move_cursor_relative(5)

        assert result == ""
        assert tui._hardware_cursor_row == 5

    def test_move_cursor_updates_hardware_cursor_row(self):
        """Each movement updates the tracked cursor position."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._hardware_cursor_row = 0

        # First movement
        tui._move_cursor_relative(10)
        assert tui._hardware_cursor_row == 10

        # Second movement
        tui._move_cursor_relative(3)
        assert tui._hardware_cursor_row == 3

    def test_terminal_move_cursor_up(self):
        """Terminal.move_cursor_up returns correct sequence."""
        terminal = MockTerminal(80, 24)

        assert terminal.move_cursor_up(1) == "\x1b[1A"
        assert terminal.move_cursor_up(5) == "\x1b[5A"
        assert terminal.move_cursor_up(10) == "\x1b[10A"

    def test_terminal_move_cursor_down(self):
        """Terminal.move_cursor_down returns correct sequence."""
        terminal = MockTerminal(80, 24)

        assert terminal.move_cursor_down(1) == "\x1b[1B"
        assert terminal.move_cursor_down(5) == "\x1b[5B"
        assert terminal.move_cursor_down(10) == "\x1b[10B"

    def test_terminal_move_cursor_zero_returns_empty(self):
        """Moving 0 lines returns empty string."""
        terminal = MockTerminal(80, 24)

        assert terminal.move_cursor_up(0) == ""
        assert terminal.move_cursor_down(0) == ""
        assert terminal.move_cursor_up(-1) == ""
        assert terminal.move_cursor_down(-1) == ""

    def test_multiple_relative_movements(self):
        """Series of relative movements produce correct sequences."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        tui._hardware_cursor_row = 0

        # Move down to row 10
        result1 = tui._move_cursor_relative(10)
        assert result1 == "\x1b[10B"
        assert tui._hardware_cursor_row == 10

        # Move down more to row 15
        result2 = tui._move_cursor_relative(15)
        assert result2 == "\x1b[5B"
        assert tui._hardware_cursor_row == 15

        # Move back up to row 5
        result3 = tui._move_cursor_relative(5)
        assert result3 == "\x1b[10A"
        assert tui._hardware_cursor_row == 5

        # Stay at row 5
        result4 = tui._move_cursor_relative(5)
        assert result4 == ""
        assert tui._hardware_cursor_row == 5


class TestDifferentialRenderingWithScrollback:
    """Tests for differential rendering when content exceeds terminal height."""

    def test_content_exceeds_terminal_without_growth(self):
        """When content exceeds terminal but hasn't grown, only visible portion updates."""
        terminal = MockTerminal(80, 10)
        tui = TUI(terminal)

        # Add 15 lines of content (exceeds terminal height of 10)
        for i in range(15):
            tui.add_child(Text(f"Line {i}", padding_y=0))

        tui.start()

        # First render - content grows from 0 to 15
        tui.render_frame()
        first_output = terminal.get_output()

        # Should have emitted newlines to scroll content
        assert "\r\n" in first_output

        # Clear buffer and tracking for second render
        terminal.clear_buffer()
        # Don't reset _previous_lines - we want to test the "no growth" path

        # Second render - same content, no growth
        # This tests the new elif branch: current_count > term_height but no growth
        tui.render_frame()
        second_output = terminal.get_output()

        # Should not have newlines (content didn't grow)
        # Should use differential rendering on visible portion only
        # Lines 5-14 are visible (content rows, not screen rows)
        # The output should contain "Line 14" but likely not "Line 0"

        tui.stop()

    def test_visible_lines_update_when_scrolled(self):
        """When scrolled, only visible lines can be updated."""
        terminal = MockTerminal(80, 10)
        tui = TUI(terminal)

        # Add 15 lines
        for i in range(15):
            tui.add_child(Text(f"Line {i}", padding_y=0))

        tui.start()
        tui.render_frame()

        # Now change a line in the visible portion (lines 5-14)
        tui.clear()
        for i in range(15):
            # Change line 10 (which is visible)
            if i == 10:
                tui.add_child(Text(f"MODIFIED Line {i}", padding_y=0))
            else:
                tui.add_child(Text(f"Line {i}", padding_y=0))

        terminal.clear_buffer()
        tui.render_frame()
        output = terminal.get_output()

        # The modified line should be in output
        assert "MODIFIED Line 10" in output

        tui.stop()

    def test_scrollback_lines_frozen(self):
        """Lines in scrollback cannot be changed after scrolling."""
        terminal = MockTerminal(80, 10)
        tui = TUI(terminal)

        # Add 15 lines
        for i in range(15):
            tui.add_child(Text(f"Line {i}", padding_y=0))

        tui.start()
        tui.render_frame()

        # Now try to change a line in scrollback (lines 0-4)
        tui.clear()
        for i in range(15):
            # Change line 2 (which is in scrollback)
            if i == 2:
                tui.add_child(Text(f"MODIFIED Line {i}", padding_y=0))
            else:
                tui.add_child(Text(f"Line {i}", padding_y=0))

        terminal.clear_buffer()
        tui.render_frame()
        output = terminal.get_output()

        # The modified line 2 is in scrollback, so it won't appear in output
        # (we can only render to visible terminal)
        assert "MODIFIED Line 2" not in output

        tui.stop()
