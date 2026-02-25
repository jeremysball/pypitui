# PRD: Scrollback and Streaming Support

**Status**: Draft
**Priority**: High
**Created**: 2025-02-25

---

## Problem Statement

pypitui uses absolute cursor positioning (`\x1b[row;colH`), which limits all content to the visible viewport. When content exceeds terminal height:

- Users cannot scroll back through history using Shift+PgUp or mouse wheel
- Content must be pre-clipped to viewport height
- No content flows into the terminal's native scrollback buffer
- Chat/log applications lose historical context

This differs from pi-tui (TypeScript reference implementation) which supports full scrollback via relative cursor movement.

---

## Solution Overview

Implement relative cursor positioning with working area tracking:

1. **Main buffer mode** - Don't use alternate screen (already default)
2. **Relative movement** - Use `\x1b[nA/B` instead of `\x1b[row;colH`
3. **Working area tracking** - Track virtual canvas height with `_max_lines_rendered`
4. **Viewport calculation** - Map content lines to screen rows dynamically
5. **Synchronized output** - Use DEC 2026 to prevent flickering

---

## User Stories

- As a chat app user, I can scroll up to see previous messages
- As a log viewer user, I can use my terminal's scrollback to review history
- As a streaming app user, I see smooth updates without flickering
- As a developer, overlays still work correctly when content is scrolled

---

## Success Criteria

- [ ] Content exceeding terminal height flows into scrollback buffer
- [ ] Shift+PgUp and mouse wheel reveal historical content
- [ ] No visible flickering during streaming updates
- [ ] Overlays render correctly regardless of scroll position
- [ ] All existing demos continue to work
- [ ] Test coverage for new functionality ≥80%

---

## Technical Design

### Key Concepts

```
Terminal: 24 rows
Content rendered: 100 lines

Working Area (maxLinesRendered = 100):
┌─────────────────────────────────────────────────┐
│ Line 0-75                                        │ ← In scrollback
├─────────────────────────────────────────────────┤ ← viewportTop = 76
│ Line 76  ← Screen row 0                         │
│ Line 77  ← Screen row 1                         │
│ ...                                             │
│ Line 99  ← Screen row 23                        │
└─────────────────────────────────────────────────┘
```

### Escape Sequences Reference

| Sequence | Meaning |
|----------|---------|
| `\x1b[nA` | Move cursor up n lines (relative) |
| `\x1b[nB` | Move cursor down n lines (relative) |
| `\x1b[?2026h` | Begin synchronized output |
| `\x1b[?2026l` | End synchronized output |
| `\r` | Carriage return (column 0) |
| `\x1b[2K` | Clear entire line |

---

## Milestones

### Milestone 1: Working Area Tracking
**Goal**: Track virtual canvas height and cursor position for relative movement

**Key Concept**: The "first visible row" is the line number in the entire scrollback buffer that currently appears at the top of the terminal viewport. When content exceeds terminal height, this tells us which slice of content is visible.

```
Scrollback buffer (100 lines total):
┌─────────────────────┐
│ Line 0              │
│ Line 1              │
│ ...                 │
│ Line 75             │
├─────────────────────┤ ← first_visible_row = 76 (top of terminal)
│ Line 76  (row 0)    │ ← Visible in terminal
│ Line 77  (row 1)    │
│ ...                 │
│ Line 99  (row 23)   │ ← Bottom of terminal
└─────────────────────┘
```

**Tasks**:
- [x] Add `_max_lines_rendered: int = 0` to TUI class (total lines in virtual canvas)
- [x] Add `_hardware_cursor_row: int = 0` to TUI class (current cursor position in scrollback)
- [x] Add `_first_visible_row_previous: int = 0` to TUI class (first visible row from last frame)
- [x] Add `_calculate_first_visible_row(self, term_height: int) -> int`
  - Returns `max(0, self._max_lines_rendered - term_height)`
  - This tells us which line in the scrollback is at the top of the screen
- [x] Update `_max_lines_rendered` in `render_frame()` after rendering
- [x] Write test: `_calculate_first_visible_row()` with various content/terminal sizes

**Validation**: ✅ Unit tests pass, state variables update correctly during render

---

### Milestone 2: Synchronized Output
**Goal**: Prevent flickering during batched updates

**Tasks**:
- [x] Add `_begin_sync(self) -> str` returning `"\x1b[?2026h"`
- [x] Add `_end_sync(self) -> str` returning `"\x1b[?2026l"`
- [x] Add sync constants to `Terminal` class (optional abstraction)
- [x] Write test: sync wrappers produce correct escape sequences

**Validation**: ✅ Unit tests pass, sequences are correct

---

