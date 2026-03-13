from pypitui.utils import visible_width as visible_width, wrap_text_with_ansi as wrap_text_with_ansi

TOP_LEFT: str
TOP_RIGHT: str
BOTTOM_LEFT: str
BOTTOM_RIGHT: str
HORIZONTAL: str
VERTICAL: str
NBSP: str

def build_bordered_box(lines: list[str], width: int, color: str = '', title: str | None = None, center: bool = True) -> list[str]: ...
