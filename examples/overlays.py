#!/usr/bin/env python3
"""Overlay/Modal dialog demo - focused on Overlay component.

Demonstrates:
- Creating overlays with OverlayPosition
- show_overlay() and close_overlay()
- Focus management with overlays
- Modal dialog patterns

Usage:
    python overlays.py

Controls:
    o          - Open modal overlay
    Esc        - Close current overlay
    Tab        - Cycle focus
    Ctrl+C     - Exit
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypitui import (
    TUI,
    Container,
    Text,
    Input,
    BorderedBox,
    Overlay,
    OverlayPosition,
    Terminal,
)


def main() -> None:
    """Run the overlay demo."""
    print("Overlay Demo")
    print("Press 'o' to open modal, Esc to close, Ctrl+C to exit.")
    print()
    
    container = Container()
    container.add_child(Text("Overlay/Modal Demo"))
    container.add_child(Text("=" * 40))
    container.add_child(Text(""))
    container.add_child(Text("Press 'o' to open a modal overlay"))
    container.add_child(Text("Press Esc to close the modal"))
    container.add_child(Text(""))
    
    # Main input
    main_box = BorderedBox(title="Main Input")
    main_input = Input(placeholder="Type here...")
    main_box.add_child(main_input)
    container.add_child(main_box)
    
    # Status
    container.add_child(Text(""))
    status_text = Text("Status: Ready")
    container.add_child(status_text)
    
    def open_modal() -> None:
        """Open a modal overlay."""
        modal_container = Container()
        modal_container.add_child(Text("Modal Dialog"))
        modal_container.add_child(Text("-" * 20))
        modal_container.add_child(Text(""))
        modal_container.add_child(Text("This is a modal overlay!"))
        modal_container.add_child(Text("Press Esc to close."))
        
        modal_box = BorderedBox(title="Modal")
        modal_input = Input(placeholder="Modal input...")
        modal_box.add_child(modal_input)
        modal_container.add_child(modal_box)
        
        # Create overlay centered on screen
        overlay = Overlay(
            content=modal_container,
            position=OverlayPosition(row=5, col=20, width=40, height=8)
        )
        
        tui.show_overlay(overlay)
        status_text._text = "Status: Modal open"
        tui.render_frame()
    
    def close_modal() -> None:
        """Close current modal if any."""
        if tui._overlays:
            overlay = tui._overlays[-1]
            tui.close_overlay(overlay)
            status_text._text = "Status: Modal closed"
            tui.render_frame()
    
    with Terminal() as term:
        tui = TUI(term)
        tui.add_child(container)
        tui.render_frame()
        
        # Track nonlocal reference
        tui_ref = tui
        
        def on_input(data: bytes) -> None:
            if data == b"\x03":  # Ctrl+C
                term.stop()
                return
            
            if data == b"\x1b":  # Escape - close modal
                close_modal()
                return
            
            if data == b"o":  # Open modal
                open_modal()
                return
            
            if tui_ref._focused and hasattr(tui_ref._focused, 'handle_input'):
                if tui_ref._focused.handle_input(data):
                    tui_ref.render_frame()
        
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
