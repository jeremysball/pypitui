"""Tests for public API exports."""


class TestPublicAPI:
    """Tests that all public API exports are importable."""

    def test_import_all_exports(self) -> None:
        """All __all__ exports can be imported."""
        # This test imports everything from pypitui
        from pypitui import (  # noqa: F401
            BorderedBox,
            Component,
            Container,
            Input,
            Key,
            LineOverflowError,
            MouseEvent,
            Overlay,
            OverlayPosition,
            Rect,
            RenderedLine,
            SelectItem,
            SelectList,
            Size,
            StyleSpan,
            TUI,
            Terminal,
            Text,
            detect_color_support,
            matches_key,
            parse_key,
            parse_mouse,
            slice_by_width,
            truncate_to_width,
            wcwidth,
        )

    def test_tui_import(self) -> None:
        """TUI can be imported directly."""
        from pypitui import TUI

        assert TUI is not None

    def test_container_import(self) -> None:
        """Container can be imported directly."""
        from pypitui import Container

        assert Container is not None

    def test_text_import(self) -> None:
        """Text can be imported directly."""
        from pypitui import Text

        assert Text is not None

    def test_input_import(self) -> None:
        """Input can be imported directly."""
        from pypitui import Input

        assert Input is not None

    def test_all_list_matches_exports(self) -> None:
        """__all__ matches actual exports."""
        import pypitui

        # Everything in __all__ should be accessible
        for name in pypitui.__all__:
            assert hasattr(pypitui, name), f"{name} not in pypitui module"

    def test_version_exported(self) -> None:
        """__version__ is exported."""
        from pypitui import __version__

        assert isinstance(__version__, str)
        assert len(__version__.split(".")) >= 2
