#!/usr/bin/env python3
"""PyPiTUI Ultimate Demo - Full Rich Theme Integration

Demonstrates how to use Rich markup to theme the ENTIRE UI.
All text uses Rich markup instead of raw ANSI codes, making
the entire interface themeable through Rich's style system.
"""

from __future__ import annotations

import math
import random
import time
from collections.abc import Callable
from dataclasses import dataclass

from pypitui import (
    TUI, Container, Text, Box, BorderedBox, Spacer,
    SelectList, SelectItem, SelectListTheme, Input,
    OverlayOptions, ProcessTerminal, matches_key, Key,
)
from pypitui.tui import Component

try:
    from pypitui.rich_components import Markdown, RichText, RichTable, rich_to_ansi, rich_color_to_ansi
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# =============================================================================
# RICH THEME SYSTEM - All UI uses Rich markup
# =============================================================================

@dataclass
class RichTheme:
    """Rich-compatible theme using markup names instead of ANSI codes."""
    name: str
    primary: str      # Rich color name
    secondary: str    # Rich color name
    accent: str       # Rich color name
    muted: str        # Rich color name
    success: str      # Rich color name
    error: str        # Rich color name


THEMES: dict[str, RichTheme] = {
    "neon": RichTheme(
        name="Cyberpunk Neon",
        primary="bright_cyan",
        secondary="bright_magenta",
        accent="bright_yellow",
        muted="dim",
        success="bright_green",
        error="bright_red",
    ),
    "warm": RichTheme(
        name="Warm Sunset",
        primary="yellow",
        secondary="red",
        accent="bright_red",
        muted="dim",
        success="green",
        error="red",
    ),
    "ocean": RichTheme(
        name="Deep Ocean",
        primary="blue",
        secondary="cyan",
        accent="bright_cyan",
        muted="dim",
        success="green",
        error="red",
    ),
}

# =============================================================================
# RENDER HELPERS - Convert Rich markup to ANSI for SelectList compatibility
# =============================================================================


# =============================================================================
# RICH UI HELPERS - Everything uses Rich markup
# =============================================================================

def rich_header(title: str, subtitle: str = "", theme: RichTheme | None = None) -> list[Component]:
    """Create header using RichText for full theme integration."""
    components: list[Component] = [Spacer(1)]
    
    t = theme or THEMES["neon"]
    
    # Title uses Rich markup via set_rich_title
    box = BorderedBox(padding_x=2, max_width=45)
    box.set_rich_title(f"[bold {t.primary}]{title}[/bold {t.primary}]")
    
    if subtitle:
        # RichText gets the theme styling
        box.add_child(RichText(f"[{t.muted}]{subtitle}[/{t.muted}]"))
    
    components.append(box)
    components.append(Spacer(1))
    
    return components


def rich_text(content: str, theme: RichTheme, style: str = "") -> RichText:
    """Create RichText with theme color.
    
    PATTERN: Use Rich markup [color]text[/color] instead of ANSI codes.
    This makes the entire UI themeable and consistent.
    """
    if style:
        return RichText(f"[{theme.primary}]{content}[/{theme.primary}]")
    return RichText(content)


def rich_label(text: str, theme: RichTheme) -> RichText:
    """Bold label using Rich markup."""
    return RichText(f"[bold {theme.primary}]{text}[/bold {theme.primary}]")


def rich_footer(text: str = "ESC to go back", theme: RichTheme | None = None) -> RichText:
    """Footer using Rich markup."""
    t = theme or THEMES["neon"]
    return RichText(f"[{t.muted}]{text}[/{t.muted}]")


