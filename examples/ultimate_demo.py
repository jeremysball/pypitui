#!/usr/bin/env python3
"""The Ultimate PyPiTUI Demo - Showcasing all features."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from pypitui import (
    TUI,
    Container,
    Text,
    Box,
    BorderedBox,
    Spacer,
    SelectList,
    SelectItem,
    SelectListTheme,
    Input,
    OverlayOptions,
    OverlayMargin,
    ProcessTerminal,
    matches_key,
    Key,
)
from pypitui.tui import Component

# Try to import rich components
try:
    from pypitui.rich_components import Markdown, RichText, RichTable

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ============================================================================
# COLOR PALETTE - Beautiful ANSI colors
# ============================================================================


class Colors:
    """ANSI color utilities."""

    # Standard colors
    BLACK = "\x1b[30m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"

    # Bright colors
    BRIGHT_BLACK = "\x1b[90m"
    BRIGHT_RED = "\x1b[91m"
    BRIGHT_GREEN = "\x1b[92m"
    BRIGHT_YELLOW = "\x1b[93m"
    BRIGHT_BLUE = "\x1b[94m"
    BRIGHT_MAGENTA = "\x1b[95m"
    BRIGHT_CYAN = "\x1b[96m"
    BRIGHT_WHITE = "\x1b[97m"

    # Background colors
    BG_BLACK = "\x1b[40m"
    BG_RED = "\x1b[41m"
    BG_GREEN = "\x1b[42m"
    BG_YELLOW = "\x1b[43m"
    BG_BLUE = "\x1b[44m"
    BG_MAGENTA = "\x1b[45m"
    BG_CYAN = "\x1b[46m"
    BG_WHITE = "\x1b[47m"

    # Styles
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    ITALIC = "\x1b[3m"
    UNDERLINE = "\x1b[4m"
    BLINK = "\x1b[5m"
    REVERSE = "\x1b[7m"
    STRIKETHROUGH = "\x1b[9m"

    # Reset
    RESET = "\x1b[0m"

    @staticmethod
    def hex_fg(r: int, g: int, b: int) -> str:
        """Create 256-color foreground from RGB."""
        return f"\x1b[38;2;{r};{g};{b}m"

    @staticmethod
    def hex_bg(r: int, g: int, b: int) -> str:
        """Create 256-color background from RGB."""
        return f"\x1b[48;2;{r};{g};{b}m"

    @staticmethod
    def gradient_line(text: str, start_rgb: tuple, end_rgb: tuple) -> str:
        """Create a gradient-colored line."""
        if not text:
            return text

        result = []
        length = len(text)
        for i, char in enumerate(text):
            ratio = i / max(1, length - 1)
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            result.append(f"\x1b[38;2;{r};{g};{b}m{char}")

        return "".join(result) + Colors.RESET


# ============================================================================
# THEMES
# ============================================================================


def create_neon_theme() -> SelectListTheme:
    """Cyberpunk neon theme."""
    return SelectListTheme(
        selected_prefix=lambda s: f"{Colors.CYAN}▶{Colors.RESET}",
        selected_text=lambda s: f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{s}{Colors.RESET}",
        description=lambda s: f"{Colors.DIM}{Colors.CYAN}{s}{Colors.RESET}",
        scroll_info=lambda s: f"{Colors.DIM}{s}{Colors.RESET}",
        no_match=lambda s: f"{Colors.DIM}{s}{Colors.RESET}",
    )


def create_warm_theme() -> SelectListTheme:
    """Warm sunset theme."""
    return SelectListTheme(
        selected_prefix=lambda s: f"{Colors.YELLOW}→{Colors.RESET}",
        selected_text=lambda s: f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}{s}{Colors.RESET}",
        description=lambda s: f"{Colors.DIM}{Colors.YELLOW}{s}{Colors.RESET}",
        scroll_info=lambda s: f"{Colors.DIM}{s}{Colors.RESET}",
        no_match=lambda s: f"{Colors.DIM}{s}{Colors.RESET}",
    )


def create_ocean_theme() -> SelectListTheme:
    """Deep ocean theme."""
    return SelectListTheme(
        selected_prefix=lambda s: f"{Colors.BLUE}❯{Colors.RESET}",
        selected_text=lambda s: f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{s}{Colors.RESET}",
        description=lambda s: f"{Colors.DIM}{Colors.BLUE}{s}{Colors.RESET}",
        scroll_info=lambda s: f"{Colors.DIM}{s}{Colors.RESET}",
        no_match=lambda s: f"{Colors.DIM}{s}{Colors.RESET}",
    )


# ============================================================================
# UI BUILDERS
# ============================================================================


def create_header(text: str, subtitle: str = "") -> list[Component]:
    """Create a beautiful header section."""
    components: list[Component] = []

    # Top border with gradient
    border = "═" * min(50, len(text) + 8)
    gradient_border = Colors.gradient_line(border, (255, 100, 100), (100, 200, 255))
    components.append(Text(gradient_border, 0, 0))

    # Title
    title_text = f"  {Colors.BOLD}{Colors.BRIGHT_WHITE}{text}{Colors.RESET}  "
    components.append(Text(title_text, 0, 0))

    if subtitle:
        sub_text = f"  {Colors.DIM}{Colors.WHITE}{subtitle}{Colors.RESET}  "
        components.append(Text(sub_text, 0, 0))

    # Bottom border
    components.append(Text(gradient_border, 0, 0))

    return components


def create_footer(
    message: str = "ESC: Back  •  ↑↓: Navigate  •  Enter: Select",
) -> Text:
    """Create a footer with help text."""
    return Text(
        f"{Colors.DIM}{Colors.WHITE}{message}{Colors.RESET}",
        padding_x=1,
        padding_y=0,
    )


# ============================================================================
# DEMO DATA
# ============================================================================

DEMO_MENU_ITEMS = [
    SelectItem("splash", "🎨 Splash Screen", "Animated intro sequence"),
    SelectItem("components", "🧩 Component Showcase", "All UI components"),
    SelectItem("inputs", "⌨️  Input Forms", "Text input with validation"),
    SelectItem("overlays", "🪟 Overlay System", "Floating panels & dialogs"),
    SelectItem("themes", "🎨 Theme Gallery", "Visual style variations"),
    SelectItem("rich", "✨ Rich Integration", "Markdown & formatted text"),
    SelectItem("about", "ℹ️  About", "Library information"),
]

WIZARD_STEPS = [
    ("Welcome", "Let's set up your preferences"),
    ("Profile", "Enter your details"),
    ("Theme", "Choose your style"),
    ("Complete", "You're all set!"),
]


# ============================================================================
# SPLASH SCREEN ANIMATION
# ============================================================================

# Splash screen animation frames - using BorderedBox instead of manual box drawing
SPLASH_ICONS = ["🖥️", "🎨", "🚀"]
SPLASH_EMOJIS = ["✨", "⚡", "🔥"]


# ============================================================================
# ULTIMATE DEMO APPLICATION
# ============================================================================


class UltimateDemoApp:
    """The ultimate PyPiTUI demo application."""

    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal, show_hardware_cursor=True)
        self.running = True
        self.current_screen = "menu"
        self.previous_screen = "menu"
        self.theme = create_neon_theme()
        self.wizard_step = 0
        self.overlay_handle = None
        self.splash_frame = 0
        self.last_update = time.time()
        self.animation_active = False

        # Form data
        self.form_data = {
            "name": "",
            "email": "",
            "theme": "neon",
        }

        # Build initial screen
        self.build_menu()

    def _clear_screen(self) -> None:
        """Clear content while preserving differential rendering state."""
        self.tui.clear()

    def build_menu(self) -> None:
        """Build the main menu screen."""
        self._clear_screen()
        self.current_screen = "menu"
        self.animation_active = False

        # Logo header using BorderedBox with constrained width
        logo_box = BorderedBox(padding_x=2, padding_y=0, max_width=50, title="🐍 PyPiTUI 🖥️")
        logo_box.add_child(Text("Terminal UI Framework", 0, 0))
        self.tui.add_child(logo_box)

        self.tui.add_child(Spacer(1))

        # Menu title
        self.tui.add_child(
            Text(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}    Main Menu{Colors.RESET}", 0, 0)
        )
        self.tui.add_child(
            Text(f"{Colors.DIM}    Select a demo to explore{Colors.RESET}", 0, 0)
        )
        self.tui.add_child(Spacer(1))

        # Menu list
        menu = SelectList(DEMO_MENU_ITEMS, 7, self.theme)
        menu.on_select = self.on_menu_select
        self.tui.add_child(menu)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(create_footer("↑↓ Navigate  •  Enter Select  •  Q Quit"))

        self.tui.set_focus(menu)
        self.tui.request_render(force=True)

    def on_menu_select(self, item: SelectItem) -> None:
        """Handle menu selection."""
        if item.value == "splash":
            self.show_splash()
        elif item.value == "components":
            self.show_components()
        elif item.value == "inputs":
            self.show_inputs()
        elif item.value == "overlays":
            self.show_overlay_demo()
        elif item.value == "themes":
            self.show_theme_gallery()
        elif item.value == "rich":
            self.show_rich_demo()
        elif item.value == "about":
            self.show_about()

    def show_splash(self) -> None:
        """Show animated splash screen."""
        # Guard: don't restart if already showing splash
        if self.current_screen == "splash" and self.animation_active:
            return

        self._clear_screen()
        self.current_screen = "splash"
        self.animation_active = True
        self.splash_frame = 0
        self.last_update = time.time()
        self.frame_count = 0  # For 60 FPS timing

        self.tui.add_child(Spacer(3))

        # Title using BorderedBox with constrained width
        self.splash_box = BorderedBox(padding_x=2, padding_y=0, max_width=50, title="🐍 PyPiTUI 🖥️")
        self.splash_box.add_child(Text("Terminal UI Framework", 0, 0))
        self.tui.add_child(self.splash_box)

        self.tui.add_child(Spacer(2))
        self.splash_subtitle = Text(f"{Colors.DIM}    Watch the animation...{Colors.RESET}", 0, 0)
        self.tui.add_child(self.splash_subtitle)
        self.tui.add_child(Spacer(1))
        self.tui.add_child(create_footer("Press any key to continue"))

        self.update_splash()

    def update_splash(self) -> None:
        """Update splash screen animation at 60 FPS."""
        if not self.animation_active:
            return

        now = time.time()
        # 60 FPS = ~16.67ms per frame, but we use every 10th frame for animation
        # so the text animation cycles at ~6 FPS while maintaining 60 FPS updates
        frame_duration = 1.0 / 60.0

        if now - self.last_update >= frame_duration:
            self.last_update = now
            self.frame_count += 1

            # Update animation every 10 frames (~6 FPS for text animation)
            if self.frame_count % 10 == 0:
                self.splash_frame = (self.splash_frame + 1) % len(SPLASH_ICONS)

                # Update the BorderedBox content dynamically
                icon = SPLASH_ICONS[self.splash_frame]
                emoji = SPLASH_EMOJIS[self.splash_frame]
                self.splash_box.clear()
                self.splash_box.add_child(Text(f"{icon} Terminal UI {icon}", 0, 0))
                self.splash_subtitle.set_text(f"    {emoji} {Colors.DIM}Watch the animation...{Colors.RESET} {emoji}")
                self.tui.request_render()
            else:
                # Still request render at 60 FPS for smooth display
                self.tui.request_render()

    def show_components(self) -> None:
        """Show all UI components."""
        self._clear_screen()
        self.current_screen = "components"

        for comp in create_header("Component Showcase"):
            self.tui.add_child(comp)

        self.tui.add_child(Spacer(1))

        # Text component examples
        self.tui.add_child(
            Text(
                f"{Colors.BOLD}Text Component:{Colors.RESET} Multi-line text with automatic wrapping",
                0,
                0,
            )
        )

        wrapped_text = (
            "This demonstrates the Text component's word wrapping capabilities. "
            "Long text automatically wraps to fit the available width while preserving "
            "the content meaning and readability."
        )
        self.tui.add_child(Text(wrapped_text, 2, 1))

        self.tui.add_child(Spacer(1))

        # Box component
        self.tui.add_child(
            Text(
                f"{Colors.BOLD}Box Component:{Colors.RESET} Container with padding",
                0,
                0,
            )
        )

        box = Box(2, 1)
        box.add_child(
            Text(f"{Colors.CYAN}Content inside a padded box{Colors.RESET}", 0, 0)
        )
        box.set_bg_fn(lambda s: f"{Colors.BG_BLACK}{s}{Colors.RESET}")
        self.tui.add_child(box)

        self.tui.add_child(Spacer(1))

        # Spacer demo
        self.tui.add_child(
            Text(
                f"{Colors.BOLD}Spacer:{Colors.RESET} Adjustable vertical spacing (above)",
                0,
                0,
            )
        )

        self.tui.add_child(create_footer())

    def show_inputs(self) -> None:
        """Show form input wizard."""
        self._clear_screen()
        self.current_screen = "inputs"

        step_title, step_desc = WIZARD_STEPS[self.wizard_step]

        for comp in create_header(f"Wizard: {step_title}", step_desc):
            self.tui.add_child(comp)

        self.tui.add_child(Spacer(1))

        # Progress indicator
        progress = " → ".join(
            [
                f"{Colors.BRIGHT_CYAN if i == self.wizard_step else Colors.DIM}{name}{Colors.RESET}"
                for i, (name, _) in enumerate(WIZARD_STEPS)
            ]
        )
        self.tui.add_child(Text(progress, 0, 0))

        self.tui.add_child(Spacer(2))

        if self.wizard_step == 0:
            # Welcome step - auto-advance to profile step immediately
            self.wizard_step = 1
            self.show_inputs()
            return

        elif self.wizard_step == 1:
            # Profile step
            self.tui.add_child(Text(f"{Colors.BOLD}Name:{Colors.RESET}", 0, 0))

            name_input = Input(placeholder="Enter your name...")
            name_input.set_value(self.form_data["name"])
            self.tui.add_child(name_input)

            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"{Colors.BOLD}Email:{Colors.RESET}", 0, 0))

            email_input = Input(placeholder="Enter your email...")
            email_input.set_value(self.form_data["email"])
            self.tui.add_child(email_input)
            
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text(f"{Colors.DIM}Press Enter to continue{Colors.RESET}", 0, 0))
            
            # Store inputs for Tab navigation
            self.name_input = name_input
            self.email_input = email_input
            
            # Focus the first empty input
            if not self.form_data["name"]:
                self.tui.set_focus(name_input)
            elif not self.form_data["email"]:
                self.tui.set_focus(email_input)
            else:
                self.tui.set_focus(name_input)

        elif self.wizard_step == 2:
            # Theme step
            self.tui.add_child(Text(f"{Colors.BOLD}Select Theme:{Colors.RESET}", 0, 0))

            theme_items = [
                SelectItem("neon", "Cyberpunk Neon", "Cyan highlights on dark"),
                SelectItem("warm", "Warm Sunset", "Yellow and orange tones"),
                SelectItem("ocean", "Deep Ocean", "Blue underwater theme"),
            ]

            theme_list = SelectList(theme_items, 3, self.theme)
            theme_list.on_select = lambda item: self.advance_wizard(theme=item.value)
            self.tui.add_child(theme_list)
            self.tui.set_focus(theme_list)

        elif self.wizard_step == 3:
            # Complete step
            self.tui.add_child(
                Text(
                    f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓ Setup Complete!{Colors.RESET}",
                    0,
                    0,
                )
            )
            self.tui.add_child(Spacer(1))

            summary = [
                f"Name:  {self.form_data['name'] or '(not set)'}",
                f"Email: {self.form_data['email'] or '(not set)'}",
                f"Theme: {self.form_data['theme']}",
            ]
            for line in summary:
                self.tui.add_child(Text(f"  {Colors.DIM}{line}{Colors.RESET}", 0, 0))

            self.tui.add_child(Spacer(1))
            self.tui.add_child(
                Text(
                    f"{Colors.DIM}Press Enter to restart wizard...{Colors.RESET}", 0, 0
                )
            )

        self.tui.add_child(Spacer(1))

        # Navigation hints
        nav_text = "Tab: Next field  •  Enter: Continue"
        if self.wizard_step > 0:
            nav_text = "←: Previous  •  " + nav_text
        self.tui.add_child(create_footer(nav_text))

    def advance_wizard(self, **kwargs) -> None:
        """Advance to next wizard step."""
        # Update form data
        self.form_data.update(kwargs)

        # Move to next step or loop
        if self.wizard_step < len(WIZARD_STEPS) - 1:
            self.wizard_step += 1
        else:
            self.wizard_step = 0
            self.form_data = {"name": "", "email": "", "theme": "neon"}

        self.show_inputs()

    def show_overlay_demo(self) -> None:
        """Show overlay system demo."""
        self._clear_screen()
        self.current_screen = "overlays"

        for comp in create_header("Overlay System"):
            self.tui.add_child(comp)

        self.tui.add_child(Spacer(1))

        self.tui.add_child(Text(f"{Colors.BOLD}Overlay Positions:{Colors.RESET}", 0, 0))

        demo_items = [
            SelectItem("center", "Center", "Standard centered overlay"),
            SelectItem("top-left", "Top Left", "Anchored to top-left"),
            SelectItem("top-right", "Top Right", "Anchored to top-right"),
            SelectItem("bottom-left", "Bottom Left", "Anchored to bottom-left"),
            SelectItem("bottom-right", "Bottom Right", "Anchored to bottom-right"),
            SelectItem("custom", "Custom", "With offset and margin"),
            SelectItem("stacked", "Stacked", "Multiple overlays"),
        ]

        overlay_menu = SelectList(demo_items, 7, self.theme)
        overlay_menu.on_select = self.on_overlay_select
        self.tui.add_child(overlay_menu)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(create_footer("ESC closes overlay"))

        self.tui.set_focus(overlay_menu)

    def on_overlay_select(self, item: SelectItem) -> None:
        """Handle overlay demo selection."""
        anchor = item.value

        if anchor == "stacked":
            # Show multiple stacked overlays
            for i, (a, offset) in enumerate(
                [
                    ("center", 0),
                    ("center", 2),
                    ("center", 4),
                ]
            ):
                content = self.create_overlay_content(f"Overlay {i+1}")
                opts = OverlayOptions(
                    width=40,
                    anchor=a,
                    offset_x=offset * 2,
                    offset_y=offset,
                )
                self.tui.show_overlay(content, opts)
        elif anchor == "custom":
            content = self.create_overlay_content("Custom Position")
            opts = OverlayOptions(
                width=35,
                anchor="center",
                offset_x=5,
                offset_y=2,
                margin=OverlayMargin(top=2, left=4, bottom=2, right=4),
            )
            self.tui.show_overlay(content, opts)
        else:
            content = self.create_overlay_content(f"{anchor.title()} Overlay")
            opts = OverlayOptions(width=35, anchor=anchor)
            self.tui.show_overlay(content, opts)

    def create_overlay_content(self, title: str) -> BorderedBox:
        """Create overlay content using BorderedBox."""
        box = BorderedBox(padding_x=1, padding_y=0, max_width=40, title=title)
        box.add_child(Text("This overlay is positioned", 0, 0))
        box.add_child(Text("using OverlayOptions.", 0, 0))
        box.add_child(Text("", 0, 0))
        box.add_child(Text("Press ESC to close", 0, 0))
        return box

    def show_theme_gallery(self) -> None:
        """Show theme gallery."""
        self._clear_screen()
        self.current_screen = "themes"

        for comp in create_header("Theme Gallery"):
            self.tui.add_child(comp)

        self.tui.add_child(Spacer(1))

        self.tui.add_child(
            Text(f"{Colors.BOLD}Select a theme to preview:{Colors.RESET}", 0, 0)
        )

        theme_items = [
            SelectItem("neon", "Cyberpunk Neon", "Cyan and magenta highlights"),
            SelectItem("warm", "Warm Sunset", "Orange and yellow tones"),
            SelectItem("ocean", "Deep Ocean", "Blue and teal shades"),
        ]

        theme_list = SelectList(theme_items, 3, self.theme)
        theme_list.on_select = self.on_theme_select
        self.tui.add_child(theme_list)

        self.tui.add_child(Spacer(2))
        self.tui.add_child(
            Text(
                f"{Colors.DIM}Current theme: {self.get_theme_name()}{Colors.RESET}",
                0,
                0,
            )
        )

        # Color palette preview
        self.tui.add_child(Spacer(1))
        self.tui.add_child(Text(f"{Colors.BOLD}Color Palette:{Colors.RESET}", 0, 0))

        palette = (
            f"{Colors.RED}■{Colors.RESET} "
            f"{Colors.YELLOW}■{Colors.RESET} "
            f"{Colors.GREEN}■{Colors.RESET} "
            f"{Colors.CYAN}■{Colors.RESET} "
            f"{Colors.BLUE}■{Colors.RESET} "
            f"{Colors.MAGENTA}■{Colors.RESET} "
            f"{Colors.WHITE}■{Colors.RESET}"
        )
        self.tui.add_child(Text(f"  {palette}", 0, 0))

        self.tui.add_child(Spacer(1))
        self.tui.add_child(create_footer())

        self.tui.set_focus(theme_list)

    def get_theme_name(self) -> str:
        """Get current theme name."""
        if self.theme == create_neon_theme():
            return "Cyberpunk Neon"
        elif self.theme == create_warm_theme():
            return "Warm Sunset"
        else:
            return "Deep Ocean"

    def on_theme_select(self, item: SelectItem) -> None:
        """Apply selected theme."""
        if item.value == "neon":
            self.theme = create_neon_theme()
        elif item.value == "warm":
            self.theme = create_warm_theme()
        elif item.value == "ocean":
            self.theme = create_ocean_theme()

        self.show_theme_gallery()

    def show_rich_demo(self) -> None:
        """Show Rich integration demo."""
        self._clear_screen()
        self.current_screen = "rich"

        for comp in create_header("Rich Integration"):
            self.tui.add_child(comp)

        self.tui.add_child(Spacer(1))

        if not RICH_AVAILABLE:
            self.tui.add_child(
                Text(f"{Colors.RED}Rich library not installed.{Colors.RESET}", 0, 0)
            )
            self.tui.add_child(Spacer(1))
            self.tui.add_child(Text("Install with: pip install pypitui[rich]", 0, 0))
        else:
            self.tui.add_child(
                Text(f"{Colors.GREEN}✓{Colors.RESET} Rich library is available!", 0, 0)
            )
            self.tui.add_child(Spacer(1))

            self.tui.add_child(
                Text(f"{Colors.BOLD}Available Components:{Colors.RESET}", 0, 0)
            )

            rich_items = [
                SelectItem("markdown", "Markdown", "Render markdown content"),
                SelectItem("richtext", "RichText", "Styled text markup"),
                SelectItem("table", "RichTable", "Formatted tables"),
            ]

            rich_list = SelectList(rich_items, 3, self.theme)
            rich_list.on_select = self.on_rich_select
            self.tui.add_child(rich_list)
            self.tui.set_focus(rich_list)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(create_footer())

    def on_rich_select(self, item: SelectItem) -> None:
        """Show Rich component overlay."""
        if not RICH_AVAILABLE:
            return

        # Hide any existing overlay first
        if self.overlay_handle:
            self.overlay_handle.hide()
            self.overlay_handle = None

        content = Container()

        if item.value == "markdown":
            md_text = """# Markdown Demo

