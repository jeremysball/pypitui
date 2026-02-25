# PyPiTUI - Terminal UI Library for Python

**A Python terminal UI library with differential rendering, component-based architecture, and Rich integration.**

---

## Quick Start

```python
from pypitui import TUI, Text, Spacer, ProcessTerminal, Key, matches_key

terminal = ProcessTerminal()
tui = TUI(terminal)
tui.add_child(Text("Hello, World!"))
tui.add_child(Spacer(1))

tui.start()
try:
    while True:
        data = terminal.read_sequence(timeout=0.05)
        if data:
            if matches_key(data, Key.escape):
                break
            tui.handle_input(data)
        tui.request_render()
        tui.render_frame()
finally:
    tui.stop()
```

---

## Core Concepts

### TUI (Terminal User Interface)

Main class managing terminal state, input handling, and differential rendering.

```python
tui = TUI(
    terminal,
    show_hardware_cursor=False,  # Show cursor for IME (default: False)
    clear_on_shrink=True,        # Clear old lines when content shrinks (default: True)
    use_alternate_buffer=False,  # Use alternate screen buffer (default: False)
)
```

**CRITICAL: Reuse TUI Instances**
```python
# WRONG - loses _previous_lines, causes ghost content
self.tui = TUI(terminal)
self.tui.add_child(Text("New screen"))

# RIGHT - reuse TUI, preserves differential rendering state
self.tui.clear()
self.tui.add_child(Text("New screen"))
```

### Component Model

All UI elements inherit from `Component`:
- `render(width: int) -> list[str]` - Render to lines
- `invalidate()` - Clear render cache
- `handle_input(data: str)` - Optional input handler
- `wants_key_release` - Set `True` to receive Kitty key release events

### Differential Rendering

TUI only updates changed lines. Creating new TUI instances loses `_previous_lines` state needed for clearing old content.

---

## Components

### Text

Multi-line text with word wrapping.

```python
text = Text("Hello!", padding_x=1, padding_y=1)
text.set_text("New content")
text.set_custom_bg_fn(lambda line: f"\x1b[44m{line}\x1b[0m")  # Blue bg
```

**Word Wrapping:** Uses `wrap_text_with_ansi()` which splits on spaces. Use non-breaking spaces (`\xa0`) for pre-formatted content.

### Box

Container with padding and optional background.

```python
box = Box(padding_x=2, padding_y=1)
box.add_child(Text("Content"))
box.set_bg_fn(lambda line: f"\x1b[44m{line}\x1b[0m")
box.clear()  # Remove all children
```

### BorderedBox

Box with borders, wraps content to fit.

```python
box = BorderedBox(padding_x=1, padding_y=0, min_width=10, max_width=40, title="Panel")
box.add_child(Text("Content"))
box.set_title("Plain Title")
box.set_rich_title("[bold cyan]Rich Title[/bold cyan]")  # Requires pypitui[rich]
```

### Spacer

Empty vertical space.

```python
spacer = Spacer(height=2)
```

### Container

Groups components vertically.

```python
container = Container()
container.add_child(Text("Line 1"))
container.add_child(Text("Line 2"))
container.clear()
```

### SelectList

Interactive selection list with filtering.

```python
from pypitui import SelectList, SelectItem, SelectListTheme

items = [
    SelectItem("val1", "Label 1", "Description 1"),
    SelectItem("val2", "Label 2", "Description 2"),
]

theme = SelectListTheme(
    selected_prefix=lambda s: f"\x1b[32m{s}\x1b[0m",
    selected_text=lambda s: f"\x1b[1m{s}\x1b[0m",
    description=lambda s: f"\x1b[90m{s}\x1b[0m",
)

select = SelectList(items, max_visible=5, theme=theme)
select.on_select = lambda item: print(f"Selected: {item.value}")
select.on_cancel = lambda: print("Cancelled")
select.on_selection_change = lambda item: print(f"Hover: {item.label}")

tui.set_focus(select)
```

**Key Bindings:** ↑/↓ navigate, Enter select, Escape cancel/clear filter, Backspace delete filter, type to filter.

### Input

Text input with cursor.

```python
input_field = Input(placeholder="Enter text...", password=False)
input_field.on_submit = lambda v: print(f"Submitted: {v}")
input_field.on_cancel = lambda: print("Cancelled")

value = input_field.get_value()
input_field.set_value("Initial")

tui.set_focus(input_field)
```

