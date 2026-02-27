# PyPiTUI - Quick Reference

**Terminal UI library with differential rendering and component-based architecture.**

---

## Quick Reference (Common Patterns)

```python
from pypitui import (
    TUI, Container, Text, Input, SelectList, SelectItem,
    ProcessTerminal, Key, matches_key, parse_key,
    EVENT_PRESS, EVENT_RELEASE,
)

# Setup
terminal = ProcessTerminal()
tui = TUI(terminal)
root = Container()
tui.add_child(root)

# Screen switching (REUSE TUI - don't create new one)
root.children.clear()  # Clear container, not TUI
root.add_child(Text("New Screen"))

# Keyboard handling
data = terminal.read_sequence(timeout=0.05)
key_id, event_type = parse_key(data)  # Returns tuple!
if matches_key(data, Key.ctrl("c")): ...
if event_type == EVENT_RELEASE: ...  # Kitty protocol only

# Input with validation
inp = Input(placeholder="Name", max_length=50)
inp.on_submit = lambda v: print(f"Hello {v}")

# Selection list
items = [SelectItem("a", "Option A"), SelectItem("b", "Option B")]
select = SelectList(items, max_visible=5, theme=default_theme)
select.on_select = lambda item: print(item.value)

# Main loop
tui.run()  # Built-in ~60fps loop
```

---

# Full Guide

## Core Concepts

### TUI Instance Reuse (CRITICAL)

**WRONG** - Creates ghost content:
```python
self.tui = TUI(terminal)  # Loses _previous_lines state
self.tui.add_child(Text("Screen"))
```

**RIGHT** - Reuse TUI instance:
```python
self.root = Container()
self.tui.add_child(self.root)

# Switch screens:
self.root.children.clear()  # Clear container
self.root.add_child(Text("New Screen"))
```

### Component Model

All components inherit from `Component`:
- `render(width: int) -> list[str]` - Render to lines
- `invalidate()` - Clear render cache
- `handle_input(data: str)` - Optional input handler
- `wants_key_release: bool` - Set True for Kitty release events

### Differential Rendering

TUI only updates changed lines. The `_previous_lines` state enables efficient updates. Creating new TUI instances loses this state.

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

Box with borders and optional title.

```python
box = BorderedBox(
    padding_x=1, padding_y=0,
    min_width=10, max_width=40,
    title="Panel"
)
box.add_child(Text("Content"))
box.set_title("Plain Title")
box.set_rich_title("[bold cyan]Rich Title[/bold cyan]")  # Requires rich
```

### Spacer

Empty vertical space.

```python
spacer = Spacer(height=2)
```

### Container

Groups components vertically. Use for screen switching.

```python
container = Container()
container.add_child(Text("Line 1"))
container.add_child(Text("Line 2"))
container.clear()  # Remove all children
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

Text input with cursor and optional max length.

```python
input_field = Input(
    placeholder="Enter text...",
    password=False,
    max_length=100  # Optional validation
)
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
from pypitui import Key, matches_key, parse_key, EVENT_PRESS, EVENT_RELEASE

if matches_key(data, Key.escape): ...
if matches_key(data, Key.enter): ...
if matches_key(data, Key.up): ...
if matches_key(data, Key.ctrl("c")): ...
if matches_key(data, Key.ctrl_shift("p")): ...
if matches_key(data, Key.alt("enter")): ...

# Parse returns tuple: (key_id, event_type)
key_id, event_type = parse_key(data)
if event_type == EVENT_RELEASE:
    return  # Ignore key releases
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
from pypitui.keys import set_kitty_protocol_active
from pypitui import EVENT_PRESS, EVENT_REPEAT, EVENT_RELEASE

set_kitty_protocol_active(True)  # Enable after terminal setup

# In component:
@property
def wants_key_release(self) -> bool:
    return True

def handle_input(self, data):
    key_id, event_type = parse_key(data)
    if event_type == EVENT_RELEASE:
        return  # Ignore releases
    if event_type == EVENT_REPEAT:
        pass  # Handle repeat
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
from pypitui import (
    visible_width, truncate_to_width, wrap_text_with_ansi,
    slice_by_column, get_terminal_size
)
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
from pypitui.rich_components import (
    RichText, Markdown, RichTable,
    rich_to_ansi, rich_color_to_ansi
)

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
from pypitui import FRAME_TIME  # ~60fps target

