# Execution Plan: PRD #007 - Phase 8: Error Handling & Demo

## Overview
Graceful error handling, PII stripping, working examples, and public API exports.

---

## Phase 8: Error Handling & Demo

### Error Handling

- [ ] **Test**: `test_render_error_shows_overlay()` — component render error displays error overlay
- [ ] **Implement**: `TUI._show_error_overlay(message: str)` — displays error without crashing
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_render_error_shows_overlay -v`

- [ ] **Test**: `test_terminal_write_error_cleanup()` — IOError triggers cleanup and exit
- [ ] **Implement**: Terminal write error handling with state restoration
- [ ] **Run**: `uv run pytest tests/unit/test_terminal.py::test_terminal_write_error_cleanup -v`

- [ ] **Test**: `test_input_callback_error_continues()` — callback error shows overlay, continues running
- [ ] **Implement**: Input callback error isolation
- [ ] **Run**: `uv run pytest tests/unit/test_terminal.py::test_input_callback_error_continues -v`

- [ ] **Test**: `test_debug_mode_re_raises()` — PYPITUI_DEBUG=1 re-raises for stack traces
- [ ] **Implement**: Debug mode exception handling
- [ ] **Run**: `uv run pytest tests/unit/test_tui.py::test_debug_mode_re_raises -v`

### PII Stripping in Logs

- [ ] **Test**: `test_log_sanitizes_passwords()` — password patterns replaced with ***
- [ ] **Test**: `test_log_sanitizes_tokens()` — token patterns replaced with ***
- [ ] **Implement**: Log sanitization patterns for sensitive data
- [ ] **Run**: `uv run pytest tests/unit/test_utils.py -k "sanitiz" -v`

### Examples

- [ ] **E2E**: `demo.py` runs without errors — smoke test
- [ ] **Implement**: `examples/demo.py` with all component showcase
- [ ] **Run**: E2E test via tmux automation

- [ ] **E2E**: `inputs.py` interactive test — type, submit, verify
- [ ] **Implement**: `examples/inputs.py` focused input demo
- [ ] **Run**: E2E test via tmux automation

- [ ] **E2E**: `overlays.py` modal test — open, interact, close
- [ ] **Implement**: `examples/overlays.py` modal dialog examples
- [ ] **Run**: E2E test via tmux automation

### Public API

- [ ] **Implement**: Complete `src/pypitui/__init__.py` exports:
  - Core: `TUI`, `Component`, `Size`, `RenderedLine`, `Rect`
  - Components: `Container`, `Text`, `Input`, `SelectList`, `SelectItem`, `BorderedBox`
  - Overlays: `Overlay`, `OverlayPosition`
  - Input: `Key`, `matches_key`, `parse_key`, `MouseEvent`, `parse_mouse`
  - Focus: `Focusable` protocol
  - Errors: `LineOverflowError`
  - Styles: `StyleSpan`, `detect_color_support`
  - Utils: `truncate_to_width`, `slice_by_width`, `wcwidth`
- [ ] **Test**: `test_all_public_api_importable()` — verify each export
- [ ] **Run**: `uv run pytest tests/unit/test_api.py -v`

- [ ] **Verify**: `from pypitui import TUI, Container, Text, Input` works

### Documentation

- [ ] **Update**: README.md quickstart section
- [ ] **Add**: API docstrings for all public methods
- [ ] **Verify**: mypy strict mode passes
- [ ] **Run**: `uv run mypy --strict src/`

- [ ] **Verify**: ruff linting passes
- [ ] **Run**: `uv run ruff check src/`

- [ ] **Verify**: pytest all green
- [ ] **Run**: `uv run pytest`

- [ ] **Test**: `test_file_structure_matches_spec()` — verify all files exist at correct paths
- [ ] **Run**: `uv run pytest tests/unit/test_structure.py -v`

---

## Files to Create/Modify

1. `src/pypitui/__init__.py` — Public API exports
2. `src/pypitui/tui.py` — Error overlay (extends Phase 6)
3. `src/pypitui/utils.py` — Log sanitization (extends Phase 3)
4. `examples/demo.py` — Full showcase
5. `examples/inputs.py` — Input demo
6. `examples/overlays.py` — Modal dialog demo
7. `tests/unit/test_api.py` — Public API tests
8. `tests/unit/test_structure.py` — File structure tests
9. `README.md` — Quickstart documentation

---

## Progress

**Phase 8 Status**: 0/13 tasks complete

**Dependencies**: Phase 7 (Rich Integration) must be complete

---

## Project Completion

When Phase 8 is complete:
- ✅ 274 total tasks (137 test + 137 implement)
- ✅ 80%+ unit test coverage
- ✅ All E2E tests passing
- ✅ mypy strict mode passes
- ✅ ruff linting passes
- ✅ Examples run without errors
