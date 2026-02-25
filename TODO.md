# Scrollback and Streaming Implementation TODO

Based on `docs/scrollback-and-streaming.md`

## Overview

Convert pypitui from absolute positioning (viewport-only) to relative positioning with working area tracking. This enables native terminal scrollback (Shift+PgUp, mouse wheel) and streaming content.

---

## Phase 1: Working Area Tracking

### 1.1 Add State Variables to TUI Class
- [ ] Add `_max_lines_rendered: int = 0` - tracks virtual canvas height (grows, never shrinks unless cleared)
- [ ] Add `_hardware_cursor_row: int = 0` - tracks actual cursor position in terminal
- [ ] Add `_previous_viewport_top: int = 0` - tracks first visible line (for scroll detection)
- [ ] Verify `_max_lines_rendered` is already partially present (line 197 in tui.py)

### 1.2 Add Viewport Calculation Method
- [ ] Add `_calculate_viewport_top(self, content_lines: int, term_height: int) -> int`
  - Returns `max(0, self._max_lines_rendered - term_height)`
  - Determines which content line is at screen row 0

### 1.3 Update State During Render
- [ ] In `render_frame()`, update `_max_lines_rendered` after rendering:
  - `self._max_lines_rendered = max(self._max_lines_rendered, len(lines))`
- [ ] Track viewport top: `viewport_top = self._calculate_viewport_top(len(lines), term_height)`
- [ ] Store `_previous_viewport_top` for detecting scroll events

---

## Phase 2: Relative Cursor Movement

### 2.1 Add Relative Movement Helper
- [ ] Add `_move_cursor_relative(self, target_row: int) -> str`
  - Calculate delta: `delta = target_row - self._hardware_cursor_row`
  - Return `""` if delta == 0
  - Return `f"\x1b[{delta}B"` if delta > 0 (move down)
  - Return `f"\x1b[{-delta}A"` if delta < 0 (move up)
  - **Returns escape sequence string, doesn't write directly**

### 2.2 Add Cursor Position Tracking
- [ ] Track cursor position after every movement
- [ ] Update `_hardware_cursor_row` whenever cursor moves
- [ ] Initialize `_hardware_cursor_row` to `len(lines) - 1` at end of render (cursor at bottom)

---

## Phase 3: Synchronized Output

### 3.1 Add Sync Wrapper Methods
- [ ] Add `_begin_sync(self) -> str` returning `"\x1b[?2026h"`
- [ ] Add `_end_sync(self) -> str` returning `"\x1b[?2026l"`

### 3.2 Batch All Output
- [ ] Create output buffer string at start of `render_frame()`
- [ ] Accumulate all cursor movements and content in buffer
- [ ] Single `terminal.write()` call at end
- [ ] Wrap entire frame output with sync begin/end

---

## Phase 4: Refactor render_frame()

### 4.1 Replace Absolute Positioning Loop
Current code (to replace):
```python
for i, line in enumerate(lines):
    if i >= len(self._previous_lines) or self._previous_lines[i] != line:
        self.terminal.move_cursor(i, 0)  # ← Absolute!
        self.terminal.write(line)
```

- [ ] Replace with relative positioning:
  ```python
  buffer = self._begin_sync()
  for i, line in enumerate(lines):
      if i >= len(self._previous_lines) or self._previous_lines[i] != line:
          buffer += self._move_cursor_relative(i)
          buffer += "\r\x1b[2K"  # CR + clear line
          buffer += line
          self._hardware_cursor_row = i
  buffer += self._end_sync()
  self.terminal.write(buffer)
  ```

### 4.2 Handle Content Shrinkage
- [ ] When `len(lines) < len(self._previous_lines)`:
  - Move to first orphaned line: `buffer += self._move_cursor_relative(len(lines))`
  - Clear each orphaned line with `"\r\x1b[2K"`
  - Update `_hardware_cursor_row` appropriately

