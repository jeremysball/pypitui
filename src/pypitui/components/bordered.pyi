from ..component import Component as Component, RenderedLine as RenderedLine, Size as Size
from ..utils import truncate_to_width as truncate_to_width
from dataclasses import dataclass
from typing import override

BOX_TOP_LEFT: str
BOX_TOP_RIGHT: str
BOX_BOTTOM_LEFT: str
BOX_BOTTOM_RIGHT: str
BOX_HORIZONTAL: str
BOX_VERTICAL: str

@dataclass
class BorderedBox(Component):
    title: str | None = ...
    @override
    def measure(self, available_width: int, available_height: int) -> Size: ...
    @override
    def render(self, width: int) -> list[RenderedLine]: ...
    def add_child(self, component: Component) -> None: ...
