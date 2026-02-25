"""Core TUI implementation with differential rendering.

Based on @mariozechner/pi-tui's component model.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

from .terminal import Terminal
from .utils import slice_by_column, visible_width

# Cursor position marker - APC (Application Program Command) sequence
CURSOR_MARKER = "\x1b_pi:c\x07"


class Component(ABC):
    """Component interface - all components must implement this.

    Components are the building blocks of the TUI, similar to React components.
    Each component is responsible for rendering itself to a list of strings.
    """

    @abstractmethod
    def render(self, width: int) -> list[str]:
        """Render the component to lines for the given viewport width.

        Args:
            width: Current viewport width in columns

        Returns:
            Array of strings, each representing a line.
            Each line must not exceed `width` visible characters.
        """
        pass

    def handle_input(self, data: str) -> None:  # noqa: B027
        """Optional handler for keyboard input when component has focus.

        Args:
            data: Raw input data from terminal
        """
        pass

    @property
    def wants_key_release(self) -> bool:
        """If True, component receives key release events (Kitty protocol).

        Default is False - release events are filtered out.
        """
        return False

    @abstractmethod
    def invalidate(self) -> None:
        """Invalidate any cached rendering state.

        Called when theme changes or when component needs to re-render from scratch.
        """
        pass


class Focusable(ABC):
    """Interface for components that can receive focus and display a hardware cursor.

    When focused, the component should emit CURSOR_MARKER at the cursor position
    in its render output. TUI will find this marker and position the hardware
    cursor there for proper IME candidate window positioning.
    """

    @property
    @abstractmethod
    def focused(self) -> bool:
        """Set by TUI when focus changes. Component should emit CURSOR_MARKER when True."""
        pass

    @focused.setter
    @abstractmethod
    def focused(self, value: bool) -> None:
        pass


def is_focusable(component: Component | None) -> bool:
    """Type guard to check if a component implements Focusable."""
    return isinstance(component, Focusable)


# Type alias for size values
SizeValue = int | str  # e.g., 50 or "50%"

# Anchor position for overlays
OverlayAnchor = str  # "center", "top-left", "top-right", etc.


@dataclass
class OverlayMargin:
    """Margin configuration for overlays."""

    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0


@dataclass
class OverlayOptions:
    """Options for overlay positioning and sizing.

    Values can be absolute numbers or percentage strings (e.g., "50%").
    """

    width: SizeValue | None = None
    min_width: int | None = None
    max_height: SizeValue | None = None
    anchor: OverlayAnchor = "center"
    offset_x: int = 0
    offset_y: int = 0
    row: SizeValue | None = None
    col: SizeValue | None = None
    margin: OverlayMargin | int | None = None
    visible: Callable[[int, int], bool] | None = None


@dataclass
class OverlayHandle:
    """Handle returned by show_overlay for controlling the overlay."""

    overlay: _OverlayEntry

    def hide(self) -> None:
        """Permanently remove the overlay (cannot be shown again)."""
        self.overlay.closed = True

    def set_hidden(self, hidden: bool) -> None:
        """Temporarily hide or show the overlay."""
        self.overlay.hidden = hidden

    def is_hidden(self) -> bool:
        """Check if overlay is temporarily hidden."""
        return self.overlay.hidden


@dataclass
class _OverlayEntry:
    """Internal overlay entry."""

    component: Component
    options: OverlayOptions
    hidden: bool = False
    closed: bool = False
    previous_focus: Component | None = None


class Container(Component):
    """Container - a component that contains other components.

    Components are arranged vertically in the order they were added.
    """

    def __init__(self) -> None:
        self.children: list[Component] = []

    def add_child(self, component: Component) -> None:
        """Add a child component."""
        self.children.append(component)

    def remove_child(self, component: Component) -> None:
        """Remove a child component."""
        if component in self.children:
            self.children.remove(component)

    def clear(self) -> None:
        """Remove all child components."""
        self.children.clear()

    def invalidate(self) -> None:
        """Invalidate all children."""
        for child in self.children:
            child.invalidate()

    def render(self, width: int) -> list[str]:
        """Render all children vertically."""
        lines: list[str] = []
        for child in self.children:
            child_lines = child.render(width)
            lines.extend(child_lines)
        return lines


class TUI(Container):
    """Main class for managing terminal UI with differential rendering.

    The TUI manages the terminal state, handles input, and renders components
    efficiently by only updating changed lines.

    IMPORTANT: Reuse TUI instances when switching screens. Creating new TUI
    instances loses the _previous_lines state needed for differential rendering,
    causing ghost content from previous screens. Instead, call tui.clear() to
    remove children, then add new children - the existing _previous_lines will
    ensure old content is properly cleared.

    Example:
        # WRONG - loses differential rendering state
        self.tui = TUI(terminal)
        self.tui.add_child(...)

        # RIGHT - reuse TUI, preserves _previous_lines
        self.tui.clear()  # Remove old children
        self.tui.add_child(...)  # Add new content
    """

    # ANSI reset sequence: reset attributes, clear to end of line, end hyperlink
    _SEGMENT_RESET = "\x1b[0m\x1b[K\x1b]8;;\x07"

    def __init__(
        self,
        terminal: Terminal,
        show_hardware_cursor: bool = False,
        clear_on_shrink: bool = True,
        use_alternate_buffer: bool = False,
    ) -> None:
        super().__init__()
        self.terminal = terminal
        self._show_hardware_cursor = show_hardware_cursor
        self._clear_on_shrink = clear_on_shrink
        self._use_alternate_buffer = use_alternate_buffer

        # State for differential rendering
        self._previous_lines: list[str] = []
        self._previous_width: int = 0

        # Focus management
        self._focused_component: Component | None = None

        # Input handling
        self._input_listeners: list[Callable[[str], dict | None]] = []

        # Rendering state
        self._render_requested = False
        self._cursor_row: int = 0
        self._hardware_cursor_row: int = -1
        self._input_buffer: str = ""
        self._max_lines_rendered: int = 0
        self._first_visible_row_previous: int = 0  # First visible row in scrollback from last frame
        self._stopped = False

        # Overlay stack
        self._overlay_stack: list[_OverlayEntry] = []

        # Terminal size tracking for resize detection
        self._last_terminal_size: tuple[int, int] = (0, 0)

        # Debug callback
        self.on_debug: Callable[[], None] | None = None

    @property
    def clear_on_shrink(self) -> bool:
        return self._clear_on_shrink

    @clear_on_shrink.setter
    def clear_on_shrink(self, enabled: bool) -> None:
        """Set whether to trigger full re-render when content shrinks.

        When True (default), empty rows are cleared when content shrinks.
        When False, empty rows remain (reduces redraws on slower terminals).
        """
        self._clear_on_shrink = enabled

    def set_focus(self, component: Component | None) -> None:
        """Set the focused component."""
        # Unfocus previous
        if self._focused_component and is_focusable(self._focused_component):
            self._focused_component.focused = False  # type: ignore[attr-defined]

        self._focused_component = component

        # Focus new
        if component and is_focusable(component):
            component.focused = True  # type: ignore[attr-defined]

    def show_overlay(
        self, component: Component, options: OverlayOptions | None = None
    ) -> OverlayHandle:
        """Show an overlay component with configurable positioning and sizing.

        Args:
            component: The component to display as overlay
            options: Positioning and sizing options

        Returns:
            Handle to control the overlay's visibility
        """
        opts = options or OverlayOptions()
        entry = _OverlayEntry(component, opts, previous_focus=self._focused_component)
        self._overlay_stack.append(entry)

        # Set focus to overlay component if it's focusable
        if is_focusable(component):
            self.set_focus(component)
        # Or if the overlay has children, try to focus the first focusable one
        elif hasattr(component, "children"):
            for child in component.children:
                if is_focusable(child):
                    self.set_focus(child)
                    break

        self.request_render()
        return OverlayHandle(entry)

    def hide_overlay(self) -> None:
        """Hide the topmost overlay and restore previous focus."""
        if self._overlay_stack:
            entry = self._overlay_stack.pop()
            entry.closed = True

            # Restore previous focus
            if entry.previous_focus:
                self.set_focus(entry.previous_focus)

            self.request_render()

    def has_overlay(self) -> bool:
        """Check if there are any visible overlays."""
        return any(not entry.hidden and not entry.closed for entry in self._overlay_stack)

    def _is_overlay_visible(self, entry: _OverlayEntry) -> bool:
        """Check if an overlay entry is currently visible."""
        return not entry.hidden and not entry.closed

    def _get_topmost_visible_overlay(self) -> _OverlayEntry | None:
        """Find the topmost visible overlay, if any."""
        for entry in reversed(self._overlay_stack):
            if self._is_overlay_visible(entry):
                return entry
        return None

    def invalidate(self) -> None:
        """Invalidate the TUI and all children."""
        self._previous_lines = []
        for child in self.children:
            child.invalidate()
        for entry in self._overlay_stack:
            entry.component.invalidate()

    def start(self) -> None:
        """Start the TUI - set up terminal for rendering."""
        if self._use_alternate_buffer:
            self.terminal.enter_alternate_screen()
        else:
            # Save cursor position and clear screen for main buffer mode
            self.terminal.write("\x1b[s")  # Save cursor
            self.terminal.write("\x1b[H")  # Move to home first
            self.terminal.write("\x1b[2J")  # Clear screen

        self.terminal.hide_cursor()
        self.terminal.set_raw_mode()
        self._stopped = False
        self._previous_lines = []  # Reset differential rendering

    def stop(self) -> None:
        """Stop the TUI - restore terminal state."""
        self._stopped = True

        if not self._use_alternate_buffer:
            # Clear our content and restore cursor in main buffer mode
            self.terminal.write("\x1b[H")  # Move to home first
            self.terminal.write("\x1b[2J")  # Clear screen
            self.terminal.write("\x1b[u")  # Restore cursor

        self.terminal.show_cursor()

        if self._use_alternate_buffer:
            self.terminal.exit_alternate_screen()

        self.terminal.restore_mode()

    def add_input_listener(self, listener: Callable[[str], dict | None]) -> Callable[[], None]:
        """Add an input listener. Returns a function to remove the listener."""
        self._input_listeners.append(listener)

        def remove() -> None:
            if listener in self._input_listeners:
                self._input_listeners.remove(listener)

        return remove

    def request_render(self, force: bool = False) -> None:
        """Request a render on next frame.

        Args:
            force: If True, force full redraw (clear differential rendering cache)
        """
        self._render_requested = True
        if force:
            self._previous_lines = []

    def handle_input(self, data: str) -> None:
        """Handle keyboard input - forwards to focused component.
        
        Call this from your main loop with data from terminal.read_sequence().
        """
        self._handle_input(data)

    def _handle_input(self, data: str) -> None:
        """Process input data."""
        # Check for debug key (Shift+Ctrl+D)
        if data == "\x04" and self.on_debug:
            self.on_debug()
            return

        # Notify listeners
        for listener in self._input_listeners:
            result = listener(data)
            if result and result.get("consume"):
                return

        # Check for escape to close overlay
        if data == "\x1b" and self.has_overlay():
            self.hide_overlay()
            return

        # Send to focused component
        if self._focused_component and hasattr(self._focused_component, "handle_input"):
            self._focused_component.handle_input(data)

    def _resolve_size_value(self, value: SizeValue | None, total: int) -> int:
        """Resolve a SizeValue to actual pixels."""
        if value is None:
            return total
        if isinstance(value, str) and value.endswith("%"):
            try:
                pct = int(value[:-1])
                return int(total * pct / 100)
            except ValueError:
                return total
        return int(value)

    def _resolve_anchor_row(
        self, anchor: str, height: int, content_height: int, offset_y: int
    ) -> int:
        """Calculate row position from anchor."""
        row = 0
        if "top" in anchor:
            row = 0
        elif "bottom" in anchor:
            row = max(0, height - content_height)
        else:  # center
            row = max(0, (height - content_height) // 2)
        return row + offset_y

    def _resolve_anchor_col(
        self, anchor: str, width: int, content_width: int, offset_x: int
    ) -> int:
        """Calculate column position from anchor."""
        col = 0
        if "left" in anchor:
            col = 0
        elif "right" in anchor:
            col = max(0, width - content_width)
        else:  # center
            col = max(0, (width - content_width) // 2)
        return col + offset_x

    def _resolve_overlay_layout(
        self, options: OverlayOptions, term_width: int, term_height: int, content_height: int
    ) -> tuple[int, int, int, int]:
        """Resolve overlay layout from options.

        Returns (width, row, col, max_height).
        """
        # Resolve width
        width = self._resolve_size_value(options.width, term_width)
        if options.min_width and width < options.min_width:
            width = options.min_width
        width = min(width, term_width)

        # Resolve max height
        max_height = self._resolve_size_value(options.max_height, term_height)
        if max_height == 0 or max_height > term_height:
            max_height = term_height

        # Apply margins
        margin = options.margin
        if isinstance(margin, int):
            margin_top = margin_bottom = margin_left = margin_right = margin
        elif margin:
            margin_top = margin.top
            margin_bottom = margin.bottom
            margin_left = margin.left
            margin_right = margin.right
        else:
            margin_top = margin_bottom = margin_left = margin_right = 0

        # Adjust for margins
        avail_width = term_width - margin_left - margin_right
        avail_height = term_height - margin_top - margin_bottom

        width = min(width, avail_width)
        max_height = min(max_height, avail_height)

        # Resolve position
        if options.row is not None:
            row = self._resolve_size_value(options.row, term_height)
        else:
            row = self._resolve_anchor_row(
                options.anchor, avail_height, min(content_height, max_height), options.offset_y
            )

        if options.col is not None:
            col = self._resolve_size_value(options.col, term_width)
        else:
            col = self._resolve_anchor_col(options.anchor, avail_width, width, options.offset_x)

        row += margin_top
        col += margin_left

        return (width, row, col, max_height)

    def _composite_overlays(
        self, base_lines: list[str], term_width: int, term_height: int
    ) -> list[str]:
        """Composite all overlays into content lines (in stack order)."""
        result = list(base_lines)

        for entry in self._overlay_stack:
            if not self._is_overlay_visible(entry):
                continue

            # Check visibility condition
            if entry.options.visible and not entry.options.visible(term_width, term_height):
                continue

            # Calculate margins first
            margin = entry.options.margin
            if isinstance(margin, int):
                margin_left = margin_right = margin
            elif margin:
                margin_left = margin.left
                margin_right = margin.right
            else:
                margin_left = margin_right = 0

            avail_width = term_width - margin_left - margin_right

            # Resolve width (same logic as _resolve_overlay_layout)
            width = self._resolve_size_value(entry.options.width, term_width)
            if entry.options.min_width and width < entry.options.min_width:
                width = entry.options.min_width
            width = min(width, term_width)
            width = min(width, avail_width)

            # Render overlay content at the resolved width
            content = entry.component.render(width)
            content_height = len(content)

            # Now resolve full layout (row, col, max_height) with actual content height
            _, row, col, max_height = self._resolve_overlay_layout(
                entry.options, term_width, term_height, content_height
            )

            # Limit content to max_height
            if len(content) > max_height:
                content = content[:max_height]

            # Composite each line
            for i, overlay_line in enumerate(content):
                target_row = row + i
                if target_row < 0 or target_row >= term_height:
                    continue

                # Ensure result has enough lines
                while len(result) <= target_row:
                    result.append("")

                result[target_row] = self._composite_line_at(
                    result[target_row], overlay_line, col, width, term_width
                )

        return result

    def _composite_line_at(
        self, base_line: str, overlay_line: str, col: int, width: int, total_width: int
    ) -> str:
        """Splice overlay content into a base line at a specific column."""
        # Get before segment (everything up to col)
        before = slice_by_column(base_line, 0, col)

        # Pad before if it's shorter than col (base line was shorter)
        before_width = visible_width(before)
        if before_width < col:
            before += " " * (col - before_width)

        # Get overlay content, limited to its width
        overlay = slice_by_column(overlay_line, 0, width)
        # Preserve trailing reset code if original had one (prevents color bleeding)
        if overlay_line.rstrip().endswith("\x1b[0m") and not overlay.endswith("\x1b[0m"):
            overlay += "\x1b[0m"
        overlay_visible_width = visible_width(overlay)

        # Calculate where overlay ends and after segment begins
        after_start = col + overlay_visible_width

        # Calculate remaining width for after segment
        remaining_width = total_width - after_start
        remaining_width = max(remaining_width, 0)

        # Get after segment
        after = slice_by_column(base_line, after_start, remaining_width)

        # Pad after if needed to fill total_width
        after_width = visible_width(after)
        if after_start + after_width < total_width:
            after += " " * (total_width - after_start - after_width)

        return before + overlay + after

    def _apply_line_resets(self, lines: list[str]) -> list[str]:
        """Apply SGR reset at end of each line."""
        return [line + self._SEGMENT_RESET for line in lines]

    def _extract_cursor_position(self, lines: list[str], height: int) -> tuple[int, int] | None:
        """Find and extract cursor position from rendered lines.

        Searches for CURSOR_MARKER, calculates its position, and strips it.
        Only scans the bottom terminal height lines (visible viewport).

        Returns:
            (row, col) or None if no marker found
        """
        # Scan from bottom up (viewport area)
        start_line = max(0, len(lines) - height)

        for i in range(len(lines) - 1, start_line - 1, -1):
            line = lines[i]
            pos = line.find(CURSOR_MARKER)
            if pos != -1:
                # Calculate column position
                before_marker = line[:pos]
                col = visible_width(before_marker)
                # Return position and stripped line
                return (i, col)

        return None

    def render_frame(self) -> None:
        """Render a single frame."""
        if self._stopped:
            return

        self._render_requested = False

        # Get terminal size
        term_width, term_height = self.terminal.get_size()

        # Check for terminal resize
        current_size = (term_width, term_height)
        if current_size != self._last_terminal_size:
            self._last_terminal_size = current_size
            self._previous_lines = []  # Force full redraw
            self.invalidate()  # Invalidate all children

        # Render base content
        base_lines = self.render(term_width)

        # Composite overlays
        lines = self._composite_overlays(base_lines, term_width, term_height)

        # Apply line resets
        lines = self._apply_line_resets(lines)

        # Extract cursor position before output
        cursor_pos = self._extract_cursor_position(lines, term_height)

        # Strip cursor markers from output
        lines = [line.replace(CURSOR_MARKER, "") for line in lines]

        # Differential rendering
        for i, line in enumerate(lines):
            if i >= len(self._previous_lines) or self._previous_lines[i] != line:
                self.terminal.move_cursor(i, 0)
                self.terminal.write(line)

        # Clear remaining lines if content shrank
        if self._clear_on_shrink and len(lines) < len(self._previous_lines):
            for i in range(len(lines), len(self._previous_lines)):
                self.terminal.move_cursor(i, 0)
                self.terminal.write(" " * term_width)

        # Position hardware cursor if needed
        self._position_hardware_cursor(cursor_pos, len(lines))

        self._previous_lines = lines
        self._previous_width = term_width
        self._max_lines_rendered = max(self._max_lines_rendered, len(lines))

    def _position_hardware_cursor(
        self, cursor_pos: tuple[int, int] | None, total_lines: int
    ) -> None:
        """Position the hardware cursor for IME candidate window."""
        if not self._show_hardware_cursor:
            return

        if cursor_pos:
            row, col = cursor_pos
            if row < total_lines:
                self.terminal.move_cursor(row, col)
                self.terminal.show_cursor()
                self._hardware_cursor_row = row
                return

        self.terminal.hide_cursor()

    def _calculate_first_visible_row(self, term_height: int) -> int:
        """Calculate which line in the scrollback buffer is at the top of the terminal.

        When content exceeds terminal height, this tells us the first line
        of the scrollback that's currently visible. Lines before this are
        in the terminal's native scrollback history (accessible via Shift+PgUp).

        Args:
            term_height: Current terminal height in rows

        Returns:
            The line number (0-indexed) in the virtual canvas that appears
            at the top of the terminal screen.

        Example:
            If max_lines_rendered=100 and term_height=24:
            - Returns 76 (lines 0-75 are in scrollback, lines 76-99 are visible)
        """
        return max(0, self._max_lines_rendered - term_height)

    def _begin_sync(self) -> str:
        """Begin synchronized output mode (DEC 2026).

        This tells the terminal to buffer all output until _end_sync() is called,
        preventing flickering during partial screen updates. Terminals that don't
        support this mode will simply ignore it (graceful degradation).

        Returns:
            Escape sequence to begin synchronized output: "\\x1b[?2026h"
        """
        return "\x1b[?2026h"

    def _end_sync(self) -> str:
        """End synchronized output mode (DEC 2026).

        Flushes the buffered output to the screen as a single atomic update.
        Must be called after _begin_sync() to make changes visible.

        Returns:
            Escape sequence to end synchronized output: "\\x1b[?2026l"
        """
        return "\x1b[?2026l"

    def _move_cursor_relative(self, target_row: int) -> str:
        """Generate escape sequence to move cursor relative to current position.

        Uses relative cursor movement (\x1b[nA/B) instead of absolute positioning.
        This allows content to flow into the terminal's scrollback buffer.

        Args:
            target_row: The row to move to (0-indexed in virtual canvas)

        Returns:
            Escape sequence to move cursor, or empty string if already at target.

        Example:
            If cursor is at row 5 and target is row 8:
            - Returns "\\x1b[3B" (move down 3 lines)
            - Updates _hardware_cursor_row to 8
        """
        delta = target_row - self._hardware_cursor_row

        if delta == 0:
            return ""

        if delta > 0:
            # Move cursor down
            self._hardware_cursor_row = target_row
            return self.terminal.move_cursor_down(delta)
        else:
            # Move cursor up (negative delta)
            self._hardware_cursor_row = target_row
            return self.terminal.move_cursor_up(-delta)

    def run_frame(self) -> bool:
        """Run a single frame - process input and render.

        Returns:
            True if should continue, False if should stop.
        """
        if self._stopped:
            return False

        # Check for input
        while True:
            char = self.terminal.read(timeout=0.0)
            if char is None:
                break
            self._input_buffer += char

            # Try to parse complete sequences
            key = self._try_parse_input(self._input_buffer)
            if key is not None:
                self._input_buffer = ""
                self._handle_input(key)

        # Render if needed
        if self._render_requested:
            self.render_frame()

        return True

    def _try_parse_input(self, data: str) -> str | None:
        """Try to parse a complete input sequence."""
        if not data:
            return None

        # Check for complete escape sequences
        if data.startswith("\x1b"):
            # CSI sequences
            if len(data) >= 3 and data[1] == "[":
                # Wait for alphabetic or ~ terminator
                if data[-1].isalpha() or data[-1] == "~":
                    return data
                # Or CSI u format
                if "u" in data:
                    return data
                return None
            # SS3 sequences (F1-F4)
            if len(data) == 3 and data[1] == "O":
                return data
            # Just ESC is a complete sequence
            if len(data) == 1:
                return data
            # Alt+key combination
            if len(data) == 2:
                return data
            return None

        # Single byte is complete
        if len(data) == 1:
            return data

        return None

    def run(self) -> None:
        """Main run loop."""
        self.start()
        try:
            while self.run_frame():
                import time

                time.sleep(0.016)  # ~60fps
        finally:
            self.stop()
