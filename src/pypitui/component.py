"""Component base class and data structures for PyPiTUI.

Provides the foundation for the component system including Size,
RenderedLine, Rect, and the abstract Component base class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Size:
    """Dimensions for component measurement.

    Attributes:
        width: Width in characters
        height: Height in lines
    """

    width: int
    height: int


@dataclass(frozen=True)
class StyleSpan:
    """A styled span within a rendered line.

    Attributes:
        start: Start column (inclusive)
        end: End column (exclusive)
        fg: Foreground color (optional)
        bg: Background color (optional)
        bold: Bold text (optional)
        italic: Italic text (optional)
        underline: Underlined text (optional)
    """

    start: int
    end: int
    fg: str | None = None
    bg: str | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False


@dataclass(frozen=True)
class RenderedLine:
    """A single line of rendered output with style information.

    This is the canonical return type for all render() methods.

    Attributes:
        content: The text content of the line
        styles: List of style spans applying to this line
    """

    content: str
    styles: list[StyleSpan]


@dataclass(frozen=True)
class Rect:
    """Rectangle defining position and dimensions.

    Attributes:
        x: Column position (0-indexed, from left)
        y: Row position (0-indexed, from top)
        width: Width in characters
        height: Height in lines
    """

    x: int
    y: int
    width: int
    height: int

    @property
    def left(self) -> int:
        """Left edge column (same as x)."""
        return self.x

    @property
    def right(self) -> int:
        """Right edge column (exclusive)."""
        return self.x + self.width

    @property
    def top(self) -> int:
        """Top edge row (same as y)."""
        return self.y

    @property
    def bottom(self) -> int:
        """Bottom edge row (exclusive)."""
        return self.y + self.height


class Component(ABC):
    """Abstract base class for all UI components.

    Components implement a measure/render lifecycle:
    1. measure() - Calculate required dimensions given available space
    2. render() - Generate output lines given allocated width

    Subclasses must implement both measure() and render().
    """

    def __init__(self) -> None:
        """Initialize component."""
        self._rect: Rect | None = None

    @abstractmethod
    def measure(self, available_width: int, available_height: int) -> Size:
        """Calculate the component's preferred size.

        Args:
            available_width: Maximum width available
            available_height: Maximum height available

        Returns:
            Preferred Size (width, height)
        """
        ...

    @abstractmethod
    def render(self, width: int) -> list[RenderedLine]:
        """Render the component to output lines.

        Args:
            width: Width allocated for rendering

        Returns:
            List of RenderedLine objects
        """
        ...

    def invalidate(self) -> None:  # noqa: B027
        """Mark this component as needing re-render.

        Subclasses can override to notify parents of invalidation.
        """
        pass

    def _child_invalidated(self, _child: "Component") -> None:
        """Called when a child component is invalidated.

        Args:
            child: The child component that was invalidated
        """
        # By default, invalidate ourselves when a child changes
        self.invalidate()
