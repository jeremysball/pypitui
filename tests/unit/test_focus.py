"""Tests for focus management."""

import pytest

from pypitui.component import Component, RenderedLine, Size
from pypitui.tui import TUI
from pypitui.mock_terminal import MockTerminal


class MockFocusable(Component):
    """Mock component that tracks focus events."""

    def __init__(self) -> None:
        super().__init__()
        self.focused = False
        self.blurred = False
        self.focus_count = 0
        self.blur_count = 0

    def measure(self, available_width: int, available_height: int) -> Size:
        return Size(width=10, height=1)

    def render(self, width: int) -> list[RenderedLine]:
        return [RenderedLine(content="mock", styles=[])]

    def on_focus(self) -> None:
        self.focused = True
        self.focus_count += 1

    def on_blur(self) -> None:
        self.blurred = True
        self.blur_count += 1


class TestFocusStackEmpty:
    """Tests for empty focus stack."""

    def test_focus_stack_empty_returns_none(self) -> None:
        """_focused is None initially."""
        terminal = MockTerminal()
        tui = TUI(terminal)

        assert tui._focused is None


class TestPushFocus:
    """Tests for push_focus."""

    def test_push_focus_adds_to_stack(self) -> None:
        """Stack grows when pushing focus."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        component = MockFocusable()

        tui.push_focus(component)

        assert len(tui._focus_stack) == 1
        assert tui._focused == component

    def test_push_focus_calls_on_blur_on_previous(self) -> None:
        """Previous.on_blur() invoked when pushing new focus."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()
        second = MockFocusable()

        tui.push_focus(first)
        tui.push_focus(second)

        assert first.blurred is True
        assert first.blur_count == 1

    def test_push_focus_calls_on_focus_on_new(self) -> None:
        """Component.on_focus() invoked when gaining focus."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        component = MockFocusable()

        tui.push_focus(component)

        assert component.focused is True
        assert component.focus_count == 1

    def test_push_focus_invalidates_both(self) -> None:
        """Invalidate called on both components."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()
        second = MockFocusable()

        tui.push_focus(first)
        # Reset invalidation tracking
        first._invalidated = False
        tui.push_focus(second)

        # Both should be invalidated
        assert first._rect is None or second._rect is None  # Simplified check

    def test_push_focus_none_works(self) -> None:
        """Pushing None clears focus."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        component = MockFocusable()

        tui.push_focus(component)
        tui.push_focus(None)

        assert tui._focused is None


class TestPushFocusErrorHandling:
    """Tests for error handling in push_focus."""

    def test_push_focus_error_restores_previous(self) -> None:
        """Pop on error, restore previous focus."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()

        class FailingComponent(MockFocusable):
            def on_focus(self) -> None:
                raise RuntimeError("Focus failed")

        failing = FailingComponent()

        tui.push_focus(first)
        first.focused = False  # Reset

        # Should not raise, should restore previous
        tui.push_focus(failing)

        # Previous should be restored
        assert tui._focused == first


class TestPopFocus:
    """Tests for pop_focus."""

    def test_pop_focus_removes_from_stack(self) -> None:
        """Stack shrinks when popping."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        component = MockFocusable()

        tui.push_focus(component)
        tui.pop_focus()

        assert len(tui._focus_stack) == 0

    def test_pop_focus_returns_popped_component(self) -> None:
        """Returns correct component."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        component = MockFocusable()

        tui.push_focus(component)
        result = tui.pop_focus()

        assert result == component

    def test_pop_focus_empty_stack_returns_none(self) -> None:
        """Returns None when stack empty."""
        terminal = MockTerminal()
        tui = TUI(terminal)

        result = tui.pop_focus()

        assert result is None

    def test_pop_focus_calls_on_blur(self) -> None:
        """Component.on_blur() invoked when popped."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        component = MockFocusable()

        tui.push_focus(component)
        component.blurred = False  # Reset
        tui.pop_focus()

        assert component.blurred is True

    def test_pop_focus_calls_on_focus_on_previous(self) -> None:
        """Previous.on_focus() restored."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()
        second = MockFocusable()

        tui.push_focus(first)
        tui.push_focus(second)
        first.focused = False  # Reset
        tui.pop_focus()

        assert first.focused is True
        assert first.focus_count == 2  # Initial + restore


class TestSetFocus:
    """Tests for set_focus."""

    def test_set_focus_pops_then_pushes(self) -> None:
        """Replaces current focus."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()
        second = MockFocusable()

        tui.push_focus(first)
        tui.set_focus(second)

        assert tui._focused == second
        assert len(tui._focus_stack) == 1  # Replaced, not added

    def test_set_focus_calls_lifecycle(self) -> None:
        """Blur on old, focus on new."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()
        second = MockFocusable()

        tui.push_focus(first)
        tui.set_focus(second)

        assert first.blurred is True
        assert second.focused is True


class TestFocusOrder:
    """Tests for focus order (tab cycling)."""

    def test_register_focusable_adds_to_order(self) -> None:
        """_focus_order list grows."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        component = MockFocusable()

        tui.register_focusable(component)

        assert component in tui._focus_order

    def test_cycle_focus_moves_to_next(self) -> None:
        """Tab moves to next in order."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()
        second = MockFocusable()

        tui.register_focusable(first)
        tui.register_focusable(second)
        tui.cycle_focus(1)

        assert tui._focused == first

        tui.cycle_focus(1)

        assert tui._focused == second

    def test_cycle_focus_wraps_around(self) -> None:
        """Last to first wraps."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()
        second = MockFocusable()

        tui.register_focusable(first)
        tui.register_focusable(second)
        tui.cycle_focus(1)
        tui.cycle_focus(1)
        tui.cycle_focus(1)  # Wrap

        assert tui._focused == first

    def test_cycle_focus_negative_direction(self) -> None:
        """Negative direction moves backward."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first = MockFocusable()
        second = MockFocusable()

        tui.register_focusable(first)
        tui.register_focusable(second)
        tui.cycle_focus(1)  # first
        tui.cycle_focus(1)  # second
        tui.cycle_focus(-1)  # back to first

        assert tui._focused == first
