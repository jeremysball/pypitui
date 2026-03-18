# Execution Plan: PRD #007 - Phase 4: Interactive Components

## Overview
Implement Input, SelectList with SelectItem, and BorderedBox components with E2E testing.

---

## Phase 4: Interactive Components

### Input Component

- [ ] **E2E Test**: `test_input_typing_renders_text()` — type "hello", see "hello" on screen
- [ ] **Implement**: `Input.__init__()` with placeholder, max_length
- [ ] **Run**: E2E test via tmux automation

- [ ] **Test**: `test_input_measure_returns_one_line()` — height=1 always
- [ ] **Implement**: `Input.measure()`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_input_measure_returns_one_line -v`

- [ ] **Test**: `test_input_render_shows_content()` — typed text appears in render
- [ ] **Test**: `test_input_render_shows_placeholder_when_empty()` — placeholder visible
- [ ] **Implement**: `Input.render(self, width: int) -> list[RenderedLine]`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py -k "test_input_render" -v`

- [ ] **Test**: `test_input_handle_key_appends_char()` — "a" typed adds "a" to content
- [ ] **Test**: `test_input_handle_backspace_removes_char()` — backspace removes last char
- [ ] **Test**: `test_input_handle_input_returns_bool()` — returns True when consuming input
- [ ] **Implement**: `Input.handle_input(self, data: bytes) -> bool`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py -k "test_input_handle" -v`

- [ ] **Test**: `test_input_cursor_position_relative()` — returns (row, col) relative to component origin
- [ ] **Implement**: `Input.get_cursor_position(self) -> tuple[int, int] | None`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_input_cursor_position_relative -v`

- [ ] **Test**: `test_input_on_submit_callback()` — Enter triggers on_submit
- [ ] **Implement**: `Input.on_submit` callback field
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_input_on_submit_callback -v`

### SelectItem Dataclass

- [ ] **Test**: `test_selectitem_creation()` — id and label stored
- [ ] **Implement**: `SelectItem` dataclass with `id: str`, `label: str`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_selectitem_creation -v`

### SelectList Component

- [ ] **E2E Test**: `test_selectlist_navigation()` — Down arrow moves selection
- [ ] **Implement**: `SelectList.__init__(self, items: list[SelectItem], max_visible: int)`
- [ ] **Run**: E2E test via tmux automation

- [ ] **Test**: `test_selectlist_measure_respects_max_visible()` — height = min(len(items), max_visible)
- [ ] **Implement**: `SelectList.measure()`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_selectlist_measure_respects_max_visible -v`

- [ ] **Test**: `test_selectlist_render_shows_items()` — all visible items rendered
- [ ] **Test**: `test_selectlist_render_highlights_selected()` — selected item has different style
- [ ] **Implement**: `SelectList.render()` with selection highlighting
- [ ] **Run**: `uv run pytest tests/unit/test_components.py -k "test_selectlist_render" -v`

- [ ] **Test**: `test_selectlist_handle_down_moves_selection()` — selection index increments
- [ ] **Test**: `test_selectlist_handle_up_moves_selection()` — selection index decrements
- [ ] **Test**: `test_selectlist_wraps_at_boundaries()` — Up at top wraps to bottom, vice versa
- [ ] **Test**: `test_selectlist_handle_input_returns_bool()` — returns True when consuming input
- [ ] **Implement**: `SelectList.handle_input(data: bytes) -> bool` for Up/Down/Enter
- [ ] **Run**: `uv run pytest tests/unit/test_components.py -k "test_selectlist_handle" -v`

### BorderedBox Component

- [ ] **E2E Test**: `test_borderedbox_renders_frame()` — box appears around content
- [ ] **Implement**: `BorderedBox.__init__(self, title: str | None = None)`
- [ ] **Run**: E2E test via tmux automation

- [ ] **Test**: `test_borderedbox_measure_adds_border()` — width + 2, height + 2
- [ ] **Implement**: `BorderedBox.measure()` accounting for borders
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_borderedbox_measure_adds_border -v`

- [ ] **Test**: `test_borderedbox_render_draws_box_drawing_chars()` — ┌─┐│ etc.
- [ ] **Test**: `test_borderedbox_render_shows_title()` — title appears in top border
- [ ] **Implement**: `BorderedBox.render()` with box-drawing characters
- [ ] **Run**: `uv run pytest tests/unit/test_components.py -k "test_borderedbox_render" -v`

- [ ] **Test**: `test_borderedbox_add_child()` — single child stored
- [ ] **Implement**: `BorderedBox.add_child(self, component: Component)`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_borderedbox_add_child -v`

---

## Files to Create/Modify

1. `src/pypitui/components/input.py` — Input component
2. `src/pypitui/components/select.py` — SelectList and SelectItem
3. `src/pypitui/components/bordered.py` — BorderedBox component
4. `tests/unit/test_components.py` — Interactive component tests
5. `tests/e2e/test_input.py` — E2E input tests
6. `tests/e2e/test_select.py` — E2E select tests

---

## Progress

**Phase 4 Status**: 0/16 tasks complete

**Dependencies**: Phase 3 (Component Base) must be complete