### Milestone 3: Relative Cursor Movement
**Goal**: Replace absolute positioning with relative movement

**Tasks**:
- [x] Add `_move_cursor_relative(self, target_row: int) -> str`
  - Calculate delta: `delta = target_row - self._hardware_cursor_row`
  - Return `""` if delta == 0
  - Return `f"\x1b[{delta}B"` if delta > 0 (down)
  - Return `f"\x1b[{-delta}A"` if delta < 0 (up)
- [x] Update `_hardware_cursor_row` after every movement
- [x] Add `move_cursor_up(n: int) -> str` to `Terminal` ABC
- [x] Add `move_cursor_down(n: int) -> str` to `Terminal` ABC
- [x] Implement in `ProcessTerminal` and `MockTerminal`
- [x] Write test: `_move_cursor_relative()` produces correct sequences
- [x] Write test: delta calculations for various start/end positions

**Validation**: ✅ Unit tests pass, cursor tracking is accurate

---

### Milestone 4: Refactor render_frame()
**Goal**: Core rendering uses relative positioning with batching

**Tasks**:
- [x] Create output buffer string at start of `render_frame()`
- [x] Replace absolute `move_cursor(i, 0)` loop with relative movement
- [x] Handle content shrinkage (clear orphaned lines)
- [x] Handle content growth (scroll terminal, add newlines)
- [x] Single `terminal.write(buffer)` at end
- [x] Initialize `_hardware_cursor_row` at end of render
- [x] Write test: differential rendering with relative positioning
- [x] Write test: content growth triggers scroll (verified via tmux)
- [x] Write test: content shrinkage clears orphaned lines

**Validation**: ✅ Demo shows scrollback working, tmux history contains all lines

---

### Milestone 5: Overlay Viewport Positioning
**Goal**: Overlays work correctly with scrolled content

**Tasks**:
- [ ] Add `viewport_top` parameter to `_composite_overlays()`
- [ ] Convert overlay content row to screen row: `screen_row = content_row - viewport_top`
- [ ] Only render overlay if `0 <= screen_row < term_height`
- [ ] Update `_resolve_overlay_layout()` to account for viewport offset
- [ ] Update overlay position calculation for "top"/"center"/"bottom" anchors
- [ ] Write test: overlay positioning with various scroll states
- [ ] Write test: overlay hidden when scrolled out of view

**Validation**: Overlay demos work with scrolled content

---

### Milestone 6: Remove Height Limiting
**Goal**: Content can grow unbounded into scrollback

**Tasks**:
- [ ] Audit `components.py` for height clipping logic
- [ ] Audit `rich_components.py` for height limiting
- [ ] Remove or make optional any `min(height, term_height)` capping
- [ ] Ensure `Container.render()` returns all lines without limiting
- [ ] Write test: component renders more lines than terminal height

**Validation**: Content flows into scrollback naturally

---

### Milestone 7: Integration Testing
**Goal**: End-to-end validation of scrollback functionality

**Tasks**:
- [ ] Create `examples/scrollback_demo.py` with streaming content
- [ ] Test: content exceeding terminal height flows to scrollback
- [ ] Test: Shift+PgUp shows history (manual/E2E with tmux)
- [ ] Test: mouse wheel scrolls (manual/E2E with tmux)
- [ ] Test: streaming updates don't flicker
- [ ] Test: all existing demos still work
- [ ] Run full test suite: `uv run pytest`

**Validation**: All tests pass, manual testing confirms scrollback works

---

### Milestone 8: Documentation
**Goal**: Users understand how to use scrollback features

**Tasks**:
- [ ] Update README.md with scrollback support documentation
- [ ] Document `use_alternate_buffer=False` requirement (default)
- [ ] Add docstrings to new methods
- [ ] Add inline comments explaining working area concept
- [ ] Update `docs/tui-reuse.md` if needed

**Validation**: Documentation is clear and accurate

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Terminal doesn't support DEC 2026 | Low | Medium | Sync is optional; graceful degradation |
| Overlay positioning breaks | Medium | High | Dedicated milestone with thorough tests |
| Performance regression | Low | Medium | Profile before/after render changes |
| Existing demos break | Medium | High | Run all examples after each phase |
| Cursor tracking drifts | Medium | High | Unit tests for cursor position accuracy |

---

## Dependencies

- None (standalone feature)

---

## References

- [pi-tui source](https://github.com/badlogic/pi-mono) - TypeScript reference implementation
- [XTerm Control Sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html)
- [DEC Private Mode 2026](https://gitlab.com/gnachman/iterm2/-/wikis/synchronized-updates-spec)
- `docs/scrollback-and-streaming.md` - Technical specification
