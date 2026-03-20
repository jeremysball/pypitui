from ..component import Component as Component, RenderedLine as RenderedLine, Size as Size, StyleSpan as StyleSpan
from ..utils import truncate_to_width as truncate_to_width
from collections.abc import Callable as Callable
from dataclasses import dataclass
from typing import override

@dataclass(frozen=True)
class SelectItem:
    id: str
    label: str

@dataclass
class SelectList(Component):
    items: list[SelectItem]
    max_visible: int
    on_select: Callable[[str], None] | None = ...
    @override
    def measure(self, available_width: int, available_height: int) -> Size: ...
    @override
    def render(self, width: int) -> list[RenderedLine]: ...
    def handle_input(self, data: bytes) -> bool: ...
