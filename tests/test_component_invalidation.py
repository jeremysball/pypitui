"""Tests for component-aware invalidation with parent references."""

import pytest
from pypitui import TUI, Container, Text, Component
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
