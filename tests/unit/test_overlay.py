"""Tests for overlay system."""

import pytest

from pypitui.component import Component, RenderedLine, Size
from pypitui.overlay import Overlay, OverlayPosition
from pypitui.tui import TUI
from pypitui.mock_terminal import MockTerminal


class MockComponent(Component):
    """Mock component for testing overlays."""

    def __init__(self, lines: list[str] | None = None) -> None:
        super().__init__()
        self._lines = lines or ["content"]
        self.focused = False
        self.blurred = False

    def measure(self, available_width: int, available_height: int) -> Size:
        return Size(width=10, height=len(self._lines))

    def render(self, width: int) -> list[RenderedLine]:
        return [
            RenderedLine(content=line[:width], styles=[])
            for line in self._lines
        ]

    def on_focus(self) -> None:
        self.focused = True

    def on_blur(self) -> None:
        self.blurred = True


class TestOverlayPosition:
    """Tests for OverlayPosition dataclass."""

    def test_overlay_position_fields(self) -> None:
        """Row, col, width, height, anchor stored."""
        pos = OverlayPosition(
            row=5,
            col=10,
            width=20,
            height=3,
            anchor="center"
        )

        assert pos.row == 5
        assert pos.col == 10
        assert pos.width == 20
        assert pos.height == 3
        assert pos.anchor == "center"

    def test_overlay_position_defaults(self) -> None:
        """Default values for optional fields."""
        pos = OverlayPosition(row=0)

        assert pos.col == 0
        assert pos.width == -1
        assert pos.height == -1
        assert pos.anchor is None

    def test_overlay_position_negative_row(self) -> None:
        """Negative row means from bottom."""
        pos = OverlayPosition(row=-1)

        assert pos.row == -1


class TestOverlayWrapper:
    """Tests for Overlay class."""

    def test_overlay_wraps_component(self) -> None:
        """Content is Component instance."""
        content = MockComponent()
        position = OverlayPosition(row=0)
        overlay = Overlay(content=content, position=position)

        assert overlay.content == content

    def test_overlay_visible_flag(self) -> None:
        """Visible: bool = True."""
        content = MockComponent()
        position = OverlayPosition(row=0)
        overlay = Overlay(content=content, position=position)

        assert overlay.visible is True

        overlay.visible = False

        assert overlay.visible is False

    def test_overlay_z_index(self) -> None:
        """Z-index: int = 0 for stacking."""
        content = MockComponent()
        position = OverlayPosition(row=0)
        overlay = Overlay(content=content, position=position)

        assert overlay.z_index == 0

    def test_overlay_custom_z_index(self) -> None:
        """Custom z-index supported."""
        content = MockComponent()
        position = OverlayPosition(row=0)
        overlay = Overlay(
            content=content,
            position=position,
            z_index=5
        )

        assert overlay.z_index == 5


class TestTUIShowOverlay:
    """Tests for TUI.show_overlay()."""

    def test_show_overlay_adds_to_list(self) -> None:
        """_overlays grows."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        overlay = Overlay(content=MockComponent(), position=OverlayPosition(row=0))

        tui.show_overlay(overlay)

        assert overlay in tui._overlays

    def test_show_overlay_pushes_content_focus(self) -> None:
        """Overlay.content gets focus."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        content = MockComponent()
        overlay = Overlay(content=content, position=OverlayPosition(row=0))

        tui.show_overlay(overlay)

        assert tui._focused == content
        assert content.focused is True


class TestTUICloseOverlay:
    """Tests for TUI.close_overlay()."""

    def test_close_overlay_removes_from_list(self) -> None:
        """_overlays shrinks."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        overlay = Overlay(content=MockComponent(), position=OverlayPosition(row=0))

        tui.show_overlay(overlay)
        tui.close_overlay(overlay)

        assert overlay not in tui._overlays

    def test_close_overlay_pops_content_focus(self) -> None:
        """Focus restored if overlay.content is current."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        content = MockComponent()
        overlay = Overlay(content=content, position=OverlayPosition(row=0))

        tui.show_overlay(overlay)
        tui.close_overlay(overlay)

        assert tui._focused is None
        assert content.blurred is True


