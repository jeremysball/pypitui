#!/usr/bin/env python3
"""PyPiTUI Demo - Full component showcase.

Demonstrates all PyPiTUI components and features:
- Container with vertical layout
- Text with wrapping
- Input with placeholder and submit callback
- SelectList with navigation
- BorderedBox decoration
- Overlay modal
- Focus management
- Differential rendering

Usage:
    python demo.py

Controls:
    Tab        - Cycle focus between components
    Up/Down    - Navigate SelectList
    Enter      - Submit Input or SelectList selection
    Ctrl+C     - Exit
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypitui import (
    TUI,
    Container,
    Text,
    Input,
    SelectList,
    SelectItem,
    BorderedBox,
    Overlay,
    OverlayPosition,
    Terminal,
)


def main() -> None:
    """Run the demo."""
    print("PyPiTUI Demo")
    print("This demo shows all components. Run in a terminal for full effect.")
    print()
    
    # Create components
    container = Container()
    
    # Header text
    header = Text("PyPiTUI Demo - Full Component Showcase")
    container.add_child(header)
    
    # Empty line
    container.add_child(Text(""))
    
    # Input with bordered box
    input_box = BorderedBox(title="Name Input")
    name_input = Input(placeholder="Enter your name", max_length=20)
    
    def on_name_submit(value: str) -> None:
        """Handle name submission."""
        print(f"Hello, {value}!")
    
    name_input.on_submit = on_name_submit
    input_box.add_child(name_input)
    container.add_child(input_box)
    
    # Empty line
    container.add_child(Text(""))
    
    # SelectList with bordered box
    select_box = BorderedBox(title="Choose Option")
    items = [
        SelectItem(id="option1", label="Option 1 - First choice"),
        SelectItem(id="option2", label="Option 2 - Second choice"),
        SelectItem(id="option3", label="Option 3 - Third choice"),
    ]
    select_list = SelectList(items=items, max_visible=3)
    
    def on_select(item_id: str) -> None:
        """Handle selection."""
        print(f"Selected: {item_id}")
    
    select_list.on_select = on_select
    select_box.add_child(select_list)
    container.add_child(select_box)
    
    # Empty line
    container.add_child(Text(""))
    
    # Footer text
    footer = Text("Controls: Tab=cycle focus | Up/Down=navigate | Enter=submit | Ctrl+C=exit")
    container.add_child(footer)
    
    # Create TUI and render
    with Terminal() as term:
        tui = TUI(term)
        tui.add_child(container)
        
        # Initial render
        tui.render_frame()
        
        # Set up input handling
        def on_input(data: bytes) -> None:
            """Handle terminal input."""
            # Handle Ctrl+C
            if data == b"\x03":
                term.stop()
                return
            
            # Pass to focused component
            if tui._focused is not None:
                consumed = tui._focused.handle_input(data)
                if consumed:
                    tui.render_frame()
        
        term.start(on_input)
        
        # Keep running until stopped
        try:
            while term._input_thread and term._input_thread.is_alive():
                import time
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            term.stop()


if __name__ == "__main__":
    main()
