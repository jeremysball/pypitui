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
        assert tui._calculate_first_visible_row(50) == 50  # max(0, 100-50) = 50

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
