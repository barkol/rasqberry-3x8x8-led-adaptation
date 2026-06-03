#!/usr/bin/env python3
"""Test all text display modes on the LED matrix."""

from rq_led_utils import (
    get_led_config, create_neopixel_strip,
    display_scrolling_text, display_static_text,
    display_flashing_text, display_scrolling_text_rainbow,
    display_static_text_rainbow, display_text_gradient,
)

config = get_led_config()
pixels = create_neopixel_strip(
    config['led_count'], config['pixel_order'],
    brightness=config['led_default_brightness']
)

print("1/6 Scrolling text (green)...")
display_scrolling_text(pixels, "HELLO RASQBERRY!", duration_seconds=10, scroll_speed=0.08, color=(0, 255, 0))

print("2/6 Static text...")
display_static_text(pixels, "TEST", duration_seconds=4, color=(255, 255, 0))

print("3/6 Flashing text (red)...")
display_flashing_text(pixels, "ALERT", flash_count=4, flash_speed=0.5, color=(255, 0, 0))

print("4/6 Rainbow scrolling text...")
display_scrolling_text_rainbow(pixels, "QUANTUM!", duration_seconds=10, scroll_speed=0.08)

print("5/6 Static rainbow text...")
display_static_text_rainbow(pixels, "RGB", duration_seconds=5)

print("6/6 Gradient text...")
display_text_gradient(pixels, "GRAD", duration_seconds=4, color1=(255, 0, 0), color2=(0, 0, 255))

print("All tests complete!")
