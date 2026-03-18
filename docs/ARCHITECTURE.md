# PyPiTUI Architecture

## Core Tenets

1. **Native scrollback** — Content flows into the terminal's normal scrollback buffer. No alternate screen buffer.
2. **Atomic rendering** — DEC 2026 synchronized updates ensure frames render atomically. No intermediate states are visible.
3. **Differential rendering** — Only changed lines redraw. Unchanged lines generate zero output.
4. **Any scrollback change triggers full redraw** — Terminal scrollback is immutable; cursor positioning cannot reach scrolled-off content.

## Terminal I/O Architecture

**Async User Input** — Keyboard and mouse events are handled asynchronously via a dedicated input thread:
- Thread spawned on `Terminal.start(on_input_callback)`
- Blocking reads with timeout for escape sequence completion
- Callback dispatch to main thread
- Graceful shutdown via `Terminal.stop()`

**Sync Feature Queries** — Terminal capability detection (DEC 2026, Kitty graphics) uses synchronous request/response during initialization before the async input thread starts. This avoids complexity correlating async responses with requests.

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
│  - TUI sets component._rect with absolute position          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Composite Phase                                            │
│  - Overlays stamped into buffer at viewport-relative coords │
│  - Z-index ordering (ascending)                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Diff Phase                                                 │
│  - Compare new render against _previous_lines               │
│  - Identify which line numbers changed                      │
│  - Scrollback edit detection (first_changed < viewport_top) │
│  - Skip identical lines entirely                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Output Phase                                               │
│  - Send DEC 2026 sync start (CSI ? 2026 h)                  │
│  - For each changed line: move cursor, write line           │
│  - Hardware cursor position tracked per write               │
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

**Component Position Tracking:** The TUI sets `component._rect: Rect` during render with absolute screen coordinates. This enables targeted invalidation and cursor position calculations.

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

### Component Caching (Post-MVP)

**Current (MVP):** No component-level render caching. TUI-level diff caching (`_previous_lines`) is sufficient.

**Future:** Intelligent component caching where expensive operations (text wrapping) are cached and automatically invalidated when:
- Terminal width changes
- Component properties change
- Parent layout changes

**Challenge:** Manual `invalidate()` calls are error-prone. Need automatic cache invalidation mechanism.

## Differential Rendering

Differential rendering reduces output volume by skipping unchanged lines. It works alongside DEC 2026—while sync codes ensure atomic frames, diffing ensures we don't write lines that haven't changed.

```python
class TUI:
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal
        self._previous_lines: dict[int, str] = {}  # row -> content hash
        self._root: Component | None = None
        self._viewport_top: int = 0

    def render_frame(self) -> None:
        """Render only what changed."""
        if not self._root:
            return

        lines = self._root.render(self.terminal.width)
        self._output_diff(lines)

    def _output_diff(self, lines: list[RenderedLine]) -> None:
        """Write only changed lines to the terminal."""
        first_changed, last_changed = self._find_changed_bounds(lines)
        
        # CRITICAL: Any change in scrollback requires full redraw
        if first_changed < self._viewport_top:
            self._full_render(clear=True)
            return
        
        self.terminal.write(DEC_2026_START)

        for row in range(first_changed, last_changed + 1):
            content_hash = hash_line(lines[row])
            if self._previous_lines.get(row) != content_hash:
                self.terminal.move_cursor(0, row - self._viewport_top)
                self.terminal.write(lines[row].content)
                self._previous_lines[row] = content_hash

        self.terminal.write(DEC_2026_END)
```

### Scrollback Edit Detection (CRITICAL)

**Any change in scrollback triggers full clear+redraw.** Once content scrolls into the terminal's history buffer, it cannot be edited—cursor positioning only works within the visible viewport.

```python
def _is_scrollback_edit(self, first_changed: int) -> bool:
    """Return True if edit is in scrollback (above visible viewport)."""
    return first_changed < self._viewport_top
```

| Change Location | Behavior | Renders |
|-----------------|----------|---------|
| Append at end | Optimized | Only new lines |
| Edit within viewport | Differential | Changed lines only |
| **Edit in scrollback** | **Full clear + redraw** | All lines |
| Shrink with `clear_on_shrink=True` | Full clear + redraw | All lines |
| Shrink with `clear_on_shrink=False` | Differential | Cleared lines only, viewport anchored |

**Why full redraw for scrollback edits?** Cursor positioning only works within the visible terminal area (terminal height). Content in scrollback history cannot be reached by cursor movement—the only mechanism to modify it is clearing the screen (`CSI 2J CSI 3J`) and redrawing all content, which updates both the visible area and the scrollback.

