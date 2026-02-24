"""Keyboard input handling for terminal applications.

Supports both legacy terminal sequences and Kitty keyboard protocol.
See: https://sw.kovidgoyal.net/kitty/keyboard-protocol/
"""

from __future__ import annotations

import re

# Global Kitty protocol state
_kitty_protocol_active: bool = False

# Last key event type for Kitty protocol
_last_key_event_type: str = "press"


def set_kitty_protocol_active(active: bool) -> None:
    """Set the global Kitty keyboard protocol state."""
    global _kitty_protocol_active
    _kitty_protocol_active = active


def is_kitty_protocol_active() -> bool:
    """Query whether Kitty keyboard protocol is currently active."""
    return _kitty_protocol_active


def is_key_release(data: str) -> bool:
    """Check if the last parsed key event was a key release.

    Only meaningful when Kitty keyboard protocol with flag 2 is active.
    """
    return _last_key_event_type == "release"


def is_key_repeat(data: str) -> bool:
    """Check if the last parsed key event was a key repeat.

    Only meaningful when Kitty keyboard protocol with flag 2 is active.
    """
    return _last_key_event_type == "repeat"


# Key type definitions
KeyId = str  # e.g., "ctrl+a", "shift+tab", "escape"


# Key accessor singleton - use Key.escape, Key.ctrl("c"), etc.
class _KeyAccessor:
    """Accessor class for key identifiers with autocomplete support."""

    # Special keys
    escape: KeyId = "escape"
    esc: KeyId = "esc"
    enter: KeyId = "enter"
    return_: KeyId = "return"
    tab: KeyId = "tab"
    space: KeyId = "space"
    backspace: KeyId = "backspace"
    delete: KeyId = "delete"
    insert: KeyId = "insert"
    clear: KeyId = "clear"
    home: KeyId = "home"
    end: KeyId = "end"
    page_up: KeyId = "pageup"
    page_down: KeyId = "pagedown"
    up: KeyId = "up"
    down: KeyId = "down"
    left: KeyId = "left"
    right: KeyId = "right"
    f1: KeyId = "f1"
    f2: KeyId = "f2"
    f3: KeyId = "f3"
    f4: KeyId = "f4"
    f5: KeyId = "f5"
    f6: KeyId = "f6"
    f7: KeyId = "f7"
    f8: KeyId = "f8"
    f9: KeyId = "f9"
    f10: KeyId = "f10"
    f11: KeyId = "f11"
    f12: KeyId = "f12"

    # Symbol keys
    backtick: KeyId = "`"
    hyphen: KeyId = "-"
    equals: KeyId = "="
    left_bracket: KeyId = "["
    right_bracket: KeyId = "]"
    backslash: KeyId = "\\"
    semicolon: KeyId = ";"
    quote: KeyId = "'"
    comma: KeyId = ","
    period: KeyId = "."
    slash: KeyId = "/"
    exclamation: KeyId = "!"
    at: KeyId = "@"
    hash: KeyId = "#"
    dollar: KeyId = "$"
    percent: KeyId = "%"
    caret: KeyId = "^"
    ampersand: KeyId = "&"
    asterisk: KeyId = "*"
    left_paren: KeyId = "("
    right_paren: KeyId = ")"
    underscore: KeyId = "_"
    plus: KeyId = "+"
    pipe: KeyId = "|"
    tilde: KeyId = "~"
    left_brace: KeyId = "{"
    right_brace: KeyId = "}"
    colon: KeyId = ":"
    less_than: KeyId = "<"
    greater_than: KeyId = ">"
    question: KeyId = "?"

    @staticmethod
    def ctrl(key: str) -> KeyId:
        return f"ctrl+{key}"

    @staticmethod
    def shift(key: str) -> KeyId:
        return f"shift+{key}"

    @staticmethod
    def alt(key: str) -> KeyId:
        return f"alt+{key}"

    @staticmethod
    def ctrl_shift(key: str) -> KeyId:
        return f"ctrl+shift+{key}"

    @staticmethod
    def ctrl_alt(key: str) -> KeyId:
        return f"ctrl+alt+{key}"

    @staticmethod
    def shift_alt(key: str) -> KeyId:
        return f"shift+alt+{key}"


