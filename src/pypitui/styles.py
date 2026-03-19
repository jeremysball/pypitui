"""Color support detection and style codes."""

import os


def _parse_int_env(name: str, default: int) -> int:
    """Parse integer from environment variable."""
    try:
        return int(os.environ[name])
    except (KeyError, ValueError, TypeError):
        return default


def detect_color_support() -> int:
    """Detect terminal color support level.

    Returns:
        0: No color support (NO_COLOR set)
        1: 16 colors (TERM=color)
        2: 256 colors (TERM=256color)
        3: Truecolor/16M colors (COLORTERM=truecolor or default)

    Priority:
        1. NO_COLOR takes precedence and returns 0
        2. PYPITUI_COLOR overrides all other detection
        3. FORCE_COLOR overrides auto-detection
        4. Auto-detection based on TERM and COLORTERM
    """
    result = 3  # Default to truecolor for modern terminals

    # NO_COLOR takes precedence
    if os.environ.get("NO_COLOR"):
        result = 0
    # PYPITUI_COLOR override
    elif "PYPITUI_COLOR" in os.environ:
        result = _parse_int_env("PYPITUI_COLOR", 3)
    # FORCE_COLOR override
    elif "FORCE_COLOR" in os.environ:
        result = _parse_int_env("FORCE_COLOR", 3)
    else:
        # Auto-detection
        colorterm = os.environ.get("COLORTERM", "").lower()
        term = os.environ.get("TERM", "").lower()

        if colorterm == "truecolor":
            result = 3
        elif "256color" in term:
            result = 2
        elif "color" in term:
            result = 1

    return result
