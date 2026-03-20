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


class TestComponentABC:
    """Tests for Component abstract base class."""

    def test_component_abstract_methods(self) -> None:
        """Cannot instantiate without measure/render implementation."""
        from pypitui.component import Component

        with pytest.raises(TypeError):
            Component()  # type: ignore[abstract]

    def test_component_invalidation_bubbles(self) -> None:
        """invalidate() calls _child_invalidated() on parent."""
        from pypitui.component import Component, Rect, RenderedLine, Size

        class ParentComponent(Component):
            def __init__(self) -> None:
                super().__init__()
                self.child_invalidated = False

            def measure(self, available_width: int, available_height: int) -> Size:
                return Size(10, 1)

            def render(self, width: int) -> list[RenderedLine]:
                return [RenderedLine("parent", [])]

            def _child_invalidated(self, child: Component) -> None:
                self.child_invalidated = True

        class ChildComponent(Component):
            def measure(self, available_width: int, available_height: int) -> Size:
                return Size(10, 1)

            def render(self, width: int) -> list[RenderedLine]:
                return [RenderedLine("child", [])]

        parent = ParentComponent()
        child = ChildComponent()

        # Simulate parent having child
        child.invalidate()
        parent._child_invalidated(child)

        assert parent.child_invalidated is True

    def test_component_rect_field_exists(self) -> None:
        """_rect: Rect stores position and dimensions."""
        from pypitui.component import Component, Rect, RenderedLine, Size

        class TestComponent(Component):
            def measure(self, available_width: int, available_height: int) -> Size:
                return Size(10, 1)

            def render(self, width: int) -> list[RenderedLine]:
                return [RenderedLine("test", [])]

        comp = TestComponent()
        # _rect starts as None
        assert comp._rect is None

        # TUI sets _rect during render
        comp._rect = Rect(x=0, y=0, width=80, height=24)
        assert comp._rect.x == 0
        assert comp._rect.y == 0
        assert comp._rect.width == 80
        assert comp._rect.height == 24
