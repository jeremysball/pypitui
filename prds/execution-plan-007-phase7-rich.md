# Execution Plan: PRD #007 - Phase 7: Rich Integration

## Overview
Implement basic markdown and code highlighting using mistune + pygments with lazy imports.

---

## Phase 7: Rich Integration

### Dependencies

- [ ] **Add**: `mistune>=3.0` to optional dependencies `[rich]`
- [ ] **Add**: `pygments>=2.17` to optional dependencies `[rich]`
- [ ] **Run**: Verify `pyproject.toml` updated

### Markdown Component

- [ ] **Test**: `test_markdown_renders_headers()` — # Header becomes bold/underlined
- [ ] **Test**: `test_markdown_renders_bold()` — **text** becomes bold
- [ ] **Test**: `test_markdown_renders_lists()` — bullet points rendered correctly
- [ ] **Implement**: `Markdown(Component)` using mistune parser
- [ ] **Run**: `uv run pytest tests/unit/test_rich.py -k "markdown" -v`

### Code Component

- [ ] **Test**: `test_code_renders_with_syntax_highlighting()` — colored tokens via pygments
- [ ] **Test**: `test_code_language_detection()` — language parameter used for lexer
- [ ] **Implement**: `CodeBlock(Component)` with pygments highlighting
- [ ] **Run**: `uv run pytest tests/unit/test_rich.py -k "code" -v`

### Lazy Import Pattern

- [ ] **Test**: `test_rich_components_lazy_import()` — import error handled gracefully
- [ ] **Implement**: Lazy import in `components/rich.py` to avoid hard dependency
- [ ] **Run**: `uv run pytest tests/unit/test_rich.py::test_rich_components_lazy_import -v`

---

## Files to Create/Modify

1. `pyproject.toml` — Add optional dependencies `[rich]`
2. `src/pypitui/components/rich.py` — Markdown and CodeBlock components
3. `tests/unit/test_rich.py` — Rich component tests

---

## Progress

**Phase 7 Status**: 0/6 tasks complete

**Dependencies**: Phase 6 (Overlays) must be complete
