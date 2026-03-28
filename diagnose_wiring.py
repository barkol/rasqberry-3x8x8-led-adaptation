#!/usr/bin/env python3
"""
Diagnostic script to determine the physical wiring order of WS2812B LED panels.

Run on the Raspberry Pi with panels connected. Lights up pixels one at a time
so you can observe the physical layout and serpentine pattern.

Usage:
    sudo python3 diagnose_wiring.py

Watch the panels and note:
  - Where pixel 0 lights up (which corner, which panel)
  - Which direction pixels 0-7 travel (row or column? left/right? up/down?)
  - Whether pixels 8-15 reverse direction (serpentine) or continue straight
  - Where pixel 64 starts (second panel)
"""

import sys
import time

sys.path.insert(0, '/usr/bin')

from rq_led_utils import get_pixels

PAUSE = 0.8
BRIGHTNESS = 0.3


def test_first_16(pixels):
    """Light pixels 0-15 one by one to reveal serpentine direction."""
    print("=== Test 1: First 16 pixels (row 0 and row 1 of panel 0) ===")
    print("Watch which corner pixel 0 starts at and how 0-7 vs 8-15 flow.\n")

    for i in range(16):
        pixels.fill((0, 0, 0))
        pixels[i] = (255, 0, 0) if i < 8 else (0, 255, 0)
        pixels.show()
        label = "RED" if i < 8 else "GREEN"
        print(f"  pixel {i:3d}  ({label})")
        time.sleep(PAUSE)

    pixels.fill((0, 0, 0))
    pixels.show()
    input("\nPress Enter to continue...\n")


def test_panel_boundaries(pixels):
    """Light first pixel of each panel to confirm chaining order."""
    print("=== Test 2: Panel boundaries (pixel 0, 64, 128) ===")
    print("Three LEDs should light, one per panel.\n")

    pixels.fill((0, 0, 0))
    pixels[0] = (255, 0, 0)     # Panel 0 - RED
    pixels[64] = (0, 255, 0)    # Panel 1 - GREEN
    pixels[128] = (0, 0, 255)   # Panel 2 - BLUE
    pixels.show()

    print("  pixel   0 = RED    (should be panel 0 / leftmost)")
    print("  pixel  64 = GREEN  (should be panel 1 / middle)")
    print("  pixel 128 = BLUE   (should be panel 2 / rightmost)")

    input("\nPress Enter to continue...\n")

    pixels.fill((0, 0, 0))
    pixels.show()


def test_corners(pixels):
    """Light corners of the full grid to confirm orientation."""
    print("=== Test 3: Grid corners ===")
    print("Four LEDs at the expected corners of the 8x24 grid.\n")

    # If standard row-serpentine 8x8 panels, the corners are:
    #   Top-left:     pixel 0   (panel 0, row 0, col 0)
    #   Top-right:    pixel 135 (panel 2, row 0, col 7)
    #   Bottom-left:  pixel 56  (panel 0, row 7, col 0... or 63 if reversed)
    #   Bottom-right: pixel 191 or 184 depending on serpentine

    # Instead, just light the raw indices and let the user report
    corners = [
        (0, (255, 0, 0), "pixel 0   (RED)    - expected: top-left of panel 0"),
        (7, (0, 255, 0), "pixel 7   (GREEN)  - expected: end of first row, panel 0"),
        (8, (0, 0, 255), "pixel 8   (BLUE)   - expected: start of second row, panel 0"),
        (63, (255, 255, 0), "pixel 63  (YELLOW) - expected: last pixel of panel 0"),
    ]

    pixels.fill((0, 0, 0))
    for idx, color, label in corners:
        pixels[idx] = color
        print(f"  {label}")
    pixels.show()

    input("\nPress Enter to continue...\n")

    pixels.fill((0, 0, 0))
    pixels.show()


def test_full_sweep(pixels):
    """Sweep all 192 pixels quickly to see the overall wiring path."""
    print("=== Test 4: Full sweep (all 192 pixels) ===")
    print("Fast sweep to visualize the entire wiring path.\n")

    for i in range(192):
        pixels.fill((0, 0, 0))
        # Color changes per panel: red / green / blue
        if i < 64:
            color = (255, 0, 0)
        elif i < 128:
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)
        pixels[i] = color
        pixels.show()
        time.sleep(0.03)

    pixels.fill((0, 0, 0))
    pixels.show()
    print("  Sweep complete.")
    print()


def test_grid_rows(pixels):
    """Light up one logical row at a time using raw indices.

    If standard row-serpentine: row N = pixels N*8 .. N*8+7 within each panel.
    This test lights them per-panel so you can see if rows are horizontal.
    """
    print("=== Test 5: Row test (per panel) ===")
    print("Lights pixels 0-7, then 8-15, etc. within panel 0.")
    print("Each group of 8 should form a horizontal row.\n")

    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255),
    ]

    for row in range(8):
        pixels.fill((0, 0, 0))
        start = row * 8
        for col in range(8):
            pixels[start + col] = colors[row]
        pixels.show()
        print(f"  pixels {start:3d}-{start+7:3d}  (row {row})")
        time.sleep(PAUSE)

    input("\nPress Enter to continue...\n")

    pixels.fill((0, 0, 0))
    pixels.show()


def main():
    print()
    print("=" * 60)
    print("  WS2812B Panel Wiring Diagnostic")
    print("  3x 8x8 (192 pixels)")
    print("=" * 60)
    print()
    print("This will light LEDs in specific patterns so you can")
    print("observe the physical wiring and report back.")
    print()

    pixels = get_pixels(BRIGHTNESS)

    test_panel_boundaries(pixels)
    test_first_16(pixels)
    test_corners(pixels)
    test_grid_rows(pixels)
    test_full_sweep(pixels)

    print("=" * 60)
    print("  Diagnostic complete. Please report:")
    print()
    print("  1. Where did pixel 0 light up? (corner & panel)")
    print("  2. Did 0-7 go left-to-right or top-to-bottom?")
    print("  3. Did 8-15 reverse direction (serpentine)?")
    print("  4. Were panel 0/1/2 left/middle/right?")
    print("  5. In test 5, did each group of 8 form a horizontal row?")
    print("=" * 60)
    print()

    pixels.fill((0, 0, 0))
    pixels.show()


if __name__ == "__main__":
    main()
