# Scrollback and Streaming Implementation TODO

> **PRD**: [prds/scrollback-and-streaming.md](prds/scrollback-and-streaming.md)

## Current: Milestone 5 - Overlay Viewport Positioning

**Concept**: Overlays work correctly with scrolled content.

### Tasks
- [ ] Add `viewport_top` parameter to `_composite_overlays()`
- [ ] Convert overlay content row to screen row
- [ ] Only render overlay if visible
- [ ] Update overlay position calculation for anchors
- [ ] Write test: overlay positioning with various scroll states
- [ ] Write test: overlay hidden when scrolled out of view

---

## Progress

| Phase | Milestone | Status |
|-------|-----------|--------|
| 1 | Working Area Tracking | ✅ Complete |
| 2 | Synchronized Output | ✅ Complete |
| 3 | Relative Cursor Movement | ✅ Complete |
| 4 | Refactor render_frame() | ✅ Complete |
| 5 | Overlay Viewport Positioning | 🔄 In Progress |
| 6 | Remove Height Limiting | 🔲 Not Started |
| 7 | Integration Testing | 🔲 Not Started |
| 8 | Documentation | 🔲 Not Started |

## Escape Sequences

| Sequence | Meaning |
|----------|---------|
| `\x1b[nA` | Move cursor up n lines |
| `\x1b[nB` | Move cursor down n lines |
| `\x1b[?2026h` | Begin synchronized output |
| `\x1b[?2026l` | End synchronized output |
| `\r\x1b[2K` | CR + clear line |

See [PRD](prds/scrollback-and-streaming.md) for detailed tasks per milestone.
