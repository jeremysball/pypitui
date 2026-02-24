# PyPiTUI Agent Guidelines

## Generating Type Stubs

When adding type stubs to this library, use `stubgen` from mypy instead of writing them manually:

```bash
uv run stubgen src/pypitui -o src/pypitui/stubs
```

Then refine the generated stubs as needed. Manual stub creation is error-prone and may miss edge cases that stubgen handles automatically.

## Critical: TUI Instance Reuse

**Never create new TUI instances when switching screens.** Always reuse the same TUI instance.

### Correct Pattern
```python
def switch_screen(self):
    self.tui.clear()  # Remove children, preserve _previous_lines
    self.tui.add_child(Text("New content", 0, 0))
```

### Wrong Pattern
```python
def switch_screen(self):
    self.tui = TUI(terminal)  # ❌ Loses _previous_lines, breaks clearing
    self.tui.add_child(Text("New content", 0, 0))
```

### Why This Matters
The TUI uses `_previous_lines` for differential rendering. Creating a new TUI loses this state, causing ghost content and uncleared lines.

### Reference
See `examples/demo.py` for the correct implementation using `_clear_screen()`.
