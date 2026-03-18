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