**Key Bindings:** ←/→ move, Home/Ctrl+A start, End/Ctrl+E end, Backspace/Delete delete, Ctrl+U delete to start, Ctrl+K delete to end, Enter submit, Escape cancel.

---

## Overlays

Floating panels on top of content.

```python
from pypitui import OverlayOptions, OverlayMargin

box = BorderedBox(title="Dialog")
box.add_child(Text("Press ESC to close"))

options = OverlayOptions(
    width=40,              # int or "50%"
    min_width=20,
    max_height=10,
    anchor="center",       # "center", "top", "bottom", "top-left", etc.
    offset_x=0,
    offset_y=0,
    margin=2,              # int or OverlayMargin(top=1, bottom=1, left=2, right=2)
)

handle = tui.show_overlay(box, options)
handle.hide()              # Permanently remove
handle.set_hidden(True)    # Temporarily hide
handle.is_hidden()         # Check visibility

tui.hide_overlay()         # Close top overlay
tui.has_overlay()          # Check if any visible
```

---

## Keyboard Input

### Key Matching

```python
from pypitui import Key, matches_key, parse_key

if matches_key(data, Key.escape): ...
if matches_key(data, Key.enter): ...
if matches_key(data, Key.up): ...
if matches_key(data, Key.ctrl("c")): ...
if matches_key(data, Key.ctrl_shift("p")): ...
if matches_key(data, Key.alt("enter")): ...

key_id = parse_key(data)  # Returns "ctrl+c", "escape", "a", etc.
```

### Available Keys

```python
# Special
Key.escape, Key.esc, Key.enter, Key.return_, Key.tab, Key.space
Key.backspace, Key.delete, Key.insert, Key.clear
Key.home, Key.end, Key.page_up, Key.page_down
Key.up, Key.down, Key.left, Key.right

# Function keys
Key.f1 through Key.f12

# Modifier methods
Key.ctrl("a"), Key.shift("a"), Key.alt("a")
Key.ctrl_shift("a"), Key.ctrl_alt("a"), Key.shift_alt("a")
```

### Kitty Keyboard Protocol

For key release/repeat events (Kitty terminal only):

```python
from pypitui.keys import set_kitty_protocol_active, is_key_release, is_key_repeat

set_kitty_protocol_active(True)  # Enable after setting up terminal

# In component:
@property
def wants_key_release(self) -> bool:
    return True

def handle_input(self, data):
    if is_key_release(data):
        return  # Ignore releases
```

---

## Terminal

### ProcessTerminal

Real terminal for applications.

```python
terminal = ProcessTerminal()
terminal.write("\x1b[31mRed text\x1b[0m")
char = terminal.read(timeout=0.0)
sequence = terminal.read_sequence(timeout=0.1)
cols, rows = terminal.get_size()
terminal.move_cursor(row, col)
terminal.hide_cursor() / terminal.show_cursor()
terminal.clear()
terminal.enter_alternate_screen() / terminal.exit_alternate_screen()
terminal.set_raw_mode() / terminal.restore_mode()
```

### MockTerminal

For testing.

```python
terminal = MockTerminal(cols=80, rows=24)
terminal.queue_input("h")
terminal.queue_input_sequence("\x1b[A")  # Up arrow
output = terminal.get_output()
```

---

## Utilities

```python
from pypitui import visible_width, truncate_to_width, wrap_text_with_ansi, slice_by_column
from pypitui import get_terminal_size
from pypitui.utils import strip_ansi

width = visible_width("\x1b[31mHello\x1b[0m")  # 5
truncated = truncate_to_width("Long text", 10, ellipsis="...", pad=False)
lines = wrap_text_with_ansi("Text with \x1b[31mcolors\x1b[0m", width=20)
slice = slice_by_column(line, start_col=5, length=10)
cols, rows = get_terminal_size()
clean = strip_ansi("\x1b[31mText\x1b[0m")  # "Text"
```

---

## Rich Integration (Optional)

Install: `pip install pypitui[rich]`

```python
from pypitui.rich_components import RichText, Markdown, RichTable, rich_to_ansi, rich_color_to_ansi

text = RichText("[bold cyan]Hello[/bold cyan]!")
md = Markdown("# Heading\n\n**Bold** text", code_theme="monokai")
table = RichTable(title="My Table")
table.add_column("Name", style="cyan")
table.add_row("Item 1", "100")

ansi = rich_to_ansi("[bold cyan]Hello[/bold cyan]")
code = rich_color_to_ansi("bright_cyan")  # "\x1b[96m"
```

---

