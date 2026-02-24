#!/usr/bin/env python3
"""PyPiTUI Educational Demo - LLM Learning Guide

This demo teaches agents how to build PyPiTUI applications correctly.
Focuses on patterns, not visual effects.

KEY PATTERNS DEMONSTRATED:
1. TUI lifecycle (start/stop/render loop)
2. Screen management (clear/build pattern)
3. Full Rich theme integration (not just ANSI colors)
4. Component hierarchy and composition
5. Event handling and routing
6. State management

CRITICAL LESSONS:
- Always reuse TUI instance (use tui.clear(), not new TUI())
- Use Rich markup [color] instead of ANSI codes \x1b[32m
- Rich themes affect the ENTIRE UI, not just one component
- Form state persists across screens via instance variables
"""

import time
from dataclasses import dataclass

from pypitui import (
    TUI, Container, Text, Box, BorderedBox, Spacer,
    SelectList, SelectItem, SelectListTheme, Input,
    OverlayOptions, ProcessTerminal, matches_key, Key,
)

try:
    from pypitui.rich_components import RichText, RichTable
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# =============================================================================
# THEME SYSTEM - Rich markup (not ANSI codes)
# =============================================================================

@dataclass
class Theme:
    """Theme using Rich color names, not ANSI codes.
    
    WHY: Rich markup [bright_cyan]text[/bright_cyan] is:
    - More readable than \x1b[96m
    - Portable across terminals
    - Composable (can nest styles)
    """
    name: str
    primary: str      # e.g., "bright_cyan"
    secondary: str    # e.g., "bright_magenta"
    muted: str        # e.g., "dim"


THEMES = {
    "neon": Theme("Cyberpunk", "bright_cyan", "bright_magenta", "dim"),
    "warm": Theme("Sunset", "yellow", "red", "dim"),
}


# =============================================================================
# RICH UI HELPERS - Theme everything
# =============================================================================

def themed_header(title: str, subtitle: str, theme: Theme) -> list:
    """Create header with Rich theming.
    
    PATTERN: Use RichText with markup [color]text[/color]
    instead of f"{theme.primary}text{theme.reset}".
    """
    components = [Spacer(1)]
    
    box = BorderedBox(padding_x=2, max_width=40, title=title)
    if subtitle:
        # RichText gets theme styling
        box.add_child(RichText(f"[{theme.muted}]{subtitle}[/{theme.muted}]"))
    components.append(box)
    components.append(Spacer(1))
    
    return components


def themed_label(text: str, theme: Theme) -> RichText:
    """Bold label using Rich markup."""
    return RichText(f"[bold {theme.primary}]{text}[/bold {theme.primary}]")


