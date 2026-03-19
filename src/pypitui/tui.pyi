from _typeshed import Incomplete
from pypitui.component import Component as Component
from pypitui.terminal import Terminal as Terminal

class TUI:
    terminal: Incomplete
    def __init__(self, terminal: Terminal) -> None: ...
    def add_child(self, component: Component) -> None: ...
