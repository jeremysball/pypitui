# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

