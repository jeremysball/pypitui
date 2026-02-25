"""Comprehensive tests for PyPiTUI library."""

from pypitui import (
    CURSOR_MARKER,
    TUI,
    Box,
    Container,
    Input,
    Key,
    MockTerminal,
    OverlayOptions,
    SelectItem,
    SelectList,
    SelectListTheme,
    Spacer,
    Text,
    is_focusable,
    matches_key,
    truncate_to_width,
    visible_width,
)


def test_visible_width():
    """Test visible_width function."""
    assert visible_width("hello") == 5
    assert visible_width("\x1b[31mhello\x1b[0m") == 5  # ANSI codes don't count
    assert visible_width("") == 0


def test_truncate_to_width():
    """Test truncate_to_width function."""
    assert truncate_to_width("hello", 10) == "hello"
    assert truncate_to_width("hello world this is a test", 10) == "hello w..."
    # Default ellipsis is "...", third param is ellipsis string
    result = truncate_to_width("hello world this is a test", 11, "...")
    assert "..." in result


def test_matches_key():
    """Test matches_key function."""
    assert matches_key("\x1b[A", Key.up)
    assert matches_key("\x1b[B", Key.down)
    assert matches_key("\x03", Key.ctrl("c"))
    assert matches_key("\r", Key.enter)
    assert matches_key("\x1b", Key.escape)
    assert not matches_key("x", Key.escape)


def test_select_list():
    """Test SelectList component."""
    items = [
        SelectItem(value="a", label="Option A"),
        SelectItem(value="b", label="Option B"),
        SelectItem(value="c", label="Option C"),
    ]

    theme = SelectListTheme()
    select_list = SelectList(items, 5, theme)

    # Test render
    lines = select_list.render(40)
    assert len(lines) == 3
    assert "> Option A" in lines[0]


def test_text_component():
    """Test Text component."""
    text = Text("Hello World", 1, 1)
    lines = text.render(20)
    assert len(lines) > 0
    # Text has padding, so content is in middle lines
    assert any("Hello World" in line for line in lines)


def test_input_component():
    """Test Input component."""
    input_cmp = Input(placeholder="Type here...")

    # When not focused and empty, shows placeholder
    lines = input_cmp.render(30)
    # Placeholder is shown when empty and not focused
    assert "Type here..." in lines[0] or ">" in lines[0]

    # Type some text
    input_cmp.handle_input("h")
    input_cmp.handle_input("e")
    input_cmp.handle_input("l")
    input_cmp.handle_input("l")
    input_cmp.handle_input("o")
    assert input_cmp.get_value() == "hello"

    # When focused, cursor marker is present
    input_cmp.focused = True
    lines = input_cmp.render(30)
    assert CURSOR_MARKER in lines[0]


def test_container():
    """Test Container component."""
    container = Container()
    container.add_child(Text("Line 1", 0, 0))
    container.add_child(Spacer(1))
    container.add_child(Text("Line 2", 0, 0))

    lines = container.render(40)
    # Text with padding adds lines, spacer adds 1 empty line
    assert len(lines) >= 3

    container.remove_child(container.children[1])
    lines = container.render(40)
    assert len(lines) >= 2

    container.clear()
    assert len(container.children) == 0


def test_box_component():
    """Test Box component."""
    box = Box(2, 1)
    box.add_child(Text("Content", 0, 0))
    lines = box.render(40)
    # Box with padding_y=1 adds 2 padding lines + content lines
    assert len(lines) >= 3
    # Content should be somewhere in the output
    assert any("Content" in line for line in lines)


def test_key_parsing():
    """Test key parsing."""
    # Control characters
    assert matches_key("\x03", "ctrl+c")
    assert matches_key("\x1b", "escape")
    assert matches_key("\r", "enter")
    assert matches_key("\t", "tab")
    assert matches_key("\x7f", "backspace")
    assert matches_key("\x1b[A", "up")
    assert matches_key("\x1b[B", "down")
    assert matches_key("\x1b[C", "right")
    assert matches_key("\x1b[D", "left")


def test_mock_terminal():
    """Test MockTerminal."""
    terminal = MockTerminal(80, 24)
    assert terminal.get_size() == (80, 24)

    terminal.queue_input("hello")
    assert terminal.read() == "h"
    assert terminal.read() == "e"
    assert terminal.read() == "l"
    assert terminal.read() == "l"
    assert terminal.read() == "o"
    assert terminal.read() is None

    terminal.write("test")
    assert "test" in terminal.get_output()

    terminal.hide_cursor()
    assert not terminal.cursor_visible

    terminal.show_cursor()
    assert terminal.cursor_visible

    terminal.enter_alternate_screen()
    assert terminal._in_alternate_screen

    terminal.exit_alternate_screen()
    assert not terminal._in_alternate_screen

    terminal.clear()
    assert "[CLEAR]" in terminal.get_output()

    terminal.clear_buffer()
    assert terminal.get_output() == ""


def test_overlay():
    """Test overlay system."""
    terminal = MockTerminal(80, 24)
    tui = TUI(terminal)

    tui.add_child(Text("Base content line 1"))
    tui.add_child(Text("Base content line 2"))

    # Show overlay
    options = OverlayOptions(
        width="50%",
        anchor="center",
    )
    handle = tui.show_overlay(Text("Overlay content"), options)
    assert tui.has_overlay()

    # Render and check output
    tui.render_frame()
    output = terminal.get_output()
    assert "Overlay content" in output

    # Hide overlay
    handle.hide()
    assert not tui.has_overlay()


def test_focusable():
    """Test Focusable interface."""
    assert not is_focusable(None)

    input_cmp = Input()
    assert is_focusable(input_cmp)

    terminal = MockTerminal(80, 24)
    tui = TUI(terminal)

    # Test setting focus
    tui.set_focus(input_cmp)
    assert input_cmp.focused

    tui.set_focus(None)
    assert not input_cmp.focused
