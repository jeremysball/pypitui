"""Mock terminal for testing escape sequence efficiency."""

from io import BytesIO
from types import TracebackType
from typing import Self


class MockTerminal:
    """Mock terminal that counts escape sequences for efficiency testing."""

    _buffer: BytesIO
    _width: int
    _height: int
    _escape_count: int
    _write_count: int

    def __init__(self, width: int = 80, height: int = 24) -> None:
        """Initialize mock terminal.

        Args:
            width: Terminal width in columns
            height: Terminal height in rows
        """
        self._buffer = BytesIO()
        self._width = width
        self._height = height
        self._escape_count = 0
        self._write_count = 0

    def write(self, data: str | bytes) -> None:
        """Write data and count escape sequences."""
        encoded = data.encode() if isinstance(data, str) else data
        self._buffer.write(encoded)
        self._write_count += len(encoded)
        # Count CSI sequences (ESC [)
        text = data if isinstance(data, str) else data.decode()
        self._escape_count += text.count("\x1b[")

    def move_cursor(self, col: int, row: int) -> None:
        """Move cursor - counts as escape sequence."""
        # Use write() to ensure escape counting works
        self.write(f"\x1b[{row + 1};{col + 1}H")

    def clear_line(self) -> None:
        """Clear line - counts as escape sequence."""
        self.write("\x1b[K")

    def clear_screen(self) -> None:
        """Clear screen - counts as escape sequence."""
        self.write("\x1b[2J")

    def hide_cursor(self) -> None:
        """Hide cursor."""
        self._escape_count += 1

    def show_cursor(self) -> None:
        """Show cursor."""
        self._escape_count += 1

    def get_escape_count(self) -> int:
        """Get number of escape sequences emitted."""
        return self._escape_count

    def get_write_count(self) -> int:
        """Get total characters written."""
        return self._write_count

    def reset_counts(self) -> None:
        """Reset counters."""
        self._escape_count = 0
        self._write_count = 0
        self._buffer = BytesIO()

    def get_output(self) -> bytes:
        """Get all output written."""
        return self._buffer.getvalue()

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager."""
        pass
