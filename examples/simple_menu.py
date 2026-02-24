#!/usr/bin/env python3
"""Simple interactive menu example using PyPiTUI."""

from pypitui import (
    TUI,
    Text,
    Spacer,
    SelectList,
    SelectItem,
    SelectListTheme,
    ProcessTerminal,
)


def main():
    """Run a simple interactive menu."""
    # Create terminal and TUI (no alternate buffer - content stays visible)
    terminal = ProcessTerminal()
    tui = TUI(terminal)

    # Build UI
    tui.add_child(Text("════════════════════════════", 0, 0))
    tui.add_child(Text("  Select an Option:", 0, 0))
    tui.add_child(Text("════════════════════════════", 0, 0))
    tui.add_child(Spacer(1))

    # Create menu items
    items = [
        SelectItem("1", "Option One", "First choice"),
        SelectItem("2", "Option Two", "Second choice"),
        SelectItem("3", "Option Three", "Third choice"),
        SelectItem("q", "Quit", "Exit the program"),
    ]

    # Create theme
    theme = SelectListTheme(
        selected_prefix=lambda s: s,
        selected_text=lambda s: s,
        description=lambda s: s,
        scroll_info=lambda s: s,
        no_match=lambda s: s,
    )

    # Create select list
    select_list = SelectList(items, 5, theme)
    tui.add_child(select_list)

    # Result display
    tui.add_child(Spacer(1))
    result_text = Text("", 0, 0)
    tui.add_child(result_text)

    # Set focus
    tui.set_focus(select_list)

    # Track running state
    running = True

    # Selection callback
    def on_select(item: SelectItem):
        nonlocal running
        if item.value == "q":
            running = False
        else:
            result_text.set_text(f"You selected: {item.label}")

    select_list.on_select = on_select

    # Start TUI
    tui.start()

    try:
        while running:
            # Read input with read_sequence for arrow keys
            data = terminal.read_sequence(timeout=0.05)
            if data:
                tui.handle_input(data)

            # Render
            tui.request_render()
            tui.render_frame()

    except KeyboardInterrupt:
        pass
    finally:
        tui.stop()
        print("Goodbye!")


if __name__ == "__main__":
    main()
