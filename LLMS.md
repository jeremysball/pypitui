# PyPiTUI - LLM System Guide

> **Everything you need to know to use PyPiTUI effectively.**

---

## Overview

PyPiTUI is a Python TUI (Terminal User Interface) library with **differential rendering** for 60 FPS performance. It provides a component-based architecture similar to React but for terminal applications.

### Key Philosophy

- **Component-based**: Build UIs from reusable components
- **Differential rendering**: Only changed lines re-render
- **Declarative**: Describe what the UI should look like, not how to draw it
- **Zero dependencies** (except `wcwidth` for Unicode)

---

## Quick Start

```python
from pypitui import TUI, Container, Text, Input, Terminal

with Terminal() as term:
    tui = TUI(term)
    
    # Build your UI
    container = Container()
    container.add_child(Text("Hello, World!"))
    
    input_field = Input(placeholder="Type something...")
    container.add_child(input_field)
    
    # Add to TUI and render
    tui.add_child(container)
    tui.render_frame()
    
    # Handle input
    def on_input(data: bytes):
        if input_field.handle_input(data):
            tui.render_frame()  # Re-render on change
    
    term.start(on_input)
```

---

## Core Concepts

### 1. Components

Components are the building blocks. All components inherit from `Component` and implement:

```python
from pypitui import Component, Size, RenderedLine

class MyComponent(Component):
    def measure(self, available_width: int, available_height: int) -> Size:
        """Return preferred size given available space."""
        return Size(width=available_width, height=1)
    
    def render(self, width: int) -> list[RenderedLine]:
        """Return list of rendered lines."""
        return [RenderedLine(content="Hello", styles=[])]
```

### 2. The TUI Class

`TUI` is the orchestrator:

```python
tui = TUI(terminal)
tui.add_child(root_component)
tui.render_frame()  # Performs differential render
```

**Key Methods:**
- `add_child(component)` - Set root component
- `render_frame()` - Render to terminal (differential)
- `push_focus(component)` - Push component onto focus stack
- `pop_focus()` - Pop and restore previous focus
- `show_overlay(overlay)` - Show floating overlay
- `close_overlay(overlay)` - Close overlay

### 3. RenderedLine

The canonical output type:

```python
from pypitui import RenderedLine, StyleSpan

# Simple line
line = RenderedLine(content="Hello", styles=[])

# With styling
line = RenderedLine(
    content="Hello",
    styles=[StyleSpan(start=0, end=5, bold=True)]
)
```

---

## Built-in Components

### Container

Vertical stack layout (no flexbox - simple and fast):

```python
from pypitui import Container, Text

container = Container()
container.add_child(Text("First"))
container.add_child(Text("Second"))
container.add_child(Text("Third"))
# Renders:
# First
# Second
# Third
```

### Text

Display text with wrapping:

```python
from pypitui import Text

text = Text("Long text that will wrap automatically")
text.set_text("New content")  # Update content
text.get_text()  # Get current content
```

### Input

Single-line text input:

```python
from pypitui import Input

input_field = Input(
    placeholder="Enter name...",
    max_length=50
)

# Handle submission
def on_submit(value: str):
    print(f"User entered: {value}")

input_field.on_submit = on_submit

# Handle keystrokes
input_field.handle_input(b"a")  # Adds "a"
input_field.handle_input(b"\x7f")  # Backspace
input_field.handle_input(b"\r")  # Enter (triggers on_submit)
```

### SelectList

Scrollable selection list:

```python
from pypitui import SelectList, SelectItem

items = [
    SelectItem(id="1", label="Option 1"),
    SelectItem(id="2", label="Option 2"),
]

select = SelectList(items=items, max_visible=5)

# Handle selection
def on_select(item_id: str):
    print(f"Selected: {item_id}")

select.on_select = on_select

# Navigation
select.handle_input(b"\x1b[B")  # Down arrow
select.handle_input(b"\x1b[A")  # Up arrow
select.handle_input(b"\r")  # Enter (triggers on_select)
```

### BorderedBox

Decorative frame with optional title:

```python
from pypitui import BorderedBox, Text

box = BorderedBox(title="My Box")
box.add_child(Text("Content inside box"))

# Renders:
# ┌─ My Box ───────┐
# │ Content inside │
# │ box            │
# └────────────────┘
```

