"""SelectList component for item selection.

Provides a scrollable list of items with keyboard navigation.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import override

from ..component import Component, RenderedLine, Size, StyleSpan
from ..utils import truncate_to_width


@dataclass(frozen=True)
class SelectItem:
    """An item in a SelectList.

    Attributes:
        id: Unique identifier for the item
        label: Display text for the item
    """

    id: str
    label: str


@dataclass
class SelectList(Component):
    """Scrollable list with keyboard navigation.

    Attributes:
        items: List of SelectItem objects to display
        max_visible: Maximum number of items visible at once
        on_select: Callback invoked with item id when Enter pressed
    """

    items: list[SelectItem]
    max_visible: int
    on_select: Callable[[str], None] | None = None
    _selected_index: int = field(default=0, init=False)

    @override
    def measure(self, available_width: int, available_height: int) -> Size:
        """Return size for the list.

        Height is limited by both item count and max_visible.

        Args:
            available_width: Maximum width available
            available_height: Maximum height available (not used)

        Returns:
            Size with height=min(len(items), max_visible)
        """
        height = min(len(self.items), self.max_visible)
        return Size(width=available_width, height=height)

    @override
    def render(self, width: int) -> list[RenderedLine]:
        """Render visible items with selection highlighting.

        Args:
            width: Maximum width for rendering

        Returns:
            List of rendered lines for visible items
        """
        lines = []
        visible_count = min(len(self.items), self.max_visible)

        for i in range(visible_count):
            item = self.items[i]
            label = truncate_to_width(item.label, width)

            if i == self._selected_index:
                # Highlight selected item with full-width style span
                style = StyleSpan(start=0, end=len(label), bold=True)
                lines.append(RenderedLine(content=label, styles=[style]))
            else:
                lines.append(RenderedLine(content=label, styles=[]))

        return lines

    def _move_selection(self, delta: int) -> None:
        """Move selection by delta, wrapping around."""
        if not self.items:
            return

        self._selected_index = (self._selected_index + delta) % len(self.items)
        self.invalidate()

    def _handle_enter(self) -> bool:
        """Handle Enter key press."""
        if self.on_select and self.items:
            self.on_select(self.items[self._selected_index].id)
        return True

    def handle_input(self, data: bytes) -> bool:
        """Handle keyboard input for navigation.

        Processes:
        - Up arrow: move selection up
        - Down arrow: move selection down
        - Enter: trigger on_select callback

        Args:
            data: Raw input bytes from terminal

        Returns:
            True if input was consumed, False otherwise
        """
        if not data:
            return False

        # Handle Enter
        if data in (b"\r", b"\n"):
            return self._handle_enter()

        # Handle CSI sequences (arrow keys)
        if data.startswith(b"\x1b["):
            seq = data[2:]  # Remove CSI prefix

            if seq == b"A":  # Up
                self._move_selection(-1)
                return True

            if seq == b"B":  # Down
                self._move_selection(1)
                return True

        return False
