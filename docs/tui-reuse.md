# TUI Instance Reuse

## The Rule

**Always reuse TUI instances. Never create new TUI instances when switching screens.**

## Why This Matters

The TUI uses differential rendering to optimize screen updates. It tracks `_previous_lines` to know what was rendered in the previous frame. When you create a new TUI instance, this state is lost, causing:

- Ghost content from previous screens
- Lines not being cleared properly
- Visual artifacts

## The Wrong Way

```python
# WRONG - Creates new TUI, loses _previous_lines state
def switch_screen():
    tui = TUI(terminal)  # ❌ New instance!
    tui.add_child(...)
    return tui

# In your main loop:
tui = switch_screen()  # Old content not cleared!
```

## The Right Way

```python
# RIGHT - Reuse TUI instance, preserve _previous_lines
def switch_screen():
    tui.clear()  # ✅ Remove old children, keep state
    tui.add_child(...)  # Add new content
    # _previous_lines is preserved, old content will be cleared

# In your main loop:
switch_screen()  # Screen switches cleanly
```

## Complete Example

```python
from pypitui import TUI, Text, ProcessTerminal

class MyApp:
    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal)  # Create once
        self.show_menu()

    def _clear_screen(self):
        """Clear for new screen while preserving diff rendering state."""
        self.tui.clear()  # Remove children, keep _previous_lines

    def show_menu(self):
        """Show main menu."""
        self._clear_screen()
        self.tui.add_child(Text("Menu", 0, 0))
        # ...

    def show_detail(self):
        """Show detail screen."""
        self._clear_screen()
        self.tui.add_child(Text("Detail", 0, 0))
        # ...

    def run(self):
        self.tui.start()
        try:
            while True:
                data = self.terminal.read_sequence(timeout=0.05)
                if data:
                    self.handle_input(data)
                self.tui.request_render()
                self.tui.render_frame()
        finally:
            self.tui.stop()
```

## What `tui.clear()` Does

- Removes all child components
- Preserves `_previous_lines` (previous render state)
- Preserves `_previous_width` (terminal width tracking)

This allows the next `render_frame()` to:
1. Render new content
2. Compare with `_previous_lines`
3. Clear any lines that are no longer used

## Common Mistakes

### Mistake 1: Creating new TUI for each screen

```python
# ❌ WRONG
def show_screen_a():
    return TUI(terminal)  # New instance!

def show_screen_b():
    return TUI(terminal)  # New instance!
```

### Mistake 2: Not calling `tui.clear()`

```python
# ❌ WRONG - old children accumulate
def switch_screen():
    # Forgot to call tui.clear()!
    tui.add_child(new_content)  # Old content still there
```

### Mistake 3: Calling `tui.invalidate()` when switching

```python
# ❌ WRONG - clears _previous_lines, breaks diff rendering
def switch_screen():
    tui.clear()
    tui.invalidate()  # ❌ Don't do this!
    tui.add_child(...)
```

## Summary

| Do This | Not This |
|---------|----------|
| Create TUI once in `__init__` | Create new TUI for each screen |
| Call `tui.clear()` to switch | Create `TUI(terminal)` to switch |
| Keep `_previous_lines` intact | Call `tui.invalidate()` when switching |
| Reuse the same TUI instance | Assign `tui = TUI(...)` mid-run |
