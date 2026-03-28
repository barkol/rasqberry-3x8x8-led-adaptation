#!/usr/bin/env python3
"""
Diagnostic script to determine the physical wiring order of WS2812B LED panels.

Run on the Raspberry Pi with panels connected. Lights up pixels one at a time
so you can observe the physical layout and serpentine pattern.

Uses SPI (GPIO 10) directly — no rq_led_utils dependency, no GPIO conflicts.

Usage:
    # Stop any running LED services first:
    sudo systemctl stop rasqberry-led 2>/dev/null; sudo systemctl stop rasqberry-virtual-led 2>/dev/null
    # Then run (no sudo needed for SPI):
    /home/rasqberry/RasQberry-Two/venv/RQB2/bin/python3 diagnose_wiring.py
"""

import sys
import time

try:
    import board
    import neopixel_spi as neopixel
except ImportError:
    print("ERROR: neopixel_spi not installed. Run with the RQB2 venv python:")
    print("  /home/rasqberry/RasQberry-Two/venv/RQB2/bin/python3 diagnose_wiring.py")
    sys.exit(1)

NUM_PIXELS = 192
PAUSE = 0.8
BRIGHTNESS = 0.3

spi = board.SPI()
pixels = neopixel.NeoPixel_SPI(
    spi, NUM_PIXELS, pixel_order=neopixel.GRB,
    auto_write=False, brightness=BRIGHTNESS
)


def clear():
    pixels.fill(0)
    pixels.show()


def test_panel_boundaries():
    """Light first pixel of each panel to confirm chaining order."""
    print("=== Test 1: Panel boundaries (pixel 0, 64, 128) ===")
    print("Three LEDs should light, one per panel.\n")

    clear()
    pixels[0] = (255, 0, 0)
    pixels[64] = (0, 255, 0)
    pixels[128] = (0, 0, 255)
    pixels.show()

    print("  pixel   0 = RED    (expected: panel 0 / leftmost)")
    print("  pixel  64 = GREEN  (expected: panel 1 / middle)")
    print("  pixel 128 = BLUE   (expected: panel 2 / rightmost)")
    print()
    print("  Q1: Are the panels left=RED, middle=GREEN, right=BLUE?")
    print("  Q2: Or is the order different? Note the actual order.")

    input("\nPress Enter to continue...\n")
    clear()


def test_first_16():
    """Light pixels 0-15 one by one to reveal serpentine direction."""
    print("=== Test 2: First 16 pixels of panel 0 ===")
    print("Watch which corner pixel 0 starts at and how 0-7 vs 8-15 flow.\n")

    for i in range(16):
        clear()
        pixels[i] = (255, 0, 0) if i < 8 else (0, 255, 0)
        pixels.show()
        label = "RED" if i < 8 else "GREEN"
        print(f"  pixel {i:3d}  ({label})")
        time.sleep(PAUSE)

    clear()
    print()
    print("  Q3: Where did pixel 0 light? (e.g. top-left corner)")
    print("  Q4: Did 0->7 go left-to-right or top-to-bottom?")
    print("  Q5: Did 8->15 reverse direction (serpentine)?")

    input("\nPress Enter to continue...\n")


def test_corners():
    """Light key pixels to confirm orientation."""
    print("=== Test 3: Key pixels on panel 0 ===")
    print("Four LEDs on panel 0 to identify corners.\n")

    clear()
    pixels[0] = (255, 0, 0)       # RED
    pixels[7] = (0, 255, 0)       # GREEN
    pixels[8] = (0, 0, 255)       # BLUE
    pixels[63] = (255, 255, 0)    # YELLOW
    pixels.show()

    print("  pixel  0 = RED      (first pixel)")
    print("  pixel  7 = GREEN    (end of first group of 8)")
    print("  pixel  8 = BLUE     (start of second group of 8)")
    print("  pixel 63 = YELLOW   (last pixel of panel 0)")
    print()
    print("  Q6: Which corners do these occupy?")

    input("\nPress Enter to continue...\n")
    clear()


def test_rows():
    """Light 8 pixels at a time within panel 0."""
    print("=== Test 4: Groups of 8 on panel 0 ===")
    print("Each group of 8 pixels lights in a different color.")
    print("If row-serpentine: each group = one horizontal row.\n")

    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255),
    ]

    for group in range(8):
        clear()
        start = group * 8
        for j in range(8):
            pixels[start + j] = colors[group]
        pixels.show()
        print(f"  pixels {start:3d}-{start+7:3d}  (group {group})")
        time.sleep(PAUSE)

    print()
    print("  Q7: Does each group form a horizontal row?")
    print("  Q8: Or does each group form a vertical column?")

    input("\nPress Enter to continue...\n")
    clear()


def test_full_sweep():
    """Fast sweep all 192 pixels."""
    print("=== Test 5: Full sweep (all 192 pixels) ===")
    print("Fast sweep: red=panel0, green=panel1, blue=panel2.\n")

    for i in range(192):
        clear()
        if i < 64:
            color = (255, 0, 0)
        elif i < 128:
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)
        pixels[i] = color
        pixels.show()
        time.sleep(0.03)

    clear()
    print("  Sweep complete.\n")


def main():
    print()
    print("=" * 60)
    print("  WS2812B Panel Wiring Diagnostic")
    print("  3x 8x8 (192 pixels) — using SPI directly")
    print("=" * 60)
    print()

    test_panel_boundaries()
    test_first_16()
    test_corners()
    test_rows()
    test_full_sweep()

    print("=" * 60)
    print("  Diagnostic complete. Please report:")
    print()
    print("  1. Panel order: left/middle/right = which colors?")
    print("  2. Pixel 0 location (which corner of which panel?)")
    print("  3. Direction of 0->7 (horizontal or vertical?)")
    print("  4. Did 8->15 reverse? (serpentine yes/no)")
    print("  5. Did groups of 8 form rows or columns?")
    print("=" * 60)
    print()

    clear()


if __name__ == "__main__":
    main()
