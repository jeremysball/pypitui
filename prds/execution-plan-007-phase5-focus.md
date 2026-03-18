# Execution Plan: PRD #007 - Phase 5: Focus Management

## Overview
Implement stack-based focus management for overlays/context and tab order cycling for keyboard navigation.

---

## Phase 5: Focus Management

### Focus Stack (LIFO for Overlay/Context Management)

- [ ] **Test**: `test_focus_stack_empty_returns_none()` — _focused is None initially
- [ ] **Test**: `test_push_focus_adds_to_stack()` — stack grows
- [ ] **Implement**: `TUI.push_focus(self, component: Component | None)`
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py -k "push_focus" -v`

- [ ] **Test**: `test_push_focus_calls_on_blur_on_previous()` — previous.on_blur() invoked
- [ ] **Test**: `test_push_focus_calls_on_focus_on_new()` — component.on_focus() invoked
- [ ] **Test**: `test_push_focus_invalidates_both()` — invalidate called on both components
- [ ] **Implement**: Full lifecycle: on_blur() previous, on_focus() new, invalidation
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py -k "lifecycle" -v`

- [ ] **Test**: `test_push_focus_error_restores_previous()` — pop on error, restore previous focus
- [ ] **Implement**: Error handling: pop and restore on on_focus() failure
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py::test_push_focus_error_restores_previous -v`

- [ ] **Test**: `test_pop_focus_removes_from_stack()` — stack shrinks
- [ ] **Test**: `test_pop_focus_returns_popped_component()` — returns correct component
- [ ] **Implement**: `TUI.pop_focus(self) -> Component | None`
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py -k "pop_focus" -v`

- [ ] **Test**: `test_pop_focus_calls_on_blur()` — component.on_blur() invoked
- [ ] **Test**: `test_pop_focus_calls_on_focus_on_previous()` — previous.on_focus() restored
- [ ] **Implement**: on_blur() lifecycle and previous restore
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py -k "pop_focus_calls" -v`

- [ ] **Test**: `test_set_focus_pops_then_pushes()` — replaces current focus
- [ ] **Implement**: `TUI.set_focus(self, component: Component | None)`
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py::test_set_focus_pops_then_pushes -v`

### Focus Order (Tab Cycling)

- [ ] **Test**: `test_register_focusable_adds_to_order()` — _focus_order list grows
- [ ] **Implement**: `TUI.register_focusable(self, component: Component)`
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py::test_register_focusable_adds_to_order -v`

- [ ] **Test**: `test_cycle_focus_moves_to_next()` — Tab moves to next in order
- [ ] **Test**: `test_cycle_focus_wraps_around()` — last to first wraps
- [ ] **Implement**: `TUI.cycle_focus(self, direction: int = 1)`
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py -k "cycle_focus" -v`

### Focusable Protocol

- [ ] **Test**: `test_focusable_components_have_on_focus()` — Focusable protocol check
- [ ] **Implement**: `@runtime_checkable class Focusable(Protocol)` with `on_focus()`, `on_blur()`, `handle_input() -> bool`
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py::test_focusable_components_have_on_focus -v`

- [ ] **Test**: `test_focusable_get_cursor_position()` — returns relative position for IME
- [ ] **Implement**: `Focusable.get_cursor_position(self) -> tuple[int, int] | None`
- [ ] **Run**: `uv run pytest tests/unit/test_focus.py::test_focusable_get_cursor_position -v`

---

## Files to Create/Modify

1. `src/pypitui/tui.py` — Extend TUI with focus methods (extends Phase 2)
2. `src/pypitui/component.py` — Focusable protocol
3. `tests/unit/test_focus.py` — Focus management tests

---

## Progress

**Phase 5 Status**: 0/15 tasks complete

**Dependencies**: Phase 4 (Interactive Components) must be complete
