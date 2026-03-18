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
3. **Terminal abstraction** with DEC 2026 sync codes and Kitty keyboard protocol
4. **Focus management** with stack-based focus and tab order
5. **Built-in components**: Container, Text, Input, SelectList, BorderedBox, Overlay
6. **Test-first development** with hybrid strategy: unit tests for rendering engine, E2E for interactive components

---

## Architecture Highlights

### Differential Rendering
- Track `_previous_lines` (row -> content hash)
- Detect appends vs. edits for optimal output
- Handle viewport shifts when content exceeds terminal height
- Full clear+redraw when editing scrollback (above visible viewport)
- DEC 2026 synchronized updates for atomic frames

### Component System
- Abstract `Component` base class with `measure()` and `render()`
- Vertical-only layout (no flexbox/grids—keep it simple)
- Parent containers distribute width; children handle internal layout
- Overlays for viewport-relative positioning (fixed headers/footers)

### Zero-Dependency Core
- Only `wcwidth` for Unicode width handling
- Rich integration optional, isolated in `rich_components.py`
- Markdown/code highlighting via lighter alternative (mistune/pygments)

---

## Success Criteria

1. `examples/demo.py` runs without errors showing all component types
2. Differential rendering produces minimal escape sequences (verified by debug logs)
3. 80%+ unit test coverage for `tui.py`, `terminal.py`, `styles.py`
4. E2E tests verify Input, SelectList, and Overlay interactions
5. mypy strict mode passes with zero errors
6. Pre-commit hooks (ruff, mypy, pytest) all green

---

## Milestones

### Milestone 1: Foundation & Terminal Abstraction
**Goal**: Low-level terminal I/O with DEC 2026 sync codes and input parsing.

#### terminal.py - Core Terminal I/O
- [ ] **Test**: `test_terminal_enter_raw_mode()` — verify tty flags are saved and raw mode is set
- [ ] **Implement**: `Terminal.__enter__()` and `__exit__()` for context manager raw mode
- [ ] **Test**: `test_terminal_write_emits_escape_sequence()` — verify bytes written to fd
- [ ] **Implement**: `Terminal.write(data: str | bytes)` method
- [ ] **Test**: `test_terminal_move_cursor()` — verify CSI row;colH sequence
- [ ] **Implement**: `Terminal.move_cursor(col: int, row: int)` method
- [ ] **Test**: `test_terminal_clear_line()` — verify CSI 2K sequence
- [ ] **Implement**: `Terminal.clear_line()` method
- [ ] **Test**: `test_terminal_clear_screen()` — verify CSI 2J CSI 3J sequence
- [ ] **Implement**: `Terminal.clear_screen()` method
- [ ] **Test**: `test_terminal_hide_show_cursor()` — verify CSI ?25l and CSI ?25h
- [ ] **Implement**: `Terminal.hide_cursor()` and `show_cursor()` methods

#### DEC 2026 Synchronized Output
- [ ] **Test**: `test_dec2026_start_end_constants()` — verify escape sequence bytes
- [ ] **Implement**: `DEC_2026_START = "\x1b[?2026h"`, `DEC_2026_END = "\x1b[?2026l"`
- [ ] **Test**: `test_terminal_write_within_sync_block()` — verify sequences wrapped correctly
- [ ] **Implement**: `Terminal.write_sync_block(data: str)` context helper

#### Color Support Detection
- [ ] **Test**: `test_detect_color_support_no_color()` — NO_COLOR=1 returns 0
- [ ] **Test**: `test_detect_color_support_force_color()` — FORCE_COLOR=3 returns 3
- [ ] **Test**: `test_detect_color_support_truecolor()` — COLORTERM=truecolor returns 3
- [ ] **Test**: `test_detect_color_support_256color()` — TERM=256color returns 2
- [ ] **Implement**: `detect_color_support() -> int` function

#### Key Parsing (Kitty Protocol)
- [ ] **Test**: `test_key_enum_values()` — verify Key.ENTER, Key.ESCAPE, Key.TAB bytes
- [ ] **Implement**: `Key` enum with common keys
- [ ] **Test**: `test_matches_key_exact_match()` — matches_key(b"\r", Key.ENTER) is True
- [ ] **Test**: `test_matches_key_no_match()` — matches_key(b"x", Key.ENTER) is False
- [ ] **Implement**: `matches_key(data: bytes, key: Key) -> bool`
- [ ] **Test**: `test_parse_key_simple()` — parse_key(b"q") returns "q"
- [ ] **Test**: `test_parse_key_control()` — parse_key(b"\x01") returns Key.ctrl("a")
- [ ] **Implement**: `parse_key(data: bytes) -> str | Key`

