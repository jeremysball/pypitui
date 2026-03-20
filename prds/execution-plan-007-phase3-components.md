# Execution Plan: PRD #007 - Phase 3: Component Base & Container

## Overview
Implement the Component abstract base class, Container for vertical layout, Text component with wrapping, and wide character support via wcwidth.

---

## Phase 3: Component Base & Container

### Component ABC

- [x] **Test**: `test_component_abstract_methods()` — cannot instantiate without measure/render
- [x] **Implement**: `Component` ABC with `measure()`, `render()`, `invalidate()`
- [x] **Run**: `uv run pytest tests/unit/test_component.py::test_component_abstract_methods -v`

- [x] **Test**: `test_component_invalidation_bubbles()` — invalidate() calls _child_invalidated()
- [x] **Implement**: `Component.invalidate(self)` and `_child_invalidated(self, child)`
- [x] **Run**: `uv run pytest tests/unit/test_component.py::test_component_invalidation_bubbles -v`

- [x] **Test**: `test_component_rect_field_exists()` — _rect: Rect stores position and dimensions
- [x] **Implement**: `Component._rect: Rect` field for TUI to set during render
- [x] **Run**: `uv run pytest tests/unit/test_component.py::test_component_rect_field_exists -v`

### Container Component

- [x] **Test**: `test_container_measure_returns_sum_of_children()` — height = sum(child heights)
- [x] **Implement**: `Container.measure(self, available_width: int, available_height: int) -> Size`
- [x] **Run**: `uv run pytest tests/unit/test_components.py::test_container_measure_returns_sum_of_children -v`

- [x] **Test**: `test_container_render_stacks_vertically()` — children rendered sequentially
- [x] **Implement**: `Container.render(self, width: int) -> list[RenderedLine]`
- [x] **Run**: `uv run pytest tests/unit/test_components.py::test_container_render_stacks_vertically -v`

- [x] **Test**: `test_container_add_child_appends_to_list()` — children list grows
- [x] **Implement**: `Container.add_child(self, component: Component)`
- [x] **Run**: `uv run pytest tests/unit/test_components.py::test_container_add_child_appends_to_list -v`

- [x] **Test**: `test_container_clear_children()` — children list emptied
- [x] **Implement**: `Container.clear_children(self)`
- [x] **Run**: `uv run pytest tests/unit/test_components.py::test_container_clear_children -v`

### Text Component

- [x] **Test**: `test_text_measure_single_line()` — height=1 for simple text
- [x] **Test**: `test_text_measure_multi_line()` — height=n for n lines
- [x] **Implement**: `Text.measure(self, available_width: int, available_height: int) -> Size`
- [x] **Run**: `uv run pytest tests/unit/test_components.py -k "test_text_measure" -v`

- [x] **Test**: `test_text_render_returns_lines()` — returns list of RenderedLine
- [x] **Test**: `test_text_render_wraps_long_lines()` — wrapping at width boundary using wcwidth
- [x] **Implement**: `Text.render(self, width: int) -> list[RenderedLine]` with proper wide char handling
- [x] **Run**: `uv run pytest tests/unit/test_components.py -k "test_text_render" -v`

- [x] **Test**: `test_text_content_mutable()` — set_text updates content and invalidates
- [x] **Implement**: `Text.set_text(self, text: str)` with invalidation
- [x] **Run**: `uv run pytest tests/unit/test_components.py::test_text_content_mutable -v`

### Wide Character Support

- [x] **Test**: `test_wcwidth_emoji()` — emoji counted as width 2
- [x] **Test**: `test_wcwidth_cjk()` — CJK characters counted as width 2
- [x] **Test**: `test_truncate_to_width_respects_wide_chars()` — never splits wide chars
- [x] **Test**: `test_wide_char_at_boundary_excluded()` — wide chars at exact width boundary are excluded
- [x] **Implement**: `truncate_to_width(text: str, width: int) -> str` using wcwidth
- [x] **Run**: `uv run pytest tests/unit/test_utils.py -k "truncate" -v`

- [x] **Test**: `test_slice_by_width_atomic()` — wide chars treated as atomic units
- [x] **Implement**: `slice_by_width(text: str, start: int, end: int) -> str`
- [x] **Run**: `uv run pytest tests/unit/test_utils.py::test_slice_by_width_atomic -v`

---

## Files Created/Modified

1. ✅ `src/pypitui/component.py` — Component ABC (extends Phase 2)
2. ✅ `src/pypitui/components/container.py` — Container component
3. ✅ `src/pypitui/components/text.py` — Text component
4. ✅ `src/pypitui/utils.py` — truncate_to_width, slice_by_width, wcwidth wrappers
5. ✅ `tests/unit/test_component.py` — Component ABC tests
6. ✅ `tests/unit/test_components.py` — Container and Text tests
7. ✅ `tests/unit/test_utils.py` — Utility function tests

---

## Progress

**Phase 3 Status**: 17/17 tasks ✅ COMPLETE

**Test Results**: 115 tests passing, 91% coverage

**Dependencies**: Phase 2 (Rendering Engine) complete
