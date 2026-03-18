# PyPiTUI Scrolling Model (Verified from pi-tui source)

## The Mental Model

**Your confusion is valid** - the model is subtle. Here's how it actually works:

### Two Coordinate Systems

1. **Content coordinates** - Array indices into `newLines[]` and `previousLines[]`
2. **Screen coordinates** - Visible rows (0 to terminal_height-1)

```
Content (grows indefinitely):
[0] Line 0          <- scrolled into scrollback
[1] Line 1          <- scrolled into scrollback  
[2] Line 2          <- scrolled into scrollback
[3] Line 3          <- visible at screen row 0
[4] Line 4          <- visible at screen row 1
[5] Line 5          <- visible at screen row 2
    ...
[N] Line N          <- visible at screen row (height-1)
```

### Viewport Calculation

```python
viewport_top = max(0, max_lines_rendered - terminal_height)
```

This gives the content index of the first visible line.

### The Diff is INDEX-BASED, Not Screen-Based

```typescript
// From tui.ts lines 961-972
for (let i = 0; i < maxLines; i++) {
    const oldLine = i < this.previousLines.length ? this.previousLines[i] : "";
    const newLine = i < newLines.length ? newLines[i] : "";
    if (oldLine !== newLine) {
        firstChanged = i;
        lastChanged = i;
    }
}
```

**This compares line content at the SAME ARRAY INDEX.**

### What Happens When Content Scrolls

**Scenario:** Terminal height = 5, content grows from 3 lines to 8 lines

**Frame 1 (3 lines):**
- `previousLines = ["A", "B", "C"]`
- `viewport_top = max(0, 3 - 5) = 0`
- Visible: indices 0,1,2 at screen rows 0,1,2

**Frame 2 (8 lines - content grew by 5):**
- `newLines = ["A", "B", "C", "D", "E", "F", "G", "H"]`
- `viewport_top = max(0, 8 - 5) = 3`
- Visible: indices 3,4,5,6,7 at screen rows 0,1,2,3,4

**Diff result:**
- Index 3: `"D"` vs `""` (was empty, now has content) → **CHANGED**
- Index 4: `"E"` vs `""` → **CHANGED**
- Index 5: `"F"` vs `""` → **CHANGED**
- etc.

**All visible lines appear changed** because the viewport shifted and different content is now at those array indices.

### How Scrolling Into Scrollback Works

When content grows beyond the visible area, pi-tui emits `\r\n` (newlines) to push old content up:

```typescript
// From tui.ts lines 1048-1052
const scroll = moveTargetRow - prevViewportBottom;
buffer += "\r\n".repeat(scroll);
prevViewportTop += scroll;
viewportTop += scroll;
```

The terminal's natural scrolling behavior pushes old lines into scrollback history.

### Absolute Positioning Within the Viewport

Once the viewport is established, pi-tui uses absolute positioning to update changed lines:

```typescript
// Move cursor to first changed line
const lineDiff = computeLineDiff(moveTargetRow);
if (lineDiff > 0) buffer += `\x1b[${lineDiff}B`;  // Move down
buffer += "\r";  // Carriage return to column 0

// Write changed lines
for (let i = firstChanged; i <= renderEnd; i++) {
    if (i > firstChanged) buffer += "\r\n";  // Next line
    buffer += "\x1b[2K";  // Clear line
    buffer += newLines[i];  // Write content
}
```

### The Key Insight

**The diff compares content at the same array index.** When the viewport scrolls:
1. Different content appears at the same indices (now visible vs previously visible)
2. The diff sees these as "changed" lines
3. All visible lines get redrawn
4. But overlays composite at viewport-relative positions, so they stay fixed

**This is NOT a full clear+redraw.** It's differential rendering where the "difference" is that the viewport shifted, exposing different content at the same indices.

## pi-tui's Optimization for Appending

When content simply appends (no viewport shift yet):

```typescript
const appendStart = appendedLines && firstChanged === this.previousLines.length && firstChanged > 0;
```

If `appendStart` is true, pi-tui:
1. Positions cursor at the end of existing content
2. Emits `\r\n` to create new lines
3. Writes only the new appended lines

This is efficient because only new lines are written, not the entire viewport.

## Summary

| Your Mental Model | Reality |
|-------------------|---------|
| Clear screen + redraw on scroll | No - differential index-based comparison |
| Re-render everything in viewport | Yes - because viewport shift changes which content is at visible indices |
| Screen-based diff | No - content-index-based diff |
| Newlines for scrollback | Yes - `\r\n` emits push content into scrollback |
| Absolute positioning | Yes - but only within the current viewport |
