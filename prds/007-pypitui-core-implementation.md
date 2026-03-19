# PRD: PyPiTUI Core Implementation

**GitHub Issue**: [#7](https://github.com/jeremysball/pypitui/issues/7)  
**Status**: In Progress  
**Priority**: High  
**Created**: 2026-03-18  
**Branch**: `feature/prd-007-pypitui-core`

---

## Problem

PyPiTUI is a Python TUI library with comprehensive architecture documentation but zero implementation. The project has detailed specs for differential rendering, component systems, overlay management, and focus handling—but no working code. We need to build the complete core library from scratch following the documented architecture.

## Solution

Implement the full PyPiTUI library with:
1. **Differential rendering engine** with full viewport-aware diffing from day one
2. **Component system** with measure/render lifecycle
3. **Terminal abstraction** with DEC 2026 sync codes and threaded async input handling
4. **Focus management** with stack-based focus and tab order
5. **Built-in components**: Container, Text, Input, SelectList, BorderedBox, Overlay
6. **Test-first development** with hybrid strategy: unit tests for rendering engine, E2E for interactive components

---

## Architecture Highlights

### Differential Rendering
- Track `_previous_lines` (row -> content hash)
- Detect appends vs. edits for optimal output
- Handle viewport shifts when content exceeds terminal height
- **Any change in scrollback triggers full clear+redraw** (scrollback content is immutable in terminal)
- DEC 2026 synchronized updates for atomic frames

### Component System
- Abstract `Component` base class with `measure()` and `render()`
- Vertical-only layout (no flexbox/grids—keep it simple)
- Parent containers distribute width; children handle internal layout
- Overlays for viewport-relative positioning (fixed headers/footers)
- **Component caching post-MVP**: Manual invalidation is error-prone; design better mechanism later

### Terminal I/O Architecture
- **Async**: User input (keyboard, mouse) via threaded input handler with callbacks
- **Sync**: Feature queries (DEC 2026 detection, etc.) during initialization before async thread starts

### Zero-Dependency Core
- Only `wcwidth` for Unicode width handling
- Rich integration optional, isolated in `components/rich.py`
- Markdown/code highlighting via lighter alternative (mistune/pygments)

---

## Success Criteria

1. `examples/demo.py` runs without errors showing all component types
2. **Differential rendering efficiency**: Append-only scenario emits ≤20% of escape sequences vs full clear+redraw (measured via MockTerminal)
3. **Performance**: Frame render time <16ms (60 FPS target) for 100-line terminal
4. 80%+ unit test coverage for `tui.py`, `terminal.py`, `styles.py`
5. **Integration tests** cover Terminal+TUI pipeline, differential rendering, and render loop
6. E2E tests verify Input, SelectList, and Overlay interactions
7. mypy strict mode passes with zero errors
8. Pre-commit hooks (ruff, mypy, pytest) all green
9. Wide character handling verified for emoji (width 2) and CJK text

### Test Strategy

**Unit Tests** (47 tests): Core functionality in isolation
- Terminal I/O operations
- Key/mouse parsing
- Style/color detection
- Component data structures
- TUI differential rendering

**Integration Tests** (20 tests): Component interactions
- Terminal + TUI pipeline
- Differential rendering end-to-end
- Full render loop with components
- MockTerminal verification

**E2E Tests** (planned): tmux automation for interactive components
- Input typing and submission
- SelectList navigation
- Overlay modal interactions

---

## Milestones

### Milestone 1: Foundation & Terminal Abstraction
**Goal**: Low-level terminal I/O with DEC 2026 sync codes and threaded async input handling.

#### terminal.py - Core Terminal I/O
- [x] **Test**: `test_terminal_enter_raw_mode()` — verify tty flags are saved and raw mode is set
- [x] **Implement**: `Terminal.__enter__()` and `__exit__()` for context manager raw mode
- [x] **Test**: `test_terminal_write_emits_escape_sequence()` — verify bytes written to fd
- [x] **Implement**: `Terminal.write(data: str | bytes)` method
- [x] **Test**: `test_terminal_move_cursor()` — verify CSI row;colH sequence
- [x] **Implement**: `Terminal.move_cursor(col: int, row: int)` method
- [x] **Test**: `test_terminal_clear_line()` — verify CSI 2K sequence
- [x] **Implement**: `Terminal.clear_line()` method
- [x] **Test**: `test_terminal_clear_screen()` — verify CSI 2J CSI 3J sequence
- [x] **Implement**: `Terminal.clear_screen()` method
- [x] **Test**: `test_terminal_hide_show_cursor()` — verify CSI ?25l and CSI ?25h
- [x] **Implement**: `Terminal.hide_cursor()` and `show_cursor()` methods

#### DEC 2026 Synchronized Output
- [x] **Test**: `test_dec2026_start_end_constants()` — verify escape sequence bytes
- [x] **Implement**: `DEC_2026_START = "\x1b[?2026h"`, `DEC_2026_END = "\x1b[?2026l"`
- [x] **Test**: `test_terminal_write_within_sync_block()` — verify sequences wrapped correctly
- [x] **Implement**: `Terminal.write_sync_block(data: str)` context helper
- [x] **Decision**: DEC 2026 feature detection deferred to post-MVP; assume modern terminal support

#### Color Support Detection
- [x] **Test**: `test_detect_color_support_no_color()` — NO_COLOR=1 returns 0
- [x] **Test**: `test_detect_color_support_force_color()` — FORCE_COLOR=3 returns 3
- [x] **Test**: `test_detect_color_support_truecolor()` — COLORTERM=truecolor returns 3
- [x] **Test**: `test_detect_color_support_256color()` — TERM=256color returns 2
- [x] **Test**: `test_detect_color_support_16color()` — TERM=color returns 1
- [x] **Test**: `test_detect_color_support_default()` — no env vars returns 3 (assume modern)
- [x] **Test**: `test_detect_color_support_pypitui_override()` — PYPITUI_COLOR=2 returns 2
- [x] **Test**: `test_detect_color_support_invalid_force()` — invalid FORCE_COLOR defaults to 3
- [x] **Implement**: `detect_color_support() -> int` function

#### Threaded Async Input Handling
- [x] **Test**: `test_sync_queries_complete_before_async_thread()` — DEC 2026 detection and other capability queries finish before input thread spawns
- [x] **Implement**: All synchronous terminal queries (DEC 2026 detection, capability queries) MUST complete before `Terminal.start()` spawns the async input thread
- [x] **Test**: `test_input_thread_started()` — input thread spawned on `start()`
- [x] **Implement**: `Terminal.start(on_input: Callable[[bytes], None])` — spawn input thread
- [x] **Test**: `test_input_callback_receives_data()` — callback invoked with raw bytes
- [x] **Implement**: `Terminal._read_loop()` — blocking read with callback dispatch
- [x] **Test**: `test_input_thread_stopped()` — thread terminates on `stop()`
- [x] **Implement**: `Terminal.stop()` — signal thread exit and join
- [x] **Test**: `test_partial_escape_sequence_buffering()` — incomplete sequence buffered
- [x] **Implement**: `Terminal._read_with_timeout()` — 50ms timeout for sequence completion

#### Key Parsing (Basic CSI)
- [x] **Test**: `test_key_enum_values()` — verify Key.ENTER, Key.ESCAPE, Key.TAB bytes
- [x] **Implement**: `Key` enum with common keys
- [x] **Test**: `test_matches_key_exact_match()` — matches_key(b"\r", Key.ENTER) is True
- [x] **Test**: `test_matches_key_no_match()` — matches_key(b"x", Key.ENTER) is False
- [x] **Implement**: `matches_key(data: bytes, key: Key) -> bool`
- [x] **Test**: `test_parse_key_simple()` — parse_key(b"q") returns "q"
- [x] **Test**: `test_parse_key_control()` — parse_key(b"\x01") returns Key.ctrl("a")
- [x] **Implement**: `parse_key(data: bytes) -> str | Key`

#### Mouse Events (SGR 1006 Extended)
- [x] **Test**: `test_parse_mouse_click()` — parse SGR extended mouse sequence (CSI < 0;10;20 M)
- [x] **Test**: `test_parse_mouse_release()` — verify release event parsing (CSI < 0;10;20 m)
- [x] **Test**: `test_parse_mouse_wheel()` — verify scroll wheel events
- [x] **Test**: `test_parse_mouse_move()` — verify mouse move with button held
- [x] **Test**: `test_mouse_coordinates_converted_to_zero_indexed()` — SGR 1006 reports 1-indexed coordinates, MouseEvent stores 0-indexed screen coordinates
- [x] **Implement**: `MouseEvent` dataclass with `row: int, col: int` (0-indexed screen coordinates) and `parse_mouse(data: bytes) -> MouseEvent | None`

#### Milestone 1 Integration Tests
- [x] **Test**: `test_full_render_pipeline()` — TUI renders through Terminal
- [x] **Test**: `test_second_render_only_changes_diff()` — differential output verified
- [x] **Test**: `test_mock_terminal_counts_escapes()` — MockTerminal escape counting works

**Status**: ✅ Complete (48/48 tasks, 100%)

---

### Milestone 2: Rendering Engine
**Goal**: Differential rendering with full viewport-aware diffing and 60 FPS performance (<16ms frame time).

#### Core Data Structures
- [ ] **Test**: `test_size_dataclass()` — Size(width, height) stores dimensions
- [ ] **Implement**: `Size` dataclass with `width: int`, `height: int`
- [ ] **Test**: `test_rendered_line_dataclass()` — RenderedLine stores content and styles
- [ ] **Implement**: `RenderedLine` dataclass with `content: str`, `styles: list[StyleSpan]`
- [ ] **Note**: `RenderedLine` is the canonical return type for all `render()` methods. The architecture document's `list[str]` references are simplified for conceptual clarity.
- [ ] **Test**: `test_rect_dataclass()` — Rect(x, y, width, height) stores position and dimensions
- [ ] **Implement**: `Rect` dataclass with `x: int`, `y: int`, `width: int`, `height: int`

#### TUI Class Foundation
- [ ] **Test**: `test_tui_init_caches_previous_lines()` — _previous_lines is empty dict row->content_hash
- [ ] **Test**: `test_tui_init_tracks_max_lines()` — _max_lines_rendered starts at 0
- [ ] **Test**: `test_tui_init_tracks_viewport_top()` — _viewport_top starts at 0
- [ ] **Test**: `test_tui_init_hardware_cursor()` — _hardware_cursor_row and _hardware_cursor_col tracked
- [ ] **Implement**: `TUI.__init__(self, terminal: Terminal)` with full state tracking
- [ ] **Test**: `test_tui_add_child_sets_root()` — add_child stores component
- [ ] **Implement**: `TUI.add_child(self, component: Component)`

#### Differential Rendering Core
- [ ] **Test**: `test_find_changed_bounds_identifies_range()` — returns (first, last) changed indices
- [ ] **Implement**: `TUI._find_changed_bounds(self, new_lines: list[str]) -> tuple[int, int]`
- [ ] **Test**: `test_output_diff_writes_changed_lines()` — only changed lines emit escape sequences
- [ ] **Test**: `test_output_diff_skips_unchanged_lines()` — unchanged lines generate no output
- [ ] **Test**: `test_escape_sequence_efficiency()` — append-only emits ≤20% sequences vs full redraw (via MockTerminal)
- [ ] **Implement**: `TUI._output_diff(self, lines: list[str])` with full diffing algorithm

#### Viewport Tracking
- [ ] **Test**: `test_viewport_top_calculation()` — viewport_top = max(0, content_height - term_height)
- [ ] **Test**: `test_viewport_top_zero_when_content_fits()` — 3 lines on 24-line terminal = 0
- [ ] **Test**: `test_viewport_top_nonzero_when_content_scrolls()` — 30 lines on 24-line terminal = 6
- [ ] **Implement**: `TUI._calculate_viewport_top(self, content_height: int) -> int`
- [ ] **Test**: `test_compute_line_diff_accounts_for_viewport()` — cursor positioning with viewport offset
- [ ] **Implement**: `TUI._compute_line_diff(self, target_row: int, prev_viewport_top: int, viewport_top: int) -> int`

#### Append Optimization
- [ ] **Test**: `test_detect_append_start()` — pure append returns append_start=True
- [ ] **Test**: `test_detect_edit_not_append()` — middle edit returns append_start=False
- [ ] **Implement**: `TUI._detect_append(self, new_lines: list[str], prev_lines: dict[int, str], first_changed: int) -> bool`
- [ ] **Test**: `test_append_uses_newline_scrolling()` — append writes \r\n not cursor positioning
- [ ] **Test**: `test_append_with_viewport_shift()` — scrollback handled via terminal natural scroll
- [ ] **Implement**: Append path with `\r\n` for terminal natural scrolling

#### Scrollback-Aware Redraw (CRITICAL)
- [ ] **Test**: `test_edit_in_scrollback_triggers_full_redraw()` — first_changed < viewport_top triggers clear
- [ ] **Test**: `test_edit_in_viewport_does_not_clear()` — first_changed >= viewport_top uses diff
- [ ] **Implement**: `TUI._is_scrollback_edit(self, first_changed: int, viewport_top: int) -> bool`
- [ ] **Test**: `test_mixed_scrollback_edit_and_append_triggers_full_redraw()` — when both scrollback edit and append occur in same frame, full redraw takes precedence over append optimization
- [ ] **Implement**: Scrollback edit detection takes precedence; full redraw occurs when `first_changed < viewport_top`, even if append optimization would otherwise apply
- [ ] **Test**: `test_clear_on_shrink_true()` — full clear when content shrinks
- [ ] **Test**: `test_clear_on_shrink_false()` — differential clear when content shrinks
- [ ] **Implement**: `clear_on_shrink: bool` parameter in TUI config

**Design Note:** Any change in scrollback (content above current viewport) triggers full clear+redraw because terminal scrollback is immutable. Cursor positioning cannot reach scrolled-off content. This takes precedence over append optimization.

#### Line Overflow Protection
- [ ] **Test**: `test_line_overflow_raises_error()` — line exceeding width raises LineOverflowError
- [ ] **Test**: `test_line_overflow_includes_context()` — error shows row, width, content
- [ ] **Implement**: `LineOverflowError` exception and width validation in `_output_line()`
- [ ] **Test**: `test_render_error_shows_overlay()` — component render error displays error overlay
- [ ] **Implement**: Error overlay display in `render_frame()` exception handler

#### Component Position Tracking
- [ ] **Test**: `test_component_rect_set_during_render()` — _rect populated after render_frame()
- [ ] **Implement**: TUI sets `component._rect` during render with absolute (x, y, width, height)
- [ ] **Test**: `test_invalidate_component_clears_rect_lines()` — specific rows removed from _previous_lines
- [ ] **Implement**: `TUI.invalidate_component(self, component: Component)`

#### Hardware Cursor Management
- [ ] **Test**: `test_hardware_cursor_tracked_per_write()` — _hardware_cursor_row/col updated after each line
- [ ] **Test**: `test_hardware_cursor_reset_on_render_start()` — cursor reset to (0,0) before diff output
- [ ] **Implement**: Explicit cursor tracking in `_output_line()` and `_output_diff()`
- [ ] **Test**: `test_hardware_cursor_for_overlay_focus()` — absolute positioning for overlay content
- [ ] **Implement**: Absolute screen coordinate calculation for overlay-focused components

#### Terminal Resize
- [ ] **Test**: `test_resize_clears_previous_lines()` — _previous_lines cleared on resize
- [ ] **Test**: `test_resize_updates_terminal_dimensions()` — width/height updated
- [ ] **Test**: `test_resize_updates_viewport_top()` — viewport recalculated
- [ ] **Test**: `test_resize_triggers_full_redraw()` — all visible lines are re-emitted after resize via MockTerminal escape sequence verification
- [ ] **Implement**: `TUI.on_resize(self, new_width: int, new_height: int)`

#### Performance
- [ ] **Test**: `test_frame_render_time_under_16ms()` — render completes within 60 FPS budget
- [ ] **Implement**: Frame timing instrumentation in `render_frame()`

---

### Milestone 3: Component Base & Container
**Goal**: Component lifecycle and vertical layout.

#### Component ABC
- [ ] **Test**: `test_component_abstract_methods()` — cannot instantiate without measure/render
- [ ] **Implement**: `Component` ABC with `measure()`, `render()`, `invalidate()`
- [ ] **Test**: `test_component_invalidation_bubbles()` — invalidate() calls _child_invalidated()
- [ ] **Implement**: `Component.invalidate(self)` and `_child_invalidated(self, child)`
- [ ] **Test**: `test_component_rect_field_exists()` — _rect: Rect stores position and dimensions
- [ ] **Implement**: `Component._rect: Rect` field for TUI to set during render

**Note:** Components MAY implement internal caching (e.g., Text component caching wrapped lines) as an optimization, but TUI does not rely on it. TUI-level `_previous_lines` diffing is the primary and required caching mechanism.

#### Container Component
- [ ] **Test**: `test_container_measure_returns_sum_of_children()` — height = sum(child heights)
- [ ] **Implement**: `Container.measure(self, available_width: int, available_height: int) -> Size`
- [ ] **Test**: `test_container_render_stacks_vertically()` — children rendered sequentially
- [ ] **Implement**: `Container.render(self, width: int) -> list[RenderedLine]`
- [ ] **Test**: `test_container_add_child_appends_to_list()` — children list grows
- [ ] **Implement**: `Container.add_child(self, component: Component)`
- [ ] **Test**: `test_container_clear_children()` — children list emptied
- [ ] **Implement**: `Container.clear_children(self)`

#### Text Component
- [ ] **Test**: `test_text_measure_single_line()` — height=1 for simple text
- [ ] **Test**: `test_text_measure_multi_line()` — height=n for n lines
- [ ] **Implement**: `Text.measure(self, available_width: int, available_height: int) -> Size`
- [ ] **Test**: `test_text_render_returns_lines()` — returns list of RenderedLine
- [ ] **Test**: `test_text_render_wraps_long_lines()` — wrapping at width boundary using wcwidth
- [ ] **Implement**: `Text.render(self, width: int) -> list[RenderedLine]` with proper wide char handling
- [ ] **Test**: `test_text_content_mutable()` — set_text updates content and invalidates
- [ ] **Implement**: `Text.set_text(self, text: str)` with invalidation

**Note:** No render caching in MVP. May add intelligent caching post-MVP.

#### Wide Character Support
- [ ] **Test**: `test_wcwidth_emoji()` — emoji counted as width 2
- [ ] **Test**: `test_wcwidth_cjk()` — CJK characters counted as width 2
- [ ] **Test**: `test_truncate_to_width_respects_wide_chars()` — never splits wide chars
- [ ] **Test**: `test_wide_char_at_boundary_excluded()` — wide characters at exact width boundary are excluded (strict <= rule)
- [ ] **Implement**: `truncate_to_width(text: str, width: int) -> str` using wcwidth — wide chars at exact boundary are excluded
- [ ] **Test**: `test_slice_by_width_atomic()` — wide chars treated as atomic units
- [ ] **Implement**: `slice_by_width(text: str, start: int, end: int) -> str`

---

### Milestone 4: Interactive Components
**Goal**: Input, SelectList, and BorderedBox.

#### Input Component
- [ ] **E2E Test**: `test_input_typing_renders_text()` — type "hello", see "hello" on screen
- [ ] **Implement**: `Input.__init__()` with placeholder, max_length
- [ ] **Test**: `test_input_measure_returns_one_line()` — height=1 always
- [ ] **Implement**: `Input.measure()`
- [ ] **Test**: `test_input_render_shows_content()` — typed text appears in render
- [ ] **Test**: `test_input_render_shows_placeholder_when_empty()` — placeholder visible
- [ ] **Implement**: `Input.render(self, width: int) -> list[RenderedLine]`
- [ ] **Test**: `test_input_handle_key_appends_char()` — "a" typed adds "a" to content
- [ ] **Test**: `test_input_handle_backspace_removes_char()` — backspace removes last char
- [ ] **Test**: `test_input_handle_input_returns_bool()` — returns True when consuming input
- [ ] **Implement**: `Input.handle_input(self, data: bytes) -> bool`
- [ ] **Test**: `test_input_cursor_position_relative()` — returns (row, col) relative to component's top-left origin; row 0 = first rendered line, col = display width units (wcwidth)
- [ ] **Implement**: `Input.get_cursor_position(self) -> tuple[int, int] | None` — returns cursor position relative to component's top-left corner; row 0 = first rendered line, column = wcwidth display units
- [ ] **Test**: `test_input_on_submit_callback()` — Enter triggers on_submit
- [ ] **Implement**: `Input.on_submit` callback field

#### SelectList Component
- [ ] **E2E Test**: `test_selectlist_navigation()` — Down arrow moves selection
- [ ] **Implement**: `SelectList.__init__(self, items: list[SelectItem], max_visible: int)`
- [ ] **Test**: `test_selectlist_measure_respects_max_visible()` — height = min(len(items), max_visible)
- [ ] **Implement**: `SelectList.measure()`
- [ ] **Test**: `test_selectlist_render_shows_items()` — all visible items rendered
- [ ] **Test**: `test_selectlist_render_highlights_selected()` — selected item has different style
- [ ] **Implement**: `SelectList.render()` with selection highlighting
- [ ] **Test**: `test_selectlist_handle_down_moves_selection()` — selection index increments
- [ ] **Test**: `test_selectlist_handle_up_moves_selection()` — selection index decrements
- [ ] **Test**: `test_selectlist_wraps_at_boundaries()` — Up at top wraps to bottom, vice versa
- [ ] **Test**: `test_selectlist_handle_input_returns_bool()` — returns True when consuming input
- [ ] **Implement**: `SelectList.handle_input(data: bytes) -> bool` for Up/Down/Enter

#### SelectItem Dataclass
- [ ] **Test**: `test_selectitem_creation()` — id and label stored
- [ ] **Implement**: `SelectItem` dataclass with `id: str`, `label: str`

#### BorderedBox Component
- [ ] **E2E Test**: `test_borderedbox_renders_frame()` — box appears around content
- [ ] **Implement**: `BorderedBox.__init__(self, title: str | None = None)`
- [ ] **Test**: `test_borderedbox_measure_adds_border()` — width + 2, height + 2
- [ ] **Implement**: `BorderedBox.measure()` accounting for borders
- [ ] **Test**: `test_borderedbox_render_draws_box_drawing_chars()` — ┌─┐│ etc.
- [ ] **Test**: `test_borderedbox_render_shows_title()` — title appears in top border
- [ ] **Implement**: `BorderedBox.render()` with box-drawing characters
- [ ] **Test**: `test_borderedbox_add_child()` — single child stored
- [ ] **Implement**: `BorderedBox.add_child(self, component: Component)`

---

### Milestone 5: Focus Management
**Goal**: Stack-based focus (_focus_stack for overlays/context) with tab order (_focus_order for cycling).

#### Focus Stack (LIFO for Overlay/Context Management)
- [ ] **Test**: `test_focus_stack_empty_returns_none()` — _focused is None initially
- [ ] **Test**: `test_push_focus_adds_to_stack()` — stack grows
- [ ] **Implement**: `TUI.push_focus(self, component: Component | None)`
- [ ] **Test**: `test_push_focus_calls_on_blur_on_previous()` — previous.on_blur() invoked
- [ ] **Test**: `test_push_focus_calls_on_focus_on_new()` — component.on_focus() invoked
- [ ] **Test**: `test_push_focus_invalidates_both()` — invalidate called on both components
- [ ] **Implement**: Full lifecycle: on_blur() previous, on_focus() new, invalidation
- [ ] **Test**: `test_push_focus_error_restores_previous()` — pop on error, restore previous focus
- [ ] **Implement**: Error handling: pop and restore on on_focus() failure
- [ ] **Test**: `test_pop_focus_removes_from_stack()` — stack shrinks
- [ ] **Test**: `test_pop_focus_returns_popped_component()` — returns correct component
- [ ] **Implement**: `TUI.pop_focus(self) -> Component | None`
- [ ] **Test**: `test_pop_focus_calls_on_blur()` — component.on_blur() invoked
- [ ] **Test**: `test_pop_focus_calls_on_focus_on_previous()` — previous.on_focus() restored
- [ ] **Implement**: on_blur() lifecycle and previous restore
- [ ] **Test**: `test_set_focus_pops_then_pushes()` — replaces current focus
- [ ] **Implement**: `TUI.set_focus(self, component: Component | None)`

#### Focus Order (Tab Cycling)
- [ ] **Test**: `test_register_focusable_adds_to_order()` — _focus_order list grows
- [ ] **Implement**: `TUI.register_focusable(self, component: Component)`
- [ ] **Test**: `test_cycle_focus_moves_to_next()` — Tab moves to next in order
- [ ] **Test**: `test_cycle_focus_wraps_around()` — last to first wraps
- [ ] **Implement**: `TUI.cycle_focus(self, direction: int = 1)`

#### Focusable Protocol
- [ ] **Test**: `test_focusable_components_have_on_focus()` — Focusable protocol check using `@runtime_checkable` with `isinstance()`
- [ ] **Implement**: `@runtime_checkable class Focusable(Protocol)` with `on_focus()`, `on_blur()`, `handle_input() -> bool`
- [ ] **Test**: `test_focusable_get_cursor_position()` — returns relative position for IME
- [ ] **Implement**: `Focusable.get_cursor_position(self) -> tuple[int, int] | None`

---

### Milestone 6: Overlay System
**Goal**: Viewport-relative floating UI. **Note: Overlay is NOT a Component—it wraps a Component.**

#### OverlayPosition Dataclass
- [ ] **Test**: `test_overlay_position_fields()` — row, col, width, height, anchor stored
- [ ] **Implement**: `OverlayPosition` dataclass:
  - `row: int` — 0=top, -1=bottom (Python negative indexing)
  - `col: int = 0` — 0=left edge
  - `width: int = -1` — -1=auto-size to content
  - `height: int = -1` — -1=auto-size to content
  - `anchor: str | None = None` — "center", "top-left", "bottom-right", etc.

#### Overlay Class (Wrapper, Not Component)
- [ ] **Test**: `test_overlay_wraps_component()` — content is Component instance
- [ ] **Implement**: `Overlay.__init__(self, content: Component, position: OverlayPosition)`
- [ ] **Test**: `test_overlay_visible_flag()` — visible: bool = True
- [ ] **Implement**: `Overlay.visible` property
- [ ] **Test**: `test_overlay_z_index()` — z_index: int = 0 for stacking
- [ ] **Implement**: `Overlay.z_index` property

#### TUI Overlay Management
- [ ] **Test**: `test_show_overlay_adds_to_list()` — _overlays grows
- [ ] **Test**: `test_show_overlay_pushes_content_focus()` — overlay.content (Component) gets focus via push_focus(); NOT the Overlay wrapper itself
- [ ] **Implement**: `TUI.show_overlay(self, overlay: Overlay)` — adds to list, pushes overlay.content (the Component, not the Overlay wrapper) onto focus stack
- [ ] **Test**: `test_close_overlay_removes_from_list()` — _overlays shrinks
- [ ] **Test**: `test_close_overlay_pops_content_focus()` — focus restored via pop_focus() if overlay.content is current
- [ ] **Implement**: `TUI.close_overlay(self, overlay: Overlay)` — removes from list, pops focus if overlay.content is current
- [ ] **Test**: `test_nested_overlays_stack_focus()` — multiple overlays push/pop correctly; focus stack contains only Components, never Overlay wrappers
- [ ] **Implement**: Nested overlay support via focus stack

**Clarification:** The focus stack stores only `Component` instances, never `Overlay` wrappers. When showing an overlay, extract `overlay.content` (a Component) and push that. When comparing focus, compare Component references.

#### Overlay Position Resolution (TUI Method)
- [ ] **Test**: `test_resolve_position_absolute()` — row=5, col=10 → screen coordinates
- [ ] **Test**: `test_resolve_position_negative()` — row=-1 → bottom row
- [ ] **Test**: `test_resolve_position_anchor_center()` — anchor="center" calculates center position
- [ ] **Test**: `test_resolve_position_clamping()` — position clamped to terminal bounds
- [ ] **Implement**: `TUI._resolve_position(pos: OverlayPosition) -> tuple[int, int, int, int]` — returns (row, col, width, height)

#### Overlay Compositing
- [ ] **Test**: `test_composite_overlay_stamps_content()` — overlay lines merged into buffer
- [ ] **Test**: `test_composite_overlay_respects_position()` — content at resolved offset
- [ ] **Implement**: `TUI._composite_overlay(self, lines: list[RenderedLine], overlay: Overlay, viewport_top: int)`
- [ ] **Test**: `test_composite_overlay_clipping()` — content past terminal bounds truncated
- [ ] **Implement**: Clipping to terminal bounds (0->width/height)

#### Line Compositing with Wide Char Support
- [ ] **Test**: `test_composite_line_splices_content()` — overlay replaces base at column
- [ ] **Test**: `test_composite_line_respects_wide_chars()` — never splits wide characters
- [ ] **Implement**: `TUI._composite_line(base: str, overlay: str, col: int, width: int) -> str`
- [ ] **Test**: `test_pad_or_truncate_overlay()` — overlay padded/truncated to declared width
- [ ] **Implement**: `pad_or_truncate(text: str, width: int) -> str`

#### Z-Index Ordering
- [ ] **Test**: `test_overlays_composite_in_z_order()` — sorted by z_index ascending
- [ ] **Test**: `test_overlays_same_z_index_fifo()` — overlays with equal z_index composite in `_overlays` list insertion order (most recently shown on top)
- [ ] **Implement**: Sort overlays by `z_index` before compositing in `render_frame()`; ties broken by `_overlays` list order (insertion order, most recent appended to end)

---

### Milestone 7: Rich Integration (MVP Basic Support)
**Goal**: Basic markdown and code highlighting using mistune + pygments.

#### Dependencies
- [ ] **Add**: `mistune>=3.0` to optional dependencies `[rich]`
- [ ] **Add**: `pygments>=2.17` to optional dependencies `[rich]`

#### Markdown Component
- [ ] **Test**: `test_markdown_renders_headers()` — # Header becomes bold/underlined
- [ ] **Test**: `test_markdown_renders_bold()` — **text** becomes bold
- [ ] **Test**: `test_markdown_renders_lists()` — bullet points rendered correctly
- [ ] **Implement**: `Markdown(Component)` using mistune parser

#### Code Component
- [ ] **Test**: `test_code_renders_with_syntax_highlighting()` — colored tokens via pygments
- [ ] **Test**: `test_code_language_detection()` — language parameter used for lexer
- [ ] **Implement**: `CodeBlock(Component)` with pygments highlighting

#### Lazy Import Pattern
- [ ] **Test**: `test_rich_components_lazy_import()` — import error handled gracefully
- [ ] **Implement**: Lazy import in `components/rich.py` to avoid hard dependency

**File Location:** `src/pypitui/components/rich.py` (moved from top-level)

---

### Milestone 8: Error Handling & Demo
**Goal**: Graceful error handling and working examples.

#### Error Handling
- [ ] **Test**: `test_render_error_shows_overlay()` — component render error displays error overlay
- [ ] **Implement**: `TUI._show_error_overlay(message: str)` — displays error without crashing; message is plain text (not pre-formatted), BorderedBox handles wrapping, recommended max 200 chars
- [ ] **Test**: `test_terminal_write_error_cleanup()` — IOError triggers cleanup and exit
- [ ] **Implement**: Terminal write error handling with state restoration
- [ ] **Test**: `test_input_callback_error_continues()` — callback error shows overlay, continues running
- [ ] **Implement**: Input callback error isolation
- [ ] **Test**: `test_debug_mode_re_raises()` — PYPITUI_DEBUG=1 re-raises for stack traces
- [ ] **Implement**: Debug mode exception handling

#### PII Stripping in Logs
- [ ] **Test**: `test_log_sanitizes_passwords()` — password patterns replaced with ***
- [ ] **Test**: `test_log_sanitizes_tokens()` — token patterns replaced with ***
- [ ] **Implement**: Log sanitization patterns for sensitive data

#### Examples
- [ ] **E2E**: `demo.py` runs without errors — smoke test
- [ ] **Implement**: `examples/demo.py` with all component showcase
- [ ] **E2E**: `inputs.py` interactive test — type, submit, verify
- [ ] **Implement**: `examples/inputs.py` focused input demo
- [ ] **E2E**: `overlays.py` modal test — open, interact, close
- [ ] **Implement**: `examples/overlays.py` modal dialog examples

#### Public API
- [ ] **Implement**: Complete `src/pypitui/__init__.py` exports:
  - Core: `TUI`, `Component`, `Size`, `RenderedLine`, `Rect`
  - Components: `Container`, `Text`, `Input`, `SelectList`, `SelectItem`, `BorderedBox`
  - Overlays: `Overlay`, `OverlayPosition`
  - Input: `Key`, `matches_key`, `parse_key`, `MouseEvent`, `parse_mouse`
  - Focus: `Focusable` protocol
  - Errors: `LineOverflowError`
  - Styles: `StyleSpan`, `detect_color_support`
  - Utils: `truncate_to_width`, `slice_by_width`, `wcwidth`
- [ ] **Test**: `test_all_public_api_importable()` — verify each export can be imported from `pypitui`
- [ ] **Verify**: `from pypitui import TUI, Container, Text, Input` works

#### Documentation
- [ ] **Update**: README.md quickstart section
- [ ] **Add**: API docstrings for all public methods
- [ ] **Verify**: mypy strict mode passes
- [ ] **Verify**: ruff linting passes
- [ ] **Verify**: pytest all green
- [ ] **Test**: `test_file_structure_matches_spec()` — verify all files from "File Structure" section exist at correct paths

---

## Testing Infrastructure

### MockTerminal for Unit Tests
```python
class MockTerminal:
    """Mock terminal for testing escape sequence efficiency and output correctness."""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self._output: list[str] = []
        self._escape_counts: dict[str, int] = {}
    
    def write(self, data: str | bytes) -> None:
        s = data.decode() if isinstance(data, bytes) else data
        self._output.append(s)
        # Count escape sequences for efficiency metrics
        for seq in re.findall(r'\x1b\[[0-9;]*[A-Za-z]', s):
            self._escape_counts[seq] = self._escape_counts.get(seq, 0) + 1
    
    def get_escape_sequence_count(self) -> int:
        return sum(self._escape_counts.values())
    
    def get_output(self) -> str:
        return "".join(self._output)
    
    def clear_output(self) -> None:
        self._output.clear()
        self._escape_counts.clear()
```

### Efficiency Test Pattern
```python
def test_append_efficiency():
    term = MockTerminal(width=80, height=24)
    tui = TUI(term)
    
    # Setup: render initial content
    container = Container()
    container.add_child(Text("Line 1\nLine 2\nLine 3"))
    tui.add_child(container)
    tui.render_frame()
    
    # Measure: append more lines
    term.clear_output()
    container.add_child(Text("Line 4\nLine 5"))
    tui.render_frame()
    
    append_sequences = term.get_escape_sequence_count()
    
    # Baseline: what would full redraw cost?
    # Full redraw = cursor moves + clear lines for ALL 5 lines
    # Append = newlines + content for 2 new lines only
    # Assert: append uses ≤20% of full redraw sequences
    assert append_sequences <= FULL_REDRAW_BASELINE * 0.20
```

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-18 | Full diffing algorithm from day one | User requirement; append optimization critical for log-heavy UIs |
| 2026-03-18 | Zero-dependency core (except wcwidth) | Keep library lightweight; Rich optional for advanced formatting |
| 2026-03-18 | Hybrid testing strategy | Rendering engine is deterministic → unit tests; Interactive components need E2E |
| 2026-03-18 | Remove .agents/ folder | User direction; ultimate_demo.py not aligned with test-first approach |
| 2026-03-18 | Post-MVP: Images | Kitty Graphics Protocol adds complexity; ASCII fallback sufficient for v1 |
| 2026-03-18 | Threaded async input for user input | Dedicated input thread with callback dispatch; main loop polls |
| 2026-03-18 | Sync stdin/stdout for feature queries | DEC 2026 detection requires request/response during init |
| 2026-03-18 | Basic CSI input, full Kitty later | Enable full Kitty protocol post-MVP |
| 2026-03-18 | `mistune` for markdown | ~20KB, pure Python, no dependencies |
| 2026-03-18 | Rich integration in MVP | Basic wrapper for markdown + syntax highlighting via pygments |
| 2026-03-18 | 60 FPS performance target | <16ms max frame render time |
| 2026-03-18 | Escape sequence efficiency metric | Append-only emits ≤20% vs full redraw (measured via MockTerminal) |
| 2026-03-18 | Any scrollback change = full redraw | Scrollback content is immutable in terminal; cursor cannot reach it |
| 2026-03-18 | Component render caching post-MVP | Manual invalidation is error-prone; design better mechanism later |
| 2026-03-18 | Focus stack stores Components, not Overlays | Overlay.content (Component) is pushed; maintains type consistency |
| 2026-03-18 | handle_input() returns bool | True = consumed, False = bubble up; explicit flow control |
| 2026-03-18 | DEC 2026 feature detection post-MVP | Assume modern terminal support for MVP; add detection later |
| 2026-03-18 | SGR 1006 mouse protocol | Modern standard; focus by hit-detection on painted canvas |

---

## Open Questions

1. ~~**Markdown Library**: `mistune` selected.~~
2. ~~**Input Handling**: Threaded async for user input; sync for feature queries.~~
3. ~~**E2E Framework**: tmux-based (existing skill) vs `pytest-terminal` — sticking with tmux for consistency with pi-tui origins.~~
4. ~~**Scrollback handling**: Any change in scrollback triggers full redraw.~~
5. ~~**Component caching**: Deferred post-MVP.~~

---

## Related Files

- `docs/ARCHITECTURE.md` — Full technical specification
- `docs/APPEND_VS_SCROLL.md` — Diffing algorithm details
- `docs/VT100.md` — Escape sequence reference
- `pyproject.toml` — Project configuration

---

## File Structure

```
src/pypitui/
├── __init__.py          # Public exports (TUI, Container, Text, Input, etc.)
├── tui.py               # TUI class, rendering loop, overlay management
├── component.py         # Component base class, Size, RenderedLine, Rect
├── components/          # Built-in components
│   ├── __init__.py
│   ├── container.py     # Vertical layout
│   ├── text.py          # Static text
│   ├── input.py         # Text input with cursor
│   ├── select.py        # Selection list
│   ├── bordered.py      # Box with borders
│   └── rich.py          # Optional Rich integration (markdown, code)
├── overlay.py           # Overlay wrapper class (NOT a Component)
├── terminal.py          # Terminal I/O abstraction, threaded input
├── keys.py              # Key parsing (basic CSI)
├── mouse.py             # Mouse event parsing (SGR 1006)
├── styles.py            # Color and style codes
└── utils.py             # wcwidth, truncate_to_width, slice_by_width

tests/
├── unit/                # Unit tests (deterministic)
│   ├── test_terminal.py
│   ├── test_tui.py
│   ├── test_components.py
│   ├── test_overlay.py
│   ├── test_styles.py
│   └── test_utils.py
├── e2e/                 # E2E tests (interactive)
│   ├── test_input.py
│   ├── test_select.py
│   └── test_overlays.py
└── mocks.py             # MockTerminal and other test utilities

examples/
├── demo.py              # Full showcase
├── inputs.py            # Input handling
└── overlays.py          # Modal dialogs
```

**Key Architectural Notes:**
- `Overlay` is in `overlay.py` — it is **NOT** a Component, it wraps a Component
- `OverlayPosition` is defined alongside `Overlay` for viewport-relative positioning
- `TUI` manages overlays via `show_overlay()`, `close_overlay()`, and `_composite_overlay()`
- Rich components are optional via `components/rich.py` with lazy imports
- Threaded input handling lives in `terminal.py` with `start()`/`stop()` lifecycle
- Hardware cursor tracking in TUI for efficient diff output and IME positioning
- Focus stack stores Components (overlay.content), not Overlay wrappers

---

## Post-MVP Enhancements

### Component Render Caching
**Problem:** Text wrapping is expensive for large content.

**Current (MVP):** No component-level caching; rely on TUI diff cache.

**Future:** Intelligent invalidation system where components cache renders and TUI invalidates automatically when width changes or explicit invalidation occurs.

**Challenge:** Manual `invalidate()` calls are error-prone. Need automatic cache invalidation when:
- Terminal width changes
- Component properties change
- Parent layout changes

### DEC 2026 Feature Detection
**Current (MVP):** Assume DEC 2026 support; always emit sync codes.

**Future:** Query during `Terminal.start()` before spawning async thread:
```python
def start(self, on_input):
    # Synchronous query
    self._dec2026_supported = self._sync_query_dec2026()
    # Then start async thread
    self._input_thread = threading.Thread(target=self._read_loop)
```

### Kitty Keyboard Protocol
**Current (MVP):** Basic CSI sequences for arrow keys, enter, escape.

**Future:** Full progressive enhancement with key release events, modifier state, and Unicode key input via `CSI > 1 u`.

### Kitty Graphics Protocol
**Current (MVP):** ASCII fallback for images.

**Future:** Full graphics support with terminal capability detection.

---

## Progress Summary

| Milestone | Status | Tests | Implement | Total |
|-----------|--------|-------|-----------|-------|
| 1: Terminal | ✅ | 24/24 | 24/24 | 48/48 |
| 2: Rendering | 🟡 | 10/28 | 10/28 | 20/56 |
| 3: Components | ⬜ | 0/17 | 0/17 | 0/34 |
| 4: Interactive | ⬜ | 0/16 | 0/16 | 0/32 |
| 5: Focus | ⬜ | 0/15 | 0/15 | 0/30 |
| 6: Overlays | ⬜ | 0/18 | 0/18 | 0/36 |
| 7: Rich | ⬜ | 0/6 | 0/6 | 0/12 |
| 8: Error Handling & Demo | ⬜ | 0/13 | 0/13 | 0/26 |
| **Total** | **🟡** | **24/137** | **24/137** | **48/274** |

**Legend:** ⬜ Not started | 🟡 In Progress | ✅ Complete
7** | **0/137** | **0/274** |
*0/274** |
* | **0/274** |
*0/274** |
** |
**0/274** |
*0/274** |
* | **0/274** |
*0/274** |
** |
** |

*0/274** |
* | **0/274** |
*0/274** |
** |

*0/274** |
* | **0/274** |
*0/274** |
** |
