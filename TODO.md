# pypitui Scrollback Bug Fix - Implementation Todo

## Bug Summary
The `_handle_content_growth()` method in `pypitui/tui.py` emits newlines for **ALL** scrollback lines on every frame redraw, causing exponential scrollback growth. It should only emit newlines for **NEW** scrollback lines.

---

## Phase 1: Implement the Fix ✅ COMPLETE

### 1.1 Add State Tracking to TUI Class ✅
- [x] Open `src/pypitui/tui.py`
- [x] Locate `TUI.__init__()` method
- [x] Add instance variable after `_first_visible_row_previous`:
  ```python
  self._emitted_scrollback_lines: int = 0  # Track scrollback lines already emitted
  self._anchor_top: bool = False  # When True, skip scrollback handling
  ```

### 1.2 Modify _handle_content_growth Method ✅
- [x] Locate `_handle_content_growth()` method
- [x] Replace the method body with fixed implementation
- [x] Added anchor_top check to skip scrollback handling when needed

### 1.3 Add Reset Logic on Invalidate ✅
- [x] Locate `invalidate()` method in TUI class
- [x] Add at the end of the method:
  ```python
  self._emitted_scrollback_lines = 0
  ```

---

## Phase 2: Update Type Stubs ✅ COMPLETE

### 2.1 Update tui.pyi Stub File ✅
- [x] Open `src/pypitui/tui.pyi`
- [x] Add to TUI class attributes:
  ```python
  _emitted_scrollback_lines: int
  ```

---

## Phase 3: Test the Fix ✅ COMPLETE

### 3.1 Create Test Case ✅
- [x] Create `tests/test_scrollback_bug.py` with comprehensive tests

### 3.2 Run Tests ✅
- [x] Run: `uv run pytest tests/test_scrollback_bug.py -v`
- [x] All 5 tests pass
- [x] Run full test suite: `uv run pytest`
- [x] All 174 tests pass - no regressions

---

## Phase 4: Manual Verification (Optional)

### 4.1 Create Manual Test Script
- [ ] Create `examples/scrollback_test.py` if needed

### 4.2 Run Manual Test
- [ ] Run: `uv run python examples/scrollback_test.py`

---

## Phase 5: Documentation (Optional)

### 5.1 Update Changelog
- [ ] Open `CHANGELOG.md`
- [ ] Add entry under "Fixed"

---

## Phase 6: Release (Optional)

### 6.1 Version Bump
- [ ] Update `__init__.py` version: `__version__ = "0.2.4"`
- [ ] Update `pyproject.toml` version: `version = "0.2.4"`

### 6.2 Tag and Release
- [ ] Commit changes
- [ ] Create tag: `git tag v0.2.4`
- [ ] Push with tags
- [ ] Create GitHub release

### 6.3 Publish to PyPI
- [ ] Build: `uv build`
- [ ] Publish: `uv publish`

---

## Verification Checklist

- [x] `_emitted_scrollback_lines` initialized to 0 in `__init__`
- [x] `_handle_content_growth` only emits new scrollback lines
- [x] `invalidate()` resets counter to 0
- [x] Type stubs updated
- [x] Unit tests pass (5/5)
- [x] Full test suite passes (174/174)

---

## Files Modified

1. `src/pypitui/tui.py` - Main fix ✅
2. `src/pypitui/tui.pyi` - Type stubs ✅
3. `tests/test_scrollback_bug.py` - New test file ✅

## Summary

The scrollback bug fix has been successfully implemented and tested. The key changes:

1. Added `_emitted_scrollback_lines` counter to track which scrollback lines have already been emitted
2. Modified `_handle_content_growth()` to only emit newlines for NEW scrollback lines (those not already emitted)
3. Added `_anchor_top` flag for future use to skip scrollback handling
4. Reset counter in `invalidate()` to handle full re-renders
5. Added comprehensive unit tests to verify the fix

The fix prevents exponential blank line growth in terminal scrollback history by tracking state across render frames.
