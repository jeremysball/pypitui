"""Tests for SelectList component - ported from pi-tui."""

import pytest
from pypitui import SelectList, SelectItem, SelectListTheme


class TestSelectList:
    """Tests for SelectList component."""

    @pytest.fixture
    def theme(self):
        """Create a test theme."""
        return SelectListTheme(
            selected_prefix=lambda s: s,
            selected_text=lambda s: s,
            description=lambda s: s,
            scroll_info=lambda s: s,
            no_match=lambda s: s,
        )

    def test_renders_items(self, theme):
        """SelectList renders items correctly."""
        items = [
            SelectItem(value="a", label="Option A"),
            SelectItem(value="b", label="Option B"),
        ]
        select_list = SelectList(items, 5, theme)
        lines = select_list.render(50)
        assert len(lines) == 2
        assert "> Option A" in lines[0]
        assert "Option B" in lines[1]

    def test_selection_highlight(self, theme):
        """First item is selected by default."""
        items = [
            SelectItem(value="a", label="Option A"),
            SelectItem(value="b", label="Option B"),
        ]
        select_list = SelectList(items, 5, theme)
        
        # First item should have selection marker
        lines = select_list.render(50)
        assert lines[0].startswith(">")
        assert ">" not in lines[1]  # Second item not selected

    def test_navigation(self, theme):
        """Can navigate with up/down keys."""
        from pypitui.keys import Key
        
        items = [
            SelectItem(value="a", label="Option A"),
            SelectItem(value="b", label="Option B"),
            SelectItem(value="c", label="Option C"),
        ]
        select_list = SelectList(items, 5, theme)
        
        # Move down
        select_list.handle_input("\x1b[B")  # down
        lines = select_list.render(50)
        assert ">" not in lines[0]
        assert ">" in lines[1]
        
        # Move up
        select_list.handle_input("\x1b[A")  # up
        lines = select_list.render(50)
        assert ">" in lines[0]
        assert ">" not in lines[1]

    def test_description_display(self, theme):
        """Shows description if present."""
        items = [
            SelectItem(value="a", label="Option A", description="First option"),
        ]
        select_list = SelectList(items, 5, theme)
        lines = select_list.render(80)
        assert "First option" in lines[0]

    def test_multiline_description_normalized(self, theme):
        """Multiline descriptions are normalized to single line."""
        items = [
            SelectItem(
                value="test",
                label="test",
                description="Line one\nLine two\nLine three",
            ),
        ]
        select_list = SelectList(items, 5, theme)
        lines = select_list.render(100)
        
        assert len(lines) == 1
        assert "\n" not in lines[0]
        assert "Line one Line two Line three" in lines[0]

    def test_filter(self, theme):
        """Can filter items."""
        items = [
            SelectItem(value="a", label="Apple"),
            SelectItem(value="b", label="Banana"),
            SelectItem(value="c", label="Cherry"),
        ]
        select_list = SelectList(items, 5, theme)
        
        select_list.set_filter("ban")
        lines = select_list.render(50)
        
        assert len(lines) == 1
        assert "Banana" in lines[0]

    def test_no_match(self, theme):
        """Shows no match message when filter has no results."""
        items = [
            SelectItem(value="a", label="Apple"),
        ]
        select_list = SelectList(items, 5, theme)
        
        select_list.set_filter("xyz")
        lines = select_list.render(50)
        
        assert "No matches" in lines[0]

    def test_on_select_callback(self, theme):
        """on_select callback is called on Enter."""
        from pypitui.keys import Key
        
        items = [
            SelectItem(value="a", label="Option A"),
        ]
        select_list = SelectList(items, 5, theme)
        
        selected_value = None
        
        def on_select(item):
            nonlocal selected_value
            selected_value = item.value
        
        select_list.on_select = on_select
        select_list.handle_input("\r")  # Enter
        
        assert selected_value == "a"

    def test_on_cancel_callback(self, theme):
        """on_cancel callback is called on Escape."""
        items = [
            SelectItem(value="a", label="Option A"),
        ]
        select_list = SelectList(items, 5, theme)
        
        cancelled = False
        
        def on_cancel():
            nonlocal cancelled
            cancelled = True
        
        select_list.on_cancel = on_cancel
        select_list.handle_input("\x1b")  # Escape
        
        assert cancelled is True

    def test_scroll_info(self, theme):
        """Shows scroll info when items exceed max visible."""
        items = [SelectItem(value=str(i), label=f"Item {i}") for i in range(10)]
        select_list = SelectList(items, 3, theme)
        
        lines = select_list.render(50)
        
        # Should show scroll info
        assert any("of 10" in line for line in lines)

    def test_get_selected_item(self, theme):
        """get_selected_item returns current selection."""
        items = [
            SelectItem(value="a", label="Option A"),
            SelectItem(value="b", label="Option B"),
        ]
        select_list = SelectList(items, 5, theme)
        
        selected = select_list.get_selected_item()
        assert selected is not None
        assert selected.value == "a"
        
        # Move to second item
        select_list.handle_input("\x1b[B")
        selected = select_list.get_selected_item()
        assert selected is not None
        assert selected.value == "b"


