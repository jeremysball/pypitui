"""TUI components for PyPiTUI.

Ported from @mariozechner/pi-tui's component library.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .keys import Key, matches_key
from .tui import CURSOR_MARKER, Component, Focusable
from .utils import truncate_to_width, visible_width, wrap_text_with_ansi


class Text(Component):
    """Text component - displays multi-line text with word wrapping."""

    def __init__(
        self,
        text: str = "",
        padding_x: int = 1,
        padding_y: int = 1,
        custom_bg_fn: Callable[[str], str] | None = None,
    ) -> None:
        self._text = text
        self._padding_x = padding_x
        self._padding_y = padding_y
        self._custom_bg_fn = custom_bg_fn
        self._cached_text: str | None = None
        self._cached_width: int | None = None
        self._cached_lines: list[str] | None = None

    def set_text(self, text: str) -> None:
        """Update the text content."""
        self._text = text
        self.invalidate()

    def set_custom_bg_fn(self, custom_bg_fn: Callable[[str], str] | None) -> None:
        """Set custom background function."""
        self._custom_bg_fn = custom_bg_fn
        self.invalidate()

    def invalidate(self) -> None:
        """Clear render cache."""
        self._cached_text = None
        self._cached_width = None
        self._cached_lines = None

    def render(self, width: int) -> list[str]:
        """Render text with padding and wrapping."""
        # Check cache
        if (
            self._cached_lines is not None
            and self._cached_width == width
            and self._cached_text == self._text
        ):
            return self._cached_lines

        content_width = max(0, width - self._padding_x * 2)

        if content_width <= 0 or not self._text:
            lines = [""] * (self._padding_y * 2)
        else:
            # Wrap text
            wrapped = wrap_text_with_ansi(self._text, content_width)

            # Add horizontal padding
            lines = []
            for _ in range(self._padding_y):
                lines.append(" " * width)

            for line in wrapped:
                # Strip trailing reset codes from wrap_text_with_ansi
                # They interfere with background color application
                while line.endswith("\x1b[0m"):
                    line = line[:-4]
                visible = visible_width(line)
                padding = " " * self._padding_x
                right_padding = " " * (width - visible - self._padding_x * 2)
                lines.append(padding + line + right_padding)

            for _ in range(self._padding_y):
                lines.append(" " * width)

        # Apply background - ensure full width padding first
        if self._custom_bg_fn:
            bg_lines = []
            for line in lines:
                # Remove trailing reset codes that would clear the background
                # before we apply our background function (wrap_text_with_ansi adds these)
                while line.endswith("\x1b[0m"):
                    line = line[:-4]
                # Pad to full width before applying background
                visible = visible_width(line)
                if visible < width:
                    line += " " * (width - visible)
                bg_lines.append(self._custom_bg_fn(line))
            lines = bg_lines

        # Cache
        self._cached_lines = lines
        self._cached_width = width
        self._cached_text = self._text

        return lines


class Box(Component):
    """Box component - a container that applies padding and background."""

    def __init__(
        self, padding_x: int = 1, padding_y: int = 1, bg_fn: Callable[[str], str] | None = None
    ) -> None:
        self.children: list[Component] = []
        self._padding_x = padding_x
        self._padding_y = padding_y
        self._bg_fn = bg_fn
        self._cache: tuple[int, list[str]] | None = None

    def add_child(self, component: Component) -> None:
        """Add a child component."""
        self.children.append(component)
        self._invalidate_cache()

    def remove_child(self, component: Component) -> None:
        """Remove a child component."""
        if component in self.children:
            self.children.remove(component)
            self._invalidate_cache()

    def clear(self) -> None:
        """Remove all children."""
        self.children.clear()
        self._invalidate_cache()

    def set_bg_fn(self, bg_fn: Callable[[str], str] | None) -> None:
        """Set background function."""
        self._bg_fn = bg_fn
        self._invalidate_cache()

    def _invalidate_cache(self) -> None:
        """Clear render cache."""
        self._cache = None

    def invalidate(self) -> None:
        """Invalidate box and children."""
        self._invalidate_cache()
        for child in self.children:
            child.invalidate()

    def render(self, width: int) -> list[str]:
        """Render box with children."""
        # Check cache
        if self._cache and self._cache[0] == width:
            return self._cache[1]

        content_width = max(0, width - self._padding_x * 2)

        lines: list[str] = []

        # Top padding
        for _ in range(self._padding_y):
            lines.append(self._apply_bg(" " * width, width))

        # Render children
        for child in self.children:
            child_lines = child.render(content_width)
            for line in child_lines:
                padded = " " * self._padding_x + line
                visible = visible_width(padded)
                if visible < width:
                    padded += " " * (width - visible)
                lines.append(self._apply_bg(padded, width))

        # Bottom padding
        for _ in range(self._padding_y):
            lines.append(self._apply_bg(" " * width, width))

        # Cache
        self._cache = (width, lines)

        return lines

    def _apply_bg(self, line: str, width: int) -> str:
        """Apply background to a line."""
        if self._bg_fn:
            # Remove trailing reset codes that would clear the background
            while line.endswith("\x1b[0m"):
                line = line[:-4]
            visible = visible_width(line)
            if visible < width:
                line += " " * (width - visible)
            return self._bg_fn(line)
        return line


class Spacer(Component):
    """Spacer component - empty vertical space."""

    def __init__(self, height: int = 1) -> None:
        self._height = height

    def invalidate(self) -> None:
        """No cache to invalidate."""
        pass

    def render(self, width: int) -> list[str]:
        """Render empty lines."""
        return [""] * self._height


@dataclass
class SelectItem:
    """Item for SelectList."""

    value: str
    label: str
    description: str | None = None


@dataclass
class SelectListTheme:
    """Theme for SelectList."""

    selected_prefix: Callable[[str], str] = lambda s: s
    selected_text: Callable[[str], str] = lambda s: s
    description: Callable[[str], str] = lambda s: s
    scroll_info: Callable[[str], str] = lambda s: s
    no_match: Callable[[str], str] = lambda s: s


class SelectList(Component):
    """Selectable list component."""

    def __init__(self, items: list[SelectItem], max_visible: int, theme: SelectListTheme) -> None:
        self._items = items
        self._filtered_items = list(items)
        self._selected_index = 0
        self._max_visible = max_visible
        self._theme = theme
        self._scroll_offset = 0
        self._filter = ""

        self.on_select: Callable[[SelectItem], None] | None = None
        self.on_cancel: Callable[[], None] | None = None
        self.on_selection_change: Callable[[SelectItem], None] | None = None

    def set_filter(self, filter_text: str) -> None:
        """Set filter text."""
        self._filter = filter_text.lower()
        self._filtered_items = [
            item
            for item in self._items
            if self._filter in item.label.lower()
            or (item.description and self._filter in item.description.lower())
        ]
        self._selected_index = 0
        self._scroll_offset = 0

    def set_selected_index(self, index: int) -> None:
        """Set selected index."""
        if 0 <= index < len(self._filtered_items):
            self._selected_index = index
            self._notify_selection_change()

    def _notify_selection_change(self) -> None:
        """Notify selection change callback."""
        if self.on_selection_change and self._filtered_items:
            self.on_selection_change(self._filtered_items[self._selected_index])

    def get_selected_item(self) -> SelectItem | None:
        """Get currently selected item."""
        if self._filtered_items and 0 <= self._selected_index < len(self._filtered_items):
            return self._filtered_items[self._selected_index]
        return None

    def invalidate(self) -> None:
        """No cache to invalidate."""
        pass

    def render(self, width: int) -> list[str]:
        """Render the select list."""
        lines: list[str] = []

        if not self._filtered_items:
            no_match = self._theme.no_match("No matches")
            lines.append(truncate_to_width(no_match, width))
            return lines

        # Calculate visible range
        total_items = len(self._filtered_items)
        visible_count = min(self._max_visible, total_items)

        # Adjust scroll offset to keep selection visible
        if self._selected_index < self._scroll_offset:
            self._scroll_offset = self._selected_index
        elif self._selected_index >= self._scroll_offset + visible_count:
            self._scroll_offset = self._selected_index - visible_count + 1

        end_offset = min(self._scroll_offset + visible_count, total_items)
        visible_items = self._filtered_items[self._scroll_offset : end_offset]

        for i, item in enumerate(visible_items):
            actual_index = self._scroll_offset + i
            is_selected = actual_index == self._selected_index

            # Build line
            if is_selected:
                prefix = self._theme.selected_prefix("> ")
                label = self._theme.selected_text(item.label)
            else:
                prefix = "  "
                label = item.label

            line = prefix + label

            # Add description if present and there's room
            if item.description and visible_width(line) + 3 < width:
                desc = " - " + item.description
                desc = self._theme.description(desc)
                line += desc

            lines.append(truncate_to_width(line, width))

        # Scroll indicator
        if total_items > visible_count:
            scroll_text = f" {self._scroll_offset + 1}-{end_offset} of {total_items} "
            scroll_line = self._theme.scroll_info(scroll_text)
            lines.append(truncate_to_width(scroll_line, width))

        return lines

    def handle_input(self, data: str) -> None:
        """Handle keyboard input."""
        if matches_key(data, Key.up):
            if self._selected_index > 0:
                self._selected_index -= 1
                self._notify_selection_change()
        elif matches_key(data, Key.down):
            if self._selected_index < len(self._filtered_items) - 1:
                self._selected_index += 1
                self._notify_selection_change()
        elif matches_key(data, Key.enter):
            if self._filtered_items and self.on_select:
                self.on_select(self._filtered_items[self._selected_index])
        elif matches_key(data, Key.escape):
            if self._filter:
                # Clear filter on first escape
                self.set_filter("")
            elif self.on_cancel:
                self.on_cancel()
        elif matches_key(data, Key.backspace):
            # Remove last character from filter
            if self._filter:
                self.set_filter(self._filter[:-1])
        elif len(data) == 1 and ord(data[0]) >= 32:
            # Printable character - add to filter
            self.set_filter(self._filter + data.lower())


class Input(Component, Focusable):
    """Text input component with cursor support."""

    def __init__(self, placeholder: str = "", password: bool = False) -> None:
        self._text = ""
        self._placeholder = placeholder
        self._password = password
        self._cursor_pos = 0
        self._focused = False
        # Callbacks
        self.on_submit: Callable[[str], None] | None = None
        self.on_cancel: Callable[[], None] | None = None

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, value: bool) -> None:
        self._focused = value

    def get_value(self) -> str:
        """Get current input value."""
        return self._text

    def set_value(self, text: str) -> None:
        """Set input value."""
        self._text = text
        self._cursor_pos = len(text)

    def invalidate(self) -> None:
        """No cache."""
        pass

    def render(self, width: int) -> list[str]:
        """Render input with cursor."""
        display_text = self._text if not self._password else "*" * len(self._text)

        if not display_text and not self._focused:
            # Show placeholder
            line = truncate_to_width(self._placeholder, width)
            return [line]

        # Truncate to fit width, keeping cursor visible
        if visible_width(display_text) > width - 2:
            # Need to scroll text to keep cursor visible
            # Simple approach: show end of text
            display_text = truncate_to_width(display_text, width - 2)

        # Build line with cursor
        before_cursor = display_text[: self._cursor_pos]
        at_cursor = display_text[self._cursor_pos : self._cursor_pos + 1] or " "
        after_cursor = display_text[self._cursor_pos + 1 :]

        if self._focused:
            # Use reverse video for cursor
            line = f"> {before_cursor}{CURSOR_MARKER}\x1b[7m{at_cursor}\x1b[27m{after_cursor}"
        else:
            line = f"> {before_cursor}{at_cursor}{after_cursor}"

        return [truncate_to_width(line, width)]

    def handle_input(self, data: str) -> None:
        """Handle keyboard input."""
        if matches_key(data, Key.left):
            if self._cursor_pos > 0:
                self._cursor_pos -= 1
        elif matches_key(data, Key.right):
            if self._cursor_pos < len(self._text):
                self._cursor_pos += 1
        elif matches_key(data, Key.home) or matches_key(data, Key.ctrl("a")):
            self._cursor_pos = 0
        elif matches_key(data, Key.end) or matches_key(data, Key.ctrl("e")):
            self._cursor_pos = len(self._text)
        elif matches_key(data, Key.backspace):
            if self._cursor_pos > 0:
                self._text = self._text[: self._cursor_pos - 1] + self._text[self._cursor_pos :]
                self._cursor_pos -= 1
        elif matches_key(data, Key.delete):
            if self._cursor_pos < len(self._text):
                self._text = self._text[: self._cursor_pos] + self._text[self._cursor_pos + 1 :]
        elif matches_key(data, Key.ctrl("u")):
            # Delete to start of line
            self._text = self._text[self._cursor_pos :]
            self._cursor_pos = 0
        elif matches_key(data, Key.ctrl("k")):
            # Delete to end of line
            self._text = self._text[: self._cursor_pos]
        elif matches_key(data, Key.escape):
            if self.on_cancel:
                self.on_cancel()
        elif matches_key(data, Key.enter):
            if self.on_submit:
                self.on_submit(self._text)
        elif len(data) == 1 and ord(data[0]) >= 32:
            # Printable character
            self._text = self._text[: self._cursor_pos] + data + self._text[self._cursor_pos :]
            self._cursor_pos += 1
