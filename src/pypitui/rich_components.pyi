"""Markdown component using Rich for rendering."""

from .tui import Component

class Markdown(Component):
    """Render markdown using Rich library."""

    def __init__(
        self,
        text: str = ...,
        padding_x: int = ...,
        padding_y: int = ...,
        width: int | None = ...,
        code_theme: str = ...,
    ) -> None: ...
    def set_text(self, text: str) -> None: ...
    def set_code_theme(self, theme: str) -> None: ...
    def invalidate(self) -> None: ...
    def render(self, width: int) -> list[str]: ...

class RichText(Component):
    """Render Rich text/markup."""

    def __init__(
        self,
        text: str = ...,
        padding_x: int = ...,
        padding_y: int = ...,
    ) -> None: ...
    def set_text(self, text: str) -> None: ...
    def invalidate(self) -> None: ...
    def render(self, width: int) -> list[str]: ...

class RichTable(Component):
    """Render Rich tables."""

    def __init__(
        self,
        title: str = ...,
        padding_x: int = ...,
        padding_y: int = ...,
    ) -> None: ...
    def add_column(
        self,
        name: str,
        style: str | None = ...,
        justify: str = ...,
    ) -> None: ...
    def add_row(self, *values: str) -> None: ...
    def clear_rows(self) -> None: ...
    def invalidate(self) -> None: ...
    def render(self, width: int) -> list[str]: ...
