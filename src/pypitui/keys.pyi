"""Keyboard input handling for terminal applications."""

from typing import Final

type KeyId = str

def set_kitty_protocol_active(active: bool) -> None: ...
def is_kitty_protocol_active() -> bool: ...
def is_key_release(data: str) -> bool: ...
def is_key_repeat(data: str) -> bool: ...

class _KeyAccessor:
    """Accessor class for key identifiers with autocomplete support."""

    # Special keys
    escape: KeyId
    esc: KeyId
    enter: KeyId
    return_: KeyId
    tab: KeyId
    space: KeyId
    backspace: KeyId
    delete: KeyId
    insert: KeyId
    clear: KeyId
    home: KeyId
    end: KeyId
    page_up: KeyId
    page_down: KeyId
    up: KeyId
    down: KeyId
    left: KeyId
    right: KeyId
    f1: KeyId
    f2: KeyId
    f3: KeyId
    f4: KeyId
    f5: KeyId
    f6: KeyId
    f7: KeyId
    f8: KeyId
    f9: KeyId
    f10: KeyId
    f11: KeyId
    f12: KeyId
    # Symbol keys
    backtick: KeyId
    hyphen: KeyId
    equals: KeyId
    left_bracket: KeyId
    right_bracket: KeyId
    backslash: KeyId
    semicolon: KeyId
    quote: KeyId
    comma: KeyId
    period: KeyId
    slash: KeyId
    exclamation: KeyId
    at: KeyId
    hash: KeyId
    dollar: KeyId
    percent: KeyId
    caret: KeyId
    ampersand: KeyId
    asterisk: KeyId
    left_paren: KeyId
    right_paren: KeyId
    underscore: KeyId
    plus: KeyId
    pipe: KeyId
    tilde: KeyId
    left_brace: KeyId
    right_brace: KeyId
    colon: KeyId
    less_than: KeyId
    greater_than: KeyId
    question: KeyId

    @staticmethod
    def ctrl(key: str) -> KeyId: ...
    @staticmethod
    def shift(key: str) -> KeyId: ...
    @staticmethod
    def alt(key: str) -> KeyId: ...
    @staticmethod
    def ctrl_shift(key: str) -> KeyId: ...
    @staticmethod
    def ctrl_alt(key: str) -> KeyId: ...
    @staticmethod
    def shift_alt(key: str) -> KeyId: ...

Key: Final[_KeyAccessor]

def parse_key(data: str) -> str | None: ...
def matches_key(data: str, key_id: KeyId) -> bool: ...
