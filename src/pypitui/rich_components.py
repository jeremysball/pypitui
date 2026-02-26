"""Markdown component using Rich for rendering.

This is an optional component that requires the 'rich' extra:
    pip install pypitui[rich]
"""

from __future__ import annotations

from .tui import Component
from .utils import visible_width

_RICH_REQUIRED_MSG = (
    "This component requires 'rich' package. "
    "Install with: pip install pypitui[rich]"
)


def _apply_padding(
    lines: list[str],
    width: int,
    padding_x: int,
    padding_y: int,
) -> list[str]:
    """Apply horizontal and vertical padding to rendered lines.

    Args:
        lines: Rendered content lines
        width: Target width including padding
        padding_x: Horizontal padding (added to left)
        padding_y: Vertical padding (added to top and bottom)

    Returns:
        Padded lines with proper spacing
    """
    result: list[str] = []

    # Top padding
    result.extend(" " * width for _ in range(padding_y))

    # Content with horizontal padding
    for line in lines:
        if line:
            padded = " " * padding_x + line
            line_width = visible_width(padded)
            if line_width < width:
                padded += " " * (width - line_width)
            result.append(padded)

    # Bottom padding
    result.extend(" " * width for _ in range(padding_y))

    return result


class Markdown(Component):
    """Render markdown using Rich library.

    Requires: pip install pypitui[rich]

    Features:
    - Headings, bold, italic, code blocks
    - Lists, links, blockquotes
    - Syntax highlighting in code blocks
    - Tables
    """

    def __init__(
        self,
        text: str = "",
        padding_x: int = 0,
        padding_y: int = 0,
        width: int | None = None,
        code_theme: str = "monokai",
    ) -> None:
        """Initialize Markdown component.

        Args:
            text: Markdown content
            padding_x: Horizontal padding
            padding_y: Vertical padding
            width: Fixed width (None = use render width)
            code_theme: Pygments theme for code blocks
        """
        self._text = text
        self._padding_x = padding_x
        self._padding_y = padding_y
        self._width = width
        self._code_theme = code_theme
        self._cache: tuple[int, list[str]] | None = None

    def set_text(self, text: str) -> None:
        """Update markdown content."""
        self._text = text
        self._cache = None

    def set_code_theme(self, theme: str) -> None:
        """Set code highlighting theme."""
        self._code_theme = theme
        self._cache = None

    def invalidate(self) -> None:
        """Clear render cache."""
        self._cache = None

    def _render_with_rich(self, width: int) -> list[str]:
        """Render markdown using Rich."""
        try:
            from rich.console import Console  # noqa: PLC0415
            from rich.markdown import Markdown as RichMarkdown  # noqa: PLC0415
        except ImportError as e:
            raise ImportError(_RICH_REQUIRED_MSG) from e

        # Calculate content width
        content_width = width - self._padding_x * 2
        if content_width <= 0:
            return []

        # Create Rich markdown
        md = RichMarkdown(
            self._text,
            code_theme=self._code_theme,
        )

        # Create console and capture output
        console = Console(
            width=content_width,
            no_color=False,
            force_terminal=True,
            legacy_windows=False,
        )

        with console.capture() as capture:
            console.print(md)

        output = capture.get()
        return output.split("\n")

    def render(self, width: int) -> list[str]:
        """Render markdown to lines."""
        # Check cache
        if self._cache and self._cache[0] == width:
            return self._cache[1]

        content_width = width - self._padding_x * 2
        if content_width <= 0:
            return []

        # Render markdown and apply padding
        md_lines = self._render_with_rich(width)
        lines = _apply_padding(
            md_lines, width, self._padding_x, self._padding_y
        )

        # Cache result
        self._cache = (width, lines)
        return lines


class RichText(Component):
    """Render Rich text/markup.

    Requires: pip install pypitui[rich]

    Example:
        RichText("[bold red]Hello[/bold red] World!")
    """

    def __init__(
        self,
        text: str = "",
        padding_x: int = 0,
        padding_y: int = 0,
    ) -> None:
        self._text = text
        self._padding_x = padding_x
        self._padding_y = padding_y
        self._cache: tuple[int, list[str]] | None = None

    def set_text(self, text: str) -> None:
        """Update text content."""
        self._text = text
        self._cache = None

    def invalidate(self) -> None:
        """Clear cache."""
        self._cache = None

    def render(self, width: int) -> list[str]:
        """Render to lines."""
        if self._cache and self._cache[0] == width:
            return self._cache[1]

        try:
            from rich.console import Console  # noqa: PLC0415
            from rich.text import Text as RichTextLib  # noqa: PLC0415
        except ImportError as e:
            raise ImportError(_RICH_REQUIRED_MSG) from e

        content_width = width - self._padding_x * 2
        if content_width <= 0:
            return []

        # Parse and render
        console = Console(
            width=content_width,
            no_color=False,
            force_terminal=True,
        )

        rich_text = RichTextLib.from_markup(self._text)

        with console.capture() as capture:
            console.print(rich_text)

        # Apply padding to rendered lines
        text_lines = [line for line in capture.get().split("\n") if line]
        lines = _apply_padding(
            text_lines, width, self._padding_x, self._padding_y
        )

        self._cache = (width, lines)
        return lines


