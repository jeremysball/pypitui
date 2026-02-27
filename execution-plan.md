# Fix: Scrollback Lines Not Rendered When Content Grows

## Problem

When a large component (e.g., 25+ line MessagePanel) is added to an empty conversation:
- Top border lines are missing (blank instead of rendered)
- Root cause: `_handle_content_growth` emits blank newlines, then `_render_changed_lines` only renders visible portion

## Current Flow (Buggy)

```
render_frame():
  1. base_lines = self.render(term_width)        # Get 25 lines
  2. _handle_content_growth(buffer, 25, 0, 24)   # previous=0, current=25, height=24
     - Emits 25 newlines (ALL BLANK)
     - _hardware_cursor_row = 23
  3. _render_changed_lines(lines, 24)
     - first_visible = 25 - 24 = 1
     - Only renders lines[1] through lines[24]
     - lines[0] (top border) NEVER RENDERED
```

## Desired Flow (Fixed)

```
render_frame():
  1. base_lines = self.render(term_width)        # Get 25 lines
  2. _handle_content_growth(buffer, 25, 0, 24, lines)
     - Render lines[0] (scrollback line) FIRST
     - THEN emit newlines to scroll it off
     - _hardware_cursor_row = 23
  3. _render_changed_lines(lines, 24)
     - Renders visible lines[1] through lines[24]
```

---

## Execution Plan

### Phase A: Write Failing Test

- [x] Create test file: `tests/test_scrollback_render.py` (in alfred-prd)
- [x] Import MockTerminal from pypitui: `from pypitui import MockTerminal, TUI, BorderedBox, Text`
- [x] Test: `test_new_large_content_renders_scrollback_lines()`
- [x] Run: `uv run pytest tests/test_scrollback_render.py -v`
- [x] Confirm test FAILS (top border not in output)

### Phase B: Implement Fix in pypitui

**File:** `src/pypitui/tui.py`

- [x] Open file, locate `_handle_content_growth` (line 790)
- [x] **Change method signature** to accept `lines: list[str]` parameter
- [x] **Add scrollback rendering** before emitting newlines
- [x] **Update call site** in `render_frame()` to pass `lines`

### Phase C: Verify Fix

- [x] Run: `uv run pytest tests/test_scrollback_render.py -v`
- [x] Confirm test PASSES
- [x] Run full pypitui tests if available (169 passed)

### Phase D: Edge Cases

- [ ] Test: Content grows by exactly 1 line (boundary case)
- [ ] Test: Multiple large boxes added sequentially
- [ ] Test: Content shrinks then grows again
- [ ] Test: Terminal resize during growth

### Phase E: Commit

- [x] Run: `uv run ruff check src/ && uv run mypy src/ && uv run pytest`
- [x] All checks passed, 169 tests pass

---

## Technical Notes

### Key Variables

| Variable | Meaning |
|----------|---------|
| `current_count` | Total lines in current frame |
| `previous_count` | Total lines in previous frame |
| `term_height` | Terminal height in rows |
| `first_visible` | First line index that's visible (not in scrollback) |
| `_hardware_cursor_row` | Current cursor position (screen-relative) |

### Differential Rendering

The TUI only updates lines that changed:
- Compares `lines[i]` vs `_previous_lines[i]`
- Uses relative cursor movement (`\x1b[nA`/`\x1b[nB`)
- Scrollback lines are "frozen" after scrolling off

### Synchronized Output

Uses DEC 2026 mode to prevent flickering:
- `\x1b[?2026h` - Begin buffered mode
- `\x1b[?2026l` - Flush buffer

---

## File Locations

| File | Purpose |
|------|---------|
| `src/pypitui/tui.py` | Main TUI class with the fix |
| `tests/test_scrollback_render.py` | Test file for the bug fix |
