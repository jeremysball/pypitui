# PyPiTUI Feature Verification

This document verifies that core scrollback and streaming features work correctly. Each section describes the expected behavior and references the tests that verify it.

---

## 1. Scrollback Buffer

### Expected Behavior

When content exceeds terminal height, older lines flow into the terminal's native scrollback buffer. Users can scroll back through history using Shift+PgUp, mouse wheel, or their terminal's scroll commands.

### Implementation

- `_max_lines_rendered` tracks the total height of all content ever rendered
- `_calculate_first_visible_row()` computes which content line is at the top of the viewport
- Content is never clipped; the terminal scrolls naturally via newlines

### Verification

| Test | What It Verifies |
|------|------------------|
| `TestCalculateFirstVisibleRow::test_empty_content_returns_zero` | No content means viewport starts at row 0 |
| `TestCalculateFirstVisibleRow::test_content_fits_terminal_returns_zero` | Content smaller than terminal shows from row 0 |
| `TestCalculateFirstVisibleRow::test_content_exceeds_terminal_by_one` | 25 lines in 24-row terminal: first visible is row 1 |
| `TestCalculateFirstVisibleRow::test_content_twice_terminal_height` | 48 lines in 24-row terminal: first visible is row 24 |
| `TestCalculateFirstVisibleRow::test_large_scrollback_buffer` | 100 lines in 24-row terminal: first visible is row 76 |

### Manual Verification

```bash
uv run python examples/scrollback_demo.py
# Press Enter to add lines until content exceeds terminal height
# Use Shift+PgUp to scroll back through history
```

---

## 2. Synchronized Output (DEC 2026)

### Expected Behavior

Updates are batched and applied atomically to prevent flickering. The terminal receives all cursor movements and content changes in a single buffer, then renders the complete frame.

### Implementation

- `_begin_sync()` returns `\x1b[?2026h` (enable synchronized output)
- `_end_sync()` returns `\x1b[?2026l` (disable synchronized output)
- All updates in `render_frame()` are wrapped between these sequences

### Verification

| Test | What It Verifies |
|------|------------------|
| `TestSynchronizedOutput::test_begin_sync_returns_correct_sequence` | `_begin_sync()` returns `\x1b[?2026h` |
| `TestSynchronizedOutput::test_end_sync_returns_correct_sequence` | `_end_sync()` returns `\x1b[?2026l` |
| `TestSynchronizedOutput::test_sync_wrapper_produces_correct_sequence` | Combined wrapper is syntactically correct |
| `TestSynchronizedOutput::test_sync_sequences_are_constant_length` | Each sequence is exactly 8 characters |

### Example Output

```
\x1b[?2026h\x1b[5;1HHello World\x1b[?2026l
```

The terminal buffers this entire sequence before rendering, preventing partial updates.

---

## 3. Relative Cursor Movement

### Expected Behavior

Cursor movement uses relative sequences (`\x1b[nA` for up, `\x1b[nB` for down) rather than absolute positioning. This respects the terminal's scroll state and works correctly when content has scrolled.

### Implementation

- `_move_cursor_relative(target_row)` calculates delta from current position
- `_hardware_cursor_row` tracks the actual cursor position
- Movement commands update `_hardware_cursor_row` after execution

### Verification

| Test | What It Verifies |
|------|------------------|
| `TestRelativeCursorMovement::test_move_cursor_down_positive_delta` | Moving down 5 rows produces `\x1b[5B` |
| `TestRelativeCursorMovement::test_move_cursor_up_negative_delta` | Moving up 7 rows produces `\x1b[7A` |
| `TestRelativeCursorMovement::test_move_cursor_zero_delta_returns_empty` | No movement needed returns empty string |
| `TestRelativeCursorMovement::test_multiple_relative_movements` | Series of movements track position correctly |
| `TestRelativeCursorMovement::test_terminal_move_cursor_up` | `Terminal.move_cursor_up(n)` produces correct sequence |
| `TestRelativeCursorMovement::test_terminal_move_cursor_down` | `Terminal.move_cursor_down(n)` produces correct sequence |

### Why Relative Movement Matters

Absolute positioning (`\x1b[row;colH`) addresses screen coordinates, not content coordinates. When content scrolls:

```
Terminal: 24 rows
Content: 100 lines (lines 0-75 in scrollback, lines 76-99 visible)

\x1b[5;1H always goes to SCREEN row 5 (content line 81)
\x1b[19A moves up 19 lines from current position (respects scroll state)
```

---

## 4. Working Area Tracking

### Expected Behavior

The TUI tracks a "working area" — the virtual canvas of all rendered content. This area grows as content is added but never shrinks (unless explicitly cleared). This ensures consistent positioning even when content varies in size.

