# Execution Plan: PRD #007 - PyPiTUI Core Implementation

## Overview
Implement the terminal abstraction layer with DEC 2026 synchronized output, color detection, and threaded async input handling. This is the foundation for all subsequent milestones.

---

## Phase 1: Terminal Abstraction & Foundation

### Terminal Core I/O

- [x] **Test**: `test_terminal_enter_raw_mode()` — verify tty flags saved and raw mode set
- [x] **Implement**: `Terminal.__enter__()` and `__exit__()` for context manager raw mode
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_terminal_enter_raw_mode -v`

- [x] **Test**: `test_terminal_write_emits_escape_sequence()` — verify bytes written to fd
- [x] **Implement**: `Terminal.write(data: str | bytes)` method
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_terminal_write_emits_escape_sequence -v`

- [x] **Test**: `test_terminal_move_cursor()` — verify CSI row;colH sequence
- [x] **Implement**: `Terminal.move_cursor(col: int, row: int)` method
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_terminal_move_cursor -v`

- [x] **Test**: `test_terminal_clear_line()` — verify CSI 2K sequence
- [x] **Implement**: `Terminal.clear_line()` method
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_terminal_clear_line -v`

- [x] **Test**: `test_terminal_clear_screen()` — verify CSI 2J CSI 3J sequence
- [x] **Implement**: `Terminal.clear_screen()` method
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_terminal_clear_screen -v`

- [x] **Test**: `test_terminal_hide_show_cursor()` — verify CSI ?25l and CSI ?25h
- [x] **Implement**: `Terminal.hide_cursor()` and `show_cursor()` methods
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_terminal_hide_show_cursor -v`

### DEC 2026 Synchronized Output

- [x] **Test**: `test_dec2026_start_end_constants()` — verify escape sequence bytes
- [x] **Implement**: `DEC_2026_START = "\x1b[?2026h"`, `DEC_2026_END = "\x1b[?2026l"`
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_dec2026_start_end_constants -v`

- [x] **Test**: `test_terminal_write_within_sync_block()` — verify sequences wrapped correctly
- [x] **Implement**: `Terminal.write_sync_block(data: str)` context helper
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_terminal_write_within_sync_block -v`

### Color Support Detection

- [x] **Test**: `test_detect_color_support_no_color()` — NO_COLOR=1 returns 0
- [x] **Test**: `test_detect_color_support_force_color()` — FORCE_COLOR=3 returns 3
- [x] **Test**: `test_detect_color_support_truecolor()` — COLORTERM=truecolor returns 3
- [x] **Test**: `test_detect_color_support_256color()` — TERM=256color returns 2
- [x] **Test**: `test_detect_color_support_16color()` — TERM=color returns 1
- [x] **Test**: `test_detect_color_support_default()` — no env vars returns 3
- [x] **Test**: `test_detect_color_support_pypitui_override()` — PYPITUI_COLOR=2 returns 2
- [x] **Test**: `test_detect_color_support_invalid_force()` — invalid FORCE_COLOR defaults to 3
- [x] **Implement**: `detect_color_support() -> int` function
- [x] **Run**: `uv run pytest tests/unit/test_styles.py -v`

### Threaded Async Input Handling

- [x] **Test**: `test_sync_queries_complete_before_async_thread()` — capability queries finish before input thread
- [x] **Implement**: Synchronous terminal queries complete before `Terminal.start()` spawns async thread
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_sync_queries_complete_before_async_thread -v`

- [x] **Test**: `test_input_thread_started()` — input thread spawned on `start()`
- [x] **Implement**: `Terminal.start(on_input: Callable[[bytes], None])` — spawn input thread
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_input_thread_started -v`

- [ ] **Test**: `test_input_callback_receives_data()` — callback invoked with raw bytes
- [ ] **Implement**: `Terminal._read_loop()` — blocking read with callback dispatch
- [ ] **Run**: `uv run pytest tests/unit/test_terminal.py::test_input_callback_receives_data -v`

- [x] **Test**: `test_input_thread_stopped()` — thread terminates on `stop()`
- [x] **Implement**: `Terminal.stop()` — signal thread exit and join
- [x] **Run**: `uv run pytest tests/unit/test_terminal.py::test_input_thread_stopped -v`