tui.start()
try:
    while running:
        data = terminal.read_sequence(timeout=0.001)
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
import time

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
        self.root = Container()
        self.tui.add_child(self.root)
        self.build_menu()
    
    def build_menu(self):
        self.root.children.clear()  # Clear container, NOT tui
        self.root.add_child(Text("Main Menu"))
    
    def build_settings(self):
        self.root.children.clear()
        self.root.add_child(Text("Settings"))
```

### Terminal Resize

```python
def update_size(self):
    term_width, term_height = self.terminal.get_size()
    self.width = max(40, term_width)
    self.height = max(10, term_height - 3)  # Reserve UI lines
```

---

## Scrollback Mechanics and Renderer Internals

### How Scrollback Works

The TUI maintains a virtual canvas that can exceed terminal height. When content grows beyond the visible area, older lines flow into the terminal's native scrollback buffer (accessible via Shift+PgUp).

**Key State Variables** (from `tui.py`):

```python
self._max_lines_rendered: int = 0  # Maximum lines ever rendered
self._previous_lines: list[str] = []  # Last frame's rendered lines
self._hardware_cursor_row: int = 0  # Virtual cursor position
```

**First Visible Row Calculation**:

```python
def _calculate_first_visible_row(self, term_height: int) -> int:
    return max(0, self._max_lines_rendered - term_height)
```

Example: If `_max_lines_rendered=100` and `term_height=24`:
- Returns 76 (lines 0-75 in scrollback, lines 76-99 visible)

**Content Growth** (`_handle_content_growth`):

When content grows from 20 to 25 lines in a 24-row terminal:
1. Detects `current_count > previous_count`
2. Emits newlines to scroll the terminal
3. Updates `_hardware_cursor_row` to bottom

**Scrollback Immutability**:

Lines in scrollback cannot be updated after scrolling. From `test_scrollback.py`:

```python
def test_scrollback_lines_frozen(self):
    # Modify line 2 (in scrollback)
    # Assert: modification does NOT appear in output
    assert "MODIFIED Line 2" not in output
```

### Differential Rendering

The renderer compares current frame against `_previous_lines` to update only changed lines.

**Line Comparison** (`_render_changed_lines`):

```python
# For content fitting in terminal:
for i, line in enumerate(lines):
    if i >= len(prev) or prev[i] != line:
        buffer += self._move_cursor_relative(i)
        buffer += "\r\x1b[2K"  # Clear line
        buffer += line

# For content exceeding terminal:
first_visible = current_count - term_height
for screen_row in range(term_height):
    content_row = first_visible + screen_row
    if content_row >= len(prev) or prev[content_row] != lines[content_row]:
        # Update only visible portion
```

**Shrink Handling**:

When content shrinks (`clear_on_shrink=True`):
```python
if current_count < previous_count:
    for i in range(current_count, previous_count):
        buffer += self._move_cursor_relative(i)
        buffer += "\r\x1b[2K"  # Clear orphaned lines
