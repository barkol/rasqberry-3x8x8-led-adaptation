# 3x WS2812B-64 (8x8) Panel Adaptation

Replaces the original RasQberry-Two LED panel mapping (quad 4x12 or single
column-serpentine) with a mapping for **3 daisy-chained WS2812B-64 8x8 panels**
with row-serpentine wiring.

## Quick start

Copy this folder to your Raspberry Pi and run:

```bash
sudo bash apply.sh
```

That's it. All LED demos (text, logos, LED Painter, IBM demo) will use the new mapping.

## What's in the folder

```
3x8x8-adaptation/
  apply.sh                           # Install script (run with sudo)
  rq_led_utils_3x8x8.py             # Patched LED utils with triple_8x8 layout
  LED_array_indices_3x8x8.py         # Pixel map for LED Painter
  neopixel_spi_IBMtestFunc_3x8x8.py  # Adapted IBM logo demo
  README.md                           # This file
```

## What apply.sh does

1. Sets `LED_MATRIX_LAYOUT=triple_8x8` and `LED_MATRIX_Y_FLIP=false` in
   `/usr/config/rasqberry_environment.env`
2. Installs patched `rq_led_utils.py` to `/usr/bin/` (adds `triple_8x8` mapping)
3. Replaces `LED_array_indices.py` in the LED Painter directory (if installed)
4. Copies the adapted IBM demo to `RQB2-bin/`

Backups of all replaced files are saved with a `.bak-quad` suffix.

## Options

```bash
sudo bash apply.sh              # Apply the adaptation
sudo bash apply.sh --dry-run    # Preview changes without modifying anything
sudo bash apply.sh --revert     # Restore original files from backups
```

## Wiring

Daisy-chain three panels left-to-right, data on GPIO 18:

```
RPi GPIO 18 --> [Panel 0 DIN] --> [Panel 1 DIN] --> [Panel 2 DIN]
```

Each panel: 8x8, row-serpentine, pixel 0 at top-left.

```
Row 0:  0 ->  1 ->  2 ->  3 ->  4 ->  5 ->  6 ->  7
Row 1: 15 <- 14 <- 13 <- 12 <- 11 <- 10 <-  9 <-  8
...alternating each row
```

Panels form a single 8-row x 24-column grid (192 pixels):
- Panel 0: pixels 0-63   (columns 0-7)
- Panel 1: pixels 64-127  (columns 8-15)
- Panel 2: pixels 128-191 (columns 16-23)

## LED Painter note

The LED Painter is installed on first launch (via `rq_led_painter.sh` or the
desktop icon). If you run `apply.sh` before that, the Painter patch is skipped.
Just re-run `sudo bash apply.sh` after the Painter is installed.

## Verifying

Light pixels one-by-one to confirm wiring:

```bash
python3 -c "
import time, board, neopixel_spi as neopixel
spi = board.SPI()
px = neopixel.NeoPixel_SPI(spi, 192, pixel_order=neopixel.GRB, auto_write=False)
for i in range(192):
    px.fill(0); px[i] = 0xFF0000; px.show(); time.sleep(0.05)
"
```

Pixel 0 should light at the top-left of the first (leftmost) panel.