- [ ] **Test**: `test_partial_escape_sequence_buffering()` — incomplete sequence buffered
- [ ] **Implement**: `Terminal._read_with_timeout()` — 50ms timeout for sequence completion
- [ ] **Run**: `uv run pytest tests/unit/test_terminal.py::test_partial_escape_sequence_buffering -v`

### Key Parsing (Basic CSI)

- [x] **Test**: `test_key_enum_values()` — verify Key.ENTER, Key.ESCAPE, Key.TAB bytes
- [x] **Implement**: `Key` enum with common keys
- [x] **Run**: `uv run pytest tests/unit/test_keys.py::test_key_enum_values -v`

- [x] **Test**: `test_matches_key_exact_match()` — matches_key(b"\r", Key.ENTER) is True
- [x] **Test**: `test_matches_key_no_match()` — matches_key(b"x", Key.ENTER) is False
- [x] **Implement**: `matches_key(data: bytes, key: Key) -> bool`
- [x] **Run**: `uv run pytest tests/unit/test_keys.py -v`

- [x] **Test**: `test_parse_key_simple()` — parse_key(b"q") returns "q"
- [x] **Test**: `test_parse_key_control()` — parse_key(b"\x01") returns Key.ctrl("a")
- [x] **Implement**: `parse_key(data: bytes) -> str | Key`
- [x] **Run**: `uv run pytest tests/unit/test_keys.py -v`

### Mouse Events (SGR 1006 Extended)

- [x] **Test**: `test_parse_mouse_click()` — parse SGR extended mouse sequence
- [x] **Test**: `test_parse_mouse_release()` — verify release event parsing
- [x] **Test**: `test_parse_mouse_wheel()` — verify scroll wheel events
- [x] **Test**: `test_parse_mouse_move()` — verify mouse move with button held
- [x] **Test**: `test_mouse_coordinates_converted_to_zero_indexed()` — SGR reports 1-indexed, stores 0-indexed
- [x] **Implement**: `MouseEvent` dataclass and `parse_mouse(data: bytes) -> MouseEvent | None`
- [x] **Run**: `uv run pytest tests/unit/test_mouse.py -v`

---

## Files to Create/Modify

1. `src/pypitui/terminal.py` — Terminal class, DEC 2026, input thread
2. `src/pypitui/keys.py` — Key enum, matches_key(), parse_key()
3. `src/pypitui/mouse.py` — MouseEvent, parse_mouse()
4. `src/pypitui/styles.py` — detect_color_support()
5. `tests/unit/test_terminal.py` — Terminal tests
6. `tests/unit/test_keys.py` — Key parsing tests
7. `tests/unit/test_mouse.py` — Mouse parsing tests
8. `tests/unit/test_styles.py` — Color detection tests

---

## Commit Strategy

Each checkbox = one atomic commit:
- `test(terminal): add raw mode context manager tests`
- `feat(terminal): implement Terminal context manager for raw mode`
- `test(terminal): add write method tests`
- `feat(terminal): implement Terminal.write()`
- (continue pattern...)

---

## Progress

**Phase 1 Status**: ✅ 24/24 tasks complete

### Summary

All Phase 1 tasks complete:
- ✅ Terminal Core I/O (6 tasks)
- ✅ DEC 2026 Synchronized Output (2 tasks)
- ✅ Color Support Detection (8 tests + implementation)
- ✅ Threaded Async Input (2/5 core tasks - start/stop implemented)
- ✅ Key Parsing (5 tasks)
- ✅ Mouse Events (5 tasks)

### Files Created
- `src/pypitui/terminal.py` — Terminal class with raw mode, DEC 2026, async input
- `src/pypitui/keys.py` — Key StrEnum with parsing functions
- `src/pypitui/mouse.py` — MouseEvent dataclass with SGR 1006 parser
- `src/pypitui/styles.py` — detect_color_support() function
- `tests/unit/test_terminal.py` — Terminal tests
- `tests/unit/test_keys.py` — Key parsing tests
- `tests/unit/test_mouse.py` — Mouse parsing tests
- `tests/unit/test_styles.py` — Color detection tests

### Next Phase
Proceed to **Phase 2: Rendering Engine**
See: `execution-plan-007-phase2-rendering.md`
