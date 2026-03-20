"""Tests for built-in components."""

import pytest


class TestContainer:
    """Tests for Container component."""

    def test_container_measure_returns_sum_of_children(self) -> None:
        """Height = sum(child heights)."""
        from pypitui.component import Component, RenderedLine, Size
        from pypitui.components.container import Container

        class TestChild(Component):
            def __init__(self, height: int) -> None:
                super().__init__()
                self._height = height

            def measure(self, available_width: int, available_height: int) -> Size:
                return Size(10, self._height)

            def render(self, width: int) -> list[RenderedLine]:
                return [RenderedLine(f"h={self._height}", [])]

        container = Container()
        child1 = TestChild(3)
        child2 = TestChild(2)

        container.add_child(child1)
        container.add_child(child2)

        size = container.measure(80, 24)
        assert size.width == 10
        assert size.height == 5  # 3 + 2

    def test_container_render_stacks_vertically(self) -> None:
        """Children rendered sequentially."""
        from pypitui.component import Component, RenderedLine, Size
        from pypitui.components.container import Container

        class TestChild(Component):
            def __init__(self, name: str, height: int) -> None:
                super().__init__()
                self._name = name
                self._height = height

            def measure(self, available_width: int, available_height: int) -> Size:
                return Size(10, self._height)

            def render(self, width: int) -> list[RenderedLine]:
                return [
                    RenderedLine(f"{self._name}-{i}", [])
                    for i in range(self._height)
                ]

        container = Container()
        child1 = TestChild("A", 2)
        child2 = TestChild("B", 3)

        container.add_child(child1)
        container.add_child(child2)

        lines = container.render(80)
        assert len(lines) == 5  # 2 + 3
        assert lines[0].content == "A-0"
        assert lines[1].content == "A-1"
        assert lines[2].content == "B-0"
        assert lines[3].content == "B-1"
        assert lines[4].content == "B-2"

    def test_container_add_child_appends_to_list(self) -> None:
        """Children list grows."""
        from pypitui.component import Component, RenderedLine, Size
        from pypitui.components.container import Container

        class TestChild(Component):
            def measure(self, available_width: int, available_height: int) -> Size:
                return Size(10, 1)

            def render(self, width: int) -> list[RenderedLine]:
                return [RenderedLine("child", [])]

        container = Container()
        assert len(container._children) == 0

        container.add_child(TestChild())
        assert len(container._children) == 1

        container.add_child(TestChild())
        assert len(container._children) == 2

    def test_container_clear_children(self) -> None:
        """Children list emptied."""
        from pypitui.component import Component, RenderedLine, Size
        from pypitui.components.container import Container

        class TestChild(Component):
            def measure(self, available_width: int, available_height: int) -> Size:
                return Size(10, 1)

            def render(self, width: int) -> list[RenderedLine]:
                return [RenderedLine("child", [])]

        container = Container()
        container.add_child(TestChild())
        container.add_child(TestChild())
        assert len(container._children) == 2

        container.clear_children()
        assert len(container._children) == 0

    def test_container_empty_measure(self) -> None:
        """Empty container has size 0,0."""
        from pypitui.component import Size
        from pypitui.components.container import Container

        container = Container()
        size = container.measure(80, 24)
        assert size == Size(0, 0)

    def test_container_empty_render(self) -> None:
        """Empty container renders empty list."""
        from pypitui.components.container import Container

        container = Container()
        lines = container.render(80)
        assert lines == []


class TestText:
    """Tests for Text component."""

    def test_text_measure_single_line(self) -> None:
        """Height=1 for simple text."""
        from pypitui.components.text import Text

        text = Text("Hello")
        size = text.measure(80, 24)
        assert size.height == 1

    def test_text_measure_multi_line(self) -> None:
        """Height=n for n lines."""
        from pypitui.components.text import Text

        text = Text("Line 1\nLine 2\nLine 3")
        size = text.measure(80, 24)
        assert size.height == 3

    def test_text_render_returns_lines(self) -> None:
        """Returns list of RenderedLine."""
        from pypitui.components.text import Text

        text = Text("Hello\nWorld")
        lines = text.render(80)
        assert len(lines) == 2
        assert lines[0].content == "Hello"
        assert lines[1].content == "World"

    def test_text_render_wraps_long_lines(self) -> None:
        """Wrapping at width boundary using wcwidth."""
        from pypitui.components.text import Text

        text = Text("This is a long line that needs wrapping")
        lines = text.render(20)
        assert len(lines) >= 2  # Should wrap to multiple lines

    def test_text_content_mutable(self) -> None:
        """set_text updates content and invalidates."""
        from pypitui.components.text import Text

        text = Text("Original")
        assert text.get_text() == "Original"

        text.set_text("Updated")
        assert text.get_text() == "Updated"

    def test_text_empty(self) -> None:
        """Empty text renders nothing."""
        from pypitui.components.text import Text

        text = Text("")
        lines = text.render(80)
        assert lines == []
