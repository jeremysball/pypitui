#!/usr/bin/env python3
"""Test script using pypitui to verify arrow keys work."""

from pypitui import ProcessTerminal, matches_key, Key


def main():
    print("Testing pypitui arrow key handling")
    print("Press arrow keys (press 'q' to quit):")
    print("-" * 40)

    terminal = ProcessTerminal()
    running = True

    terminal.set_raw_mode()

    try:
        while running:
            data = terminal.read_sequence(timeout=0.1)
            if data:
                # Check what key it is
                key_name = None
                if matches_key(data, Key.up):
                    key_name = "UP ARROW"
                elif matches_key(data, Key.down):
                    key_name = "DOWN ARROW"
                elif matches_key(data, Key.left):
                    key_name = "LEFT ARROW"
                elif matches_key(data, Key.right):
                    key_name = "RIGHT ARROW"
                elif matches_key(data, Key.escape):
                    key_name = "ESC"
                elif matches_key(data, Key.enter):
                    key_name = "ENTER"
                elif data == "q":
                    running = False
                    key_name = "Q (quit)"

                # Use write to avoid line buffering issues in raw mode
                import sys

                sys.stdout.write(f"\r\x1b[KGot: {repr(data)}")
                if key_name:
                    sys.stdout.write(f" -> {key_name}")
                sys.stdout.write("\r\n")
                sys.stdout.flush()

    finally:
        terminal.restore_mode()
        print("Done!")


if __name__ == "__main__":
    main()
