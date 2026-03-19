"""TUI rendering engine with differential output.

Provides the TUI class that manages component rendering,
differential output, viewport tracking, and overlay management.
"""

from pypitui.component import Component
from pypitui.terminal import Terminal


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

    def __init__(self, terminal: Terminal) -> None:
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

        # Output changed lines
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

        # Update max lines rendered
        self._max_lines_rendered = max(
            self._max_lines_rendered, len(lines)
        )


class LineOverflowError(Exception):
    """Raised when a line exceeds terminal width."""

    pass
