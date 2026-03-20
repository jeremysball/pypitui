"""Container component for vertical layout."""

from typing import override

from pypitui.component import Component, RenderedLine, Size


class Container(Component):
    """Container that stacks children vertically.

    Arranges children in a vertical column, distributing available
    width equally (or according to child preferences).
    """

    def __init__(self) -> None:
        """Initialize container with empty children list."""
        super().__init__()
        self._children: list[Component] = []

    def add_child(self, component: Component) -> None:
        """Add a child component.

        Args:
            component: Child component to add
        """
        self._children.append(component)

    def clear_children(self) -> None:
        """Remove all children."""
        self._children.clear()

    @override
    def measure(self, available_width: int, available_height: int) -> Size:
        """Calculate container size as sum of child sizes.

        Width is max child width, height is sum of child heights.

        Args:
            available_width: Maximum width available
            available_height: Maximum height available

        Returns:
            Size (width, height) for container
        """
        if not self._children:
            return Size(0, 0)

        max_width = 0
        total_height = 0

        for child in self._children:
            child_size = child.measure(available_width, available_height)
            max_width = max(max_width, child_size.width)
            total_height += child_size.height

        return Size(max_width, total_height)

    @override
    def render(self, width: int) -> list[RenderedLine]:
        """Render children stacked vertically.

        Args:
            width: Width allocated for rendering

        Returns:
            List of RenderedLine objects from all children
        """
        lines: list[RenderedLine] = []

        for child in self._children:
            child_lines = child.render(width)
            lines.extend(child_lines)

        return lines
