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


def main():
    """Run the interactive demo."""
    terminal = ProcessTerminal()
    tui = TUI(terminal)
    running = True
    current_demo = None

    # Build menu
    tui.add_child(Text("╔══════════════════════════════════════════╗", 0, 0))
    tui.add_child(Text("║   Rich + PyPiTUI Integration Demo        ║", 0, 0))
    tui.add_child(Text("╚══════════════════════════════════════════╝", 0, 0))
    tui.add_child(Spacer(1))

    items = [
        SelectItem("1", "Rich Text", "Text markup with colors"),
        SelectItem("2", "Markdown", "Render markdown content"),
        SelectItem("3", "Tables", "Formatted tables"),
        SelectItem("q", "Quit", "Exit the demo"),
    ]

    menu = SelectList(items, 10, create_theme())
    tui.add_child(menu)
    tui.add_child(Spacer(1))
    tui.add_child(Text("ESC to return to menu", 0, 0))
    tui.set_focus(menu)

    def on_select(item: SelectItem):
        nonlocal current_demo
        if item.value == "q":
            nonlocal running
            running = False
        else:
            current_demo = item.value

    menu.on_select = on_select

    tui.start()

    try:
        while running:
            data = terminal.read_sequence(timeout=0.05)
            if data:
                if current_demo and matches_key(data, Key.escape):
                    # Return to menu
                    current_demo = None
                    tui = TUI(terminal)
                    tui.add_child(Text("╔══════════════════════════════════════════╗", 0, 0))
                    tui.add_child(Text("║   Rich + PyPiTUI Integration Demo        ║", 0, 0))
                    tui.add_child(Text("╚══════════════════════════════════════════╝", 0, 0))
                    tui.add_child(Spacer(1))
                    menu = SelectList(items, 10, create_theme())
                    menu.on_select = on_select
                    tui.add_child(menu)
                    tui.add_child(Spacer(1))
                    tui.add_child(Text("ESC to return to menu", 0, 0))
                    tui.set_focus(menu)
                elif current_demo:
                    tui.handle_input(data)
                else:
                    tui.handle_input(data)

            # Render based on current state
            if current_demo:
                width, _ = terminal.get_size()
                demo_tui = TUI(terminal)
                demo_tui.add_child(Text(f"═══ {current_demo.title()} Demo ═══", 0, 0))
                demo_tui.add_child(Spacer(1))

                if current_demo == "1":
                    demo_tui.add_child(build_rich_text_demo(width))
                elif current_demo == "2":
                    demo_tui.add_child(build_markdown_demo(width))
                elif current_demo == "3":
                    demo_tui.add_child(build_table_demo(width))

                demo_tui.add_child(Spacer(1))
                demo_tui.add_child(Text("Press ESC to return", 0, 0))
                demo_tui.request_render(force=True)
                demo_tui.render_frame()
            else:
                tui.request_render()
                tui.render_frame()

    except KeyboardInterrupt:
        pass
    finally:
        tui.stop()
        print("Goodbye!")


if __name__ == "__main__":
    main()
