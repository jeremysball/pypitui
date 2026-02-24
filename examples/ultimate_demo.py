#!/usr/bin/env python3
"""PyPiTUI Ultimate Demo - Full Rich Theme Integration

Demonstrates how to use Rich markup to theme the ENTIRE UI.
All text uses Rich markup instead of raw ANSI codes, making
the entire interface themeable through Rich's style system.
"""

from __future__ import annotations

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
    from pypitui.rich_components import Markdown, RichText, RichTable
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
# RICH UI HELPERS - Everything uses Rich markup
# =============================================================================

def rich_header(title: str, subtitle: str = "", theme: RichTheme | None = None) -> list[Component]:
    """Create header using RichText for full theme integration.
    
    GOTCHA: BorderedBox title can't use Rich markup directly,
    so we use RichText for the subtitle inside the box.
    """
    components: list[Component] = [Spacer(1)]
    
    t = theme or THEMES["neon"]
    
    # Title goes in BorderedBox title (uses plain text with ANSI fallback)
    # Subtitle uses RichText inside for full theming
    box = BorderedBox(padding_x=2, max_width=45, title=title)
    
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
    """Create SelectList theme using Rich markup.
    
    PATTERN: Even SelectList items can use Rich colors!
    The ▶ prefix and selected text get theme colors.
    """
    return SelectListTheme(
        selected_prefix=lambda s: f"▶ ",
        selected_text=lambda s: f"[bold {theme.primary}]{s}[/bold {theme.primary}]",
        description=lambda s: f"[{theme.muted}]{s}[/{theme.muted}]",
    )


# =============================================================================
# DEMO DATA
# =============================================================================

DEMO_ITEMS = [
    ("splash", "🎨 Splash", "Animated intro"),
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
        self.tui.add_child(RichText(f"[{t.muted}]https://github.com/user/pypitui[/{t.muted}]"))
        
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
                    self.update_splash()
                
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