**Design guidance:** Avoid UIs that edit scrollback. Use append-only patterns for logs, overlays for editable history.

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

## Hardware Cursor Management

The TUI tracks hardware cursor position for efficient diff output and IME positioning:

```python
class TUI:
    def __init__(self, terminal: Terminal) -> None:
        self._hardware_cursor_row: int = 0
        self._hardware_cursor_col: int = 0
        
    def _output_line(self, line: str, screen_row: int) -> None:
        """Output line with cursor tracking."""
        # Calculate optimal cursor movement
        row_diff = screen_row - self._hardware_cursor_row
        if row_diff > 0:
            self.terminal.write(f"\x1b[{row_diff}B")  # Move down
        elif row_diff < 0:
            self.terminal.write(f"\x1b[{-row_diff}A")  # Move up
            
        self.terminal.write("\r")  # Carriage return
        self.terminal.write(line)
        
        # Update tracking
        self._hardware_cursor_row = screen_row
        self._hardware_cursor_col = len(line)
        
    def render_frame(self) -> None:
        """Render with cursor tracking reset."""
        # Reset cursor tracking before diff output
        self._hardware_cursor_row = 0
        self._hardware_cursor_col = 0
        
        lines = self._build_frame()
        self._output_diff(lines)
        
        # Position cursor for IME if focused
        if self._focused:
            screen_pos = self._calculate_screen_position(self._focused)
            self.terminal.move_cursor(screen_pos.col, screen_pos.row)
```

**Cursor tracking phases:**
1. **Render start**: Reset to (0, 0)
2. **Diff output**: Track after each line written
3. **IME positioning**: Calculate absolute screen position for focused component

**Overlay focus positioning:** For components inside overlays, calculate absolute screen coordinates:
```python
def _calculate_screen_position(self, component: Component) -> Position:
    if self._is_in_overlay(component):
        overlay = self._find_overlay_for(component)
        abs_pos = self._resolve_position(overlay.position)
        rel_pos = component.get_cursor_position()
        return Position(
            row=abs_pos.row + rel_pos.row,
            col=abs_pos.col + rel_pos.col
        )
    else:
        # Regular component — content-relative
        rel_pos = component.get_cursor_position()
        return Position(
            row=component._rect.y + rel_pos.row - self._viewport_top,
            col=component._rect.x + rel_pos.col
        )
```

## Static vs Fixed Elements

### Static Content

"Static" means content doesn't change. In MVP there is no component-level caching—TUI diff caching handles unchanged lines.

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
| Static content | Content-relative | Yes | TUI diff cache |
| Fixed element | Viewport-relative | No | Overlay |

## Overlay System

Overlays provide **viewport-relative positioning** for floating UI. They are **NOT Components**—they wrap Components and manage their own lifecycle separately.

```python
class Overlay:
    """Viewport-relative floating container. Wraps a Component."""
    def __init__(self, content: Component, position: OverlayPosition):
        self.content: Component = content  # The actual UI content
        self.position: OverlayPosition = position
        self.visible: bool = True
        self.z_index: int = 0
```

**Key distinction:**
| Aspect | Component | Overlay |
|--------|-----------|---------|
| Base class | `Component` | Separate wrapper class |
| Position | Content-relative (scrolls) | Viewport-relative (fixed) |
| Focus | In `_focus_order` | Pushes `content` (Component) to focus stack |
| Lifecycle | Permanent (in tree) | Temporary (modals, toasts) |
| Added via | `tui.add_child()` | `tui.show_overlay()` |

Overlays are composited into the line buffer after base content:

```python
def render_frame(self) -> None:
    """Render base content, composite overlays, then diff."""
    # 1. Render all base components (content may scroll)
    lines = self._root.render(self.terminal.width) if self._root else []
    
    # 2. Composite overlays at viewport-relative positions
    for overlay in sorted(self._overlays, key=lambda o: o.z_index):
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
    return max(0, min(row, term_h - 1)), max(0, min(col, term_w - 1))
```

### Static Elements via Overlays

**Overlays wrap Components to create fixed UI.** Since base Components scroll into native scrollback, "fixed" elements (headers, footers) are implemented as Overlays wrapping Components:

