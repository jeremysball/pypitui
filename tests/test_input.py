"""Tests for Input component - ported from pi-tui."""

import pytest
from pypitui import Input
from pypitui.keys import Key


class TestInputComponent:
    """Tests for Input component."""

    def test_basic_typing(self):
        """Basic typing works."""
        input_cmp = Input()
        
        input_cmp.handle_input("h")
        input_cmp.handle_input("e")
        input_cmp.handle_input("l")
        input_cmp.handle_input("l")
        input_cmp.handle_input("o")
        
        assert input_cmp.get_value() == "hello"

    def test_set_value(self):
        """Can set value programmatically."""
        input_cmp = Input()
        input_cmp.set_value("initial")
        
        assert input_cmp.get_value() == "initial"

    def test_backspace(self):
        """Backspace deletes character."""
        input_cmp = Input()
        input_cmp.handle_input("h")
        input_cmp.handle_input("i")
        input_cmp.handle_input("\x7f")  # backspace
        
        assert input_cmp.get_value() == "h"

    def test_delete(self):
        """Delete removes character at cursor."""
        input_cmp = Input()
        input_cmp.set_value("hello")
        # Move cursor to start
        input_cmp.handle_input("\x01")  # Ctrl+A
        # Move cursor right once
        input_cmp.handle_input("\x1b[C")  # right
        # Delete
        input_cmp.handle_input("\x1b[3~")  # delete
        
        assert input_cmp.get_value() == "ello"

    def test_cursor_navigation_left_right(self):
        """Cursor can move left and right."""
        input_cmp = Input()
        input_cmp.set_value("hello")
        
        # Move left
        input_cmp.handle_input("\x1b[D")  # left
        # Delete should remove 'o'
        input_cmp.handle_input("\x1b[3~")  # delete
        assert input_cmp.get_value() == "hell"
        
        # Move left again
        input_cmp.handle_input("\x1b[D")  # left
        # Delete should remove 'l'
        input_cmp.handle_input("\x1b[3~")  # delete
        assert input_cmp.get_value() == "hel"

    def test_home_end(self):
        """Home and End keys work."""
        input_cmp = Input()
        input_cmp.set_value("hello")
        
        # Home - cursor at start
        input_cmp.handle_input("\x01")  # Ctrl+A
        # Type at start
        input_cmp.handle_input("X")
        assert input_cmp.get_value() == "Xhello"
        
        # End - cursor at end
        input_cmp.handle_input("\x05")  # Ctrl+E
        # Type at end
        input_cmp.handle_input("Y")
        assert input_cmp.get_value() == "XhelloY"

    def test_ctrl_u_deletes_to_start(self):
        """Ctrl+U deletes to start of line."""
        input_cmp = Input()
        input_cmp.set_value("hello world")
        
        # Move cursor to after "hello "
        input_cmp.handle_input("\x01")  # Ctrl+A - go to start
        for _ in range(6):
            input_cmp.handle_input("\x1b[C")  # right
        
        # Ctrl+U deletes "hello "
        input_cmp.handle_input("\x15")  # Ctrl+U
        
        assert input_cmp.get_value() == "world"

    def test_ctrl_k_deletes_to_end(self):
        """Ctrl+K deletes to end of line."""
        input_cmp = Input()
        input_cmp.set_value("hello world")
        
        # Go to start
        input_cmp.handle_input("\x01")  # Ctrl+A
        # Ctrl+K deletes everything
        input_cmp.handle_input("\x0b")  # Ctrl+K
        
        assert input_cmp.get_value() == ""

    def test_submits_on_enter(self):
        """Submits value on Enter."""
        input_cmp = Input()
        submitted = None
        
        def on_submit(value):
            nonlocal submitted
            submitted = value
        
        input_cmp.on_submit = on_submit
        
        input_cmp.handle_input("h")
        input_cmp.handle_input("i")
        input_cmp.handle_input("\r")  # Enter
        
        assert submitted == "hi"

    def test_backslash_inserted_as_regular_char(self):
        """Backslash is inserted as regular character."""
        input_cmp = Input()
        
        input_cmp.handle_input("\\")
        input_cmp.handle_input("x")
        
        assert input_cmp.get_value() == "\\x"

    def test_submits_value_including_backslash(self):
        """Submits value including backslash on Enter."""
        input_cmp = Input()
        submitted = None
        
        def on_submit(value):
            nonlocal submitted
            submitted = value
        
        input_cmp.on_submit = on_submit
        
        input_cmp.handle_input("h")
        input_cmp.handle_input("e")
        input_cmp.handle_input("l")
        input_cmp.handle_input("l")
        input_cmp.handle_input("o")
        input_cmp.handle_input("\\")
        input_cmp.handle_input("\r")  # Enter
        
        assert submitted == "hello\\"

    def test_placeholder_when_empty(self):
        """Shows placeholder when empty and not focused."""
        input_cmp = Input(placeholder="Enter text...")
        
        lines = input_cmp.render(30)
        assert "Enter text..." in lines[0]

    def test_password_mode(self):
        """Password mode hides characters."""
        input_cmp = Input(password=True)
        input_cmp.handle_input("s")
        input_cmp.handle_input("e")
        input_cmp.handle_input("c")
        input_cmp.handle_input("r")
        input_cmp.handle_input("e")
        input_cmp.handle_input("t")
        
        lines = input_cmp.render(20)
        # Should show asterisks, not actual text
        assert "secret" not in lines[0]
        assert "******" in lines[0]

    def test_focused_shows_cursor(self):
        """Focused input shows cursor marker."""
        from pypitui import CURSOR_MARKER
        
        input_cmp = Input()
        input_cmp.handle_input("h")
        input_cmp.handle_input("i")
        input_cmp.focused = True
        
        lines = input_cmp.render(20)
        assert CURSOR_MARKER in lines[0]

    def test_not_focused_no_cursor_marker(self):
        """Not focused input has no cursor marker."""
        from pypitui import CURSOR_MARKER
        
        input_cmp = Input()
        input_cmp.handle_input("h")
        input_cmp.handle_input("i")
        input_cmp.focused = False
        
        lines = input_cmp.render(20)
        assert CURSOR_MARKER not in lines[0]
