# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-02-27

### Fixed

- **Hardware cursor positioning with scrollback** — Cursor now positions correctly when content exceeds terminal height. Previously, the hardware cursor was placed at the absolute row position instead of the screen row position, causing typed characters to appear at wrong positions after content scrolled into scrollback buffer.

## [0.2.1] - 2025-02-27

### Changed

- **LLMS.md documentation** — Updated with scrollback mechanics, renderer internals, and cursor positioning details

## [0.2.0] - 2025-02-26

### Added

- **Automated type stub checks** — Pre-commit hook now verifies `.pyi` stubs match source code
- **Ruff per-file ignores** — Exclude E501 and I001 in generated stub files

### Changed

- **Type stubs regenerated** — All `.pyi` files updated to match current source

[0.2.0]: https://github.com/user/pypitui/releases/tag/v0.2.0

## [0.1.0] - 2025-02-26

### Overview

Initial release of PyPiTUI — a Python TUI library with differential rendering, ported from @mariozechner/pi-tui. Features a component-based architecture, scrollback buffer support, and seamless integration with Rich for complex layouts.

### Added

#### Core TUI Framework
- **Differential Rendering Engine** — Only redraws changed content for optimal performance (`feat: implement optimal differential rendering`)
- **Component-Based Architecture** — Base `Component` class with lifecycle methods (`mount`, `unmount`, `render`)
- **TUI Root Container** — Root container managing component tree and render loop
- **Input Handling** — Raw terminal input with escape sequence parsing for keyboard events
- **Scrollback Buffer Support** — Full scrollback with working area tracking, viewport positioning, and relative cursor movement

#### Components
- **Box** — Basic rectangular container with background color support
- **BorderedBox** — Box with intelligent content wrapping and title support with separator
- **Text** — Text rendering with ANSI color support
- **SelectList** — Interactive list with wrap-around navigation, search filtering, and theme integration

#### Terminal & Rendering
- **ANSI Escape Sequence Parser** — Full support for keyboard input including special keys
- **Terminal Resizing** — Proper handling of terminal resize events with screen clearing
- **Screen Management** — Screen switching with proper clearing to prevent artifacts
- **wcwidth Integration** — Accurate emoji and CJK character width calculation
- **Theme System** — Support for custom themes with bold/reset attributes

#### Rich Integration
- **Rich Component Wrapper** — Seamless integration with Rich library components
- **Theme-Aware Rendering** — Rich components respect the selected TUI theme
- **Rich Overlay Support** — Proper overlay compositing with ANSI reset code preservation

#### Demos & Examples
- **Ultimate Demo** — Comprehensive demo showcasing all features (34% size reduction while maintaining functionality)
- **Matrix Rain Demo** — Animated matrix rain with stable trails, mode toggle, FPS counter, green color mode, and help overlay
- **Streaming Demo** — Real-time data streaming with scrollback
- **Form Demo** — Input form with Tab navigation and Enter submission
- **Splash Screen** — Animated splash screen with emoji support and ASCII art

#### Developer Experience
- **CI/CD Workflows** — GitHub Actions for testing, linting, type checking, and PyPI trusted publishing
- **Code Quality Tools** — Ruff for linting/formatting, MyPy for type checking, pytest with coverage
- **Type Stubs** — Generated type stubs for mypy compatibility using stubgen
- **Documentation** — Comprehensive README, LLMS.md for AI assistants, AGENTS.md with guidelines
- **TODO Management** — Granular TODO.md tracking implementation phases

### Fixed

- **Screen Artifacts** — Force full redraw when switching screens to remove artifacts
- **Overlay Positioning** — Fixed overlay positioning and select list filtering issues
- **Matrix Rain Rendering** — Fixed first frame rendering and overlay close timing
- **Color Bleeding** — Fixed header color bleeding and background color width issues
- **Input Handling** — Fixed escape sequence handling by using file descriptor directly
- **Vertical Alignment** — Improved vertical alignment in headers and components

### Changed

- **Demo Refactoring** — 60% line reduction in ultimate demo while maintaining functionality
- **Box Component Usage** — Replaced hardcoded box characters with BorderedBox throughout demos
- **README Rewrite** — Professional OSS structure with banner, composition examples, and dev setup
- **Logo Updates** — Voxel snake logo with green bold styling

### Technical Details

- **Supported Python Versions:** 3.12, 3.13, 3.14
- **Dependencies:** wcwidth >= 0.2.13
- **Optional Dependencies:** Rich >= 13.0
- **Build System:** Hatchling
- **License:** MIT

[0.1.0]: https://github.com/user/pypitui/releases/tag/v0.1.0
