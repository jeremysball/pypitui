#!/usr/bin/env python3
"""Test color detection without entering raw mode.

Usage:
    uv run python examples/test_colors.py
"""

import os
import sys

sys.path.insert(0, "src")

from pypitui.styles import detect_color_support


def main() -> None:
    """Show color detection results."""
    print("Color Support Detection Test")
    print("=" * 40)
    print()

    # Show current environment
    print("Environment variables:")
    for var in ["NO_COLOR", "FORCE_COLOR", "COLORTERM", "TERM", "PYPITUI_COLOR"]:
        value = os.environ.get(var)
        if value:
            print(f"  {var}={value}")
        else:
            print(f"  {var} (not set)")

    print()

    # Detect color support
    level = detect_color_support()
    labels = {0: "no color", 1: "16 colors", 2: "256 colors", 3: "truecolor (16M)"}

    print(f"Detected color support: {level} ({labels.get(level, 'unknown')})")
    print()

    # Test override
    print("Testing PYPITUI_COLOR override:")
    for test_level in [0, 1, 2, 3]:
        os.environ["PYPITUI_COLOR"] = str(test_level)
        result = detect_color_support()
        print(f"  PYPITUI_COLOR={test_level} -> {result}")

    # Cleanup
    del os.environ["PYPITUI_COLOR"]
    print()
    print("Test complete!")


if __name__ == "__main__":
    main()
