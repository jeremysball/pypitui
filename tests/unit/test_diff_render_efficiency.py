"""Tests for differential rendering efficiency."""

from unittest.mock import MagicMock, patch
from io import BytesIO

from pypitui.mock_terminal import MockTerminal
from pypitui.tui import TUI
from pypitui.terminal import Terminal


class TestDiffRenderEfficiency:
    """Tests for escape sequence efficiency."""

    def test_escape_sequence_efficiency(self) -> None:
        """Append-only emits ≤20% sequences vs full redraw."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # Initial render of 20 lines
        initial_lines = [
            (i, f"hash{i}", f"Line {i} content here")
            for i in range(20)
        ]
        tui._output_diff(initial_lines, 80)
        full_redraw_escapes = mock_term.get_escape_count()

        # Reset counters
        mock_term.reset_counts()

        # Append 5 more lines (lines 20-24)
        appended_lines = [
            (i, f"hash{i}", f"Line {i} content here")
            for i in range(25)
        ]
        tui._output_diff(appended_lines, 80)
        append_escapes = mock_term.get_escape_count()

        # Append should use ≤20% of full redraw escapes
        # (only cursor positioning for new lines vs all lines)
        efficiency_ratio = append_escapes / max(full_redraw_escapes, 1)
        assert efficiency_ratio <= 0.20, (
            f"Append used {append_escapes} escapes, "
            f"full redraw used {full_redraw_escapes}, "
            f"ratio {efficiency_ratio:.2%} > 20%"
        )
