# Feature Request: Component-aware invalidation with parent references

## Problem
When a child component changes (e.g., a completion menu closes), we need to clear just that component's lines from `_previous_lines`. Currently, the only option is `tui.invalidate()` which clears the entire cache, causing a full redraw instead of targeted cleanup.

## Current Workaround
```python
# Over-invalidation - clears everything including unrelated content
def on_menu_close():
    tui.invalidate()  # Clears ALL of _previous_lines
```

## Required: Two-Layer Solution

### Layer 1: Position Tracking (the actual feature)
TUI tracks each component's line range during render:

```python
class TUI(Container):
    def render(self, width: int) -> list[str]:
        self._component_positions = {}  # component -> (start_line, end_line)
        lines = []
        for child in self.children:
            start = len(lines)
            child_lines = child.render(width)
            self._component_positions[child] = (start, len(lines))
            lines.extend(child_lines)
        return lines
    
    def invalidate_component(self, component: Component) -> None:
        """Clear specific component's lines from cache."""
        if component in self._component_positions:
            start, end = self._component_positions[component]
            for i in range(start, end):
                if i < len(self._previous_lines):
                    self._previous_lines[i] = ""  # Mark for clearing
        self.request_render()
```

### Layer 2: Bubble-up (convenience plumbing)
Children can notify TUI without direct reference:

```python
class Component:
    def __init__(self):
        self._parent: Container | None = None
    
    def invalidate(self) -> None:
        """Bubble up to TUI for targeted invalidation."""
        if self._parent:
            self._parent._child_invalidated(self)

class Container(Component):
    def add_child(self, component: Component) -> None:
        self.children.append(component)
        component._parent = self
    
    def _child_invalidated(self, child: Component) -> None:
        """Pass it up the chain until TUI handles it."""
        if self._parent:
            self._parent._child_invalidated(child)

class TUI(Container):
    def _child_invalidated(self, child: Component) -> None:
        """Child bubbled up - use position tracking."""
        self.invalidate_component(child)
```

## Usage

**Direct approach (needs TUI reference):**
```python
class CompletionAddon:
    def __init__(self, tui: TUI, input_field: WrappedInput):
        self.tui = tui
        self.input_field = input_field
    
    def on_menu_close(self):
        self.tui.invalidate_component(self.input_field)  # Targeted
```

**Bubble-up approach (no TUI reference needed):**
```python
class CompletionAddon:
    def __init__(self, input_field: WrappedInput):
        self.input_field = input_field  # Just the input, no TUI ref
    
    def on_menu_close(self):
        self.input_field.invalidate()  # Bubbles up to TUI
```

## Key Insight

**Bubble-up without position tracking is useless** - you'd still clear everything.

**Position tracking without bubble-up requires direct TUI references** - children need to know about the TUI.

**Both together:**
- Any component can call `self.invalidate()`
- It bubbles up to the TUI automatically
- TUI clears just that component's lines
- Clean API, minimal redraw

## Use Case

```
┌────────────────────────┐
│ Message 1              │  ← Keep (not invalidated)
│ Message 2              │  ← Keep (not invalidated)
┌────────────────────────┐
│ /new    New session    │  ← Clear these 4 lines only
│ /resume Resume session │
│ /help   Show help      │
└────────────────────────┘
/                        │  ← Keep (input field, part of same component)
```

Completion menu (rendered via filter) closes:
```python
# Menu was part of input_field's render output
input_field.invalidate()  # Bubbles to TUI
# TUI clears lines 2-5 from _previous_lines
# Next render only shows input line, menu lines get erased
```

## Questions

1. Should `invalidate()` accept a `region` parameter for sub-component invalidation?
2. How to handle components that change size between renders?
3. Should `Container._child_invalidated()` accumulate multiple invalidations before bubbling?

## Related

- Current `TUI.invalidate()` clears `_previous_lines = []` - full reset
- `request_render(force=True)` also clears `_previous_lines`
- Neither allows targeted invalidation
