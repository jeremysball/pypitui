#!/usr/bin/env python3
"""Simple demo of Phase 1 terminal abstraction.

Usage:
    uv run python examples/demo_terminal.py

Press 'q' to quit, 'c' to clear screen, 'h' to hide cursor, 's' to show cursor.
"""

import sys

# Add src to path for demo
sys.path.insert(0, "src")

from pypitui.keys import Key, parse_key
from pypitui.terminal import Terminal


def main() -> None:
    """Run terminal demo."""
    print("Starting terminal demo...")
    print("This will switch to raw mode. Press 'q' to quit.")
    input("Press Enter to continue...")

    with Terminal() as term:
        term.clear_screen()
        # Flush stdout to ensure output appears immediately
        import sys
        sys.stdout.flush()
        
        term.write("Terminal Demo (Phase 1)\r\n")
        term.write("=======================\r\n\r\n")
        term.write("Commands:\r\n")
        term.write("  q - quit\r\n")
        term.write("  c - clear screen\r\n")
        term.write("  h - hide cursor\r\n")
        term.write("  s - show cursor\r\n")
        term.write("\r\nPress keys to see them parsed...\r\n\r\n")

        running = True

        def on_input(data: bytes) -> None:
            nonlocal running
            result = parse_key(data)

            if result == Key.ESCAPE:
                term.write("[ESCAPE]\r\n")
            elif result == Key.ENTER:
                term.write("[ENTER]\r\n")
            elif result == Key.TAB:
                term.write("[TAB]\r\n")
            elif result == Key.BACKSPACE:
                term.write("[BACKSPACE]\r\n")
            elif result == "q":
                term.write("[QUIT]\r\n")
                running = False
            elif result == "c":
                term.clear_screen()
                term.write("Screen cleared!\r\n")
            elif result == "h":
                term.hide_cursor()
                term.write("Cursor hidden\r\n")
            elif result == "s":
                term.show_cursor()
                term.write("Cursor shown\r\n")
            elif isinstance(result, str) and len(result) == 1:
                term.write(f"Key: {result}\r\n")
            else:
                term.write(f"Parsed: {result!r}\r\n")

        term.start(on_input)

        try:
            while running:
                import time

                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            term.stop()
            term.show_cursor()  # Ensure cursor is restored
            term.write("\r\nDemo complete!\r\n")


if __name__ == "__main__":
    main()
