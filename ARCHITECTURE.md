# PyPiTUI Architecture Diagram

Based on source code analysis of `/workspace/pypitui/src/pypitui/`.

## 1. Component Hierarchy

```
Component (ABC)
├── render(width) -> list[str]  [REQUIRED]
├── handle_input(data)           [optional]
├── wants_key_release -> bool   [default: False]
└── is_transient -> bool        [default: False]

Container(Component)
├── children: list[Component]
├── add_child(component)
├── remove_child(component)
└── render_with_transient(width) -> (lines, transient_indices)

TUI(Container)  [main class]
├── terminal: Terminal
├── _overlay_stack: list[_OverlayEntry]
├── _previous_lines: list[str]        # Last rendered lines
├── _previous_transient_indices: set[int]
├── _previous_overlay_rows: set[int]
├── _total_lines_emitted: int         # Lines written via \r\n
├── _max_lines_rendered: int          # Total content lines ever
└── render_frame()                    # Main render method

Focusable(ABC)  [interface]
└── focused: bool                     # Cursor position marker
```

## 2. Data Flow - Rendering a Frame

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           render_frame() Flow                                │
└─────────────────────────────────────────────────────────────────────────────┘

[1] RENDER ALL COMPONENTS
    │
    ├─> Container.render_with_transient(width)
    │   ├─> For each child:
    │   │   ├─> child.render(width) -> child_lines
    │   │   └─> Track indices in transient_indices if child.is_transient
    │   └─> Returns: (base_lines, transient_indices)
    │
    ├─> _composite_overlays(base_lines, ...)
    │   ├─> result = list(base_lines)  [copy]
    │   ├─> For each overlay in _overlay_stack:
    │   │   └─> _composite_single_overlay(result, overlay)
    │   └─> Returns: (lines, current_overlay_rows)
    │
    └─> _apply_line_resets(lines)  [adds ANSI reset to each line]

[2] CALCULATE VISIBLE RANGE
    │
    ├─> current_count = len(lines)
    ├─> if current_count > term_height:
    │       first_visible = current_count - term_height
    │   else:
    │       first_visible = 0
    └─> use_scrollback = current_count > term_height

