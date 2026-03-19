# Execution Plan: PRD #007 - Phase 2: Rendering Engine

## Overview
Implement differential rendering with full viewport-aware diffing and 60 FPS performance (<16ms frame time).

---

## Phase 2: Rendering Engine

### Core Data Structures

- [x] **Test**: `test_size_dataclass()` — Size(width, height) stores dimensions
- [x] **Implement**: `Size` dataclass with `width: int`, `height: int`
- [x] **Run**: `uv run pytest tests/unit/test_component.py::test_size_dataclass -v`

- [x] **Test**: `test_rendered_line_dataclass()` — RenderedLine stores content and styles
- [x] **Implement**: `RenderedLine` dataclass with `content: str`, `styles: list[StyleSpan]`
- [x] **Run**: `uv run pytest tests/unit/test_component.py::test_rendered_line_dataclass -v`

- [x] **Test**: `test_rect_dataclass()` — Rect(x, y, width, height) stores position and dimensions
- [x] **Implement**: `Rect` dataclass with `x: int`, `y: int`, `width: int`, `height: int`
- [x] **Run**: `uv run pytest tests/unit/test_component.py::test_rect_dataclass -v`

### TUI Class Foundation

- [ ] **Test**: `test_tui_init_caches_previous_lines()` — _previous_lines is empty dict row->content_hash
- [ ] **Test**: `test_tui_init_tracks_max_lines()` — _max_lines_rendered starts at 0
- [ ] **Test**: `test_tui_init_tracks_viewport_top()` — _viewport_top starts at 0
- [ ] **Test**: `test_tui_init_hardware_cursor()` — _hardware_cursor_row and _hardware_cursor_col tracked
- [ ] **Implement**: `TUI.__init__(self, terminal: Terminal)` with full state tracking
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "test_tui_init" -v`

- [ ] **Test**: `test_tui_add_child_sets_root()` — add_child stores component
- [ ] **Implement**: `TUI.add_child(self, component: Component)`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_tui_add_child_sets_root -v`

### Differential Rendering Core

- [ ] **Test**: `test_find_changed_bounds_identifies_range()` — returns (first, last) changed indices
- [ ] **Implement**: `TUI._find_changed_bounds(self, new_lines: list[str]) -> tuple[int, int]`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_find_changed_bounds_identifies_range -v`

- [ ] **Test**: `test_output_diff_writes_changed_lines()` — only changed lines emit escape sequences
- [ ] **Test**: `test_output_diff_skips_unchanged_lines()` — unchanged lines generate no output
- [ ] **Test**: `test_escape_sequence_efficiency()` — append-only emits ≤20% sequences vs full redraw
- [ ] **Implement**: `TUI._output_diff(self, lines: list[str])` with full diffing algorithm
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "output_diff or efficiency" -v`

### Viewport Tracking

- [ ] **Test**: `test_viewport_top_calculation()` — viewport_top = max(0, content_height - term_height)
- [ ] **Test**: `test_viewport_top_zero_when_content_fits()` — 3 lines on 24-line terminal = 0
- [ ] **Test**: `test_viewport_top_nonzero_when_content_scrolls()` — 30 lines on 24-line terminal = 6
- [ ] **Implement**: `TUI._calculate_viewport_top(self, content_height: int) -> int`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "viewport_top" -v`

- [ ] **Test**: `test_compute_line_diff_accounts_for_viewport()` — cursor positioning with viewport offset
- [ ] **Implement**: `TUI._compute_line_diff(self, target_row: int, prev_viewport_top: int, viewport_top: int) -> int`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_compute_line_diff_accounts_for_viewport -v`

### Append Optimization

- [ ] **Test**: `test_detect_append_start()` — pure append returns append_start=True
- [ ] **Test**: `test_detect_edit_not_append()` — middle edit returns append_start=False
- [ ] **Implement**: `TUI._detect_append(self, new_lines: list[str], prev_lines: dict[int, str], first_changed: int) -> bool`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "detect_append" -v`

- [ ] **Test**: `test_append_uses_newline_scrolling()` — append writes \r\n not cursor positioning
- [ ] **Test**: `test_append_with_viewport_shift()` — scrollback handled via terminal natural scroll
- [ ] **Implement**: Append path with `\r\n` for terminal natural scrolling
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "append_uses" -v`