```python
class App:
    def __init__(self):
        self.tui = TUI(terminal)
        
        # Fixed header: Overlay wraps a Text Component
        self.header = Overlay(
            content=Text("My App v1.0"),
            position=OverlayPosition(row=0, anchor="top-center")
        )
        self.tui.show_overlay(self.header)
        
        # Fixed footer: Overlay wraps an Input Component  
        self.footer = Overlay(
            content=Input(placeholder="Type command..."),
            position=OverlayPosition(row=-1, anchor="bottom-center")
        )
        self.tui.show_overlay(self.footer)
        
        # Scrollable content: Component added directly to TUI
        self.content = Container()
        self.tui.add_child(self.content)
```

### Overlay Compositing

Overlays are stamped into the line buffer at calculated screen positions:

```python
def _composite_overlay(
    self, 
    lines: list[RenderedLine], 
    overlay: Overlay,
    viewport_top: int
) -> None:
    """Stamp overlay content at viewport-relative position."""
    row, col, width, height = self._resolve_position(
        overlay.position, self.terminal.height, self.terminal.width
    )
    
    overlay_lines = overlay.content.render(width)
    
    for i, overlay_line in enumerate(overlay_lines[:height]):
        screen_row = row + i
        if 0 <= screen_row < self.terminal.height:
            buffer_row = viewport_top + screen_row
            while len(lines) <= buffer_row:
                lines.append(RenderedLine(""))
            
            lines[buffer_row] = self._composite_line(
                lines[buffer_row], overlay_line, col, width
            )
```

### Line Compositing

Merge overlay content into a base line, respecting wide characters:

```python
def _composite_line(
    self,
    base: RenderedLine,
    overlay: RenderedLine,
    col: int,
    width: int
) -> RenderedLine:
    """Splice overlay content into base line at column."""
    before = slice_by_width(base.content, 0, col)
    after = slice_by_width(base.content, col + width, wcswidth(base.content))
    overlay_padded = pad_or_truncate(overlay.content, width)
    
    return RenderedLine(
        content=before + overlay_padded + after,
        styles=merge_styles(base.styles, overlay.styles, col)
    )
```

**Wide character handling**:
- `slice_by_width()` treats wide characters as atomic (never splits them)
- If overlay starts at a column occupied by a wide character, overlay shifts right

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
                self._focus_stack.pop()
                if self._focused:
                    self._focused.on_focus()
                self._show_error_overlay(f"Focus error: {e}")

    def pop_focus(self) -> Component | None:
        """Pop current focus, restore previous."""
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

**Critical:** Overlays push their `content` (a Component) onto the focus stack, not the Overlay itself. This maintains type consistency—focus stack always contains Components.

```python
def show_overlay(self, overlay: Overlay) -> None:
    """Show overlay and push its content onto focus stack."""
    self._overlays.append(overlay)
    if overlay.content:
        self.push_focus(overlay.content)  # Push Component, not Overlay

def close_overlay(self, overlay: Overlay) -> None:
    """Close overlay and pop its focus if content is current."""
    self._overlays.remove(overlay)
    # Compare against Component (overlay.content), not Overlay
    if self._focused is overlay.content:
        self.pop_focus()
```

**Nested overlays:**
```python
tui.set_focus(input_field)      # Stack: [input_field]
tui.show_overlay(modal)         # Stack: [input_field, modal_input]
tui.show_overlay(confirm_box)   # Stack: [input_field, modal_input, confirm_btn]
tui.close_overlay(confirm_box)  # Stack: [input_field, modal_input]
tui.close_overlay(modal)        # Stack: [input_field]
```

### Focusable Protocol

```python
class Focusable(Protocol):
    def on_focus(self) -> None: ...
    def on_blur(self) -> None: ...
    def handle_input(self, data: bytes) -> bool: ...  # Returns True if consumed
    def get_cursor_position(self) -> tuple[int, int] | None: ...
```

**Input consumption:** `handle_input()` returns `bool`:
- `True` = input was consumed, stop propagation
- `False` = input not handled, bubble to parent/container

## Flicker Reduction

1. **DEC 2026 synchronized updates** — Atomic frame rendering
2. **Line-level diffing** — Only changed lines redraw
3. **Complete frame construction** — Build entire frame before output
4. **Hardware cursor hidden during update** — Prevent cursor jumping

### DEC 2026 Synchronized Updates

```python
DEC_2026_START = "\x1b[?2026h"
DEC_2026_END = "\x1b[?2026l"
```

**MVP:** Assume DEC 2026 support on modern terminals. Always emit sync codes.

**Post-MVP:** Feature detection via `CSI ? 2026 $ p` query during initialization (before async input thread starts).

### Frame Construction