class TestNestedOverlays:
    """Tests for nested overlay support."""

    def test_nested_overlays_stack_focus(self) -> None:
        """Multiple overlays push/pop correctly."""
        terminal = MockTerminal()
        tui = TUI(terminal)
        first_content = MockComponent()
        second_content = MockComponent()

        first = Overlay(content=first_content, position=OverlayPosition(row=0))
        second = Overlay(content=second_content, position=OverlayPosition(row=1))

        tui.show_overlay(first)
        tui.show_overlay(second)

        assert tui._focused == second_content

        tui.close_overlay(second)

        assert tui._focused == first_content


class TestPositionResolution:
    """Tests for overlay position resolution."""

    def test_resolve_position_absolute(self) -> None:
        """Row=5, col=10 → screen coordinates."""
        terminal = MockTerminal()
        tui = TUI(terminal)

        pos = OverlayPosition(row=5, col=10, width=20, height=3)
        resolved = tui._resolve_position(pos, 80, 24)

        assert resolved == (5, 10, 20, 3)

    def test_resolve_position_negative_row(self) -> None:
        """Row=-1 → bottom row."""
        terminal = MockTerminal()
        tui = TUI(terminal)

        pos = OverlayPosition(row=-1, height=1)
        resolved = tui._resolve_position(pos, 80, 24)

        assert resolved[0] == 23  # Bottom row

    def test_resolve_position_clamping(self) -> None:
        """Position clamped to terminal bounds."""
        terminal = MockTerminal()
        tui = TUI(terminal)

        pos = OverlayPosition(row=100, col=100, width=50, height=10)
        resolved = tui._resolve_position(pos, 80, 24)

        # Should be clamped to fit in terminal
        row, col, width, height = resolved
        assert row + height <= 24
        assert col + width <= 80


class TestOverlayCompositing:
    """Tests for overlay compositing."""

    def test_composite_overlay_stamps_content(self) -> None:
        """Overlay lines merged into buffer."""
        terminal = MockTerminal()
        tui = TUI(terminal)

        # Base content
        base_lines = [
            RenderedLine(content="base line 0", styles=[]),
            RenderedLine(content="base line 1", styles=[]),
        ]

        # Overlay content
        overlay_content = MockComponent(["OVERLAY"])
        overlay = Overlay(
            content=overlay_content,
            position=OverlayPosition(row=0, col=0, width=7, height=1)
        )

        composited = tui._composite_overlay(base_lines, overlay, 80, 24)

        # Overlay replaces first 7 chars, rest is padded
        assert composited[0].content.startswith("OVERLAY")

    def test_composite_overlay_respects_position(self) -> None:
        """Content at resolved offset."""
        terminal = MockTerminal()
        tui = TUI(terminal)

        base_lines = [
            RenderedLine(content="0123456789", styles=[]),
        ]

        overlay_content = MockComponent(["XXXX"])
        overlay = Overlay(
            content=overlay_content,
            position=OverlayPosition(row=0, col=2, width=4, height=1)
        )

        composited = tui._composite_overlay(base_lines, overlay, 10, 24)

        assert composited[0].content == "01XXXX6789"

    def test_composite_overlay_clipping(self) -> None:
        """Content past terminal bounds truncated."""
        terminal = MockTerminal()
        tui = TUI(terminal)

        base_lines = [
            RenderedLine(content="0123456789", styles=[]),
        ]

        overlay_content = MockComponent(["VERYLONGCONTENT"])
        overlay = Overlay(
            content=overlay_content,
            position=OverlayPosition(row=0, col=5, width=20, height=1)
        )

        composited = tui._composite_overlay(base_lines, overlay, 10, 24)

        # Should be clipped to terminal width
        assert len(composited[0].content) == 10