#### Mouse Events
- [ ] **Test**: `test_parse_mouse_click()` — parse SGR extended mouse sequence
- [ ] **Test**: `test_parse_mouse_release()` — verify release event parsing
- [ ] **Implement**: `MouseEvent` dataclass and `parse_mouse(data: bytes) -> MouseEvent | None`

---

### Milestone 2: Rendering Engine
**Goal**: Differential rendering with full viewport-aware diffing.

#### TUI Class Foundation
- [ ] **Test**: `test_tui_init_caches_previous_lines()` — _previous_lines is empty dict
- [ ] **Implement**: `TUI.__init__(self, terminal: Terminal)`
- [ ] **Test**: `test_tui_add_child_sets_root()` — add_child stores component
- [ ] **Implement**: `TUI.add_child(self, component: Component)`

#### Differential Rendering Core
- [ ] **Test**: `test_output_diff_writes_changed_lines()` — only changed lines emit escape sequences
- [ ] **Test**: `test_output_diff_skips_unchanged_lines()` — unchanged lines generate no output
- [ ] **Implement**: `TUI._output_diff(self, lines: list[str])` basic version

#### Viewport Tracking
- [ ] **Test**: `test_viewport_top_calculation()` — viewport_top = max(0, content_height - term_height)
- [ ] **Test**: `test_viewport_top_zero_when_content_fits()` — 3 lines on 24-line terminal = 0
- [ ] **Test**: `test_viewport_top_nonzero_when_content_scrolls()` — 30 lines on 24-line terminal = 6
- [ ] **Implement**: `TUI._calculate_viewport_top(self, content_height: int) -> int`

#### Append Optimization
- [ ] **Test**: `test_detect_append_start()` — pure append returns appendStart=True
- [ ] **Test**: `test_detect_edit_not_append()` — middle edit returns appendStart=False
- [ ] **Implement**: `TUI._detect_append(self, new_lines: list[str], prev_lines: dict[int, str]) -> bool`
- [ ] **Test**: `test_append_uses_newline_scrolling()` — append writes \r\n not cursor positioning
- [ ] **Implement**: Append path in `_output_diff()` using `\r\n` for terminal natural scrolling

#### Scrollback-Aware Redraw
- [ ] **Test**: `test_edit_above_viewport_triggers_full_redraw()` — first_changed < viewport_top
- [ ] **Test**: `test_edit_in_viewport_does_not_clear()` — first_changed >= viewport_top
- [ ] **Implement**: Scrollback detection and `_full_render(clear=True)` path

#### Component Invalidation
- [ ] **Test**: `test_invalidate_component_clears_rect_lines()` — specific rows removed from _previous_lines
- [ ] **Implement**: `TUI.invalidate_component(self, component: Component)`

#### Terminal Resize
- [ ] **Test**: `test_resize_clears_previous_lines()` — _previous_lines cleared on resize
- [ ] **Test**: `test_resize_updates_terminal_dimensions()` — width/height updated
- [ ] **Implement**: `TUI.on_resize(self, new_width: int, new_height: int)`

---

### Milestone 3: Component Base & Container
**Goal**: Component lifecycle and vertical layout.

#### Component ABC
- [ ] **Test**: `test_component_abstract_methods()` — cannot instantiate without measure/render
- [ ] **Implement**: `Component` ABC with `measure()`, `render()`, `invalidate()`
- [ ] **Test**: `test_component_invalidation_bubbles()` — invalidate() calls _child_invalidated()
- [ ] **Implement**: `Component.invalidate(self)` and `_child_invalidated(self, child)`

#### Container Component
- [ ] **Test**: `test_container_measure_returns_sum_of_children()` — height = sum(child heights)
- [ ] **Implement**: `Container.measure(self, available_width: int, available_height: int) -> Size`
- [ ] **Test**: `test_container_render_stacks_vertically()` — children rendered sequentially
- [ ] **Implement**: `Container.render(self, width: int) -> list[str]`
- [ ] **Test**: `test_container_add_child_appends_to_list()` — children list grows
- [ ] **Implement**: `Container.add_child(self, component: Component)`
- [ ] **Test**: `test_container_clear_children()` — children list emptied
- [ ] **Implement**: `Container.clear_children(self)`