Key = _KeyAccessor()


# Legacy terminal escape sequences
LEGACY_SEQUENCES: dict[str, str] = {
    # Arrow keys (CSI)
    "\x1b[A": "up",
    "\x1b[B": "down",
    "\x1b[C": "right",
    "\x1b[D": "left",
    # Arrow keys (SS3 - used in some terminals/app-modes)
    "\x1bOA": "up",
    "\x1bOB": "down",
    "\x1bOC": "right",
    "\x1bOD": "left",
    # Home/End (CSI)
    "\x1b[H": "home",
    "\x1b[F": "end",
    # Home/End (SS3)
    "\x1bOH": "home",
    "\x1bOF": "end",
    # Special keys
    "\x1b[5~": "pageup",
    "\x1b[6~": "pagedown",
    "\x1b[3~": "delete",
    "\x1b[2~": "insert",
    "\x1b[E": "clear",
    # Function keys
    "\x1bOP": "f1",
    "\x1bOQ": "f2",
    "\x1bOR": "f3",
    "\x1bOS": "f4",
    "\x1b[15~": "f5",
    "\x1b[17~": "f6",
    "\x1b[18~": "f7",
    "\x1b[19~": "f8",
    "\x1b[20~": "f9",
    "\x1b[21~": "f10",
    "\x1b[23~": "f11",
    "\x1b[24~": "f12",
    # Double bracket pageUp (some terminals)
    "\x1b[[5~": "pageup",
    # Ctrl+arrow
    "\x1b[1;5A": "ctrl+up",
    "\x1b[1;5B": "ctrl+down",
    "\x1b[1;5C": "ctrl+right",
    "\x1b[1;5D": "ctrl+left",
}

# Control character mapping
CTRL_CHARS: dict[str, str] = {
    "\x00": "ctrl+space",
    "\x01": "ctrl+a",
    "\x02": "ctrl+b",
    "\x03": "ctrl+c",
    "\x04": "ctrl+d",
    "\x05": "ctrl+e",
    "\x06": "ctrl+f",
    "\x07": "ctrl+g",
    "\x08": "ctrl+h",  # backspace
    "\x09": "tab",
    "\x0a": "enter",  # linefeed
    "\x0b": "ctrl+k",
    "\x0c": "ctrl+l",
    "\x0d": "enter",  # carriage return
    "\x0e": "ctrl+n",
    "\x0f": "ctrl+o",
    "\x10": "ctrl+p",
    "\x11": "ctrl+q",
    "\x12": "ctrl+r",
    "\x13": "ctrl+s",
    "\x14": "ctrl+t",
    "\x15": "ctrl+u",
    "\x16": "ctrl+v",
    "\x17": "ctrl+w",
    "\x18": "ctrl+x",
    "\x19": "ctrl+y",
    "\x1a": "ctrl+z",
    "\x1b": "escape",
    "\x1c": "ctrl+\\",
    "\x1d": "ctrl+]",
    "\x1f": "ctrl+-",
    "\x7f": "backspace",
}

# Kitty protocol CSI u pattern
KITTY_CSI_U_PATTERN = re.compile(r"\x1b\[(\d+);?(\d*);?(\d*)(?:;(\d+))?u")

# Kitty key code mapping
KITTY_KEY_CODES: dict[int, str] = {
    13: "return",
    27: "escape",
    9: "tab",
    127: "backspace",
    57350: "f1",
    57351: "f2",
    57352: "f3",
    57353: "f4",
    57354: "f5",
    57355: "f6",
    57356: "f7",
    57357: "f8",
    57358: "f9",
    57359: "f10",
    57360: "f11",
    57361: "f12",
    57399: "up",
    57400: "down",
    57401: "left",
    57402: "right",
    57423: "home",
    57424: "end",
    57425: "pageup",
    57426: "pagedown",
    57427: "insert",
    57428: "delete",
}


