# PyPiTUI Agent Guidelines

---

## ⛔ PRE-FLIGHT CHECK — DO THIS FIRST

**STOP.** Before responding to any user message or command, you **MUST**:

1. Read the **writing-clearly-and-concisely** skill (`.pi/skills/writing-clearly-and-concisely/SKILL.md`)
2. Read the **ntfy** skill (`.pi/skills/ntfy/SKILL.md`)
3. Confirm completion in your first response: "✅ Skills loaded"

**No exceptions.** This applies to:
- The first message of every conversation
- Simple questions, complex tasks, everything

If you skip this step, you have failed the pre-flight check.

### Why? 📝
- **Writing skill**: Strunk's rules = clear, concise writing, prevents AI fluff
- **ntfy skill**: Push notifications for long-running tasks and input requests

### Don't skip this. Seriously. 👀

---

## 📱 Notify on Long-Running Tasks — MANDATORY

**ALWAYS** send an ntfy notification when:
- Long-running tasks complete
- User input required
- Workflow milestones (PR created/merged)
- Errors needing attention

```bash
# Simple notification
curl -s -d "Task complete" ntfy.sh/pi-agent-prometheus

# High priority for input needed
curl -s -H "Priority: high" -d "Input needed" ntfy.sh/pi-agent-prometheus
```

**Don't notify for:** simple file reads, intermediate steps, quick acknowledgments.

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

## Testing: DO NOT MOCK

**Mocking is a last resort.** Prefer:
- Real file systems (use temp directories)
- Real network calls (use test servers/containers)
- Real databases (use test instances)

**Only mock when:**
- External services you cannot control
- Non-deterministic behavior (time, randomness)
- Extremely slow operations

## Use tmux for CLI/TUI Testing

For E2E testing of interactive or visual CLI applications:

```bash
mkdir -p /tmp/pi-tmux && cp .pi/skills/tmux-tape/tmux_tool.py /tmp/pi-tmux/
cd /tmp/pi-tmux && uv run python script.py
```

```python
from tmux_tool import TerminalSession

with TerminalSession("myapp", port=7681) as s:
    s.send("myapp")
    s.send_key("Enter")
    s.sleep(3)  # Wait for startup

    result = s.capture("screenshot.png")
    assert "Expected text" in result["text"]
```

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
