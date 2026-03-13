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

## Type Safety: mypy Strict Mode

**All code must pass mypy strict mode.** No exceptions.

```bash
# Check type safety
uv run mypy --strict src/
```

Configuration in `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.12"
strict = true
disallow_any_generics = false
warn_return_any = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
show_error_codes = true
```

**Requirements:**
- All functions must have type annotations
- All return types must be explicit
- No `Any` types without justification
- All public APIs must be typed

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

---

## 🚨 CRITICAL: ALWAYS Clean Up - No Exceptions

**IT DOES NOT MATTER who created the mess.**

Whether you wrote the code or found it broken:
- **YOU ARE RESPONSIBLE** for leaving the codebase cleaner than you found it
- **YOU MUST** fix issues in code you touch
- **NO EXCUSES** about "someone else's code"

### Absolute Rules:

1. **If you touch it, you fix it** - No exceptions
2. **Pre-commit failing? FIX IT.** Don't bypass it
3. **CI failing? FIX IT.** Don't ignore it
4. **Legacy code with issues?** Fix it if you modified any part of it
5. **Broken tests?** Fix them or delete them - never leave them failing

### Who Created This Does NOT Matter:

❌ **WRONG:** "I didn't write this broken code"
❌ **WRONG:** "This was already failing before I started"
❌ **WRONG:** "I'll just commit my changes and leave the mess"

✅ **RIGHT:** "The code I touched now has issues - I will fix them"
✅ **RIGHT:** "I see failing tests - I will make them pass"
✅ **RIGHT:** "Pre-commit is failing on my changes - I will clean them up"

### Your Responsibility:

```bash
# Before committing:
pre-commit run --all-files

# If anything fails:
# 1. Fix it
# 2. Re-run pre-commit
# 3. Only commit when green
```

**THERE IS NO SITUATION WHERE IT IS ACCEPTABLE TO COMMIT BROKEN CODE.**

---

## 🚨 CRITICAL: NEVER Commit With Failing Pre-Commit

**UNDER NO CIRCUMSTANCES** may you commit code while pre-commit hooks are failing.

### Absolute Rules:

1. **NEVER use `--no-verify`** to bypass pre-commit hooks
2. **NEVER commit** when ruff, mypy, or tests are failing
3. **NEVER merge** a PR that has failing CI checks
4. **NEVER force-push** to override failing checks

### Pre-Commit Must Pass:

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Or with uv
uv run pre-commit run --all-files
```

**All checks must pass:**
- ✅ Ruff linting
- ✅ Ruff formatting
- ✅ mypy strict mode
- ✅ Tests

### If Pre-Commit Fails:

1. **STOP** - Do not commit
2. **Fix** the issues that pre-commit identified
3. **Re-run** pre-commit to verify fixes
4. **Only then** commit the changes

### Consequences of Bypassing:

- Broken code enters the repository
- CI/CD pipelines fail
- Other developers are blocked
- Loss of trust in the codebase
- **THIS IS NEVER ACCEPTABLE**

---

## 🚨 CRITICAL: NEVER Merge Failing PRs

**ABSOLUTELY NEVER** merge a pull request that:

- Has failing CI checks
- Has not passed all required reviews
- Has failing tests
- Has type errors (mypy)
- Has linting errors (ruff)

### PR Checklist (MUST PASS):

- [ ] All CI checks passing (green ✅)
- [ ] Code review approved
- [ ] Pre-commit hooks pass locally
- [ ] Tests added/updated and passing
- [ ] Type annotations complete (mypy strict)
- [ ] No linting errors (ruff)

### Emergency Protocol:

If CI is failing and you believe it should pass:
1. **DO NOT MERGE**
2. Investigate the failure
3. Fix the issue
4. Push fixes and wait for green CI
5. Only then merge

**THERE ARE NO EXCEPTIONS TO THIS RULE.**
