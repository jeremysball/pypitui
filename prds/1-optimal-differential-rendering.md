# PRD: Optimal Differential Rendering

**Issue**: #1
**Priority**: High
**Status**: Draft

---

## Problem

Current `render_frame()` implementation has a critical flaw: when ANY visible content changes, it re-renders ALL visible lines. This defeats the purpose of differential rendering and wastes:

1. **CPU cycles** - Re-rendering unchanged lines
2. **Terminal bandwidth** - Sending unnecessary escape sequences
3. **Potential for flicker** - More data in sync buffer

### Current Behavior

```python
# Current: If any line changed, re-render ALL visible lines
if content_changed:
    for screen_row in range(term_height):
        buffer += self._move_cursor_relative(screen_row)
        buffer += "\r\x1b[2K"  # Clear line
        buffer += lines[content_row]  # Re-render
```

### Expected Behavior

```python
# Optimal: Only update lines that actually changed
for screen_row in range(term_height):
    if lines[content_row] != self._previous_lines[content_row]:
        buffer += self._move_cursor_relative(screen_row)
        buffer += "\r\x1b[2K"
        buffer += lines[content_row]  # Only render changed line
```

---

## Solution

Implement true line-by-line differential rendering:

1. **Line-by-line comparison** - Compare each line to previous frame
2. **Selective updates** - Only write changed lines to terminal
3. **Preserve scrollback behavior** - Content growth still works via newlines
4. **Optimize cursor movement** - Skip cursor moves for unchanged lines

---

## Technical Design

### Current Flow

```
render_frame():
  1. Render all children to lines[]
  2. Check if ANY visible content changed
  3. If changed: re-render ALL visible lines
  4. Update _previous_lines
```

### New Flow

```
render_frame():
  1. Render all children to lines[]
  2. For each visible line:
     a. Compare to _previous_lines[i]
     b. If changed: add to update list
  3. Only render lines in update list
  4. Update _previous_lines
```

### Edge Cases

1. **Content growth** - New lines scroll into view
   - Emit newlines to scroll terminal
   - Render only the new visible portion

2. **Content shrink** - Lines removed
   - Clear the orphaned lines
   - Don't re-render unchanged lines above

3. **Terminal resize** - Force full redraw
   - Keep existing behavior (clear _previous_lines)

4. **First frame** - No _previous_lines
   - Render all lines (as before)

5. **Overlay changes** - Overlay content differs from base
   - Compare final composited lines, not base lines

---

## Milestones

### Milestone 1: Core Line-by-Line Diff ✅
- [x] Implement line-by-line comparison in `render_frame()`
- [x] Only render lines that differ from `_previous_lines`
- [x] Handle first-frame case (no previous state)

### Milestone 2: Content Growth Optimization ✅
- [x] When content grows, only render new visible lines
- [x] Preserve scrollback newline emission
- [x] Don't re-render lines already in scrollback

### Milestone 3: Content Shrink Handling ✅
- [x] Clear orphaned lines when content shrinks
- [x] Don't re-render unchanged lines above removed content

### Milestone 4: Tests & Verification ✅
- [x] All 167 existing tests pass
- [x] MockTerminal verification shows optimal output
- [x] Zero lines rendered when nothing changed
- [x] Exactly 1 line rendered when 1 line changed

### Milestone 5: Performance Validation ✅
- [x] Output buffer reduced to only changed lines
- [x] No visual regressions
- [x] Scrollback still works correctly

---

## Success Criteria

1. **Correctness**: All 167 existing tests pass
2. **Efficiency**: Output buffer size reduced by >50% for typical updates
3. **Visual**: No flicker, no missing content
4. **Scrollback**: Content still flows into scrollback correctly

---

## Implementation Notes

### Key Method Changes

```python
def _get_changed_lines(self, lines: list[str], previous: list[str],
                        term_height: int) -> list[int]:
    """Return indices of lines that changed."""
    changed = []

    # First frame - all lines are "changed"
    if not previous:
        return list(range(min(len(lines), term_height)))

    current_count = len(lines)
    previous_count = len(previous)

    # Content grew - only need to render visible portion
    if current_count > term_height:
        first_visible = current_count - term_height
        for screen_row in range(term_height):
            content_row = first_visible + screen_row
            if content_row >= current_count:
                break
            if content_row >= len(previous) or lines[content_row] != previous[content_row]:
                changed.append(screen_row)
    else:
        # Content fits in terminal
        for i, line in enumerate(lines):
            if i >= len(previous) or line != previous[i]:
                changed.append(i)

    return changed
```

### Modified render_frame()

```python
# Replace "render all if changed" with selective rendering
changed_indices = self._get_changed_lines(lines, self._previous_lines, term_height)

for screen_row in changed_indices:
    # Convert screen_row to content_row if scrolled
    if current_count > term_height:
        content_row = (current_count - term_height) + screen_row
    else:
        content_row = screen_row

    buffer += self._move_cursor_relative(screen_row)
    buffer += "\r\x1b[2K"
    buffer += lines[content_row]
```

---

## Risks

1. **Cursor position tracking** - Must maintain accurate `_hardware_cursor_row`
2. **Overlay compositing** - Changes in overlays must trigger line changes
3. **Edge cases** - Resize, first frame, empty content

## Mitigation

- Comprehensive unit tests for each edge case
- MockTerminal verification of actual output
- Manual testing with demo apps
