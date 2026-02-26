#!/usr/bin/env python3
"""Demo to test scrollback buffer with PROPER streaming.

This demonstrates the CORRECT way to use PyPiTUI for streaming content:
- Add new content incrementally with add_child()
- Never call tui.clear() for growing content
- Old content flows into terminal's native scrollback buffer
- Only NEW lines are rendered each frame (differential)

Run this and use Shift+PgUp to scroll back through history.
"""

import asyncio
import time

from pypitui import ProcessTerminal, TUI, Text


async def main():
    terminal = ProcessTerminal()
    tui = TUI(terminal)

    tui.start()

    # Header - added once, stays at top (will scroll into history)
    tui.add_child(Text("Scrollback Demo - Press Ctrl+C to exit", padding_y=0))
    tui.add_child(Text("", padding_y=0))  # Spacer

    try:
        # Add lines incrementally - THIS IS THE KEY PATTERN
        for i in range(100):
            # Just add the NEW line - don't clear, don't re-add old lines
            tui.add_child(Text(f"Line {i}: {'x' * (i % 40)}", padding_y=0))

            # Render - only the new line is differentially rendered
            # Old lines are frozen in scrollback
            tui.request_render()
            tui.render_frame()

            await asyncio.sleep(0.1)

        # Add final message
        tui.add_child(Text("", padding_y=0))
        tui.add_child(Text("=== Done! Use Shift+PgUp to scroll ===", padding_y=0))

        tui.request_render()
        tui.render_frame()

        # Keep running so user can scroll
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        tui.stop()


if __name__ == "__main__":
    asyncio.run(main())