[3] WRITE NEW LINES TO SCROLLBACK (via \r\n)
    │
    ├─> IF use_scrollback:
    │   │
    │   ├─> Clear previous transient lines (to prevent ghosts)
    │   │   For each prev_transient_row:
    │   │       ├─> Move cursor to screen_row
    │   │       └─> Clear line (\x1b[2K)
    │   │
    │   ├─> emit_start = max(_total_lines_emitted, first_visible)
    │   │
    │   └─> FOR i FROM emit_start TO len(base_lines):
    │       │   IF i NOT in transient_indices:
    │       │       buffer += base_lines[i] + "\r\n"
    │       │       newly_emitted.add(i)
    │       └─> _total_lines_emitted = len(base_lines)
    │
    └─> ELSE (content fits on screen):
        └─> Skip \r\n writing - will render via absolute positioning

[4] UPDATE VISIBLE LINES (via absolute positioning)
    │
    └─> FOR screen_row IN 0..visible_rows:
        │
        ├─> content_row = first_visible + screen_row
        │
        ├─> IF content_row beyond current content:
        │   └─> Clear line (content shrank)
        │
        ├─> Check flags:
        │   ├─> is_transient = content_row in transient_indices
        │   ├─> is_overlay = content_row in all_overlay_rows
        │   ├─> is_new = content_row >= len(_previous_lines)
        │   ├─> is_changed = _previous_lines[content_row] != lines[content_row]
        │   └─> was_just_emitted = content_row in newly_emitted
        │
        ├─> SKIP IF: was_just_emitted AND NOT is_transient AND NOT is_overlay
        │   (Lines already written via \r\n are on screen, don't redraw)
        │
        ├─> DECIDE:
        │   │
        │   ├─> IF NOT use_scrollback (content fits):
        │   │   └─> needs_render = is_transient OR is_overlay OR is_new OR is_changed
        │   │       (Full differential rendering)
        │   │
        │   └─> IF use_scrollback (content exceeds):
        │       └─> needs_render = is_transient OR is_overlay
        │           (Only transients/overlays - regular content is in scrollback)
        │
        └─> IF needs_render:
            ├─> buffer += "\x1b[{screen_row + 1};1H"  [absolute position]
            ├─> buffer += "\x1b[2K"                    [clear line]
            └─> buffer += lines[content_row]           [write content]

[5] UPDATE STATE
    │
    ├─> _previous_lines = lines
    ├─> _previous_transient_indices = transient_indices
    ├─> _previous_overlay_rows = updated_overlay_rows
    └─> _max_lines_rendered = max(_max_lines_rendered, len(lines))
```

## 3. Key Concepts

### Content Lines vs Screen Rows

```
Virtual Content Buffer (grows forever):
┌────────────────┐  row 0  [in scrollback - not visible]
│ Box 1 Top      │
├────────────────┤  row 1
│ Box 1 Content  │
└────────────────┘  row 2
┌────────────────┐  row 3  [in scrollback - not visible]
│ Box 2 Top      │
├────────────────┤  row 4
│ Box 2 Content  │
└────────────────┘  row 5
┌────────────────┐  row 6  <-- first_visible (term_height = 4)
│ Box 3 Top      │         [visible on screen - row 0]
├────────────────┤  row 7  [visible on screen - row 1]
│ Box 3 Content  │
└────────────────┘  row 8  [visible on screen - row 2]
┌────────────────┐  row 9  [visible on screen - row 3]
│ Box 4 Top      │
└────────────────┘  row 10

current_count = 11
term_height = 4
first_visible = 11 - 4 = 6
```

### Writing to Scrollback vs Absolute Positioning

```
┌────────────────────────────────────────────────────────────────┐
│ METHOD 1: \r\n (for new content exceeding terminal height)      │
└────────────────────────────────────────────────────────────────┘

When: Content grows beyond terminal height
Effect: Terminal automatically scrolls up
Cursor: After \r\n, cursor is at start of NEXT line

Example (term_height = 3):
  Before:                    After writing "Line 3\r\n":
  ┌─────────┐                ┌─────────┐
  │ Line 0  │                │ Line 1  │  <- scrolled up
  │ Line 1  │                │ Line 2  │
  │ Line 2  │                │ Line 3  │  <- new content
  └─────────┘                └─────────┘
                                    ^
                                    Cursor here (start of row 3)

┌────────────────────────────────────────────────────────────────┐
│ METHOD 2: Absolute Positioning (for updates)                   │
└────────────────────────────────────────────────────────────────┘

When: Content changes, transients update, overlays change
Effect: Cursor moves to specific screen row, line is rewritten
Command: \x1b[{row};1H\x1b[2K{content}

Example:
  \x1b[2;1H    -> Move to screen row 2 (1-indexed)
  \x1b[2K      -> Clear entire line
  New Content  -> Write new content
```

### Transient Components

```
┌─────────────────────────────────────────────────────────────────┐
│ TRANSIENT LINES (is_transient = True)                           │
└─────────────────────────────────────────────────────────────────┘

Properties:
- NOT written to scrollback via \r\n
- Always rendered via absolute positioning
- Must be cleared before scroll (prevent ghosting)
- Examples: StatusLine, InputField

Lifecycle:
  Frame N:   Render at screen row 10
             ↓
  Frame N+1: Content grows, terminal scrolls up
             ↓
  [WITHOUT clearing]:
             Old transient would scroll up with content!
             
  [WITH clearing before \r\n]:
             Clear old position -> No ghost
```

## 4. State Tracking

```
TUI maintains several key state variables:

┌────────────────────────────────────────────────────────────────┐
│ _total_lines_emitted                                           │
├────────────────────────────────────────────────────────────────┤
│ Tracks how many lines have been written via \r\n.              │
│ Used to determine which lines are "new" in subsequent renders. │
│ Reset only on full redraw or terminal clear.                   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ _max_lines_rendered                                            │
├────────────────────────────────────────────────────────────────┤
│ Maximum content lines ever rendered.                           │
│ Used to calculate first_visible: max(0, max_lines - term_height)│
│ Never decreases (content buffer only grows).                   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ _previous_lines                                                │
├────────────────────────────────────────────────────────────────┤
│ Complete copy of lines from last render.                       │
│ Used for differential comparison (is_changed detection).       │
│ Includes overlays and ANSI resets.                             │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ _previous_transient_indices                                    │
├────────────────────────────────────────────────────────────────┤
│ Set of line indices that were transient in last render.        │
│ Used to clear old transient positions before scroll.           │
└────────────────────────────────────────────────────────────────┘
```

## 5. The Scrollback Problem

```
THE ISSUE: When content scrolls, visible lines shift.

Example:
  Frame 1:                          Frame 2 (new content added):
  ┌──────────────┐                  ┌──────────────┐
  │ Box 1        │                  │ Box 1        │ <- Now in scrollback
  │ Box 2        │   + Box 3   =>   │ Box 2        │ <- Now in scrollback
  │              │                  │ Box 3        │ <- Now visible (row 0)
  │              │                  │              │ <- Now visible (row 1)
  └──────────────┘                  └──────────────┘

Terminal Behavior:
- Writing "Box 3\r\n" when cursor is at bottom scrolls everything up
- Box 3 appears at bottom of screen
- Box 1 moves into scrollback history

Current Logic Problem:
- Frame 1 writes Box 1 and Box 2 via \r\n
- Frame 2 writes Box 3 via \r\n
- Terminal scrolls, showing Box 2 (partially) and Box 3
- BUT Box 2's top border might be cut off!
- And we don't re-render Box 2 because it wasn't "just emitted"

The Corruption:
- When a box is split across the scrollback/visible boundary
- Part of it is in scrollback (already written)
- Part of it is visible (needs rendering)
- But we only render transients/overlays, not regular content
```

## 6. Correct Approach (Per Your Guidance)

```
Based on your feedback, the correct approach is:

1. Write ALL content with \r\n (not just new lines)
   - Terminal handles scrolling naturally
   - No need to track "newly_emitted" for skipping

2. After \r\n writes, cursor is at bottom

3. Use relative positioning (CUU/CUD) to move to lines needing updates
   - Only for transients, overlays, and changed lines
   - Based on first_visible as anchor

4. Clear line + rewrite for those specific lines

This avoids the "partial box" problem because:
- Full content is written via \r\n every frame
- Terminal naturally scrolls to show the right content
- Only dynamic elements (transients/overlays) need absolute updates
```

## 7. File Structure

```
pypitui/
├── __init__.py          # Public exports
├── tui.py               # Core: Component, Container, TUI, Focusable
├── components.py        # Widgets: Text, BorderedBox, SelectList, Input
├── terminal.py          # Terminal abstraction + MockTerminal
├── keys.py              # Key handling and keycodes
├── rich_components.py   # Rich library integration (optional)
└── utils.py             # Text wrapping, width calculation, etc.
```
