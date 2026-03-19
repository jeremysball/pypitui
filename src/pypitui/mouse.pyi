from dataclasses import dataclass

@dataclass(frozen=True)
class MouseEvent:
    button: int
    col: int
    row: int
    pressed: bool

def parse_mouse(data: bytes) -> MouseEvent | None: ...
