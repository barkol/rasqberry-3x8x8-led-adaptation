"""
LED Array Indices for 3x WS2812B-64 (8x8) panels, daisy-chained left-to-right.

Each panel uses progressive (non-serpentine) row wiring:
  - All rows go left to right
  - Pixel 0 at top-left corner of each panel

Panel chaining: Panel 0 (pixels 0-63) -> Panel 1 (64-127) -> Panel 2 (128-191)

GUI index is row-major: index i -> row i//24, column i%24
This dict maps GUI index -> physical LED index.

Drop-in replacement for LED_array_indices.py in the LED-Painter repo
(https://github.com/Luka-D/RasQberry-Two-LED-Painter).
"""

LED_ARRAY_INDICES = {}
for _i in range(192):
    _y = _i // 24        # row (0-7)
    _x = _i % 24         # column (0-23)
    _panel = _x // 8
    _col = _x % 8
    LED_ARRAY_INDICES[_i] = _panel * 64 + _y * 8 + _col

# Clean up loop variables
del _i, _y, _x, _panel, _col
