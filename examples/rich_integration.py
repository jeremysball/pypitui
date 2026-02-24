#!/usr/bin/env python3
"""Interactive demo showing Rich + PyPiTUI integration."""

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text as RichText
from rich.table import Table

from pypitui import (
    TUI,
    Container,
    Text,
    Spacer,
    SelectList,
    SelectItem,
    SelectListTheme,
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


def rich_to_lines(rich_obj, width: int = 80) -> list[str]:
    """Convert a Rich renderable to ANSI strings for PyPiTUI."""
    console = Console(
        width=width,
        no_color=False,
        force_terminal=True,
        legacy_windows=False,
    )
    with console.capture() as capture:
        console.print(rich_obj)
    output = capture.get()
    return [line for line in output.split("\n") if line or line == ""]


def build_rich_text_demo(width: int) -> Container:
    """Rich text markup demo."""
    container = Container()

    rich_text = RichText.from_markup(
        "[bold cyan]Hello[/bold cyan] [red]World[/red]! "
        "[dim]This is dim text.[/dim]"
    )
    for line in rich_to_lines(rich_text, width):
        container.add_child(Text(line, 0, 0))

    return container


def build_markdown_demo(width: int) -> Container:
    """Markdown rendering demo."""
    container = Container()

    md_content = """# Welcome to PyPiTUI

This is **bold** and *italic* text.

## Features

- Differential rendering
- Component-based UI
- Rich integration!

```python
from pypitui import Text
text = Text("Hello!")
```"""

    md = Markdown(md_content)
    for line in rich_to_lines(md, width):
        container.add_child(Text(line, 0, 0))

    return container


def build_table_demo(width: int) -> Container:
    """Table demo."""
    container = Container()

    table = Table(title="Demo Table", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")

    table.add_row("Item 1", "100", "✓ Active")
    table.add_row("Item 2", "200", "✗ Inactive")
    table.add_row("Item 3", "300", "✓ Active")

    for line in rich_to_lines(table, width):
        container.add_child(Text(line, 0, 0))

    return container


class RichDemoApp:
    """Rich integration demo application."""

    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal)
        self.running = True
        self.mode = "menu"

        # Menu items
        self.menu_items = [
            SelectItem("1", "Rich Text", "Text markup with colors"),
            SelectItem("2", "Markdown", "Render markdown content"),
            SelectItem("3", "Tables", "Formatted tables"),
            SelectItem("q", "Quit", "Exit the demo"),
        ]

        self.build_menu()

    def _clear_screen(self):
        """Clear TUI content for a new screen, preserving differential rendering state."""
        self.tui.clear()  # Remove old children (but keep _previous_lines for diff rendering)

    def build_menu(self):
        """Build the main menu UI."""
        self._clear_screen()
        self.mode = "menu"

        self.tui.add_child(Text("╔══════════════════════════════════════════╗", 0, 0))
        self.tui.add_child(Text("║   Rich + PyPiTUI Integration Demo        ║", 0, 0))
        self.tui.add_child(Text("╚══════════════════════════════════════════╝", 0, 0))
        self.tui.add_child(Spacer(1))

        menu = SelectList(self.menu_items, 10, create_theme())
        menu.on_select = self.on_menu_select
        self.tui.add_child(menu)
        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("ESC to return to menu", 0, 0))
        self.tui.set_focus(menu)

    def on_menu_select(self, item: SelectItem):
        """Handle menu selection."""
        if item.value == "q":
            self.running = False
        else:
            self.show_demo(item.value)

    def show_demo(self, demo_id: str):
        """Show a Rich demo."""
        self._clear_screen()
        self.mode = "demo"

        width, _ = self.terminal.get_size()

        demo_names = {"1": "Rich Text", "2": "Markdown", "3": "Tables"}
        self.tui.add_child(Text(f"═══ {demo_names.get(demo_id, 'Demo')} ═══", 0, 0))
        self.tui.add_child(Spacer(1))

        if demo_id == "1":
            self.tui.add_child(build_rich_text_demo(width))
        elif demo_id == "2":
            self.tui.add_child(build_markdown_demo(width))
        elif demo_id == "3":
            self.tui.add_child(build_table_demo(width))

        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text("Press ESC to return", 0, 0))

    def handle_input(self, data: str):
        """Handle input based on current mode."""
        if self.mode == "menu":
            if matches_key(data, Key.escape):
                self.running = False
            else:
                self.tui.handle_input(data)
        elif self.mode == "demo":
            if matches_key(data, Key.escape):
                self.build_menu()

    def run(self):
        """Main run loop."""
        self.tui.start()

        try:
            while self.running:
                data = self.terminal.read_sequence(timeout=0.05)
                if data:
                    self.handle_input(data)

                self.tui.request_render()
                self.tui.render_frame()

        except KeyboardInterrupt:
            pass
        finally:
            self.tui.stop()
            print("Goodbye!")


def main():
    """Run the interactive demo."""
    app = RichDemoApp()
    app.run()


if __name__ == "__main__":
    main()
