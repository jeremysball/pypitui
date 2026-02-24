"""Tests for utility functions - ported from pi-tui."""

import pytest
from pypitui import visible_width, truncate_to_width, wrap_text_with_ansi, slice_by_column


class TestVisibleWidth:
    """Tests for visible_width function."""

    def test_plain_text(self):
        """Visible width of plain text matches length."""
        assert visible_width("hello") == 5
        assert visible_width("") == 0
        assert visible_width("hello world") == 11

    def test_ansi_codes_ignored(self):
        """ANSI escape codes don't count toward width."""
        assert visible_width("\x1b[31mhello\x1b[0m") == 5
        assert visible_width("\x1b[1;31;42mtest\x1b[0m") == 4

    def test_multiple_ansi_codes(self):
        """Multiple ANSI codes are all ignored."""
        assert visible_width("\x1b[31m\x1b[1mhello\x1b[0m\x1b[0m") == 5


class TestTruncateToWidth:
    """Tests for truncate_to_width function."""

    def test_no_truncation_needed(self):
        """Text that fits is not truncated."""
        assert truncate_to_width("hello", 10) == "hello"
        assert truncate_to_width("hello", 5) == "hello"

    def test_truncation_with_ellipsis(self):
        """Long text is truncated with ellipsis."""
        result = truncate_to_width("hello world this is a test", 10)
        assert result == "hello w..."
        assert visible_width(result) <= 10

    def test_truncation_without_ellipsis(self):
        """Can truncate without ellipsis."""
        result = truncate_to_width("hello world", 5, "")
        assert result == "hello"
        assert visible_width(result) == 5

    def test_custom_ellipsis(self):
        """Can use custom ellipsis."""
        result = truncate_to_width("hello world", 8, "…")
        assert result.endswith("…")
        assert visible_width(result) <= 8

    def test_preserves_ansi_codes(self):
        """ANSI codes are preserved in output."""
        result = truncate_to_width("\x1b[31mhello world\x1b[0m", 8)
        assert "\x1b[31m" in result
        assert "..." in result

    def test_empty_text(self):
        """Empty text returns empty."""
        assert truncate_to_width("", 10) == ""

    def test_zero_width(self):
        """Zero width returns empty."""
        assert truncate_to_width("hello", 0) == ""

    def test_pad_option(self):
        """Can pad to exact width."""
        result = truncate_to_width("hello", 10, pad=True)
        assert visible_width(result) == 10

    def test_exact_fit_with_padding(self):
        """Exact fit with padding works."""
        result = truncate_to_width("hello", 5, pad=True)
        assert visible_width(result) == 5


class TestWrapTextWithAnsi:
    """Tests for wrap_text_with_ansi function."""

    def test_basic_wrapping(self):
        """Plain text is wrapped correctly."""
        text = "hello world this is a test"
        wrapped = wrap_text_with_ansi(text, 10)
        
        assert len(wrapped) > 1
        for line in wrapped:
            assert visible_width(line) <= 10

    def test_preserves_color_across_wraps(self):
        """Color codes are preserved across wrapped lines."""
        red = "\x1b[31m"
        reset = "\x1b[0m"
        text = f"{red}hello world this is red{reset}"
        
        wrapped = wrap_text_with_ansi(text, 10)
        
        # Each wrapped line should contain red code
        for line in wrapped:
            if line.strip():
                assert red in line

    def test_empty_text(self):
        """Empty text returns list with empty string."""
        result = wrap_text_with_ansi("", 10)
        assert result == [""]

    def test_paragraphs(self):
        """Paragraphs are preserved."""
        text = "first paragraph\n\nsecond paragraph"
        wrapped = wrap_text_with_ansi(text, 50)
        
        # Should have empty line between paragraphs
        assert "" in wrapped

    def test_single_word_per_line(self):
        """Long words stay on single line."""
        text = "supercalifragilisticexpialidocious"
        wrapped = wrap_text_with_ansi(text, 10)
        
        # Word is longer than width, stays on one line
        assert len(wrapped) == 1

    def test_trailing_whitespace_truncated(self):
        """Trailing whitespace that exceeds width is truncated."""
        result = wrap_text_with_ansi("  ", 1)
        assert visible_width(result[0]) <= 1


class TestSliceByColumn:
    """Tests for slice_by_column function."""

    def test_basic_slicing(self):
        """Basic slicing works correctly."""
        result = slice_by_column("hello world", 0, 5)
        assert result == "hello"
        assert visible_width(result) == 5

    def test_slicing_with_offset(self):
        """Slicing with start offset works."""
        result = slice_by_column("hello world", 6, 5)
        assert result == "world"
        assert visible_width(result) == 5

    def test_preserves_ansi_codes(self):
        """ANSI codes are preserved in sliced output."""
        red = "\x1b[31m"
        reset = "\x1b[0m"
        text = f"{red}hello{reset} world"

        result = slice_by_column(text, 0, 5)
        assert red in result
        assert "hello" in result
        assert visible_width(result) == 5

    def test_ansi_codes_across_start_boundary(self):
        """ANSI codes active at start boundary are preserved."""
        red = "\x1b[31m"
        reset = "\x1b[0m"
        text = f"{red}hello{reset} world"

        # Slice starting in the middle of red text
        result = slice_by_column(text, 3, 5)
        assert red in result
        assert "lo" in result
        assert visible_width(result) == 5

    def test_ansi_reset_handled(self):
        """ANSI reset codes properly deactivate styling."""
        red = "\x1b[31m"
        reset = "\x1b[0m"
        text = f"{red}hi{reset} there"

        # Slice after reset
        result = slice_by_column(text, 3, 5)
        assert red not in result
        assert "there" in result
        assert visible_width(result) == 5

    def test_empty_slice(self):
        """Zero length returns empty string."""
        result = slice_by_column("hello", 0, 0)
        assert result == ""

    def test_slice_beyond_end(self):
        """Slicing beyond text end returns available content."""
        result = slice_by_column("hi", 0, 10)
        assert visible_width(result) == 2
