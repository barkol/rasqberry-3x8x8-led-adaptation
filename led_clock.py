#!/usr/bin/env python3
"""LED matrix clock display - shows current time HH:MM with blinking colon."""

import sys
import time
sys.path.insert(0, '/usr/bin')
sys.path.insert(0, '/home/rasqberry/RasQberry-Two/demos/led-painter')

from rq_led_utils import get_led_config, create_neopixel_strip, map_xy_to_pixel

# 4x7 digit font (narrower than 5x7 to fit HH:MM in 24 columns)
DIGITS = {
    '0': [0x3E, 0x41, 0x41, 0x3E],
    '1': [0x00, 0x42, 0x7F, 0x40],
    '2': [0x62, 0x51, 0x49, 0x46],
    '3': [0x22, 0x49, 0x49, 0x36],
    '4': [0x18, 0x14, 0x12, 0x7F],
    '5': [0x27, 0x45, 0x45, 0x39],
    '6': [0x3C, 0x4A, 0x49, 0x30],
    '7': [0x01, 0x71, 0x09, 0x03],
    '8': [0x36, 0x49, 0x49, 0x36],
    '9': [0x06, 0x49, 0x29, 0x1E],
}

DIGIT_WIDTH = 4
COLON_WIDTH = 2
GAP = 1

config = get_led_config()
WIDTH = config['matrix_width']
HEIGHT = config['matrix_height']
layout = config['layout']

pixels = create_neopixel_strip(
    config['led_count'], config['pixel_order'],
    brightness=config['led_default_brightness']
)

# Pride rainbow colors mapped to font rows 0-6 (top of char to bottom)
PRIDE_CHAR = [
    (255, 0, 0),      # row 0 - red
    (255, 127, 0),    # row 1 - orange
    (255, 255, 0),    # row 2 - yellow
    (0, 200, 0),      # row 3 - green
    (0, 100, 255),    # row 4 - blue
    (75, 0, 130),     # row 5 - indigo
    (148, 0, 211),    # row 6 - violet
]


def draw_digit(digit_char, start_x, start_y):
    """Draw a single digit at position."""
    cols = DIGITS.get(digit_char, DIGITS['0'])
    for dx, col_data in enumerate(cols):
        x = start_x + dx
        if x >= WIDTH:
            break
        for y in range(7):
            if col_data & (1 << y):
                display_y = start_y + (HEIGHT - 1 - y)  # flip for display convention
                if 0 <= display_y < HEIGHT and 0 <= x < WIDTH:
                    idx = map_xy_to_pixel(x, display_y, layout)
                    if idx is not None:
                        pixels[idx] = PRIDE_CHAR[y]


def draw_colon(start_x, start_y, visible):
    """Draw blinking colon (two dots)."""
    if not visible:
        return
    for y_offset in [2, 5]:
        display_y = start_y + (HEIGHT - 1 - y_offset)
        if 0 <= display_y < HEIGHT and 0 <= start_x < WIDTH:
            idx = map_xy_to_pixel(start_x, display_y, layout)
            if idx is not None:
                pixels[idx] = PRIDE_CHAR[y_offset]


print("LED Clock running... Ctrl+C to stop")

try:
    while True:
        now = time.localtime()
        h = f"{now.tm_hour:02d}"
        m = f"{now.tm_min:02d}"
        colon_on = now.tm_sec % 2 == 0

        # Clear display
        pixels.fill((0, 0, 0))

        # Calculate total width: 4 digits (4px each) + colon (2px) + 4 gaps
        total_w = DIGIT_WIDTH * 4 + COLON_WIDTH + GAP * 4
        start_x = (WIDTH - total_w) // 2
        y_offset = 0

        x = start_x
        draw_digit(h[0], x, y_offset)
        x += DIGIT_WIDTH + GAP
        draw_digit(h[1], x, y_offset)
        x += DIGIT_WIDTH + GAP
        draw_colon(x, y_offset, colon_on)
        x += COLON_WIDTH + GAP
        draw_digit(m[0], x, y_offset)
        x += DIGIT_WIDTH + GAP
        draw_digit(m[1], x, y_offset)

        pixels.show()
        time.sleep(0.5)

except KeyboardInterrupt:
    pixels.fill((0, 0, 0))
    pixels.show()
    print("\nClock stopped.")
