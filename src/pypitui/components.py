"""TUI components for PyPiTUI.

Ported from @mariozechner/pi-tui's component library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .keys import Key, matches_key
from .tui import CURSOR_MARKER, Component, Focusable
from .utils import truncate_to_width, visible_width, wrap_text_with_ansi

if TYPE_CHECKING:
    from collections.abc import Callable

# Constants
_RICH_REQUIRED_MSG = (
    "This feature requires 'rich' package. "
    "Install with: pip install pypitui[rich]"
)

# ANSI escape codes
ANSI_RESET = "\x1b[0m"
ANSI_RESET_LEN = len(ANSI_RESET)  # 4 bytes


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

    def set_custom_bg_fn(
        self, custom_bg_fn: Callable[[str], str] | None
    ) -> None:
        """Set custom background function."""
        self._custom_bg_fn = custom_bg_fn
        self.invalidate()

    def invalidate(self) -> None:
        """Clear render cache."""
        self._cached_text = None
        self._cached_width = None
        self._cached_lines = None

    def _strip_trailing_reset(self, line: str) -> str:
        """Strip trailing ANSI reset codes from a line."""
        while line.endswith(ANSI_RESET):
            line = line[:-ANSI_RESET_LEN]
        return line

    def _apply_background(self, lines: list[str], width: int) -> list[str]:
        """Apply custom background function to all lines."""
        if not self._custom_bg_fn:
            return lines
        bg_lines = []
        for line in lines:
            current = self._strip_trailing_reset(line)
            visible = visible_width(current)
            if visible < width:
                current += " " * (width - visible)
            bg_lines.append(self._custom_bg_fn(current))
        return bg_lines

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
            lines.extend([" " * width for _ in range(self._padding_y)])

            for line in wrapped:
                current = self._strip_trailing_reset(line)
                visible = visible_width(current)
                padding = " " * self._padding_x
                right_padding = " " * (width - visible - self._padding_x * 2)
                lines.append(padding + current + right_padding)

            lines.extend([" " * width for _ in range(self._padding_y)])

        # Apply background
        lines = self._apply_background(lines, width)

        # Cache
        self._cached_lines = lines
        self._cached_width = width
        self._cached_text = self._text

        return lines


class Box(Component):
    """Box component - a container that applies padding and background."""

    def __init__(
        self,
        padding_x: int = 1,
        padding_y: int = 1,
        bg_fn: Callable[[str], str] | None = None,
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
        lines.extend(
            self._apply_bg(" " * width, width) for _ in range(self._padding_y)
        )

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
        lines.extend(
            self._apply_bg(" " * width, width) for _ in range(self._padding_y)
        )

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


class BorderedBox(Component):
    """A box with borders that intelligently wraps content to fit inside.

    Unlike Box which just adds padding, BorderedBox draws borders and
    wraps content to fit within the content area, maintaining the box shape.
    """

    # Box drawing characters
    TOP_LEFT = "┌"
    TOP_RIGHT = "┐"
    BOTTOM_LEFT = "└"
    BOTTOM_RIGHT = "┘"
    HORIZONTAL = "─"
    VERTICAL = "│"
    T_LEFT = "├"
    T_RIGHT = "┤"

    def __init__(
        self,
        padding_x: int = 1,
        padding_y: int = 0,
        min_width: int = 10,
        max_width: int | None = None,
        title: str | None = None,
    ) -> None:
        """Initialize bordered box.

        Args:
            padding_x: Horizontal padding inside the box (default 1)
            padding_y: Vertical padding inside the box (default 0)
            min_width: Minimum width for the box (default 10)
            max_width: Maximum width for the box (default None =
                use render width)
            title: Optional title to display in the top border
        """
        self.children: list[Component] = []
        self._padding_x = padding_x
        self._padding_y = padding_y
        self._min_width = min_width
        self._max_width = max_width
        self._title = title
        self._cache: tuple[int, list[str]] | None = None

    def set_title(self, title: str) -> None:
        """Set the box title.

        Args:
            title: Plain text or ANSI-escaped string
        """
        self._title = title
        self._invalidate_cache()

    def set_rich_title(self, markup: str) -> None:
        """Set the box title using Rich markup.

        Requires the 'rich' extra: pip install pypitui[rich]

        Args:
            markup: Rich markup string (e.g., "[bold cyan]Title[/bold cyan]")

        Example:
            box = BorderedBox()
            box.set_rich_title("[bold cyan]My Panel[/bold cyan]")
        """
        try:
            from .rich_components import rich_to_ansi  # noqa: PLC0415

            self._title = rich_to_ansi(markup)
            self._invalidate_cache()
        except ImportError as e:
            raise ImportError(_RICH_REQUIRED_MSG) from e

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

    def _invalidate_cache(self) -> None:
        """Clear render cache."""
        self._cache = None

    def invalidate(self) -> None:
        """Invalidate box and children."""
        self._invalidate_cache()
        for child in self.children:
            child.invalidate()

    def render(self, width: int) -> list[str]:
        """Render bordered box with wrapped content.

        The box will use the requested width if possible, but content
        will be wrapped to fit within the borders.
        """
        # Check cache
        if self._cache and self._cache[0] == width:
            return self._cache[1]

        # Apply max_width constraint if set
        if self._max_width is not None:
            width = min(width, self._max_width)

        # Ensure minimum width
        width = max(width, self._min_width)

        # Calculate content width (inside borders and padding)
        # width = border (1) + padding + content + padding + border (1)
        content_width = max(1, width - 2 - self._padding_x * 2)

        # Build content lines from children
        content_lines: list[str] = []
        for child in self.children:
            child_lines = child.render(content_width)
            content_lines.extend(child_lines)

        # Build the box
        lines: list[str] = []

        # Top border
        top_border = (
            self.TOP_LEFT + self.HORIZONTAL * (width - 2) + self.TOP_RIGHT
        )
        lines.append(top_border)

        # Top padding (if any)
        lines.extend(
            self.VERTICAL + " " * (width - 2) + self.VERTICAL
            for _ in range(self._padding_y)
        )

        # Title (if provided) - appears as first content line
        # with separator after
        if self._title:
            # Title line with padding
            title_padded = (
                " " * self._padding_x + self._title + " " * self._padding_x
            )
            inner_width = width - 2
            if visible_width(title_padded) < inner_width:
                title_padded += " " * (
                    inner_width - visible_width(title_padded)
                )
            lines.append(self.VERTICAL + title_padded + self.VERTICAL)

            # Separator line (├─┤)
            sep_inner = self.HORIZONTAL * (width - 2)
            lines.append(self.T_LEFT + sep_inner + self.T_RIGHT)

        # Content lines with wrapping and padding
        for line in content_lines:
            # Wrap line to fit content width
            wrapped = self._wrap_line(line, content_width)
            for wrapped_line in wrapped:
                # Add horizontal padding
                padded_content = (
                    " " * self._padding_x
                    + wrapped_line
                    + " " * self._padding_x
                )
                # Pad to full inner width
                inner_width = width - 2
                if visible_width(padded_content) < inner_width:
                    padded_content += " " * (
                        inner_width - visible_width(padded_content)
                    )
                lines.append(self.VERTICAL + padded_content + self.VERTICAL)

        # Bottom padding (if any)
        lines.extend(
            self.VERTICAL + " " * (width - 2) + self.VERTICAL
            for _ in range(self._padding_y)
        )

        # Bottom border
        bottom_border = (
            self.BOTTOM_LEFT
            + self.HORIZONTAL * (width - 2)
            + self.BOTTOM_RIGHT
        )
        lines.append(bottom_border)

        # Cache
        self._cache = (width, lines)

        return lines

    def _wrap_line(self, line: str, max_width: int) -> list[str]:
        """Wrap a line to fit within max_width visible characters.

        Unlike wrap_text_with_ansi, this preserves the line structure
        and doesn't add reset codes at the end.
        """
        if not line:
            return [""]

        visible = visible_width(line)
        if visible <= max_width:
            return [line]

        # Need to wrap - use word wrapping
        words = line.split(" ")
        result: list[str] = []
        current_line = ""
        current_width = 0

        for word in words:
            word_visible = visible_width(word)

            # Check if word alone exceeds max_width
            if word_visible > max_width:
                # Flush current line if any
                if current_line:
                    result.append(current_line)
                    current_line = ""
                    current_width = 0
                # Truncate the long word
                result.append(truncate_to_width(word, max_width, pad=False))
                continue

            # Check if adding this word would exceed width
            space_needed = 1 if current_line else 0
            if current_width + space_needed + word_visible > max_width:
                # Flush current line
                result.append(current_line)
                current_line = word
                current_width = word_visible
            else:
                # Add word to current line
                if current_line:
                    current_line += " "
                    current_width += 1
                current_line += word
                current_width += word_visible

        # Don't forget the last line
        if current_line:
            result.append(current_line)

        return result if result else [""]


class Spacer(Component):
    """Spacer component - empty vertical space."""

    def __init__(self, height: int = 1) -> None:
        self._height = height

    def invalidate(self) -> None:
        """No cache to invalidate."""
        pass

    def render(self, _width: int) -> list[str]:
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

    def __init__(
        self, items: list[SelectItem], max_visible: int, theme: SelectListTheme
    ) -> None:
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
            self.on_selection_change(
                self._filtered_items[self._selected_index]
            )

    def get_selected_item(self) -> SelectItem | None:
        """Get currently selected item."""
        if self._filtered_items and 0 <= self._selected_index < len(
            self._filtered_items
        ):
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
                # Normalize newlines to spaces
                normalized_desc = item.description.replace("\n", " ")
                desc = " - " + normalized_desc
                desc = self._theme.description(desc)
                line += desc

            lines.append(truncate_to_width(line, width))

        # Scroll indicator
        if total_items > visible_count:
            scroll_text = (
                f" {self._scroll_offset + 1}-{end_offset} of {total_items} "
            )
            scroll_line = self._theme.scroll_info(scroll_text)
            lines.append(truncate_to_width(scroll_line, width))

        return lines

    def _handle_up(self) -> bool:
        """Handle up arrow key."""
        if self._selected_index > 0:
            self._selected_index -= 1
        else:
            self._selected_index = len(self._filtered_items) - 1
        self._notify_selection_change()
        return True

    def _handle_down(self) -> bool:
        """Handle down arrow key."""
        if self._selected_index < len(self._filtered_items) - 1:
            self._selected_index += 1
        else:
            self._selected_index = 0
        self._notify_selection_change()
        return True

    def _handle_enter(self) -> bool:
        """Handle enter key."""
        if self._filtered_items and self.on_select:
            self.on_select(self._filtered_items[self._selected_index])
        return True

    def _handle_escape(self) -> bool:
        """Handle escape key."""
        if self._filter:
            self.set_filter("")
        elif self.on_cancel:
            self.on_cancel()
        return True

    def _handle_backspace(self) -> bool:
        """Handle backspace key."""
        if self._filter:
            self.set_filter(self._filter[:-1])
        return True

    def _handle_char(self, char: str) -> bool:
        """Handle printable character."""
        self.set_filter(self._filter + char.lower())
        return True

    def handle_input(self, data: str) -> None:
        """Handle keyboard input."""
        if matches_key(data, Key.up):
            self._handle_up()
        elif matches_key(data, Key.down):
            self._handle_down()
        elif matches_key(data, Key.enter):
            self._handle_enter()
        elif matches_key(data, Key.escape):
            self._handle_escape()
        elif matches_key(data, Key.backspace):
            self._handle_backspace()
        elif len(data) == 1 and ord(data[0]) >= 32:
            self._handle_char(data)


class Input(Component, Focusable):
    """Text input component with cursor support."""

    def __init__(
        self,
        placeholder: str = "",
        password: bool = False,
        max_length: int | None = None,
    ) -> None:
        self._text = ""
        self._placeholder = placeholder
        self._password = password
        self._max_length = max_length
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
        display_text = (
            self._text if not self._password else "*" * len(self._text)
        )

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
        at_cursor = (
            display_text[self._cursor_pos : self._cursor_pos + 1] or " "
        )
        after_cursor = display_text[self._cursor_pos + 1 :]

        if self._focused:
            # Use reverse video for cursor
            # Use reverse video for cursor
            line = (
                f"{before_cursor}{CURSOR_MARKER}"
                f"\x1b[7m{at_cursor}\x1b[27m{after_cursor}"
            )
        else:
            line = f"{before_cursor}{at_cursor}{after_cursor}"

        return [truncate_to_width(line, width)]

    def _move_cursor_left(self) -> None:
        """Move cursor left."""
        if self._cursor_pos > 0:
            self._cursor_pos -= 1

    def _move_cursor_right(self) -> None:
        """Move cursor right."""
        if self._cursor_pos < len(self._text):
            self._cursor_pos += 1

    def _delete_before_cursor(self) -> None:
        """Delete character before cursor (backspace)."""
        if self._cursor_pos > 0:
            self._text = (
                self._text[: self._cursor_pos - 1]
                + self._text[self._cursor_pos :]
            )
            self._cursor_pos -= 1

    def _delete_at_cursor(self) -> None:
        """Delete character at cursor (delete key)."""
        if self._cursor_pos < len(self._text):
            self._text = (
                self._text[: self._cursor_pos]
                + self._text[self._cursor_pos + 1 :]
            )

    def _delete_to_start(self) -> None:
        """Delete from cursor to start of line."""
        self._text = self._text[self._cursor_pos :]
        self._cursor_pos = 0

    def _delete_to_end(self) -> None:
        """Delete from cursor to end of line."""
        self._text = self._text[: self._cursor_pos]

    def _insert_char(self, char: str) -> None:
        """Insert character at cursor position."""
        # Check max length constraint
        if self._max_length and len(self._text) >= self._max_length:
            return
        self._text = (
            self._text[: self._cursor_pos]
            + char
            + self._text[self._cursor_pos :]
        )
        self._cursor_pos += 1

    def _handle_cursor_movement(self, data: str) -> bool:
        """Handle cursor movement keys. Returns True if handled."""
        if matches_key(data, Key.left):
            self._move_cursor_left()
        elif matches_key(data, Key.right):
            self._move_cursor_right()
        elif matches_key(data, Key.home) or matches_key(data, Key.ctrl("a")):
            self._cursor_pos = 0
        elif matches_key(data, Key.end) or matches_key(data, Key.ctrl("e")):
            self._cursor_pos = len(self._text)
        else:
            return False
        return True

    def _handle_deletion(self, data: str) -> bool:
        """Handle deletion keys. Returns True if handled."""
        if matches_key(data, Key.backspace):
            self._delete_before_cursor()
        elif matches_key(data, Key.delete):
            self._delete_at_cursor()
        elif matches_key(data, Key.ctrl("u")):
            self._delete_to_start()
        elif matches_key(data, Key.ctrl("k")):
            self._delete_to_end()
        else:
            return False
        return True

    def _handle_action(self, data: str) -> bool:
        """Handle action keys (escape, enter). Returns True if handled."""
        if matches_key(data, Key.escape):
            if self.on_cancel:
                self.on_cancel()
        elif matches_key(data, Key.enter):
            if self.on_submit:
                self.on_submit(self._text)
        else:
            return False
        return True

    def handle_input(self, data: str) -> None:
        """Handle keyboard input."""
        if self._handle_cursor_movement(data):
            return
        if self._handle_deletion(data):
            return
        if self._handle_action(data):
            return
        if len(data) == 1 and ord(data[0]) >= 32:
            self._insert_char(data)