def _parse_kitty_csi_u(data: str) -> tuple[str, str] | None:
    """Parse Kitty protocol CSI u sequence.

    Returns (key_id, event_type) or None.
    """
    match = KITTY_CSI_U_PATTERN.match(data)
    if not match:
        return None

    code_str, mods_str, event_type_str, _ = match.groups()
    code = int(code_str)
    mods = int(mods_str) if mods_str else 0
    event_type_num = int(event_type_str) if event_type_str else 1

    # Event types: 1 = press, 2 = repeat, 3 = release
    event_type = {1: "press", 2: "repeat", 3: "release"}.get(event_type_num, "press")

    # Get base key
    if 97 <= code <= 122:  # a-z
        base_key = chr(code)
    elif 65 <= code <= 90:  # A-Z (shifted letters)
        base_key = chr(code).lower()
        mods |= 1  # Add shift modifier
    elif code in KITTY_KEY_CODES:
        base_key = KITTY_KEY_CODES[code]
    else:
        return None

    # Build modifier string
    mod_parts: list[str] = []
    if mods & 4:  # Ctrl
        mod_parts.append("ctrl")
    if mods & 1:  # Shift
        mod_parts.append("shift")
    if mods & 2:  # Alt
        mod_parts.append("alt")

    if mod_parts:
        return (f"{'+'.join(mod_parts)}+{base_key}", event_type)
    return (base_key, event_type)


def parse_key(data: str) -> str | None:
    """Parse input data and return the key identifier if recognized.

    Args:
        data: Raw input data from terminal

    Returns:
        Key identifier string (e.g., "ctrl+c", "escape") or None
    """
    global _last_key_event_type

    if not data:
        return None

    # Try Kitty protocol first if active
    if _kitty_protocol_active:
        kitty_result = _parse_kitty_csi_u(data)
        if kitty_result:
            key_id, event_type = kitty_result
            _last_key_event_type = event_type
            return key_id

    _last_key_event_type = "press"

    # Check legacy escape sequences
    if data in LEGACY_SEQUENCES:
        return LEGACY_SEQUENCES[data]

    # Check control characters
    if data in CTRL_CHARS:
        return CTRL_CHARS[data]

    # Single printable character
    if len(data) == 1 and ord(data[0]) >= 32 and ord(data[0]) < 127:
        return data.lower()

    return None


def matches_key(data: str, key_id: KeyId) -> bool:
    """Match input data against a key identifier string.

    Supported key identifiers:
        - Single keys: "escape", "tab", "enter", "backspace", etc.
        - Arrow keys: "up", "down", "left", "right"
        - Ctrl combinations: "ctrl+c", "ctrl+z", etc.
        - Shift combinations: "shift+tab", "shift+enter"
        - Alt combinations: "alt+enter", "alt+backspace"
        - Combined modifiers: "ctrl+shift+p", "ctrl+alt+x"

    Use the Key helper for autocomplete: Key.ctrl("c"), Key.escape

    Args:
        data: Raw input data from terminal
        key_id: Key identifier (e.g., "ctrl+c", "escape", Key.ctrl("c"))

    Returns:
        True if input matches the key identifier
    """
    parsed = parse_key(data)
    if parsed is None:
        return False

    # Normalize key_id for comparison
    normalized_key_id = key_id.lower().replace("_", "")
    normalized_parsed = parsed.lower().replace("_", "")

    # Handle aliases
    aliases = {
        "esc": "escape",
        "return": "enter",
        "return_": "enter",
        "pageup": "pageup",
        "pagedown": "pagedown",
    }

    normalized_key_id = aliases.get(normalized_key_id, normalized_key_id)
    normalized_parsed = aliases.get(normalized_parsed, normalized_parsed)

    return normalized_parsed == normalized_key_id
