"""Unit tests for key parsing."""

import pytest


class TestKeyEnum:
    """Tests for Key enum values."""

    def test_key_enum_values(self) -> None:
        """Verify Key.ENTER, Key.ESCAPE, Key.TAB values."""
        from pypitui.keys import Key

        assert Key.ENTER.value == "\r"
        assert Key.ESCAPE.value == "\x1b"
        assert Key.TAB.value == "\t"


class TestMatchesKey:
    """Tests for matches_key function."""

    def test_matches_key_exact_match(self) -> None:
        """matches_key(b'\r', Key.ENTER) is True."""
        from pypitui.keys import Key, matches_key

        assert matches_key(b"\r", Key.ENTER) is True

    def test_matches_key_no_match(self) -> None:
        """matches_key(b'x', Key.ENTER) is False."""
        from pypitui.keys import Key, matches_key

        assert matches_key(b"x", Key.ENTER) is False


class TestParseKey:
    """Tests for parse_key function."""

    def test_parse_key_simple(self) -> None:
        """parse_key(b'q') returns 'q'."""
        from pypitui.keys import parse_key

        result = parse_key(b"q")
        assert result == "q"

    def test_parse_key_control(self) -> None:
        """parse_key(b'\x01') returns Key.ctrl('a')."""
        from pypitui.keys import Key, parse_key

        result = parse_key(b"\x01")
        assert result == Key.ctrl("a")
