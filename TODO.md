# Scrollback and Streaming Implementation TODO

> **PRD**: [prds/scrollback-and-streaming.md](prds/scrollback-and-streaming.md)

## Current: Milestone 4 - Refactor render_frame()

**Concept**: Core rendering uses relative positioning with batched output.

### Tasks
- [ ] Create output buffer string at start of `render_frame()`
- [ ] Replace absolute `move_cursor(i, 0)` loop with relative movement
- [ ] Handle content shrinkage (clear orphaned lines)
- [ ] Handle content growth (scroll terminal, add newlines)
- [ ] Single `terminal.write(buffer)` at end
- [ ] Initialize `_hardware_cursor_row` at end of render
- [ ] Write test: differential rendering with relative positioning
- [ ] Write test: content growth triggers scroll
- [ ] Write test: content shrinkage clears orphaned lines

---

## Progress

| Phase | Milestone | Status |
|-------|-----------|--------|
| 1 | Working Area Tracking | ✅ Complete |
| 2 | Synchronized Output | ✅ Complete |
| 3 | Relative Cursor Movement | ✅ Complete |
| 4 | Refactor render_frame() | 🔄 In Progress |
| 5 | Overlay Viewport Positioning | 🔲 Not Started |
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
