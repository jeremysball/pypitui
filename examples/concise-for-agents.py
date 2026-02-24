#!/usr/bin/env python3
"""PyPiTUI Ultimate Demo - Complete Feature Showcase & LLM Learning Guide

This demo serves as:
1. A comprehensive feature showcase for humans
2. A learning resource for AI agents understanding PyPiTUI patterns

Key Patterns Demonstrated:
- TUI lifecycle (start/stop/render loop)
- Component hierarchy (Container -> children)
- State management (screen switching, form data)
- Event handling (keyboard input, callbacks)
- Differential rendering (automatic via TUI class)
"""

import time
from pypitui import (
    TUI, Container, Text, Box, BorderedBox, Spacer,
    SelectList, SelectItem, SelectListTheme, Input,
    OverlayOptions, ProcessTerminal, matches_key, Key,
)

# Optional: Rich integration for markdown/tables
try:
    from pypitui.rich_components import Markdown, RichText, RichTable
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# =============================================================================
# ANSI COLOR UTILITIES
# =============================================================================
class Colors:
    """ANSI color codes for terminal styling."""
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    MAGENTA = "\x1b[35m"
    WHITE = "\x1b[37m"
    BRIGHT_CYAN = "\x1b[96m"


# =============================================================================
# DEMO APPLICATION
# =============================================================================
class UltimateDemoApp:
    """
    Main demo application demonstrating PyPiTUI patterns.
    
    ARCHITECTURE:
    - TUI manages terminal state and differential rendering
    - Screens built dynamically via _clear_screen() + add_child()
    - State stored in instance variables (self.current_screen, self.form_data)
    - Input handled centrally in handle_input(), dispatched to components
    """

    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal, show_hardware_cursor=True)
        self.running = True
        self.current_screen = "menu"
        self.form_data = {"name": "", "email": ""}
        self.wizard_step = 0
        self.overlay_handle = None
        
        # Theme for SelectList components
        self.theme = SelectListTheme(
            selected_prefix=lambda s: f"{Colors.BRIGHT_CYAN}▶{Colors.RESET} ",
            selected_text=lambda s: f"{Colors.BOLD}{s}{Colors.RESET}",
            description=lambda s: f"{Colors.DIM}{s}{Colors.RESET}",
        )
        
        self.build_menu()

    def _clear_screen(self):
        """Clear all children while preserving TUI state for differential rendering."""
        self.tui.clear()

    def build_menu(self):
        """Main menu - demonstrates SelectList for navigation."""
        self._clear_screen()
        self.current_screen = "menu"
        self.wizard_step = 0

        # Header using BorderedBox (preferred over manual box drawing)
        # NOTE: Uses default padding_y=0 for tight vertical alignment
        header = BorderedBox(padding_x=2, max_width=45, title="🐍 PyPiTUI")
        header.add_child(Text("Terminal UI Framework", 0, 0))
        self.tui.add_child(header)
        self.tui.add_child(Spacer(1))

        # Menu using SelectList (keyboard-navigable list)
        items = [
            SelectItem("components", "🧩 Components", "Text, Box, BorderedBox, Input"),
            SelectItem("wizard", "🧙 Form Wizard", "Multi-step form with validation"),
            SelectItem("overlays", "🪟 Overlays", "Floating panels & dialogs"),
            SelectItem("rich", "✨ Rich Integration", "Markdown & formatted text"),
        ]
        menu = SelectList(items, 4, self.theme)
        menu.on_select = self.on_menu_select
        self.tui.add_child(menu)
        self.tui.set_focus(menu)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text(f"{Colors.DIM}↑↓ Navigate • Enter Select • Q Quit{Colors.RESET}", 0, 0))

    def on_menu_select(self, item: SelectItem):
        """Route menu selection to appropriate screen."""
        handlers = {
            "components": self.show_components,
            "wizard": self.show_wizard,
            "overlays": self.show_overlays,
            "rich": self.show_rich,
        }
        handlers.get(item.value, self.build_menu)()

    def show_components(self):
        """Demonstrates core components: Text, Box, BorderedBox, Input."""
        self._clear_screen()
        self.current_screen = "components"

        self.tui.add_child(Text(f"{Colors.BOLD}Component Showcase{Colors.RESET}", 0, 0))
        self.tui.add_child(Spacer(1))

        # Text component with word wrapping
        self.tui.add_child(Text(
            "Text component automatically wraps long content to fit the terminal width. "
            "This demonstrates word wrapping in action.",
            padding_x=2, padding_y=1
        ))
        self.tui.add_child(Spacer(1))

        # Box with padding (basic container)
        self.tui.add_child(Text(f"{Colors.BOLD}Box (padding container):{Colors.RESET}", 0, 0))
        box = Box(padding_x=2, padding_y=1)
        box.add_child(Text("Content inside Box with padding"))
        self.tui.add_child(box)
        self.tui.add_child(Spacer(1))

        # BorderedBox (recommended for panels)
        self.tui.add_child(Text(f"{Colors.BOLD}BorderedBox (preferred):{Colors.RESET}", 0, 0))
        bordered = BorderedBox(padding_x=2, max_width=35, title="Panel Title")
        bordered.add_child(Text("BorderedBox draws borders and wraps content"))
        self.tui.add_child(bordered)
        self.tui.add_child(Spacer(1))

        # Input component
        self.tui.add_child(Text(f"{Colors.BOLD}Input:{Colors.RESET}", 0, 0))
        inp = Input(placeholder="Type something...")
        inp.on_submit = lambda v: self.show_result(f"You typed: {v}")
        self.tui.add_child(inp)
        self.tui.set_focus(inp)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text(f"{Colors.DIM}ESC to return{Colors.RESET}", 0, 0))

    def show_wizard(self):
        """Multi-step form demonstrating state management across screens."""
        self._clear_screen()
        self.current_screen = "wizard"

        steps = [("Profile", "Enter details"), ("Confirm", "Review")]
        step_name, step_desc = steps[self.wizard_step]

        self.tui.add_child(Text(f"{Colors.BOLD}Wizard: {step_name}{Colors.RESET}", 0, 0))
        self.tui.add_child(Text(step_desc, 0, 0))
        self.tui.add_child(Spacer(1))

        if self.wizard_step == 0:
            # Form fields
            self.tui.add_child(Text("Name:", 0, 0))
            name_inp = Input(placeholder="Your name")
            name_inp.set_value(self.form_data["name"])
            self.tui.add_child(name_inp)
            self.name_input = name_inp

            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text("Email:", 0, 0))
            email_inp = Input(placeholder="Your email")
            email_inp.set_value(self.form_data["email"])
            self.tui.add_child(email_inp)
            self.email_input = email_inp

            self.tui.set_focus(name_inp)
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"{Colors.DIM}Tab: switch fields • Enter: continue{Colors.RESET}", 0, 0))

        else:  # Confirmation step
            self.tui.add_child(Text(f"Name: {self.form_data['name'] or '(empty)'}", 0, 0))
            self.tui.add_child(Text(f"Email: {self.form_data['email'] or '(empty)'}", 0, 0))
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"{Colors.GREEN}✓ Form complete!{Colors.RESET}", 0, 0))
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"{Colors.DIM}ESC to return to menu{Colors.RESET}", 0, 0))

    def show_overlays(self):
        """Demonstrates overlay system with positioning options."""
        self._clear_screen()
        self.current_screen = "overlays"

        self.tui.add_child(Text(f"{Colors.BOLD}Overlay System{Colors.RESET}", 0, 0))
        self.tui.add_child(Spacer(1))

        items = [
            SelectItem("center", "Center", "Centered overlay"),
            SelectItem("top", "Top", "Top of screen"),
            SelectItem("bottom", "Bottom", "Bottom of screen"),
        ]
        lst = SelectList(items, 3, self.theme)
        lst.on_select = self.show_overlay_example
        self.tui.add_child(lst)
        self.tui.set_focus(lst)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text(f"{Colors.DIM}ESC to return{Colors.RESET}", 0, 0))

    def show_overlay_example(self, item: SelectItem):
        """Show overlay at specified anchor position."""
        anchors = {"center": "center", "top": "top", "bottom": "bottom"}
        anchor = anchors.get(item.value, "center")

        content = BorderedBox(padding_x=2, padding_y=1, max_width=35, title=f"{anchor.title()} Overlay")
        content.add_child(Text(f"This overlay is anchored to {anchor}"))
        content.add_child(Text("Press ESC to close"))

        self.overlay_handle = self.tui.show_overlay(
            content, OverlayOptions(width=35, anchor=anchor)
        )

    def show_rich(self):
        """Rich integration demo (markdown, formatted text, tables)."""
        self._clear_screen()
        self.current_screen = "rich"

        self.tui.add_child(Text(f"{Colors.BOLD}Rich Integration{Colors.RESET}", 0, 0))
        self.tui.add_child(Spacer(1))

        if not RICH_AVAILABLE:
            self.tui.add_child(Text(f"{Colors.YELLOW}Rich not installed. Run: pip install pypitui[rich]{Colors.RESET}", 0, 0))
        else:
            items = [
                SelectItem("markdown", "Markdown", "Render markdown"),
                SelectItem("richtext", "RichText", "Styled text"),
                SelectItem("table", "Table", "Formatted table"),
            ]
            lst = SelectList(items, 3, self.theme)
            lst.on_select = self.show_rich_overlay
            self.tui.add_child(lst)
            self.tui.set_focus(lst)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text(f"{Colors.DIM}ESC to return{Colors.RESET}", 0, 0))

    def show_rich_overlay(self, item: SelectItem):
        """Show Rich component in an overlay."""
        if self.overlay_handle:
            self.overlay_handle.hide()

        content = Container()

        if item.value == "markdown":
            md_text = "# Markdown\n\n**Bold** and *italic* text.\n\n```python\nprint('Hello')\n```"
            content.add_child(Markdown(md_text, padding_x=1, padding_y=1))
        elif item.value == "richtext":
            content.add_child(RichText("[bold cyan]Styled[/bold cyan] [red]Text[/red]!", padding_x=1, padding_y=1))
        elif item.value == "table":
            table = RichTable(title="Demo", padding_x=1, padding_y=1)
            table.add_column("Name")
            table.add_column("Status")
            table.add_row("Feature 1", "✓")
            table.add_row("Feature 2", "✓")
            content.add_child(table)

        self.overlay_handle = self.tui.show_overlay(
            content, OverlayOptions(width="70%", anchor="center")
        )

    def show_result(self, message: str):
        """Show a temporary result message."""
        self._clear_screen()
        self.current_screen = "result"
        self.tui.add_child(Text(message, 0, 0))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text(f"{Colors.DIM}Press any key...{Colors.RESET}", 0, 0))

    def handle_input(self, data: str):
        """
        Central input handler - dispatches to appropriate handler based on state.
        
        PATTERN: Check global keys first (quit, back), then route to screen-specific
        handling, finally pass to focused component via tui.handle_input().
        """
        # Global: Quit from menu
        if data.lower() == "q" and self.current_screen == "menu":
            self.running = False
            return

        # Global: ESC returns to menu or closes overlay
        if matches_key(data, Key.escape):
            if self.tui.has_overlay():
                self.tui.hide_overlay()
                self.overlay_handle = None
            else:
                self.build_menu()
            return

        # Wizard: Tab navigation and Enter submission
        if self.current_screen == "wizard" and self.wizard_step == 0:
            if matches_key(data, Key.tab) and hasattr(self, 'name_input'):
                # Toggle focus between name and email
                new_focus = self.email_input if self.tui._focused_component == self.name_input else self.name_input
                self.tui.set_focus(new_focus)
                return
            elif matches_key(data, Key.enter):
                # Submit form
                self.form_data["name"] = self.name_input.get_value()
                self.form_data["email"] = self.email_input.get_value()
                self.wizard_step = 1
                self.show_wizard()
                return

        # Default: Pass to TUI for component handling
        self.tui.handle_input(data)

    def run(self):
        """Main loop at 60 FPS with non-blocking input."""
        self.tui.start()
        frame_duration = 1.0 / 60.0

        try:
            while self.running:
                frame_start = time.time()

                # Non-blocking input read
                data = self.terminal.read_sequence(timeout=0.001)
                if data:
                    self.handle_input(data)

                # Render
                self.tui.request_render()
                self.tui.render_frame()

                # Frame timing for 60 FPS
                elapsed = time.time() - frame_start
                if elapsed < frame_duration:
                    time.sleep(frame_duration - elapsed)
        finally:
            self.tui.stop()


def main():
    """Entry point."""
    print("PyPiTUI Ultimate Demo")
    print("")
    UltimateDemoApp().run()
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
