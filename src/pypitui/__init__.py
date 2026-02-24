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
from .keys import Key, matches_key, parse_key
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
from .utils import slice_by_column, truncate_to_width, visible_width, wrap_text_with_ansi

__all__ = [
    # Core
    "TUI",
    "Component",
    "Container",
    "Focusable",
    "CURSOR_MARKER",
    "OverlayOptions",
    "OverlayMargin",
    "OverlayHandle",
    "is_focusable",
    # Components
    "Text",
    "Box",
    "BorderedBox",
    "Spacer",
    "SelectList",
    "SelectItem",
    "SelectListTheme",
    "Input",
    # Keys
    "Key",
    "matches_key",
    "parse_key",
    # Utils
    "visible_width",
    "truncate_to_width",
    "wrap_text_with_ansi",
    "slice_by_column",
    # Terminal
    "Terminal",
    "ProcessTerminal",
    "MockTerminal",
]

__version__ = "0.1.0"
