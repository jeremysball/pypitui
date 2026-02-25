#!/usr/bin/env python3
"""Demo to test scrollback buffer support.

Run this in a terminal and use Shift+PgUp to scroll back through history.
"""

import asyncio
import time

from pypitui import ProcessTerminal, TUI, Text


async def main():
    terminal = ProcessTerminal()
    tui = TUI(terminal)

    tui.start()

    # Keep all lines
    all_lines = []

    try:
        # Add lines continuously
        for i in range(40):
            all_lines.append(f"Line {i}: {'x' * (i % 40)}")
            
            # Clear and re-render all lines
            tui.clear()
            
            # Header
            tui.add_child(Text(f"Line count: {len(all_lines)}", padding_y=0))
            tui.add_child(Text(f"Max rendered: {tui._max_lines_rendered}", padding_y=0))
            tui.add_child(Text("", padding_y=0))  # Spacer
            
            # All lines
            for line in all_lines:
                tui.add_child(Text(line, padding_y=0))
            
            tui.request_render()
            tui.render_frame()
            await asyncio.sleep(0.1)
        
        # Keep running so user can scroll
        tui.add_child(Text("", padding_y=0))
        tui.add_child(Text("=== Done! Use Shift+PgUp to scroll ===", padding_y=0))
        tui.add_child(Text("Press Ctrl+C to exit", padding_y=0))
        tui.request_render()
        tui.render_frame()
        
        # Wait for user
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        pass
    finally:
        tui.stop()


if __name__ == "__main__":
    asyncio.run(main())
