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

- [ ] **Test:** `test_component_invalidate_bubbles_to_parent()` - verify bubble-up behavior
- [ ] **Test:** `test_component_invalidate_no_parent_does_nothing()` - verify no error when no parent
- [ ] **Implement:** Add `invalidate()` to `Component` that calls `self._parent._child_invalidated(self)` if parent exists
- [ ] **Commit:** `feat(tui): add bubble-up invalidate() to Component base class`

### 2.2 Add `_child_invalidated()` to Container

- [ ] **Test:** `test_container_child_invalidated_bubbles_up()` - verify container passes to its parent
- [ ] **Implement:** Add `_child_invalidated(child)` to `Container` that bubbles to `self._parent`
- [ ] **Commit:** `feat(tui): add _child_invalidated() bubble-up to Container`

### 2.3 Add `_child_invalidated()` to TUI (target handler)

- [ ] **Test:** `test_tui_child_invalidated_calls_invalidate_component()` - verify TUI receives and handles
- [ ] **Implement:** Add `_child_invalidated(child)` to `TUI` that calls `self.invalidate_component(child)`
- [ ] **Commit:** `feat(tui): add _child_invalidated() handler to TUI`

---

## Phase 3: Position Tracking Infrastructure

### 3.1 Add `_component_positions` dict to TUI

- [ ] **Test:** `test_tui_has_component_positions_dict()` - verify dict exists and is empty initially
- [ ] **Implement:** Add `_component_positions: dict[Component, tuple[int, int]]` to `TUI.__init__`
- [ ] **Commit:** `feat(tui): add _component_positions tracking dict`

### 3.2 Track positions during TUI.render()

- [ ] **Test:** `test_render_tracks_component_positions()` - verify positions recorded after render
- [ ] **Test:** `test_render_clears_previous_positions()` - verify old positions cleared before new render
- [ ] **Implement:** Override `TUI.render()` to track positions:
  ```python
  def render(self, width: int) -> list[str]:
      self._component_positions = {}  # Clear previous
      lines = []
      for child in self.children:
          start = len(lines)
          child_lines = child.render(width)
          self._component_positions[child] = (start, len(lines))
          lines.extend(child_lines)
      return lines
  ```
- [ ] **Commit:** `feat(tui): track component line positions during render`

### 3.3 Handle nested components via recursive tracking

- [ ] **Test:** `test_render_tracks_nested_container_positions()` - verify nested structure positions
- [ ] **Implement:** Add helper to recursively track positions in nested containers
- [ ] **Commit:** `feat(tui): track positions for nested container children`

---

## Phase 4: Targeted Invalidation Implementation

### 4.1 Add `invalidate_component()` method to TUI

- [ ] **Test:** `test_invalidate_component_clears_specific_lines()` - verify only target lines cleared
- [ ] **Test:** `test_invalidate_component_unknown_component_ignored()` - verify graceful handling
- [ ] **Test:** `test_invalidate_component_requests_render()` - verify render requested after invalidation
- [ ] **Implement:** Add `invalidate_component(component)`:
  ```python
  def invalidate_component(self, component: Component) -> None:
      if component in self._component_positions:
          start, end = self._component_positions[component]
          for i in range(start, end):
              if i < len(self._previous_lines):
                  self._previous_lines[i] = ""  # Mark for clearing
      self.request_render()
  ```
- [ ] **Commit:** `feat(tui): implement targeted invalidate_component()`

### 4.2 Clear position tracking on full invalidate()

- [ ] **Test:** `test_full_invalidate_clears_component_positions()` - verify positions cleared on full invalidate
- [ ] **Implement:** Add `self._component_positions = {}` to `TUI.invalidate()`
- [ ] **Commit:** `fix(tui): clear position tracking on full invalidate()`

---

## Phase 5: Edge Cases and Refinements

### 5.1 Handle components that change size

- [ ] **Test:** `test_invalidate_component_handles_size_change()` - verify works when component grew/shrank
- [ ] **Implement:** Ensure position tracking uses most recent positions, old positions naturally ignored
- [ ] **Commit:** `fix(tui): handle component size changes in targeted invalidation`

### 5.2 Handle overlay invalidation

- [ ] **Test:** `test_overlay_component_invalidation_bubbles()` - verify overlays can bubble invalidation
- [ ] **Test:** `test_invalidate_overlay_component_triggers_render()` - verify overlay invalidation works
- [ ] **Implement:** Ensure overlays participate in bubble-up if added as children
- [ ] **Commit:** `feat(tui): support overlay component invalidation`

### 5.3 Handle deep nesting edge cases

- [ ] **Test:** `test_deeply_nested_invalidation_bubbles_to_tui()` - verify 5+ level nesting works
- [ ] **Test:** `test_invalidate_mid_level_container_targets_correct_lines()` - verify intermediate container invalidation
- [ ] **Implement:** Verify parent chain works through arbitrary depth
- [ ] **Commit:** `test(tui): verify deep nesting invalidation works`

---

## Phase 6: Type Stubs

### 6.1 Update tui.pyi with new attributes

- [ ] **Implement:** Add `_parent: Container | None` to `Component` class in `tui.pyi`
- [ ] **Implement:** Add `_component_positions: dict[Component, tuple[int, int]]` to `TUI` class
- [ ] **Implement:** Add `invalidate_component(component: Component) -> None` to `TUI` class
- [ ] **Implement:** Add `_child_invalidated(child: Component) -> None` to `Container` and `TUI` classes
- [ ] **Commit:** `chore(types): update stubs for component invalidation`

---

## Phase 7: Integration Verification

### 7.1 Integration test: completion menu use case

- [ ] **Test:** `test_completion_menu_close_invalidates_input_only()` - simulate real use case
  ```python
  # Setup: Input with completion dropdown (rendered as one component)
  # Action: Close completion menu, call input.invalidate()
  # Verify: Only input lines cleared, other content preserved
  ```
- [ ] **Commit:** `test(tui): add completion menu integration test`

### 7.2 Verify no regressions

- [ ] **Run:** `uv run pytest` - all 174+ tests pass
- [ ] **Run:** `uv run ruff check src/` - no lint errors
- [ ] **Run:** `uv run mypy src/` - no type errors
- [ ] **Commit:** `chore: verify no regressions`

---

## Phase 8: Documentation

### 8.1 Update LLMS.md with new API

- [ ] **Document:** Add section on "Component Invalidation" after "Screen Switching"
- [ ] **Document:** Show direct `tui.invalidate_component(comp)` usage
- [ ] **Document:** Show bubble-up `comp.invalidate()` usage
- [ ] **Commit:** `docs: add component invalidation API to LLMS.md`

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
