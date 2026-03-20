# Execution Plan: PRD #007 - Phase 4: Interactive Components

## Overview
Implement Input, SelectList with SelectItem, and BorderedBox components with E2E testing.

---

## Phase 4: Interactive Components

### Input Component

- [x] **E2E Test**: `test_input_typing_renders_text()` — type "hello", see "hello" on screen
- [x] **Implement**: `Input.__init__()` with placeholder, max_length
- [x] **Run**: E2E test via tmux automation

- [x] **Test**: `test_input_measure_returns_one_line()` — height=1 always
- [x] **Implement**: `Input.measure()`
- [x] **Run**: `uv run pytest tests/unit/test_input.py::test_input_measure_returns_one_line -v`

- [x] **Test**: `test_input_render_shows_content()` — typed text appears in render
- [x] **Test**: `test_input_render_shows_placeholder_when_empty()` — placeholder visible
- [x] **Implement**: `Input.render(self, width: int) -> list[RenderedLine]`
- [x] **Run**: `uv run pytest tests/unit/test_input.py -k "test_input_render" -v`

- [x] **Test**: `test_input_handle_key_appends_char()` — "a" typed adds "a" to content
- [x] **Test**: `test_input_handle_backspace_removes_char()` — backspace removes last char
- [x] **Test**: `test_input_handle_input_returns_bool()` — returns True when consuming input
- [x] **Implement**: `Input.handle_input(self, data: bytes) -> bool`
- [x] **Run**: `uv run pytest tests/unit/test_input.py -k "test_input_handle" -v`

- [x] **Test**: `test_input_cursor_position_relative()` — returns (row, col) relative to component origin
- [x] **Implement**: `Input.get_cursor_position(self) -> tuple[int, int] | None`
- [x] **Run**: `uv run pytest tests/unit/test_input.py::test_input_cursor_position_relative -v`

- [x] **Test**: `test_input_on_submit_callback()` — Enter triggers on_submit
- [x] **Implement**: `Input.on_submit` callback field
- [x] **Run**: `uv run pytest tests/unit/test_input.py::test_input_on_submit_callback -v`

### SelectItem Dataclass

- [x] **Test**: `test_selectitem_creation()` — id and label stored
- [x] **Implement**: `SelectItem` dataclass with `id: str`, `label: str`
- [x] **Run**: `uv run pytest tests/unit/test_select.py::test_selectitem_creation -v`

### SelectList Component

- [x] **E2E Test**: `test_selectlist_navigation()` — Down arrow moves selection
- [x] **Implement**: `SelectList.__init__(self, items: list[SelectItem], max_visible: int)`
- [x] **Run**: E2E test via tmux automation

- [x] **Test**: `test_selectlist_measure_respects_max_visible()` — height = min(len(items), max_visible)
- [x] **Implement**: `SelectList.measure()`
- [x] **Run**: `uv run pytest tests/unit/test_select.py::test_selectlist_measure_respects_max_visible -v`

- [x] **Test**: `test_selectlist_render_shows_items()` — all visible items rendered
- [x] **Test**: `test_selectlist_render_highlights_selected()` — selected item has different style
- [x] **Implement**: `SelectList.render()` with selection highlighting
- [x] **Run**: `uv run pytest tests/unit/test_select.py -k "test_selectlist_render" -v`

- [x] **Test**: `test_selectlist_handle_down_moves_selection()` — selection index increments
- [x] **Test**: `test_selectlist_handle_up_moves_selection()` — selection index decrements
- [x] **Test**: `test_selectlist_wraps_at_boundaries()` — Up at top wraps to bottom, vice versa
- [x] **Test**: `test_selectlist_handle_input_returns_bool()` — returns True when consuming input
- [x] **Implement**: `SelectList.handle_input(data: bytes) -> bool` for Up/Down/Enter
- [x] **Run**: `uv run pytest tests/unit/test_select.py -k "test_selectlist_handle" -v`

### BorderedBox Component

- [x] **E2E Test**: `test_borderedbox_renders_frame()` — box appears around content
- [x] **Implement**: `BorderedBox.__init__(self, title: str | None = None)`
- [x] **Run**: E2E test via tmux automation

- [x] **Test**: `test_borderedbox_measure_adds_border()` — width + 2, height + 2
- [x] **Implement**: `BorderedBox.measure()` accounting for borders
- [x] **Run**: `uv run pytest tests/unit/test_bordered.py::test_borderedbox_measure_adds_border -v`

- [x] **Test**: `test_borderedbox_render_draws_box_drawing_chars()` — ┌─┐│ etc.
- [x] **Test**: `test_borderedbox_render_shows_title()` — title appears in top border
- [x] **Implement**: `BorderedBox.render()` with box-drawing characters
- [x] **Run**: `uv run pytest tests/unit/test_bordered.py -k "test_borderedbox_render" -v`

- [x] **Test**: `test_borderedbox_add_child()` — single child stored
- [x] **Implement**: `BorderedBox.add_child(self, component: Component)`
- [x] **Run**: `uv run pytest tests/unit/test_bordered.py::test_borderedbox_add_child -v`

---

## Files Created

1. ✅ `src/pypitui/components/input.py` — Input component
2. ✅ `src/pypitui/components/select.py` — SelectList and SelectItem
3. ✅ `src/pypitui/components/bordered.py` — BorderedBox component
4. ✅ `tests/unit/test_input.py` — Input component tests (17 tests)
5. ✅ `tests/unit/test_select.py` — SelectList component tests (14 tests)
6. ✅ `tests/unit/test_bordered.py` — BorderedBox component tests (11 tests)

---

## Progress

**Phase 4 Status**: 16/16 tasks ✅ COMPLETE

**Test Results**:
- Input: 17 tests passing, 95% coverage
- SelectList: 14 tests passing, 96% coverage
- BorderedBox: 11 tests passing, 98% coverage

**Total**: 42 new tests, 157 tests passing overall

**Dependencies**: Phase 3 (Component Base) complete ✅