```python
def render_frame(self) -> None:
    """Render with cursor hidden during update."""
    lines = self._build_frame()
    
    self.terminal.write(HIDE_CURSOR)
    self.terminal.write(DEC_2026_START)
    
    self._hardware_cursor_row = 0  # Reset tracking
    self._hardware_cursor_col = 0
    self._output_diff(lines)
    
    self.terminal.write(DEC_2026_END)
    
    if self._focused:
        pos = self._calculate_screen_position(self._focused)
        self.terminal.move_cursor(pos.col, pos.row)
    
    self.terminal.write(SHOW_CURSOR)
```

## Component Invalidation

When a component changes, invalidate only its lines:

```python
def invalidate_component(self, component: Component) -> None:
    """Clear a component's lines from the cache."""
    rect = component._rect
    for row in range(rect.y, rect.y + rect.height):
        self._previous_lines.pop(row, None)
    component._rect = Rect(0, 0, 0, 0)  # Clear position
```

## Public API

### Complete Export List

```python
# Core
from pypitui import TUI, Component, Size, RenderedLine, Rect

# Components
from pypitui import Container, Text, Input, SelectList, SelectItem, BorderedBox

# Overlays
from pypitui import Overlay, OverlayPosition

# Input
from pypitui import Key, matches_key, parse_key, MouseEvent, parse_mouse

# Focus
from pypitui import Focusable

# Errors
from pypitui import LineOverflowError

# Styles
from pypitui import StyleSpan, detect_color_support

# Utils
from pypitui import truncate_to_width, slice_by_width, wcwidth
```

## Implementation Requirements

### Input Handling

**Async Thread Model:**
```python
class Terminal:
    def start(self, on_input: Callable[[bytes], None]) -> None:
        """Start async input thread."""
        self._on_input = on_input
        self._running = True
        self._input_thread = threading.Thread(target=self._read_loop)
        self._input_thread.start()
        
    def _read_loop(self) -> None:
        while self._running:
            data = self._read_with_timeout(timeout=0.05)
            if data:
                self._on_input(data)
                
    def stop(self) -> None:
        self._running = False
        self._input_thread.join(timeout=1.0)
```

**Partial Escape Sequence Buffering:**
```python
def _read_with_timeout(self, timeout: float) -> bytes:
    data = os.read(self.fd, 1024)
    if data.startswith(b'\x1b') and not self._is_complete_sequence(data):
        time.sleep(timeout)
        more = os.read(self.fd, 1024)
        data += more
    return data
```

**Basic CSI Keys (MVP):**
- Arrow keys: `ESC [ A`, `ESC [ B`, `ESC [ C`, `ESC [ D`
- Enter: `\r`
- Escape: `\x1b`
- Tab: `\t`
- Control: `\x01`-`\x1f`

**Post-MVP:** Kitty Keyboard Protocol for full modifier and Unicode support.

### Mouse Events (SGR 1006 Extended)

**Protocol:** `CSI ? 1006 h` enables SGR extended coordinates

**Event format:** `CSI < Cb ; Cx ; Cy M` (press) or `m` (release)

```python
@dataclass
class MouseEvent:
    row: int
    col: int
    button: int  # 0=left, 1=middle, 2=right, 3=release, 64=wheel up, 65=wheel down
    press: bool  # True=press, False=release

def parse_mouse(data: bytes) -> MouseEvent | None:
    """Parse SGR 1006 extended mouse sequence."""
    # CSI < Cb ; Cx ; Cy M/m
    match = re.match(rb'\x1b\[<(\d+);(\d+);(\d+)([Mm])', data)
    if match:
        button = int(match.group(1))
        col = int(match.group(2)) - 1  # 1-indexed to 0-indexed
        row = int(match.group(3)) - 1
        press = match.group(4) == b'M'
        return MouseEvent(row, col, button, press)
    return None
```

**Focus determination:** Hit-test by comparing mouse position against `component._rect` for each visible component.

### Text and Unicode

**Wide Character Handling:**
```python
from wcwidth import wcswidth, wcwidth

def visible_width(text: str) -> int:
    return wcswidth(text)

def truncate_to_width(text: str, width: int) -> str:
    """Truncate without breaking wide chars or sequences."""
    result = []
    current_width = 0
    for char in text:
        char_width = wcwidth(char)
        if current_width + char_width > width:
            break
        result.append(char)
        current_width += char_width
    return ''.join(result)

def slice_by_width(text: str, start: int, end: int) -> str:
    """Slice by display width, treating wide chars as atomic."""
    result = []
    current_width = 0
    for char in text:
        char_width = wcwidth(char)
        if current_width >= end:
            break
        if current_width >= start:
            result.append(char)
        current_width += char_width
    return ''.join(result)
```

**Line Overflow:**
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

