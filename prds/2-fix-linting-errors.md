# PRD: Fix Linting Errors

**Issue**: #2
**Created**: 2026-02-26
**Status**: In Progress

## Problem

The codebase has 283 linting errors from ruff that need to be addressed for code quality and CI compliance.

## Solution

Systematically fix all linting errors by category, with appropriate `noqa` comments where needed for intentional deviations.

---

## Progress

**Started**: 283 errors
**Current**: 143 errors
**Fixed**: 140 errors (49% reduction)

### Completed
- ✅ Phase 1: Auto-fixable (38 fixes)
- ✅ Phase 2: Line length in src/
- ✅ Phase 3: Unused variables RUF059
- ✅ Phase 4: Import placement PLC0415 (justified noqa for lazy imports)
- ✅ Phase 5: Global statement PLW0603 (refactored _last_key_event_type)
- ✅ Phase 10-18: All other categories

### Remaining
- ⏳ Complexity metrics (C901, PLR0912, PLR0915, PLR0911) - deferred, require refactoring
- ⏳ examples/demo.py (116 errors) - not part of library

---

## Key Refactoring

### parse_key() API Change
Previously used a global `_last_key_event_type` to track key events. Refactored to return a tuple:
```python
# Before
def parse_key(data: str) -> str | None:
    # sets global _last_key_event_type
    return key_id

# After  
def parse_key(data: str) -> tuple[str | None, str]:
    return (key_id, event_type)  # event_type is "press", "repeat", or "release"
```

This eliminates hidden state and makes the API cleaner.

---

## Justified noqa Comments

| noqa | Location | Reason |
|------|----------|--------|
| PLC0415 | rich_components.py | Lazy imports for optional rich dependency |
| PLC0415 | utils.py:25 | Conditional import with fallback |
| PLW0603 | keys.py:17 | Module-level protocol state |
| PLW0603 | utils.py:22 | Lazy singleton initialization |
| RUF002/RUF003 | keys.py (file-level) | Intentional Cyrillic in keyboard docs |
| B027 | tui.py:44 | Empty abstract method (optional override) |

---

## Verification

- [x] All 167 tests pass
- [x] src/ down to 15 errors (all complexity metrics)
- [ ] examples/demo.py deferred
