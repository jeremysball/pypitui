"""PyPiTUI - A Python port of @mariozechner/pi-tui.

A terminal UI library with differential rendering, inspired by React's
component model but for terminal applications.
"""

from .components import (
    BorderedBox,
    Box,
    Input,
    SelectItem,
    SelectList,
    SelectListTheme,
    Spacer,
    Text,
)
from .keys import (
    EVENT_PRESS,
    EVENT_RELEASE,
    EVENT_REPEAT,
    Key,
    matches_key,
    parse_key,
)
from .terminal import MockTerminal, ProcessTerminal, Terminal
from .tui import (
    CURSOR_MARKER,
    TUI,
    Component,
    Container,
    Focusable,
    OverlayHandle,
    OverlayMargin,
    OverlayOptions,
    is_focusable,
)
from .utils import (
    slice_by_column,
    truncate_to_width,
    visible_width,
    wrap_text_with_ansi,
)

__all__ = [
    "CURSOR_MARKER",
    # Keys
    "EVENT_PRESS",
    "EVENT_RELEASE",
    "EVENT_REPEAT",
    # Core
    "TUI",
    "BorderedBox",
    "Box",
    "Component",
    "Container",
    "Focusable",
    "Input",
    "Key",
    "MockTerminal",
    "OverlayHandle",
    "OverlayMargin",
    "OverlayOptions",
    "ProcessTerminal",
    "SelectItem",
    "SelectList",
    "SelectListTheme",
    "Spacer",
    # Terminal
    "Terminal",
    # Components
    "Text",
    "is_focusable",
    "matches_key",
    "parse_key",
    "slice_by_column",
    "truncate_to_width",
    # Utils
    "visible_width",
    "wrap_text_with_ansi",
]

__version__ = "0.2.2"
