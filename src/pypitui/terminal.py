"""Terminal abstraction for TUI applications.

Provides raw terminal mode, input handling, and screen manipulation.
"""

from __future__ import annotations

import os
import select
import shutil
import sys
import termios
import tty
from abc import ABC, abstractmethod
from typing import Any


class Terminal(ABC):
    """Abstract base class for terminal implementations."""

    @abstractmethod
    def write(self, data: str) -> None:
        """Write data to terminal."""
        pass

    @abstractmethod
    def read(self, timeout: float = 0.0) -> str | None:
        """Read a single character from terminal with optional timeout."""
        pass

    @abstractmethod
    def read_sequence(self, timeout: float = 0.1) -> str | None:
        """Read a complete input sequence (handles escape sequences)."""
        pass

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        """Get terminal size as (columns, rows)."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the terminal screen."""
        pass

    @abstractmethod
    def move_cursor(self, row: int, col: int) -> None:
        """Move cursor to position (row, col)."""
        pass

    @abstractmethod
    def hide_cursor(self) -> None:
        """Hide the cursor."""
        pass

    @abstractmethod
    def show_cursor(self) -> None:
        """Show the cursor."""
        pass

    @abstractmethod
    def set_raw_mode(self) -> None:
        """Set terminal to raw mode for character-by-character input."""
        pass

    @abstractmethod
    def restore_mode(self) -> None:
        """Restore terminal to original mode."""
        pass


class ProcessTerminal(Terminal):
    """Terminal implementation for actual process stdin/stdout."""

    def __init__(self) -> None:
        self._original_settings: list[Any] | None = None
        self._is_raw: bool = False
        self._fd: int = sys.stdin.fileno()

    def write(self, data: str) -> None:
        """Write data to terminal."""
        import time
        try:
            with open("/tmp/terminal-debug.log", "a") as f:
                f.write(f"{time.time():.3f}: write {len(data)} bytes\n")
        except:
            pass
        sys.stdout.write(data)
        sys.stdout.flush()
        try:
            with open("/tmp/terminal-debug.log", "a") as f:
                f.write(f"{time.time():.3f}: write done\n")
        except:
            pass

    def read(self, timeout: float = 0.0) -> str | None:
        """Read a single character from terminal with optional timeout."""
        if not self._is_raw:
            return None

        try:
            if select.select([sys.stdin], [], [], timeout)[0]:
                return sys.stdin.read(1)
        except OSError:
            pass
        return None

    def _is_sequence_complete(self, data: bytes) -> bool:
        """Check if we have a complete escape sequence."""
        if len(data) == 1:
            # Single non-escape char is complete
            return data[0] != 0x1B
        if len(data) >= 2 and data[0] == 0x1B:
            # Escape sequence
            if data[1:2] == b"[":
                # CSI - ends with byte in range 0x40-0x7E
                return len(data) >= 3 and 0x40 <= data[-1] <= 0x7E
            if data[1:2] == b"O":
                # SS3 - ESC O + one char
                return len(data) >= 3
            # ESC + single char (meta key)
            return True
        return False

    def _is_lone_escape(self, data: bytes, fd: int) -> bool:
        """Check if we have a standalone escape key."""
        return (
            len(data) == 1
            and data[0] == 0x1B
            and not select.select([fd], [], [], 0.05)[0]
        )

    def read_sequence(self, timeout: float = 0.1) -> str | None:
        """Read a complete input sequence (handles escape sequences).

        Arrow keys and other special keys send multi-byte sequences.
        This reads all available input to get the complete sequence.

        Args:
            timeout: Timeout in seconds for initial read

        Returns:
            Complete input sequence or None
        """
        import time
        start_time = time.time()
        
        if not self._is_raw:
            return None

        try:
            fd = self._fd

            # Wait for initial data
            if not select.select([fd], [], [], timeout)[0]:
                return None

            data = b""
            read_count = 0

            # Read bytes until we have a complete sequence
            while True:
                if self._is_lone_escape(data, fd):
                    break

                byte = os.read(fd, 1)
                read_count += 1
                if not byte:
                    break
                data += byte

                if self._is_sequence_complete(data):
                    break

                elapsed = time.time() - start_time
                if elapsed > timeout * 2:  # Safety limit
                    try:
                        with open("/tmp/terminal-debug.log", "a") as f:
                            f.write(f"{time.time():.3f}: read_sequence timeout, {read_count} bytes, {len(data)} collected\n")
                    except:
                        pass
                    break

            result = data.decode("utf-8", errors="replace") if data else None
            try:
                with open("/tmp/terminal-debug.log", "a") as f:
                    f.write(f"{time.time():.3f}: read_sequence done, {read_count} reads, result={repr(result)}\n")
            except:
                pass
            return result
        except OSError:
            try:
                with open("/tmp/terminal-debug.log", "a") as f:
                    f.write(f"{time.time():.3f}: read_sequence OSError\n")
            except:
                pass
        return None

    def get_size(self) -> tuple[int, int]:
        """Get terminal size as (columns, rows)."""
        try:
            cols, rows = shutil.get_terminal_size()
        except Exception:
            return (80, 24)
        else:
            return (cols, rows)

    def clear(self) -> None:
        """Clear the terminal screen."""
        # Move to home first, then clear - more reliable than clear then move
        # \x1b[H = move cursor to home (1,1)
        # \x1b[2J = erase entire display
        self.write("\x1b[H\x1b[2J")

    def move_cursor(self, row: int, col: int) -> None:
        """Move cursor to position (row, col)."""
        self.write(f"\x1b[{row + 1};{col + 1}H")

    def hide_cursor(self) -> None:
        """Hide the cursor."""
        self.write("\x1b[?25l")

    def show_cursor(self) -> None:
        """Show the cursor."""
        self.write("\x1b[?25h")

    def set_raw_mode(self) -> None:
        """Set terminal to raw mode for character-by-character input."""
        if self._is_raw:
            return

        try:
            self._original_settings = termios.tcgetattr(self._fd)
            tty.setraw(self._fd)
            self._is_raw = True
        except termios.error:
            pass

    def restore_mode(self) -> None:
        """Restore terminal to original mode."""
        if not self._is_raw or self._original_settings is None:
            return

        try:
            termios.tcsetattr(
                self._fd, termios.TCSADRAIN, self._original_settings
            )
            self._is_raw = False
        except termios.error:
            pass


