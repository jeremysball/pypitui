#!/usr/bin/env python3
"""PyPiTUI Demo - Proper Differential Rendering Patterns.

This demo shows the CORRECT way to use PyPiTUI:

1. Use a root Container for screen switching
2. Clear the CONTAINER, not the TUI
3. For animations, update component state, don't rebuild everything
4. Let differential rendering handle the rest

Key patterns:
- tui.add_child(root_container) once at init
- root_container.children.clear() to switch screens
- root_container.add_child() to build new screen
- For streaming: just add_child() new content, never clear()
"""

from __future__ import annotations

import math
import random
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
    ProcessTerminal,
    matches_key,
    Key,
)
from pypitui.tui import Component

try:
    from pypitui.rich_components import (
        Markdown,
        RichText,
        RichTable,
        rich_color_to_ansi,
    )
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# =============================================================================
# THEME SYSTEM
# =============================================================================


@dataclass
class Theme:
    """Theme using Rich color names."""
    name: str
    primary: str
    secondary: str
    accent: str
    muted: str
    success: str
    error: str


THEMES = {
    "neon": Theme("Cyberpunk Neon", "bright_cyan", "bright_magenta", "bright_yellow", "dim", "bright_green", "bright_red"),
    "warm": Theme("Warm Sunset", "yellow", "red", "bright_red", "dim", "green", "red"),
    "ocean": Theme("Deep Ocean", "blue", "cyan", "bright_cyan", "dim", "green", "red"),
}


def create_select_theme(theme: Theme) -> SelectListTheme:
    """Create SelectList theme from Rich colors."""
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

MENU_ITEMS = [
    ("streaming", "📊 Streaming", "Proper scrollback demo"),
    ("matrix", "🌈 Matrix Rain", "Rainbow animation"),
    ("components", "🧩 Components", "UI building blocks"),
    ("wizard", "🧙 Form Wizard", "Multi-step input"),
    ("overlays", "🪟 Overlays", "Floating panels"),
    ("about", "ℹ️  About", "Library info"),
]

WIZARD_STEPS = ["Welcome", "Profile", "Theme", "Complete"]


# =============================================================================
# MAIN APPLICATION
# =============================================================================


