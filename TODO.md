# PyPiTUI Scrollback & Streaming Verification Plan

## Goal

Verify all scrollback and streaming features work correctly, remove legacy alternate buffer code, and ensure the library is production-ready for consumers.

---

## Phase 1: Remove Alternate Buffer Code ✅ COMPLETE

The alternate buffer prevents scrollback. Since scrollback is a core feature, remove all alternate buffer support.

### 1.1 Terminal Abstract Base Class

- [x] ~~Remove `enter_alternate_screen()` abstract method from `Terminal` class~~ (N/A - not abstract)
- [x] ~~Remove `exit_alternate_screen()` abstract method from `Terminal` class~~ (N/A - not abstract)

### 1.2 ProcessTerminal Class

- [x] Remove `_in_alternate_screen` instance variable
- [x] Remove `enter_alternate_screen()` method implementation
- [x] Remove `exit_alternate_screen()` method implementation
- [x] Remove `\x1b[?1049h` escape sequence (enter alternate buffer)
- [x] Remove `\x1b[?1049l` escape sequence (exit alternate buffer)

### 1.3 MockTerminal Class

- [x] Remove `_in_alternate_screen` instance variable
- [x] Remove `enter_alternate_screen()` method implementation
- [x] Remove `exit_alternate_screen()` method implementation

### 1.4 TUI Class

- [x] Remove `use_alternate_buffer` parameter from `TUI.__init__()`
- [x] Remove `self._use_alternate_buffer` instance variable
- [x] Remove alternate buffer logic from `TUI.start()` method
- [x] Remove alternate buffer logic from `TUI.stop()` method

### 1.5 Type Stubs

- [x] Remove alternate buffer methods from `terminal.pyi`
- [x] Remove `use_alternate_buffer` parameter from `tui.pyi`

### 1.6 Documentation

- [x] Remove alternate buffer references from `README.md`
- [x] Remove alternate buffer references from `docs/scrollback-and-streaming.md`
- [x] Remove alternate buffer references from `LLMS.md`

### 1.7 Tests

- [x] Remove alternate buffer tests from `tests/test_pypitui.py`

---

## Phase 2: Fix Failing Tests

Current status: **9 failed, 158 passed**

### 2.1 Input Component (1 failure)

- [ ] Investigate and fix `tests/test_input.py::TestInputComponent::test_delete`

### 2.2 Kitty Protocol Keys (5 failures)

- [ ] Fix `tests/test_keys.py::TestMatchesKeyKittyProtocol::test_ctrl_c_cyrillic_with_base_layout`
- [ ] Fix `tests/test_keys.py::TestMatchesKeyKittyProtocol::test_ctrl_d_cyrillic_with_base_layout`
- [ ] Fix `tests/test_keys.py::TestMatchesKeyKittyProtocol::test_ctrl_z_cyrillic_with_base_layout`
- [ ] Fix `tests/test_keys.py::TestMatchesKeyKittyProtocol::test_direct_codepoint_without_base_layout`
- [ ] Fix `tests/test_keys.py::TestParseKeyLegacy::test_parse_special_keys`

### 2.3 Overlay Viewport Positioning (2 failures)

- [ ] Fix `tests/test_overlay.py::TestOverlayViewportPositioning::test_overlay_visible_at_bottom_of_scrolled_content`
- [ ] Fix `tests/test_overlay.py::TestOverlayViewportPositioning::test_overlay_center_anchor_with_scrolled_content`

### 2.4 SelectList (1 failure)

- [ ] Fix `tests/test_select_list.py::TestSelectList::test_multiline_description_normalized`

---

## Phase 3: Create VERIFICATION.md

Create a document that verifies each core feature works correctly.

### 3.1 Scrollback Buffer

- [ ] Document: Content flows into scrollback when exceeding terminal height
- [ ] Document: Users can scroll back with Shift+PgUp
- [ ] Document: `_max_lines_rendered` tracks total content height
- [ ] Document: `_calculate_first_visible_row()` computes viewport offset
- [ ] Verify with test: `tests/test_scrollback.py::TestCalculateFirstVisibleRow`

### 3.2 Synchronized Output (DEC 2026)

- [ ] Document: `_begin_sync()` returns `\x1b[?2026h`
- [ ] Document: `_end_sync()` returns `\x1b[?2026l`
- [ ] Document: Prevents flickering during partial updates
- [ ] Verify with test: `tests/test_scrollback.py::TestSynchronizedOutput`

### 3.3 Relative Cursor Movement

- [ ] Document: `_move_cursor_relative()` uses `\x1b[nA/B` sequences
- [ ] Document: `_hardware_cursor_row` tracks current position
- [ ] Document: Works correctly with scrolled content
- [ ] Verify with test: `tests/test_scrollback.py::TestRelativeCursorMovement`

