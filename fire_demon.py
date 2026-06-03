#!/usr/bin/env python3
"""Fire and flames demon-inspired animated LED art."""

import sys
import time
import random
sys.path.insert(0, '/usr/bin')
sys.path.insert(0, '/home/rasqberry/RasQberry-Two/demos/led-painter')

from rq_led_utils import get_pixels, chunked_clear
from LED_array_indices import LED_ARRAY_INDICES

pixels = get_pixels(0.4)
WIDTH = 24
HEIGHT = 8
DURATION = None  # infinite loop

# Fire palette: black → red → orange → yellow → white
FIRE_PALETTE = [
    (0, 0, 0),       # 0  black
    (20, 0, 0),      # 1  dark ember
    (40, 0, 0),      # 2
    (60, 2, 0),      # 3
    (80, 4, 0),      # 4  deep red
    (110, 8, 0),     # 5
    (140, 15, 0),    # 6  red
    (170, 25, 0),    # 7
    (200, 40, 0),    # 8  red-orange
    (220, 60, 0),    # 9
    (240, 80, 0),    # 10 orange
    (250, 110, 0),   # 11
    (255, 140, 0),   # 12 bright orange
    (255, 170, 10),  # 13
    (255, 200, 30),  # 14 yellow-orange
    (255, 220, 60),  # 15
    (255, 240, 90),  # 16 yellow
    (255, 250, 130), # 17
    (255, 255, 170), # 18 pale yellow
    (255, 255, 220), # 19 near white
    (255, 255, 255), # 20 white hot
]

# Demon eye colors
EYE_RED = (255, 0, 0)
EYE_GLOW = (180, 0, 0)
PUPIL = (40, 0, 0)

# Heat buffer (wider than display for smoother edges)
heat = [[0] * WIDTH for _ in range(HEIGHT + 2)]


def fire_step():
    """Advance fire simulation one step."""
    # Random heat sources at bottom row
    for x in range(WIDTH):
        heat[HEIGHT + 1][x] = random.randint(12, 20)
        heat[HEIGHT][x] = random.randint(10, 18)

    # Propagate heat upward with cooling and spread
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Average of nearby pixels below + random cooling
            left = max(0, x - 1)
            right = min(WIDTH - 1, x + 1)
            avg = (
                heat[y + 1][left] +
                heat[y + 1][x] +
                heat[y + 1][right] +
                heat[y + 2][x]
            ) // 4
            cooling = random.randint(0, 2)
            heat[y][x] = max(0, avg - cooling)


def render_fire():
    """Render fire to LED strip."""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            idx = y * WIDTH + x
            led_idx = LED_ARRAY_INDICES[idx]
            h = min(heat[y][x], len(FIRE_PALETTE) - 1)
            pixels[led_idx] = FIRE_PALETTE[h]


# Capital Greek Psi (Ψ) - 24 cols wide, tall for slow scroll
SYMBOLS = [
    [
        0b000000000000000000000000,
        0b000000000000000000000000,
        0b011000000011000000001100,
        0b011000000011000000001100,
        0b011000000011000000001100,
        0b011000000011000000001100,
        0b011000000011000000001100,
        0b011100000011000000011100,
        0b001110000011000001110000,
        0b000111000011000011100000,
        0b000011110011001111000000,
        0b000001111111111110000000,
        0b000000111111111100000000,
        0b000000011111111000000000,
        0b000000000111100000000000,
        0b000000000011000000000000,
        0b000000000011000000000000,
        0b000000000011000000000000,
        0b000000000011000000000000,
        0b000000000011000000000000,
        0b000000000011000000000000,
        0b000000000011000000000000,
        0b000000000011000000000000,
        0b000000000000000000000000,
        0b000000000000000000000000,
    ],
]

SYMBOL_WIDTH = 24


