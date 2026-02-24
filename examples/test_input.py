#!/usr/bin/env python3
"""Test script to verify arrow key input works."""

import sys
import select
import termios
import tty
import time

def test_raw_input():
    """Test reading raw input including escape sequences."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    print("Press arrow keys to test (press 'q' to quit):")
    print("-" * 40)
    
    try:
        tty.setraw(fd)
        
        while True:
            # Wait for input
            if not select.select([sys.stdin], [], [], 0.1)[0]:
                continue
            
            # Read using buffer for raw bytes
            stdin_buffer = sys.stdin.buffer
            data = b""
            
            # Read first byte
            byte = stdin_buffer.read(1)
            if not byte:
                continue
            data = byte
            
            # If escape, wait for rest of sequence
            if data == b"\x1b":
                deadline = time.time() + 0.05  # 50ms
                while time.time() < deadline:
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        byte = stdin_buffer.read(1)
                        if byte:
                            data += byte
                            # Check if sequence complete (CSI ends with 0x40-0x7E)
                            if len(data) >= 3 and 0x40 <= data[-1] <= 0x7E:
                                break
                    else:
                        break
            
            # Decode
            try:
                decoded = data.decode("utf-8", errors="replace")
            except:
                decoded = str(data)
            
            # Print what we got
            sys.stdout.write(f"\r\x1b[K")  # Clear line
            sys.stdout.write(f"Got: {repr(data)} = {repr(decoded)}")
            sys.stdout.flush()
            
            # Check for quit
            if decoded == "q":
                break
                
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\nDone!")


if __name__ == "__main__":
    test_raw_input()
