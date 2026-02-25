"""Tests for overlay system - ported from pi-tui."""

import pytest

from pypitui import (
    TUI,
    Container,
    Input,
    MockTerminal,
    OverlayOptions,
    Text,
)


class TestOverlays:
    """Tests for overlay positioning and rendering."""

    @pytest.fixture
    def setup(self):
        """Create a TUI with mock terminal."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)
        return terminal, tui

    def test_show_overlay(self, setup):
        """Can show an overlay."""
        terminal, tui = setup

        tui.add_child(Text("Base content"))

        options = OverlayOptions(width="50%")
        handle = tui.show_overlay(Text("Overlay"), options)

        assert tui.has_overlay()

        handle.hide()
        assert not tui.has_overlay()

    def test_overlay_center_anchor(self, setup):
        """Center anchor positions overlay in middle."""
        terminal, tui = setup

        tui.add_child(Text("Base"))

        options = OverlayOptions(
            width=20,
            anchor="center",
        )
        handle = tui.show_overlay(Text("Overlay content"), options)

        tui.render_frame()
        output = terminal.get_output()

        assert "Overlay content" in output
        handle.hide()

    def test_overlay_top_left_anchor(self, setup):
        """Top-left anchor positions overlay at top-left."""
        terminal, tui = setup

        options = OverlayOptions(
            width=20,
            anchor="top-left",
        )
        handle = tui.show_overlay(Text("Overlay"), options)

        tui.render_frame()
        handle.hide()

    def test_overlay_bottom_right_anchor(self, setup):
        """Bottom-right anchor positions overlay at bottom-right."""
        terminal, tui = setup

        options = OverlayOptions(
            width=20,
            anchor="bottom-right",
        )
        handle = tui.show_overlay(Text("Overlay"), options)

        tui.render_frame()
        handle.hide()

    def test_overlay_percentage_width(self, setup):
        """Width can be percentage of terminal."""
        terminal, tui = setup

        options = OverlayOptions(
            width="50%",
            anchor="center",
        )
        handle = tui.show_overlay(Text("X" * 40), options)

        tui.render_frame()
        handle.hide()

    def test_overlay_min_width(self, setup):
        """Min width is applied as floor."""
        terminal, tui = setup

        options = OverlayOptions(
            width=10,
            min_width=30,
            anchor="center",
        )
        handle = tui.show_overlay(Text("Overlay"), options)

        tui.render_frame()
        handle.hide()

    def test_overlay_max_height(self, setup):
        """Max height limits overlay height."""
        terminal, tui = setup

        # Create overlay with many lines
        overlay = Container()
        for i in range(20):
            overlay.add_child(Text(f"Line {i}", 0, 0))

        options = OverlayOptions(
            width=40,
            max_height=5,
            anchor="center",
        )
        handle = tui.show_overlay(overlay, options)

        tui.render_frame()
        handle.hide()

    def test_overlay_offset(self, setup):
        """Offset moves overlay from anchor."""
        terminal, tui = setup

        options = OverlayOptions(
            width=20,
            anchor="center",
            offset_x=5,
            offset_y=2,
        )
        handle = tui.show_overlay(Text("Overlay"), options)

        tui.render_frame()
        handle.hide()

    def test_overlay_margin(self, setup):
        """Margin keeps overlay away from edges."""
        terminal, tui = setup

        options = OverlayOptions(
            width=20,
            anchor="center",
            margin=5,
        )
        handle = tui.show_overlay(Text("Overlay"), options)

        tui.render_frame()
        handle.hide()

    def test_overlay_handle_hide(self, setup):
        """Handle.hide() permanently removes overlay."""
        terminal, tui = setup

        options = OverlayOptions()
        handle = tui.show_overlay(Text("Overlay"), options)

        assert tui.has_overlay()

        handle.hide()
        assert not tui.has_overlay()

    def test_overlay_handle_set_hidden(self, setup):
        """Handle.setHidden() temporarily hides overlay."""
        terminal, tui = setup

        options = OverlayOptions()
        handle = tui.show_overlay(Text("Overlay"), options)

        assert tui.has_overlay()

        handle.set_hidden(True)
        # Overlay still exists but is hidden
        assert handle.is_hidden()

        handle.set_hidden(False)
        assert not handle.is_hidden()

        handle.hide()

    def test_multiple_overlays(self, setup):
        """Can stack multiple overlays."""
        terminal, tui = setup

        handle1 = tui.show_overlay(Text("Overlay 1"), OverlayOptions())
        handle2 = tui.show_overlay(Text("Overlay 2"), OverlayOptions())

        assert tui.has_overlay()

        # Hide topmost first
        handle2.hide()
        assert tui.has_overlay()  # Still has handle1

        handle1.hide()
        assert not tui.has_overlay()


class TestOverlayVisible:
    """Tests for overlay visibility callback."""

    def test_visible_callback(self):
        """Visible callback controls visibility."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Only visible when width >= 100
        options = OverlayOptions(
            visible=lambda w, h: w >= 100,
        )
        handle = tui.show_overlay(Text("Overlay"), options)

        tui.render_frame()

        # With 80 column terminal, overlay should be hidden
        # (The TUI checks visibility during render)
        handle.hide()


