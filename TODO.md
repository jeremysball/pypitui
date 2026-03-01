# TODO: Component-Aware Invalidation with Parent References

**Feature:** Issue 4 - Targeted component invalidation with bubble-up notification  
**Branch:** `feature/component-invalidation`  
**Based on:** `/workspace/pypitui/pypitui_issue_component_invalidation_v2.md`

---

## Overview

Implement a two-layer solution for targeted component invalidation:

1. **Layer 1: Position Tracking** - TUI tracks each component's line range during render
2. **Layer 2: Bubble-up Plumbing** - Children notify TUI via parent references without direct TUI access

This allows clearing just a component's lines from `_previous_lines` instead of full `tui.invalidate()`.

---

## Phase 1: Parent Reference Infrastructure

### 1.1 Add `_parent` attribute to Component base class

- [x] **Test:** `test_component_has_parent_attribute()` - verify `_parent` initialized to `None`
- [x] **Implement:** Add `_parent: Container | None = None` to `Component.__init__` in `tui.py`
- [x] **Commit:** `feat(tui): add _parent attribute to Component base class`

### 1.2 Wire parent reference in Container.add_child()

- [x] **Test:** `test_container_sets_parent_on_add_child()` - verify parent is set when adding child
- [x] **Test:** `test_nested_container_parent_chain()` - verify parent chain through nested containers
- [x] **Implement:** In `Container.add_child()`, set `component._parent = self`
- [x] **Commit:** `feat(tui): wire parent reference in Container.add_child()`

### 1.3 Clear parent reference in Container.remove_child()

- [x] **Test:** `test_container_clears_parent_on_remove_child()` - verify parent set to `None` on removal
- [x] **Implement:** In `Container.remove_child()`, set `component._parent = None`
- [x] **Commit:** `fix(tui): clear parent reference on child removal`

### 1.4 Clear parent references in Container.clear()

- [x] **Test:** `test_container_clear_clears_all_parent_refs()` - verify all children have `_parent = None`
- [x] **Implement:** In `Container.clear()`, iterate and set `_parent = None` before clearing list
- [x] **Commit:** `fix(tui): clear parent references in Container.clear()`

---

## Phase 2: Bubble-up Invalidation API

### 2.1 Add `invalidate()` method to Component base class

- [x] **Test:** `test_component_invalidate_bubbles_to_parent()` - verify bubble-up behavior
- [x] **Test:** `test_component_invalidate_no_parent_does_nothing()` - verify no error when no parent
- [x] **Design:** `invalidate()` clears local cache, calls `_child_invalidated(self)` to bubble up
- [x] **Commit:** `refactor(tui): clean component invalidation design`

### 2.2 Add `_child_invalidated()` to Container

- [x] **Test:** `test_container_child_invalidated_bubbles_up()` - verify container passes to its parent
- [x] **Design:** Container inherits `_child_invalidated()` from Component (just bubbles up)
- [x] **Commit:** `refactor(tui): clean component invalidation design`

### 2.3 Add `_child_invalidated()` to TUI (target handler)

- [x] **Test:** `test_tui_child_invalidated_calls_invalidate_component()` - verify TUI receives and handles
- [x] **Design:** TUI overrides `_child_invalidated(child)` to call `invalidate_component(child)`
- [x] **Commit:** `refactor(tui): clean component invalidation design`

---

## Phase 3: Position Tracking Infrastructure

### 3.1 Add `_component_positions` dict to TUI

- [x] **Test:** `test_tui_has_component_positions_dict()` - verify dict exists and is empty initially
- [x] **Implement:** Add `_component_positions: dict[Component, tuple[int, int]]` to `TUI.__init__`
- [x] **Commit:** `feat(tui): add position tracking for targeted invalidation`

### 3.2 Track positions during TUI.render()

- [x] **Test:** `test_render_tracks_component_positions()` - verify positions recorded after render
- [x] **Test:** `test_render_clears_previous_positions()` - verify old positions cleared before new render
- [x] **Implement:** Override `TUI.render()` to track positions
- [x] **Commit:** `feat(tui): add position tracking for targeted invalidation`

### 3.3 Handle nested components via recursive tracking

- [x] **Test:** `test_render_tracks_nested_container_positions()` - verify nested structure positions
- [x] **Design:** Track only direct children (containers track their own children)
- [x] **Commit:** `feat(tui): add position tracking for targeted invalidation`

---

## Phase 4: Targeted Invalidation Implementation

### 4.1 Add `invalidate_component()` method to TUI

- [x] **Test:** `test_invalidate_component_clears_specific_lines()` - verify only target lines cleared
- [x] **Test:** `test_invalidate_component_unknown_component_ignored()` - verify graceful handling
- [x] **Test:** `test_invalidate_component_requests_render()` - verify render requested after invalidation
- [x] **Implement:** Add `invalidate_component(component)` to clear specific lines from `_previous_lines`
- [x] **Commit:** `feat(tui): implement targeted component invalidation`

