#!/usr/bin/env python3
"""Test key parsing without raw mode.

Usage:
    uv run python examples/test_keys.py
"""

import sys

sys.path.insert(0, "src")

from pypitui.keys import Key, matches_key, parse_key


def main() -> None:
    """Show key parsing results."""
    print("Key Parsing Test")
    print("=" * 40)
    print()

    # Test data samples
    test_inputs = [
        (b"q", "simple character"),
        (b"\r", "ENTER key"),
        (b"\x1b", "ESCAPE key"),
        (b"\t", "TAB key"),
        (b"\x7f", "BACKSPACE key"),
        (b"\x01", "Ctrl+A"),
        (b"\x1b[A", "UP arrow"),
        (b"\x1b[B", "DOWN arrow"),
        (b"\x1b[C", "RIGHT arrow"),
        (b"\x1b[D", "LEFT arrow"),
        (b"\x1b[3~", "DELETE key"),
        (b"xyz", "unknown sequence"),
    ]

    print("Parsing key sequences:")
    print()

    for data, description in test_inputs:
        result = parse_key(data)
        if isinstance(result, Key):
            print(f"  {description:20} -> Key.{result.name}")
        else:
            print(f"  {description:20} -> {result!r}")

    print()
    print("Testing matches_key():")
    print(f"  matches_key(b'\\r', Key.ENTER) = {matches_key(b'\r', Key.ENTER)}")
    print(f"  matches_key(b'x', Key.ENTER)   = {matches_key(b'x', Key.ENTER)}")

    print()
    print("Test complete!")


if __name__ == "__main__":
    main()
