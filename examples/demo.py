#!/usr/bin/env python3
"""Demo application showcasing PyPiTUI library features."""

from pypitui import (
    TUI,
    Container,
    Text,
    Box,
    Spacer,
    SelectList,
    SelectItem,
    SelectListTheme,
    Input,
    OverlayOptions,
    ProcessTerminal,
    matches_key,
    Key,
)


def create_theme():
    """Create a simple theme for select lists."""
    return SelectListTheme(
        selected_prefix=lambda s: s,
        selected_text=lambda s: s,
        description=lambda s: s,
        scroll_info=lambda s: s,
        no_match=lambda s: s,
    )


class DemoApp:
    """Interactive demo application."""

    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal)
        self.running = True
        self.mode = "menu"
        self.overlay_handle = None

        # Build initial UI
        self.build_menu()

    def _clear_screen(self):
        """Clear TUI content for a new screen, preserving differential rendering state."""
        self.tui.clear()  # Remove all children (but keep _previous_lines for diff rendering)

    def build_menu(self):
        """Build the main menu UI."""
        self._clear_screen()
        self.mode = "menu"
        self.result_text = None

        # Title
        self.tui.add_child(Text("╔══════════════════════════════════════════╗", 0, 0))
        self.tui.add_child(Text("║       PyPiTUI Demo Application          ║", 0, 0))
        self.tui.add_child(Text("╚══════════════════════════════════════════╝", 0, 0))
        self.tui.add_child(Spacer(1))

        # Menu options
        menu_items = [
            SelectItem("1", "Text Demo", "Show text wrapping and styling"),
            SelectItem("2", "Input Demo", "Test text input with cursor"),
            SelectItem("3", "Select Demo", "Interactive selection list"),
            SelectItem("4", "Overlay Demo", "Show overlay dialogs"),
            SelectItem("q", "Quit", "Exit the application"),
        ]

        menu = SelectList(menu_items, 10, create_theme())
        menu.on_select = self.on_menu_select
        self.tui.add_child(menu)

        # Help text
        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("↑↓ Navigate  •  Enter Select  •  Esc Back", 0, 0))

        self.tui.set_focus(menu)

    def on_menu_select(self, item: SelectItem):
        """Handle menu selection."""
        if item.value == "1":
            self.show_text_demo()
        elif item.value == "2":
            self.show_input_demo()
        elif item.value == "3":
            self.show_select_demo()
        elif item.value == "4":
            self.show_overlay_demo()
        elif item.value == "q":
            self.running = False

    def show_text_demo(self):
        """Show text wrapping demo."""
        self._clear_screen()
        self.mode = "text"

        self.tui.add_child(Text("═══ Text Demo ═══", 0, 0))
        self.tui.add_child(Spacer(1))

        # Long text that will wrap
        long_text = (
            "This is a long line of text that demonstrates word wrapping "
            "in the Text component. It should wrap across multiple lines "
            "while preserving the content."
        )
        self.tui.add_child(Text(long_text, 1, 1))

        self.tui.add_child(Spacer(1))

        # Text in a box
        box = Box(2, 1)
        box.add_child(Text("Boxed content with padding", 0, 0))
        self.tui.add_child(box)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("Press ESC to return to menu", 0, 0))

    def show_input_demo(self):
        """Show input field demo."""
        self._clear_screen()
        self.mode = "input"

        self.tui.add_child(Text("═══ Input Demo ═══", 0, 0))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("Type something and press Enter:", 0, 0))
        self.tui.add_child(Spacer(1))

        input_field = Input(placeholder="Enter text here...")
        input_field.on_submit = self.on_input_submit
        self.tui.add_child(input_field)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("Ctrl+A/Home: Start  •  Ctrl+E/End: End", 0, 0))
        self.tui.add_child(Text("Ctrl+U: Delete to start  •  Ctrl+K: Delete to end", 0, 0))
        self.tui.add_child(Text("ESC to return to menu", 0, 0))

        self.result_text = Text("", 0, 0)
        self.tui.add_child(Spacer(1))
        self.tui.add_child(self.result_text)

        self.tui.set_focus(input_field)

    def on_input_submit(self, value: str):
        """Handle input submission."""
        if self.result_text:
            self.result_text.set_text(f"You entered: {value}")

    def show_select_demo(self):
        """Show select list demo."""
        self._clear_screen()
        self.mode = "select"

        self.tui.add_child(Text("═══ Select Demo ═══", 0, 0))
        self.tui.add_child(Spacer(1))

        items = [
            SelectItem("apple", "Apple", "A sweet red fruit"),
            SelectItem("banana", "Banana", "A yellow tropical fruit"),
            SelectItem("cherry", "Cherry", "A small red stone fruit"),
            SelectItem("date", "Date", "A sweet middle eastern fruit"),
            SelectItem("elderberry", "Elderberry", "A dark purple berry"),
            SelectItem("fig", "Fig", "A sweet Mediterranean fruit"),
            SelectItem("grape", "Grape", "Small juicy fruit"),
            SelectItem("honeydew", "Honeydew", "A sweet melon"),
        ]

        select_list = SelectList(items, 5, create_theme())
        select_list.on_select = self.on_fruit_select
        self.tui.add_child(select_list)

        self.tui.add_child(Spacer(1))
        self.result_text = Text("", 0, 0)
        self.tui.add_child(self.result_text)
        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("Type to filter  •  ESC to return", 0, 0))

        self.tui.set_focus(select_list)

    def on_fruit_select(self, item: SelectItem):
        """Handle fruit selection."""
        if self.result_text:
            self.result_text.set_text(f"Selected: {item.label} ({item.value})")

    def show_overlay_demo(self):
        """Show overlay demo."""
        self._clear_screen()
        self.mode = "overlay"
        self.overlay_handle = None

        self.tui.add_child(Text("═══ Overlay Demo ═══", 0, 0))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("Press 1-4 to show different overlays:", 0, 0))
        self.tui.add_child(Text("1. Center overlay", 0, 0))
        self.tui.add_child(Text("2. Top-right overlay", 0, 0))
        self.tui.add_child(Text("3. Bottom-left overlay", 0, 0))
        self.tui.add_child(Text("4. Wide overlay (80%)", 0, 0))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("ESC to return to menu", 0, 0))

    def show_overlay(self, anchor: str, width):
        """Show an overlay with given options."""
        if self.overlay_handle:
            self.overlay_handle.hide()

        content = Container()
        content.add_child(Text("┌─────────────────────────────────┐", 0, 0))
        content.add_child(Text("│  Overlay Panel                  │", 0, 0))
        content.add_child(Text("├─────────────────────────────────┤", 0, 0))
        content.add_child(Text("│ Press ESC to close this overlay │", 0, 0))
        content.add_child(Text("└─────────────────────────────────┘", 0, 0))

        options = OverlayOptions(width=width, anchor=anchor)
        self.overlay_handle = self.tui.show_overlay(content, options)

    def handle_input(self, data: str):
        """Handle input based on current mode."""
        if self.mode == "menu":
            if matches_key(data, Key.escape):
                self.running = False
            else:
                self.tui.handle_input(data)

        elif self.mode == "text":
            if matches_key(data, Key.escape):
                self.build_menu()

        elif self.mode == "input":
            if matches_key(data, Key.escape):
                self.build_menu()
            else:
                self.tui.handle_input(data)

        elif self.mode == "select":
            if matches_key(data, Key.escape):
                self.build_menu()
            else:
                self.tui.handle_input(data)

        elif self.mode == "overlay":
            if matches_key(data, Key.escape):
                if self.overlay_handle:
                    self.overlay_handle.hide()
                    self.overlay_handle = None
                else:
                    self.build_menu()
            elif data == "1":
                self.show_overlay("center", 35)
            elif data == "2":
                self.show_overlay("top-right", 35)
            elif data == "3":
                self.show_overlay("bottom-left", 35)
            elif data == "4":
                self.show_overlay("center", "80%")

    def run(self):
        """Main run loop."""
        self.tui.start()

        try:
            while self.running:
                # Read input (use read_sequence for arrow keys)
                data = self.terminal.read_sequence(timeout=0.05)
                if data:
                    self.handle_input(data)

                # Render with force=True when we just switched modes
                self.tui.request_render()
                self.tui.render_frame()

        finally:
            self.tui.stop()


def main():
    """Main entry point."""
    print("PyPiTUI Demo Application")
    print("Starting...")
    print()

    try:
        app = DemoApp()
        app.run()
    except KeyboardInterrupt:
        pass
    print("Goodbye!")


if __name__ == "__main__":
    main()
