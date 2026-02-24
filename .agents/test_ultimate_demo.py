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
sys.path.insert(0, str(Path(__file__).parent.parent / ".pi" / "skills" / "tmux-tape-no-img"))

try:
    from tmux_tool import TerminalSession
except ImportError:
    print("Error: tmux_tool.py not found. Make sure tmux-tape-no-img skill is available.")
    sys.exit(1)


def test_demo():
    """Run full test suite on ultimate_demo.py"""
    with TerminalSession("pypitui_test", port=7682) as s:
        print("=== PyPiTUI Ultimate Demo - Full Test ===\n")
        
        # Start demo
        s.send("cd /workspace/pypitui && uv run python examples/ultimate_demo.py")
        s.send_key("Enter")
        s.sleep(1)
        
        # Test Main Menu
        print("1. MAIN MENU:")
        print(s.capture_text()[:800])
        print("\n" + "="*60 + "\n")
        
        # Test Wizard (navigate to position 2: Down, Down, Enter)
        print("2. WIZARD:")
        s.send_key("Down")  # To Components
        s.sleep(0.2)
        s.send_key("Down")  # To Wizard
        s.sleep(0.2)
        s.send_key("Enter")
        s.sleep(0.5)
        print(s.capture_text()[:1000])
        
        print("\n2b. Wizard Profile step:")
        s.send_key("Enter")  # Advance from Welcome
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
        s.send_key("Enter")  # Select theme
        s.sleep(0.5)
        print(s.capture_text()[:800])
        
        # Back to menu (menu position resets to 0 after wizard completion)
        s.send_key("Escape")
        s.sleep(0.5)
        
        # Test Components (position 1: Down, Enter)
        # Menu is at Splash (0), Down goes to Components (1)
        print("\n3. COMPONENTS:")
        s.send_key("Down")
        s.sleep(0.2)
        s.send_key("Enter")
        s.sleep(0.5)
        result = s.capture_text()
        print(result[:1000])
        
        # Verify we're on Components screen
        if "Component Showcase" in result:
            print("\n✓ Components screen verified")
        else:
            print("\n✗ FAIL: Not on Components screen")
        
        s.send_key("Escape")
        s.sleep(0.5)
        
        # Test Overlays (position 3: Down x3 from Splash, Enter)
        # Menu resets to Splash (0) after Escape
        print("\n4. OVERLAYS:")
        s.send_key("Down")   # 1: Components
        s.sleep(0.2)
        s.send_key("Down")   # 2: Wizard
        s.sleep(0.2)
        s.send_key("Down")   # 3: Overlays
        s.sleep(0.2)
        s.send_key("Enter")
        s.sleep(0.5)
        result = s.capture_text()
        print(result[:800])
        
        # Verify we're on Overlays screen
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
        
        # Quit
        s.send("q")
        s.sleep(0.3)
        
        print("\n" + "="*60)
        print("=== All tests complete ===")


if __name__ == "__main__":
    test_demo()