class DemoApp:
    """Demo with proper differential rendering patterns."""

    def __init__(self):
        self.terminal = ProcessTerminal()
        self.tui = TUI(self.terminal, show_hardware_cursor=True)

        # ✅ CORRECT PATTERN: Root container for screen switching
        # We clear THIS container, not the TUI
        self.root = Container()
        self.tui.add_child(self.root)

        self.running = True
        self.current_screen = "menu"
        self.current_theme = "neon"
        self.wizard_step = 0
        self.form_data = {"name": "", "email": "", "theme": "neon"}
        self.overlay_handle = None
        self.animation_active = False

        # Animation state (for matrix)
        self.matrix_columns = []
        self.matrix_grid = []

        self.show_menu()

    def _theme(self) -> Theme:
        return THEMES[self.current_theme]

    def switch_screen(self, builder: Callable) -> None:
        """Switch to a new screen - PROPER PATTERN.

        Clear the root container, not the TUI.
        This preserves _previous_lines for differential rendering.
        """
        self.animation_active = False
        self.root.children.clear()  # ✅ Clear container, NOT tui
        builder()

    def show_menu(self) -> None:
        """Main menu."""
        self.current_screen = "menu"
        t = self._theme()

        # Header
        header = BorderedBox(padding_x=2, max_width=45)
        header.set_rich_title(f"[bold {t.primary}]🐍 PyPiTUI[/bold {t.primary}]")
        header.add_child(RichText(f"[{t.muted}]Terminal UI Framework[/{t.muted}]"))
        self.root.add_child(header)
        self.root.add_child(Spacer(1))

        # Menu
        items = [SelectItem(key, label, desc) for key, label, desc in MENU_ITEMS]
        menu = SelectList(items, 6, create_select_theme(t))
        menu.on_select = self.on_menu_select
        self.root.add_child(menu)
        self.tui.set_focus(menu)

        self.root.add_child(Spacer(1))
        self.root.add_child(RichText(f"[{t.muted}]↑↓ Navigate • Enter Select • Q Quit[/{t.muted}]"))

    def on_menu_select(self, item: SelectItem) -> None:
        """Handle menu selection."""
        handlers = {
            "streaming": self.show_streaming,
            "matrix": self.show_matrix,
            "components": self.show_components,
            "wizard": self.show_wizard,
            "overlays": self.show_overlays,
            "about": self.show_about,
        }
        handlers.get(item.value, lambda: None)()

    # =========================================================================
    # STREAMING DEMO - Proper incremental content
    # =========================================================================

    def show_streaming(self) -> None:
        """Streaming demo - CORRECT PATTERN for growing content.

        Key: We add new content incrementally, never clear().
        Old content flows into scrollback naturally.
        """
        self.switch_screen(self._build_streaming)

    def _build_streaming(self) -> None:
        self.current_screen = "streaming"
        t = self._theme()

        self.root.add_child(RichText(f"[bold {t.primary}]📊 Streaming Demo[/bold {t.primary}]"))
        self.root.add_child(RichText(f"[{t.muted}]Content grows incrementally - watch scrollback![/{t.muted}]"))
        self.root.add_child(Spacer(1))

        # Counter component that we'll update
        self.streaming_counter = Text("Lines: 0", padding_y=0)
        self.root.add_child(self.streaming_counter)
        self.root.add_child(Spacer(1))

        self.streaming_count = 0
        self.animation_active = True

    def update_streaming(self) -> None:
        """Add new streaming content - incremental, not rebuild."""
        if not self.animation_active or self.current_screen != "streaming":
            return

        now = time.time()
        if not hasattr(self, "_last_stream"):
            self._last_stream = 0
        if now - self._last_stream < 0.15:
            return
        self._last_stream = now

        # ✅ CORRECT: Just add new content
        self.streaming_count += 1

        # Update counter in place
        self.streaming_counter.set_text(f"Lines: {self.streaming_count}")

        # Add new line - this scrolls into scrollback
        self.root.add_child(Text(f"  Entry {self.streaming_count}: {'█' * (self.streaming_count % 30)}", padding_y=0))

        if self.streaming_count >= 50:
            self.root.add_child(Spacer(1))
            self.root.add_child(RichText(f"[{t.muted}]Done! Shift+PgUp to scroll, ESC to exit[/{t.muted}]"))
            self.animation_active = False

    # =========================================================================
    # MATRIX DEMO - Rainbow animation with delta time
    # =========================================================================

    # Rainbow colors (ANSI 256 color codes)
    RAINBOW = [
        "\x1b[38;5;196m",  # Red
        "\x1b[38;5;208m",  # Orange
        "\x1b[38;5;226m",  # Yellow
        "\x1b[38;5;46m",   # Green
        "\x1b[38;5;51m",   # Cyan
        "\x1b[38;5;21m",   # Blue
        "\x1b[38;5;129m",  # Purple
        "\x1b[38;5;201m",  # Magenta
    ]
    A = {"rs": "\x1b[0m", "bd": "\x1b[1m", "w": "\x1b[97m", "K": "\x1b[90m"}
    CHARS = "0123456789ABCDEFabcdefghijklmnopqrstuvwxyz@#$%&*+-="

    def show_matrix(self) -> None:
        """Matrix rain - rainbow animation with delta time."""
        self.switch_screen(self._build_matrix)

    def _build_matrix(self) -> None:
        self.current_screen = "matrix"
        t = self._theme()

        w, h = self.terminal.get_size()
        self.matrix_w = max(40, w)
        self.matrix_h = max(10, h - 5)  # Reserve 5 lines for UI

        # Initialize columns with slower speeds
        self.matrix_columns = [
            {
                "y": random.randint(-30, 0),
                "speed": random.uniform(0.15, 0.4),  # Slower
                "len": random.randint(8, 20),
                "color_idx": random.randint(0, len(self.RAINBOW) - 1),
            }
            for _ in range(self.matrix_w)
        ]

        # Initialize grid: (char, brightness, color_idx)
        self.matrix_grid = [[(" ", 0, 0) for _ in range(self.matrix_h)] for _ in range(self.matrix_w)]

        # Scrolling banner
        self.scroll_text = " PYPITUI - RAINBOW MATRIX - TERMINAL UI FRAMEWORK - GITHUB.COM/JEREMYSBALL/PYPITUI - "
        self.scroll_pos = 0
        self._scroll_accumulator = 0.0

        # Single text component we update in place
        self.matrix_text = Text("", 0, 0)
        self.root.add_child(self.matrix_text)

        self.animation_active = True
        self._last_matrix = 0

    def update_matrix(self) -> None:
        """Update matrix with delta time for smooth animation."""
        if not self.animation_active or self.current_screen != "matrix":
            return

        now = time.time()
        dt = now - self._last_matrix if self._last_matrix > 0 else 0.016
        self._last_matrix = now

        # Target ~30 FPS for matrix (smoother but not too fast)
        if dt < 0.033:
            return

        w, h = self.matrix_w, self.matrix_h

        # Update columns with delta time
        for x, col in enumerate(self.matrix_columns):
            col["y"] += col["speed"] * dt * 30  # Scaled by dt

            # Draw head and trail
            for dy in range(col["len"]):
                y = int(col["y"]) - dy
                if 0 <= y < h:
                    # Fade brightness along trail
                    if dy == 0:
                        self.matrix_grid[x][y] = (random.choice(self.CHARS), 4, col["color_idx"])
                    elif dy < 2:
                        self.matrix_grid[x][y] = (random.choice(self.CHARS), 3, col["color_idx"])
                    elif dy < 5:
                        self.matrix_grid[x][y] = (random.choice(self.CHARS), 2, col["color_idx"])
                    else:
                        self.matrix_grid[x][y] = (random.choice(self.CHARS), 1, col["color_idx"])

            # Reset if off screen, pick new color
            if int(col["y"]) - col["len"] > h:
                col["y"] = random.randint(-15, -3)
                col["speed"] = random.uniform(0.15, 0.4)
                col["len"] = random.randint(8, 20)
                col["color_idx"] = random.randint(0, len(self.RAINBOW) - 1)

        # Slowly fade grid
        for x in range(w):
            for y in range(h):
                char, bright, color = self.matrix_grid[x][y]
                if bright > 0 and random.random() < 0.08:
                    self.matrix_grid[x][y] = (char, bright - 1, color)

        # Build output - rainbow colored
        lines = []
        for y in range(h):
            row = []
            for x in range(w):
                char, bright, color_idx = self.matrix_grid[x][y]
                if bright >= 4:
                    # White head
                    row.append(f"{self.A['w']}{self.A['bd']}{char}{self.A['rs']}")
                elif bright >= 3:
                    # Bright rainbow
                    color = self.RAINBOW[color_idx]
                    row.append(f"{self.A['bd']}{color}{char}{self.A['rs']}")
                elif bright >= 2:
                    # Normal rainbow
                    color = self.RAINBOW[color_idx]
                    row.append(f"{color}{char}{self.A['rs']}")
                elif bright >= 1:
                    # Dim rainbow
                    color = self.RAINBOW[color_idx]
                    row.append(f"{color}\x1b[2m{char}{self.A['rs']}")
                else:
                    row.append(" ")
            lines.append("".join(row).replace(" ", "\xa0"))

        # Scrolling banner at bottom
        self._scroll_accumulator += dt * 12  # Scroll speed
        if self._scroll_accumulator >= 1.0:
            self.scroll_pos = (self.scroll_pos + int(self._scroll_accumulator)) % len(self.scroll_text)
            self._scroll_accumulator -= int(self._scroll_accumulator)

        visible_banner = ""
        for i in range(w):
            idx = (self.scroll_pos + i) % len(self.scroll_text)
            visible_banner += self.scroll_text[idx]

        # Add UI lines
        lines.append(f"{self.A['K']}{'─' * w}{self.A['rs']}")
        lines.append(f"{self.RAINBOW[2]}{visible_banner}{self.A['rs']}")
        lines.append(f"{self.A['K']}{'─' * w}{self.A['rs']}")

        # Update in place - efficient
        self.matrix_text.set_text("\n".join(lines))

    # =========================================================================
    # COMPONENTS DEMO
    # =========================================================================

    def show_components(self) -> None:
        """Component showcase."""
        self.switch_screen(self._build_components)

    def _build_components(self) -> None:
        self.current_screen = "components"
        t = self._theme()

        header = BorderedBox(padding_x=2, max_width=50)
        header.set_rich_title(f"[bold {t.primary}]Component Showcase[/bold {t.primary}]")
        self.root.add_child(header)
        self.root.add_child(Spacer(1))

        # Text
        self.root.add_child(RichText(f"[bold {t.primary}]Text:[/bold {t.primary}] Auto-wraps content. [{t.muted}]This is muted.[/{t.muted}]"))
        self.root.add_child(Spacer(1))

        # Box
        self.root.add_child(RichText(f"[bold {t.primary}]Box (padding):[/bold {t.primary}]"))
        box = Box(padding_x=2)
        box.add_child(RichText(f"[{t.secondary}]Content with padding[/{t.secondary}]"))
        self.root.add_child(box)
        self.root.add_child(Spacer(1))

        # BorderedBox
        self.root.add_child(RichText(f"[bold {t.primary}]BorderedBox:[/bold {t.primary}]"))
        bordered = BorderedBox(padding_x=2, max_width=35, title="Panel")
        bordered.add_child(RichText(f"[{t.accent}]Draws borders, wraps content[/{t.accent}]"))
        self.root.add_child(bordered)
        self.root.add_child(Spacer(1))

        # Input
        self.root.add_child(RichText(f"[bold {t.primary}]Input:[/bold {t.primary}]"))
        inp = Input(placeholder="Type and press Enter...")
        inp.on_submit = lambda v: self._show_result(f"You typed: {v}")
        self.root.add_child(inp)
        self.tui.set_focus(inp)

        self.root.add_child(Spacer(1))
        self.root.add_child(RichText(f"[{t.muted}]ESC to go back[/{t.muted}]"))

    # =========================================================================
    # WIZARD DEMO
    # =========================================================================

    def show_wizard(self) -> None:
        """Multi-step form wizard."""
        self.switch_screen(lambda: self._build_wizard())

    def _build_wizard(self) -> None:
        self.current_screen = "wizard"
        t = self._theme()
        step = self.wizard_step

        # Header with step name
        names = ["Welcome", "Profile", "Theme", "Complete"]
        header = BorderedBox(padding_x=2, max_width=50)
        header.set_rich_title(f"[bold {t.primary}]Wizard: {names[step]}[/bold {t.primary}]")
        self.root.add_child(header)

        # Progress
        progress = " → ".join(
            f"[bold {t.primary}]{n}[/bold {t.primary}]" if i == step else f"[{t.muted}]{n}[/{t.muted}]"
            for i, n in enumerate(names)
        )
        self.root.add_child(RichText(progress))
        self.root.add_child(Spacer(2))

        if step == 0:
            self.root.add_child(RichText(f"[{t.secondary}]This wizard demonstrates forms.[/{t.secondary}]"))
            self.root.add_child(Spacer(1))
            self.root.add_child(RichText(f"[{t.muted}]Press Enter to start[/{t.muted}]"))

        elif step == 1:
            self.root.add_child(RichText(f"[bold {t.primary}]Name:[/bold {t.primary}]"))
            self.name_input = Input(placeholder="Your name")
            self.name_input.set_value(self.form_data["name"])
            self.root.add_child(self.name_input)

            self.root.add_child(Spacer(1))
            self.root.add_child(RichText(f"[bold {t.primary}]Email:[/bold {t.primary}]"))
            self.email_input = Input(placeholder="Your email")
            self.email_input.set_value(self.form_data["email"])
            self.root.add_child(self.email_input)

            self.root.add_child(Spacer(1))
            self.root.add_child(RichText(f"[{t.muted}]Tab: switch • Enter: continue[/{t.muted}]"))
            self.tui.set_focus(self.name_input)

        elif step == 2:
            self.root.add_child(RichText(f"[bold {t.primary}]Choose Theme:[/bold {t.primary}]"))
            items = [SelectItem(k, v.name) for k, v in THEMES.items()]
            lst = SelectList(items, 3, create_select_theme(t))
            lst.on_select = lambda i: self._wizard_next(theme=i.value)
            self.root.add_child(lst)
            self.tui.set_focus(lst)

        else:  # Complete
            self.root.add_child(RichText(f"[bold {t.success}]✓ Setup Complete![/bold {t.success}]"))
            self.root.add_child(Spacer(1))
            self.root.add_child(RichText(f"Name: {self.form_data['name'] or '(none)'}"))
            self.root.add_child(RichText(f"Email: {self.form_data['email'] or '(none)'}"))
            theme_name = THEMES.get(self.form_data.get('theme', 'neon'), THEMES['neon']).name
            self.root.add_child(RichText(f"Theme: [{t.accent}]{theme_name}[/{t.accent}]"))

    def _wizard_next(self, **kwargs) -> None:
        """Advance wizard."""
        self.form_data.update(kwargs)
        if self.wizard_step < 3:
            self.wizard_step += 1
            self.switch_screen(self._build_wizard)
        else:
            self.wizard_step = 0
            self.switch_screen(self.show_menu)

    # =========================================================================
    # OVERLAYS DEMO
    # =========================================================================

    def show_overlays(self) -> None:
        """Overlay positioning demo."""
        self.switch_screen(self._build_overlays)

    def _build_overlays(self) -> None:
        self.current_screen = "overlays"
        t = self._theme()

        header = BorderedBox(padding_x=2, max_width=50)
        header.set_rich_title(f"[bold {t.primary}]Overlay System[/bold {t.primary}]")
        header.add_child(RichText(f"[{t.muted}]Floating panels & dialogs[/{t.muted}]"))
        self.root.add_child(header)
        self.root.add_child(Spacer(1))

        positions = [
            SelectItem("center", "Center", "Default centered"),
            SelectItem("top", "Top", "Top of screen"),
            SelectItem("bottom", "Bottom", "Bottom of screen"),
            SelectItem("top-right", "Top Right", "Upper right corner"),
        ]

        lst = SelectList(positions, 4, create_select_theme(t))
        lst.on_select = self._show_overlay
        self.root.add_child(lst)
        self.tui.set_focus(lst)

        self.root.add_child(Spacer(1))
        self.root.add_child(RichText(f"[{t.muted}]ESC to go back[/{t.muted}]"))

    def _show_overlay(self, item: SelectItem) -> None:
        """Show overlay at selected position."""
        if self.overlay_handle:
            self.overlay_handle.hide()

        t = self._theme()
        anchors = {"center": "center", "top": "top", "bottom": "bottom", "top-right": "top-right"}
        anchor = anchors.get(item.value, "center")

        content = BorderedBox(padding_x=2, max_width=35, title=f"{anchor.title()} Overlay")
        content.add_child(RichText(f"[{t.primary}]Positioned at {anchor}[/{t.primary}]"))
        content.add_child(RichText(f"[{t.muted}]Press ESC to close[/{t.muted}]"))

        self.overlay_handle = self.tui.show_overlay(content, OverlayOptions(width=35, anchor=anchor))

    # =========================================================================
    # ABOUT
    # =========================================================================

    def show_about(self) -> None:
        """About screen."""
        self.switch_screen(self._build_about)

    def _build_about(self) -> None:
        self.current_screen = "about"
        t = self._theme()

        header = BorderedBox(padding_x=2, max_width=50)
        header.set_rich_title(f"[bold {t.primary}]About PyPiTUI[/bold {t.primary}]")
        self.root.add_child(header)
        self.root.add_child(Spacer(1))

        self.root.add_child(RichText(f"[{t.secondary}]Python terminal UI library with differential rendering.[/{t.secondary}]"))
        self.root.add_child(Spacer(1))

        self.root.add_child(RichText(f"[bold {t.primary}]Features:[/bold {t.primary}]"))
        self.root.add_child(RichText(f"  • [{t.primary}]Component-based architecture[/{t.primary}]"))
        self.root.add_child(RichText(f"  • [{t.primary}]Differential rendering[/{t.primary}]"))
        self.root.add_child(RichText(f"  • [{t.primary}]DEC 2026 synchronized output[/{t.primary}]"))
        self.root.add_child(RichText(f"  • [{t.primary}]Relative cursor movement[/{t.primary}]"))
        self.root.add_child(RichText(f"  • [{t.primary}]Overlay system[/{t.primary}]"))
        self.root.add_child(RichText(f"  • [{t.primary}]Rich integration[/{t.primary}]"))

        self.root.add_child(Spacer(1))
        self.root.add_child(RichText(f"[{t.muted}]https://github.com/jeremysball/pypitui[/{t.muted}]"))
        self.root.add_child(Spacer(1))
        self.root.add_child(RichText(f"[{t.muted}]ESC to go back[/{t.muted}]"))

    # =========================================================================
    # RESULT SCREEN
    # =========================================================================

    def _show_result(self, message: str) -> None:
        """Show result message."""
        self.switch_screen(lambda: self._build_result(message))

    def _build_result(self, message: str) -> None:
        self.current_screen = "result"
        t = self._theme()

        self.root.add_child(RichText(f"[{t.success}]{message}[/{t.success}]"))
        self.root.add_child(Spacer(1))
        self.root.add_child(RichText(f"[{t.muted}]Press Enter or ESC to go back[/{t.muted}]"))

    # =========================================================================
    # INPUT HANDLING
    # =========================================================================

    def handle_input(self, data: str) -> None:
        """Handle input."""
        # Global quit
        if data.lower() == "q" and self.current_screen == "menu":
            self.running = False
            return

        # ESC
        if matches_key(data, Key.escape):
            if self.tui.has_overlay():
                self.tui.hide_overlay()
                self.overlay_handle = None
            elif self.current_screen == "menu":
                self.running = False
            else:
                self.wizard_step = 0
                self.switch_screen(self.show_menu)
            return

        # Exit animation screens
        if self.current_screen in ("streaming", "matrix"):
            self.switch_screen(self.show_menu)
            return

        # Result screen - any key goes back
        if self.current_screen == "result":
            if matches_key(data, Key.escape) or matches_key(data, Key.enter):
                self.switch_screen(self.show_menu)
            return

        # Wizard
        if self.current_screen == "wizard":
            if matches_key(data, Key.left) and self.wizard_step > 0:
                self.wizard_step -= 1
                self.switch_screen(self._build_wizard)
                return

            if self.wizard_step == 0 and matches_key(data, Key.enter):
                self._wizard_next()
                return

            if self.wizard_step == 1 and hasattr(self, "name_input"):
                if matches_key(data, Key.tab):
                    new_focus = self.email_input if self.tui._focused_component == self.name_input else self.name_input
                    self.tui.set_focus(new_focus)
                    return
                if matches_key(data, Key.enter):
                    self.form_data["name"] = self.name_input.get_value()
                    self.form_data["email"] = self.email_input.get_value()
                    self._wizard_next()
                    return

        self.tui.handle_input(data)

    # =========================================================================
    # MAIN LOOP
    # =========================================================================

    def run(self) -> None:
        """Main loop at 60 FPS."""
        self.tui.start()
        frame_time = 1.0 / 60.0

        try:
            while self.running:
                start = time.time()

                # Input
                data = self.terminal.read_sequence(timeout=0.001)
                if data:
                    self.handle_input(data)

                # Animations
                if self.animation_active:
                    if self.current_screen == "streaming":
                        self.update_streaming()
                    elif self.current_screen == "matrix":
                        self.update_matrix()

                # Render
                self.tui.request_render()
                self.tui.render_frame()

                # Frame limit
                elapsed = time.time() - start
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

        finally:
            self.tui.stop()


def main() -> None:
    print("PyPiTUI Demo - Proper Differential Rendering Patterns")
    print("")
    DemoApp().run()
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
