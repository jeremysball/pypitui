"""Tests for Container, Box, Text, and Spacer components - ported from pi-tui."""

import pytest
from pypitui import Container, Box, Text, Spacer, visible_width


class TestText:
    """Tests for Text component."""

    def test_basic_render(self):
        """Text renders content."""
        text = Text("Hello World", 1, 1)
        lines = text.render(20)
        
        assert len(lines) > 0
        # Content should appear somewhere in the output
        assert any("Hello World" in line for line in lines)

    def test_padding_x(self):
        """Horizontal padding is applied."""
        text = Text("Hi", 5, 0)
        lines = text.render(20)
        
        # With 5 padding on each side, content is in the middle
        for line in lines:
            if line.strip():
                assert visible_width(line) == 20

    def test_padding_y(self):
        """Vertical padding is applied."""
        text = Text("Hi", 0, 2)
        lines = text.render(20)
        
        # 2 lines padding top + content + 2 lines padding bottom = 5 lines
        assert len(lines) == 5

    def test_set_text(self):
        """Can update text."""
        text = Text("Original", 0, 0)
        text.set_text("Updated")
        
        lines = text.render(20)
        assert any("Updated" in line for line in lines)
        assert not any("Original" in line for line in lines)

    def test_word_wrapping(self):
        """Long text wraps correctly."""
        text = Text("This is a long line of text", 0, 0)
        lines = text.render(10)
        
        # Each line should be <= 10 visible chars
        for line in lines:
            assert visible_width(line) <= 10

    def test_empty_text(self):
        """Empty text renders empty lines."""
        text = Text("", 1, 1)
        lines = text.render(20)
        
        # Should have padding lines
        assert len(lines) == 2


class TestBox:
    """Tests for Box component."""

    def test_basic_render(self):
        """Box renders children."""
        box = Box(1, 1)
        box.add_child(Text("Content", 0, 0))
        lines = box.render(40)
        
        assert any("Content" in line for line in lines)

    def test_padding(self):
        """Box applies padding."""
        box = Box(2, 1)
        box.add_child(Text("X", 0, 0))
        lines = box.render(20)
        
        # Should have top padding, content, bottom padding
        assert len(lines) >= 3

    def test_multiple_children(self):
        """Box can contain multiple children."""
        box = Box(0, 0)
        box.add_child(Text("Line 1", 0, 0))
        box.add_child(Text("Line 2", 0, 0))
        lines = box.render(20)
        
        assert any("Line 1" in line for line in lines)
        assert any("Line 2" in line for line in lines)

    def test_remove_child(self):
        """Can remove child."""
        box = Box(0, 0)
        child = Text("Content", 0, 0)
        box.add_child(child)
        
        lines = box.render(20)
        assert any("Content" in line for line in lines)
        
        box.remove_child(child)
        lines = box.render(20)
        assert not any("Content" in line for line in lines)

    def test_clear(self):
        """Can clear all children."""
        box = Box(0, 0)
        box.add_child(Text("A", 0, 0))
        box.add_child(Text("B", 0, 0))
        
        box.clear()
        assert len(box.children) == 0


class TestContainer:
    """Tests for Container component."""

    def test_renders_children_vertically(self):
        """Container stacks children vertically."""
        container = Container()
        container.add_child(Text("First", 0, 0))
        container.add_child(Text("Second", 0, 0))
        
        lines = container.render(20)
        
        # Both should appear in output
        combined = "\n".join(lines)
        assert "First" in combined
        assert "Second" in combined

    def test_empty_container(self):
        """Empty container returns empty list."""
        container = Container()
        lines = container.render(20)
        assert lines == []

    def test_nested_containers(self):
        """Containers can be nested."""
        outer = Container()
        inner = Container()
        inner.add_child(Text("Nested", 0, 0))
        outer.add_child(inner)
        
        lines = outer.render(20)
        assert any("Nested" in line for line in lines)


class TestSpacer:
    """Tests for Spacer component."""

    def test_single_line(self):
        """Default spacer is 1 line."""
        spacer = Spacer()
        lines = spacer.render(20)
        assert len(lines) == 1
        assert lines[0] == ""

    def test_multiple_lines(self):
        """Can create multi-line spacer."""
        spacer = Spacer(5)
        lines = spacer.render(20)
        assert len(lines) == 5
        for line in lines:
            assert line == ""

    def test_invalidate(self):
        """Invalidate does nothing."""
        spacer = Spacer(3)
        spacer.invalidate()  # Should not raise
