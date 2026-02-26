# Scrollback and Streaming in Terminal UIs

This document explains how to implement proper scrollback support and streaming updates in a terminal UI. It covers the key differences between pi-tui (TypeScript) and pypitui (Python), and what changes are needed for pypitui to achieve full scrollback support.

## The Problem

When building a chat application or any long-running TUI, content eventually exceeds the terminal height. Users expect to be able to scroll back through history using their terminal's scrollback buffer (Shift+PgUp, mouse wheel, etc.).

**The challenge**: Most TUI libraries render to a fixed-size screen. When content exceeds screen height, it's either clipped or the library uses an alternate buffer that has no scrollback.

## Terminal Buffers

Terminals have a main screen buffer with scrollback support:

```
Main buffer:
┌─────────────────────┐
│ Old command 1       │ ← Scrollback history
│ Old command 2       │
│ ...                 │
│ Old command 100     │
├─────────────────────┤ ← Viewport starts here
│ Current output 1    │ ← Visible on screen
│ Current output 2    │
│ ...                 │
│ Current output 24   │
└─────────────────────┘
```

**To enable scrollback**: Use the main buffer (default). Never call alternate screen escape sequences.

## Why Absolute Positioning Breaks Scrollback

### The Trap

It's tempting to use absolute cursor positioning:

```python
# Absolute positioning: "Go to row 5, column 0"
self.terminal.write("\x1b[5;1H")  # or terminal.move_cursor(4, 0)
self.terminal.write("Hello")
```

This works fine when content fits on screen. But when content exceeds screen height:

```
Terminal: 24 rows
Content: 100 lines

Line 0-75:   In scrollback (not visible)
Line 76-99:  Visible on screen (rows 0-23)

Problem: \x1b[5;1H always goes to SCREEN row 5
         It cannot address content line 80 (which is at screen row 4)
```

**Absolute positioning addresses the screen, not the content.** When content scrolls, your row 5 is now pointing at a different part of the content.

### The Solution: Relative Movement

Relative cursor movement works from the current position, so it respects the terminal's scroll state:

```python
# Relative: "Move up 3 lines from here"
self.terminal.write("\x1b[3A")

# Relative: "Move down 1 line from here"
self.terminal.write("\x1b[1B")
```

```
Cursor is at line 99 (bottom of content)
Content line 80 needs update

Calculate: target is 80, current is 99
delta = 80 - 99 = -19

Move up 19 lines: \x1b[19A
Now cursor is at content line 80
Write the update
Move back down if needed
```

## The Working Area Concept

To use relative movement correctly, you need to track a "working area" — the virtual canvas of all rendered content.

### What pi-tui Does

