"""Utility functions for PyPiTUI.

Provides text manipulation utilities with wide character support.
"""

from wcwidth import wcwidth as _wcwidth


def wcwidth(char: str) -> int:
    """Get display width of a character.

    Handles wide characters (emoji, CJK) that occupy 2 columns.

    Args:
        char: Single character to measure

    Returns:
        Display width (0 for combining, 1 for normal, 2 for wide)
    """
    if len(char) != 1:
        msg = f"Expected single character, got {len(char)}"
        raise ValueError(msg)
    result = _wcwidth(char)
    return result if result >= 0 else 0


def truncate_to_width(text: str, width: int) -> str:
    """Truncate text to fit within display width.

    Never splits wide characters. Stops before including a character
    that would exceed the width.

    Args:
        text: Text to truncate
        width: Maximum display width

    Returns:
        Truncated text that fits within width
    """
    if width <= 0:
        return ""

    current_width = 0
    result_chars = []

    for char in text:
        char_width = wcwidth(char)

        # Skip if adding this char would exceed width
        if current_width + char_width > width:
            break

        result_chars.append(char)
        current_width += char_width

    return "".join(result_chars)


def slice_by_width(text: str, start: int, end: int) -> str:
    """Extract substring by display width positions.

    Treats wide characters as atomic units. If a wide character
    would be partially included, it's excluded entirely.

    Args:
        text: Source text
        start: Start display position (inclusive)
        end: End display position (exclusive)

    Returns:
        Substring that fits within the width range
    """
    if start >= end or end <= 0:
        return ""

    current_pos = 0
    result_chars = []
    collecting = False

    for char in text:
        char_width = wcwidth(char)

        # Start collecting when we reach start position
        if not collecting and current_pos >= start:
            collecting = True

        # Stop if we'd exceed end position
        if collecting and current_pos + char_width > end:
            break

        # Collect character if we're in range
        if collecting:
            result_chars.append(char)

        current_pos += char_width

        # Early exit if we've passed end
        if current_pos >= end:
            break

    return "".join(result_chars)
