# Execution Plan: PRD #007 - Phase 3: Component Base & Container

## Overview
Implement the Component abstract base class, Container for vertical layout, Text component with wrapping, and wide character support via wcwidth.

---

## Phase 3: Component Base & Container

### Component ABC

- [ ] **Test**: `test_component_abstract_methods()` — cannot instantiate without measure/render
- [ ] **Implement**: `Component` ABC with `measure()`, `render()`, `invalidate()`
- [ ] **Run**: `uv run pytest tests/unit/test_component.py::test_component_abstract_methods -v`

- [ ] **Test**: `test_component_invalidation_bubbles()` — invalidate() calls _child_invalidated()
- [ ] **Implement**: `Component.invalidate(self)` and `_child_invalidated(self, child)`
- [ ] **Run**: `uv run pytest tests/unit/test_component.py::test_component_invalidation_bubbles -v`

- [ ] **Test**: `test_component_rect_field_exists()` — _rect: Rect stores position and dimensions
- [ ] **Implement**: `Component._rect: Rect` field for TUI to set during render
- [ ] **Run**: `uv run pytest tests/unit/test_component.py::test_component_rect_field_exists -v`

### Container Component

- [ ] **Test**: `test_container_measure_returns_sum_of_children()` — height = sum(child heights)
- [ ] **Implement**: `Container.measure(self, available_width: int, available_height: int) -> Size`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_container_measure_returns_sum_of_children -v`

- [ ] **Test**: `test_container_render_stacks_vertically()` — children rendered sequentially
- [ ] **Implement**: `Container.render(self, width: int) -> list[RenderedLine]`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_container_render_stacks_vertically -v`

- [ ] **Test**: `test_container_add_child_appends_to_list()` — children list grows
- [ ] **Implement**: `Container.add_child(self, component: Component)`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_container_add_child_appends_to_list -v`

- [ ] **Test**: `test_container_clear_children()` — children list emptied
- [ ] **Implement**: `Container.clear_children(self)`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_container_clear_children -v`

### Text Component

- [ ] **Test**: `test_text_measure_single_line()` — height=1 for simple text
- [ ] **Test**: `test_text_measure_multi_line()` — height=n for n lines
- [ ] **Implement**: `Text.measure(self, available_width: int, available_height: int) -> Size`
- [ ] **Run**: `uv run pytest tests/unit/test_components.py -k "test_text_measure" -v`

- [ ] **Test**: `test_text_render_returns_lines()` — returns list of RenderedLine
- [ ] **Test**: `test_text_render_wraps_long_lines()` — wrapping at width boundary using wcwidth
- [ ] **Implement**: `Text.render(self, width: int) -> list[RenderedLine]` with proper wide char handling
- [ ] **Run**: `uv run pytest tests/unit/test_components.py -k "test_text_render" -v`

- [ ] **Test**: `test_text_content_mutable()` — set_text updates content and invalidates
- [ ] **Implement**: `Text.set_text(self, text: str)` with invalidation
- [ ] **Run**: `uv run pytest tests/unit/test_components.py::test_text_content_mutable -v`

### Wide Character Support

- [ ] **Test**: `test_wcwidth_emoji()` — emoji counted as width 2
- [ ] **Test**: `test_wcwidth_cjk()` — CJK characters counted as width 2
- [ ] **Test**: `test_truncate_to_width_respects_wide_chars()` — never splits wide chars
- [ ] **Test**: `test_wide_char_at_boundary_excluded()` — wide chars at exact width boundary are excluded
- [ ] **Implement**: `truncate_to_width(text: str, width: int) -> str` using wcwidth
- [ ] **Run**: `uv run pytest tests/unit/test_utils.py -k "truncate" -v`

- [ ] **Test**: `test_slice_by_width_atomic()` — wide chars treated as atomic units
- [ ] **Implement**: `slice_by_width(text: str, start: int, end: int) -> str`
- [ ] **Run**: `uv run pytest tests/unit/test_utils.py::test_slice_by_width_atomic -v`

---

## Files to Create/Modify

1. `src/pypitui/component.py` — Component ABC (extends Phase 2)
2. `src/pypitui/components/container.py` — Container component
3. `src/pypitui/components/text.py` — Text component
4. `src/pypitui/utils.py` — truncate_to_width, slice_by_width, wcwidth wrappers
5. `tests/unit/test_component.py` — Component ABC tests
6. `tests/unit/test_components.py` — Container and Text tests
7. `tests/unit/test_utils.py` — Utility function tests

---

## Progress

**Phase 3 Status**: 0/17 tasks complete

**Dependencies**: Phase 2 (Rendering Engine) must be complete