```typescript
class TUI {
    maxLinesRendered: number = 0;      // Working area height
    hardwareCursorRow: number = 0;     // Where cursor actually is
    previousViewportTop: number = 0;   // First visible line

    doRender() {
        // Track working area (grows but doesn't shrink unless cleared)
        this.maxLinesRendered = Math.max(this.maxLinesRendered, lines.length);

        // Calculate viewport position
        const viewportTop = Math.max(0, this.maxLinesRendered - termHeight);

        // Move cursor relative to current position
        const lineDiff = targetRow - this.hardwareCursorRow;
        if (lineDiff > 0) {
            this.terminal.write(`\x1b[${lineDiff}B`);  // Down
        } else if (lineDiff < 0) {
            this.terminal.write(`\x1b[${-lineDiff}A`); // Up
        }
    }
}
```

### Visual Example

```
Terminal: 24 rows
Content rendered: 100 lines

Working Area (maxLinesRendered = 100):
┌─────────────────────────────────────────────────┐
│ Line 0                                          │
│ Line 1                                          │
│ ...                                             │
│ Line 75                                         │
├─────────────────────────────────────────────────┤ ← viewportTop = 76
│ Line 76  ← Screen row 0                         │
│ Line 77  ← Screen row 1                         │
│ ...                                             │
│ Line 99  ← Screen row 23                        │
└─────────────────────────────────────────────────┘
                         ↑
              hardwareCursorRow = 99 (at bottom)

User types, need to update line 80:

1. Calculate: targetRow = 80
2. Current position: hardwareCursorRow = 99
3. Delta: 80 - 99 = -19
4. Send: \x1b[19A (move up 19 lines)
5. Update content
6. Send: \x1b[19B (move back down)
7. Update hardwareCursorRow = 80, then back to 99
```

## Synchronized Output

Updates should be batched to prevent flickering. Use DEC private mode 2026:

```python
# Begin synchronized output
buffer = "\x1b[?2026h"

# Add all cursor movements and content
buffer += "\x1b[19A"      # Move up
buffer += "\x1b[2K"       # Clear line
buffer += "New content"   # Write content
buffer += "\x1b[19B"      # Move back down

# End synchronized output
buffer += "\x1b[?2026l"

# Single atomic write
self.terminal.write(buffer)
```

Without synchronization, the terminal might render intermediate states:
```
What user sees without sync:    What user sees with sync:
┌─────────────────┐             ┌─────────────────┐
│ Old content     │             │ Old content     │
│ Old content     │             │ New content     │ ← Clean update
│ ⠋ (flicker)     │             │ Old content     │
│ Old content     │             └─────────────────┘
└─────────────────┘
```

## Current pypitui Implementation

pypitui uses absolute positioning, which limits it to the visible viewport:

```python
# From pypitui/tui.py - render_frame()
for i, line in enumerate(lines):
    if i >= len(self._previous_lines) or self._previous_lines[i] != line:
        self.terminal.move_cursor(i, 0)  # ← Absolute positioning!
        self.terminal.write(line)
```

**Consequences**:
- `i` is always 0 to `term_height - 1`
- Content must be pre-clipped to viewport height
- No content flows into scrollback
- User cannot scroll back to see history

## Required Changes for Scrollback Support

### 1. Track Working Area and Cursor Position

```python
class TUI:
    def __init__(self, ...):
        # ... existing code ...
        self._max_lines_rendered: int = 0      # Working area height
        self._hardware_cursor_row: int = 0     # Actual cursor position
        self._previous_viewport_top: int = 0   # First visible line
```

### 2. Calculate Viewport Position

```python
def _calculate_viewport_top(self, content_lines: int, term_height: int) -> int:
    """Calculate which content line is at the top of the screen."""
    return max(0, self._max_lines_rendered - term_height)
```

### 3. Use Relative Cursor Movement

```python
def _move_cursor_to_line(self, target_row: int) -> str:
    """Generate escape sequence to move to target line using relative movement."""
    delta = target_row - self._hardware_cursor_row
    if delta > 0:
        return f"\x1b[{delta}B"  # Move down
    elif delta < 0:
        return f"\x1b[{-delta}A"  # Move up
    return ""
```

### 4. Batch Updates with Synchronized Output

```python
def render_frame(self) -> None:
    # ... render content to lines ...

    buffer = "\x1b[?2026h"  # Begin sync

    for i, (old_line, new_line) in enumerate(zip(self._previous_lines, lines)):
        if old_line != new_line:
            buffer += self._move_cursor_to_line(i)
            buffer += "\r\x1b[2K"  # Clear line
            buffer += new_line
            self._hardware_cursor_row = i

    buffer += "\x1b[?2026l"  # End sync
    self.terminal.write(buffer)

    self._max_lines_rendered = max(self._max_lines_rendered, len(lines))
    self._previous_lines = lines
```

### 5. Handle Content Growth

When content grows beyond the viewport:

```python
# New lines appended - need to scroll terminal
if len(lines) > len(self._previous_lines):
    new_lines = len(lines) - len(self._previous_lines)

    # Move to bottom and add newlines (causes scroll)
    buffer += self._move_cursor_to_line(len(self._previous_lines) - 1)
    buffer += "\r\n" * new_lines

    # Now write the new content
    for i in range(len(self._previous_lines), len(lines)):
        buffer += "\r\x1b[2K" + lines[i]
```

## Overlays and Viewport Position

When compositing overlays, map overlay positions to screen coordinates:

```python
def _composite_overlay(self, overlay_row: int, overlay_height: int,
                       viewport_top: int, term_height: int) -> int:
    """Convert overlay content row to screen row."""
    # overlay_row 0 should appear at screen row 5 (for example)
    # If viewport_top = 76, screen_row = overlay_row - viewport_top + offset
    screen_row = overlay_row - viewport_top
    return screen_row
```

## Summary: The Five Pillars of Scrollback

| Pillar | What | Why |
|--------|------|-----|
| **1. Main buffer** | Don't use alternate screen | Enables terminal's native scrollback |
| **2. Relative movement** | `\x1b[nA/B` not `\x1b[row;colH` | Works with scrolled content |
| **3. Working area** | Track `maxLinesRendered` | Know where content is in virtual canvas |
| **4. Viewport calculation** | `viewportTop = max(0, maxLines - termHeight)` | Map content lines to screen rows |
| **5. Synchronized output** | `\x1b[?2026h/l` | Prevent flickering during updates |

## Implementation Checklist for pypitui

- [x] Add `_max_lines_rendered` tracking
- [x] Add `_hardware_cursor_row` tracking
- [x] Add `_previous_viewport_top` tracking
- [x] Replace `move_cursor(i, 0)` with relative movement
- [x] Add synchronized output wrapper
- [x] Update overlay compositing to use viewport-relative positioning
- [x] Remove height limiting from components (let content flow to scrollback)
- [x] Add newline-based scrolling for content growth
- [x] Remove alternate buffer support (scrollback is always enabled)

## References

- [pi-tui source](https://github.com/badlogic/pi-mono) - TypeScript implementation
- [XTerm Control Sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html) - Escape sequence reference
- [DEC Private Mode 2026](https://gitlab.com/gnachman/iterm2/-/wikis/synchronized-updates-spec) - Synchronized output specification