#### Text Component
- [ ] **Test**: `test_text_measure_single_line()` — height=1 for simple text
- [ ] **Test**: `test_text_measure_multi_line()` — height=n for n lines
- [ ] **Implement**: `Text.measure(self, available_width: int, available_height: int) -> Size`
- [ ] **Test**: `test_text_render_returns_lines()` — returns list of strings
- [ ] **Test**: `test_text_render_wraps_long_lines()` — wrapping at width boundary
- [ ] **Implement**: `Text.render(self, width: int) -> list[str]` with wrapping
- [ ] **Test**: `test_text_render_cached()` — second call returns cached result
- [ ] **Implement**: Text render caching with `_cached: list[str] | None`

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
- [ ] **Implement**: `Input.render(self, width: int) -> list[str]`
- [ ] **Test**: `test_input_handle_key_appends_char()` — "a" typed adds "a" to content
- [ ] **Test**: `test_input_handle_backspace_removes_char()` — backspace removes last char
- [ ] **Implement**: `Input.handle_input(self, data: bytes)`
- [ ] **Test**: `test_input_cursor_position()` — returns (row, col) tuple
- [ ] **Implement**: `Input.get_cursor_position(self) -> tuple[int, int] | None`
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
- [ ] **Implement**: `SelectList.handle_input()` for Up/Down/Enter

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
**Goal**: Stack-based focus with tab order.

#### Focus Stack
- [ ] **Test**: `test_focus_stack_empty_returns_none()` — _focused is None initially
- [ ] **Test**: `test_push_focus_adds_to_stack()` — stack grows
- [ ] **Implement**: `TUI.push_focus(self, component: Component | None)`
- [ ] **Test**: `test_push_focus_calls_on_focus()` — component.on_focus() invoked
- [ ] **Test**: `test_push_focus_invalidates_component()` — invalidate called
- [ ] **Implement**: on_focus() lifecycle and invalidation
- [ ] **Test**: `test_pop_focus_removes_from_stack()` — stack shrinks
- [ ] **Test**: `test_pop_focus_returns_popped_component()` — returns correct component
- [ ] **Implement**: `TUI.pop_focus(self) -> Component | None`
- [ ] **Test**: `test_pop_focus_calls_on_blur()` — component.on_blur() invoked
- [ ] **Implement**: on_blur() lifecycle
- [ ] **Test**: `test_set_focus_pops_then_pushes()` — replaces current focus
- [ ] **Implement**: `TUI.set_focus(self, component: Component | None)`

#### Focus Order / Tab Cycling
- [ ] **Test**: `test_register_focusable_adds_to_order()` — _focus_order list grows
- [ ] **Implement**: `TUI.register_focusable(self, component: Component)`
- [ ] **Test**: `test_cycle_focus_moves_to_next()` — Tab moves to next in order
- [ ] **Test**: `test_cycle_focus_wraps_around()` — last to first wraps
- [ ] **Implement**: `TUI.cycle_focus(self, direction: int = 1)`

#### Focusable Protocol
- [ ] **Test**: `test_focusable_components_have_on_focus()` — Focusable protocol check
- [ ] **Implement**: `Focusable` protocol with `on_focus()`, `on_blur()`, `handle_input()`

---

### Milestone 6: Overlay System
**Goal**: Viewport-relative floating UI.

#### OverlayPosition
- [ ] **Test**: `test_overlay_position_absolute()` — row=5, col=10 resolved correctly
- [ ] **Test**: `test_overlay_position_negative_indexing()` — row=-1 is bottom
- [ ] **Test**: `test_overlay_position_anchor_center()` — anchor="center" calculates center
- [ ] **Implement**: `OverlayPosition` dataclass with `resolve()` method

#### Overlay Class
- [ ] **Test**: `test_overlay_init_stores_content()` — content and position stored
- [ ] **Implement**: `Overlay.__init__(self, content: Component, position: OverlayPosition)`
- [ ] **Test**: `test_overlay_visibility_toggle()` — visible flag can be set
- [ ] **Implement**: `Overlay.visible` property

#### TUI Overlay Management
- [ ] **Test**: `test_show_overlay_adds_to_list()` — _overlays grows
- [ ] **Test**: `test_show_overlay_pushes_focus()` — overlay content gets focus
- [ ] **Implement**: `TUI.show_overlay(self, overlay: Overlay)`
- [ ] **Test**: `test_close_overlay_removes_from_list()` — _overlays shrinks
- [ ] **Test**: `test_close_overlay_pops_focus()` — focus restored to previous
- [ ] **Implement**: `TUI.close_overlay(self, overlay: Overlay)`

#### Overlay Compositing
- [ ] **Test**: `test_composite_overlay_stamps_content()` — overlay lines appear in buffer
- [ ] **Test**: `test_composite_overlay_respects_position()` — content at correct offset
- [ ] **Implement**: `TUI._composite_overlay(self, lines: list[str], overlay: Overlay)`
- [ ] **Test**: `test_composite_overlay_clipping()` — content past bounds is truncated
- [ ] **Implement**: Clipping to terminal bounds

#### Z-Index Ordering
- [ ] **Test**: `test_overlays_composite_in_z_order()` — higher z_index renders on top
- [ ] **Implement**: Sort overlays by `z_index` before compositing

---

