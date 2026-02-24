"""Terminal abstraction for TUI applications.

Provides raw terminal mode, input handling, and screen manipulation.
"""

from __future__ import annotations

import select
import sys
import termios
import tty
from abc import ABC, abstractmethod


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

    @abstractmethod
    def enter_alternate_screen(self) -> None:
        """Switch to alternate screen buffer."""
        pass

    @abstractmethod
    def exit_alternate_screen(self) -> None:
        """Return to normal screen buffer."""
        pass


class ProcessTerminal(Terminal):
    """Terminal implementation for actual process stdin/stdout."""

    def __init__(self) -> None:
        self._original_settings: object | None = None
        self._is_raw = False
        self._in_alternate_screen = False
        self._fd = sys.stdin.fileno()

    def write(self, data: str) -> None:
        """Write data to terminal."""
        sys.stdout.write(data)
        sys.stdout.flush()

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

    def read_sequence(self, timeout: float = 0.1) -> str | None:
        """Read a complete input sequence (handles escape sequences).

        Arrow keys and other special keys send multi-byte sequences.
        This reads all available input to get the complete sequence.

        Args:
            timeout: Timeout in seconds for initial read

        Returns:
            Complete input sequence or None
        """
        if not self._is_raw:
            return None

        try:
            import os

            # Use file descriptor directly for both select and read
            # Avoids buffering issues between sys.stdin and stdin.buffer
            fd = self._fd

            # Wait for initial data
            if not select.select([fd], [], [], timeout)[0]:
                return None

            data = b""

            # Read bytes until we have a complete sequence
            while True:
                # If we have a lone ESC, wait briefly for more bytes
                # If nothing comes, it's a standalone escape key
                if len(data) == 1 and data[0] == 0x1B:
                    if not select.select([fd], [], [], 0.05)[0]:
                        # No more data - standalone escape
                        break

                byte = os.read(fd, 1)
                if not byte:
                    break
                data += byte

                # Check if we have a complete sequence
                if len(data) == 1 and data[0] != 0x1B:
                    # Single non-escape char is complete
                    break
                elif len(data) >= 2 and data[0] == 0x1B:
                    # Escape sequence - check if complete
                    # CSI sequences: ESC [ ... final byte (0x40-0x7E)
                    # SS3 sequences: ESC O <one char>
                    if data[1:2] == b"[":
                        # CSI - ends with byte in range 0x40-0x7E
                        if len(data) >= 3 and 0x40 <= data[-1] <= 0x7E:
                            break
                    elif data[1:2] == b"O":
                        # SS3 - ESC O + one char
                        if len(data) >= 3:
                            break
                    elif len(data) == 2:
                        # ESC + single char (meta key)
                        break

            return data.decode("utf-8", errors="replace") if data else None
        except OSError:
            pass
        return None

    def get_size(self) -> tuple[int, int]:
        """Get terminal size as (columns, rows)."""
        import shutil

        try:
            cols, rows = shutil.get_terminal_size()
            return (cols, rows)
        except Exception:
            return (80, 24)

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
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._original_settings)
            self._is_raw = False
        except termios.error:
            pass

    def enter_alternate_screen(self) -> None:
        """Switch to alternate screen buffer."""
        if not self._in_alternate_screen:
            self.write("\x1b[?1049h")
            self._in_alternate_screen = True

    def exit_alternate_screen(self) -> None:
        """Return to normal screen buffer."""
        if self._in_alternate_screen:
            self.write("\x1b[?1049l")
            self._in_alternate_screen = False


class MockTerminal(Terminal):
    """Mock terminal for testing."""

    def __init__(self, cols: int = 80, rows: int = 24) -> None:
        self.cols = cols
        self.rows = rows
        self._buffer: list[str] = []
        self._input_buffer: list[str] = []
        self.cursor_visible = True
        self._in_alternate_screen = False

    def write(self, data: str) -> None:
        """Write data to buffer."""
        self._buffer.append(data)

    def read(self, timeout: float = 0.0) -> str | None:
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

    def enter_alternate_screen(self) -> None:
        """Enter alternate screen."""
        self._in_alternate_screen = True

    def exit_alternate_screen(self) -> None:
        """Exit alternate screen."""
        self._in_alternate_screen = False

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
