#!/usr/bin/env python3
"""Input handling demo - focused on Input component.

Demonstrates:
- Text input with placeholder
- Character limits
- Submit callbacks
- Backspace handling

Usage:
    python inputs.py

Controls:
    Type characters  - Add to input
    Backspace        - Remove last character
    Enter            - Submit current value
    Ctrl+C           - Exit
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypitui import TUI, Container, Text, Input, BorderedBox, Terminal


def main() -> None:
    """Run the input demo."""
    print("Input Demo")
    print("Type characters, press Enter to submit, Ctrl+C to exit.")
    print()
    
    container = Container()
    
    # Header
    container.add_child(Text("Input Component Demo"))
    container.add_child(Text("=" * 40))
    container.add_child(Text(""))
    
    # Username input
    username_box = BorderedBox(title="Username (max 15 chars)")
    username_input = Input(placeholder="Enter username...", max_length=15)
    
    def on_username_submit(value: str) -> None:
        print(f"  -> Username submitted: '{value}'")
    
    username_input.on_submit = on_username_submit
    username_box.add_child(username_input)
    container.add_child(username_box)
    
    container.add_child(Text(""))
    
    # Password input (displayed as-is for demo)
    password_box = BorderedBox(title="Password (no limit)")
    password_input = Input(placeholder="Enter password...")
    
    def on_password_submit(value: str) -> None:
        print(f"  -> Password submitted: {'*' * len(value)}")
    
    password_input.on_submit = on_password_submit
    password_box.add_child(password_input)
    container.add_child(password_box)
    
    container.add_child(Text(""))
    container.add_child(Text("Press Ctrl+C to exit"))
    
    # Run TUI
    with Terminal() as term:
        tui = TUI(term)
        tui.add_child(container)
        tui.render_frame()
        
        def on_input(data: bytes) -> None:
            if data == b"\x03":  # Ctrl+C
                term.stop()
                return
            
            if tui._focused and hasattr(tui._focused, 'handle_input'):
                if tui._focused.handle_input(data):
                    tui.render_frame()
        
        term.start(on_input)
        
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
