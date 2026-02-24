#!/usr/bin/env python3
"""PyPiTUI Ultimate Demo - Feature-Complete Showcase.

A comprehensive demonstration of PyPiTUI capabilities with production-quality
code organization. Shows best practices for TUI application architecture.

Features:
- Splash screen with animation
- Multi-screen navigation
- Form wizard with validation
- Overlay system with positioning
- Rich integration (markdown, tables)
- Theme switching
- Keyboard handling patterns
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from pypitui import (
    TUI, Container, Text, Box, BorderedBox, Spacer,
    SelectList, SelectItem, SelectListTheme, Input,
    OverlayOptions, OverlayMargin, ProcessTerminal,
    matches_key, Key,
)
from pypitui.tui import Component

try:
    from pypitui.rich_components import Markdown, RichText, RichTable
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# =============================================================================
# THEME SYSTEM
# =============================================================================

@dataclass
class Theme:
    """Visual theme configuration."""
    name: str
    primary: str
    secondary: str
    accent: str
    muted: str
    success: str
    error: str
    bold: str = "\x1b[1m"
    reset: str = "\x1b[0m"


THEMES = {
    "neon": Theme(
        name="Cyberpunk Neon",
        primary="\x1b[96m",      # Bright cyan
        secondary="\x1b[95m",    # Bright magenta
        accent="\x1b[93m",       # Bright yellow
        muted="\x1b[90m",        # Gray
        success="\x1b[92m",      # Green
        error="\x1b[91m",        # Red
    ),
    "warm": Theme(
        name="Warm Sunset",
        primary="\x1b[33m",      # Yellow
        secondary="\x1b[31m",    # Red
        accent="\x1b[91m",       # Bright red
        muted="\x1b[90m",
        success="\x1b[32m",
        error="\x1b[31m",
    ),
    "ocean": Theme(
        name="Deep Ocean",
        primary="\x1b[34m",      # Blue
        secondary="\x1b[36m",    # Cyan
        accent="\x1b[96m",       # Bright cyan
        muted="\x1b[90m",
        success="\x1b[32m",
        error="\x1b[31m",
    ),
}


# =============================================================================
# UI HELPERS
# =============================================================================

def header(title: str, subtitle: str = "", theme: Theme | None = None) -> list[Component]:
    """Create a consistent header section with styling."""
    components: list[Component] = [Spacer(1)]
    
    # Use theme colors if provided
    if theme:
        title_styled = f"{theme.bold}{theme.primary}{title}{theme.reset}"
    else:
        title_styled = title
    
    box = BorderedBox(padding_x=2, padding_y=1, max_width=60, title=title_styled)
    if subtitle:
        if theme:
            sub_styled = f"{theme.muted}{subtitle}{theme.reset}"
        else:
            sub_styled = subtitle
        box.add_child(Text(sub_styled, 0, 0))
    components.append(box)
    components.append(Spacer(1))
    
    return components


def footer(text: str = "ESC to go back") -> Text:
    """Create a consistent footer."""
    return Text(f"\x1b[90m{text}\x1b[0m", 0, 0)


# =============================================================================
# DEMO MENU DATA
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
# MAIN APPLICATION
# =============================================================================

class UltimateDemoApp:
    """Feature-complete PyPiTUI demonstration."""

    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal, show_hardware_cursor=True)
        self.running = True
        self.current_screen = "menu"
        self.current_theme = "neon"
        self.wizard_step = 0
        self.form_data = {"name": "", "email": ""}
        self.overlay_handle = None
        self.animation_active = False
        self.splash_frame = 0
        
        self.build_menu()

    def _theme(self) -> Theme:
        """Get current theme."""
        return THEMES[self.current_theme]

    def _select_theme(self) -> SelectListTheme:
        """Create SelectList theme from current colors."""
        t = self._theme()
        return SelectListTheme(
            selected_prefix=lambda s: f"{t.primary}▶\x1b[0m ",
            selected_text=lambda s: f"\x1b[1m{s}\x1b[0m",
            description=lambda s: f"{t.muted}{s}\x1b[0m",
        )

    def _clear(self) -> None:
        """Clear screen preserving TUI state."""
        self.tui.clear()

    def build_menu(self) -> None:
        """Main menu screen."""
        self._clear()
        self.current_screen = "menu"
        self.animation_active = False
        
        for comp in header("🐍 PyPiTUI", "Terminal UI Framework", self._theme()):
            self.tui.add_child(comp)
        
        items = [
            SelectItem(key, label, desc)
            for key, label, desc in DEMO_ITEMS
        ]
        
        menu = SelectList(items, 7, self._select_theme())
        menu.on_select = self.on_menu_select
        self.tui.add_child(menu)
        self.tui.set_focus(menu)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(footer("↑↓ Navigate • Enter Select • Q Quit"))

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
        handler = handlers.get(item.value, self.build_menu)
        handler()

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
        self.tui.add_child(Text("\x1b[90m  Press any key to continue\x1b[0m", 0, 0))
        
        self.update_splash()

    def update_splash(self) -> None:
        """Update splash animation (called from main loop)."""
        if not self.animation_active:
            return
        
        # Only update every 500ms (2 FPS for animation)
        now = time.time()
        if not hasattr(self, '_last_animation_update'):
            self._last_animation_update = 0
        if now - self._last_animation_update < 0.5:
            return
        self._last_animation_update = now
        
        frames = ["✨", "⭐", "💫", "🌟"]
        icon = frames[self.splash_frame % len(frames)]
        
        box = BorderedBox(padding_x=3, padding_y=2, max_width=40, title=f"{icon} PyPiTUI")
        box.add_child(Text("Terminal UI Framework", 0, 0))
        box.add_child(Spacer(1))
        box.add_child(Text(f"{self._theme().accent}Beautiful Terminal Apps", 0, 0))
        
        self.splash_text.set_text("\n".join(box.render(40)))
        self.tui.request_render()
        
        self.splash_frame += 1

    def show_components(self) -> None:
        """Component showcase."""
        self._clear()
        self.current_screen = "components"
        t = self._theme()
        
        for comp in header("Component Showcase", theme=self._theme()):
            self.tui.add_child(comp)
        
        # Text component
        self.tui.add_child(Text(
            f"{t.bold}Text:[0m Auto-wraps content to fit width. "
            "This demonstrates word wrapping in action.",
            padding_x=2, padding_y=1
        ))
        self.tui.add_child(Spacer(1))
        
        # Box component
        self.tui.add_child(Text(f"{t.bold}Box (padding):[0m", 0, 0))
        box = Box(padding_x=2, padding_y=1)
        box.add_child(Text("Content with padding"))
        self.tui.add_child(box)
        self.tui.add_child(Spacer(1))
        
        # BorderedBox component
        self.tui.add_child(Text(f"{t.bold}BorderedBox (preferred):[0m", 0, 0))
        b = BorderedBox(padding_x=2, padding_y=1, max_width=50, title="Panel")
        b.add_child(Text("Draws borders, wraps content"))
        self.tui.add_child(b)
        self.tui.add_child(Spacer(1))
        
        # Input component
        self.tui.add_child(Text(f"{t.bold}Input:[0m", 0, 0))
        inp = Input(placeholder="Type and press Enter...")
        inp.on_submit = lambda v: self.show_result(f"You typed: {v}")
        self.tui.add_child(inp)
        self.tui.set_focus(inp)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(footer())

    def show_wizard(self) -> None:
        """Multi-step form wizard."""
        self._clear()
        self.current_screen = "wizard"
        t = self._theme()
        
        step_name, step_desc = WIZARD_STEPS[self.wizard_step]
        
        for comp in header(f"Wizard: {step_name}", step_desc, self._theme()):
            self.tui.add_child(comp)
        
        # Progress indicator
        progress = " → ".join(
            f"{t.primary if i == self.wizard_step else t.muted}{name}\x1b[0m"
            for i, (name, _) in enumerate(WIZARD_STEPS)
        )
        self.tui.add_child(Text(progress, 0, 0))
        self.tui.add_child(Spacer(2))
        
        if self.wizard_step == 0:
            self.tui.add_child(Text("This wizard demonstrates forms.", 0, 0))
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"{t.muted}Press Enter to start\x1b[0m", 0, 0))
            
        elif self.wizard_step == 1:
            self.tui.add_child(Text(f"{t.bold}Name:[0m", 0, 0))
            name = Input(placeholder="Your name")
            name.set_value(self.form_data["name"])
            self.tui.add_child(name)
            self.name_input = name
            
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"{t.bold}Email:[0m", 0, 0))
            email = Input(placeholder="Your email")
            email.set_value(self.form_data["email"])
            self.tui.add_child(email)
            self.email_input = email
            
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"{t.muted}Tab: switch • Enter: continue[0m", 0, 0))
            self.tui.set_focus(name)
            
        elif self.wizard_step == 2:
            self.tui.add_child(Text(f"{t.bold}Choose Theme:[0m", 0, 0))
            
            items = [SelectItem(k, v.name) for k, v in THEMES.items()]
            lst = SelectList(items, 3, self._select_theme())
            lst.on_select = lambda i: self.advance_wizard(theme=i.value)
            self.tui.add_child(lst)
            self.tui.set_focus(lst)
            
        else:  # Complete
            self.tui.add_child(Text(f"{t.success}✓ Setup Complete![0m", 0, 0))
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"Name: {self.form_data['name'] or '(none)'}", 0, 0))
            self.tui.add_child(Text(f"Email: {self.form_data['email'] or '(none)'}", 0, 0))
            self.tui.add_child(Text(f"Theme: {THEMES[self.form_data.get('theme', 'neon')].name}", 0, 0))

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
        """Overlay positioning demo."""
        self._clear()
        self.current_screen = "overlays"
        
        for comp in header("Overlay System", "Floating panels & dialogs", self._theme()):
            self.tui.add_child(comp)
        
        positions = [
            SelectItem("center", "Center", "Default centered"),
            SelectItem("top", "Top", "Top of screen"),
            SelectItem("bottom", "Bottom", "Bottom of screen"),
            SelectItem("top-right", "Top Right", "Upper right corner"),
        ]
        
        lst = SelectList(positions, 4, self._select_theme())
        lst.on_select = self.show_overlay_demo
        self.tui.add_child(lst)
        self.tui.set_focus(lst)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(footer())

    def show_overlay_demo(self, item: SelectItem) -> None:
        """Show example overlay."""
        if self.overlay_handle:
            self.overlay_handle.hide()
        
        anchors = {
            "center": "center",
            "top": "top",
            "bottom": "bottom",
            "top-right": "top-right",
        }
        anchor = anchors.get(item.value, "center")
        
        content = BorderedBox(
            padding_x=2, padding_y=1, max_width=35,
            title=f"{anchor.title()} Overlay"
        )
        content.add_child(Text(f"Positioned at {anchor}"))
        content.add_child(Text("Press ESC to close"))
        
        opts = OverlayOptions(width=35, anchor=anchor)
        self.overlay_handle = self.tui.show_overlay(content, opts)

    def show_themes(self) -> None:
        """Theme gallery."""
        self._clear()
        self.current_screen = "themes"
        
        for comp in header("Theme Gallery", theme=self._theme()):
            self.tui.add_child(comp)
        
        items = [
            SelectItem(k, v.name, f"Preview: {v.primary}████{v.secondary}████\x1b[0m")
            for k, v in THEMES.items()
        ]
        
        lst = SelectList(items, 3, self._select_theme())
        lst.on_select = self.apply_theme
        self.tui.add_child(lst)
        self.tui.set_focus(lst)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(footer())

    def apply_theme(self, item: SelectItem) -> None:
        """Apply selected theme and return to menu."""
        self.current_theme = item.value
        self.build_menu()

    def show_rich(self) -> None:
        """Rich integration demo."""
        self._clear()
        self.current_screen = "rich"
        t = self._theme()
        
        for comp in header("Rich Integration", theme=self._theme()):
            self.tui.add_child(comp)
        
        if not RICH_AVAILABLE:
            self.tui.add_child(Text(
                f"{t.error}Rich not installed. Run: pip install pypitui[rich][0m",
                0, 0
            ))
        else:
            items = [
                SelectItem("markdown", "Markdown", "Render markdown content"),
                SelectItem("text", "RichText", "Styled text markup"),
                SelectItem("table", "Table", "Formatted tables"),
            ]
            lst = SelectList(items, 3, self._select_theme())
            lst.on_select = self.show_rich_example
            self.tui.add_child(lst)
            self.tui.set_focus(lst)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(footer())

    def show_rich_example(self, item: SelectItem) -> None:
        """Show Rich component."""
        if self.overlay_handle:
            self.overlay_handle.hide()
        
        content = Container()
        
        if item.value == "markdown":
            md = "# Markdown\n\n**Bold** and *italic* text.\n\n```python\nprint('Hello')\n```"
            content.add_child(Markdown(md, padding_x=1, padding_y=1))
        elif item.value == "text":
            content.add_child(RichText(
                "[bold cyan]Styled[/bold cyan] [red]Text[/red]!",
                padding_x=1, padding_y=1
            ))
        elif item.value == "table":
            table = RichTable(title="Features", padding_x=1, padding_y=1)
            table.add_column("Name")
            table.add_column("Status")
            table.add_row("Markdown", "✓")
            table.add_row("Tables", "✓")
            content.add_child(table)
        
        self.overlay_handle = self.tui.show_overlay(
            content, OverlayOptions(width="70%", anchor="center")
        )

    def show_about(self) -> None:
        """About screen."""
        self._clear()
        self.current_screen = "about"
        t = self._theme()
        
        for comp in header("About PyPiTUI", theme=self._theme()):
            self.tui.add_child(comp)
        
        lines = [
            "PyPiTUI is a Python terminal UI library.",
            "",
            f"{t.bold}Features:[0m",
            "• Component-based architecture",
            "• Differential rendering",
            "• Overlay system",
            "• Rich integration",
            "",
            f"{t.muted}https://github.com/user/pypitui[0m",
        ]
        
        for line in lines:
            self.tui.add_child(Text(line, 0, 0))
        
        self.tui.add_child(Spacer(2))
        
        box = BorderedBox(padding_x=2, padding_y=1, max_width=50)
        box.add_child(Text(f"  {t.primary}Try the other demos![0m"))
        self.tui.add_child(box)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(footer())

    def show_result(self, message: str) -> None:
        """Show temporary result."""
        self._clear()
        self.current_screen = "result"
        
        self.tui.add_child(Text(message, 0, 0))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(footer("Press any key"))

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
                    # Toggle focus
                    new_focus = self.email_input if self.tui._focused_component == self.name_input else self.name_input
                    self.tui.set_focus(new_focus)
                    return
                elif matches_key(data, Key.enter):
                    # Submit form
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
                
                # Input
                data = self.terminal.read_sequence(timeout=0.001)
                if data:
                    self.handle_input(data)
                
                # Animation
                if self.animation_active:
                    self.update_splash()
                
                # Render
                self.tui.request_render()
                self.tui.render_frame()
                
                # Frame timing
                elapsed = time.time() - frame_start
                if elapsed < frame_duration:
                    time.sleep(frame_duration - elapsed)
        finally:
            self.tui.stop()


def main() -> None:
    """Entry point."""
    print("PyPiTUI Ultimate Demo")
    print("")
    UltimateDemoApp().run()
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
