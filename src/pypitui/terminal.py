"""Terminal I/O abstraction with raw mode and threaded input handling."""

import sys
import termios
import tty
from types import TracebackType
from typing import Any, Self


class Terminal:
    """Terminal abstraction with raw mode context manager.

    Usage:
        with Terminal() as term:
            term.write("Hello")
    """

    def __init__(self, fd: int | None = None) -> None:
        """Initialize terminal.

        Args:
            fd: File descriptor (defaults to stdout)
        """
        self._fd: int = fd if fd is not None else sys.stdout.buffer.fileno()
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