class MockTerminal(Terminal):
    """Mock terminal for testing."""

    def __init__(self, cols: int = 80, rows: int = 24) -> None:
        self.cols: int = cols
        self.rows: int = rows
        self._buffer: list[str] = []
        self._input_buffer: list[str] = []
        self.cursor_visible: bool = True

    def write(self, data: str) -> None:
        """Write data to buffer."""
        self._buffer.append(data)

    def read(self, timeout: float = 0.0) -> str | None:  # noqa: ARG002
        """Read from input buffer."""
        if self._input_buffer:
            return self._input_buffer.pop(0)
        return None

    def read_sequence(self, timeout: float = 0.1) -> str | None:
        """Read a complete sequence from input buffer."""
        # For mock, just return the next item (could be a full sequence)
        return self.read(timeout)

    def get_size(self) -> tuple[int, int]:
        """Get terminal size."""
        return (self.cols, self.rows)

    def clear(self) -> None:
        """Clear screen."""
        self._buffer.append("[CLEAR]")

    def move_cursor(self, row: int, col: int) -> None:
        """Move cursor."""
        pass

    def hide_cursor(self) -> None:
        """Hide cursor."""
        self.cursor_visible = False

    def show_cursor(self) -> None:
        """Show cursor."""
        self.cursor_visible = True

    def set_raw_mode(self) -> None:
        """Set raw mode."""
        pass

    def restore_mode(self) -> None:
        """Restore mode."""
        pass

    def queue_input(self, data: str) -> None:
        """Queue input data for testing."""
        for char in data:
            self._input_buffer.append(char)

    def queue_input_sequence(self, sequence: str) -> None:
        """Queue a complete input sequence for testing."""
        self._input_buffer.append(sequence)

    def get_output(self) -> str:
        """Get all written output."""
        return "".join(self._buffer)

    def clear_buffer(self) -> None:
        """Clear output buffer."""
        self._buffer = []
