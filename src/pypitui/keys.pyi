from enum import StrEnum

class Key(StrEnum):
    ENTER = '\r'
    ESCAPE = '\x1b'
    TAB = '\t'
    BACKSPACE = '\x7f'
    DELETE = 'delete'
    UP = 'up'
    DOWN = 'down'
    RIGHT = 'right'
    LEFT = 'left'
    HOME = 'home'
    END = 'end'
    INSERT = 'insert'
    PAGE_UP = 'page_up'
    PAGE_DOWN = 'page_down'
    @classmethod
    def ctrl(cls, char: str) -> Key: ...

def matches_key(data: bytes, key: Key) -> bool: ...
def parse_key(data: bytes) -> str | Key: ...
