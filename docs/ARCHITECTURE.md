# PyPiTUI Architecture

## Core Tenets

1. **Native scrollback** — Content flows into the terminal's normal scrollback buffer. No alternate screen buffer.
2. **Atomic rendering** — DEC 2026 synchronized updates ensure frames render atomically. No intermediate states are visible.
3. **Differential rendering** — Only changed lines redraw. Unchanged lines generate zero output.

## Rendering Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  Component Tree                                             │
│  ├── Container                                              │
│  │   ├── Text (static)                                      │
│  │   ├── Input (focusable)                                  │
│  │   └── SelectList (focusable)                             │
│  └── Overlay (composited last)                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layout Phase                                               │
│  - Components calculate their size requirements             │
│  - Parent containers distribute available space             │
│  - Each component receives final (x, y, width, height)      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Render Phase                                               │
│  - Each component renders to its allocated buffer slice     │
│  - Components return list of (line content, styles)         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Diff Phase                                                 │
│  - Compare new render against _previous_lines               │
│  - Identify which line numbers changed                      │
│  - Skip identical lines entirely                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Output Phase                                               │
│  - Send DEC 2026 sync start (CSI ? 2026 h)                  │
│  - For each changed line: move cursor, write line           │
│  - Send DEC 2026 sync end (CSI ? 2026 l)                    │
│  - Update _previous_lines for next diff                     │
└─────────────────────────────────────────────────────────────┘
```

## Component System

### Component Base Class

Components render independently given a width constraint:

```python
class Component(ABC):
    """Base class for all UI components."""

    @abstractmethod
    def measure(self, available_width: int, available_height: int) -> Size:
        """Return the component's desired size given available space."""
        # Height may be unbounded (available_height = -1)

    @abstractmethod  
    def render(self, width: int) -> list[str]:
        """Render component to lines at the given width.
        
        Must handle wrapping internally. Must not exceed width.
        """
```

**Key principle:** Each component is responsible for its own layout given a width constraint. Containers compose children vertically; complex layouts are built by nesting containers or creating custom components.

### Layout Model

**Simple vertical stacking** — No flexbox, no grids. Layout is:
1. Parent passes `width` to children
2. Children return how many lines they need
3. Parent stacks them vertically
4. Components handle their own internal layout

```python
class Container(Component):
    """Vertical stack."""
    
    def render(self, width: int) -> list[str]:
        lines: list[str] = []
        for child in self.children:
            child_lines = child.render(width)
            lines.extend(child_lines)
        return lines
