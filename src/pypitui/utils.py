"""Utility functions for terminal UI rendering.

Handles ANSI escape codes, text width calculations, and text wrapping.
"""

import re
import shutil
from collections.abc import Callable

# ANSI escape sequence pattern
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

# Grapheme segmenter cache
_segmenter: object | None = None


def get_segmenter() -> object:
    """Get the shared grapheme segmenter instance."""
    global _segmenter
    if _segmenter is None:
        try:
            import unicodedatapkg  # type: ignore

            _segmenter = unicodedatapkg.grapheme_cluster_break
        except ImportError:
            # Fallback to simple iteration
            _segmenter = None
    return _segmenter


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return ANSI_PATTERN.sub("", text)


def visible_width(text: str) -> int:
    """Calculate the visible width of a string in terminal columns.

    Ignores ANSI escape codes and handles wide characters.
    """
    text = strip_ansi(text)
    width = 0
    for char in text:
        # Check for wide characters (CJK, etc.)
        if ord(char) > 127:
            import unicodedata

            cat = unicodedata.category(char)
            # CJK characters are typically 2 columns wide
            if cat.startswith("C") or cat in ("Lo", "Ll", "Lu", "Lt", "Lm"):
                width += 2
            else:
                width += 1
        else:
            width += 1
    return width


def extract_ansi_code(text: str, pos: int) -> tuple[str, int] | None:
    """Extract ANSI escape sequence from text at given position.

    Returns (code, length) or None if no code at position.
    """
    if pos >= len(text) or text[pos] != "\x1b":
        return None

    match = ANSI_PATTERN.match(text[pos:])
    if match:
        return (match.group(), match.end())
    return None


def wrap_text_with_ansi(text: str, width: int) -> list[str]:
    """Wrap text preserving ANSI codes.

    Only does word wrapping - NO padding, NO background colors.
    Returns lines where each line is <= width visible chars.
    Active ANSI codes are preserved across line breaks.
    """
    if not text:
        return [""]

    lines: list[str] = []
    paragraphs = text.split("\n")

    for paragraph in paragraphs:
        if not paragraph:
            lines.append("")
            continue

        words = paragraph.split(" ")
        current_line = ""
        current_width = 0
        active_ansi = ""

        for word in words:
            word_width = visible_width(word)

            if current_width + word_width + (1 if current_line else 0) > width:
                # Line would exceed width, flush current line
                if current_line:
                    lines.append(current_line + "\x1b[0m")  # Reset at end
                # Start new line with active ANSI codes
                current_line = active_ansi + word if active_ansi else word
                current_width = word_width
            else:
                # Add word to current line
                if current_line:
                    current_line += " "
                    current_width += 1
                current_line += word
                current_width += word_width

            # Update active ANSI codes from word
            pos = 0
            while pos < len(word):
                code_info = extract_ansi_code(word, pos)
                if code_info:
                    code, length = code_info
                    if code == "\x1b[0m":
                        active_ansi = ""
                    else:
                        active_ansi += code
                    pos += length
                else:
                    pos += 1

        if current_line:
            lines.append(current_line + "\x1b[0m")

    return lines


def is_whitespace(char: str) -> bool:
    """Check if a character is whitespace."""
    return char in " \t\n\r\f\v"


def is_punctuation(char: str) -> bool:
    """Check if a character is punctuation."""
    import unicodedata

    cat = unicodedata.category(char)
    return cat.startswith("P")


def apply_background_to_line(line: str, width: int, bg_fn: Callable[[str], str]) -> str:
    """Apply background color to a line, padding to full width.

    Args:
        line: Line of text (may contain ANSI codes)
        width: Total width to pad to
        bg_fn: Background color function

    Returns:
        Line with background applied and padded to width
    """
    text_width = visible_width(line)
    if text_width < width:
        padding = " " * (width - text_width)
        return bg_fn(line + padding)
    return bg_fn(line)


def truncate_to_width(text: str, max_width: int, ellipsis: str = "...", pad: bool = False) -> str:
    """Truncate text to fit within a maximum visible width.

    Properly handles ANSI escape codes (they don't count toward width).

    Args:
        text: Text to truncate (may contain ANSI codes)
        max_width: Maximum visible width
        ellipsis: Ellipsis string when truncating (default: "...")
        pad: If True, pad result with spaces to exactly max_width

    Returns:
        Truncated text, optionally padded to exactly max_width
    """
    if max_width <= 0:
        return ""

    visible = visible_width(text)
    if visible <= max_width:
        if pad and visible < max_width:
            return text + " " * (max_width - visible)
        return text

    # Need to truncate
    ellipsis_width = 0 if not ellipsis else visible_width(ellipsis)

    target_width = max_width - ellipsis_width
    if target_width < 0:
        target_width = 0

    result = []
    current_width = 0

    i = 0
    while i < len(text) and current_width < target_width:
        # Check for ANSI code
        code_info = extract_ansi_code(text, i)
        if code_info:
            code, length = code_info
            result.append(code)
            i += length
            continue

        char = text[i]
        char_width = 2 if visible_width(char) > 1 else 1

        if current_width + char_width > target_width:
            break

        result.append(char)
        current_width += char_width
        i += 1

    result.append(ellipsis)

    if pad:
        total_width = current_width + ellipsis_width
        if total_width < max_width:
            result.append(" " * (max_width - total_width))

    return "".join(result)


def slice_by_column(line: str, start_col: int, length: int, strict: bool = False) -> str:
    """Extract a range of visible columns from a line.

    Handles ANSI codes and wide characters.

    Args:
        line: Input line
        start_col: Starting column (0-indexed)
        length: Number of columns to extract
        strict: If True, exclude wide chars at boundary that would extend past range

    Returns:
        Extracted text with ANSI codes preserved
    """
    result = []
    col = 0
    i = 0

    # Skip to start_col
    while i < len(line) and col < start_col:
        code_info = extract_ansi_code(line, i)
        if code_info:
            _, code_len = code_info
            i += code_len
            continue

        char = line[i]
        char_width = visible_width(char)
        col += char_width
        i += 1

    # Include any active ANSI codes at this position
    active_ansi = ""
    temp_i = 0
    while temp_i < i:
        code_info = extract_ansi_code(line, temp_i)
        if code_info:
            code, code_len = code_info
            active_ansi += code
            temp_i += code_len
        else:
            temp_i += 1

    result.append(active_ansi)

    # Extract length columns
    extracted_width = 0
    while i < len(line) and extracted_width < length:
        code_info = extract_ansi_code(line, i)
        if code_info:
            code, code_len = code_info
            result.append(code)
            i += code_len
            continue

        char = line[i]
        char_width = visible_width(char)

        if strict and extracted_width + char_width > length:
            break

        result.append(char)
        extracted_width += char_width
        i += 1

    return "".join(result)


def get_terminal_size() -> tuple[int, int]:
    """Get terminal size as (columns, rows)."""
    try:
        cols, rows = shutil.get_terminal_size()
        return (cols, rows)
    except Exception:
        return (80, 24)
