"""Unit tests for terminal abstraction."""

import termios
import tty
from unittest.mock import MagicMock, patch

import pytest


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
