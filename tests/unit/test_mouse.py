"""Unit tests for mouse event parsing."""

import pytest


class TestParseMouse:
    """Tests for parse_mouse function with SGR 1006 protocol."""

    def test_parse_mouse_click(self) -> None:
        """Parse SGR extended mouse sequence (CSI < 0;10;20 M)."""
        from pypitui.mouse import MouseEvent, parse_mouse

        # Button 0 (left) pressed at col 10, row 20 (1-indexed)
        result = parse_mouse(b"\x1b[<0;10;20M")
        assert result is not None
        assert result.button == 0
        assert result.col == 9  # 0-indexed
        assert result.row == 19  # 0-indexed
        assert result.pressed is True

    def test_parse_mouse_release(self) -> None:
        """Verify release event parsing (CSI < 0;10;20 m)."""
        from pypitui.mouse import MouseEvent, parse_mouse

        # Button 0 (left) released at col 10, row 20 (1-indexed)
        result = parse_mouse(b"\x1b[<0;10;20m")
        assert result is not None
        assert result.button == 0
        assert result.col == 9  # 0-indexed
        assert result.row == 19  # 0-indexed
        assert result.pressed is False

    def test_parse_mouse_wheel(self) -> None:
        """Verify scroll wheel events."""
        from pypitui.mouse import MouseEvent, parse_mouse

        # Scroll wheel up (button 64) at col 5, row 10
        result = parse_mouse(b"\x1b[<64;5;10M")
        assert result is not None
        assert result.button == 64
        assert result.col == 4
        assert result.row == 9

    def test_parse_mouse_move(self) -> None:
        """Verify mouse move with button held."""
        from pypitui.mouse import MouseEvent, parse_mouse

        # Mouse move with button 0 held (button + 32 = 32)
        result = parse_mouse(b"\x1b[<32;15;25M")
        assert result is not None
        assert result.button == 32
        assert result.col == 14
        assert result.row == 24

    def test_mouse_coordinates_converted_to_zero_indexed(self) -> None:
        """SGR 1006 reports 1-indexed coordinates, MouseEvent stores 0-indexed."""
        from pypitui.mouse import parse_mouse

        # 1,1 should become 0,0
        result = parse_mouse(b"\x1b[<0;1;1M")
        assert result is not None
        assert result.col == 0
        assert result.row == 0

        # 80,24 should become 79,23
        result = parse_mouse(b"\x1b[<0;80;24M")
        assert result is not None
        assert result.col == 79
        assert result.row == 23

    def test_parse_mouse_invalid(self) -> None:
        """Invalid sequences return None."""
        from pypitui.mouse import parse_mouse

        assert parse_mouse(b"not a mouse sequence") is None
        assert parse_mouse(b"\x1b[?25l") is None  # cursor hide
        assert parse_mouse(b"") is None
