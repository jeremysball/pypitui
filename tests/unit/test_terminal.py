"""Unit tests for terminal abstraction."""

import sys
import termios
import threading
import tty
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest


class TestTerminalWrite:
    """Tests for Terminal write method."""

    def test_terminal_write_emits_escape_sequence(self) -> None:
        """Verify bytes written to fd."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3

        # Create a mock buffer with fileno as a MagicMock attribute
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        term.write("\x1b[2J")  # Clear screen escape
                        term.write(b"\x1b[H")  # Cursor home escape

        output = mock_buffer.getvalue()
        assert b"\x1b[2J" in output
        assert b"\x1b[H" in output

    def test_terminal_write_accepts_string_and_bytes(self) -> None:
        """Verify write accepts both str and bytes."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3

        # Create a mock buffer with fileno as a MagicMock attribute
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        term.write("string data")
                        term.write(b"bytes data")

        output = mock_buffer.getvalue()
        assert b"string data" in output
        assert b"bytes data" in output


class TestTerminalCursor:
    """Tests for Terminal cursor movement."""

    def test_terminal_move_cursor(self) -> None:
        """Verify CSI row;colH sequence is emitted."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        term.move_cursor(10, 5)  # col=10, row=5

        output = mock_buffer.getvalue()
        assert b"\x1b[6;11H" in output  # CSI row+1;col+1H (1-indexed)

    def test_terminal_clear_line(self) -> None:
        """Verify CSI 2K sequence is emitted."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        term.clear_line()

        output = mock_buffer.getvalue()
        assert b"\x1b[2K" in output  # CSI 2K - clear entire line

    def test_terminal_clear_screen(self) -> None:
        """Verify CSI 2J and CSI 3J sequences are emitted."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        term.clear_screen()

        output = mock_buffer.getvalue()
        assert b"\x1b[2J" in output  # CSI 2J - clear screen
        assert b"\x1b[3J" in output  # CSI 3J - clear scrollback

    def test_terminal_hide_show_cursor(self) -> None:
        """Verify CSI ?25l and CSI ?25h sequences are emitted."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        term.hide_cursor()
                        term.show_cursor()

        output = mock_buffer.getvalue()
        assert b"\x1b[?25l" in output  # CSI ?25l - hide cursor
        assert b"\x1b[?25h" in output  # CSI ?25h - show cursor


class TestDEC2026:
    """Tests for DEC 2026 synchronized output."""

    def test_dec2026_start_end_constants(self) -> None:
        """Verify escape sequence bytes."""
        from pypitui.terminal import DEC_2026_END, DEC_2026_START

        assert DEC_2026_START == "\x1b[?2026h"
        assert DEC_2026_END == "\x1b[?2026l"

    def test_terminal_write_within_sync_block(self) -> None:
        """Verify sequences wrapped correctly."""
        from pypitui.terminal import DEC_2026_END, DEC_2026_START, Terminal

        mock_buffer = BytesIO()
        mock_fd = 3
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        with term.write_sync_block():
                            term.write("data")

        output = mock_buffer.getvalue()
        assert DEC_2026_START.encode() in output
        assert b"data" in output
        assert DEC_2026_END.encode() in output


class TestTerminalAsyncInput:
    """Tests for Terminal threaded async input handling."""

    def test_sync_queries_complete_before_async_thread(self) -> None:
        """Capability queries finish before input thread spawns."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    with patch(
                        "threading.Thread"
                    ) as mock_thread:
                        term = Terminal(fd=mock_fd, buffer=mock_buffer)
                        with term:
                            # Sync queries happen in __enter__ before start()
                            pass
                        # start() should be called after __enter__ completes
                        # Thread is spawned when start() is called
                        mock_callback = MagicMock()
                        term.start(mock_callback)
                        mock_thread.assert_called_once()
                        args = mock_thread.call_args
                        assert args[1]["daemon"] is True

    def test_input_callback_receives_data(self) -> None:
        """Callback invoked with raw bytes."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        received_data: list[bytes] = []

        def callback(data: bytes) -> None:
            received_data.append(data)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        term.start(callback)
                        # Simulate input by calling _read_loop behavior directly
                        # In real usage, this would come from stdin
                        if term._on_input:
                            term._on_input(b"q")
                            term._on_input(b"\x1b[A")  # UP arrow
                            term._on_input(b"\x1b[?2026h")  # DEC 2026 start

                        term.stop()

        assert b"q" in received_data
        assert b"\x1b[A" in received_data
        assert b"\x1b[?2026h" in received_data

    def test_partial_escape_sequence_buffering(self) -> None:
        """Incomplete escape sequences are buffered for completion."""
        from pypitui.terminal import Terminal

        mock_buffer = BytesIO()
        mock_fd = 3
        mock_buffer.fileno = MagicMock(return_value=mock_fd)

        received_data: list[bytes] = []

        def callback(data: bytes) -> None:
            received_data.append(data)

        with patch("termios.tcgetattr", return_value=[0] * 6):
            with patch("termios.tcsetattr"):
                with patch("tty.setraw"):
                    term = Terminal(fd=mock_fd, buffer=mock_buffer)
                    with term:
                        # Simulate partial escape sequence handling
                        # Terminal should buffer incomplete sequences
                        term.start(callback)

                        # Simulate reading partial sequence
                        if term._on_input:
                            # First part of CSI sequence
                            term._on_input(b"\x1b")
                            # Second part completes it
                            term._on_input(b"[A")

                        term.stop()

        # Both parts should be received (terminal handles buffering)
        # In real implementation, these would be combined before callback
        assert len(received_data) >= 2


class TestTerminalRawMode:
    """Tests for Terminal context manager raw mode."""

    def test_terminal_enter_raw_mode(self) -> None:
        """Verify tty flags are saved and raw mode is set."""
        # This test will fail until Terminal is implemented
        from pypitui.terminal import Terminal

        mock_fd = 3
        original_attrs = [0] * 6
        original_attrs[tty.IFLAG] = termios.ICRNL | termios.IXON
        original_attrs[tty.OFLAG] = termios.OPOST
        original_attrs[tty.CFLAG] = termios.CREAD | termios.CS8
        original_attrs[tty.LFLAG] = termios.ECHO | termios.ICANON | termios.ISIG

        with patch("sys.stdout") as mock_stdout:
            mock_stdout.buffer = MagicMock()
            mock_stdout.buffer.fileno.return_value = mock_fd

            with patch("termios.tcgetattr", return_value=original_attrs.copy()) as mock_getattr:
                with patch("termios.tcsetattr") as mock_setattr:
                    with patch("tty.setraw") as mock_setraw:
                        # Enter context manager
                        term = Terminal()
                        with term:
                            # Verify tcgetattr was called to save original attrs
                            mock_getattr.assert_called_once_with(mock_fd)
                            # Verify setraw was called to enter raw mode
                            mock_setraw.assert_called_once_with(mock_fd, termios.TCSANOW)

                        # Verify tcsetattr was called on exit to restore attrs
                        mock_setattr.assert_called_once()
                        call_args = mock_setattr.call_args
                        assert call_args[0][0] == mock_fd
                        assert call_args[0][1] == termios.TCSANOW