## Main Loop Patterns

### Manual Loop

```python
tui.start()
try:
    while running:
        data = terminal.read_sequence(timeout=0.05)
        if data:
            if matches_key(data, Key.escape):
                running = False
            else:
                tui.handle_input(data)
        tui.request_render()
        tui.render_frame()
finally:
    tui.stop()
```

### Built-in Loop

```python
tui.run()  # Handles start/stop, input, and ~60fps rendering
```

### With Animation

```python
last_time = time.time()

tui.start()
try:
    while running:
        data = terminal.read_sequence(timeout=0.001)
        if data:
            handle_input(data)
        
        now = time.time()
        dt = now - last_time
        last_time = now
        update_animation(dt)
        
        tui.request_render()
        tui.render_frame()
finally:
    tui.stop()
```

### Input Listeners

```python
def intercept_input(data: str) -> dict | None:
    if matches_key(data, Key.ctrl("c")):
        return {"consume": True}  # Block from focused component
    return None

remove = tui.add_input_listener(intercept_input)
remove()  # Unregister
```

---

## Common Patterns

### Screen Switching

```python
class App:
    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal)
        self.build_menu()
    
    def build_menu(self):
        self.tui.clear()
        self.tui.add_child(Text("Main Menu"))
    
    def build_settings(self):
        self.tui.clear()
        self.tui.add_child(Text("Settings"))
```

### Terminal Resize

```python
def update_size(self):
    term_width, term_height = self.terminal.get_size()
    self.width = max(40, term_width)
    self.height = max(10, term_height - 3)  # Reserve UI lines
```

---

## Edge Cases

| Issue | Solution |
|-------|----------|
| Ghost content | Reuse TUI instance, call `tui.clear()` |
| Text breaks pre-formatted lines | Use `\xa0` (non-breaking space) |
| First frame huge delta time | Skip first frame or initialize `_last_time` |
| Resize loops | Use consistent min values everywhere |
| ANSI codes count in `len()` | Use `visible_width()` for layout |

---

## ANSI Colors

```python
# Basic: 30-37 (foreground), 40-47 (background)
"\x1b[31m"  # Red    "\x1b[32m"  # Green
"\x1b[33m"  # Yellow "\x1b[34m"  # Blue
"\x1b[35m"  # Magenta "\x1b[36m" # Cyan
"\x1b[37m"  # White

# Bright: 90-97 (foreground), 100-107 (background)
"\x1b[90m"  # Gray   "\x1b[91m"  # Bright Red
"\x1b[92m"  # Bright Green

# Styles
"\x1b[1m"   # Bold    "\x1b[4m"  # Underline
"\x1b[7m"   # Reverse  "\x1b[0m"  # Reset
```

---

## API Reference

### Imports

```python
from pypitui import (
    # Core
    TUI, Component, Container, Focusable,
    OverlayOptions, OverlayMargin, OverlayHandle,
    CURSOR_MARKER, is_focusable,
    
    # Components
    Text, Box, BorderedBox, Spacer,
    SelectList, SelectItem, SelectListTheme, Input,
    
    # Keys
    Key, matches_key, parse_key,
    
    # Terminal
    Terminal, ProcessTerminal, MockTerminal,
    
    # Utils
    visible_width, truncate_to_width, wrap_text_with_ansi,
    slice_by_column, get_terminal_size,
)
```

### TUI Methods

| Method | Description |
|--------|-------------|
| `add_child(c)` / `remove_child(c)` / `clear()` | Manage children |
| `set_focus(component)` | Set focused component |
| `show_overlay(c, opts)` → `OverlayHandle` | Show overlay |
| `hide_overlay()` / `has_overlay()` | Manage overlays |
| `handle_input(data)` | Forward input to focused component |
| `add_input_listener(fn)` → `remove_fn` | Intercept input |
| `request_render(force=False)` | Request next frame render |
| `render_frame()` | Render current frame |
| `run()` | Built-in main loop |
| `start()` / `stop()` | Enter/exit TUI mode |

### Component Interface

| Method | Description |
|--------|-------------|
| `render(width) -> list[str]` | Render to lines |
| `invalidate()` | Clear cache |
| `handle_input(data)` | Handle input (optional) |
| `wants_key_release` | Receive Kitty release events |

### Focusable Interface

| Property | Description |
|----------|-------------|
| `focused` | Get/set focus state |

---

## Installation

```bash
pip install pypitui
pip install pypitui[rich]  # With Rich integration
```

## License

MIT
