"""TUI rendering engine with differential output.

Provides the TUI class that manages component rendering,
differential output, viewport tracking, and overlay management.
"""

from typing import Protocol

from pypitui.component import Component, Rect


class TerminalProtocol(Protocol):
    """Protocol for terminal implementations."""

    def write(self, data: str | bytes) -> None: ...
    def move_cursor(self, col: int, row: int) -> None: ...
    def clear_line(self) -> None: ...
    def clear_screen(self) -> None: ...
    def hide_cursor(self) -> None: ...
    def show_cursor(self) -> None: ...


class TUI:
    """Terminal User Interface rendering engine.

    Manages component hierarchy, differential rendering, and viewport tracking.

    Attributes:
        terminal: The Terminal instance for I/O
        _previous_lines: Dict mapping row -> content hash for diffing
        _max_lines_rendered: Maximum lines ever rendered (for cleanup)
        _viewport_top: Current viewport scroll position
        _hardware_cursor_row: Current hardware cursor row
        _hardware_cursor_col: Current hardware cursor column
        _root: Root component to render
    """

    def __init__(self, terminal: TerminalProtocol) -> None:
        """Initialize TUI with terminal.

        Args:
            terminal: Terminal instance for I/O
        """
        self.terminal = terminal

        # Differential rendering state
        self._previous_lines: dict[int, str] = {}
        self._max_lines_rendered: int = 0

        # Viewport tracking
        self._viewport_top: int = 0

        # Hardware cursor tracking
        self._hardware_cursor_row: int = 0
        self._hardware_cursor_col: int = 0

        # Component hierarchy
        self._root: Component | None = None

    def add_child(self, component: Component) -> None:
        """Set the root component.

        Args:
            component: Root component to render
        """
        self._root = component

    def invalidate_component(self, component: Component) -> None:
        """Invalidate a component, clearing its rows from the cache.

        This forces the component's rows to be re-rendered in the next frame.

        Args:
            component: The component to invalidate
        """
        # Access _rect attribute which is defined in Component.__init__
        rect: Rect | None = getattr(component, "_rect", None)
        if rect is None:
            return

        # Clear all rows covered by this component's rect
        for row in range(rect.y, rect.y + rect.height):
            self._previous_lines.pop(row, None)

    def on_resize(self, _new_width: int, _new_height: int) -> None:
        """Handle terminal resize event.

        Clears cached line data and resets viewport since all
        positions become invalid after resize.

        Args:
            new_width: New terminal width in columns
            new_height: New terminal height in rows
        """
        # Clear all cached lines - positions are invalid after resize
        self._previous_lines.clear()

        # Reset max lines rendered
        self._max_lines_rendered = 0

        # Reset viewport to top
        self._viewport_top = 0

        # Reset hardware cursor
        self._hardware_cursor_row = 0
        self._hardware_cursor_col = 0

    def _calculate_viewport_top(self, content_height: int) -> int:
        """Calculate viewport scroll position.

        Viewport stays at top (0) until content exceeds terminal height,
        then scrolls to keep bottom of content visible.

        Args:
            content_height: Total content height in lines

        Returns:
            Viewport top position (0 or content_height - term_height)
        """
        # Default terminal height to 24 if not available
        term_height = 24
        return max(0, content_height - term_height)

    def _is_scrollback_edit(
        self, first_changed: int, viewport_top: int
    ) -> bool:
        """Detect if edit is in scrollback (off-screen content).

        Scrollback content is immutable in terminal history. Any edit to
        scrollback requires a full clear+redraw to maintain consistency.

        Args:
            first_changed: Row index of first changed line
            viewport_top: Current viewport top position

        Returns:
            True if edit is in scrollback (requires full redraw)
        """
        return first_changed < viewport_top

    def _find_changed_bounds(
        self, new_lines: list[tuple[int, str]]
    ) -> tuple[int, int]:
        """Find the range of changed lines.

        Args:
            new_lines: List of (row, content_hash) tuples

        Returns:
            Tuple of (first_changed, last_changed) indices
        """
        first_changed = len(new_lines)
        last_changed = -1

        for i, (row, content_hash) in enumerate(new_lines):
            if row not in self._previous_lines:
                # New line
                first_changed = min(first_changed, i)
                last_changed = max(last_changed, i)
            elif self._previous_lines[row] != content_hash:
                # Changed line
                first_changed = min(first_changed, i)
                last_changed = max(last_changed, i)

        # Handle case where nothing changed
        if last_changed == -1:
            return (0, -1)

        return (first_changed, last_changed)

    def _detect_append(
        self,
        new_lines: list[tuple[int, str, str]],
        first_changed: int,
    ) -> bool:
        """Detect if this is a pure append operation.

        Pure append means only new lines are being added at the end,
        with no changes to existing lines.

        Args:
            new_lines: List of (row, content_hash, content) tuples
            first_changed: Index of first changed line from
                _find_changed_bounds

        Returns:
            True if this is a pure append operation
        """
        if first_changed >= len(new_lines):
            return False

        # Must have existing lines to be an append (not initial render)
        if first_changed == 0:
            return False

        # Check that all lines before first_changed are unchanged
        for i in range(first_changed):
            row, content_hash, _ = new_lines[i]
            if row not in self._previous_lines:
                return False
            if self._previous_lines[row] != content_hash:
                return False

        # Check that all lines from first_changed onwards are new
        for i in range(first_changed, len(new_lines)):
            row, _, _ = new_lines[i]
            if row in self._previous_lines:
                return False

        return True

    def _output_diff(
        self, lines: list[tuple[int, str, str]], width: int
    ) -> None:
        """Output only changed lines to terminal.

        Args:
            lines: List of (row, content_hash, content) tuples
            width: Terminal width for line validation
        """
        # Find changed bounds
        first_changed, last_changed = self._find_changed_bounds(
            [(row, hash_val) for row, hash_val, _ in lines]
        )

        # Nothing changed
        if last_changed == -1:
            return

        # Get the actual row of the first changed line
        first_changed_row = lines[first_changed][0]

        # Check if edit is in scrollback (requires full redraw)
        if self._is_scrollback_edit(first_changed_row, self._viewport_top):
            self._output_full_redraw(lines, width)
            return

        # Check if this is a pure append operation
        is_append = self._detect_append(lines, first_changed)

        if is_append:
            # Optimized append path: use \r\n for natural scrolling
            self._output_append(lines, first_changed, last_changed, width)
        else:
            # Standard diff path: cursor positioning for each line
            self._output_standard_diff(
                lines, first_changed, last_changed, width
            )

        # Update max lines rendered
        self._max_lines_rendered = max(
            self._max_lines_rendered, len(lines)
        )

    def _output_full_redraw(
        self, lines: list[tuple[int, str, str]], width: int
    ) -> None:
        """Clear screen and redraw all lines.

        Used when scrollback content is edited, requiring full redraw
        to maintain terminal consistency.

        Args:
            lines: List of (row, content_hash, content) tuples
            width: Terminal width for line validation
        """
        # Clear screen and move cursor to top
        self.terminal.clear_screen()
        self.terminal.move_cursor(0, 0)

        # Redraw all lines
        for row, content_hash, content in lines:
            # Validate line width
            if len(content) > width:
                msg = (
                    f"Line {row} exceeds width {width}: "
                    f"{len(content)} chars"
                )
                raise LineOverflowError(msg)

            # Output line with newline
            self.terminal.write(content + "\r\n")

            # Update tracking
            self._previous_lines[row] = content_hash

        # Update cursor position
        if lines:
            last_row, _, last_content = lines[-1]
            self._hardware_cursor_row = last_row - self._viewport_top
            self._hardware_cursor_col = len(last_content)

    def _output_append(
        self,
        lines: list[tuple[int, str, str]],
        first_changed: int,
        last_changed: int,
        width: int,
    ) -> None:
        """Output appended lines using natural terminal scrolling.

        Uses \r\n to move to next line without cursor positioning,
        leveraging the terminal's natural scroll behavior.

        Args:
            lines: List of (row, content_hash, content) tuples
            first_changed: Index of first new line
            last_changed: Index of last new line
            width: Terminal width for validation
        """
        for i in range(first_changed, last_changed + 1):
            row, content_hash, content = lines[i]

            # Validate line width
            if len(content) > width:
                msg = (
                    f"Line {row} exceeds width {width}: "
                    f"{len(content)} chars"
                )
                raise LineOverflowError(msg)

            # For first appended line, position cursor if needed
            if i == first_changed and first_changed > 0:
                # Move to end of previous line
                prev_row, _, prev_content = lines[i - 1]
                self.terminal.move_cursor(
                    len(prev_content), prev_row - self._viewport_top
                )

            # Use \r\n for natural scrolling (no cursor positioning)
            self.terminal.write("\r\n" + content)

            # Update tracking
            self._previous_lines[row] = content_hash

        # Update cursor position to end of last line
        if last_changed >= 0:
            last_row, _, last_content = lines[last_changed]
            self._hardware_cursor_row = last_row - self._viewport_top
            self._hardware_cursor_col = len(last_content)

    def _output_standard_diff(
        self,
        lines: list[tuple[int, str, str]],
        first_changed: int,
        last_changed: int,
        width: int,
    ) -> None:
        """Output changed lines using cursor positioning.

        Standard differential rendering with explicit cursor movement.

        Args:
            lines: List of (row, content_hash, content) tuples
            first_changed: Index of first changed line
            last_changed: Index of last changed line
            width: Terminal width for validation
        """
        for i in range(first_changed, last_changed + 1):
            row, content_hash, content = lines[i]

            # Skip if unchanged
            if (
                row in self._previous_lines
                and self._previous_lines[row] == content_hash
            ):
                continue

            # Validate line width
            if len(content) > width:
                msg = (
                    f"Line {row} exceeds width {width}: "
                    f"{len(content)} chars"
                )
                raise LineOverflowError(msg)

            # Move cursor and output line
            self.terminal.move_cursor(0, row - self._viewport_top)
            self.terminal.clear_line()
            self.terminal.write(content)

            # Update tracking
            self._previous_lines[row] = content_hash
            self._hardware_cursor_row = row - self._viewport_top
            self._hardware_cursor_col = len(content)


class LineOverflowError(Exception):
    """Raised when a line exceeds terminal width."""

    pass
