import abc
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class Size:
    width: int
    height: int

@dataclass(frozen=True)
class StyleSpan:
    start: int
    end: int
    fg: str | None = ...
    bg: str | None = ...
    bold: bool = ...
    italic: bool = ...
    underline: bool = ...

@dataclass(frozen=True)
class RenderedLine:
    content: str
    styles: list[StyleSpan]

@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int
    @property
    def left(self) -> int: ...
    @property
    def right(self) -> int: ...
    @property
    def top(self) -> int: ...
    @property
    def bottom(self) -> int: ...

class Component(ABC, metaclass=abc.ABCMeta):
    def __init__(self) -> None: ...
    @abstractmethod
    def measure(self, available_width: int, available_height: int) -> Size: ...
    @abstractmethod
    def render(self, width: int) -> list[RenderedLine]: ...
    def invalidate(self) -> None: ...
