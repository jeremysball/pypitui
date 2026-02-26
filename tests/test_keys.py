"""Tests for keyboard input handling - ported from pi-tui."""

from pypitui.keys import (
    EVENT_PRESS,
    matches_key,
    parse_key,
    set_kitty_protocol_active,
)


class TestMatchesKeyKittyProtocol:
    """Tests for Kitty protocol with alternate keys (non-Latin layouts)."""

    def test_ctrl_c_cyrillic_with_base_layout(self):
        """Match Ctrl+c when pressing Ctrl+С (Cyrillic) with base layout."""  # noqa: RUF002
        set_kitty_protocol_active(True)
        # Cyrillic 'с' = codepoint 1089, Latin 'c' = 99  # noqa: RUF003
        cyrillic_ctrl_c = "\x1b[1089::99;5u"
        assert matches_key(cyrillic_ctrl_c, "ctrl+c") is True
        set_kitty_protocol_active(False)

    def test_ctrl_d_cyrillic_with_base_layout(self):
        """Match Ctrl+d when pressing Ctrl+В (Cyrillic) with base layout."""  # noqa: RUF002
        set_kitty_protocol_active(True)
        # Cyrillic 'в' = codepoint 1074, Latin 'd' = codepoint 100
        cyrillic_ctrl_d = "\x1b[1074::100;5u"
        assert matches_key(cyrillic_ctrl_d, "ctrl+d") is True
        set_kitty_protocol_active(False)

    def test_ctrl_z_cyrillic_with_base_layout(self):
        """Match Ctrl+z when pressing Ctrl+Я (Cyrillic) with base layout."""
        set_kitty_protocol_active(True)
        # Cyrillic 'я' = codepoint 1103, Latin 'z' = codepoint 122
        cyrillic_ctrl_z = "\x1b[1103::122;5u"
        assert matches_key(cyrillic_ctrl_z, "ctrl+z") is True
        set_kitty_protocol_active(False)

    def test_direct_codepoint_without_base_layout(self):
        """Still match direct codepoint when no base layout key."""
        set_kitty_protocol_active(True)
        latin_ctrl_c = "\x1b[99;5u"
        assert matches_key(latin_ctrl_c, "ctrl+c") is True
        set_kitty_protocol_active(False)


class TestMatchesKeyLegacy:
    """Tests for legacy key matching."""

    def test_legacy_ctrl_c(self):
        """Match legacy Ctrl+c (ASCII 3)."""
        set_kitty_protocol_active(False)
        assert matches_key("\x03", "ctrl+c") is True

    def test_legacy_ctrl_d(self):
        """Match legacy Ctrl+d (ASCII 4)."""
        set_kitty_protocol_active(False)
        assert matches_key("\x04", "ctrl+d") is True

    def test_escape_key(self):
        """Match escape key."""
        assert matches_key("\x1b", "escape") is True

    def test_legacy_linefeed_as_enter(self):
        """Match legacy linefeed as enter."""
        set_kitty_protocol_active(False)
        assert matches_key("\n", "enter") is True
        assert parse_key("\n") == ("enter", EVENT_PRESS)

    def test_ctrl_space(self):
        """Parse ctrl+space."""
        set_kitty_protocol_active(False)
        assert matches_key("\x00", "ctrl+space") is True
        assert parse_key("\x00") == ("ctrl+space", EVENT_PRESS)

    def test_arrow_keys(self):
        """Match arrow keys."""
        assert matches_key("\x1b[A", "up") is True
        assert matches_key("\x1b[B", "down") is True
        assert matches_key("\x1b[C", "right") is True
        assert matches_key("\x1b[D", "left") is True

    def test_ss3_arrows_and_home_end(self):
        """Match SS3 arrows and home/end."""
        assert matches_key("\x1bOA", "up") is True
        assert matches_key("\x1bOB", "down") is True
        assert matches_key("\x1bOC", "right") is True
        assert matches_key("\x1bOD", "left") is True
        assert matches_key("\x1bOH", "home") is True
        assert matches_key("\x1bOF", "end") is True

    def test_legacy_function_keys(self):
        """Match legacy function keys."""
        assert matches_key("\x1bOP", "f1") is True
        assert matches_key("\x1b[24~", "f12") is True


class TestParseKeyLegacy:
    """Tests for legacy key parsing."""

    def test_parse_ctrl_letter(self):
        """Parse legacy Ctrl+letter."""
        set_kitty_protocol_active(False)
        assert parse_key("\x03") == ("ctrl+c", EVENT_PRESS)
        assert parse_key("\x04") == ("ctrl+d", EVENT_PRESS)

    def test_parse_special_keys(self):
        """Parse special keys."""
        assert parse_key("\x1b") == ("escape", EVENT_PRESS)
        assert parse_key("\t") == ("tab", EVENT_PRESS)
        assert parse_key("\r") == ("enter", EVENT_PRESS)
        assert parse_key(" ") == ("space", EVENT_PRESS)

    def test_parse_arrow_keys(self):
        """Parse arrow keys."""
        assert parse_key("\x1b[A") == ("up", EVENT_PRESS)
        assert parse_key("\x1b[B") == ("down", EVENT_PRESS)
        assert parse_key("\x1b[C") == ("right", EVENT_PRESS)
        assert parse_key("\x1b[D") == ("left", EVENT_PRESS)

    def test_parse_ss3_keys(self):
        """Parse SS3 arrows and home/end."""
        assert parse_key("\x1bOA") == ("up", EVENT_PRESS)
        assert parse_key("\x1bOB") == ("down", EVENT_PRESS)
        assert parse_key("\x1bOC") == ("right", EVENT_PRESS)
        assert parse_key("\x1bOD") == ("left", EVENT_PRESS)
        assert parse_key("\x1bOH") == ("home", EVENT_PRESS)
        assert parse_key("\x1bOF") == ("end", EVENT_PRESS)

    def test_parse_function_keys(self):
        """Parse legacy function keys."""
        assert parse_key("\x1bOP") == ("f1", EVENT_PRESS)
        assert parse_key("\x1b[24~") == ("f12", EVENT_PRESS)

    def test_parse_single_printable(self):
        """Parse single printable character."""
        assert parse_key("a") == ("a", EVENT_PRESS)
        assert parse_key("Z") == ("z", EVENT_PRESS)  # lowercase

    def test_parse_empty_returns_none(self):
        """Parse empty string returns None."""
        assert parse_key("") == (None, EVENT_PRESS)

    def test_parse_unknown_returns_none(self):
        """Parse unknown sequence returns None."""
        assert parse_key("\x1b[XYZ") == (None, EVENT_PRESS)
