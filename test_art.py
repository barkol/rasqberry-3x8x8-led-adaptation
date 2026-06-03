#!/usr/bin/env python3
"""Generate and display test LED art patterns using LED_array_indices."""

import json
import sys
sys.path.insert(0, '/usr/bin')
sys.path.insert(0, '/home/rasqberry/RasQberry-Two/demos/led-painter')

from rq_led_utils import get_pixels, clear_all_leds, chunked_clear
from LED_array_indices import LED_ARRAY_INDICES
import time

pixels = get_pixels(0.3)

def display_art(data, duration=4):
    """Display art from dict {gui_index: [R,G,B]}."""
    chunked_clear(pixels)
    for idx_str, color in data.items():
        led_idx = LED_ARRAY_INDICES[int(idx_str)]
        pixels[led_idx] = tuple(color)
    pixels.show()
    time.sleep(duration)

# Pattern 1: Smiley face (yellow on blue background)
print("1/3 Smiley face...")
art = {}
for i in range(192):
    art[str(i)] = [0, 0, 30]  # dark blue background
# Eyes (row 2, columns 7-8 and 15-16)
for x in [7, 8]:
    for y in [2, 3]:
        art[str(y * 24 + x)] = [255, 255, 0]
for x in [15, 16]:
    for y in [2, 3]:
        art[str(y * 24 + x)] = [255, 255, 0]
# Mouth (row 5-6, columns 6-17)
for x in range(6, 18):
    art[str(5 * 24 + x)] = [255, 255, 0]
for x in [6, 17]:
    art[str(4 * 24 + x)] = [255, 255, 0]
display_art(art, 5)

# Pattern 2: Rainbow stripes (horizontal)
print("2/3 Rainbow stripes...")
rainbow = [
    [255, 0, 0], [255, 127, 0], [255, 255, 0], [0, 255, 0],
    [0, 255, 255], [0, 0, 255], [75, 0, 130], [148, 0, 211]
]
art2 = {}
for y in range(8):
    for x in range(24):
        art2[str(y * 24 + x)] = rainbow[y]
display_art(art2, 5)

# Pattern 3: Checkerboard (red/white)
print("3/3 Checkerboard...")
art3 = {}
for y in range(8):
    for x in range(24):
        if (x + y) % 2 == 0:
            art3[str(y * 24 + x)] = [255, 0, 0]
        else:
            art3[str(y * 24 + x)] = [255, 255, 255]
display_art(art3, 5)

chunked_clear(pixels)
print("All art tests complete!")