class RichTable(Component):
    """Render Rich tables.

    Requires: pip install pypitui[rich]

    Example:
        table = RichTable(title="My Table")
        table.add_column("Name", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Item 1", "100")
    """

    def __init__(
        self,
        title: str = "",
        padding_x: int = 0,
        padding_y: int = 0,
    ) -> None:
        self._title = title
        self._padding_x = padding_x
        self._padding_y = padding_y
        self._columns: list[tuple[str, str | None, str]] = []
        self._rows: list[tuple[str, ...]] = []
        self._cache: tuple[int, list[str]] | None = None

    def add_column(
        self,
        name: str,
        style: str | None = None,
        justify: str = "left",
    ) -> None:
        """Add a column."""
        self._columns.append((name, style, justify))
        self._cache = None

    def add_row(self, *values: str) -> None:
        """Add a row."""
        self._rows.append(values)
        self._cache = None

    def clear_rows(self) -> None:
        """Clear all rows."""
        self._rows.clear()
        self._cache = None

    def invalidate(self) -> None:
        """Clear cache."""
        self._cache = None

    def render(self, width: int) -> list[str]:
        """Render to lines."""
        if self._cache and self._cache[0] == width:
            return self._cache[1]

        try:
            from rich.console import Console  # noqa: PLC0415
            from rich.table import Table  # noqa: PLC0415
        except ImportError as e:
            raise ImportError(_RICH_REQUIRED_MSG) from e

        content_width = width - self._padding_x * 2
        if content_width <= 0:
            return []

        # Build table
        table = Table(title=self._title if self._title else None)

        for col in self._columns:
            name, style, justify = col
            table.add_column(name, style=style, justify=justify)

        for row in self._rows:
            table.add_row(*row)

        # Render
        console = Console(
            width=content_width,
            no_color=False,
            force_terminal=True,
        )

        with console.capture() as capture:
            console.print(table)

        # Apply padding to rendered lines
        table_lines = [line for line in capture.get().split("\n") if line]
        lines = _apply_padding(
            table_lines, width, self._padding_x, self._padding_y
        )

        self._cache = (width, lines)
        return lines


# =============================================================================
# Rich <-> ANSI Conversion Utilities
# =============================================================================


def rich_to_ansi(markup: str) -> str:
    """Convert Rich markup to ANSI codes.

    Use this to convert Rich markup strings for components that expect
    plain ANSI strings (like SelectList items).

    Args:
        markup: Rich markup string (e.g., "[bold cyan]Hello[/bold cyan]")

    Returns:
        ANSI-escaped string ready for display

    Example:
        from pypitui.rich_components import rich_to_ansi

        # Rich markup for regular components
        tui.add_child(RichText("[bold cyan]Hello[/bold cyan]"))

        # Convert to ANSI for SelectList
        label = rich_to_ansi("[bold cyan]Menu Item[/bold cyan]")
        items = [SelectItem("key", label,
                            rich_to_ansi("[dim]Description[/dim]"))]
    """
    from io import StringIO  # noqa: PLC0415

    from rich.console import Console  # noqa: PLC0415

    buf = StringIO()
    console = Console(
        file=buf, force_terminal=True, width=200, legacy_windows=False
    )
    console.print(markup, end="")
    return buf.getvalue()


def rich_color_to_ansi(color: str) -> str:
    """Convert a Rich color name to its ANSI escape code.

    Args:
        color: Rich color name (e.g., "bright_cyan", "red", "bold magenta")

    Returns:
        ANSI escape code string, or empty string if color is empty

    Example:
        from pypitui.rich_components import rich_color_to_ansi

        cyan = rich_color_to_ansi("bright_cyan")  # "\\x1b[96m"
        bold_red = rich_color_to_ansi("bold red")  # "\\x1b[1;31m"
    """
    if not color:
        return ""

    from rich.console import Console  # noqa: PLC0415
    from rich.text import Text  # noqa: PLC0415

    # Create a Console to render the color
    console = Console(force_terminal=True, legacy_windows=False)

    # Render text with the color and extract the ANSI code
    text = Text("X", style=color)
    with console.capture() as capture:
        console.print(text, end="")

    result = capture.get()
    # Remove the "X" character, leaving only the ANSI codes
    # Result may be "\x1b[1;31mX\x1b[0m" or "\x1b[1;31mX"
    # depending on Rich version
    if "X" in result:
        # Find the position of X and take everything before it
        x_pos = result.index("X")
        return result[:x_pos]
    return result