### 4.3 Handle Content Growth (Scrollback)
- [ ] When `len(lines) > len(self._previous_lines)`:
  - Move to last previous line: `buffer += self._move_cursor_relative(len(self._previous_lines) - 1)`
  - Add newlines to scroll terminal: `buffer += "\r\n" * (len(lines) - len(self._previous_lines))`
  - This pushes old content into scrollback naturally
  - Write new lines at bottom

---

## Phase 5: Terminal Abstraction Updates

### 5.1 Add Relative Movement to Terminal Class
- [ ] Add `move_cursor_relative(rows: int) -> str` method to `Terminal` ABC
  - Returns escape sequence, doesn't write
  - Positive = down, negative = up
- [ ] Implement in `ProcessTerminal`
- [ ] Implement in `MockTerminal`

### 5.2 Add Synchronized Output to Terminal Class
- [ ] Add `begin_sync() -> str` method
- [ ] Add `end_sync() -> str` method
- [ ] Or add these as constants on the class

---

## Phase 6: Overlay Compositing Updates

### 6.1 Viewport-Relative Overlay Positioning
- [ ] Update `_composite_overlays()` to accept `viewport_top` parameter
- [ ] Convert overlay content row to screen row:
  - `screen_row = overlay_content_row - viewport_top`
- [ ] Only render overlay if `0 <= screen_row < term_height`

### 6.2 Overlay Position Calculation
- [ ] In `_resolve_overlay_layout()`, account for viewport offset
- [ ] Overlays positioned at "top" should be at `viewport_top + offset`
- [ ] Overlays positioned at "center" should center within visible viewport

---

## Phase 7: Remove Height Limiting

### 7.1 Audit Components for Height Clipping
- [ ] Check `components.py` for any `min(height, term_height)` logic
- [ ] Check `rich_components.py` for height limiting
- [ ] Remove or make optional any height capping

### 7.2 Update Container.render()
- [ ] Ensure `Container.render()` doesn't limit returned lines
- [ ] Let content grow unbounded; differential render handles it

---

## Phase 8: Testing

### 8.1 Unit Tests for New Methods
- [ ] Test `_calculate_viewport_top()` with various content/terminal sizes
- [ ] Test `_move_cursor_relative()` produces correct escape sequences
- [ ] Test sync wrapper methods

### 8.2 Integration Tests
- [ ] Test content exceeding terminal height flows to scrollback
- [ ] Test overlay positioning with scrolled content
- [ ] Test differential rendering with relative positioning
- [ ] Test no flickering (sync output working)

### 8.3 Manual E2E Test
- [ ] Run demo app
- [ ] Add content beyond terminal height
- [ ] Verify Shift+PgUp shows history
- [ ] Verify mouse wheel scrolls
- [ ] Verify streaming updates don't flicker

---

## Phase 9: Documentation

### 9.1 Update README
- [ ] Document scrollback support
- [ ] Note: must use `use_alternate_buffer=False` (default)

### 9.2 Add Example
- [ ] Create `examples/scrollback_demo.py` showing streaming chat-like content

---

## Quick Reference: Escape Sequences

| Sequence | Meaning |
|----------|---------|
| `\x1b[nA` | Move cursor up n lines |
| `\x1b[nB` | Move cursor down n lines |
| `\x1b[?2026h` | Begin synchronized output |
| `\x1b[?2026l` | End synchronized output |
| `\r` | Carriage return (column 0) |
| `\x1b[2K` | Clear entire line |

---

## Implementation Order

1. **Phase 1** - State tracking (foundation)
2. **Phase 3** - Sync output (prevents flickering early)
3. **Phase 2** - Relative movement (core change)
4. **Phase 4** - Refactor render_frame (main work)
5. **Phase 5** - Terminal abstraction (cleanup)
6. **Phase 6** - Overlay updates (edge case)
7. **Phase 7** - Remove height limits (enables scrollback)
8. **Phase 8** - Testing (validation)
9. **Phase 9** - Documentation (polish)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Terminal doesn't support DEC 2026 | Sync is optional; test without it |
| Overlay positioning breaks | Phase 6 dedicated to this |
| Performance regression from batching | Profile before/after |
| Existing demos break | Test all examples after changes |
