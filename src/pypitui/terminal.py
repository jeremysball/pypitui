"""Terminal I/O abstraction with raw mode and threaded input handling."""

import sys
import termios
import tty
from types import TracebackType
from typing import Any, BinaryIO, Self


class Terminal:
    """Terminal abstraction with raw mode context manager.

    Usage:
        with Terminal() as term:
            term.write("Hello")
    """

    def __init__(
        self, fd: int | None = None, buffer: BinaryIO | None = None
    ) -> None:
        """Initialize terminal.

        Args:
            fd: File descriptor (defaults to stdout)
            buffer: Output buffer (defaults to stdout.buffer)
        """
        self._fd: int = fd if fd is not None else sys.stdout.buffer.fileno()
        self._buffer: BinaryIO = (
            buffer if buffer is not None else sys.stdout.buffer
        )
        self._original_attrs: Any | None = None

    def __enter__(self) -> Self:
        """Enter raw mode context.

        Saves current tty attributes and switches to raw mode.
        """
        self._original_attrs = termios.tcgetattr(self._fd)
        tty.setraw(self._fd, termios.TCSANOW)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit raw mode context.

        Restores original tty attributes.
        """
        if self._original_attrs is not None:
            termios.tcsetattr(self._fd, termios.TCSANOW, self._original_attrs)

    def write(self, data: str | bytes) -> None:
        """Write data to terminal.

        Args:
            data: String or bytes to write. Strings are encoded to UTF-8.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        self._buffer.write(data)

    def move_cursor(self, col: int, row: int) -> None:
        """Move cursor to position.

        Args:
            col: Column (0-indexed)
            row: Row (0-indexed)
        """
        # CSI row+1;col+1H - terminals use 1-indexed coordinates
        self.write(f"\x1b[{row + 1};{col + 1}H")

    def clear_line(self) -> None:
        """Clear the current line."""
        self.write("\x1b[2K")  # CSI 2K - clear entire line

    def clear_screen(self) -> None:
        """Clear the screen and scrollback."""
        self.write("\x1b[2J")  # CSI 2J - clear screen
        self.write("\x1b[3J")  # CSI 3J - clear scrollback

    def hide_cursor(self) -> None:
        """Hide the cursor."""
        self.write("\x1b[?25l")  # CSI ?25l - hide cursor

    def show_cursor(self) -> None:
        """Show the cursor."""
        self.write("\x1b[?25h")  # CSI ?25h - show cursor