**Truecolor (RGB):**
```python
TRUECOLOR_FG = "\x1b[38;2;{};{};{}m"
TRUECOLOR_BG = "\x1b[48;2;{};{};{}m"
```

**Color Detection:**
```python
def detect_color_support() -> int:
    if os.environ.get("PYPITUI_COLOR"):
        return int(os.environ["PYPITUI_COLOR"])
    if os.environ.get("NO_COLOR"):
        return 0
    if os.environ.get("FORCE_COLOR") is not None:
        return min(int(os.environ["FORCE_COLOR"]), 3)
    
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        return 3
    
    term = os.environ.get("TERM", "").lower()
    if "256color" in term:
        return 2
    if "color" in term or "ansi" in term:
        return 1
    
    return 3  # Default: assume modern terminal
```

| Variable | Effect |
|----------|--------|
| `NO_COLOR` | Disable all colors |
| `FORCE_COLOR=0/1/2/3` | Force color level |
| `PYPITUI_COLOR=0/1/2/3` | PyPiTUI-specific override |
| `COLORTERM=truecolor/24bit` | Auto-detect truecolor |
| `TERM=*256color*` | Auto-detect 256 color |
| `TERM=*color*` or `*ansi*` | Auto-detect 16 color |

### Images

**MVP:** ASCII fallback only.

**Post-MVP:** Kitty Graphics Protocol with capability detection.

### Debug Mode

| Variable | Effect |
|----------|--------|
| `PYPITUI_DEBUG=1` | Raw render frames to `/tmp/pypitui/`, re-raise exceptions |
| `PYPITUI_LOG=debug` or path | Application logging |

### Error Handling

```python
def render_frame(self) -> None:
    try:
        lines = self._root.render(self.terminal.width)
        self._output_diff(lines)
    except LineOverflowError as e:
        self._show_error_overlay(f"Layout error: {e}")
    except Exception as e:
        self._show_error_overlay(f"Render error: {e}")
        if os.environ.get("PYPITUI_DEBUG"):
            raise
```

## File Structure

```
src/pypitui/
├── __init__.py          # Public exports
├── tui.py               # TUI class, rendering loop
├── component.py         # Component base class, Size, RenderedLine, Rect
├── components/          # Built-in components
│   ├── __init__.py
│   ├── container.py     # Vertical layout
│   ├── text.py          # Static text
│   ├── input.py         # Text input with cursor
│   ├── select.py        # Selection list
│   ├── bordered.py      # Box with borders
│   └── rich.py          # Optional Rich integration
├── overlay.py           # Overlay wrapper class (NOT a Component)
├── terminal.py          # Terminal I/O abstraction, threaded input
├── keys.py              # Key parsing (basic CSI)
├── mouse.py             # Mouse event parsing (SGR 1006)
├── styles.py            # Color and style codes
└── utils.py             # wcwidth, truncate_to_width, slice_by_width
```

## Post-MVP Enhancements

### Component Render Caching

**Challenge:** Manual `invalidate()` is error-prone. Need automatic cache invalidation when width changes or component properties change.

### DEC 2026 Feature Detection

Query during `Terminal.start()` before spawning async thread:
```python
def start(self, on_input):
    self._dec2026_supported = self._sync_query_dec2026()
    self._input_thread = threading.Thread(target=self._read_loop)
```

### Kitty Keyboard Protocol

Full progressive enhancement with key release events and modifier state.

### Kitty Graphics Protocol

Inline image display with fallback for unsupported terminals.

## Resolved Edge Cases

### Terminal Resize
- Full redraw on resize
- Container reflow with new width
- Viewport recalculation

### Wide Characters
- `slice_by_width()` treats wide chars as atomic
- Overlay collision shifts right to avoid splitting
- Grapheme clusters as single units

### Overlay Positioning
- Negative indexing (Python-style)
- Clamping to terminal bounds
- Z-index ordering (ascending)

### Scrollback Handling
- **Any change in scrollback triggers full redraw**
- Terminal scrollback is immutable
- Cursor positioning cannot reach scrolled-off content

### Focus Management
- Stack stores Components (not Overlays)
- `show_overlay()` pushes `overlay.content`
- `handle_input()` returns `bool` for consumption

### Input Architecture
- **Async:** User input (keyboard, mouse)
- **Sync:** Feature queries during init

### Color Detection
- `PYPITUI_COLOR` override
- Standard `NO_COLOR`/`FORCE_COLOR` support
- Defaults to truecolor

### Error Handling
- Error overlays for graceful degradation
- Debug mode re-raises for stack traces
