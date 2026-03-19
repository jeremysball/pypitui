"""Mouse event parsing for terminal input.

Provides MouseEvent dataclass and parse_mouse() for SGR 1006 protocol.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MouseEvent:
    """Mouse event from terminal.

    Coordinates are 0-indexed (screen coordinates).
    """

    button: int
    """Button number or event type:
    - 0-2: Left, Middle, Right button press
    - 3: Release (any button)
    - 32-34: Left, Middle, Right drag
    - 64-65: Scroll wheel up/down
    """

    col: int
    """Column (0-indexed, from left)."""

    row: int
    """Row (0-indexed, from top)."""

    pressed: bool
    """True for press/drag, False for release."""


def parse_mouse(data: bytes) -> MouseEvent | None:
    """Parse SGR 1006 extended mouse sequence.

    SGR format: CSI < Pb ; Px ; Py M/m
    - Pb: button + modifiers
    - Px: column (1-indexed)
    - Py: row (1-indexed)
    - M: press, m: release

    Args:
        data: Raw byte sequence from terminal

    Returns:
        MouseEvent or None if not a valid mouse sequence
    """
    # Check for CSI prefix
    if not data.startswith(b"\x1b["):
        return None

    # Check for SGR marker '<'
    if len(data) < 6 or data[2:3] != b"<":
        return None

    # Parse: <button>;<col>;<row>M or <button>;<col>;<row>m
    try:
        # Skip CSI < (3 bytes) and parse the rest
        content = data[3:].decode("ascii")

        # Should end with M (press) or m (release)
        if not content or content[-1] not in "Mm":
            return None

        pressed = content[-1] == "M"
        params = content[:-1].split(";")

        if len(params) != 3:
            return None

        button = int(params[0])
        # SGR is 1-indexed, we store 0-indexed
        col = int(params[1]) - 1
        row = int(params[2]) - 1

        return MouseEvent(
            button=button,
            col=col,
            row=row,
            pressed=pressed,
        )
    except (ValueError, UnicodeDecodeError):
        return None