```

### Relative Cursor Movement

The renderer uses relative positioning (`\x1b[nA`/`\x1b[nB`) instead of absolute (`\x1b[row;colH`). This allows content to flow into scrollback.

**Movement Logic** (`_move_cursor_relative`):

```python
def _move_cursor_relative(self, target_row: int) -> str:
    delta = target_row - self._hardware_cursor_row
    if delta == 0:
        return ""
    if delta > 0:
        self._hardware_cursor_row = target_row
        return self.terminal.move_cursor_down(delta)  # "\x1b[nB"
    else:
        self._hardware_cursor_row = target_row
        return self.terminal.move_cursor_up(-delta)   # "\x1b[nA"
```

**Terminal Methods** (`terminal.py`):

```python
def move_cursor_up(self, n: int = 1) -> str:
    if n <= 0:
        return ""
    return f"\x1b[{n}A"

def move_cursor_down(self, n: int = 1) -> str:
    if n <= 0:
        return ""
    return f"\x1b[{n}B"
```

### Synchronized Output (DEC 2026)

Prevents flickering by buffering output until frame is complete.

**Sequences**:

```python
def _begin_sync(self) -> str:
    return "\x1b[?2026h"  # Begin buffered mode

def _end_sync(self) -> str:
    return "\x1b[?2026l"  # Flush buffer
```

**Frame Structure** (`render_frame`):

```python
buffer = self._begin_sync()
# ... render all changes ...
buffer += self._end_sync()
self.terminal.write(buffer)
```

Terminals without DEC 2026 support ignore these sequences (graceful degradation).

### Line Reset Sequence

Each rendered line ends with a reset sequence to prevent style bleeding:

```python
_SEGMENT_RESET = "\x1b[0m\x1b[K\x1b]8;;\x07"
# \x1b[0m    - Reset all attributes
# \x1b[K     - Clear to end of line
# \x1b]8;;\x07 - End hyperlink
```

Applied in `_apply_line_resets`:

```python
def _apply_line_resets(self, lines: list[str]) -> list[str]:
    return [line + self._SEGMENT_RESET for line in lines]
```

### Resize Handling

On terminal resize, clears both screen and scrollback to prevent corrupted output:

```python
def _check_resize(self, term_width: int, term_height: int) -> None:
    if (term_width, term_height) != self._last_terminal_size:
        self._previous_lines = []
        self._hardware_cursor_row = -1
        self.terminal.write("\x1b[2J\x1b[3J\x1b[H")  # Clear screen + scrollback
        self.invalidate()
```

### Hardware Cursor Positioning

For IME candidate window positioning. Focusable components emit `CURSOR_MARKER` (`"\x1b_pi:c\x07"`) in rendered output.

**Extraction** (`_extract_cursor_position`):

```python
# Scan from bottom up (viewport area only)
start_line = max(0, len(lines) - height)
for i in range(len(lines) - 1, start_line - 1, -1):
    pos = lines[i].find(CURSOR_MARKER)
    if pos != -1:
        col = visible_width(lines[i][:pos])
        return (i, col)
```

**Positioning** (`_position_hardware_cursor_relative`):

```python
self.terminal.write(self._move_cursor_relative(row))
self.terminal.write(f"\r\x1b[{col}C")  # Move to column
self.terminal.show_cursor()
```

### Frame Rendering Flow

Complete `render_frame()` sequence:

1. Check `_force_full_redraw` → clear screen if needed
2. `_check_resize()` → invalidate on size change
3. `render(term_width)` → get base lines from children
4. `_calculate_first_visible_row()` → determine scrollback offset
5. `_composite_overlays()` → overlay content onto base
6. `_apply_line_resets()` → append reset to each line
7. `_extract_cursor_position()` → find and strip cursor marker
8. `_begin_sync()` → start buffered output
9. `_handle_content_growth()` → emit newlines if content grew
10. `_render_changed_lines()` → differential update
11. `_end_sync()` → flush buffered output
12. `_position_hardware_cursor_relative()` → place IME cursor

---

## Edge Cases

| Issue | Solution |
|-------|----------|
| Ghost content | Reuse TUI instance, use `container.children.clear()` |
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
    CURSOR_MARKER, is_focusable, FRAME_TIME,
    
    # Components
    Text, Box, BorderedBox, Spacer,
    SelectList, SelectItem, SelectListTheme, Input,
    
    # Keys
    Key, matches_key, parse_key,
    EVENT_PRESS, EVENT_RELEASE, EVENT_REPEAT,
    
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
| `add_child(c)` / `remove_child(c)` | Manage children |
| `set_focus(component)` | Set focused component |
| `show_overlay(c, opts)` → `OverlayHandle` | Show overlay |
| `hide_overlay()` / `has_overlay()` | Manage overlays |
| `handle_input(data)` | Forward input to focused component |
| `add_input_listener(fn)` → `remove_fn` | Intercept input |
| `request_render(force=False)` | Request next frame render |
| `render_frame()` | Render current frame |
| `run()` | Built-in main loop (~60fps) |
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

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `CURSOR_MARKER` | `"\x1b_pi:c\x07"` | Hardware cursor position |
| `FRAME_TIME` | `0.016` | ~60fps target (seconds) |
| `EVENT_PRESS` | `"press"` | Key press event |
| `EVENT_RELEASE` | `"release"` | Key release event |
| `EVENT_REPEAT` | `"repeat"` | Key repeat event |
| `ANSI_RESET` | `"\x1b[0m"` | ANSI reset code |

---

## Installation

```bash
pip install pypitui
pip install pypitui[rich]  # With Rich integration
```

## License

MIT
