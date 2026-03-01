"""Test for scrollback explosion bug fix."""
from pypitui import TUI, Container, Text
from pypitui.terminal import MockTerminal


def test_scrollback_lines_emitted_once():
    """Verify scrollback lines are only emitted once, not on every frame."""
    terminal = MockTerminal(cols=40, rows=5)
    tui = TUI(terminal)

    # Add enough content to overflow terminal height
    container = Container()
    for i in range(10):
        container.add_child(Text(f"Line {i}"))
    tui.add_child(container)

    tui.start()

    # First render - should emit scrollback newlines
    tui.render_frame()
    first_output = terminal.get_output()
    scrollback_count_1 = first_output.count("\r\n")

    # Second render (no change) - should NOT emit more scrollback newlines
    terminal.clear_buffer()
    tui.render_frame()
    second_output = terminal.get_output()
    scrollback_count_2 = second_output.count("\r\n")

    tui.stop()

    # The second render should have significantly fewer newlines
    # because scrollback was already emitted
    assert scrollback_count_2 < scrollback_count_1, (
        f"Second render emitted {scrollback_count_2} newlines, "
        f"expected less than {scrollback_count_1}. "
        "Scrollback lines are being re-emitted on every frame!"
    )


def test_scrollback_counter_tracks_correctly():
    """Verify _emitted_scrollback_lines counter increments correctly."""
    terminal = MockTerminal(cols=40, rows=5)
    tui = TUI(terminal)

    assert tui._emitted_scrollback_lines == 0

    # Add 7 lines (2 scrollback lines with height 5)
    container = Container()
    for i in range(7):
        container.add_child(Text(f"Line {i}"))
    tui.add_child(container)

    tui.start()
    tui.render_frame()
    tui.stop()

    # Text has default padding_y=1, so each Text renders as 3 lines
    # 7 Text components = 21 lines total
    # With height 5: 21 - 5 = 16 scrollback lines expected
    assert tui._emitted_scrollback_lines == 16

    # Render again - counter should stay at 16
    tui.start()
    tui.render_frame()
    tui.stop()
    assert tui._emitted_scrollback_lines == 16


def test_invalidate_resets_scrollback_counter():
    """Verify invalidate() resets the scrollback counter."""
    terminal = MockTerminal(cols=40, rows=5)
    tui = TUI(terminal)

    # Add content and render
    container = Container()
    for i in range(7):
        container.add_child(Text(f"Line {i}"))
    tui.add_child(container)

    tui.start()
    tui.render_frame()
    tui.stop()

    # Text has padding, so scrollback lines > 0
    assert tui._emitted_scrollback_lines > 0

    # Invalidate should reset counter
    tui.invalidate()
    assert tui._emitted_scrollback_lines == 0


def test_content_growth_emits_only_new_scrollback():
    """When content grows, only new scrollback lines are emitted."""
    terminal = MockTerminal(cols=40, rows=5)
    tui = TUI(terminal)

    tui.start()

    # Start with 7 lines of content
    container = Container()
    for i in range(7):
        container.add_child(Text(f"Line {i}"))
    tui.add_child(container)

    tui.render_frame()
    first_scrollback = tui._emitted_scrollback_lines
    terminal.clear_buffer()

    # Add more content
    for i in range(7, 10):
        container.add_child(Text(f"Line {i}"))

    tui.render_frame()
    second_scrollback = tui._emitted_scrollback_lines

    tui.stop()

    # The counter should have increased, but not reset
    assert second_scrollback > first_scrollback


def test_no_scrollback_when_content_fits():
    """When content fits in terminal, no scrollback is emitted."""
    terminal = MockTerminal(cols=40, rows=20)
    tui = TUI(terminal)

    # Add content that fits (Text with padding_y=1 renders 3 lines each)
    container = Container()
    for i in range(3):
        container.add_child(Text(f"Line {i}"))
    tui.add_child(container)

    tui.start()
    tui.render_frame()
    tui.stop()

    # No scrollback lines since content fits
    assert tui._emitted_scrollback_lines == 0