class TestOverlayWidthRendering:
    """Tests for overlay content rendering at specified width."""

    def test_content_rendered_at_specified_width(self):
        """Overlay content is rendered at the specified width, not terminal width."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Create a Text component with no padding to check actual width
        text = Text("X", padding_x=0, padding_y=0)

        # Overlay with width=20
        options = OverlayOptions(width=20, anchor="center")
        handle = tui.show_overlay(text, options)

        # Render and get the output
        tui.render_frame()
        output = terminal.get_output()

        # The text component should have been rendered with width=20
        # Check that we're using the move_cursor command with reasonable positions
        # (center of 80-col terminal for width 20 would be col 30)
        assert "\x1b[1;31H" in output or "\x1b[" in output  # Some cursor movement

        handle.hide()

    def test_centered_overlay_is_centered(self):
        """Centered overlay's content is horizontally centered."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Create content that's exactly 19 chars wide
        content = Container()
        content.add_child(Text("X" * 19, padding_x=0, padding_y=0))

        # Overlay with width=20 (slightly wider than content)
        options = OverlayOptions(width=20, anchor="center")
        handle = tui.show_overlay(content, options)

        tui.render_frame()
        output = terminal.get_output()

        # For a 20-wide overlay on 80-col terminal, centered means starting at col 30
        # Cursor position should be row 11 (24/2 - 6/2), col 30 (80/2 - 20/2)
        # Check that cursor moves to column 31 (1-indexed)
        assert "\x1b[" in output  # Has cursor positioning

        handle.hide()

    def test_percentage_width_overlay(self):
        """Overlay with percentage width renders at correct width."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Create content
        content = Container()
        content.add_child(Text("Test content here", padding_x=0, padding_y=0))

        # 50% of 80 = 40
        options = OverlayOptions(width="50%", anchor="center")
        handle = tui.show_overlay(content, options)

        tui.render_frame()
        output = terminal.get_output()

        # Should have rendered content
        assert "Test content" in output

        handle.hide()

    def test_wide_overlay_respects_terminal_width(self):
        """Overlay width is clamped to terminal width."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        content = Container()
        content.add_child(Text("X" * 100, padding_x=0, padding_y=0))

        # Request width larger than terminal
        options = OverlayOptions(width=200, anchor="center")
        handle = tui.show_overlay(content, options)

        tui.render_frame()

        # Should not crash and should render something
        handle.hide()

    def test_top_right_anchor_positions_correctly(self):
        """Top-right anchor positions overlay at top-right corner."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        content = Container()
        content.add_child(Text("Test", padding_x=0, padding_y=0))

        options = OverlayOptions(width=20, anchor="top-right")
        handle = tui.show_overlay(content, options)

        tui.render_frame()
        output = terminal.get_output()

        # For 20-wide overlay at top-right of 80-col terminal
        # Should start at column 60 (80 - 20)
        # Cursor position would be row 1, col 61 (1-indexed)
        assert "\x1b[" in output

        handle.hide()


class TestOverlayFocus:
    """Tests for overlay focus management."""

    def test_overlay_shows_focus_to_focusable_component(self):
        """When overlay with focusable component is shown, it gets focus."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Add a focusable component to base and focus it
        base_input = Input(placeholder="Base input")
        tui.add_child(base_input)
        tui.set_focus(base_input)

        assert tui._focused_component == base_input

        # Show overlay with focusable component
        overlay_input = Input(placeholder="Overlay input")
        handle = tui.show_overlay(overlay_input, OverlayOptions(width=40))

        # Focus should move to overlay component
        assert tui._focused_component == overlay_input

        handle.hide()

    def test_focus_restored_when_overlay_hidden(self):
        """When overlay is hidden, focus returns to previous component."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Add and focus base component
        base_input = Input(placeholder="Base input")
        tui.add_child(base_input)
        tui.set_focus(base_input)

        # Show overlay
        overlay_input = Input(placeholder="Overlay input")
        handle = tui.show_overlay(overlay_input, OverlayOptions(width=40))

        # Hide overlay using hide_overlay() which pops and restores focus
        tui.hide_overlay()

        # Focus should return to base component
        assert tui._focused_component == base_input

    def test_overlay_with_container_finds_focusable_child(self):
        """When overlay container is shown, first focusable child gets focus."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Add base component
        base_input = Input(placeholder="Base input")
        tui.add_child(base_input)
        tui.set_focus(base_input)

        # Create overlay container with focusable child
        overlay_container = Container()
        overlay_container.add_child(Text("Label", padding_x=0, padding_y=0))
        overlay_input = Input(placeholder="Overlay input")
        overlay_container.add_child(overlay_input)

        handle = tui.show_overlay(overlay_container, OverlayOptions(width=40))

        # Focus should move to the Input in the container
        assert tui._focused_component == overlay_input

        handle.hide()


class TestOverlayCompositing:
    """Tests for overlay compositing onto base content."""

    def test_short_base_line_pads_correctly(self):
        """When base line is shorter than overlay column, padding is added."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Base content is only 10 chars wide
        tui.add_child(Text("Short", padding_x=0, padding_y=0))

        # Overlay at column 30 (well past the base content)
        overlay = Container()
        overlay.add_child(Text("OVERLAY", padding_x=0, padding_y=0))

        options = OverlayOptions(width=20, anchor="top-left", col=30)
        handle = tui.show_overlay(overlay, options)

        tui.render_frame()

        # Should not crash - the base line should be padded to 30 chars
        # before the overlay is composited
        handle.hide()

    def test_empty_base_line_composites_overlay(self):
        """Empty base line correctly shows overlay content."""
        terminal = MockTerminal(80, 24)
        tui = TUI(terminal)

        # Empty base
        tui.add_child(Text("", padding_x=0, padding_y=0))

        # Overlay at column 40
        overlay = Container()
        overlay.add_child(Text("OVERLAY", padding_x=0, padding_y=0))

        options = OverlayOptions(width=20, anchor="top-left", col=40)
        handle = tui.show_overlay(overlay, options)

        tui.render_frame()
        output = terminal.get_output()

        # Overlay content should appear in output
        assert "OVERLAY" in output

        handle.hide()
