"""Tests for utility functions."""

import pytest


class TestWcwidth:
    """Tests for wcwidth utility."""

    def test_wcwidth_emoji(self) -> None:
        """Emoji counted as width 2."""
        from pypitui.utils import wcwidth

        assert wcwidth("😀") == 2
        assert wcwidth("🎉") == 2
        assert wcwidth("❤") == 1  # Single heart, not variant

    def test_wcwidth_cjk(self) -> None:
        """CJK characters counted as width 2."""
        from pypitui.utils import wcwidth

        assert wcwidth("中") == 2
        assert wcwidth("文") == 2
        assert wcwidth("ひ") == 2
        assert wcwidth("ら") == 2
        assert wcwidth("が") == 2
        assert wcwidth("な") == 2

    def test_wcwidth_ascii(self) -> None:
        """ASCII characters counted as width 1."""
        from pypitui.utils import wcwidth

        assert wcwidth("a") == 1
        assert wcwidth("Z") == 1
        assert wcwidth("0") == 1
        assert wcwidth(" ") == 1
        assert wcwidth("!") == 1

    def test_wcwidth_invalid(self) -> None:
        """Multi-character strings raise ValueError."""
        from pypitui.utils import wcwidth

        with pytest.raises(ValueError):
            wcwidth("ab")

        with pytest.raises(ValueError):
            wcwidth("😀😀")


class TestTruncateToWidth:
    """Tests for truncate_to_width utility."""

    def test_truncate_to_width_respects_wide_chars(self) -> None:
        """Never splits wide characters."""
        from pypitui.utils import truncate_to_width

        # "中" is width 2, "文" is width 2
        result = truncate_to_width("中文", 3)
        # Should include "中" (2) but not "文" (would be 4 total)
        assert result == "中"

    def test_truncate_to_width_exact_boundary(self) -> None:
        """Wide chars at exact width boundary are included."""
        from pypitui.utils import truncate_to_width

        # "中" is width 2, fits exactly at width 2
        result = truncate_to_width("中文", 2)
        assert result == "中"

    def test_truncate_to_width_emoji(self) -> None:
        """Emoji handled correctly."""
        from pypitui.utils import truncate_to_width

        # "😀" is width 2
        result = truncate_to_width("😀😀", 3)
        assert result == "😀"

    def test_truncate_to_width_mixed(self) -> None:
        """Mixed ASCII and wide chars."""
        from pypitui.utils import truncate_to_width

        # "a" (1) + "中" (2) = 3, "b" would make 4
        result = truncate_to_width("a中文b", 4)
        assert result == "a中"

    def test_truncate_to_width_zero(self) -> None:
        """Zero width returns empty string."""
        from pypitui.utils import truncate_to_width

        result = truncate_to_width("hello", 0)
        assert result == ""

    def test_truncate_to_width_empty(self) -> None:
        """Empty text returns empty string."""
        from pypitui.utils import truncate_to_width

        result = truncate_to_width("", 10)
        assert result == ""


class TestSliceByWidth:
    """Tests for slice_by_width utility."""

    def test_slice_by_width_atomic(self) -> None:
        """Wide chars treated as atomic units."""
        from pypitui.utils import slice_by_width

        # "中文测试" - each char is width 2
        # Positions: 中(0-2), 文(2-4), 测(4-6), 试(6-8)
        result = slice_by_width("中文测试", 2, 6)
        # Should get "文测" (positions 2-6)
        assert result == "文测"

    def test_slice_by_width_partial_wide_char(self) -> None:
        """Partial wide chars are excluded."""
        from pypitui.utils import slice_by_width

        # "中" is width 2 (positions 0-2)
        # Slicing from 1 would partially include it
        result = slice_by_width("中文", 1, 4)
        # "中" starts at 0, so not included
        # "文" starts at 2, included (2-4 fits)
        assert result == "文"

    def test_slice_by_width_emoji(self) -> None:
        """Emoji handled as atomic units."""
        from pypitui.utils import slice_by_width

        # "😀😁" - each is width 2
        # Positions: 😀(0-2), 😁(2-4)
        result = slice_by_width("😀😁", 2, 4)
        assert result == "😁"

    def test_slice_by_width_empty_range(self) -> None:
        """Empty range returns empty string."""
        from pypitui.utils import slice_by_width

        result = slice_by_width("hello", 3, 3)
        assert result == ""

    def test_slice_by_width_out_of_range(self) -> None:
        """Out of range returns empty string."""
        from pypitui.utils import slice_by_width

        result = slice_by_width("hi", 10, 20)
        assert result == ""
