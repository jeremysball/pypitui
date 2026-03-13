"""Utilities for building bordered boxes in terminal UI."""

from pypitui.utils import visible_width, wrap_text_with_ansi

# Box characters
TOP_LEFT = "┌"
TOP_RIGHT = "┐"
BOTTOM_LEFT = "└"
BOTTOM_RIGHT = "┘"
HORIZONTAL = "─"
VERTICAL = "│"
# Non-breaking space to prevent word-wrapping from splitting border lines
NBSP = "\u00a0"


def build_bordered_box(
    lines: list[str],
    width: int,
    color: str = "",
    title: str | None = None,
    center: bool = True,
) -> list[str]:
    """Build a bordered box with optional title.

    Args:
        lines: Content lines to wrap in box (will be wrapped to fit)
        width: Total box width
        color: ANSI color code (applied to borders)
        title: Optional title for top border
        center: Whether to center content lines

    Returns:
        List of rendered lines with borders
    """
    reset = "\x1b[0m" if color else ""

    # Content width inside borders: │ X + space + content + space + X │
    content_width = max(10, width - 4)

    # Top border - use non-breaking spaces to prevent word-wrapping
    if title:
        # ┌─ title ──────┐  (spaces are non-breaking to prevent wrap)
        title_part = f"─{NBSP}{title}{NBSP}"
        title_visible = visible_width(title) + 3  # ─ + nbsp + title + nbsp
        dashes_after = width - 2 - title_visible
        dashes = "─" * max(1, dashes_after)
        top = f"{color}{TOP_LEFT}{title_part}{dashes}{TOP_RIGHT}{reset}"
    else:
        border = HORIZONTAL * (width - 2)
        top = f"{color}{TOP_LEFT}{border}{TOP_RIGHT}{reset}"

    result = [top]

    # Wrap and pad content lines
    for line in lines:
        # Wrap long lines to content width
        wrapped = wrap_text_with_ansi(line, content_width) if line else [""]

        for wrapped_line in wrapped:
            line_width = visible_width(wrapped_line)
            padded_line = wrapped_line
            if line_width < content_width:
                if center:
                    # Center the text using NBSP to prevent word-wrapping
                    total_padding = content_width - line_width
                    left_pad = total_padding // 2
                    right_pad = total_padding - left_pad
                    padded_line = (
                        NBSP * left_pad + wrapped_line + NBSP * right_pad
                    )
                else:
                    # Left-align: pad with NBSP on right
                    pad_len = content_width - line_width
                    padded_line = wrapped_line + NBSP * pad_len

            # Use NBSP around content to prevent wrap splitting
            content = f"{NBSP}{padded_line}{NBSP}"
            border_left = f"{color}{VERTICAL}{reset}"
            border_right = f"{color}{VERTICAL}{reset}"
            result.append(f"{border_left}{content}{border_right}")

    # Bottom border
    bottom_border = HORIZONTAL * (width - 2)
    bottom = f"{color}{BOTTOM_LEFT}{bottom_border}{BOTTOM_RIGHT}{reset}"
    result.append(bottom)

    return result