### 3.4 Working Area Tracking

- [ ] Document: `_max_lines_rendered` grows but doesn't shrink
- [ ] Document: `_first_visible_row_previous` tracks viewport state
- [ ] Verify with test: `tests/test_scrollback.py::TestWorkingAreaTracking`

### 3.5 Overlay Positioning with Scrollback

- [ ] Document: Overlays use screen coordinates, not content coordinates
- [ ] Document: `_composite_overlays()` receives `viewport_top` parameter
- [ ] Document: Anchor-based overlays stay fixed on screen
- [ ] Document: Explicit row overlays scroll with content
- [ ] Verify with test: `tests/test_overlay.py::TestOverlayViewportPositioning`

### 3.6 Streaming Content Updates

- [ ] Document: New content causes terminal scroll via newlines
- [ ] Document: Existing content in scrollback is frozen (cannot be modified)
- [ ] Document: Only visible portion is re-rendered
- [ ] Verify with test: `tests/test_scrollback.py::TestDifferentialRenderingWithScrollback`

---

## Phase 4: Update Documentation ✅ COMPLETE

### 4.1 README.md

- [x] Remove `use_alternate_buffer` parameter from examples
- [x] Update Quick Start to clarify scrollback is always enabled
- [x] Remove "alternate buffer" mentions from Scrollback Support section
- [x] Update TUI constructor signature in examples

### 4.2 docs/scrollback-and-streaming.md

- [x] Remove "Main Buffer vs Alternate Buffer" comparison table
- [x] Remove alternate buffer implementation checklist items
- [x] Update to reflect current implementation (no alternate buffer option)
- [ ] Add practical usage examples

### 4.3 LLMS.md

- [x] Remove alternate buffer API references
- [x] Update TUI constructor documentation

---

## Phase 5: Integration Testing

### 5.1 Automated Tests

- [ ] Run `uv run pytest -v` - all tests pass (0 failures)
- [ ] Run `uv run pytest --cov` - review coverage report
- [ ] Run `uv run ruff check src/` - no linting issues
- [ ] Run `uv run mypy src/` - no type errors

### 5.2 Manual Testing

- [ ] Run `uv run python examples/demo.py` - all screens work
- [ ] Run `uv run python examples/scrollback_demo.py` - scrollback works with Shift+PgUp
- [ ] Test terminal resize during operation
- [ ] Test with small terminal (80x24)
- [ ] Test with large terminal (120x40)
- [ ] Test rapid content updates (streaming)

### 5.3 E2E Testing

- [ ] Check if `.agents/test_ultimate_demo.py` exists and run it
- [ ] Verify no visual glitches or artifacts

---

## Phase 6: Final Verification Checklist

### 6.1 Code Quality

- [ ] No `# TODO` or `# FIXME` comments related to scrollback/streaming
- [ ] No dead code or unused imports
- [ ] All functions have docstrings

### 6.2 Test Coverage

- [ ] All scrollback features have unit tests
- [ ] All overlay positioning scenarios have tests
- [ ] Edge cases covered (empty content, resize, rapid updates)

### 6.3 Documentation Consistency

- [ ] README.md matches actual API
- [ ] Type stubs match implementation
- [ ] Docstrings match function signatures

### 6.4 Final Sign-off

- [ ] All 167 tests pass
- [ ] Coverage >= 65%
- [ ] No regressions in demo apps
- [ ] Documentation is accurate and complete

---

## Test Failure Details

### Input: test_delete

```
Location: tests/test_input.py
Issue: Delete key not working as expected
```

### Kitty Protocol (5 failures)

```
Location: tests/test_keys.py
Issue: Cyrillic key combinations with Ctrl not matching expected behavior
Tests:
- test_ctrl_c_cyrillic_with_base_layout
- test_ctrl_d_cyrillic_with_base_layout
- test_ctrl_z_cyrillic_with_base_layout
- test_direct_codepoint_without_base_layout
- test_parse_special_keys
```

### Overlay Viewport (2 failures)

```
Location: tests/test_overlay.py
Issue: Overlay positioning when content is scrolled
Tests:
- test_overlay_visible_at_bottom_of_scrolled_content
- test_overlay_center_anchor_with_scrolled_content
```

### SelectList (1 failure)

```
Location: tests/test_select_list.py
Issue: Multiline descriptions not normalized to single line
Test: test_multiline_description_normalized
```

---

## Implementation Order

1. **Phase 1** - Remove alternate buffer code (eliminates confusion, scrollback is the only mode)
2. **Phase 2** - Fix failing tests (stabilize the codebase)
3. **Phase 3** - Create VERIFICATION.md (document expected behavior)
4. **Phase 4** - Update documentation (keep docs in sync with code)
5. **Phase 5** - Integration testing (verify everything works together)
6. **Phase 6** - Final verification (sign off on quality)
