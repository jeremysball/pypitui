"""Text component with wrapping support."""

from typing import override

from pypitui.component import Component, RenderedLine, Size


class Text(Component):
    """Text component with wrapping support.

    Displays text content with automatic line wrapping based on
    available width.
    """

    _text: str

    def __init__(self, text: str = "") -> None:
        """Initialize text component.

        Args:
            text: Initial text content
        """
        super().__init__()
        self._text = text

    def get_text(self) -> str:
        """Get current text content."""
        return self._text

    def set_text(self, text: str) -> None:
        """Set text content.

        Args:
            text: New text content
        """
        self._text = text
        self.invalidate()

    @override
    def measure(
        self, available_width: int, available_height: int
    ) -> Size:
        """Calculate size based on wrapped text lines.

        Args:
            available_width: Maximum width available
            available_height: Maximum height available

        Returns:
            Size (width, height) for text
        """
        if not self._text:
            return Size(0, 0)

        lines = self._text.split("\n")
        # Count wrapped lines
        wrapped_lines = 0
        for line in lines:
            if not line:
                wrapped_lines += 1
            else:
                # Simple wrap: each available_width chars is a line
                numerator = len(line) + available_width - 1
                lines_needed = numerator // available_width
                wrapped_lines += max(1, lines_needed)

        # Width is min of content or available
        max_line_len = max((len(line) for line in lines), default=0)
        width = min(max_line_len, available_width)

        return Size(width, wrapped_lines)

    @override
    def render(self, width: int) -> list[RenderedLine]:
        """Render text with wrapping.

        Args:
            width: Width allocated for rendering

        Returns:
            List of RenderedLine objects
        """
        if not self._text:
            return []

        result: list[RenderedLine] = []
        lines = self._text.split("\n")

        for line in lines:
            if not line:
                result.append(RenderedLine("", []))
            else:
                # Simple wrap at width boundary
                for i in range(0, len(line), width):
                    chunk = line[i : i + width]
                    result.append(RenderedLine(chunk, []))

        return result
