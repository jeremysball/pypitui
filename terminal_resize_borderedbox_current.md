# Terminal Resizing & BorderedBox Usage Fixes

## Issue 1: Terminal Resizing Not Properly Handled

### Current Behavior
- Terminal resizing causes display corruption
- Content doesn't reflow to new terminal dimensions
- Overlays may appear in wrong positions after resize
- Text wrapping doesn't update when terminal gets narrower/wider

### Expected Behavior
- TUI should detect terminal size changes
- All components should re-render with new dimensions
- Layout should adapt smoothly to new terminal size
- No display corruption or ghost content after resize

### Implementation Plan

1. **Detect Terminal Resize**
   - Check for SIGWINCH signal (Unix) or terminal size changes
   - In the main render loop, compare current terminal size with previous size
   - If size changed, trigger a full re-render

2. **Add Resize Handling to TUI Class**
   ```python
   def check_resize(self) -> bool:
       """Check if terminal was resized and handle it."""
       current_size = self.terminal.get_size()
       if current_size != self._last_terminal_size:
           self._last_terminal_size = current_size
           self._previous_lines = []  # Force full redraw
           self.invalidate()  # Invalidate all children
           return True
       return False
   ```

3. **Update Render Loop**
   - Call `check_resize()` before each frame render
   - If resized, force full redraw by clearing `_previous_lines`

4. **Test Cases**
   - Resize terminal while menu is displayed
   - Resize terminal while overlay is open
   - Resize terminal to very small dimensions
   - Resize terminal to very large dimensions
   - Rapid resizing should not crash

### Files to Modify
- `src/pypitui/tui.py` - Add resize detection and handling

---

## Issue 2: Manual Border Creation Should Use BorderedBox

### Current Problem
Some parts of the codebase (especially examples) manually create border art using Text components with box-drawing characters. This is error-prone and doesn't handle content wrapping properly.

### Examples of Incorrect Usage

1. **ultimate_demo.py - Manual overlay borders (lines 642-680)**
   Currently creates borders manually:
   ```python
   container.add_child(Text(
       f"{Colors.CYAN}┌{'─' * 33}┐{Colors.RESET}", 0, 0
   ))
   container.add_child(Text(
       f"{Colors.CYAN}│{Colors.RESET}  {title}{' ' * (31 - len(title))}{Colors.CYAN}│{Colors.RESET}", 0, 0
   ))
   ```

2. **Other potential locations**
   - Any place using manual `┌─┐│└┘` characters with Text components
   - Any place calculating padding manually for borders

### Solution

Replace all manual border creation with `BorderedBox`:

```python
# Instead of:
container = Container()
container.add_child(Text(f"{Colors.CYAN}┌{'─' * 33}┐{Colors.RESET}", 0, 0))
container.add_child(Text(f"{Colors.CYAN}│{Colors.RESET}  {title}{Colors.CYAN}│{Colors.RESET}", 0, 0))
container.add_child(Text(f"{Colors.CYAN}└{'─' * 33}┘{Colors.RESET}", 0, 0))

# Use:
box = BorderedBox(padding_x=1, padding_y=0, title=title)
box.add_child(Text("Content that wraps automatically"))
```

### Files to Audit and Fix

1. **examples/ultimate_demo.py**
   - Fix `create_overlay_content()` method (around line 642)
   - Search for any other manual box drawing

2. **examples/demo.py**
   - Already fixed - uses BorderedBox

3. **examples/simple_menu.py**
   - Check if manual borders are used

4. **Documentation**
   - README.md already discourages manual borders
   - Add stronger warning in code comments

### BorderedBox Benefits
- Automatic content wrapping
- Proper width handling
- Consistent styling
- Title support with separator
- No manual width calculations needed

---

## Priority
1. Fix terminal resizing (high impact on user experience)
2. Audit and fix manual border usage (code quality)

## Testing Checklist

### Terminal Resize
- [ ] Resize while on main menu
- [ ] Resize while overlay is open
- [ ] Resize to 80x24
- [ ] Resize to 120x40
- [ ] Resize to 40x10 (small)
- [ ] Rapid consecutive resizes

### BorderedBox Usage
- [ ] No manual `┌─┐│└┘` in examples
- [ ] All panels use BorderedBox
- [ ] Consistent padding across all boxes