---

## Focus Management

### Focus Stack (LIFO)

For overlays and context switching:

```python
# Push new focus (e.g., opening modal)
tui.push_focus(modal_content)

# Pop to restore previous (e.g., closing modal)
tui.pop_focus()

# Replace current focus
tui.set_focus(new_component)
```

### Focus Lifecycle

Components can implement callbacks:

```python
class MyComponent(Component):
    def on_focus(self):
        """Called when component gains focus."""
        self._focused = True
    
    def on_blur(self):
        """Called when component loses focus."""
        self._focused = False
```

### Tab Cycling

```python
# Register components for tab order
tui.register_focusable(input1)
tui.register_focusable(input2)
tui.register_focusable(input3)

# Cycle forward
tui.cycle_focus(direction=1)

# Cycle backward
tui.cycle_focus(direction=-1)
```

---

## Overlays

### Creating Overlays

Overlays are NOT components - they wrap components:

```python
from pypitui import Overlay, OverlayPosition

# Create overlay at specific position
overlay = Overlay(
    content=my_component,
    position=OverlayPosition(row=5, col=10, width=40, height=10),
    z_index=100  # Higher = on top
)

# Show it
tui.show_overlay(overlay)

# Close it
tui.close_overlay(overlay)
```

### Position Types

```python
# Absolute position
OverlayPosition(row=5, col=10, width=40, height=10)

# Relative to bottom (row=-1 means bottom)
OverlayPosition(row=-3, col=0, width=80, height=3)

# Auto-size (width=-1 means use content size)
OverlayPosition(row=5, col=10, width=-1, height=-1)
```

### Visibility

```python
overlay.visible = False  # Hide but keep in list
overlay.visible = True   # Show again
```

---

## Terminal Abstraction

### Basic Usage

```python
from pypitui import Terminal

with Terminal() as term:
    # Terminal is in raw mode here
    term.write("Hello\r\n")
    term.move_cursor(0, 0)
    term.clear_line()
    term.hide_cursor()
    
    # Async input handling
    def on_input(data: bytes):
        if data == b"\x03":  # Ctrl+C
            term.stop()
    
    term.start(on_input)
```

### Raw Mode

`Terminal.__enter__()` puts terminal in raw mode:
- Disables line buffering
- Disables echo
- Enables reading individual keystrokes
- Automatically restored on exit

### DEC 2026 Synchronized Output

For flicker-free rendering:

```python
from pypitui.terminal import DEC_SYNC_START, DEC_SYNC_END

term.write(DEC_SYNC_START)
# ... multiple write operations ...
term.write(DEC_SYNC_END)
# Terminal updates atomically
```

---

## Input Handling

### Key Parsing

```python
from pypitui import Key, parse_key

# Parse key from bytes
key = parse_key(b"\x1b[A")  # Returns Key.UP
key = parse_key(b"a")       # Returns Key.A

# Check matches
def handle_input(data: bytes) -> bool:
    key = parse_key(data)
    
    if key == Key.UP:
        move_up()
        return True
    elif key == Key.ENTER:
        submit()
        return True
    
    return False  # Not handled
```

### Key Constants

```python
from pypitui import Key

# Arrow keys
Key.UP, Key.DOWN, Key.LEFT, Key.RIGHT

# Special keys
Key.ENTER, Key.ESC, Key.TAB, Key.BACKSPACE

# Control combinations
Key.CTRL_C, Key.CTRL_D, Key.CTRL_L

# Function keys
Key.F1, Key.F2, ... Key.F12
```

### Mouse Events

```python
from pypitui import MouseEvent, parse_mouse

# Enable mouse tracking first
term.write("\x1b[?1006h\x1b[?1000h")

# Parse mouse events
event = parse_mouse(b"\x1b[<0;10;5M")  # Click at col 10, row 5
# event = MouseEvent(x=9, y=4, button=0, pressed=True)
```

---

## Differential Rendering

### How It Works

PyPiTUI tracks previous frame and only outputs changes:

```python
# Frame 1
lines = ["Hello", "World"]
tui.render(lines)  # Full output

# Frame 2 - only first line changed
lines = ["Hi", "World"]
tui.render(lines)  # Only "Hi" output, "World" skipped
```