### Implementation

- `_max_lines_rendered` grows with each render, never shrinks
- `_first_visible_row_previous` tracks the previous viewport state

### Verification

| Test | What It Verifies |
|------|------------------|
| `TestWorkingAreaTracking::test_max_lines_rendered_updates_on_render` | Counter updates correctly after render |
| `TestWorkingAreaTracking::test_max_lines_rendered_grows_not_shrinks` | Adding 10 lines, then 3: counter stays at 10 |
| `TestWorkingAreaTracking::test_max_lines_rendered_grows_with_more_content` | Adding more content grows the counter |
| `TestFirstVisibleRowPrevious::test_initial_value_is_zero` | Initial state is correct |

### Example

```
Render 1: 10 lines → _max_lines_rendered = 10
Render 2: 5 lines  → _max_lines_rendered = 10 (doesn't shrink)
Render 3: 15 lines → _max_lines_rendered = 15 (grows)
```

---

## 5. Overlay Positioning with Scrollback

### Expected Behavior

Overlays use content coordinates, not screen coordinates. When content scrolls, overlays stay attached to their content row. Anchor-based overlays (center, top-left, etc.) remain fixed on screen.

### Implementation

- `_composite_overlays()` receives `viewport_top` parameter
- Overlay rows are content row indices
- Anchor-based overlays calculate position relative to viewport

### Verification

| Test | What It Verifies |
|------|------------------|
| `TestOverlayViewportPositioning::test_overlay_visible_at_bottom_of_scrolled_content` | Overlay at row 18 visible when viewport starts at row 10 |
| `TestOverlayViewportPositioning::test_overlay_center_anchor_with_scrolled_content` | Center anchor works with scrolled content |
| `TestOverlayViewportPositioning::test_composite_overlays_with_viewport_offset` | Compositing correctly adjusts for viewport offset |
| `TestOverlayViewportPositioning::test_overlay_at_viewport_boundary` | Overlay at exact viewport boundary is visible |
| `TestOverlayViewportPositioning::test_overlay_below_viewport_not_rendered` | Overlay outside viewport is not rendered |

### Content vs Screen Coordinates

```
Content rows: 0, 1, 2, ..., 99 (total 100 lines)
Terminal: 24 rows
Viewport: shows content rows 76-99

Overlay at content row 80:
  - Screen row = 80 - 76 = 4
  - Visible ✓

Overlay at content row 50:
  - Screen row = 50 - 76 = -26
  - Not visible (in scrollback)
```

---

## 6. Streaming Content Updates

### Expected Behavior

New content causes the terminal to scroll via newlines. Existing content in scrollback is frozen and cannot be modified. Only the visible portion is re-rendered each frame.

### Implementation

- Content growth emits newlines to scroll the terminal
- Differential rendering compares against `_previous_lines`
- Only changed lines within the viewport are updated

### Verification

| Test | What It Verifies |
|------|------------------|
| `TestDifferentialRenderingWithScrollback::test_content_exceeds_terminal_without_growth` | No newlines when content hasn't grown |
| `TestDifferentialRenderingWithScrollback::test_visible_lines_update_when_scrolled` | Only visible lines update |
| `TestDifferentialRenderingWithScrollback::test_scrollback_lines_frozen` | Lines in scrollback cannot be modified |

### Streaming Flow

```
Frame 1: 20 lines rendered, terminal shows rows 0-19
Frame 2: 25 lines rendered
  - Emit 5 newlines (scrolls terminal)
  - Render lines 20-24
  - Lines 0-19 now in scrollback (frozen)
Frame 3: 25 lines (same count)
  - No newlines (no growth)
  - Only update lines that changed
```

---

## Test Coverage Summary

All 167 tests pass. Key test files:

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_scrollback.py` | 25 | Scrollback, sync, cursor movement, working area |
| `tests/test_overlay.py` | 30 | Overlay positioning, compositing, viewport handling |
| `tests/test_tui.py` | 20 | Core TUI functionality |
| `tests/test_input.py` | 15 | Input component |
| `tests/test_keys.py` | 40 | Keyboard handling |

Run verification:

```bash
uv run pytest -v                                    # All tests
uv run pytest tests/test_scrollback.py -v          # Scrollback tests
uv run pytest tests/test_overlay.py -v             # Overlay tests
```

---

## Manual Testing Checklist

- [x] Run `uv run python examples/demo.py` — all screens work
- [x] Run `uv run python examples/scrollback_demo.py` — scrollback works with Shift+PgUp
- [x] Test terminal resize during operation
- [x] Test with small terminal (80x24)
- [x] Test with large terminal (120x40)
- [x] Test rapid content updates (streaming)