This is **bold** and *italic* text.

## Code Block
```python
from pypitui import TUI
print("Hello!")
```

- Bullet points
- Are supported too
"""
            content.add_child(Markdown(md_text, padding_x=1, padding_y=1))

        elif item.value == "richtext":
            rt_text = "[bold cyan]Rich[/bold cyan] [red]Text[/red] [green]Demo[/green]!"
            content.add_child(RichText(rt_text, padding_x=1, padding_y=1))

        elif item.value == "table":
            table = RichTable(title="Demo Table", padding_x=1, padding_y=1)
            table.add_column("Name", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Feature 1", "✓")
            table.add_row("Feature 2", "✓")
            table.add_row("Feature 3", "✓")
            content.add_child(table)

        opts = OverlayOptions(width="70%", anchor="center")
        self.overlay_handle = self.tui.show_overlay(content, opts)

    def show_about(self) -> None:
        """Show about screen."""
        self._clear_screen()
        self.current_screen = "about"

        for comp in create_header("About PyPiTUI"):
            self.tui.add_child(comp)

        self.tui.add_child(Spacer(1))

        about_text = """PyPiTUI is a Python port of the @mariozechner/pi-tui
terminal UI library.

Key Features:
• Component-based architecture (React-like)
• Differential rendering (only redraws changes)
• Focus management with hardware cursor
• Overlay system with flexible positioning
• Rich integration for markdown & tables
• Kitty keyboard protocol support"""

        for line in about_text.split("\n"):
            self.tui.add_child(Text(line, 0, 0))

        self.tui.add_child(Spacer(2))

        # Box with highlight
        box = Box(2, 1)
        box.add_child(
            Text(
                f"  {Colors.CYAN}https://github.com/yourusername/pypitui{Colors.RESET}",
                0,
                0,
            )
        )
        box.set_bg_fn(lambda s: f"{Colors.BG_BLACK}{Colors.DIM}{s}{Colors.RESET}")
        self.tui.add_child(box)

        self.tui.add_child(Spacer(1))
        self.tui.add_child(create_footer())

    def handle_input(self, data: str) -> None:
        """Handle keyboard input."""
        # Global quit
        if data.lower() == "q" and self.current_screen == "menu":
            self.running = False
            return

        # Animation skip
        if self.animation_active and self.current_screen == "splash":
            self.build_menu()
            return

        # ESC handling
        if matches_key(data, Key.escape):
            if self.tui.has_overlay():
                self.tui.hide_overlay()
            elif self.current_screen == "menu":
                self.running = False
            else:
                self.wizard_step = 0  # Reset wizard
                self.build_menu()
            return

        # Wizard navigation
        if self.current_screen == "inputs":
            if matches_key(data, Key.left) and self.wizard_step > 0:
                self.wizard_step -= 1
                self.show_inputs()
                return
            elif matches_key(data, Key.tab):
                # Tab between inputs in step 1
                if self.wizard_step == 1 and hasattr(self, 'name_input') and hasattr(self, 'email_input'):
                    if self.tui._focused_component == self.name_input:
                        self.tui.set_focus(self.email_input)
                    else:
                        self.tui.set_focus(self.name_input)
                    return
            elif matches_key(data, Key.enter):
                # Handle form submission in step 1
                if self.wizard_step == 1 and hasattr(self, 'name_input') and hasattr(self, 'email_input'):
                    name_val = self.name_input.get_value()
                    email_val = self.email_input.get_value()
                    self.advance_wizard(name=name_val, email=email_val)
                    return

        # Pass to TUI for component handling
        self.tui.handle_input(data)

    def run(self) -> None:
        """Main run loop at 60 FPS."""
        self.tui.start()

        frame_duration = 1.0 / 60.0  # ~16.67ms for 60 FPS

        try:
            while self.running:
                frame_start = time.time()

                # Read input (non-blocking for 60 FPS)
                data = self.terminal.read_sequence(timeout=0.001)
                if data:
                    self.handle_input(data)

                # Update animation
                if self.animation_active:
                    self.update_splash()

                # Render
                self.tui.request_render()
                self.tui.render_frame()

                # Maintain 60 FPS
                elapsed = time.time() - frame_start
                sleep_time = frame_duration - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            pass
        finally:
            self.tui.stop()


def main():
    """Run the ultimate demo."""
    print("Loading PyPiTUI Ultimate Demo...")
    print()

    try:
        app = UltimateDemoApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        raise

    print("\nThanks for trying PyPiTUI!")


if __name__ == "__main__":
    main()
