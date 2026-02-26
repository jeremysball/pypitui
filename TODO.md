# TODO: Fix Screen Switching Artifacts

## Status: ✅ FIXED

## Problem

When switching from a screen with many lines (streaming with 50+ lines) back to a screen with fewer lines (menu with ~10 lines), old content remained visible below the new content. The `request_render(force=True)` resets `_previous_lines` but doesn't actually clear the terminal screen.

## Root Cause Analysis

### What `request_render(force=True)` did:
```python
def request_render(self, force: bool = False) -> None:
    self._render_requested = True
    if force:
        self._previous_lines = []  # Only resets the diff tracking
```

### What was missing:
The terminal still has 50+ lines of content. When we render 10 new lines:
- Lines 0-9: Updated with menu content
- Lines 10-50: **Still have old streaming content** (never cleared!)

The differential renderer only updates lines that exist in the NEW content. It doesn't know about the orphaned lines below.

## Solution Implemented

Added `_force_full_redraw` flag that triggers a full screen clear:

```python
def request_render(self, force: bool = False) -> None:
    self._render_requested = True
    if force:
        self._force_full_redraw = True
        self._previous_lines = []
```

In `render_frame()`:
```python
if self._force_full_redraw:
    self._force_full_redraw = False
    self.terminal.write("\x1b[2J\x1b[H")  # Clear screen, move cursor home
    self._hardware_cursor_row = 0
    self._previous_lines = []
    self._max_lines_rendered = 0
```

## Tasks

### Phase 1: Understand the Issue ✅
- [x] Reproduce the bug with streaming → menu switch
- [x] Verify `request_render(force=True)` doesn't clear terminal
- [x] Check if `_clear_on_shrink` handles this case (it didn't)
- [x] Document exact sequence of events causing artifacts

### Phase 2: Implement Fix ✅
- [x] Add `_force_full_redraw` flag
- [x] Emit clear screen sequence when flag is set
- [x] Reset `_hardware_cursor_row` and `_max_lines_rendered`

### Phase 3: Test ✅
- [x] All 167 tests pass
- [x] No regressions introduced

### Phase 4: Update Examples ✅
- [x] demo.py already uses `request_render(force=True)` in `switch_screen()`

---

## Committed

```
903c905 fix: clear screen on force=True to remove artifacts
```
