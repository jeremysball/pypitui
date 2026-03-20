# Execution Plan: PRD #007 - Phase 6: Overlay System

## Overview
Implement viewport-relative floating UI with Overlay wrapper (NOT a Component), compositing, and z-index ordering.

---

## Phase 6: Overlay System

### OverlayPosition Dataclass

- [x] **Test**: `test_overlay_position_fields()` — row, col, width, height, anchor stored
- [x] **Implement**: `OverlayPosition` dataclass:
  - `row: int` — 0=top, -1=bottom
  - `col: int = 0` — 0=left edge
  - `width: int = -1` — -1=auto-size
  - `height: int = -1` — -1=auto-size
  - `anchor: str | None = None` — "center", "top-left", etc.
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py::test_overlay_position_fields -v`

### Overlay Class (Wrapper, Not Component)

- [x] **Test**: `test_overlay_wraps_component()` — content is Component instance
- [x] **Implement**: `Overlay.__init__(self, content: Component, position: OverlayPosition)`
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py::test_overlay_wraps_component -v`

- [x] **Test**: `test_overlay_visible_flag()` — visible: bool = True
- [x] **Implement**: `Overlay.visible` property
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py::test_overlay_visible_flag -v`

- [x] **Test**: `test_overlay_z_index()` — z_index: int = 0 for stacking
- [x] **Implement**: `Overlay.z_index` property
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py::test_overlay_z_index -v`

### TUI Overlay Management

- [x] **Test**: `test_show_overlay_adds_to_list()` — _overlays grows
- [x] **Test**: `test_show_overlay_pushes_content_focus()` — overlay.content gets focus
- [x] **Implement**: `TUI.show_overlay(self, overlay: Overlay)` — adds to list, pushes overlay.content
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py -k "show_overlay" -v`

- [x] **Test**: `test_close_overlay_removes_from_list()` — _overlays shrinks
- [x] **Test**: `test_close_overlay_pops_content_focus()` — focus restored if overlay.content is current
- [x] **Implement**: `TUI.close_overlay(self, overlay: Overlay)` — removes, pops focus
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py -k "close_overlay" -v`

- [x] **Test**: `test_nested_overlays_stack_focus()` — multiple overlays push/pop correctly
- [x] **Implement**: Nested overlay support via focus stack
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py::test_nested_overlays_stack_focus -v`

### Overlay Position Resolution

- [x] **Test**: `test_resolve_position_absolute()` — row=5, col=10 → screen coordinates
- [x] **Test**: `test_resolve_position_negative()` — row=-1 → bottom row
- [x] **Test**: `test_resolve_position_clamping()` — position clamped to terminal bounds
- [x] **Implement**: `TUI._resolve_position(pos: OverlayPosition) -> tuple[int, int, int, int]`
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py -k "resolve_position" -v`

### Overlay Compositing

- [x] **Test**: `test_composite_overlay_stamps_content()` — overlay lines merged into buffer
- [x] **Test**: `test_composite_overlay_respects_position()` — content at resolved offset
- [x] **Implement**: `TUI._composite_overlay()` for merging overlay onto base UI
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py -k "composite_overlay" -v`

- [x] **Test**: `test_composite_overlay_clipping()` — content past terminal bounds truncated
- [x] **Implement**: Clipping to terminal bounds
- [x] **Run**: `uv run pytest tests/unit/test_overlay.py::test_composite_overlay_clipping -v`

---

## Files Created

1. ✅ `src/pypitui/overlay.py` — Overlay class, OverlayPosition dataclass
2. ✅ `src/pypitui/tui.py` — Extended TUI with overlay methods
3. ✅ `tests/unit/test_overlay.py` — 18 overlay tests

---

## Progress

**Phase 6 Status**: 15/15 tasks ✅ COMPLETE

**Test Results**:
- Overlay: 18 tests passing, 100% coverage
- Position resolution with relative/negative coordinates
- Compositing with clipping to terminal bounds
- Focus management integration

**Total**: 193 tests passing, 93% overall coverage

**Dependencies**: Phase 5 (Focus Management) complete ✅
