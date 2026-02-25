# PyPiTUI

A Python port of [@mariozechner/pi-tui](https://github.com/badlogic/pi-mono/tree/main/packages/tui) - a terminal UI library with differential rendering.

## Installation

```bash
pip install pypitui

# With Rich integration for markdown, tables, etc.
pip install pypitui[rich]
```

## Rich Integration

PyPiTUI works seamlessly with [Rich](https://github.com/Textualize/rich) for advanced formatting:

- **Markdown rendering** - Headers, lists, code blocks, links
- **Tables** - Beautiful bordered tables
- **Syntax highlighting** - Code blocks with pygments
- **Text markup** - `[bold red]Hello[/bold red]`
- **Panels, progress bars, trees** - Any Rich renderable

```python
from pypitui.rich_components import Markdown, RichTable, RichText

# Markdown
md = Markdown("# Hello\n\n**Bold** and *italic* text.")

# Rich text markup
text = RichText("[bold cyan]Hello[/bold cyan] [red]World[/red]!")

# Tables
table = RichTable(title="Results")
table.add_column("Name", style="cyan")
table.add_column("Value", style="green")
table.add_row("Item 1", "100")
```

See `examples/rich_integration.py` for the full demo.

## Running the Examples

```bash
# Clone the repository
git clone https://github.com/user/pypitui.git
cd pypitui

# Install with dev dependencies
uv sync --extra dev

# Run the simple menu example
uv run python examples/simple_menu.py

# Run the full demo
uv run python examples/demo.py
```

## Features

- **Differential Rendering** - Only updates changed lines for flicker-free UI
- **Scrollback Support** - Content flows into terminal's native scrollback buffer (use Shift+PgUp to view history)
- **Component-based** - Simple Component interface similar to React
- **Built-in Components** - Text, Box, Input, SelectList, Spacer, Container
- **Overlay System** - Modal dialogs and overlays with flexible positioning
- **Keyboard Input** - Cross-platform key detection with Kitty protocol support
- **IME Support** - Proper cursor positioning for CJK input methods

## Quick Start

```python
from pypitui import TUI, Text, Input, ProcessTerminal

# Create terminal and TUI
terminal = ProcessTerminal()
tui = TUI(terminal)  # Uses main buffer (content stays visible after exit)

# For full-screen apps that restore terminal on exit:
# tui = TUI(terminal, use_alternate_buffer=True)

# Add components
tui.add_child(Text("Welcome to PyPiTUI!"))

input_field = Input(placeholder="Type something...")
input_field.on_submit = lambda text: print(f"You typed: {text}")
tui.add_child(input_field)

# Set focus
tui.set_focus(input_field)

# Main loop
tui.start()
try:
    while True:
        data = terminal.read_sequence(timeout=0.1)
        if data:
            tui.handle_input(data)  # Or: input_field.handle_input(data)
        tui.request_render()
        tui.render_frame()
finally:
    tui.stop()
```

## Scrollback Support

PyPiTUI supports terminal scrollback by default. When content exceeds the terminal height, it flows into the terminal's native scrollback buffer instead of being clipped.

```python
# Default: main buffer mode - content stays in scrollback
tui = TUI(terminal)

# Use Shift+PgUp or mouse wheel to scroll back through history
```

**How it works:**
- Uses relative cursor movement (`\x1b[nA/B`) instead of absolute positioning
- Content that scrolls off-screen remains accessible via terminal scrollback
- Synchronized output (DEC 2026) prevents flickering during updates
- Overlays position correctly relative to the visible viewport

**Note:** For traditional full-screen apps where content should NOT persist after exit, use `use_alternate_buffer=True`.

## Components

### Text

```python
from pypitui import Text

text = Text("Hello World", padding_x=1, padding_y=1)
lines = text.render(width=40)
```

### Input

```python
from pypitui import Input

input_field = Input(placeholder="Enter text...")
input_field.on_submit = lambda value: print(f"Submitted: {value}")

# Handle input
input_field.handle_input("h")
input_field.handle_input("i")
input_field.handle_input("\r")  # Enter

print(input_field.get_value())  # "hi"
```

### SelectList

```python
from pypitui import SelectList, SelectItem, SelectListTheme

items = [
    SelectItem(value="a", label="Option A", description="First option"),
    SelectItem(value="b", label="Option B"),
]

theme = SelectListTheme()
select = SelectList(items, max_visible=5, theme=theme)

select.on_select = lambda item: print(f"Selected: {item.value}")
select.on_cancel = lambda: print("Cancelled")

# Navigate and select
select.handle_input("\x1b[B")  # Down
select.handle_input("\r")     # Enter
```

### Container

```python
from pypitui import Container, Text, Spacer

container = Container()
container.add_child(Text("Line 1"))
container.add_child(Spacer(1))
container.add_child(Text("Line 2"))
```

### Box

```python
from pypitui import Box, Text

box = Box(padding_x=2, padding_y=1)
box.add_child(Text("Content"))
```

### BorderedBox

**Recommended** for panels and overlays with borders. Automatically wraps content and maintains proper box shape:

```python
from pypitui import BorderedBox, Text

# BorderedBox draws borders and wraps content automatically
box = BorderedBox(
    padding_x=1,      # Horizontal padding inside borders
    padding_y=0,      # Vertical padding inside borders  
    title="My Panel"  # Optional title with separator
)
box.add_child(Text("Long content that will wrap automatically"))

# Renders as:
# ┌─────────────────────────────┐
# │ My Panel                    │
# ├─────────────────────────────┤
# │ Long content that will wrap │
# │ automatically               │
# └─────────────────────────────┘
```

> **Note:** Do not create your own box borders using Text components. Use `BorderedBox` instead - it handles content wrapping, maintains proper box shape at any width, and provides consistent styling.

## Keyboard Input

```python
from pypitui import matches_key, Key

# Check for specific keys
if matches_key(data, Key.up):
    move_up()
elif matches_key(data, Key.enter):
    submit()
elif matches_key(data, Key.ctrl("c")):
    exit()
```

**Important:** When reading input, use `read_sequence()` instead of `read()` to properly handle arrow keys and other escape sequences:

```python
# In your main loop:
data = terminal.read_sequence(timeout=0.1)
if data:
    component.handle_input(data)
```

## Overlays

```python
from pypitui import TUI, Text, OverlayOptions

# Show overlay
options = OverlayOptions(
    width="50%",
    anchor="center",
)
handle = tui.show_overlay(Text("Overlay content"), options)

# Hide overlay
handle.hide()
```

## Utilities

```python
from pypitui import visible_width, truncate_to_width, wrap_text_with_ansi

# Get visible width (ANSI codes don't count)
w = visible_width("\x1b[31mhello\x1b[0m")  # 5

# Truncate to width
truncated = truncate_to_width("hello world", 8)  # "hello..."

# Wrap text preserving ANSI codes
lines = wrap_text_with_ansi("long text here", width=10)
```

## Running Tests

```bash
uv run pytest -v
```

## Known Limitations

- **Apple Emoji Font** - The Apple Emoji Font is known to cause alignment issues in some terminals. This is a font/terminal rendering issue, not a PyPiTUI bug. If you experience misaligned emoji characters, try using a different font (e.g., Noto Color Emoji) or terminal emulator.

## License

MIT
