# TODO: Fix Linting Errors

PRD: #2 - Fix Linting Errors
Total Errors: 283 → 0 ✅

---

## All Phases Complete ✅

- [x] Phase 1: Auto-fixable (38 fixes)
- [x] Phase 2: Line length E501 (src/, tests/, examples/)
- [x] Phase 3: Unused variables RUF059
- [x] Phase 4: Import placement PLC0415 (justified noqa for lazy imports)
- [x] Phase 5: Global statement PLW0603 (refactored _last_key_event_type)
- [x] Phase 6-9: Complexity (refactored methods to reduce complexity)
- [x] Phase 10: Performance PERF401 (list.extend patterns)
- [x] Phase 11: Type checking TC001/TC003
- [x] Phase 12: Long exceptions TRY003
- [x] Phase 13: Try/else TRY300
- [x] Phase 14: Unused arguments ARG002/ARG005
- [x] Phase 15: Nested if SIM102
- [x] Phase 16: Ambiguous unicode RUF002/RUF003 (justified file-level noqa)
- [x] Phase 17: Unused variables F841
- [x] Phase 18: Import sorting I001

---

## Verification

- [x] `ruff check .` - 0 errors
- [x] `ruff format --check .` - formatting correct
- [x] `uv run pytest` - 167 passed

---

## Key Refactoring

### parse_key() API Change
- Removed global `_last_key_event_type`
- Now returns `tuple[str | None, str]` (key_id, event_type)

### Complexity Reduction
Extracted helper methods in:
- `components.py`: Text.render, SelectList.handle_input, Input.handle_input
- `terminal.py`: read_sequence
- `tui.py`: _composite_overlays, render_frame, _try_parse_input
- `utils.py`: wrap_text_with_ansi

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
