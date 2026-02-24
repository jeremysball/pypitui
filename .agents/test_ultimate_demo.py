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
        
        # Test Wizard (position 2: Down, Down, Enter)
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
        
        # Back to menu
        s.send_key("Escape")
        s.sleep(0.5)
        
        # Test Components (position 1 from Splash: Down, Enter)
        print("\n3. COMPONENTS:")
        s.send_key("Down")
        s.sleep(0.2)
        s.send_key("Enter")
        s.sleep(0.5)
        print(s.capture_text()[:1000])
        
        s.send_key("Escape")
        s.sleep(0.5)
        
        # Test Overlays (position 3: Down, Down, Enter)
        print("\n4. OVERLAYS:")
        s.send_key("Down")
        s.sleep(0.2)
        s.send_key("Down")
        s.sleep(0.2)
        s.send_key("Enter")
        s.sleep(0.5)
        print(s.capture_text()[:800])
        
        print("\n4b. Center overlay:")
        s.send_key("Enter")
        s.sleep(0.5)
        print(s.capture_text()[:1000])
        
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
