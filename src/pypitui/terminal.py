"""Terminal I/O abstraction with raw mode and threaded input handling."""

import os
import selectors
import sys
import termios
import threading
import tty
from collections.abc import Callable, Generator
from contextlib import contextmanager
from types import TracebackType
from typing import Any, BinaryIO, Self

# DEC 2026 synchronized output sequences
DEC_2026_START = "\x1b[?2026h"
DEC_2026_END = "\x1b[?2026l"


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
        self._on_input: Callable[[bytes], None] | None = None
        self._running: bool = False
        self._input_thread: threading.Thread | None = None

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

    @contextmanager
    def write_sync_block(self) -> Generator[None, None, None]:
        """Context manager for DEC 2026 synchronized output.

        Wraps output in DEC 2026 start/end sequences for atomic updates.

        Usage:
            with term.write_sync_block():
                term.write("data")
        """
        self.write(DEC_2026_START)
        try:
            yield
        finally:
            self.write(DEC_2026_END)

    def start(
        self, on_input: Callable[[bytes], None] | None = None
    ) -> None:
        """Start async input handling.

        Spawns a daemon thread to read input and dispatch to callback.
        Must be called after entering raw mode context.

        Args:
            on_input: Callback for input data
        """
        self._on_input = on_input
        self._running = True
        self._input_thread = threading.Thread(
            target=self._read_loop, daemon=True
        )
        self._input_thread.start()

    def stop(self) -> None:
        """Stop async input handling.

        Signals the input thread to exit and waits for it to finish.
        """
        self._running = False
        if self._input_thread is not None and self._input_thread.is_alive():
            self._input_thread.join(timeout=0.1)

    def _read_loop(self) -> None:
        """Main loop for async input reading.

        Reads from stdin and dispatches to callback.
        Runs in daemon thread.
        """
        # Use stdin for input (file descriptor 0)
        stdin_fd = 0
        sel = selectors.DefaultSelector()
        sel.register(stdin_fd, selectors.EVENT_READ)

        while self._running:
            events = sel.select(timeout=0.05)  # 50ms timeout
            for _ in events:
                try:
                    data = os.read(stdin_fd, 1024)
                    if data and self._on_input:
                        self._on_input(data)
                except OSError:
                    break
            if not self._running:
                break

        sel.close()