def demonic_symbols(frame):
    """Scroll tall demonic symbols top-to-bottom, red on black."""
    # Each symbol scrolls for its full height + display height
    sym_idx = _symbol_index[0]
    symbol = SYMBOLS[sym_idx]
    sym_height = len(symbol)
    total_scroll = sym_height + HEIGHT  # full pass through display

    # Scroll position (1 row per 4 frames = slow roll)
    scroll_pos = (frame // 4) % (total_scroll + 10)  # +10 = pause between symbols

    if scroll_pos >= total_scroll:
        # Brief black pause between symbols
        for i in range(WIDTH * HEIGHT):
            led_idx = LED_ARRAY_INDICES[i]
            pixels[led_idx] = (0, 0, 0)
        # Advance to next symbol at end of pause
        if scroll_pos == total_scroll + 9:
            _symbol_index[0] = (sym_idx + 1) % len(SYMBOLS)
        return

    # Pulse the red intensity
    pulse = 0.7 + 0.3 * abs((frame % 20) - 10) / 10.0

    # Black background
    for i in range(WIDTH * HEIGHT):
        led_idx = LED_ARRAY_INDICES[i]
        pixels[led_idx] = (0, 0, 0)

    # Draw visible portion of symbol scrolling down
    for display_y in range(HEIGHT):
        sym_y = display_y + scroll_pos - HEIGHT + 1
        if 0 <= sym_y < sym_height:
            row = symbol[sym_y]
            for x in range(SYMBOL_WIDTH):
                if row & (1 << (SYMBOL_WIDTH - 1 - x)):
                    if 0 <= x < WIDTH:
                        idx = display_y * WIDTH + x
                        led_idx = LED_ARRAY_INDICES[idx]
                        r = int(255 * pulse)
                        g = int(25 * pulse)
                        pixels[led_idx] = (r, g, 0)


# Mutable container for symbol index (to track across calls)
_symbol_index = [0]


def demon_eyes_step(frame):
    """Overlay demon eyes that pulse and shift."""
    pulse = abs((frame % 40) - 20) / 20.0  # 0..1 pulsing
    brightness = 0.5 + 0.5 * pulse

    # Two eyes, slightly shifting position
    shift = 0 if (frame // 60) % 2 == 0 else 1
    eye_y = 2
    left_eye_x = 7 + shift
    right_eye_x = 15 + shift

    for eye_x in [left_eye_x, right_eye_x]:
        # Eye glow (3x3 area)
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                ey = eye_y + dy
                ex = eye_x + dx
                if 0 <= ey < HEIGHT and 0 <= ex < WIDTH:
                    idx = ey * WIDTH + ex
                    led_idx = LED_ARRAY_INDICES[idx]
                    r = int(EYE_GLOW[0] * brightness * 0.4)
                    pixels[led_idx] = (r, 0, 0)

        # Eye outline (bright red ring)
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ey = eye_y + dy
            ex = eye_x + dx
            if 0 <= ey < HEIGHT and 0 <= ex < WIDTH:
                idx = ey * WIDTH + ex
                led_idx = LED_ARRAY_INDICES[idx]
                r = int(EYE_RED[0] * brightness)
                pixels[led_idx] = (r, 0, 0)

        # Pupil center
        idx = eye_y * WIDTH + eye_x
        led_idx = LED_ARRAY_INDICES[idx]
        pixels[led_idx] = PUPIL


def demon_mouth(frame):
    """Flickering jagged mouth."""
    mouth_y = 5
    flicker = random.random() > 0.3

    if not flicker:
        return

    brightness = 0.6 + 0.4 * random.random()
    # Jagged mouth shape
    teeth = [9, 10, 11, 12, 13, 14]
    for x in teeth:
        if random.random() > 0.2:  # some teeth flicker independently
            idx = mouth_y * WIDTH + x
            led_idx = LED_ARRAY_INDICES[idx]
            r = int(255 * brightness)
            g = int(40 * brightness)
            pixels[led_idx] = (r, g, 0)

    # Lower jaw glow
    for x in [10, 11, 12, 13]:
        if random.random() > 0.4:
            idx = (mouth_y + 1) * WIDTH + x
            led_idx = LED_ARRAY_INDICES[idx]
            r = int(180 * brightness)
            pixels[led_idx] = (r, 0, 0)


def horns(frame):
    """Glowing horns above eyes."""
    pulse = abs((frame % 30) - 15) / 15.0
    brightness = 0.3 + 0.7 * pulse

    # Left horn
    for x, y in [(5, 0), (6, 0), (6, 1), (7, 1)]:
        if 0 <= y < HEIGHT and 0 <= x < WIDTH:
            idx = y * WIDTH + x
            led_idx = LED_ARRAY_INDICES[idx]
            r = int(200 * brightness)
            g = int(30 * brightness)
            pixels[led_idx] = (r, g, 0)

    # Right horn
    for x, y in [(17, 0), (18, 0), (17, 1), (16, 1)]:
        if 0 <= y < HEIGHT and 0 <= x < WIDTH:
            idx = y * WIDTH + x
            led_idx = LED_ARRAY_INDICES[idx]
            r = int(200 * brightness)
            g = int(30 * brightness)
            pixels[led_idx] = (r, g, 0)


# === Main animation loop ===
print("Fire & Demon animation starting...")
print(f"Duration: {DURATION}s")

start = time.time()
frame = 0

try:
    while True:
        # Alternate: 5s fire+demon, then 8s symbol
        cycle = frame % 217  # ~13s total cycle
        if cycle < 83:  # ~5s fire phase
            fire_step()
            render_fire()
            demon_eyes_step(frame)
            demon_mouth(frame)
            horns(frame)
        else:  # ~8s symbol phase
            demonic_symbols(frame)
        pixels.show()
        frame += 1
        time.sleep(0.06)
except KeyboardInterrupt:
    pass

chunked_clear(pixels)
print("Done!")