```

**Custom layouts** — Create a component that positions children internally:

```python
class SidebarLayout(Component):
    """Two-column: sidebar left, main content right."""
    
    def render(self, width: int) -> list[str]:
        sidebar_width = min(30, width // 4)
        main_width = width - sidebar_width
        
        sidebar_lines = self.sidebar.render(sidebar_width)
        main_lines = self.main.render(main_width)
        
        # Interleave side-by-side
        lines = []
        for i in range(max(len(sidebar_lines), len(main_lines))):
            left = sidebar_lines[i] if i < len(sidebar_lines) else " " * sidebar_width
            right = main_lines[i] if i < len(main_lines) else ""
            lines.append(left + right)
        return lines
```

## Differential Rendering

Differential rendering reduces output volume by skipping unchanged lines. It works alongside DEC 2026—while sync codes ensure atomic frames, diffing ensures we don't write lines that haven't changed.

```python
class TUI:
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal
        self._previous_lines: dict[int, str] = {}  # row -> content hash
        self._root: Component | None = None

    def render_frame(self) -> None:
        """Render only what changed."""
        if not self._root:
            return

        lines = self._root.render()
        self._output_diff(lines)

    def _output_diff(self, lines: list[RenderedLine]) -> None:
        """Write only changed lines to the terminal."""
        self.terminal.write(DEC_2026_START)

        for row, line in enumerate(lines):
            content_hash = hash_line(line)
            if self._previous_lines.get(row) != content_hash:
                self.terminal.move_cursor(0, row)
                self.terminal.write(line.content)
                self._previous_lines[row] = content_hash

        # Clear any lines from previous render that no longer exist
        for old_row in list(self._previous_lines.keys()):
            if old_row >= len(lines):
                self.terminal.move_cursor(0, old_row)
                self.terminal.clear_line()
                del self._previous_lines[old_row]

        self.terminal.write(DEC_2026_END)
```

### Scrollback Editing

**Modifying content above the visible viewport triggers a full redraw.** Once content scrolls into the terminal's scrollback history, we cannot position the cursor to edit it—the only way to change scrollback content is to clear the screen and redraw everything.

```python
def _output_diff(self, lines: list[str]) -> None:
    # Find bounds of changes
    first_changed, last_changed = self._find_changed_bounds(lines)
    
    # If changes are above the visible viewport, full redraw
    viewport_top = max(0, len(self._previous_lines) - self.terminal.height)
    if first_changed < viewport_top:
        # Content in scrollback changed - cannot position cursor there
        # Must clear and redraw to update scrollback
        self._full_render(clear=True)
        return
    
    # Otherwise, render only changed lines efficiently
    self._render_changed_lines(first_changed, last_changed, lines)
```

| Change Location | Behavior | Renders |
|-----------------|----------|---------|
| Append at end | Optimized | Only new lines |
| Edit within viewport | Differential | Changed lines only |
| Edit in scrollback (above viewport) | **Full clear + redraw** | All lines |
| Shrink with `clear_on_shrink=True` | Full clear + redraw | All lines |
| Shrink with `clear_on_shrink=False` | Differential | Cleared lines only, viewport anchored |

**Why full redraw for scrollback edits?** Cursor positioning only works within the visible terminal area (terminal height). Content in scrollback history cannot be reached by cursor movement—the only mechanism to modify it is clearing the screen (`CSI 2J CSI 3J`) and redrawing all content, which updates both the visible area and the scrollback.

### Terminal Resize

**Full redraw on resize** — Terminal width/height changes trigger complete reflow:

```python
def on_resize(self, new_width: int, new_height: int) -> None:
    """Handle terminal resize."""
    self.terminal.width = new_width
    self.terminal.height = new_height
    
    # Invalidate all cached lines (full redraw required)
    self._previous_lines.clear()
    
    # Re-render everything; containers handle reflow
    self.render_frame()
```

**Reflow behavior**:
1. Container receives new width in `render(width)`
2. Container recalculates child layouts
3. Content reflows to fit new dimensions
4. Scroll position updates to new `viewport_top`

**Height changes**: Similar to width—content reflows, viewport adjusts. Height primarily affects which lines are visible and when scrollback behavior triggers.



## Static vs Fixed Elements

### Static Content (Cached Render)

"Static" means content doesn't change—useful for caching. But it still scrolls with the viewport:

```python
class Text(Component):
    """Immutable text block with cached render."""

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text
        self._cached: list[str] | None = None

    def render(self, width: int) -> list[str]:
        """Return cached lines (still scrolls with viewport)."""
        if self._cached is None:
            self._cached = self._text.split("\n")
        return self._cached
```

Static components avoid re-computing content, but they redraw when the viewport scrolls (because their screen position changes).

### Fixed Elements (Overlays)

"Fixed" means viewport-relative position—stays at same screen coordinates while content scrolls beneath. **Overlays are the only mechanism for fixed UI**:

```python
# Fixed header that stays at top while content scrolls
header = Overlay(
    Text("=== HEADER ==="),
    position=OverlayPosition(row=0, col=0, width=80)
)

# Fixed footer at bottom  
footer = Overlay(
    Input(),
    position=OverlayPosition(row=-1, anchor="bottom-center")
)
```

**Key distinction:**
| Type | Position | Scrolls | Mechanism |
|------|----------|---------|-----------|
| Static content | Content-relative | Yes | Component cache |
| Fixed element | Viewport-relative | No | Overlay |

## Overlay System

Overlays provide **viewport-relative positioning** for floating UI. They are **NOT Components**—they wrap Components and manage their own lifecycle separately.

```python
class Overlay:
    """Viewport-relative floating container. Wraps a Component."""
    def __init__(self, content: Component, position: OverlayPosition):
        self.content = Component       # The actual UI content
        self.position: OverlayPosition # Where to place it
        self.visible: bool = True
        self.z_index: int = 0
```

**Key distinction:**
| Aspect | Component | Overlay |
|--------|-----------|---------|
| Base class | `Component` | Separate wrapper class |
| Position | Content-relative (scrolls) | Viewport-relative (fixed) |
| Focus | In `_focus_order` | Separate focus management |
| Lifecycle | Permanent (in tree) | Temporary (modals, toasts) |
| Added via | `tui.add_child()` | `tui.show_overlay()` |

Overlays are composited into the line buffer after base content:

```python
def render_frame(self) -> None:
    """Render base content, composite overlays, then diff."""
    # 1. Render all base components (content may scroll)
    lines = self._root.render() if self._root else []
    
    # 2. Composite overlays at viewport-relative positions
    for overlay in self._overlays:
        if overlay.visible:
            self._composite_overlay(lines, overlay)
    
    # 3. Diff and output
    self._output_diff(lines)
```

### Overlay Positioning

Overlays support **absolute viewport positioning** with full layout control:

```python
@dataclass
class OverlayPosition:
    """Viewport-relative position."""
    row: int          # 0 = top, -1 = bottom (Python negative indexing)
    col: int = 0      # 0 = left edge
    width: int = -1   # -1 = auto-size to content
    height: int = -1  # -1 = auto-size to content
    
    # Anchor-based shortcuts
    anchor: Literal[
        "center", "top-left", "top-right",
        "bottom-left", "bottom-right",
        "top-center", "bottom-center",
        "left-center", "right-center"
    ] | None = None
```

**Negative indexing**: Like Python lists, negative coordinates count from the opposite edge:
- `row=-1` = bottom row of terminal
- `row=-2` = second from bottom
- `col=-1` = rightmost column

**Clipping**: Overlays extending past terminal bounds are clamped:
```python
def _resolve_position(pos: OverlayPosition, term_h: int, term_w: int):
    row = pos.row if pos.row >= 0 else term_h + pos.row + 1
    col = pos.col if pos.col >= 0 else term_w + pos.col + 1
    # Clamp to visible bounds
    return max(0, min(row, term_h - 1)), max(0, min(col, term_w - 1))
```

**Absolute positioning example** — Fixed header at top:

```python
header = Text("Status: Connected")
overlay = Overlay(
    content=header,
    position=OverlayPosition(row=0, col=0, width=80)
)
tui.show_overlay(overlay)
```

**Anchor-based positioning example** — Centered modal:

```python
modal = BorderedBox(title="Confirm")
modal.add_child(Text("Delete this file?"))

overlay = Overlay(
    content=modal,  # Component to render
    position=OverlayPosition(anchor="center")
)
tui.show_overlay(overlay)
```

### Static Elements via Overlays

**Overlays wrap Components to create fixed UI.** Since base Components scroll into native scrollback, "fixed" elements (headers, footers) are implemented as Overlays wrapping Components:

```python
class App:
    def __init__(self):
        self.tui = TUI(terminal)
        
        # Fixed header: Overlay wraps a Text Component
        self.header = Overlay(
            content=Text("My App v1.0"),  # Component
            position=OverlayPosition(row=0, anchor="top-center")
        )
        self.tui.show_overlay(self.header)
        
        # Fixed footer: Overlay wraps an Input Component
        self.footer = Overlay(
            content=Input(placeholder="Type command..."),  # Component
            position=OverlayPosition(row=-1, anchor="bottom-center")
        )
        self.tui.show_overlay(self.footer)
        
        # Scrollable content: Component added directly to TUI
        self.content = Container()  # Component
        self.tui.add_child(self.content)
```

The Overlay's `content` attribute holds the Component that renders the actual UI. The Overlay itself only manages position and visibility.

### Viewport-Relative Coordinate System

Overlays use **screen coordinates**, not content coordinates:

```
Screen Coordinates (viewport-relative):
┌─────────────────────────────┐  row=0
│  [Fixed Header Overlay]     │
├─────────────────────────────┤  row=1
│                             │
│  Scrollable content         │  ← moves into scrollback
│  (base components)          │
│                             │
├─────────────────────────────┤  row=22 (height-2)
│  [Fixed Footer Overlay]     │
└─────────────────────────────┘  row=23 (height-1)
```

When content scrolls:
- Base component lines shift up (into scrollback)
- Overlays stay at same screen row because they're composited after viewport calculation

### Overlay Compositing

Overlays are stamped into the line buffer at calculated screen positions:

```python
def _composite_overlay(
    self, 
    lines: list[str], 
    overlay: Overlay,
    viewport_top: int,
    term_height: int
) -> None:
    """Stamp overlay content at viewport-relative position."""
    # Resolve position (viewport-relative)
    row, col, width = self._resolve_position(
        overlay.position, 
        term_height, 
        term_width
    )
    
    # Render overlay at fixed width
    overlay_lines = overlay.render(width)
    
    # Clamp to terminal bounds
    for i, overlay_line in enumerate(overlay_lines):
        screen_row = row + i
        if 0 <= screen_row < term_height:
            # Calculate actual buffer index
            buffer_row = viewport_top + screen_row
            
            # Extend buffer if needed (content shorter than screen)
            while len(lines) <= buffer_row:
                lines.append("")
            
            # Composite overlay line into buffer
            lines[buffer_row] = self._composite_line(
                lines[buffer_row],  # base (possibly scrolled content)
                overlay_line,       # overlay
                col,
                width
            )
```

### Scrolling Behavior

**When content grows and scrolls:**

1. Base content renders longer line array
2. `viewport_top = max(0, content_height - term_height)` increases
3. Visible base content shifts (different lines now visible)
4. Overlays composite at same screen positions (fixed)
5. Diff engine sees ALL visible lines changed (viewport shifted)
6. Entire viewport redraws, but overlays stay fixed

**Yes** — pi-tui re-renders everything in the visible viewport upon scroll because the content shifted. But overlays are re-composited at fixed screen positions, so they appear static.

### Line Compositing

Merge overlay content into a base line, respecting wide characters:

```python
def _composite_line(
    self,
    base: str,
    overlay: str,
    col: int,
    width: int
) -> str:
    """Splice overlay content into base line at column."""
    # Slice base at overlay boundaries (respecting wide chars)
    # Wide chars (emoji, CJK) are treated as atomic units
    before = slice_by_width(base, 0, col)
    after = slice_by_width(base, col + width, wcswidth(base))
    
    # Pad/truncate overlay to declared width
    overlay_padded = pad_or_truncate(overlay, width)
    
    # Compose: base before + overlay + base after
    return before + overlay_padded + after
```

**Wide character handling**:
- `slice_by_width()` treats wide characters as atomic (never splits them)
- If overlay starts at a column occupied by a wide character, overlay shifts right
- Grapheme clusters (é = e + ◌́) are treated as single units

### Z-Order and Focus

Overlays composite in stacking order (last = on top):

```python
# Later overlays overwrite earlier ones
for overlay in sorted(self._overlays, key=lambda o: o.z_index):
    self._composite_overlay(lines, overlay)
```

Focus order is separate from visual order:
- `focus_order` determines tab cycling
- `z_index` determines visual layering

## Focus Management

Focus is managed as a **stack (LIFO)**. Components can be focusable; overlays push/pop focus automatically.

```python
class TUI:
    def __init__(self, terminal: Terminal) -> None:
        self._focus_stack: list[Component] = []  # Stack of focused components
        self._focus_order: list[Component] = []  # Tab order registration

    @property
    def _focused(self) -> Component | None:
        """Current focus is top of stack."""
        return self._focus_stack[-1] if self._focus_stack else None

    def push_focus(self, component: Component | None) -> None:
        """Push component onto focus stack."""
        if self._focused:
            self._focused.on_blur()
            self._focused.invalidate()

        self._focus_stack.append(component)
        
        if component:
            try:
                component.on_focus()
                component.invalidate()
            except Exception as e:
                # Pop on error, restore previous
                self._focus_stack.pop()
                if self._focused:
                    self._focused.on_focus()
                self._show_error_overlay(f"Focus error: {e}")

    def pop_focus(self) -> Component | None:
        """Pop current focus, restore previous. Returns popped component."""
        if not self._focus_stack:
            return None
            
        old = self._focus_stack.pop()
        if old:
            old.on_blur()
            old.invalidate()
        
        if self._focused:
            self._focused.on_focus()
            self._focused.invalidate()
        
        return old

    def set_focus(self, component: Component | None) -> None:
        """Replace current focus (pop then push)."""
        self.pop_focus()
        self.push_focus(component)
```

### Tab Order

Components register for Tab cycling within their context:

```python
class TUI:
    def register_focusable(self, component: Component) -> None:
        """Register for Tab cycling."""
        if component not in self._focus_order:
            self._focus_order.append(component)

    def cycle_focus(self, direction: int = 1) -> None:
        """Tab to next in current context."""
        if not self._focus_order or not self._focused:
            return
        
        current_idx = self._focus_order.index(self._focused)
        next_idx = (current_idx + direction) % len(self._focus_order)
        self.set_focus(self._focus_order[next_idx])
```

### Overlays and Focus Stack

Overlays push their content onto the focus stack when opened:

```python
def show_overlay(self, overlay: Overlay) -> None:
    """Show overlay and push its content onto focus stack."""
    self._overlays.append(overlay)
    if overlay.content:
        self.push_focus(overlay.content)

def close_overlay(self, overlay: Overlay) -> None:
    """Close overlay and pop its focus."""
    self._overlays.remove(overlay)
    # Pop if this overlay's content is current focus
    if self._focused is overlay.content:
        self.pop_focus()
```

**Nested overlays work naturally:**
```python
tui.set_focus(input_field)      # Stack: [input_field]
tui.show_overlay(modal)         # Stack: [input_field, modal_input]
tui.show_overlay(confirm_box)   # Stack: [input_field, modal_input, confirm_btn]
tui.close_overlay(confirm_box)  # Stack: [input_field, modal_input]
tui.close_overlay(modal)        # Stack: [input_field]
```

### Component API

```python
class Input(Component):
    def __init__(self, tui: TUI):
        super().__init__()
        tui.register_focusable(self)  # For Tab cycling

    def on_focus(self) -> None:
        self.focused = True

    def on_blur(self) -> None:
        self.focused = False

    def handle_input(self, data: bytes) -> None:
        if is_click(data):
            tui.push_focus(self)  # Push onto stack
```

## Flicker Reduction

Flicker happens when the user sees intermediate states. We eliminate it through:

1. **DEC 2026 synchronized updates** — Atomic frame rendering; the terminal buffers all output and displays it as one frame
2. **Line-level diffing** — Only changed lines redraw; stable content never updates
3. **Complete frame construction** — Build the entire frame (including overlays) before any output

### DEC 2026 Synchronized Updates

DEC 2026 (synchronized output) is the primary flicker-reduction mechanism:

```python
# Enable synchronized output
DEC_2026_START = "\x1b[?2026h"

# Disable synchronized output  
DEC_2026_END = "\x1b[?2026l"
```

Terminals that support this (kitty, iTerm2, Windows Terminal, alacritty, wezterm) buffer all output between start/end and render it as one atomic frame. The user never sees cursor movement, partial writes, or intermediate states.

**Critical:** All cursor movement and content writes must happen between these markers. Never write outside the sync block.

**Feature Detection** — Query terminal support:
```python
# Query: CSI ? 2026 $ p
dec_2026_query = "\x1b[?2026$p"

# Response if supported: CSI ? 2026 ; 1 $ y
dec_2026_supported = "\x1b[?2026;1$y"

# Response if not supported: CSI ? 2026 ; 2 $ y  
dec_2026_not_supported = "\x1b[?2026;2$y"
```

**Graceful degradation**: If DEC 2026 not supported, TUI renders without sync codes. May show flicker on complex updates. Terminal support assumed on modern terminals; query for certainty.

### Frame Construction

Build the complete frame before output:

```python
def render_frame(self) -> None:
    """Render main content and overlays atomically."""
    # Build complete frame buffer first
    lines = self._root.render() if self._root else []
    
    # Composite overlays into the same buffer
    for overlay in self._overlays:
        if overlay.visible:
            self._composite_overlay(lines, overlay)
    
    # Single atomic output
    self._output_frame(lines)
```

### Output Phase

Write the entire frame inside the sync block:

```python
def _output_frame(self, lines: list[RenderedLine]) -> None:
    """Output complete frame atomically."""
    self.terminal.write(DEC_2026_START)
    
    for row, line in enumerate(lines):
        self.terminal.move_cursor(0, row)
        self.terminal.write(line.content)
    
    self.terminal.write(DEC_2026_END)
```

Within the sync block, cursor movement patterns and multiple writes do not matter—the terminal only renders the final state.

### Cursor Management

Hide the cursor before the sync block, position it after:

```python
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"

def render_frame(self) -> None:
    """Render with cursor hidden during update."""
    lines = self._build_frame()
    
    self.terminal.write(HIDE_CURSOR)
    self.terminal.write(DEC_2026_START)
    
    for row, line in enumerate(lines):
        self.terminal.move_cursor(0, row)
        self.terminal.write(line.content)
    
    self.terminal.write(DEC_2026_END)
    
    # Position cursor for user input
    if self._focused:
        pos = self._focused.get_cursor_position()
        self.terminal.move_cursor(pos.col, pos.row)
    
    self.terminal.write(SHOW_CURSOR)
```

This prevents the cursor from appearing at random positions during the frame update.

## Component Invalidation

When a component changes, invalidate only its lines:

```python
def invalidate_component(self, component: Component) -> None:
    """Clear a component's lines from the cache."""
    rect = component._rect
    for row in range(rect.y, rect.y + rect.height):
        self._previous_lines.pop(row, None)
```

This forces those lines to redraw on the next frame while unchanged lines remain cached.

## Public API

### Creating Components

Users subclass `Component` and implement `measure()` and `render()`:

```python
class MyComponent(Component):
    def measure(self, width: int, height: int) -> Size:
        return Size(min(20, width), 1)

    def render(self) -> list[RenderedLine]:
        return [RenderedLine("Hello", width=5)]
```

### Composing the UI

```python
tui = TUI(terminal)
container = Container()
tui.add_child(container)

container.add_child(Text("Header"))
container.add_child(MyComponent())
```

### Handling Input

```python
def handle_input(self, data: bytes) -> None:
    if matches_key(data, Key.TAB):
        self.tui.cycle_focus()
    elif self.tui._focused:
        self.tui._focused.handle_input(data)
```

## Implementation Requirements

### Input Handling

**Kitty Keyboard Protocol** — Full support for progressive enhancement:
```python
# Enable: CSI > 1 u
# Full mode: CSI > 3 u
KITTY_ENABLE = "\x1b[>1u"
KITTY_FULL = "\x1b[>3u"
```
- Key release events
- Modifier key state
- Unicode key input

**Partial Escape Sequence Buffering** — Handle incomplete sequences with timeout:
```python
def _read_input(self) -> bytes:
    """Read input with timeout for partial sequences."""
    data = os.read(self.fd, 1024)
    
    # Buffer incomplete escape sequences
    if data.startswith(b'\x1b') and not self._is_complete_sequence(data):
        # Wait up to 50ms for rest of sequence
        time.sleep(0.05)
        more = os.read(self.fd, 1024)
        data += more
    
    return data
```

**Mouse Support** — Both focus and selection:
- Click to focus components
- Click to select items in SelectList
- Mouse events via `CSI ? 1006 h` (SGR extended coordinates)

**Async Input** — Separate thread for non-blocking reads:
```python
class Terminal:
    def start(self, on_input: Callable[[bytes], None]) -> None:
        """Start input thread."""
        self._input_thread = threading.Thread(target=self._read_loop)
        
    def _read_loop(self) -> None:
        while self._running:
            data = self._read_with_timeout()
            if data:
                self._on_input(data)
```

### Text and Unicode

**Wide Character Handling** — Critical for emoji and CJK:
```python
from wcwidth import wcswidth, wcwidth

def visible_width(text: str) -> int:
    """Return display width accounting for wide chars."""
    return wcswidth(text)

def truncate_to_width(text: str, width: int) -> str:
    """Truncate at column boundary without breaking sequences."""
    # Handle emoji, wide chars, combining marks
```

**Line Overflow** — Crash on overflow:
```python
def _output_line(self, line: str, row: int) -> None:
    if visible_width(line) > self.terminal.width:
        raise LineOverflowError(
            f"Line {row} exceeds terminal width: "
            f"{visible_width(line)} > {self.terminal.width}\n"
            f"Content: {line!r}"
        )
```

### Colors and Styles

**Truecolor (RGB)** — Primary support:
```python
# Foreground: CSI 38 ; 2 ; r ; g ; b m
# Background: CSI 48 ; 2 ; r ; g ; b m
TRUECOLOR_FG = "\x1b[38;2;{};{};{}m"
TRUECOLOR_BG = "\x1b[48;2;{};{};{}m"
```

**Color Capability Detection** — Auto-detect with environment overrides:

```python
def detect_color_support() -> int:
    """Return color level: 0=none, 1=16, 2=256, 3=truecolor."""
    # Explicit user override takes precedence
    if os.environ.get("PYPITUI_COLOR"):
        return int(os.environ["PYPITUI_COLOR"])
    
    # Respect NO_COLOR (any value disables colors)
    if os.environ.get("NO_COLOR"):
        return 0
    
    # FORCE_COLOR overrides detection
    force = os.environ.get("FORCE_COLOR")
    if force is not None:
        return min(int(force), 3)
    
    # Auto-detection via environment variables
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        return 3
    
    term = os.environ.get("TERM", "").lower()
    if "256color" in term:
        return 2
    if "color" in term or "ansi" in term:
        return 1
    
    # Default to truecolor (assume modern terminal)
    return 3
```

| Variable | Effect |
|----------|--------|
| `NO_COLOR` | Disable all colors (any value) |
| `FORCE_COLOR=0/1/2/3` | Force color level |
| `PYPITUI_COLOR=0/1/2/3` | PyPiTUI-specific override |
| `COLORTERM=truecolor/24bit` | Auto-detect truecolor |
| `TERM=*256color*` | Auto-detect 256 color |
| `TERM=*color*` or `*ansi*` | Auto-detect 16 color |

### Images

**Kitty Graphics Protocol** — Inline image display with fallback:

```python
class ImageComponent(Component):
    def __init__(self, image_path: str) -> None:
        self.image_path = image_path
        self._supports_graphics: bool | None = None
    
    def render(self, width: int) -> list[str]:
        # Check support (cached after first query)
        if self._supports_graphics is None:
            self._supports_graphics = self._detect_graphics_support()
        
        if self._supports_graphics:
            return self._render_kitty_graphics(width)
        else:
            return self._render_placeholder(width)
    
    def _render_placeholder(self, width: int) -> list[str]:
        """Fallback when graphics not supported."""
        filename = Path(self.image_path).name
        return [
            "┌" + "─" * (width - 2) + "┐",
            "│  [Image]" + " " * (width - 12) + "│",
            f"│  {filename[:width-6]:<{width-4}}│",
            "└" + "─" * (width - 2) + "┘",
        ]
```

**Graphics Detection** — Query terminal support:
```python
def _detect_graphics_support(self) -> bool:
    """Send Kitty graphics query and await response."""
    # Query: CSI_Gi=31,s=1,v=1,a=q;AAAA\x1b\\
    # Response indicates support level
    # For now, assume supported; implement query later
    return True
```

**Fallback behavior**: When Kitty graphics not supported, render ASCII box with filename.

### Debug Mode

Two separate debug mechanisms controlled by different environment variables:

**`PYPITUI_DEBUG`** — Raw escape sequence logging:
```python
if os.environ.get("PYPITUI_DEBUG"):
    debug_dir = Path("/tmp/pypitui")
    debug_dir.mkdir(exist_ok=True)
    
    # Log every render frame with raw output
    log_path = debug_dir / f"render-{timestamp}-{uuid}.log"
    log_data = {
        "first_changed": first_changed,
        "viewport_top": viewport_top,
        "cursor_row": cursor_row,
        "new_lines": new_lines,
        "previous_lines": previous_lines,
        "output_buffer": buffer,  # Raw escape sequences
    }
```

**`PYPITUI_LOG`** — Application logging (Python stdlib):
```python
import logging

logger = logging.getLogger("pypitui")

# In TUI operations
logger.debug("Rendering frame with %d lines", len(lines))
logger.info("Focus changed to %s", component)
logger.error("Component render failed: %s", e)
```

Log rotation: 100MB per file, keeps 3 backups.

**PII Stripping** — Logs sanitize sensitive data:
```python
SENSITIVE_PATTERNS = [
    (r'password[=:]\S+', 'password=***'),
    (r'token[=:]\S+', 'token=***'),
    # Add more as discovered
]
```

| Variable | Effect |
|----------|--------|
| `PYPITUI_DEBUG=1` | Raw render frames to `/tmp/pypitui/`, re-raise exceptions |
| `PYPITUI_LOG=debug` | Application logs to stderr |
| `PYPITUI_LOG=/path/to/file` | Application logs to file |

### Error Handling

TUI catches errors and displays them to users via error overlays:

```python
def do_render(self) -> None:
    try:
        lines = self._root.render()
    except Exception as e:
        # Show error overlay instead of crashing
        self._show_error_overlay(f"Render error: {e}")
        if os.environ.get("PYPITUI_DEBUG"):
            raise  # Re-raise in debug mode for stack traces
```

**Error Overlay** — Displays error message without crashing:
```python
def _show_error_overlay(self, message: str) -> None:
    error_overlay = Overlay(
        BorderedBox(
            title="Error",
            children=[Text(message)]
        ),
        position=OverlayPosition(anchor="center")
    )
    self.show_overlay(error_overlay)
```

**Terminal write failures** — Unrecoverable, cleanup and exit:
```python
def _write_output(self, data: str) -> None:
    try:
        self.terminal.write(data)
    except (IOError, OSError) as e:
        self.stop()  # Restore terminal state
        sys.exit(f"Terminal write failed: {e}")
```

**Input callback errors** — Show overlay, continue running:
```python
def _handle_input(self, data: bytes) -> None:
    try:
        self._focused.handle_input(data)
    except Exception as e:
        self._show_error_overlay(f"Input error: {e}")
        if os.environ.get("PYPITUI_DEBUG"):
            raise
```

Debug mode (`PYPITUI_DEBUG=1`) re-raises exceptions for development.

### Hardware Cursor / IME Support

**Cursor Position API** — Components report cursor position for IME support:

```python
class Input(Component, Focusable):
    def get_cursor_position(self) -> tuple[int, int] | None:
        """Return (row, col) relative to component origin, or None if not focused."""
        if not self.focused:
            return None
        
        # Calculate position within component
        row = self.cursor_line  # Line number within rendered content
        col = wcswidth(self.content[:self.cursor_pos])
        return (row, col)
```

TUI queries focused component and translates to screen coordinates:

```python
def render_frame(self) -> None:
    # ... render frame ...
    
    # Position hardware cursor for IME
    if self._focused:
        rel_pos = self._focused.get_cursor_position()
        if rel_pos:
            screen_row = component_screen_y + rel_pos[0]
            screen_col = component_screen_x + rel_pos[1]
            self.terminal.move_cursor(screen_col, screen_row)
    
    self.terminal.write(SHOW_CURSOR)
```

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
│   ├── overlay.py       # Floating overlays
│   └── image.py         # Kitty graphics
├── terminal.py          # Terminal I/O abstraction
├── keys.py              # Key parsing (Kitty protocol)
├── mouse.py             # Mouse event parsing
├── styles.py            # Color and style codes
└── utils.py             # wcwidth, truncation helpers
```

## Resolved Edge Cases

### Terminal Resize
- **Behavior**: Full redraw on resize
- **Reflow**: Container recalculates layouts with new width
- **Scroll position**: Updates to new `viewport_top`

### Wide Characters
- **Slicing**: `slice_by_width()` treats wide chars as atomic units
- **Overlay collision**: Overlay shifts right if it would split a wide char
- **Grapheme clusters**: Treated as single units (é = e + ◌́)

### Overlay Positioning
- **Negative indexing**: `row=-1` means bottom (Python-style)
- **Clipping**: Overlays clamped to terminal bounds
- **Z-order**: Higher `z_index` renders on top
- **Overlap**: Latest overlay in list wins on same z-index

### Scrollback "Thrashing"
- **Rapid append-then-edit**: Triggers full redraw each time
- **Acceptable cost**: Not optimized; correct behavior preferred

### Focus Management
- **Stack (LIFO)**: `_focus_stack` holds focus history
- **Current**: Top of stack (or None if empty)
- **Operations**: `push_focus()`, `pop_focus()`, `set_focus()` (pop+push)
- **Tab order**: `register_focusable()` for Tab cycling within context
- **Error in `on_focus()`**: Pop and restore previous, show error overlay
- **Overlay opens**: Pushes overlay content onto stack
- **Overlay closes**: Pops focus (if overlay content is current)
- **Nested overlays**: Work naturally via stack
- **No focus**: Empty stack, keyboard input dropped

### Color Detection
- **Algorithm**: `COLORTERM` → `TERM` → default truecolor
- **Overrides**: `NO_COLOR`, `FORCE_COLOR`, `PYPITUI_COLOR`
- **Respect standards**: Follows de facto terminal conventions

### Image Fallback
- **Unsupported terminals**: Render ASCII box with filename
- **Detection**: Kitty graphics query (assumed supported initially)

### Error Handling
- **Component render errors**: Error overlay displayed
- **Terminal write errors**: Cleanup and exit
- **Input callback errors**: Error overlay, continue running
- **Debug mode**: Re-raises exceptions for stack traces

### DEC 2026 Detection
- **Query**: `CSI ? 2026 $ p`
- **Fallback**: Graceful degradation (no sync codes)
- **Assumption**: Modern terminals support it
