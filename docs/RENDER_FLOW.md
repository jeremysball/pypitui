# PyPiTUI Rendering Control Flow

Complete control flow diagram of the pypitui rendering process.

## TUI Main Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TUI MAIN LOOP                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  while running:                                                              │
│      1. Read terminal input (terminal.read_sequence)                        │
│      2. Handle input (tui.handle_input → component.handle_input)            │
│      3. tui.request_render()                                                │
│      4. tui.render_frame()                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## render_frame() Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      render_frame() FLOW                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
            ┌─────────────────────────────────────────┐
            │  base_lines = self.render(term_width)   │
            └─────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────┐
        │  FOR EACH child in children:                            │
        │    component_lines = child.render(width)                 │
        │    lines.extend(component_lines)                          │
        └─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│    lines = _composite_overlays(base_lines, ...)                             │
│    lines = _apply_line_resets(lines)                                         │
│    cursor_pos = _extract_cursor_position(lines)                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              DIFFERENTIAL RENDERING: _render_changed_lines()                │
│                                                                              │
│    Compare current lines vs _previous_lines                                  │
│    Update only changed lines                                                 │
│    Clear orphaned lines if content shrank                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│    buffer = _begin_sync() + changes + _end_sync()                           │
│    terminal.write(buffer)                                                    │
│    _previous_lines = lines  (save for next frame)                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Differential Rendering

The renderer compares the current frame against `_previous_lines` to update only changed lines. No explicit invalidation is needed - components simply update their state and the differential renderer detects changes automatically.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              DIFFERENTIAL RENDERING: _render_changed_lines()                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            content > term_height?          content <= term_height?
                    │                               │
                    ▼                               ▼
        ┌───────────────────────┐       ┌───────────────────────────┐
        │ Scrollback handling   │       │ Simple comparison loop:   │
        │ (emit newlines for    │       │                           │
        │  new scrollback)      │       │ for i, line in enumerate(lines):
        │                       │       │     if i >= len(_previous_lines)
        │ Render visible portion│       │        or _previous_lines[i] != line:
        └───────────────────────┘       │         clear line i      │
                                        │         write new line    │
                                        │                           │
                                        │ if _clear_on_shrink and   │
                                        │    current < previous:    │
                                        │    for i in range(current,│
                                        │            previous):     │
                                        │        clear line i ◄─────┼── SHRINK HANDLING
                                        └───────────────────────────┘
```

## Layout Example

```python
# Vertical stack layout (top to bottom)
self.tui.add_child(self.conversation)      # Messages (flex)
self.tui.add_child(self.status_line)       # Status bar
self.tui.add_child(self.completion_menu)   # Completion menu (0 lines when closed)
self.tui.add_child(self.input_field)       # Input field
```

Each child is rendered in order. The differential renderer automatically detects when components change size or content.
