"""Tests for component-aware invalidation with parent references."""

import pytest
from pypitui import TUI, Container, Text, Component, Spacer
from pypitui.terminal import MockTerminal


class TestParentAttribute:
    """Phase 1.1: Component._parent attribute."""

    def test_component_has_parent_attribute(self):
        """Component should have _parent attribute initialized to None."""
        # Text is a concrete Component subclass
        text = Text("hello")
        assert hasattr(text, "_parent")
        assert text._parent is None

    def test_container_has_parent_attribute(self):
        """Container should also have _parent attribute."""
        container = Container()
        assert hasattr(container, "_parent")
        assert container._parent is None


class TestParentWiring:
    """Phase 1.2: Parent reference wiring in Container."""

    def test_container_sets_parent_on_add_child(self):
        """Container.add_child() should set child's _parent."""
        container = Container()
        text = Text("hello")

        container.add_child(text)

        assert text._parent is container

    def test_nested_container_parent_chain(self):
        """Parent chain should work through nested containers."""
        outer = Container()
        inner = Container()
        text = Text("hello")

        inner.add_child(text)
        outer.add_child(inner)

        assert text._parent is inner
        assert inner._parent is outer

    def test_container_clears_parent_on_remove_child(self):
        """Container.remove_child() should clear child's _parent."""
        container = Container()
        text = Text("hello")

        container.add_child(text)
        assert text._parent is container

        container.remove_child(text)
        assert text._parent is None

    def test_container_clear_clears_all_parent_refs(self):
        """Container.clear() should clear all children's _parent."""
        container = Container()
        text1 = Text("hello")
        text2 = Text("world")

        container.add_child(text1)
        container.add_child(text2)
        assert text1._parent is container
        assert text2._parent is container

        container.clear()
        assert text1._parent is None
        assert text2._parent is None


class TestBubbleUpInvalidation:
    """Phase 2: Bubble-up invalidation API."""

    def test_component_invalidate_bubbles_to_parent(self):
        """Component.invalidate() should bubble up to parent._child_invalidated()."""
        container = Container()
        text = Text("hello")
        container.add_child(text)

        # Track if _child_invalidated was called
        called_with = []
        def mock_child_invalidated(child):
            called_with.append(child)
        container._child_invalidated = mock_child_invalidated

        text.invalidate()

        assert len(called_with) == 1
        assert called_with[0] is text

    def test_component_invalidate_no_parent_does_nothing(self):
        """Component.invalidate() should not error when no parent."""
        text = Text("hello")
        # Should not raise
        text.invalidate()

    def test_container_child_invalidated_bubbles_up(self):
        """Container._child_invalidated() should bubble to its parent."""
        outer = Container()
        inner = Container()
        text = Text("hello")

        inner.add_child(text)
        outer.add_child(inner)

        # Track if outer's _child_invalidated was called
        called_with = []
        def mock_child_invalidated(child):
            called_with.append(child)
        outer._child_invalidated = mock_child_invalidated

        text.invalidate()

        assert len(called_with) == 1
        assert called_with[0] is text

    def test_tui_child_invalidated_calls_invalidate_component(self):
        """TUI._child_invalidated() should call invalidate_component()."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)
        text = Text("hello")
        tui.add_child(text)

        # Track if invalidate_component was called
        called_with = []
        def mock_invalidate_component(component):
            called_with.append(component)
        tui.invalidate_component = mock_invalidate_component

        text.invalidate()

        assert len(called_with) == 1
        assert called_with[0] is text


class TestPositionTracking:
    """Phase 3: Position tracking during render."""

    def test_tui_has_component_positions_dict(self):
        """TUI should have _component_positions dict initialized empty."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        assert hasattr(tui, "_component_positions")
        assert tui._component_positions == {}

    def test_render_tracks_component_positions(self):
        """TUI.render() should track each child's line range."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        text1 = Text("Line 1")
        text2 = Text("Line 2")
        tui.add_child(text1)
        tui.add_child(text2)

        # Render to trigger position tracking
        lines = tui.render(40)

        # Text with default padding renders 3 lines each
        # text1: lines 0-2, text2: lines 3-5
        assert tui._component_positions[text1] == (0, 3)
        assert tui._component_positions[text2] == (3, 6)

    def test_render_clears_previous_positions(self):
        """TUI.render() should clear previous positions before tracking."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        text1 = Text("Line 1")
        tui.add_child(text1)

        # First render
        tui.render(40)
        assert text1 in tui._component_positions

        # Remove and add different child
        tui.remove_child(text1)
        text2 = Text("Line 2")
        tui.add_child(text2)

        # Second render should clear old positions
        tui.render(40)
        assert text1 not in tui._component_positions
        assert text2 in tui._component_positions

    def test_render_tracks_nested_container_positions(self):
        """TUI.render() should track positions for nested containers."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        outer = Container()
        inner = Container()
        text = Text("Nested text")

        inner.add_child(text)
        outer.add_child(inner)
        tui.add_child(outer)

        lines = tui.render(40)

        # Should track outer container position
        # outer: lines 0-2 (3 lines of text with padding)
        assert outer in tui._component_positions
        start, end = tui._component_positions[outer]
        assert end - start == 3  # Text renders 3 lines

    def test_position_tracks_content_size(self):
        """Positions should reflect actual rendered content size."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        # Spacer with height 5
        spacer = Spacer(height=5)
        tui.add_child(spacer)

        lines = tui.render(40)

        # Spacer should be tracked with correct line count
        assert tui._component_positions[spacer] == (0, 5)