### Milestone 7: Rich Integration (Optional)
**Goal**: Markdown and code highlighting via lighter alternative.

#### Research
- [ ] **Spike**: Evaluate `mistune` vs `markdown-it-py` for markdown parsing
- [ ] **Spike**: Evaluate `pygments` alone for code highlighting
- [ ] **Decision**: Choose lighter library combination

#### Markdown Component
- [ ] **Test**: `test_markdown_renders_headers()` — # Header becomes bold/underlined
- [ ] **Test**: `test_markdown_renders_bold()` — **text** becomes bold
- [ ] **Implement**: `Markdown(Component)` using chosen library

#### Code Component
- [ ] **Test**: `test_code_renders_with_syntax_highlighting()` — colored tokens
- [ ] **Implement**: `CodeBlock(Component)` with pygments highlighting

---

### Milestone 8: Demo & Documentation
**Goal**: Working demo and user-facing docs.

#### Examples
- [ ] **E2E**: `demo.py` runs without errors — smoke test
- [ ] **Implement**: `examples/demo.py` with all component showcase
- [ ] **E2E**: `inputs.py` interactive test — type, submit, verify
- [ ] **Implement**: `examples/inputs.py` focused input demo
- [ ] **E2E**: `overlays.py` modal test — open, interact, close
- [ ] **Implement**: `examples/overlays.py` modal dialog examples

#### Public API
- [ ] **Implement**: `src/pypitui/__init__.py` exports
- [ ] **Verify**: `from pypitui import TUI, Container, Text, Input` works

#### Documentation
- [ ] **Update**: README.md quickstart section
- [ ] **Add**: API docstrings for all public methods
- [ ] **Verify**: mypy strict mode passes
- [ ] **Verify**: ruff linting passes
- [ ] **Verify**: pytest all green

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-18 | Full diffing algorithm from day one | User requirement; append optimization critical for log-heavy UIs |
| 2026-03-18 | Zero-dependency core (except wcwidth) | Keep library lightweight; Rich optional for advanced formatting |
| 2026-03-18 | Hybrid testing strategy | Rendering engine is deterministic → unit tests; Interactive components need E2E |
| 2026-03-18 | Remove .agents/ folder | User direction; ultimate_demo.py not aligned with test-first approach |
| 2026-03-18 | Post-MVP: Images | Kitty Graphics Protocol adds complexity; ASCII fallback sufficient for v1 |

---

## Open Questions

1. **Markdown Library**: `mistune` (~20KB) vs `markdown-it-py` (~150KB) — both lighter than Rich (~10MB). Mistune is pure Python with no dependencies.
2. **Test Runner**: pytest with pytest-asyncio for input handling tests.
3. **E2E Framework**: tmux-based (existing skill) vs `pytest-terminal` — sticking with tmux for consistency with pi-tui origins.

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
├── __init__.py          # Public exports
├── tui.py               # TUI class, rendering loop
├── component.py         # Component base class
├── components/          # Built-in components
│   ├── __init__.py
│   ├── container.py     # Vertical layout
│   ├── text.py          # Static text
│   ├── input.py         # Text input with cursor
│   ├── select.py        # Selection list
│   ├── bordered.py      # Box with borders
│   └── overlay.py       # Floating overlays
├── terminal.py          # Terminal I/O abstraction
├── keys.py              # Key parsing (Kitty protocol)
├── mouse.py             # Mouse event parsing
├── styles.py            # Color and style codes
└── utils.py             # wcwidth, truncation helpers

tests/
├── unit/                # Unit tests (deterministic)
│   ├── test_terminal.py
│   ├── test_tui.py
│   ├── test_components.py
│   └── test_styles.py
└── e2e/                 # E2E tests (interactive)
    ├── test_input.py
    ├── test_select.py
    └── test_overlays.py

examples/
├── demo.py              # Full showcase
├── inputs.py            # Input handling
└── overlays.py          # Modal dialogs
```

---

## Progress Summary

| Milestone | Status | Tests | Implement | Total |
|-----------|--------|-------|-----------|-------|
| 1: Terminal | ⬜ | 0/14 | 0/14 | 0/28 |
| 2: Rendering | ⬜ | 0/14 | 0/14 | 0/28 |
| 3: Components | ⬜ | 0/12 | 0/12 | 0/24 |
| 4: Interactive | ⬜ | 0/14 | 0/14 | 0/28 |
| 5: Focus | ⬜ | 0/12 | 0/12 | 0/24 |
| 6: Overlays | ⬜ | 0/12 | 0/12 | 0/24 |
| 7: Rich | ⬜ | 0/3 | 0/3 | 0/6 |
| 8: Demo | ⬜ | 0/3 | 0/3 | 0/6 |
| **Total** | **⬜** | **0/84** | **0/84** | **0/168** |
