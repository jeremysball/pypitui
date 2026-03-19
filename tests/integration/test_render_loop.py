"""Integration tests for full render loop."""

from pypitui.component import Component, RenderedLine, Size
from pypitui.mock_terminal import MockTerminal
from pypitui.tui import TUI


class FakeComponent(Component):
    """Fake component for testing render loop."""

    def __init__(self, width: int, height: int, content: str) -> None:
        self._width = width
        self._height = height
        self.content = content

    def measure(self, available_width: int, available_height: int) -> Size:
        return Size(
            min(self._width, available_width),
            min(self._height, available_height),
        )

    def render(self, width: int) -> list[RenderedLine]:
        lines = []
        for i in range(self._height):
            line_content = f"{self.content} {i}"
            lines.append(RenderedLine(line_content[:width], []))
        return lines


class TestRenderLoop:
    """Integration tests for full render loop."""

    def test_component_measure_and_render(self) -> None:
        """Component measure + render pipeline works."""
        component = FakeComponent(40, 3, "Test")

        size = component.measure(80, 24)
        assert size.width == 40
        assert size.height == 3

        rendered = component.render(40)
        assert len(rendered) == 3
        assert "Test 0" in rendered[0].content
        assert "Test 1" in rendered[1].content
        assert "Test 2" in rendered[2].content

    def test_tui_with_component(self) -> None:
        """TUI can manage and render a component."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        component = FakeComponent(40, 2, "Hello")
        tui.add_child(component)

        assert tui._root is component

        # Simulate render loop
        size = component.measure(80, 24)
        rendered = component.render(size.width)

        lines = [
            (i, f"hash{i}", line.content)
            for i, line in enumerate(rendered)
        ]
        tui._output_diff(lines, 80)

        output = mock_term.get_output()
        assert b"Hello 0" in output
        assert b"Hello 1" in output

    def test_render_multiple_frames(self) -> None:
        """Multiple render frames with changes."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # Frame 1: Initial render
        component1 = FakeComponent(40, 2, "First")
        tui.add_child(component1)

        size = component1.measure(80, 24)
        rendered = component1.render(size.width)
        lines1 = [
            (i, f"hash{i}", line.content)
            for i, line in enumerate(rendered)
        ]
        tui._output_diff(lines1, 80)

        # Frame 2: Different component
        mock_term.reset_counts()
        component2 = FakeComponent(40, 2, "Second")
        tui.add_child(component2)

        rendered2 = component2.render(size.width)
        lines2 = [
            (i, f"new_hash{i}", line.content)
            for i, line in enumerate(rendered2)
        ]
        tui._output_diff(lines2, 80)

        output = mock_term.get_output()
        assert b"Second 0" in output
        assert b"Second 1" in output

    def test_viewport_adjusts_with_content_height(self) -> None:
        """Viewport scrolls when content exceeds terminal."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # Small content - no scroll
        viewport = tui._calculate_viewport_top(5)
        assert viewport == 0

        # Large content - scroll to bottom (uses default 24-line term)
        viewport = tui._calculate_viewport_top(30)
        assert viewport == 6  # 30 - 24

    def test_rendered_line_structure(self) -> None:
        """RenderedLine contains content and styles."""
        from pypitui.component import StyleSpan

        line = RenderedLine(
            content="Hello World",
            styles=[
                StyleSpan(0, 5, fg="red", bg=None, bold=True, italic=False, underline=False),
            ],
        )

        assert line.content == "Hello World"
        assert len(line.styles) == 1
        assert line.styles[0].start == 0
        assert line.styles[0].end == 5
        assert line.styles[0].fg == "red"

    def test_component_resize(self) -> None:
        """Component adapts to available space."""
        component = FakeComponent(100, 10, "Resize")

        # Large available space
        size1 = component.measure(80, 24)
        assert size1.width == 80
        assert size1.height == 10

        # Small available space
        size2 = component.measure(40, 5)
        assert size2.width == 40
        assert size2.height == 5
