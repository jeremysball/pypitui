"""Tests for Input component."""

from pypitui.component import Size
from pypitui.components.input import Input


class TestInputMeasure:
    """Tests for Input.measure()."""

    def test_input_measure_returns_one_line(self) -> None:
        """Height=1 always for single-line input."""
        input_component = Input(placeholder="Enter text")
        size = input_component.measure(80, 24)

        assert size.height == 1
        assert size.width == 80

    def test_input_measure_respects_available_width(self) -> None:
        """Width matches available width."""
        input_component = Input()
        size = input_component.measure(40, 24)

        assert size.width == 40
        assert size.height == 1


class TestInputRender:
    """Tests for Input.render()."""

    def test_input_render_shows_content(self) -> None:
        """Typed text appears in render."""
        input_component = Input()
        input_component._content = "hello"

        lines = input_component.render(80)

        assert len(lines) == 1
        assert lines[0].content == "hello"

    def test_input_render_shows_placeholder_when_empty(self) -> None:
        """Placeholder visible when no content."""
        input_component = Input(placeholder="Enter name")

        lines = input_component.render(80)

        assert len(lines) == 1
        assert "Enter name" in lines[0].content

    def test_input_render_truncate_long_content(self) -> None:
        """Long content truncated to width."""
        input_component = Input()
        input_component._content = "a" * 100

        lines = input_component.render(20)

        assert len(lines) == 1
        assert len(lines[0].content) <= 20


class TestInputHandleInput:
    """Tests for Input.handle_input()."""

    def test_input_handle_key_appends_char(self) -> None:
        """'a' typed adds 'a' to content."""
        input_component = Input()

        consumed = input_component.handle_input(b"a")

        assert consumed is True
        assert input_component._content == "a"

    def test_input_handle_backspace_removes_char(self) -> None:
        """Backspace removes last character."""
        input_component = Input()
        input_component._content = "hi"

        consumed = input_component.handle_input(b"\x7f")  # DEL character

        assert consumed is True
        assert input_component._content == "h"

    def test_input_handle_backspace_on_empty(self) -> None:
        """Backspace on empty input does nothing."""
        input_component = Input()

        consumed = input_component.handle_input(b"\x7f")

        assert consumed is True
        assert input_component._content == ""

    def test_input_handle_input_returns_bool(self) -> None:
        """Returns True when consuming input."""
        input_component = Input()

        result = input_component.handle_input(b"x")

        assert isinstance(result, bool)
        assert result is True

    def test_input_ignores_unhandled_input(self) -> None:
        """Returns False for unhandled input."""
        input_component = Input()

        # ESC is not handled by Input
        result = input_component.handle_input(b"\x1b")

        assert result is False


class TestInputCursorPosition:
    """Tests for Input.get_cursor_position()."""

    def test_input_cursor_position_relative(self) -> None:
        """Returns (row, col) relative to component origin."""
        input_component = Input()
        input_component._content = "hello"
        input_component._cursor_pos = 5

        pos = input_component.get_cursor_position()

        assert pos is not None
        assert pos == (0, 5)  # row 0, col 5 (after "hello")

    def test_input_cursor_position_updates_with_content(self) -> None:
        """Cursor follows content length."""
        input_component = Input()

        input_component.handle_input(b"ab")
        pos = input_component.get_cursor_position()

        assert pos == (0, 2)


class TestInputOnSubmit:
    """Tests for Input.on_submit callback."""

    def test_input_on_submit_callback(self) -> None:
        """Enter triggers on_submit with content."""
        submitted_value = None

        def on_submit(value: str) -> None:
            nonlocal submitted_value
            submitted_value = value

        input_component = Input(on_submit=on_submit)
        input_component._content = "test value"

        input_component.handle_input(b"\r")  # Enter key

        assert submitted_value == "test value"

    def test_input_on_submit_clears_content(self) -> None:
        """Enter clears content after submit."""
        input_component = Input(on_submit=lambda x: None)
        input_component._content = "test"

        input_component.handle_input(b"\r")

        assert input_component._content == ""

    def test_input_on_submit_without_callback(self) -> None:
        """Enter without callback just clears content."""
        input_component = Input()
        input_component._content = "test"

        input_component.handle_input(b"\r")

        assert input_component._content == ""


class TestInputMaxLength:
    """Tests for Input.max_length."""

    def test_input_respects_max_length(self) -> None:
        """Typing stops at max_length."""
        input_component = Input(max_length=5)

        for char in "abcdef":
            input_component.handle_input(char.encode())

        assert input_component._content == "abcde"

    def test_input_max_length_zero_unlimited(self) -> None:
        """max_length=0 means unlimited."""
        input_component = Input(max_length=0)

        for char in "abcdefghij":
            input_component.handle_input(char.encode())

        assert input_component._content == "abcdefghij"