def create_rich_theme(theme: RichTheme) -> SelectListTheme:
    """Create SelectList theme using ANSI colors.
    
    GOTCHA: SelectList displays raw strings, not Rich-rendered markup.
    Use ANSI codes for SelectList, RichText for everything else.
    """
    primary = rich_color_to_ansi(theme.primary)
    muted = rich_color_to_ansi(theme.muted)
    reset = "\x1b[0m"
    
    return SelectListTheme(
        selected_prefix=lambda s: f"{primary}▶{reset} ",
        selected_text=lambda s: f"\x1b[1m{primary}{s}{reset}",
        description=lambda s: f"{muted}{s}{reset}",
    )


# =============================================================================
# DEMO DATA
# =============================================================================

DEMO_ITEMS = [
    ("splash", "🎨 Splash", "Animated intro"),
    ("demoscene", "🔥 Demo Scene", "ANSI art animations"),
    ("components", "🧩 Components", "UI building blocks"),
    ("wizard", "🧙 Form Wizard", "Multi-step input"),
    ("overlays", "🪟 Overlays", "Floating panels"),
    ("themes", "🎨 Themes", "Visual styles"),
    ("rich", "✨ Rich", "Markdown & tables"),
    ("about", "ℹ️  About", "Library info"),
]


WIZARD_STEPS = [
    ("Welcome", "Get started"),
    ("Profile", "Your details"),
    ("Theme", "Choose style"),
    ("Complete", "Done!"),
]


# =============================================================================
# MAIN APPLICATION - All UI uses Rich theming
# =============================================================================