### Performance

- **50-line render**: <16ms (60 FPS target)
- **Escape sequence efficiency**: ~80% reduction vs full redraw
- **Append optimization**: Uses `\r\n` instead of cursor positioning

### Scrollback Handling

```python
# If edit is in scrollback (above viewport), triggers full redraw
# Because terminal history is immutable - can't reach scrolled-off content
```

---

## Wide Character Support

### Utilities

```python
from pypitui import wcwidth, truncate_to_width, slice_by_width

# Measure display width
wcwidth("a")     # Returns 1
wcwidth("中")    # Returns 2 (CJK)
wcwidth("😀")    # Returns 2 (emoji)

# Truncate without splitting
truncate_to_width("Hello World", 8)  # "Hello Wo"
truncate_to_width("中文测试", 3)     # "中" (respects wide chars)

# Extract by display position
slice_by_width("Hello World", 2, 7)  # "llo W"
```

### In Components

Components automatically handle wide characters via `truncate_to_width()`.

---

## Common Patterns

### Modal Dialog

```python
from pypitui import Container, Text, Input, BorderedBox, Overlay, OverlayPosition

def show_modal(tui: TUI, title: str, on_submit: Callable):
    # Create modal content
    modal = Container()
    box = BorderedBox(title=title)
    user_input = Input(placeholder="Enter value...")
    
    def handle_submit(value: str):
        on_submit(value)
        tui.close_overlay(overlay)
        tui.pop_focus()  # Restore previous focus
    
    user_input.on_submit = handle_submit
    box.add_child(user_input)
    modal.add_child(box)
    
    # Show as overlay
    overlay = Overlay(
        content=modal,
        position=OverlayPosition(row=5, col=10, width=60, height=5),
        z_index=100
    )
    
    tui.show_overlay(overlay)
    tui.push_focus(user_input)  # Focus the input
```

### Form with Multiple Inputs

```python
from pypitui import Container, Input, BorderedBox

class Form(Container):
    def __init__(self):
        super().__init__()
        
        # Name field
        name_box = BorderedBox(title="Name")
        self.name_input = Input(placeholder="Enter name...")
        name_box.add_child(self.name_input)
        self.add_child(name_box)
        
        # Email field
        email_box = BorderedBox(title="Email")
        self.email_input = Input(placeholder="Enter email...")
        email_box.add_child(self.email_input)
        self.add_child(email_box)
        
        # Register for tab cycling
        self._register_focusables()
    
    def _register_focusables(self):
        # Called by parent TUI
        pass
    
    def get_values(self) -> dict[str, str]:
        return {
            "name": self.name_input.get_text(),
            "email": self.email_input.get_text(),
        }
```

### Toast Notifications

```python
from pypitui import Container, Text, Overlay, OverlayPosition

class ToastManager:
    def __init__(self, tui: TUI):
        self.tui = tui
        self._current_toast: Overlay | None = None
    
    def show(self, message: str, duration: float = 3.0):
        # Close existing toast
        if self._current_toast:
            self.tui.close_overlay(self._current_toast)
        
        # Create toast
        container = Container()
        container.add_child(Text(message))
        
        overlay = Overlay(
            content=container,
            position=OverlayPosition(row=-2, col=0),  # 2 lines from bottom
            z_index=1000
        )
        
        self.tui.show_overlay(overlay)
        self._current_toast = overlay
        
        # Auto-close
        import threading
        threading.Timer(duration, lambda: self._close(overlay)).start()
    
    def _close(self, overlay: Overlay):
        if self._current_toast == overlay:
            self.tui.close_overlay(overlay)
            self._current_toast = None
```

### Chat Interface

```python
class ChatInterface(Container):
    def __init__(self):
        super().__init__()
        self.messages: list[BorderedBox] = []
        self.input_field = Input(placeholder="Type message...")
        
    def add_message(self, role: str, content: str):
        """Add a message to the chat."""
        box = BorderedBox(title=role.capitalize())
        box.add_child(Text(content))
        
        self.messages.append(box)
        self.add_child(box)
        
        # Invalidate to trigger re-render
        self.invalidate()
    
    def clear(self):
        """Clear all messages."""
        self.clear_children()
        self.messages.clear()
        self.invalidate()
```