class TestTargetedInvalidation:
    """Phase 4: Targeted invalidation implementation."""

    def test_invalidate_component_clears_specific_lines(self):
        """invalidate_component() should clear only the component's lines."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        text1 = Text("Line 1")
        text2 = Text("Line 2")
        tui.add_child(text1)
        tui.add_child(text2)

        # Initial render to populate _previous_lines
        tui.start()
        tui.render_frame()
        tui.stop()

        # Verify content was rendered
        assert len(tui._previous_lines) > 0
        original_line_count = len(tui._previous_lines)

        # Invalidate only text1
        tui.invalidate_component(text1)

        # Check that text1's lines (0-2) were cleared
        # (set to "" to trigger clearing on next render)
        assert tui._previous_lines[0] == ""
        assert tui._previous_lines[1] == ""
        assert tui._previous_lines[2] == ""

        # But text2's lines should be preserved
        # (not empty strings)
        assert tui._previous_lines[3] != ""
        assert tui._previous_lines[4] != ""
        assert tui._previous_lines[5] != ""

    def test_invalidate_component_unknown_component_ignored(self):
        """invalidate_component() should gracefully ignore unknown components."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        # Component not added to TUI
        orphan = Text("Orphan")

        # Should not raise
        tui.invalidate_component(orphan)

    def test_invalidate_component_requests_render(self):
        """invalidate_component() should request a render."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        text = Text("Hello")
        tui.add_child(text)

        # Render to populate positions
        tui.render(40)

        # Reset render flag
        tui._render_requested = False

        # Invalidate should request render
        tui.invalidate_component(text)
        assert tui._render_requested is True

    def test_full_invalidate_clears_component_positions(self):
        """Full invalidate() should clear component positions."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        text = Text("Hello")
        tui.add_child(text)

        # Render to populate positions
        tui.render(40)
        assert text in tui._component_positions

        # Full invalidate should clear positions
        tui.invalidate()
        assert tui._component_positions == {}

    def test_invalidate_component_handles_size_change(self):
        """invalidate_component() should work when component size changes."""
        terminal = MockTerminal(cols=40, rows=10)
        tui = TUI(terminal)

        # Start with long text (will render multiple lines)
        text = Text("This is a long text that will wrap to multiple lines")
        tui.add_child(text)

        # First render
        tui.start()
        tui.render_frame()
        tui.stop()

        # Store original line count
        original_count = len(tui._previous_lines)

        # Change text to be shorter
        text.set_text("Short")

        # Invalidate - should still work even though size changed
        tui.invalidate_component(text)

        # Lines should be marked for clearing (even if fewer now)
        # The key is that it doesn't crash
