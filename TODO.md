# TODO: Fix Screen Switching Artifacts

## Problem

When switching from a screen with many lines (streaming with 50+ lines) back to a screen with fewer lines (menu with ~10 lines), old content remains visible below the new content. The `request_render(force=True)` resets `_previous_lines` but doesn't actually clear the terminal screen.

## Root Cause Analysis

### What `request_render(force=True)` does:
```python
def request_render(self, force: bool = False) -> None:
    self._render_requested = True
    if force:
        self._previous_lines = []  # Only resets the diff tracking
```

### What's missing:
The terminal still has 50+ lines of content. When we render 10 new lines:
- Lines 0-9: Updated with menu content
- Lines 10-50: **Still have old streaming content** (never cleared!)

The differential renderer only updates lines that exist in the NEW content. It doesn't know about the orphaned lines below.

## Solution Options

### Option 1: Clear orphaned lines in render_frame (RECOMMENDED)

Modify `render_frame()` to detect when content shrunk and clear the orphaned lines:

```python
# In render_frame(), after rendering new content:
if current_count < previous_count:
    # Content shrank - clear orphaned lines
    for i in range(current_count, previous_count):
        buffer += self._move_cursor_relative(i)
        buffer += "\r\x1b[2K"
```

**Note**: This already exists with `_clear_on_shrink` but only works when content fits in terminal. Need to extend for scrollback case.

### Option 2: Add TUI.clear_screen() method

Add a method that emits clear screen sequence while preserving scrollback:

```python
def clear_screen(self) -> None:
    """Clear visible screen (not scrollback)."""
    self.terminal.write("\x1b[2J")  # Clear screen
    self.terminal.write("\x1b[H")   # Move cursor home
    self._previous_lines = []
    self._hardware_cursor_row = 0
```

### Option 3: Track max rendered lines and clear to that

Track the maximum lines ever rendered and always clear up to that:

```python
# In render_frame():
lines_to_clear = max(current_count, self._max_lines_rendered, previous_count)
for i in range(current_count, lines_to_clear):
    buffer += self._move_cursor_relative(i)
    buffer += "\r\x1b[2K"
```

---

## Tasks

### Phase 1: Understand the Issue
- [ ] Reproduce the bug with streaming → menu switch
- [ ] Verify `request_render(force=True)` doesn't clear terminal
- [ ] Check if `_clear_on_shrink` handles this case
- [ ] Document exact sequence of events causing artifacts

### Phase 2: Implement Fix
- [ ] Choose solution (Option 1, 2, or 3)
- [ ] Implement the fix in `tui.py`
- [ ] Ensure fix works with scrollback (content > terminal height)
- [ ] Ensure fix works without scrollback (content < terminal height)

### Phase 3: Test
- [ ] Test streaming → menu (50 lines → 10 lines)
- [ ] Test matrix → menu (full screen animation → 10 lines)
- [ ] Test menu → components → menu (similar sizes)
- [ ] Test with terminal resize during operation
- [ ] Verify no new flicker introduced

### Phase 4: Update Examples
- [ ] Review if examples need changes after fix
- [ ] Update any workarounds in demo.py
- [ ] Document the proper pattern in comments

---

## Implementation Notes

### Current `_clear_on_shrink` behavior:
```python
# Only clears if content fits in terminal AND shrank
if self._clear_on_shrink and current_count < previous_count:
    for i in range(current_count, previous_count):
        buffer += self._move_cursor_relative(i)
        buffer += "\r\x1b[2K"
```

### The bug case:
```
Terminal height: 30 lines
Streaming screen: 50 lines (20 in scrollback, 30 visible)
Menu screen: 10 lines

Previous: 50 content lines
Current: 10 content lines

Problem: The 40 extra lines (10 visible + 30 in scrollback) aren't cleared
```

### Proposed fix in `render_frame()`:
```python
# After rendering content, always clear to previous max
if current_count < previous_count:
    # Clear lines from current_count to previous_count
    # This handles both on-screen and ensures clean transition
    for i in range(current_count, min(previous_count, term_height)):
        buffer += self._move_cursor_relative(i)
        buffer += "\r\x1b[2K"
```

Wait, this still won't work for scrollback case. Need to think more...

Actually, the real issue is:
- Streaming added 50 lines to TUI children
- Menu only has 10 children
- The terminal has scrolled, so lines 0-39 are in scrollback
- We can't modify scrollback content!

So the fix needs to happen BEFORE switching screens:
1. Clear the visible terminal
2. Reset scroll position to bottom
3. Then render new content

This might require emitting clear screen + scrolling to bottom.
