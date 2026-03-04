# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-03-03

### Fixed

- **Critical: Differential rendering now compares screen positions, not content indices**
  - Previously compared content at same index (e.g., `prev[134]` vs `curr[134]`)
  - When viewport shifted (content grew/shrank), same content moved to different screen positions
  - Old content stayed on screen because comparison said "no change"
  - Now tracks `_first_visible_row_previous` to detect viewport shifts
  - When viewport shifts, all visible rows are redrawn

### Changed

- `_render_changed_lines` uses absolute positioning (`\x1b[row;1H`) instead of relative cursor movement
- Removed `_handle_content_growth` function (no longer needed with new approach)
- Removed `_emitted_scrollback_lines` and `_anchor_top` state variables
- Removed `clear_on_shrink` parameter from `TUI.__init__` (handled in `_render_changed_lines` now)
- `request_render(force=True)` now also resets `_first_visible_row_previous`

### Removed

- Invalidation system (Component.invalidate, TUI.invalidate_component) - no longer needed with screen-based comparison

## [0.3.0] - 2025-03-01

### Added

- **Component-aware invalidation with parent references** - Targeted invalidation that clears only a component's lines instead of full redraw
  - `Component._parent` attribute for tracking parent container
  - `Component.invalidate()` method that clears local cache and bubbles up
  - `Component._child_invalidated(child)` method for bubble-up notification
  - `TUI.invalidate_component(component)` for direct targeted invalidation
  - `TUI._component_positions` dict tracking component line ranges during render
  - Recursive position tracking for nested containers
  - Overlay component parent wiring for invalidation bubbling

### Changed

- `Container.add_child()` now wires `component._parent = self`
- `Container.remove_child()` now clears `component._parent = None`
- `Container.clear()` now clears all children's parent references
- `TUI.show_overlay()` now sets overlay component's parent to TUI
- `TUI.hide_overlay()` now clears overlay component's parent reference

## [0.2.5] - 2025-02-28

### Fixed

- Scrollback rendering bug where top border lines were missing when content grew
- `_handle_content_growth` now renders scrollback lines before emitting newlines

## [0.2.4] - 2025-02-26

### Fixed

- Scrollback explosion bug - lines no longer emitted on every frame redraw
- Added `_emitted_scrollback_lines` counter to track already-emitted lines

## [0.2.0] - 2025-02-23

### Added

- Initial release with differential rendering
- Component model (Text, Input, SelectList, BorderedBox, Container)
- Overlay support with OverlayOptions
- Keyboard handling with Kitty protocol support
- Scrollback buffer support
- Rich integration for markdown and tables

