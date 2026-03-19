"""Key parsing for terminal input.

Provides Key enum for common keys and functions for parsing key input.
"""

from enum import StrEnum


class Key(StrEnum):
    """Common terminal keys.

    Values are the byte sequences emitted by terminals for special keys,
    or string representations for control keys.
    """

    # Special keys with byte sequences
    ENTER = "\r"
    ESCAPE = "\x1b"
    TAB = "\t"
    BACKSPACE = "\x7f"
    DELETE = "delete"
    UP = "up"
    DOWN = "down"
    RIGHT = "right"
    LEFT = "left"
    HOME = "home"
    END = "end"
    INSERT = "insert"
    PAGE_UP = "page_up"
    PAGE_DOWN = "page_down"

    @classmethod
    def _missing_(cls, value: object) -> "Key":
        """Handle dynamic control key creation."""
        if isinstance(value, str) and value.startswith("ctrl+"):
            # Create dynamic control key member
            obj = str.__new__(cls, value)
            obj._value_ = value
            return obj
        msg = "invalid key"
        raise ValueError(msg)

    @classmethod
    def ctrl(cls, char: str) -> "Key":
        """Create a control key (Ctrl+char).

        Args:
            char: Single lowercase character (a-z)

        Returns:
            Key representing the control combination
        """
        return cls(f"ctrl+{char.lower()}")


# Byte sequence mappings for special keys
_KEY_BYTES: dict[bytes, Key] = {
    b"\r": Key.ENTER,
    b"\x1b": Key.ESCAPE,
    b"\t": Key.TAB,
    b"\x7f": Key.BACKSPACE,
    b"\x1b[3~": Key.DELETE,
    b"\x1b[A": Key.UP,
    b"\x1b[B": Key.DOWN,
    b"\x1b[C": Key.RIGHT,
    b"\x1b[D": Key.LEFT,
    b"\x1b[H": Key.HOME,
    b"\x1b[F": Key.END,
    b"\x1b[2~": Key.INSERT,
    b"\x1b[5~": Key.PAGE_UP,
    b"\x1b[6~": Key.PAGE_DOWN,
}


def matches_key(data: bytes, key: Key) -> bool:
    """Check if data matches a key.

    Args:
        data: Raw byte input from terminal
        key: Key enum value to match against

    Returns:
        True if data exactly matches the key's byte sequence
    """
    result = _KEY_BYTES.get(data)
    return result == key


def parse_key(data: bytes) -> str | Key:
    """Parse raw key input.

    Args:
        data: Raw byte input from terminal

    Returns:
        String character for printable keys, or Key enum for special keys
    """
    # Check for known special keys first
    if data in _KEY_BYTES:
        return _KEY_BYTES[data]

    # Check for control characters (0x01-0x1F, excluding tab, cr, esc)
    if len(data) == 1:
        byte = data[0]
        if 1 <= byte <= 26 and byte not in (9, 13, 27):
            # Ctrl+A through Ctrl+Z (excluding tab, enter, escape)
            char = chr(byte + ord("a") - 1)
            return Key.ctrl(char)

        # Printable ASCII
        if 32 <= byte <= 126:
            return chr(byte)

    # Unknown sequence, return as repr
    return repr(data)