def themed_list_theme(theme: Theme) -> SelectListTheme:
    """Create SelectList theme using Rich colors.
    
    PATTERN: Even list items use Rich markup for consistency.
    """
    return SelectListTheme(
        selected_prefix=lambda s: "▶ ",
        selected_text=lambda s: f"[bold {theme.primary}]{s}[/bold {theme.primary}]",
        description=lambda s: f"[{theme.muted}]{s}[/{theme.muted}]",
    )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class DemoApp:
    """Educational demo showing proper PyPiTUI patterns."""

    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal, show_hardware_cursor=True)
        self.running = True
        self.current_screen = "menu"
        self.theme_name = "neon"
        self.form_data = {"name": "", "email": ""}
        
        self.build_menu()

    def _theme(self) -> Theme:
        """Get current theme."""
        return THEMES[self.theme_name]

    def _clear(self) -> None:
        """Clear screen preserving TUI state.
        
        CRITICAL: Use tui.clear(), NOT 'self.tui = TUI(terminal)'
        Creating new TUI instances breaks differential rendering.
        """
        self.tui.clear()

    def build_menu(self) -> None:
        """Main menu with full Rich theming."""
        self._clear()
        self.current_screen = "menu"
        
        t = self._theme()
        
        # Header with Rich subtitle
        for comp in themed_header("🐍 PyPiTUI", "Rich Theme Demo", t):
            self.tui.add_child(comp)
        
        # Menu with themed items
        items = [
            SelectItem("rich", "Rich Integration", f"All UI uses {t.primary} theme"),
            SelectItem("form", "Form Example", "Multi-step with validation"),
        ]
        
        menu = SelectList(items, 2, themed_list_theme(t))
        menu.on_select = self.on_select
        self.tui.add_child(menu)
        self.tui.set_focus(menu)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(RichText(f"[{t.muted}]Q to quit[/{t.muted}]"))

    def on_select(self, item: SelectItem) -> None:
        """Route menu selection."""
        if item.value == "rich":
            self.show_rich()
        elif item.value == "form":
            self.show_form()

    def show_rich(self) -> None:
        """Demonstrate full Rich theme integration.
        
        KEY INSIGHT: Rich themes affect EVERYTHING:
        - Headers use RichText for subtitles
        - Labels use Rich markup
        - List items use Rich colors
        - Even static text uses theme colors
        """
        self._clear()
        self.current_screen = "rich"
        t = self._theme()
        
        for comp in themed_header("Rich Demo", f"Theme: {t.name}", t):
            self.tui.add_child(comp)
        
        if not RICH_AVAILABLE:
            self.tui.add_child(Text("pip install pypitui[rich]"))
        else:
            # Everything uses Rich markup with theme colors
            self.tui.add_child(themed_label("Themed Labels:", t))
            self.tui.add_child(RichText(f"  Primary: [{t.primary}]This is primary[/{t.primary}]"))
            self.tui.add_child(RichText(f"  Secondary: [{t.secondary}]This is secondary[/{t.secondary}]"))
            self.tui.add_child(Spacer(1))
            
            # Theme switcher
            self.tui.add_child(themed_label("Switch Theme:", t))
            items = [
                SelectItem("neon", "Cyberpunk", f"[{THEMES['neon'].primary}]Cyan/Magenta[/{THEMES['neon'].primary}]"),
                SelectItem("warm", "Sunset", f"[{THEMES['warm'].primary}]Yellow/Red[/{THEMES['warm'].primary}]"),
            ]
            lst = SelectList(items, 2, themed_list_theme(t))
            lst.on_select = lambda i: self.set_theme(i.value)
            self.tui.add_child(lst)
            self.tui.set_focus(lst)
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(RichText(f"[{t.muted}]ESC to return[/{t.muted}]"))

    def set_theme(self, name: str) -> None:
        """Change theme and refresh."""
        self.theme_name = name
        self.build_menu()

    def show_form(self) -> None:
        """Form with validation and state persistence."""
        self._clear()
        self.current_screen = "form"
        t = self._theme()
        
        for comp in themed_header("Form Demo", "Enter your details", t):
            self.tui.add_child(comp)
        
        # Form fields with themed labels
        self.tui.add_child(themed_label("Name:", t))
        name = Input(placeholder="Your name")
        name.set_value(self.form_data["name"])
        self.tui.add_child(name)
        self.name_input = name
        
        self.tui.add_child(Spacer(1))
        self.tui.add_child(themed_label("Email:", t))
        email = Input(placeholder="Your email")
        email.set_value(self.form_data["email"])
        self.tui.add_child(email)
        self.email_input = email
        
        # Submit button pattern
        def on_submit(value: str):
            self.form_data["name"] = self.name_input.get_value()
            self.form_data["email"] = self.email_input.get_value()
            self.show_result(f"Hello, {self.form_data['name']}!")
        
        name.on_submit = on_submit
        email.on_submit = on_submit
        
        self.tui.set_focus(name)
        self.tui.add_child(Spacer(1))
        self.tui.add_child(RichText(f"[{t.muted}]Tab: switch • Enter: submit[/{t.muted}]"))

    def show_result(self, message: str) -> None:
        """Show result with themed styling."""
        self._clear()
        self.current_screen = "result"
        t = self._theme()
        
        self.tui.add_child(RichText(f"[bold {t.primary}]{message}[/bold {t.primary}]"))
        self.tui.add_child(Spacer(1))
        self.tui.add_child(RichText(f"[{t.muted}]Press any key[/{t.muted}]"))

    def handle_input(self, data: str) -> None:
        """Central input handler.
        
        PATTERN: Check global keys first, then route to screen-specific,
        finally pass to focused component.
        """
        # Global: Quit
        if data.lower() == "q" and self.current_screen == "menu":
            self.running = False
            return
        
        # Global: ESC returns to menu
        if matches_key(data, Key.escape):
            self.build_menu()
            return
        
        # Global: Tab navigation in forms
        if self.current_screen == "form" and matches_key(data, Key.tab):
            if hasattr(self, 'name_input'):
                new_focus = self.email_input if self.tui._focused_component == self.name_input else self.name_input
                self.tui.set_focus(new_focus)
                return
        
        # Pass to TUI for component handling
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
                
                self.tui.request_render()
                self.tui.render_frame()
                
                elapsed = time.time() - frame_start
                if elapsed < frame_duration:
                    time.sleep(frame_duration - elapsed)
        finally:
            self.tui.stop()


def main() -> None:
    """Entry point."""
    print("PyPiTUI Educational Demo")
    print("")
    DemoApp().run()
    print("\nDone!")


if __name__ == "__main__":
    main()
