"""Unit tests for component base classes and data structures."""

import pytest


class TestSizeDataclass:
    """Tests for Size dataclass."""

    def test_size_dataclass(self) -> None:
        """Size(width, height) stores dimensions."""
        from pypitui.component import Size

        size = Size(width=80, height=24)
        assert size.width == 80
        assert size.height == 24

    def test_size_is_immutable(self) -> None:
        """Size dataclass is frozen (immutable)."""
        from pypitui.component import Size

        size = Size(width=80, height=24)
        with pytest.raises(AttributeError):
            size.width = 100


class TestRenderedLineDataclass:
    """Tests for RenderedLine dataclass."""

    def test_rendered_line_dataclass(self) -> None:
        """RenderedLine stores content and styles."""
        from pypitui.component import RenderedLine, StyleSpan

        styles = [StyleSpan(start=0, end=5, fg="red")]
        line = RenderedLine(content="Hello", styles=styles)
        assert line.content == "Hello"
        assert len(line.styles) == 1
        assert line.styles[0].fg == "red"


class TestRectDataclass:
    """Tests for Rect dataclass."""

    def test_rect_dataclass(self) -> None:
        """Rect(x, y, width, height) stores position and dimensions."""
        from pypitui.component import Rect

        rect = Rect(x=10, y=5, width=80, height=24)
        assert rect.x == 10
        assert rect.y == 5
        assert rect.width == 80
        assert rect.height == 24
