"""PyPiTUI - A Python TUI library with differential rendering."""

from .components import (
    Box as Box,
    Input as Input,
    SelectItem as SelectItem,
    SelectList as SelectList,
    SelectListTheme as SelectListTheme,
    Spacer as Spacer,
    Text as Text,
)
from .keys import Key as Key, matches_key as matches_key, parse_key as parse_key
from .terminal import MockTerminal as MockTerminal, ProcessTerminal as ProcessTerminal, Terminal as Terminal
from .tui import (
    CURSOR_MARKER as CURSOR_MARKER,
    TUI as TUI,
    Component as Component,
    Container as Container,
    Focusable as Focusable,
    OverlayHandle as OverlayHandle,
    OverlayMargin as OverlayMargin,
    OverlayOptions as OverlayOptions,
    is_focusable as is_focusable,
)
from .utils import (
    truncate_to_width as truncate_to_width,
    visible_width as visible_width,
    wrap_text_with_ansi as wrap_text_with_ansi,
)

__version__: str