---

## Testing

### MockTerminal

```python
from pypitui import MockTerminal

def test_component_render():
    term = MockTerminal(width=80, height=24)
    tui = TUI(term)
    
    component = MyComponent()
    tui.add_child(component)
    tui.render_frame()
    
    # Check escape sequences
    assert term.move_cursor_count == expected
    assert term.write_count == expected
```

### Component Testing

```python
def test_input_handles_typing():
    from pypitui import Input
    
    input_field = Input()
    
    # Type "hello"
    for char in "hello":
        input_field.handle_input(char.encode())
    
    assert input_field.get_text() == "hello"
```

---

## Error Handling

### Line Overflow

```python
from pypitui import TUI, LineOverflowError

try:
    tui.render_frame()
except LineOverflowError as e:
    # Content exceeded terminal width
    print(f"Line too long: {e}")
```

### Terminal Errors

```python
from pypitui import Terminal

with Terminal() as term:
    try:
        term.write(data)
    except IOError:
        # Terminal disconnected
        term.stop()
```

---

## Best Practices

1. **Always use context manager for Terminal**
   ```python
   with Terminal() as term:
       # Your code
   # Raw mode automatically restored
   ```

2. **Call invalidate() when component state changes**
   ```python
   def set_value(self, value: str):
       self._value = value
       self.invalidate()  # Marks for re-render
   ```

3. **Handle input at TUI level, not component level**
   ```python
   def on_input(data: bytes):
       if tui._focused:
           if tui._focused.handle_input(data):
               tui.render_frame()
   ```

4. **Use overlays for modals, not child components**
   ```python
   # Good: Overlay for modal
   tui.show_overlay(Overlay(content=modal, ...))
   
   # Bad: Adding modal as child
   tui.add_child(modal)  # Doesn't float above content
   ```

5. **Register focusables for tab navigation**
   ```python
   for component in [input1, input2, input3]:
       tui.register_focusable(component)
   ```

---

## API Reference

See `src/pypitui/__init__.py` for complete public API exports.

### Core Classes
- `TUI` - Main orchestrator
- `Component` - Base class for all components
- `Container` - Vertical stack layout
- `Text` - Text display with wrapping
- `Input` - Single-line text input
- `SelectList` - Scrollable selection list
- `BorderedBox` - Decorative frame
- `Overlay` - Floating viewport-relative content
- `Terminal` - Terminal abstraction

### Data Structures
- `Size` - Width/height dimensions
- `Rect` - Position and dimensions
- `RenderedLine` - Output line with styles
- `StyleSpan` - Styled text segment
- `SelectItem` - Item for SelectList
- `OverlayPosition` - Position specification

### Input
- `Key` - Key constants (UP, DOWN, ENTER, etc.)
- `parse_key()` - Parse bytes to Key
- `matches_key()` - Check if data matches key
- `MouseEvent` - Mouse event data
- `parse_mouse()` - Parse mouse escape sequences

### Utilities
- `wcwidth()` - Display width of character
- `truncate_to_width()` - Truncate respecting wide chars
- `slice_by_width()` - Extract substring by display width
- `detect_color_support()` - Terminal color capability

---

## Examples

See `examples/` directory:
- `demo.py` - Full component showcase
- `inputs.py` - Input handling demo
- `overlays.py` - Modal dialog demo

---

## Migration from Other Libraries

### From Rich

```python
# Rich
from rich.console import Console
console = Console()
console.print("[bold]Hello[/bold]")

# PyPiTUI
from pypitui import Text, StyleSpan
text = Text("Hello")
text.styles = [StyleSpan(0, 5, bold=True)]
```

### From prompt-toolkit

```python
# prompt-toolkit
from prompt_toolkit import Application
app = Application(layout=..., key_bindings=...)
app.run()

# PyPiTUI
with Terminal() as term:
    tui = TUI(term)
    # ... setup components ...
    term.start(on_input)
```

---

## Contributing

1. All code must pass `ruff check`
2. All code must pass `mypy --strict`
3. All tests must pass (`pytest`)
4. 80%+ coverage required

---

## License

MIT License - See LICENSE file
