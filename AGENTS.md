# PyPiTUI Agent Guidelines

---

## ⚠️ 🚨 🔔 LOAD THIS SKILL FIRST — EVERY CONVERSATION — NO EXCEPTIONS 🔔 🚨 ⚠️

```
/skill:writing-clearly-and-concisely
```

### Why? 📝
- Strunk's rules = clear, concise writing
- Prevents AI fluff and corporate-speak
- Better commit messages, docs, and explanations

### When? 🕐
- ✅ Start of EVERY conversation
- ✅ Before writing ANY prose humans will read
- ✅ BEFORE you start coding or planning

### Don't skip this. Seriously. 👀

---

## Check `.agents/` Folders for Utilities

Always check for `.agents/` folders in the project root. These contain:
- E2E test scripts using tmux
- Automation utilities
- Agent-specific tooling

Example: `.agents/test_ultimate_demo.py` runs automated tests on the demo.

## Generating Type Stubs

When adding type stubs to this library, use `stubgen` from mypy instead of writing them manually:

```bash
uv run stubgen src/pypitui -o src/pypitui/stubs
```

Then refine the generated stubs as needed. Manual stub creation is error-prone and may miss edge cases that stubgen handles automatically.

## Critical: TUI Instance Reuse

**Never create new TUI instances when switching screens.** Always reuse the same TUI instance.

### Correct Pattern
```python
def switch_screen(self):
    self.tui.clear()  # Remove children, preserve _previous_lines
    self.tui.add_child(Text("New content", 0, 0))
```

### Wrong Pattern
```python
def switch_screen(self):
    self.tui = TUI(terminal)  # ❌ Loses _previous_lines, breaks clearing
    self.tui.add_child(Text("New content", 0, 0))
```

### Why This Matters
The TUI uses `_previous_lines` for differential rendering. Creating a new TUI loses this state, causing ghost content and uncleared lines.

### Reference
See `examples/demo.py` for the correct implementation using `_clear_screen()`.

## Decompose Your Tasks Into a GRANULAR, TOPICAL TODO.md 
- Ensure:
  - TODO.md is kept up to date via checkboxes \[ \]
  - Ensure TODO.md is kept UP TO DATE with ANY new design decisions
