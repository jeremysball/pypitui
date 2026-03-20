"""Input component for text entry.

Provides a single-line text input with cursor support and placeholder text.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import override

from ..component import Component, RenderedLine, Size, StyleSpan
from ..utils import truncate_to_width


@dataclass
class Input(Component):
    """Single-line text input component.

    Attributes:
        placeholder: Text shown when input is empty
        max_length: Maximum character count (0 = unlimited)
        on_submit: Callback invoked with content when Enter pressed
    """

    placeholder: str = ""
    max_length: int = 0
    on_submit: Callable[[str], None] | None = None
    _content: str = field(default="", init=False)
    _cursor_pos: int = field(default=0, init=False)

    @override
    def measure(self, available_width: int, available_height: int) -> Size:
        """Return size for single-line input.

        Input always occupies exactly one line.

        Args:
            available_width: Maximum width available
            available_height: Maximum height available (ignored for Input)

        Returns:
            Size with height=1, width=available_width
        """
        return Size(width=available_width, height=1)

    @override
    def render(self, width: int) -> list[RenderedLine]:
        """Render input content or placeholder.

        Args:
            width: Maximum width for rendering

        Returns:
            Single rendered line with content or placeholder
        """
        if self._content:
            text = truncate_to_width(self._content, width)
            spans = []
        else:
            text = truncate_to_width(self.placeholder, width)
            # Placeholder styling (can be extended with proper styles)
            spans = [StyleSpan(0, len(text))] if text else []

        return [RenderedLine(content=text, styles=spans)]

    def _handle_enter(self) -> bool:
        """Handle Enter key press."""
        if self.on_submit:
            self.on_submit(self._content)
        self._content = ""
        self._cursor_pos = 0
        self.invalidate()
        return True

    def _handle_backspace(self) -> bool:
        """Handle Backspace key press."""
        if self._content:
            self._content = self._content[:-1]
            self._cursor_pos = len(self._content)
            self.invalidate()
        return True

    def _handle_printable(self, data: bytes) -> bool:
        """Handle printable character input."""
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return False

        consumed = False
        for char in text:
            if not char.isprintable():
                break
            if self.max_length > 0 and len(self._content) >= self.max_length:
                break
            self._content += char
            self._cursor_pos = len(self._content)
            consumed = True

        if consumed:
            self.invalidate()
            return True
        return False

    def handle_input(self, data: bytes) -> bool:
        """Handle keyboard input.

        Processes:
        - Printable characters: appended to content
        - Backspace (DEL, \b): removes last character
        - Enter (\r, \n): triggers on_submit callback

        Args:
            data: Raw input bytes from terminal

        Returns:
            True if input was consumed, False otherwise
        """
        if not data:
            return False

        if data in (b"\r", b"\n"):
            return self._handle_enter()

        if data in (b"\x7f", b"\x08"):
            return self._handle_backspace()

        return self._handle_printable(data)

    def get_cursor_position(self) -> tuple[int, int] | None:
        """Get cursor position relative to component origin.

        Returns:
            Tuple of (row, col) where row is always 0 for single-line input,
            or None if component doesn't need cursor
        """
        return (0, self._cursor_pos)