### Scrollback-Aware Redraw (CRITICAL)

- [ ] **Test**: `test_edit_in_scrollback_triggers_full_redraw()` — first_changed < viewport_top triggers clear
- [ ] **Test**: `test_edit_in_viewport_does_not_clear()` — first_changed >= viewport_top uses diff
- [ ] **Implement**: `TUI._is_scrollback_edit(self, first_changed: int, viewport_top: int) -> bool`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "scrollback" -v`

- [ ] **Test**: `test_mixed_scrollback_edit_and_append_triggers_full_redraw()` — full redraw takes precedence
- [ ] **Implement**: Scrollback edit detection takes precedence over append optimization
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_mixed_scrollback_edit_and_append_triggers_full_redraw -v`

- [ ] **Test**: `test_clear_on_shrink_true()` — full clear when content shrinks
- [ ] **Test**: `test_clear_on_shrink_false()` — differential clear when content shrinks
- [ ] **Implement**: `clear_on_shrink: bool` parameter in TUI config
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "clear_on_shrink" -v`

### Line Overflow Protection

- [ ] **Test**: `test_line_overflow_raises_error()` — line exceeding width raises LineOverflowError
- [ ] **Test**: `test_line_overflow_includes_context()` — error shows row, width, content
- [ ] **Implement**: `LineOverflowError` exception and width validation in `_output_line()`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "overflow" -v`

- [ ] **Test**: `test_render_error_shows_overlay()` — component render error displays error overlay
- [ ] **Implement**: Error overlay display in `render_frame()` exception handler
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_render_error_shows_overlay -v`

### Component Position Tracking

- [ ] **Test**: `test_component_rect_set_during_render()` — _rect populated after render_frame()
- [ ] **Implement**: TUI sets `component._rect` during render with absolute (x, y, width, height)
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_component_rect_set_during_render -v`

- [ ] **Test**: `test_invalidate_component_clears_rect_lines()` — specific rows removed from _previous_lines
- [ ] **Implement**: `TUI.invalidate_component(self, component: Component)`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_invalidate_component_clears_rect_lines -v`

### Hardware Cursor Management

- [ ] **Test**: `test_hardware_cursor_tracked_per_write()` — _hardware_cursor_row/col updated after each line
- [ ] **Test**: `test_hardware_cursor_reset_on_render_start()` — cursor reset to (0,0) before diff output
- [ ] **Implement**: Explicit cursor tracking in `_output_line()` and `_output_diff()`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "hardware_cursor" -v`

- [ ] **Test**: `test_hardware_cursor_for_overlay_focus()` — absolute positioning for overlay content
- [ ] **Implement**: Absolute screen coordinate calculation for overlay-focused components
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_hardware_cursor_for_overlay_focus -v`

### Terminal Resize

- [ ] **Test**: `test_resize_clears_previous_lines()` — _previous_lines cleared on resize
- [ ] **Test**: `test_resize_updates_terminal_dimensions()` — width/height updated
- [ ] **Test**: `test_resize_updates_viewport_top()` — viewport recalculated
- [ ] **Test**: `test_resize_triggers_full_redraw()` — all visible lines re-emitted after resize
- [ ] **Implement**: `TUI.on_resize(self, new_width: int, new_height: int)`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py -k "resize" -v`

### Performance

- [ ] **Test**: `test_frame_render_time_under_16ms()` — render completes within 60 FPS budget
- [ ] **Implement**: Frame timing instrumentation in `render_frame()`
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_frame_render_time_under_16ms -v`

---

## Files to Create/Modify

1. `src/pypitui/tui.py` — TUI class, rendering loop, differential output
2. `src/pypitui/component.py` — Size, RenderedLine, Rect dataclasses
3. `tests/unit/test_tui.py` — TUI rendering tests
4. `tests/mocks.py` — MockTerminal for efficiency testing

---

## Progress

**Phase 2 Status**: 0/28 tasks complete

**Dependencies**: Phase 1 (Terminal Abstraction) must be complete
