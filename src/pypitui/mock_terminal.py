"""Mock terminal for testing escape sequence efficiency and input polling."""

from __future__ import annotations

import time
from collections import deque
from io import BytesIO
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from types import TracebackType


class MockTerminal:
    """Mock terminal that counts escape sequences for efficiency testing.

    The compatibility layer used by Alfred's current TUI tests also relies on
    this mock terminal to provide a simple input queue and terminal sizing
    contract.
    """

    _buffer: BytesIO
    _width: int
    _height: int
    _escape_count: int
    _write_count: int
    _input_queue: deque[str]

    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        *,
        cols: int | None = None,
        rows: int | None = None,
    ) -> None:
        """Initialize mock terminal.

        Args:
            width: Terminal width in columns.
            height: Terminal height in rows.
            cols: Compatibility alias for ``width``.
            rows: Compatibility alias for ``height``.
        """
        self._buffer = BytesIO()
        self._width = cols if cols is not None else width
        self._height = rows if rows is not None else height
        self._escape_count = 0
        self._write_count = 0
        self._input_queue = deque()

    def get_size(self) -> tuple[int, int]:
        """Return the configured terminal size."""
        return (self._width, self._height)

    def queue_input(self, data: str | bytes) -> None:
        """Queue input data for polling with ``read_sequence``."""
        text = (
            data.decode("utf-8", errors="ignore")
            if isinstance(data, bytes)
            else data
        )
        self._input_queue.extend(text)

    def read_sequence(self, timeout: float = 0.0) -> str:
        """Poll the next queued input sequence.

        Args:
            timeout: Optional polling timeout in seconds.
        """
        if self._input_queue:
            return self._input_queue.popleft()

        if timeout > 0:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if self._input_queue:
                    return self._input_queue.popleft()
                time.sleep(0.01)

        return ""

    def start(self) -> None:
        """Compatibility no-op for the Alfred TUI adapter."""

    def stop(self) -> None:
        """Compatibility no-op for the Alfred TUI adapter."""

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
        self._input_queue.clear()

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