class TestSelectListFiltering:
    """Tests for SelectList type-to-filter functionality."""

    @pytest.fixture
    def theme(self):
        """Create a test theme."""
        return SelectListTheme(
            selected_prefix=lambda s: s,
            selected_text=lambda s: s,
            description=lambda s: s,
            scroll_info=lambda s: s,
            no_match=lambda s: s,
        )

    def test_typing_filters_items(self, theme):
        """Typing characters filters the list."""
        items = [
            SelectItem(value="a", label="Apple"),
            SelectItem(value="b", label="Banana"),
            SelectItem(value="c", label="Cherry"),
        ]
        select_list = SelectList(items, 5, theme)
        
        # Type 'b' to filter
        select_list.handle_input("b")
        lines = select_list.render(50)
        
        assert len(lines) == 1
        assert "Banana" in lines[0]

    def test_typing_multiple_chars(self, theme):
        """Typing multiple characters refines filter."""
        items = [
            SelectItem(value="a", label="Apple"),
            SelectItem(value="ap", label="Appetizer"),
            SelectItem(value="b", label="Banana"),
        ]
        select_list = SelectList(items, 5, theme)
        
        # Type 'ap' to filter
        select_list.handle_input("a")
        select_list.handle_input("p")
        lines = select_list.render(50)
        
        # Should show Apple and Appetizer
        assert len(lines) == 2

    def test_backspace_removes_filter_char(self, theme):
        """Backspace removes last filter character."""
        items = [
            SelectItem(value="a", label="Apple"),
            SelectItem(value="b", label="Banana"),
            SelectItem(value="c", label="Cherry"),
        ]
        select_list = SelectList(items, 5, theme)
        
        # Type 'ba' then backspace
        select_list.handle_input("b")
        select_list.handle_input("a")
        select_list.handle_input("\x7f")  # backspace
        
        # Filter should now be just 'b'
        lines = select_list.render(50)
        assert "Banana" in lines[0]

    def test_escape_clears_filter(self, theme):
        """Escape clears the filter before triggering cancel."""
        items = [
            SelectItem(value="a", label="Apple"),
            SelectItem(value="b", label="Banana"),
        ]
        select_list = SelectList(items, 5, theme)
        
        # Type to filter
        select_list.handle_input("b")
        lines = select_list.render(50)
        assert len(lines) == 1
        
        # Escape should clear filter
        select_list.handle_input("\x1b")
        lines = select_list.render(50)
        assert len(lines) == 2  # All items visible again

    def test_escape_calls_cancel_when_no_filter(self, theme):
        """Escape calls on_cancel when there's no filter."""
        items = [
            SelectItem(value="a", label="Option A"),
        ]
        select_list = SelectList(items, 5, theme)
        
        cancelled = False
        
        def on_cancel():
            nonlocal cancelled
            cancelled = True
        
        select_list.on_cancel = on_cancel
        select_list.handle_input("\x1b")  # Escape with no filter
        
        assert cancelled is True

    def test_filter_is_case_insensitive(self, theme):
        """Filter matches regardless of case."""
        items = [
            SelectItem(value="a", label="Apple"),
            SelectItem(value="b", label="Banana"),
        ]
        select_list = SelectList(items, 5, theme)
        
        select_list.handle_input("B")  # Uppercase
        lines = select_list.render(50)
        
        assert "Banana" in lines[0]
        assert "Apple" not in lines[0]

    def test_filter_resets_selection(self, theme):
        """Filter resets selection to first matching item."""
        items = [
            SelectItem(value="a", label="Apple"),
            SelectItem(value="ap", label="Appetizer"),
        ]
        select_list = SelectList(items, 5, theme)
        
        # Move selection to second item
        select_list.handle_input("\x1b[B")  # down
        
        # Filter should reset selection
        select_list.handle_input("a")
        selected = select_list.get_selected_item()
        assert selected.value == "a"  # First matching item
