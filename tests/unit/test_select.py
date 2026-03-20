"""Tests for SelectList component."""

from pypitui.component import Size
from pypitui.components.select import SelectItem, SelectList


class TestSelectItem:
    """Tests for SelectItem dataclass."""

    def test_selectitem_creation(self) -> None:
        """Id and label stored."""
        item = SelectItem(id="option1", label="Option 1")

        assert item.id == "option1"
        assert item.label == "Option 1"


class TestSelectListMeasure:
    """Tests for SelectList.measure()."""

    def test_selectlist_measure_respects_max_visible(self) -> None:
        """Height = min(len(items), max_visible)."""
        items = [
            SelectItem(id="1", label="One"),
            SelectItem(id="2", label="Two"),
            SelectItem(id="3", label="Three"),
        ]
        select_list = SelectList(items=items, max_visible=2)
        size = select_list.measure(80, 24)

        assert size.height == 2
        assert size.width == 80

    def test_selectlist_measure_fits_content_when_less_than_max(self) -> None:
        """Height equals item count when less than max_visible."""
        items = [SelectItem(id="1", label="One")]
        select_list = SelectList(items=items, max_visible=5)
        size = select_list.measure(80, 24)

        assert size.height == 1


class TestSelectListRender:
    """Tests for SelectList.render()."""

    def test_selectlist_render_shows_items(self) -> None:
        """All visible items rendered."""
        items = [
            SelectItem(id="1", label="One"),
            SelectItem(id="2", label="Two"),
        ]
        select_list = SelectList(items=items, max_visible=5)

        lines = select_list.render(80)

        assert len(lines) == 2
        assert "One" in lines[0].content
        assert "Two" in lines[1].content

    def test_selectlist_render_highlights_selected(self) -> None:
        """Selected item has different style."""
        items = [
            SelectItem(id="1", label="One"),
            SelectItem(id="2", label="Two"),
        ]
        select_list = SelectList(items=items, max_visible=5)
        select_list._selected_index = 1

        lines = select_list.render(80)

        # Second line should have highlight styling (more style spans)
        assert len(lines[1].styles) > 0

    def test_selectlist_render_truncates_long_labels(self) -> None:
        """Long labels truncated to width."""
        items = [SelectItem(id="1", label="A" * 100)]
        select_list = SelectList(items=items, max_visible=5)

        lines = select_list.render(20)

        assert len(lines[0].content) <= 20


class TestSelectListHandleInput:
    """Tests for SelectList.handle_input()."""

    def test_selectlist_handle_down_moves_selection(self) -> None:
        """Selection index increments on Down."""
        items = [
            SelectItem(id="1", label="One"),
            SelectItem(id="2", label="Two"),
        ]
        select_list = SelectList(items=items, max_visible=5)

        consumed = select_list.handle_input(b"\x1b[B")  # CSI B = Down

        assert consumed is True
        assert select_list._selected_index == 1

    def test_selectlist_handle_up_moves_selection(self) -> None:
        """Selection index decrements on Up."""
        items = [
            SelectItem(id="1", label="One"),
            SelectItem(id="2", label="Two"),
        ]
        select_list = SelectList(items=items, max_visible=5)
        select_list._selected_index = 1

        consumed = select_list.handle_input(b"\x1b[A")  # CSI A = Up

        assert consumed is True
        assert select_list._selected_index == 0

    def test_selectlist_wraps_at_bottom(self) -> None:
        """Down at bottom wraps to top."""
        items = [
            SelectItem(id="1", label="One"),
            SelectItem(id="2", label="Two"),
        ]
        select_list = SelectList(items=items, max_visible=5)
        select_list._selected_index = 1

        select_list.handle_input(b"\x1b[B")  # Down

        assert select_list._selected_index == 0

    def test_selectlist_wraps_at_top(self) -> None:
        """Up at top wraps to bottom."""
        items = [
            SelectItem(id="1", label="One"),
            SelectItem(id="2", label="Two"),
        ]
        select_list = SelectList(items=items, max_visible=5)
        select_list._selected_index = 0

        select_list.handle_input(b"\x1b[A")  # Up

        assert select_list._selected_index == 1

    def test_selectlist_handle_input_returns_bool(self) -> None:
        """Returns True when consuming input."""
        items = [SelectItem(id="1", label="One")]
        select_list = SelectList(items=items, max_visible=5)

        result = select_list.handle_input(b"\x1b[B")  # Down

        assert isinstance(result, bool)
        assert result is True

    def test_selectlist_ignores_unhandled_input(self) -> None:
        """Returns False for unhandled input."""
        items = [SelectItem(id="1", label="One")]
        select_list = SelectList(items=items, max_visible=5)

        result = select_list.handle_input(b"x")

        assert result is False


class TestSelectListOnSelect:
    """Tests for SelectList.on_select callback."""

    def test_selectlist_on_select_callback(self) -> None:
        """Enter triggers on_select with selected item id."""
        selected_id = None

        def on_select(item_id: str) -> None:
            nonlocal selected_id
            selected_id = item_id

        items = [
            SelectItem(id="option1", label="Option 1"),
            SelectItem(id="option2", label="Option 2"),
        ]
        select_list = SelectList(items=items, max_visible=5, on_select=on_select)
        select_list._selected_index = 1

        select_list.handle_input(b"\r")  # Enter

        assert selected_id == "option2"

    def test_selectlist_on_select_without_callback(self) -> None:
        """Enter without callback does nothing."""
        items = [SelectItem(id="1", label="One")]
        select_list = SelectList(items=items, max_visible=5)

        # Should not raise
        select_list.handle_input(b"\r")
