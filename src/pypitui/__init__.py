"""PyPiTUI - A Python TUI library with differential rendering.

PyPiTUI provides a component-based TUI framework with:
- Differential rendering for 60 FPS performance
- Terminal abstraction with raw mode and async input
- Component system with measure/render lifecycle
- Focus management with stack and tab cycling
- Overlay system for floating UI
- Wide character support for CJK and emoji

Example:

    >>> from pypitui import TUI, Container, Text, Input
    >>> from pypitui.terminal import Terminal
    >>>
    >>> with Terminal() as term:
    ...     tui = TUI(term)
    ...     container = Container()
    ...     container.add_child(Text("Hello, PyPiTUI!"))
    ...     tui.add_child(container)
    ...     tui.render_frame()
"""

__version__ = "0.1.0"

# Core data structures
from .component import Component, Rect, RenderedLine, Size, StyleSpan

# Components
from .components.bordered import BorderedBox
from .components.container import Container
from .components.input import Input
from .components.select import SelectItem, SelectList
from .components.text import Text

# Input handling
from .keys import Key, matches_key, parse_key
from .mouse import MouseEvent, parse_mouse

# Overlays
from .overlay import Overlay, OverlayPosition

# Styles and colors
from .styles import detect_color_support

# Terminal abstraction
from .terminal import Terminal

# Errors
# Main TUI class
from .tui import TUI, LineOverflowError

# Utilities
from .utils import slice_by_width, truncate_to_width, wcwidth

__all__ = [
    "TUI",
    "BorderedBox",
    "Component",
    "Container",
    "Input",
    "Key",
    "LineOverflowError",
    "MouseEvent",
    "Overlay",
    "OverlayPosition",
    "Rect",
    "RenderedLine",
    "SelectItem",
    "SelectList",
    "Size",
    "StyleSpan",
    "Terminal",
    "Text",
    "__version__",
    "detect_color_support",
    "matches_key",
    "parse_key",
    "parse_mouse",
    "slice_by_width",
    "truncate_to_width",
    "wcwidth",
]
