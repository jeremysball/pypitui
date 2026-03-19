"""Unit tests for styles and color detection."""

from unittest.mock import patch

import pytest


class TestDetectColorSupport:
    """Tests for detect_color_support function."""

    def test_detect_color_support_no_color(self) -> None:
        """NO_COLOR=1 returns 0."""
        from pypitui.styles import detect_color_support

        with patch.dict("os.environ", {"NO_COLOR": "1"}, clear=True):
            result = detect_color_support()
            assert result == 0

    def test_detect_color_support_force_color(self) -> None:
        """FORCE_COLOR=3 returns 3."""
        from pypitui.styles import detect_color_support

        with patch.dict("os.environ", {"FORCE_COLOR": "3"}, clear=True):
            result = detect_color_support()
            assert result == 3

    def test_detect_color_support_truecolor(self) -> None:
        """COLORTERM=truecolor returns 3."""
        from pypitui.styles import detect_color_support

        with patch.dict("os.environ", {"COLORTERM": "truecolor"}, clear=True):
            result = detect_color_support()
            assert result == 3

    def test_detect_color_support_256color(self) -> None:
        """TERM=256color returns 2."""
        from pypitui.styles import detect_color_support

        with patch.dict("os.environ", {"TERM": "256color"}, clear=True):
            result = detect_color_support()
            assert result == 2

    def test_detect_color_support_16color(self) -> None:
        """TERM=color returns 1."""
        from pypitui.styles import detect_color_support

        with patch.dict("os.environ", {"TERM": "color"}, clear=True):
            result = detect_color_support()
            assert result == 1

    def test_detect_color_support_default(self) -> None:
        """No env vars returns 3 (assume modern)."""
        from pypitui.styles import detect_color_support

        with patch.dict("os.environ", {}, clear=True):
            result = detect_color_support()
            assert result == 3

    def test_detect_color_support_pypitui_override(self) -> None:
        """PYPITUI_COLOR=2 returns 2."""
        from pypitui.styles import detect_color_support

        with patch.dict("os.environ", {"PYPITUI_COLOR": "2"}, clear=True):
            result = detect_color_support()
            assert result == 2

    def test_detect_color_support_invalid_force(self) -> None:
        """Invalid FORCE_COLOR defaults to 3."""
        from pypitui.styles import detect_color_support

        with patch.dict("os.environ", {"FORCE_COLOR": "invalid"}, clear=True):
            result = detect_color_support()
            assert result == 3
