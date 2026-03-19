"""Integration tests for differential rendering pipeline."""

from pypitui.mock_terminal import MockTerminal
from pypitui.tui import TUI


class TestDifferentialRenderingPipeline:
    """Integration tests for full differential rendering."""

    def test_initial_full_render(self) -> None:
        """First render outputs all lines."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        lines = [
            (0, "hash0", "Line 0"),
            (1, "hash1", "Line 1"),
            (2, "hash2", "Line 2"),
        ]
        tui._output_diff(lines, 80)

        output = mock_term.get_output()
        assert b"Line 0" in output
        assert b"Line 1" in output
        assert b"Line 2" in output

    def test_no_output_when_nothing_changes(self) -> None:
        """Render with no changes produces minimal output."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # First render
        lines = [
            (0, "hash0", "Line 0"),
            (1, "hash1", "Line 1"),
        ]
        tui._output_diff(lines, 80)

        # Reset and render same content
        mock_term.reset_counts()
        tui._output_diff(lines, 80)

        # Should have minimal or no escape sequences
        assert mock_term.get_escape_count() == 0

    def test_single_line_change(self) -> None:
        """Changing one line only outputs that line."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # First render
        lines1 = [
            (0, "hash0", "Line 0"),
            (1, "hash1", "Line 1"),
            (2, "hash2", "Line 2"),
        ]
        tui._output_diff(lines1, 80)

        # Reset counters
        mock_term.reset_counts()

        # Change middle line only
        lines2 = [
            (0, "hash0", "Line 0"),  # unchanged
            (1, "new_hash", "CHANGED"),  # changed
            (2, "hash2", "Line 2"),  # unchanged
        ]
        tui._output_diff(lines2, 80)

        output = mock_term.get_output()
        # Should only contain the changed line
        assert b"CHANGED" in output
        assert b"Line 0" not in output
        assert b"Line 2" not in output

    def test_append_new_lines(self) -> None:
        """Appending lines uses optimized path."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # Initial render
        lines1 = [
            (0, "hash0", "Line 0"),
            (1, "hash1", "Line 1"),
        ]
        tui._output_diff(lines1, 80)
        initial_escapes = mock_term.get_escape_count()

        # Reset
        mock_term.reset_counts()

        # Append new lines
        lines2 = [
            (0, "hash0", "Line 0"),
            (1, "hash1", "Line 1"),
            (2, "hash2", "Line 2"),  # new
            (3, "hash3", "Line 3"),  # new
        ]
        tui._output_diff(lines2, 80)
        append_escapes = mock_term.get_escape_count()

        # Append should use fewer escapes than initial render
        # (uses \r\n instead of cursor positioning for each line)
        assert append_escapes < initial_escapes

        output = mock_term.get_output()
        assert b"Line 2" in output
        assert b"Line 3" in output

    def test_edit_in_middle_not_append(self) -> None:
        """Editing middle line uses standard diff, not append."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # Initial render
        lines1 = [
            (0, "hash0", "Line 0"),
            (1, "hash1", "Line 1"),
            (2, "hash2", "Line 2"),
        ]
        tui._output_diff(lines1, 80)

        # Reset
        mock_term.reset_counts()

        # Edit middle line (not append)
        lines2 = [
            (0, "hash0", "Line 0"),
            (1, "new_hash", "CHANGED"),  # edited
            (2, "hash2", "Line 2"),
        ]
        tui._output_diff(lines2, 80)

        # Should use cursor positioning (more escapes than append)
        output = mock_term.get_output()
        assert b"CHANGED" in output
        # Cursor positioning used
        assert b"\x1b[" in output

    def test_content_hash_tracking(self) -> None:
        """TUI tracks content hashes for diffing."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        lines = [
            (0, "abc123", "Content"),
            (1, "def456", "More content"),
        ]
        tui._output_diff(lines, 80)

        # Check hashes stored
        assert tui._previous_lines[0] == "abc123"
        assert tui._previous_lines[1] == "def456"

    def test_max_lines_rendered_tracking(self) -> None:
        """TUI tracks maximum lines ever rendered."""
        mock_term = MockTerminal(width=80, height=24)
        tui = TUI(mock_term)

        # Render 5 lines
        lines1 = [(i, f"hash{i}", f"Line {i}") for i in range(5)]
        tui._output_diff(lines1, 80)
        assert tui._max_lines_rendered == 5

        # Render 3 lines (shrink)
        lines2 = [(i, f"hash{i}", f"Line {i}") for i in range(3)]
        tui._output_diff(lines2, 80)
        # Max should still be 5
        assert tui._max_lines_rendered == 5

        # Render 10 lines (grow)
        lines3 = [(i, f"hash{i}", f"Line {i}") for i in range(10)]
        tui._output_diff(lines3, 80)
        # Max should update to 10
        assert tui._max_lines_rendered == 10
