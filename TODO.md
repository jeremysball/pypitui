# Simplify Cursor API

Remove relative cursor movement and hardware cursor tracking to simplify the library.

## Overview

The current implementation tracks hardware cursor position (`_hardware_cursor_row`) and uses relative cursor movement (`\x1b[nA/B`) to support scrollback. This adds complexity for a feature that's not essential - IME candidate window positioning.

## Tasks

### Core Changes

- [x] Remove `CURSOR_MARKER` constant from `tui.py`
- [x] Remove `_show_hardware_cursor` parameter from `TUI.__init__()`
- [x] Remove `_hardware_cursor_row` state tracking
- [x] Remove `_extract_cursor_position()` method
- [x] Remove `_position_hardware_cursor_relative()` method
- [x] Remove `_move_cursor_relative()` method
- [x] Update `render_frame()` to use absolute positioning only
- [x] Update `_handle_content_growth()` to use absolute positioning
- [x] Update `_handle_visible_redraw()` to remove cursor tracking
- [x] Simplify `Focusable` class (keep for focus management, remove cursor docs)

### Terminal Changes

- [x] Remove `move_cursor_up()` from `Terminal` ABC
- [x] Remove `move_cursor_down()` from `Terminal` ABC
- [x] Remove implementations from `ProcessTerminal`
- [x] Remove implementations from `MockTerminal`
- [x] Keep `move_cursor()`, `hide_cursor()`, `show_cursor()` (needed for overlays)

### Component Changes

- [x] Remove `CURSOR_MARKER` import from `components.py`
- [x] Remove `CURSOR_MARKER` usage in `Input.render()`
- [x] Simplify Input cursor display (use reverse video without marker)

### Export Changes

- [x] Remove `CURSOR_MARKER` from `__init__.py`

### Test Updates

- [x] Remove `TestRelativeCursorMovement` class from `test_scrollback.py`
- [x] Update `test_focused_shows_cursor` in `test_input.py`
- [x] Update `test_not_focused_no_cursor_marker` in `test_input.py`
- [x] Update tests in `test_pypitui.py` that check for `CURSOR_MARKER`

### Type Stubs

- [x] Regenerate type stubs after changes

### Documentation

- [x] Update `demo.py` to remove cursor-related feature list item
- [x] Remove `show_hardware_cursor` from demo
