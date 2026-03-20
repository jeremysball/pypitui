"""Overlay system for viewport-relative floating UI.

Overlays are NOT Components - they wrap Components for
viewport-relative positioning and compositing.
"""

from dataclasses import dataclass

from .component import Component


@dataclass(frozen=True)
class OverlayPosition:
    """Position specification for overlay placement.

    Supports absolute and relative positioning:
    - row=0: top of viewport, row=-1: bottom
    - col=0: left edge
    - width=-1: auto-size to content
    - height=-1: auto-size to content

    Attributes:
        row: Vertical position (0=top, -1=bottom)
        col: Horizontal position (0=left edge)
        width: Width constraint (-1=auto)
        height: Height constraint (-1=auto)
        anchor: Optional anchor point ("center", "top-left", etc.)
    """

    row: int
    col: int = 0
    width: int = -1
    height: int = -1
    anchor: str | None = None


@dataclass
class Overlay:
    """Wrapper for floating viewport-relative content.

    Overlays are NOT Components. They wrap a Component for
    compositing on top of the base UI.

    Attributes:
        content: The Component to render inside the overlay
        position: Where to place the overlay
        visible: Whether the overlay is currently visible
        z_index: Stacking order (higher = on top)
    """

    content: Component
    position: OverlayPosition
    visible: bool = True
    z_index: int = 0