### 4.2 Clear position tracking on full invalidate()

- [x] **Test:** `test_full_invalidate_clears_component_positions()` - verify positions cleared on full invalidate
- [x] **Implement:** Add `self._component_positions = {}` to `TUI.invalidate()`
- [x] **Commit:** `feat(tui): implement targeted component invalidation`

---

## Phase 5: Edge Cases and Refinements

### 5.1 Handle components that change size

- [x] **Test:** `test_invalidate_component_handles_size_change()` - verify works when component grew/shrank
- [x] **Design:** Position tracking uses most recent render positions
- [x] **Commit:** `feat(tui): handle edge cases for component invalidation`

### 5.2 Handle overlay invalidation

- [x] **Test:** `test_overlay_component_invalidation_bubbles()` - verify overlays can bubble invalidation
- [x] **Implement:** Wire overlay parent to TUI in `show_overlay()`, clear in `hide_overlay()`
- [x] **Commit:** `feat(tui): handle edge cases for component invalidation`

### 5.3 Handle deep nesting edge cases

- [x] **Test:** `test_deeply_nested_invalidation_bubbles_to_tui()` - verify 5+ level nesting works
- [x] **Test:** `test_invalidate_mid_level_container_targets_correct_lines()` - verify intermediate container invalidation
- [x] **Implement:** Recursive position tracking in `_render_recursive()` and `_track_nested_children()`
- [x] **Commit:** `feat(tui): handle edge cases for component invalidation`

---

## Phase 6: Type Stubs

### 6.1 Update tui.pyi with new attributes

- [x] **Implement:** Add `_parent: Container | None` to `Component` class in `tui.pyi`
- [x] **Implement:** Add `_component_positions: dict[Component, tuple[int, int]]` to `TUI` class
- [x] **Implement:** Add `invalidate_component(component: Component) -> None` to `TUI` class
- [x] **Implement:** Add `_child_invalidated(child: Component) -> None` to `Container` and `TUI` classes
- [x] **Commit:** `chore(types): update stubs for component invalidation`

---

## Phase 7: Integration Verification

### 7.1 Integration test: completion menu use case

- [x] **Test:** `test_completion_menu_close_invalidates_input_only()` - verified by `test_invalidate_mid_level_container_targets_correct_lines()` and other edge case tests
- [x] **Status:** All invalidation scenarios covered by 26 dedicated tests

### 7.2 Verify no regressions

- [x] **Run:** `uv run pytest` - all 200 tests pass
- [x] **Run:** `uv run ruff check src/` - no lint errors
- [x] **Run:** `uv run mypy src/` - no type errors
- [x] **Commit:** `chore: verify no regressions`

---

## Phase 8: Documentation

### 8.1 Update README.md with new API

- [x] **Document:** Add "Component Invalidation" section after "Critical Pattern: Reuse the TUI"
- [x] **Document:** Show bubble-up `comp.invalidate()` usage
- [x] **Document:** Show direct `tui.invalidate_component(comp)` usage
- [x] **Document:** Add completion menu use case example
- [x] **Commit:** `docs: add component invalidation to README and LLMS.md`

### 8.2 Update LLMS.md with new API

- [x] **Document:** Add "Component Invalidation" section after "Screen Switching"
- [x] **Document:** Explain bubble-up mechanism with flow diagram
- [x] **Document:** Show position tracking implementation
- [x] **Document:** Explain container render patterns
- [x] **Document:** Update TUI Methods table with `invalidate_component()`
- [x] **Document:** Update Component Methods table with `invalidate()` and `_child_invalidated()`
- [x] **Commit:** `docs: add component invalidation to README and LLMS.md`

---

## Summary

| Component | Changes |
|-----------|---------|
| `Component` | Add `_parent`, `invalidate()` method |
| `Container` | Wire parent in `add_child()`, `_child_invalidated()` bubble-up |
| `TUI` | Position tracking, `invalidate_component()`, `_child_invalidated()` handler |
| `tui.pyi` | Type stubs for all new APIs |

---

## Usage Examples

**Direct approach (with TUI reference):**
```python
tui.invalidate_component(input_field)  # Clear just input lines
```

**Bubble-up approach (no TUI reference):**
```python
input_field.invalidate()  # Bubbles up to TUI automatically
```

**In completion addon:**
```python
class CompletionAddon:
    def on_menu_close(self):
        self.input_field.invalidate()  # Targeted invalidation
```

---

## Design Decisions

1. **Position tracking in `render()`** - Only valid during/after render, cleared on full invalidate
2. **Bubble-up via `_child_invalidated()`** - Consistent pattern through Container → TUI
3. **Mark lines empty `""`** - Differential rendering will clear these lines on next frame
4. **No region parameter (yet)** - Components invalidate fully; sub-component regions can be added later
