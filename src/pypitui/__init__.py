"""PyPiTUI - A Python port of @mariozechner/pi-tui.

A terminal UI library with differential rendering, inspired by React's
component model but for terminal applications.
"""

from .box_utils import (
    BOTTOM_LEFT,
    BOTTOM_RIGHT,
    HORIZONTAL,
    NBSP,
    TOP_LEFT,
    TOP_RIGHT,
    VERTICAL,
    build_bordered_box,
)
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
    set_kitty_protocol_active,
)
from .terminal import MockTerminal, ProcessTerminal, Terminal
from .tui import (
    CURSOR_MARKER,
    FRAME_TIME,
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
    get_terminal_size,
    slice_by_column,
    strip_ansi,
    truncate_to_width,
    visible_width,
    wrap_text_with_ansi,
)

__all__ = [
    "BOTTOM_LEFT",
    "BOTTOM_RIGHT",
    "CURSOR_MARKER",
    "EVENT_PRESS",
    "EVENT_RELEASE",
    "EVENT_REPEAT",
    "FRAME_TIME",
    "HORIZONTAL",
    "NBSP",
    "TOP_LEFT",
    "TOP_RIGHT",
    "TUI",
    "VERTICAL",
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
    "Terminal",
    "Text",
    "build_bordered_box",
    "get_terminal_size",
    "is_focusable",
    "matches_key",
    "parse_key",
    "set_kitty_protocol_active",
    "slice_by_column",
    "strip_ansi",
    "truncate_to_width",
    "visible_width",
    "wrap_text_with_ansi",
]

__version__ = "0.4.3"
