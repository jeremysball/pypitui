#!/usr/bin/env python3
"""Test all menus in ultimate_demo.py using tmux.

Usage:
    cd /workspace/pypitui
    uv run python .agents/test_ultimate_demo.py

This script tests:
- Main menu display
- Wizard flow (all 4 steps)
- Components showcase
- Overlays with positioning
"""

import sys
from pathlib import Path

# Add tmux_tool to path
sys.path.insert(
    0,
    str(Path(__file__).parent.parent / ".pi" / "skills" / "tmux-tape-no-img"),
)

try:
    from tmux_tool import TerminalSession
except ImportError:
    print("Error: tmux_tool.py not found.")
    print("Make sure tmux-tape-no-img skill is available.")
    sys.exit(1)


def test_main_menu(s: TerminalSession) -> None:
    """Test main menu display."""
    print("1. MAIN MENU:")
    print(s.capture_text()[:800])
    print("\n" + "=" * 60 + "\n")


def test_wizard(s: TerminalSession) -> None:
    """Test wizard flow."""
    print("2. WIZARD:")
    s.send_key("Down")
    s.sleep(0.2)
    s.send_key("Down")
    s.sleep(0.2)
    s.send_key("Enter")
    s.sleep(0.5)
    print(s.capture_text()[:1000])

    print("\n2b. Wizard Profile step:")
    s.send_key("Enter")
    s.sleep(0.5)
    print(s.capture_text()[:1000])

    print("\n2c. Wizard Theme step:")
    s.send("Test User")
    s.sleep(0.2)
    s.send_key("Tab")
    s.sleep(0.2)
    s.send("test@test.com")
    s.sleep(0.2)
    s.send_key("Enter")
    s.sleep(0.5)
    print(s.capture_text()[:800])

    print("\n2d. Wizard Complete:")
    s.send_key("Enter")
    s.sleep(0.5)
    print(s.capture_text()[:800])

    s.send_key("Escape")
    s.sleep(0.5)


def test_components(s: TerminalSession) -> None:
    """Test components screen."""
    print("\n3. COMPONENTS:")
    s.send_key("Down")
    s.sleep(0.2)
    s.send_key("Enter")
    s.sleep(0.5)
    result = s.capture_text()
    print(result[:1000])

    if "Component Showcase" in result:
        print("\n✓ Components screen verified")
    else:
        print("\n✗ FAIL: Not on Components screen")

    s.send_key("Escape")
    s.sleep(0.5)


def test_overlays(s: TerminalSession) -> None:
    """Test overlays screen."""
    print("\n4. OVERLAYS:")
    s.send_key("Down")
    s.sleep(0.2)
    s.send_key("Down")
    s.sleep(0.2)
    s.send_key("Down")
    s.sleep(0.2)
    s.send_key("Enter")
    s.sleep(0.5)
    result = s.capture_text()
    print(result[:800])

    if "Overlay System" in result:
        print("\n✓ Overlays screen verified")
    else:
        print("\n✗ FAIL: Not on Overlays screen")

    print("\n4b. Center overlay:")
    s.send_key("Enter")
    s.sleep(0.5)
    result = s.capture_text()
    print(result[:1000])

    if "Center Overlay" in result:
        print("\n✓ Overlay displayed correctly")
    else:
        print("\n✗ FAIL: Overlay not shown")

    s.send_key("Escape")
    s.sleep(0.3)
    s.send_key("Escape")
    s.sleep(0.5)


def test_demo():
    """Run full test suite on ultimate_demo.py"""
    with TerminalSession("pypitui_test", port=7682) as s:
        print("=== PyPiTUI Ultimate Demo - Full Test ===\n")

        # Start demo
        demo_cmd = (
            "cd /workspace/pypitui && "
            "uv run python examples/ultimate_demo.py"
        )
        s.send(demo_cmd)
        s.send_key("Enter")
        s.sleep(1)

        test_main_menu(s)
        test_wizard(s)
        test_components(s)
        test_overlays(s)

        # Quit
        s.send("q")
        s.sleep(0.3)

        print("\n" + "=" * 60)
        print("=== All tests complete ===")


if __name__ == "__main__":
    test_demo()
