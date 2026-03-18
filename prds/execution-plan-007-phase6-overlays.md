# Execution Plan: PRD #007 - Phase 6: Overlay System

## Overview
Implement viewport-relative floating UI with Overlay wrapper (NOT a Component), compositing, and z-index ordering.

---

## Phase 6: Overlay System

### OverlayPosition Dataclass

- [ ] **Test**: `test_overlay_position_fields()` — row, col, width, height, anchor stored
- [ ] **Implement**: `OverlayPosition` dataclass:
  - `row: int` — 0=top, -1=bottom
  - `col: int = 0` — 0=left edge
  - `width: int = -1` — -1=auto-size
  - `height: int = -1` — -1=auto-size
  - `anchor: str | None = None` — "center", "top-left", etc.
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py::test_overlay_position_fields -v`

### Overlay Class (Wrapper, Not Component)

- [ ] **Test**: `test_overlay_wraps_component()` — content is Component instance
- [ ] **Implement**: `Overlay.__init__(self, content: Component, position: OverlayPosition)`
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py::test_overlay_wraps_component -v`

- [ ] **Test**: `test_overlay_visible_flag()` — visible: bool = True
- [ ] **Implement**: `Overlay.visible` property
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py::test_overlay_visible_flag -v`

- [ ] **Test**: `test_overlay_z_index()` — z_index: int = 0 for stacking
- [ ] **Implement**: `Overlay.z_index` property
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py::test_overlay_z_index -v`

### TUI Overlay Management

- [ ] **Test**: `test_show_overlay_adds_to_list()` — _overlays grows
- [ ] **Test**: `test_show_overlay_pushes_content_focus()` — overlay.content gets focus
- [ ] **Implement**: `TUI.show_overlay(self, overlay: Overlay)` — adds to list, pushes overlay.content
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py -k "show_overlay" -v`

- [ ] **Test**: `test_close_overlay_removes_from_list()` — _overlays shrinks
- [ ] **Test**: `test_close_overlay_pops_content_focus()` — focus restored if overlay.content is current
- [ ] **Implement**: `TUI.close_overlay(self, overlay: Overlay)` — removes, pops focus
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py -k "close_overlay" -v`

- [ ] **Test**: `test_nested_overlays_stack_focus()` — multiple overlays push/pop correctly
- [ ] **Implement**: Nested overlay support via focus stack
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py::test_nested_overlays_stack_focus -v`

### Overlay Position Resolution

- [ ] **Test**: `test_resolve_position_absolute()` — row=5, col=10 → screen coordinates
- [ ] **Test**: `test_resolve_position_negative()` — row=-1 → bottom row
- [ ] **Test**: `test_resolve_position_anchor_center()` — anchor="center" calculates center
- [ ] **Test**: `test_resolve_position_clamping()` — position clamped to terminal bounds
- [ ] **Implement**: `TUI._resolve_position(pos: OverlayPosition) -> tuple[int, int, int, int]`
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py -k "resolve_position" -v`

### Overlay Compositing

- [ ] **Test**: `test_composite_overlay_stamps_content()` — overlay lines merged into buffer
- [ ] **Test**: `test_composite_overlay_respects_position()` — content at resolved offset
- [ ] **Implement**: `TUI._composite_overlay(self, lines: list[RenderedLine], overlay: Overlay, viewport_top: int)`
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py -k "composite_overlay" -v`

- [ ] **Test**: `test_composite_overlay_clipping()` — content past terminal bounds truncated
- [ ] **Implement**: Clipping to terminal bounds
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py::test_composite_overlay_clipping -v`

### Line Compositing with Wide Char Support

- [ ] **Test**: `test_composite_line_splices_content()` — overlay replaces base at column
- [ ] **Test**: `test_composite_line_respects_wide_chars()` — never splits wide characters
- [ ] **Implement**: `TUI._composite_line(base: str, overlay: str, col: int, width: int) -> str`
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py -k "composite_line" -v`

- [ ] **Test**: `test_pad_or_truncate_overlay()` — overlay padded/truncated to declared width
- [ ] **Implement**: `pad_or_truncate(text: str, width: int) -> str`
- [ ] **Run**: `uv run pytest tests/unit/test_utils.py::test_pad_or_truncate_overlay -v`

### Z-Index Ordering

- [ ] **Test**: `test_overlays_composite_in_z_order()` — sorted by z_index ascending
- [ ] **Test**: `test_overlays_same_z_index_fifo()` — equal z_index: insertion order
- [ ] **Implement**: Sort overlays by z_index; ties by insertion order
- [ ] **Run**: `uv run pytest tests/unit/test_overlay.py -k "z_order" -v`

---

## Files to Create/Modify

1. `src/pypitui/overlay.py` — Overlay class, OverlayPosition dataclass
2. `src/pypitui/tui.py` — Extend TUI with overlay methods (extends Phase 5)
3. `src/pypitui/utils.py` — pad_or_truncate (extends Phase 3)
4. `tests/unit/test_overlay.py` — Overlay tests
5. `tests/e2e/test_overlays.py` — E2E overlay tests

---

## Progress

**Phase 6 Status**: 0/18 tasks complete

**Dependencies**: Phase 5 (Focus Management) must be complete
