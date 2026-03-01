# PyPiTUI 0.3.0 Invalidation Analysis

## What EXISTS in pypitui 0.3.0

### 1. Component.invalidate() - Abstract Method
```python
class Component(ABC):
    @abstractmethod
    def invalidate(self) -> None:
        """Invalidate any cached rendering state."""
        pass
```
- Clears component's internal render cache
- Does NOT notify parent of invalidation
- No bubbling mechanism

### 2. Container.invalidate()
```python
class Container(Component):
    def invalidate(self) -> None:
        """Invalidate all children."""
        for child in self.children:
            child.invalidate()
```
- Calls invalidate() on all children
- Still no parent notification/bubbling
- Container itself doesn't know which child was invalidated

### 3. TUI.invalidate()
```python
class TUI(Container):
    def invalidate(self) -> None:
        """Invalidate the TUI and all children."""
        self._previous_lines = []
        self._emitted_scrollback_lines = 0
        for child in self.children:
            child.invalidate()
        for entry in self._overlay_stack:
            entry.component.invalidate()
```
- Clears ALL differential rendering state
- Forces full screen redraw
- Nuclear option - inefficient for small updates

### 4. TUI.invalidate_component() - NEW in 0.3.0
```python
class TUI(Container):
    def invalidate_component(self, component: Component) -> None:
        """Invalidate a specific component by clearing its lines from cache."""
        if component in self._component_positions:
            start, end = self._component_positions[component]
            for i in range(start, end):
                if i < len(self._previous_lines):
                    self._previous_lines[i] = ""  # Mark for clearing
        self.request_render()
```
- Efficient line-wise invalidation
- Requires TUI reference to call
- Component positions tracked during render

---

## What's MISSING

### 1. Parent References in Components
Components have no `parent` reference:
```python
class Component(ABC):
    # MISSING: parent: Component | None = None
    pass
```

### 2. Bubbling Invalidation Mechanism
No way for child to notify parent:
```python
class Component(ABC):
    def invalidate(self) -> None:
        """MISSING: Should bubble up to parent."""
        # Current: only clears own cache
        # Missing: notify parent so TUI can invalidate_component()
        if self.parent and hasattr(self.parent, '_child_invalidated'):
            self.parent._child_invalidated(self)
```

### 3. Container._child_invalidated() Callback
Container doesn't track which child was invalidated:
```python
class Container(Component):
    def _child_invalidated(self, child: Component) -> None:
        """MISSING: Should propagate to parent until reaching TUI."""
        # Should bubble up until TUI calls invalidate_component(child)
        pass
```

### 4. TUI Integration with Component.invalidate()
TUI doesn't intercept Component.invalidate() calls:
```python
class TUI(Container):
    def invalidate_component(self, component: Component) -> None:
        # EXISTS but requires EXPLICIT call
        # MISSING: automatic trigger from component.invalidate()
        pass
```

---

## Current Workaround (Explicit TUI Reference)

Components must hold a TUI reference to trigger efficient invalidation:

```python
class CompletionAddon:
    def __init__(self, tui: TUI | None = None, ...):
        self._tui = tui  # Must store TUI reference
    
    def on_menu_change(self) -> None:
        if self._tui:
            # Explicit call required
            self._tui.invalidate_component(self._input)
        else:
            # Fallback: full re-render (inefficient)
            self._input.invalidate()
```

**Problems:**
- Tight coupling to TUI
- Components can't be TUI-agnostic
- Easy to forget passing TUI reference
- Falls back to inefficient full redraw

---

## Desired Behavior (Bubbling Invalidation)

### Pattern: Automatic Bubble-Up
```python
# Component calls own invalidate
my_component.invalidate()

# Should bubble: my_component -> parent -> ... -> TUI
# TUI automatically calls invalidate_component(my_component)
```

### Implementation Would Require:

1. **Parent references in Component:**
```python
class Component(ABC):
    def __init__(self):
        self._parent: Component | None = None
    
    @property
    def parent(self) -> Component | None:
        return self._parent
    
    def invalidate(self) -> None:
        self._invalidate_self()
        if self._parent is not None:
            self._parent._child_invalidated(self)
```

2. **Container._child_invalidated propagates:**
```python
class Container(Component):
    def _child_invalidated(self, child: Component) -> None:
        """Propagate child invalidation to parent."""
        if self._parent is not None:
            self._parent._child_invalidated(child)
```

3. **TUI intercepts and handles efficiently:**
```python
class TUI(Container):
    def _child_invalidated(self, child: Component) -> None:
        """TUI endpoint - perform efficient line-wise invalidation."""
        self.invalidate_component(child)
```

### Usage Would Be Clean:
```python
class CompletionAddon:
    def on_menu_change(self) -> None:
        # Just invalidate the input - TUI handles the rest
        self._input.invalidate()
        # Automatically bubbles up, TUI.invalidate_component() called
```

---

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| `Component.invalidate()` | ✅ Exists | Clears component cache only |
| `Container.invalidate()` | ✅ Exists | Calls invalidate on all children |
| `TUI.invalidate()` | ✅ Exists | Clears all lines (full redraw) |
| `TUI.invalidate_component()` | ✅ Exists | Efficient line-wise invalidation |
| Parent references | ❌ Missing | Components don't know their parent |
| Bubbling invalidation | ❌ Missing | No `_child_invalidated()` chain |
| TUI-agnostic components | ❌ Impossible | Must pass TUI reference for efficient invalidation |

The missing bubbling mechanism forces tight coupling between components and TUI, or inefficient full-screen redraws.