class UltimateDemoApp:
    """Demo with full Rich theme integration throughout the UI."""

    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal, show_hardware_cursor=True)
        self.running = True
        self.current_screen = "menu"
        self.current_theme = "neon"
        self.wizard_step = 0
        self.form_data = {"name": "", "email": "", "theme": "neon"}
        self.overlay_handle = None
        self.animation_active = False
        self.splash_frame = 0
        
        self.build_menu()

    def _theme(self) -> RichTheme:
        """Get current Rich theme."""
        return THEMES[self.current_theme]

    def _clear(self) -> None:
        """Clear screen preserving TUI state."""
        self.tui.clear()

    def build_menu(self) -> None:
        """Main menu with Rich-styled everything."""
        self._clear()
        self.current_screen = "menu"
        self.animation_active = False
        
        t = self._theme()
        
        # Header with Rich subtitle
        for comp in rich_header("🐍 PyPiTUI", "Terminal UI Framework", t):
            self.tui.add_child(comp)
        
        # Menu items with Rich theme
        items = [
            SelectItem(key, label, desc)
            for key, label, desc in DEMO_ITEMS
        ]
        
        menu = SelectList(items, 7, create_rich_theme(t))
        menu.on_select = self.on_menu_select
        self.tui.add_child(menu)
        self.tui.set_focus(menu)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(rich_footer("↑↓ Navigate • Enter Select • Q Quit", t))

    def on_menu_select(self, item: SelectItem) -> None:
        """Route menu selection."""
        handlers: dict[str, Callable] = {
            "splash": self.show_splash,
            "demoscene": self.show_demoscene,
            "components": self.show_components,
            "wizard": self.show_wizard,
            "overlays": self.show_overlays,
            "themes": self.show_themes,
            "rich": self.show_rich,
            "about": self.show_about,
        }
        handlers.get(item.value, self.build_menu)()

    def show_splash(self) -> None:
        """Animated splash screen."""
        self._clear()
        self.current_screen = "splash"
        self.animation_active = True
        self.splash_frame = 0
        
        self.tui.add_child(Spacer(3))
        
        self.splash_text = Text("", 0, 0)
        self.tui.add_child(self.splash_text)
        
        self.tui.add_child(Spacer(2))
        self.tui.add_child(rich_footer("Press any key to continue", self._theme()))
        
        self.update_splash()

    def update_splash(self) -> None:
        """Update splash animation."""
        if not self.animation_active:
            return
        
        now = time.time()
        if not hasattr(self, '_last_animation_update'):
            self._last_animation_update = 0
        if now - self._last_animation_update < 0.5:
            return
        self._last_animation_update = now
        
        frames = ["✨", "⭐", "💫", "🌟"]
        icon = frames[self.splash_frame % len(frames)]
        t = self._theme()
        
        # Use Rich markup for splash content
        splash_content = Container()
        box = BorderedBox(padding_x=3, max_width=40, title=f"{icon} PyPiTUI")
        box.add_child(RichText(f"[{t.primary}]Terminal UI Framework[/{t.primary}]"))
        box.add_child(Spacer(1))
        box.add_child(RichText(f"[{t.accent}]Beautiful Terminal Apps[/{t.accent}]"))
        splash_content.add_child(box)
        
        # Render to text
        lines = splash_content.render(40)
        self.splash_text.set_text("\n".join(lines))
        self.tui.request_render()
        
        self.splash_frame += 1

    # =============================================================================
    # DEMO SCENE - MATRIX RAIN EFFECT (Proper Implementation)
    # Based on unimatrix/cmatrix techniques:
    # - Column-based state with moving heads
    # - White head character, green trail
    # - Random character mutations
    # - Smooth asynchronous scrolling
    # =============================================================================

    # ANSI codes
    A = {
        'rs': '\x1b[0m', 'bd': '\x1b[1m',
        'g': '\x1b[32m', 'G': '\x1b[92m', 'w': '\x1b[97m',
        'k': '\x1b[30m', 'K': '\x1b[90m',
    }

    # ASCII only - universally supported
    CHARS = '0123456789ABCDEF' + \
            'abcdefghijklmnopqrstuvwxyz' + \
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
            '@#$%&*+-=<>~'

    def show_demoscene(self) -> None:
        """Matrix rain animation based on cmatrix/unimatrix.
        
        EDGE CASES DISCOVERED:
        1. Hardcoded sizes break on small terminals - must use actual terminal size
        2. Grid must be resized when terminal changes size
        3. Minimum size check needed - animation needs at least 10x10 to look good
        4. ANSI codes in output affect line wrapping calculations
        5. Scroller text must adapt to actual width, not hardcoded width
        """
        self._clear()
        self.current_screen = "demoscene"
        self.animation_active = True
        self.demoscene_frame = 0
        self.scroll_pos = 0
        
        # Get ACTUAL terminal size - critical for proper rendering
        # EDGE CASE: If terminal is resized during demo, we handle it in update_demoscene
        term_width, term_height = self.terminal.get_size()
        
        # Reserve bottom 3 rows for UI (separator, scroller, help text)
        # EDGE CASE: Small terminals - animation area may be very limited
        min_width, min_height = 40, 5  # Reduced min_height for edge cases
        self.demo_width = max(min_width, term_width)
        # Animation height is whatever is left after UI rows (minimum 1)
        self.demo_height = max(min_height, term_height - 3)
        self.total_height = self.demo_height + 3
        
        # Scroller text - defined once here
        self.scroll_text = " PYPITUI - TERMINAL UI FRAMEWORK - GITHUB.COM/JEREMYSBALL/PYPITUI - "
        
        # Initialize columns for the animation
        self.columns: list[dict] = []
        self._init_columns()
        
        # Grid stores (char, brightness, age) for each cell
        # brightness: 0=dark, 1=green, 2=bright green, 3=white
        self.grid: list[list[tuple[str, int, int]]] = []
        self._init_grid()
        
        self.demoscene_text = Text("", 0, 0)
        self.tui.add_child(self.demoscene_text)
        
        self.update_demoscene()
    
    def _init_columns(self) -> None:
        """Initialize/reset column state for animation.
        
        EDGE CASE: When terminal grows, we need more columns.
        When it shrinks, we keep columns but clip rendering.
        """
        target_cols = self.demo_width
        
        # If we need more columns, add them
        while len(self.columns) < target_cols:
            self.columns.append({
                'head_y': random.randint(-20, 0),
                'speed': random.uniform(0.3, 1.2),
                'length': random.randint(5, 15),
                'timer': random.randint(0, 30),
                'active': True,
            })
    
    def _init_grid(self) -> None:
        """Initialize/resize the animation grid.
        
        EDGE CASE: Grid must match current terminal dimensions.
        Old content is lost on resize - this is intentional for simplicity.
        """
        self.grid = [[(' ', 0, 0) for _ in range(self.demo_height)] 
                     for _ in range(self.demo_width)]

    def _get_char(self) -> str:
        """Get random Matrix character."""
        return random.choice(self.CHARS)

    def update_demoscene(self) -> None:
        """Update Matrix rain at 60 FPS.
        
        EDGE CASES HANDLED:
        1. Terminal resize: Check size each frame, reinit grid if changed
        2. Grid bounds: Always clip to current grid dimensions
        3. ANSI accumulation: Each cell gets fresh ANSI codes, no stacking
        4. Minimum size: Enforced at initialization, but checked here too
        5. Full grid aging: ALL cells must age each frame to prevent artifacts
        """
        if not self.animation_active or self.current_screen != "demoscene":
            return
        
        now = time.time()
        if not hasattr(self, '_last_demo_update') or self._last_demo_update == 0:
            self._last_demo_update = now
            return  # Skip first frame to initialize timing
        if now - self._last_demo_update < 0.016:  # ~60 FPS
            return
        
        # Calculate delta time for smooth animation regardless of frame rate
        dt = now - self._last_demo_update
        self._last_demo_update = now
        
        # EDGE CASE: Handle terminal resize
        term_width, term_height = self.terminal.get_size()
        # Must match the logic in show_demoscene exactly!
        min_width, min_height = 40, 5
        new_width = max(min_width, term_width)
        new_height = max(min_height, term_height - 3)
        
        if new_width != self.demo_width or new_height != self.demo_height:
            # Terminal resized - reinitialize to match new size
            self.demo_width = new_width
            self.demo_height = new_height
            self.total_height = new_height + 3
            self._init_columns()
            self._init_grid()
        
        w, h = self.demo_width, self.demo_height
        
        # Update each column
        for x, col in enumerate(self.columns):
            if x >= w:  # EDGE CASE: Skip columns beyond visible width
                continue
                
            if not col['active']:
                col['timer'] -= 1
                if col['timer'] <= 0:
                    col['head_y'] = random.randint(-10, -2)
                    col['speed'] = random.uniform(0.3, 1.2)
                    col['length'] = random.randint(5, 15)
                    col['active'] = True
                continue
            
            # Use delta time for smooth animation speed regardless of frame rate
            # Scale speed down so it's visible but not too fast at 60 FPS
            col['head_y'] += col['speed'] * dt * 2.0
            head_int = int(col['head_y'])
            
            # Draw trail - clip to animation bounds
            for dy in range(col['length']):
                y = head_int - dy
                if y < 0 or y >= h:  # EDGE CASE: Clip to grid bounds
                    continue
                if dy == 0:
                    # White head
                    self.grid[x][y] = (self._get_char(), 3, 0)
                elif dy < 3:
                    # Bright green near head - with random mutation for variety
                    if random.random() < 0.3:
                        self.grid[x][y] = (self._get_char(), 2, dy)
                    else:
                        old_char = self.grid[x][y][0] if self.grid[x][y][0] != ' ' else self._get_char()
                        self.grid[x][y] = (old_char, 2, dy)
                else:
                    # Dark green trail - occasional mutation
                    if random.random() < 0.05:
                        old_char = self.grid[x][y][0] if self.grid[x][y][0] != ' ' else self._get_char()
                        self.grid[x][y] = (old_char, 1, dy)
            
            # Deactivate if trail goes off bottom
            if head_int - col['length'] > h:
                col['active'] = False
                col['timer'] = random.randint(10, 60)
        
        # Age/fade trail below head (original approach - per column)
        for x, col in enumerate(self.columns):
            if x >= w:
                continue
            if not col['active']:
                continue
            head_int = int(col['head_y'])
            fade_start = max(0, head_int - col['length'] - 2)
            fade_end = min(h, head_int - col['length'] + 2)
            for y in range(fade_start, fade_end):
                char, bright, age = self.grid[x][y]
                if bright > 0:
                    age += 1
                    if age > 3 and bright == 2:
                        bright = 1
                    elif age > 6 and bright == 1:
                        bright = 0
                        char = ' '
                    self.grid[x][y] = (char, bright, age)
        
        # Render animation - build exactly h lines
        lines = []
        for y in range(h):
            line_chars = []
            for x in range(w):
                char, brightness, _ = self.grid[x][y]
                # EDGE CASE: Fresh ANSI codes each frame - don't accumulate
                if brightness == 3:
                    line_chars.append(f"{self.A['w']}{self.A['bd']}{char}{self.A['rs']}")
                elif brightness == 2:
                    line_chars.append(f"{self.A['G']}{char}{self.A['rs']}")
                elif brightness == 1:
                    line_chars.append(f"{self.A['g']}{char}{self.A['rs']}")
                else:
                    line_chars.append(' ')
            # Use non-breaking spaces so wrap_text_with_ansi doesn't split our lines
            lines.append(''.join(line_chars).replace(' ', '\xa0'))
        
        # Fixed UI at bottom - exactly 3 lines
        # Use delta time for smooth scrolling (slower than the rain)
        self._scroll_accumulator = getattr(self, '_scroll_accumulator', 0.0) + dt * 8.0
        if self._scroll_accumulator >= 1.0:
            self.scroll_pos = (self.scroll_pos + int(self._scroll_accumulator)) % len(self.scroll_text)
            self._scroll_accumulator = 0.0
        
        # Build scroller to match actual terminal width
        visible = ""
        text_len = len(self.scroll_text)
        for i in range(w):
            idx = (self.scroll_pos + i) % text_len
            visible += self.scroll_text[idx]
        
        # Center the help text
        help_raw = "Press any key to exit"
        pad_left = max(0, (w - len(help_raw)) // 2)
        pad_right = max(0, w - len(help_raw) - pad_left)
        help_text = ' ' * pad_left + help_raw + ' ' * pad_right
        
        lines.append(f"{self.A['K']}{'═' * w}{self.A['rs']}")
        lines.append(f"{self.A['g']}{visible}{self.A['rs']}")
        lines.append(f"{self.A['K']}{help_text}{self.A['rs']}")
        
        self.demoscene_text.set_text('\n'.join(lines))
        self.tui.request_render()

    def show_components(self) -> None:
        """Component showcase with Rich theming."""
        self._clear()
        self.current_screen = "components"
        t = self._theme()
        
        for comp in rich_header("Component Showcase", theme=t):
            self.tui.add_child(comp)
        
        # Text component - uses Rich
        self.tui.add_child(RichText(
            f"[bold {t.primary}]Text:[/bold {t.primary}] Auto-wraps content. "
            f"[{t.muted}]This demonstrates word wrapping.[/{t.muted}]"
        ))
        self.tui.add_child(Spacer(1))
        
        # Box component
        self.tui.add_child(rich_label("Box (padding):", t))
        box = Box(padding_x=2)
        box.add_child(RichText(f"[{t.secondary}]Content with padding[/{t.secondary}]"))
        self.tui.add_child(box)
        self.tui.add_child(Spacer(1))
        
        # BorderedBox component
        self.tui.add_child(rich_label("BorderedBox (preferred):", t))
        b = BorderedBox(padding_x=2, max_width=35, title="Panel")
        b.add_child(RichText(f"[{t.accent}]Draws borders, wraps content[/{t.accent}]"))
        self.tui.add_child(b)
        self.tui.add_child(Spacer(1))
        
        # Input component
        self.tui.add_child(rich_label("Input:", t))
        inp = Input(placeholder="Type and press Enter...")
        inp.on_submit = lambda v: self.show_result(f"You typed: {v}")
        self.tui.add_child(inp)
        self.tui.set_focus(inp)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(rich_footer(theme=t))

    def show_wizard(self) -> None:
        """Multi-step form wizard with Rich theming."""
        self._clear()
        self.current_screen = "wizard"
        t = self._theme()
        
        step_name, step_desc = WIZARD_STEPS[self.wizard_step]
        
        for comp in rich_header(f"Wizard: {step_name}", step_desc, t):
            self.tui.add_child(comp)
        
        # Progress indicator with Rich colors
        progress_parts = []
        for i, (name, _) in enumerate(WIZARD_STEPS):
            if i == self.wizard_step:
                progress_parts.append(f"[bold {t.primary}]{name}[/bold {t.primary}]")
            else:
                progress_parts.append(f"[{t.muted}]{name}[/{t.muted}]")
        progress = " → ".join(progress_parts)
        self.tui.add_child(RichText(progress))
        self.tui.add_child(Spacer(2))
        
        if self.wizard_step == 0:
            self.tui.add_child(RichText(f"[{t.secondary}]This wizard demonstrates forms.[/{t.secondary}]"))
            self.tui.add_child(Spacer(1))
            self.tui.add_child(rich_footer("Press Enter to start", t))
            
        elif self.wizard_step == 1:
            self.tui.add_child(rich_label("Name:", t))
            name = Input(placeholder="Your name")
            name.set_value(self.form_data["name"])
            self.tui.add_child(name)
            self.name_input = name
            
            self.tui.add_child(Spacer(1))
            self.tui.add_child(rich_label("Email:", t))
            email = Input(placeholder="Your email")
            email.set_value(self.form_data["email"])
            self.tui.add_child(email)
            self.email_input = email
            
            self.tui.add_child(Spacer(1))
            self.tui.add_child(rich_footer("Tab: switch • Enter: continue", t))
            self.tui.set_focus(name)
            
        elif self.wizard_step == 2:
            self.tui.add_child(rich_label("Choose Theme:", t))
            
            items = [SelectItem(k, v.name) for k, v in THEMES.items()]
            lst = SelectList(items, 3, create_rich_theme(t))
            lst.on_select = lambda i: self.advance_wizard(theme=i.value)
            self.tui.add_child(lst)
            self.tui.set_focus(lst)
            
        else:  # Complete
            self.tui.add_child(RichText(f"[bold {t.success}]✓ Setup Complete![/bold {t.success}]"))
            self.tui.add_child(Spacer(1))
            self.tui.add_child(RichText(f"Name: {self.form_data['name'] or '(none)'}"))
            self.tui.add_child(RichText(f"Email: {self.form_data['email'] or '(none)'}"))
            self.tui.add_child(RichText(f"Theme: [{t.accent}]{THEMES[self.form_data.get('theme', 'neon')].name}[/{t.accent}]"))

    def advance_wizard(self, **kwargs) -> None:
        """Advance to next wizard step."""
        self.form_data.update(kwargs)
        
        if self.wizard_step < len(WIZARD_STEPS) - 1:
            self.wizard_step += 1
            self.show_wizard()
        else:
            self.wizard_step = 0
            self.build_menu()

    def show_overlays(self) -> None:
        """Overlay positioning demo with Rich theming."""
        self._clear()
        self.current_screen = "overlays"
        t = self._theme()
        
        for comp in rich_header("Overlay System", "Floating panels & dialogs", t):
            self.tui.add_child(comp)
        
        positions = [
            SelectItem("center", "Center", "Default centered"),
            SelectItem("top", "Top", "Top of screen"),
            SelectItem("bottom", "Bottom", "Bottom of screen"),
            SelectItem("top-right", "Top Right", "Upper right corner"),
        ]
        
        lst = SelectList(positions, 4, create_rich_theme(t))
        lst.on_select = self.show_overlay_demo
        self.tui.add_child(lst)
        self.tui.set_focus(lst)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(rich_footer(theme=t))

    def show_overlay_demo(self, item: SelectItem) -> None:
        """Show example overlay with Rich theming."""
        if self.overlay_handle:
            self.overlay_handle.hide()
        
        anchors = {
            "center": "center",
            "top": "top",
            "bottom": "bottom",
            "top-right": "top-right",
        }
        anchor = anchors.get(item.value, "center")
        t = self._theme()
        
        content = BorderedBox(padding_x=2, max_width=35, title=f"{anchor.title()} Overlay")
        content.add_child(RichText(f"[{t.primary}]Positioned at {anchor}[/{t.primary}]"))
        content.add_child(RichText(f"[{t.muted}]Press ESC to close[/{t.muted}]"))
        
        opts = OverlayOptions(width=35, anchor=anchor)
        self.overlay_handle = self.tui.show_overlay(content, opts)

    def show_themes(self) -> None:
        """Theme gallery with Rich color previews."""
        self._clear()
        self.current_screen = "themes"
        t = self._theme()
        
        for comp in rich_header("Theme Gallery", theme=t):
            self.tui.add_child(comp)
        
        # Show themes with Rich color previews
        items = []
        for key, th in THEMES.items():
            desc = f"[bold {th.primary}]████[/bold {th.primary}] [bold {th.secondary}]████[/bold {th.secondary}]"
            items.append(SelectItem(key, th.name, desc))
        
        lst = SelectList(items, 3, create_rich_theme(t))
        lst.on_select = self.apply_theme
        self.tui.add_child(lst)
        self.tui.set_focus(lst)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(rich_footer(theme=t))

    def apply_theme(self, item: SelectItem) -> None:
        """Apply selected theme and return to menu."""
        self.current_theme = item.value
        self.form_data["theme"] = item.value
        self.build_menu()

    def show_rich(self) -> None:
        """Rich integration demo with full theme support."""
        self._clear()
        self.current_screen = "rich"
        t = self._theme()
        
        for comp in rich_header("Rich Integration", theme=t):
            self.tui.add_child(comp)
        
        if not RICH_AVAILABLE:
            self.tui.add_child(RichText(
                f"[bold {t.error}]Rich not installed. Run: pip install pypitui[rich][/bold {t.error}]"
            ))
        else:
            items = [
                SelectItem("markdown", "Markdown", f"Render markdown with {t.primary}"),
                SelectItem("text", "RichText", f"Styled text in {t.primary}"),
                SelectItem("table", "Table", f"Formatted tables ({t.primary} theme)"),
            ]
            lst = SelectList(items, 3, create_rich_theme(t))
            lst.on_select = self.show_rich_example
            self.tui.add_child(lst)
            self.tui.set_focus(lst)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(rich_footer(theme=t))

    def show_rich_example(self, item: SelectItem) -> None:
        """Show Rich component with current theme colors."""
        if self.overlay_handle:
            self.overlay_handle.hide()
        
        content = Container()
        t = self._theme()
        
        if item.value == "markdown":
            md = f"# {t.name}\n\n**Bold** and *italic* text.\n\n```python\nprint('Hello from {self.current_theme} theme')\n```"
            content.add_child(Markdown(md))
        elif item.value == "text":
            content.add_child(RichText(
                f"[bold {t.primary}]{t.name}[/bold {t.primary}] "
                f"[bold {t.secondary}]Theme[/bold {t.secondary}]!"
            ))
        elif item.value == "table":
            table = RichTable(title=f"{t.name}")
            table.add_column("Feature")
            table.add_column("Status", style=t.success)
            table.add_row("Markdown", "✓")
            table.add_row("Tables", "✓")
            content.add_child(table)
        
        self.overlay_handle = self.tui.show_overlay(
            content, OverlayOptions(width="70%", anchor="center")
        )

    def show_about(self) -> None:
        """About screen with Rich theming."""
        self._clear()
        self.current_screen = "about"
        t = self._theme()
        
        for comp in rich_header("About PyPiTUI", theme=t):
            self.tui.add_child(comp)
        
        self.tui.add_child(RichText(f"[{t.secondary}]PyPiTUI is a Python terminal UI library.[/{t.secondary}]"))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(rich_label("Features:", t))
        self.tui.add_child(RichText(f"  • [{t.primary}]Component-based architecture[/{t.primary}]"))
        self.tui.add_child(RichText(f"  • [{t.primary}]Differential rendering[/{t.primary}]"))
        self.tui.add_child(RichText(f"  • [{t.primary}]Overlay system[/{t.primary}]"))
        self.tui.add_child(RichText(f"  • [{t.primary}]Rich integration[/{t.primary}]"))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(RichText(f"[{t.muted}]https://github.com/jeremysball/pypitui[/{t.muted}]"))
        
        self.tui.add_child(Spacer(2))
        
        box = BorderedBox(padding_x=2, max_width=40)
        box.add_child(RichText(f"  [bold {t.primary}]Try the other demos![/bold {t.primary}]"))
        self.tui.add_child(box)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(rich_footer(theme=t))

    def show_result(self, message: str) -> None:
        """Show temporary result with Rich theming."""
        self._clear()
        self.current_screen = "result"
        t = self._theme()
        
        self.tui.add_child(RichText(message))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(rich_footer("Press any key", t))

    def handle_input(self, data: str) -> None:
        """Central input handler."""
        # Global quit
        if data.lower() == "q" and self.current_screen == "menu":
            self.running = False
            return
        
        # ESC: back or close overlay
        if matches_key(data, Key.escape):
            if self.tui.has_overlay():
                self.tui.hide_overlay()
                self.overlay_handle = None
            elif self.current_screen == "menu":
                self.running = False
            else:
                self.wizard_step = 0
                self.build_menu()
            return
        
        # Demo scene - any key exits
        if self.current_screen == "demoscene":
            self.animation_active = False
            self.build_menu()
            return
        
        # Wizard navigation
        if self.current_screen == "wizard":
            if matches_key(data, Key.left) and self.wizard_step > 0:
                self.wizard_step -= 1
                self.show_wizard()
                return
            
            if self.wizard_step == 1 and hasattr(self, 'name_input'):
                if matches_key(data, Key.tab):
                    new_focus = self.email_input if self.tui._focused_component == self.name_input else self.name_input
                    self.tui.set_focus(new_focus)
                    return
                elif matches_key(data, Key.enter):
                    self.form_data["name"] = self.name_input.get_value()
                    self.form_data["email"] = self.email_input.get_value()
                    self.advance_wizard()
                    return
            elif self.wizard_step == 0 and matches_key(data, Key.enter):
                self.advance_wizard()
                return
        
        # Pass to TUI for components
        self.tui.handle_input(data)

    def run(self) -> None:
        """Main loop at 60 FPS."""
        self.tui.start()
        frame_duration = 1.0 / 60.0
        
        try:
            while self.running:
                frame_start = time.time()
                
                data = self.terminal.read_sequence(timeout=0.001)
                if data:
                    self.handle_input(data)
                
                if self.animation_active:
                    if self.current_screen == "splash":
                        self.update_splash()
                    elif self.current_screen == "demoscene":
                        self.update_demoscene()
                
                self.tui.request_render()
                self.tui.render_frame()
                
                elapsed = time.time() - frame_start
                if elapsed < frame_duration:
                    time.sleep(frame_duration - elapsed)
        finally:
            self.tui.stop()


def main() -> None:
    """Entry point."""
    print("PyPiTUI Ultimate Demo - Full Rich Theme Integration")
    print("")
    UltimateDemoApp().run()
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
