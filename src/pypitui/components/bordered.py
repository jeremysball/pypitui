"""BorderedBox component for framed content.

Provides a decorative border around a single child component using
Unicode box-drawing characters.
"""

from dataclasses import dataclass, field
from typing import override

from ..component import Component, RenderedLine, Size
from ..utils import truncate_to_width

# Box drawing characters
BOX_TOP_LEFT = "┌"
BOX_TOP_RIGHT = "┐"
BOX_BOTTOM_LEFT = "└"
BOX_BOTTOM_RIGHT = "┘"
BOX_HORIZONTAL = "─"
BOX_VERTICAL = "│"


@dataclass
class BorderedBox(Component):
    """Decorative border around content.

    Attributes:
        title: Optional title displayed in top border
    """

    title: str | None = None
    _child: Component | None = field(default=None, init=False)

    @override
    def measure(self, available_width: int, available_height: int) -> Size:
        """Return size including borders.

        Adds 2 to child dimensions for borders.

        Args:
            available_width: Maximum width available
            available_height: Maximum height available

        Returns:
            Size including border space
        """
        if self._child is None:
            # Just borders, no interior
            return Size(width=available_width, height=2)

        # Child measures interior space (width - 2 for borders)
        child_size = self._child.measure(
            max(0, available_width - 2), max(0, available_height - 2)
        )

        # Add 2 for borders
        return Size(
            width=available_width,
            height=child_size.height + 2,
        )

    @override
    def render(self, width: int) -> list[RenderedLine]:
        """Render box with content.

        Args:
            width: Maximum width for rendering

        Returns:
            List of rendered lines with box drawing characters
        """
        lines: list[RenderedLine] = []

        # Top border with optional title
        if self.title:
            title = truncate_to_width(self.title, max(0, width - 4))
            fill_len = width - len(title) - 4
            border_fill = BOX_HORIZONTAL * fill_len
            top = f"{BOX_TOP_LEFT} {title} {border_fill}{BOX_TOP_RIGHT}"
            # Ensure exact width
            if len(top) > width:
                top = top[:width - 1] + BOX_TOP_RIGHT
        else:
            top = BOX_TOP_LEFT + BOX_HORIZONTAL * (width - 2) + BOX_TOP_RIGHT
        lines.append(RenderedLine(content=top[:width], styles=[]))

        # Interior content
        if self._child is not None:
            interior_width = width - 2
            child_lines = self._child.render(interior_width)
            for child_line in child_lines:
                # Pad or truncate content to fit interior width
                content = child_line.content[:interior_width]
                content = content + " " * (interior_width - len(content))
                line = f"{BOX_VERTICAL}{content}{BOX_VERTICAL}"
                rendered = RenderedLine(content=line, styles=child_line.styles)
                lines.append(rendered)
        # else: no interior lines when no child

        # Bottom border
        border_fill = BOX_HORIZONTAL * (width - 2)
        bottom = BOX_BOTTOM_LEFT + border_fill + BOX_BOTTOM_RIGHT
        lines.append(RenderedLine(content=bottom[:width], styles=[]))

        return lines

    def add_child(self, component: Component) -> None:
        """Add child component inside the border.

        Only one child is supported; subsequent calls replace.

        Args:
            component: Child component to wrap
        """
        self._child = component
        self.invalidate()
