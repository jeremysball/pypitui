# Scrollback and Streaming Implementation TODO

> **PRD**: [prds/scrollback-and-streaming.md](prds/scrollback-and-streaming.md)

## Quick Reference

| Phase | Milestone | Status |
|-------|-----------|--------|
| 1 | Working Area Tracking | 🔲 Not Started |
| 2 | Synchronized Output | 🔲 Not Started |
| 3 | Relative Cursor Movement | 🔲 Not Started |
| 4 | Refactor render_frame() | 🔲 Not Started |
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
