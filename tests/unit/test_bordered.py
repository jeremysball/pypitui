"""Tests for BorderedBox component."""

import pytest

from pypitui.component import Size
from pypitui.components.bordered import BorderedBox
from pypitui.components.text import Text


class TestBorderedBoxMeasure:
    """Tests for BorderedBox.measure()."""

    def test_borderedbox_measure_adds_border(self) -> None:
        """Width + 2, height + 2 for borders."""
        box = BorderedBox()
        child = Text("Hello")
        box.add_child(child)

        size = box.measure(80, 24)

        # Child measures at available width, box adds 2 for borders
        assert size.width == 80
        assert size.height == 3  # 1 (child) + 2 (borders)

    def test_borderedbox_measure_without_child(self) -> None:
        """Without child, minimum size is border only."""
        box = BorderedBox()

        size = box.measure(80, 24)

        assert size.width == 80
        assert size.height == 2  # Just top and bottom borders


class TestBorderedBoxRender:
    """Tests for BorderedBox.render()."""

    def test_borderedbox_render_draws_box_drawing_chars(self) -> None:
        """Box drawing characters: ┌─┐│ etc."""
        box = BorderedBox()
        child = Text("Hi")
        box.add_child(child)

        lines = box.render(10)

        assert len(lines) == 3  # Top border, content, bottom border
        assert lines[0].content.startswith("┌")
        assert lines[0].content.endswith("┐")
        assert lines[1].content.startswith("│")
        assert lines[1].content.endswith("│")
        assert lines[2].content.startswith("└")
        assert lines[2].content.endswith("┘")

    def test_borderedbox_render_shows_title(self) -> None:
        """Title appears in top border."""
        box = BorderedBox(title="My Box")
        child = Text("Content")
        box.add_child(child)

        lines = box.render(20)

        assert "My Box" in lines[0].content

    def test_borderedbox_render_pads_content(self) -> None:
        """Content padded with spaces and borders."""
        box = BorderedBox()
        child = Text("X")
        box.add_child(child)

        lines = box.render(10)

        # Content line should have padding: │ X        │
        content_line = lines[1].content
        assert content_line.startswith("│")
        assert content_line.endswith("│")
        assert "X" in content_line

    def test_borderedbox_render_empty_box(self) -> None:
        """Box without child renders empty interior."""
        box = BorderedBox()

        lines = box.render(10)

        assert len(lines) == 2
        assert lines[0].content == "┌────────┐"
        assert lines[1].content == "└────────┘"

    def test_borderedbox_render_respects_width(self) -> None:
        """Box width matches requested width."""
        box = BorderedBox()
        child = Text("Test")
        box.add_child(child)

        lines = box.render(15)

        for line in lines:
            assert len(line.content) == 15


class TestBorderedBoxChild:
    """Tests for BorderedBox child management."""

    def test_borderedbox_add_child(self) -> None:
        """Single child stored."""
        box = BorderedBox()
        child = Text("Hello")

        box.add_child(child)

        assert box._child == child

    def test_borderedbox_add_child_replaces_existing(self) -> None:
        """Adding second child replaces first."""
        box = BorderedBox()
        child1 = Text("First")
        child2 = Text("Second")

        box.add_child(child1)
        box.add_child(child2)

        assert box._child == child2


class TestBorderedBoxTitleTruncation:
    """Tests for title handling."""

    def test_borderedbox_truncates_long_title(self) -> None:
        """Long title truncated to fit box."""
        box = BorderedBox(title="A very long title that won't fit")
        child = Text("Content")
        box.add_child(child)

        lines = box.render(15)

        top_line = lines[0].content
        assert "A very" in top_line
        # Title should not overflow box boundaries
        assert len(top_line) == 15

    def test_borderedbox_empty_title(self) -> None:
        """Empty title renders plain top border."""
        box = BorderedBox(title="")
        child = Text("Content")
        box.add_child(child)

        lines = box.render(10)

        # Should be just the border without title
        assert lines[0].content == "┌────────┐"
