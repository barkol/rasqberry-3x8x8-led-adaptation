#!/bin/bash
set -euo pipefail

################################################################################
# apply.sh - Apply 3x WS2812B-64 (8x8) panel adaptation to RasQberry-Two
#
# Replaces the original quad (4x12) / single (column-serpentine) LED mapping
# with a triple 8x8 row-serpentine layout.
#
# What this script does:
#   1. Patches /usr/config/rasqberry_environment.env (LED_MATRIX_LAYOUT, Y_FLIP)
#   2. Installs patched rq_led_utils.py with triple_8x8 mapping to /usr/bin/
#   3. Patches LED Painter's LED_array_indices.py (if installed)
#   4. Patches virtual LED GUI with triple_8x8 mapping
#   5. Copies adapted IBM demo to /usr/bin/
#
# Usage:  sudo bash apply.sh
#         sudo bash apply.sh --dry-run    (show what would be changed)
#         sudo bash apply.sh --revert     (undo all changes from backups)
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Paths — on pi-gen images, RQB2-bin/* is installed to /usr/bin/
#   and RQB2-config/* to /usr/config/. Demos clone into ~/RasQberry-Two/demos/.
ENV_FILE="/usr/config/rasqberry_environment.env"
LED_UTILS_DEST="/usr/bin/rq_led_utils.py"
VIRTUAL_GUI_DEST="/usr/bin/rq_led_virtual_gui.py"
IBM_DEMO_DEST="/usr/bin/neopixel_spi_IBMtestFunc_3x8x8.py"

# Detect user home (rasqberry on image, or current user)
if [ -d "/home/rasqberry" ]; then
    RASQBERRY_HOME="/home/rasqberry"
else
    RASQBERRY_HOME="$HOME"
fi
PAINTER_DIR="$RASQBERRY_HOME/RasQberry-Two/demos/led-painter"

# Source files (in same directory as this script)
SRC_LED_UTILS="$SCRIPT_DIR/rq_led_utils_3x8x8.py"
SRC_VIRTUAL_GUI="$SCRIPT_DIR/rq_led_virtual_gui_3x8x8.py"
SRC_ARRAY_INDICES="$SCRIPT_DIR/LED_array_indices_3x8x8.py"
SRC_IBM_DEMO="$SCRIPT_DIR/neopixel_spi_IBMtestFunc_3x8x8.py"

# Backup suffix
BACKUP=".bak-quad"

DRY_RUN=false
REVERT=false

# --- Helpers ---

info()  { echo -e "\033[1;32m[OK]\033[0m  $*"; }
warn()  { echo -e "\033[1;33m[!!]\033[0m  $*"; }
skip()  { echo -e "\033[0;36m[--]\033[0m  $*"; }
fail()  { echo -e "\033[1;31m[ERR]\033[0m $*"; exit 1; }

backup_and_copy() {
    local src="$1" dest="$2"
    if $DRY_RUN; then
        echo "  would copy: $src -> $dest"
        return
    fi
    if [ -f "$dest" ] && [ ! -f "${dest}${BACKUP}" ]; then
        cp "$dest" "${dest}${BACKUP}"
    fi
    cp "$src" "$dest"
}

restore_backup() {
    local dest="$1"
    if [ -f "${dest}${BACKUP}" ]; then
        if $DRY_RUN; then
            echo "  would restore: ${dest}${BACKUP} -> $dest"
            return
        fi
        mv "${dest}${BACKUP}" "$dest"
        info "Restored $dest"
    else
        skip "No backup for $dest"
    fi
}

# --- Parse args ---

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --revert)  REVERT=true ;;
        -h|--help)
            echo "Usage: sudo bash apply.sh [--dry-run] [--revert]"
            echo ""
            echo "  --dry-run   Show what would be changed without making changes"
            echo "  --revert    Restore original files from backups"
            exit 0
            ;;
        *) fail "Unknown argument: $arg" ;;
    esac
done

# --- Root check ---

if [ "$(id -u)" -ne 0 ] && ! $DRY_RUN; then
    fail "This script must be run as root (sudo bash apply.sh)"
fi

echo ""
echo "=== RasQberry-Two: 3x WS2812B-64 (8x8) panel adaptation ==="
echo ""

# --- Revert mode ---

if $REVERT; then
    echo "Reverting to original panel configuration..."
    echo ""
    restore_backup "$ENV_FILE"
    restore_backup "$LED_UTILS_DEST"
    [ -f "$PAINTER_DIR/LED_array_indices.py" ] && restore_backup "$PAINTER_DIR/LED_array_indices.py"
    restore_backup "$VIRTUAL_GUI_DEST"
    restore_backup "$IBM_DEMO_DEST"
    echo ""
    info "Revert complete. Original quad/single panel layout restored."
    exit 0
fi

# --- Verify source files exist ---

for f in "$SRC_LED_UTILS" "$SRC_VIRTUAL_GUI" "$SRC_ARRAY_INDICES" "$SRC_IBM_DEMO"; do
    [ -f "$f" ] || fail "Missing source file: $f"
done

# --- 1. Patch environment config ---

echo "1. Patching $ENV_FILE ..."

if [ -f "$ENV_FILE" ]; then
    if $DRY_RUN; then
        echo "  would set LED_MATRIX_LAYOUT=triple_8x8"
        echo "  would set LED_MATRIX_Y_FLIP=false"
    else
        # Backup
        if [ ! -f "${ENV_FILE}${BACKUP}" ]; then
            cp "$ENV_FILE" "${ENV_FILE}${BACKUP}"
        fi
        sed -i 's/^LED_MATRIX_LAYOUT=.*/LED_MATRIX_LAYOUT=triple_8x8/' "$ENV_FILE"
        sed -i 's/^LED_MATRIX_Y_FLIP=.*/LED_MATRIX_Y_FLIP=false/' "$ENV_FILE"
        info "Environment config patched"
    fi
else
    warn "$ENV_FILE not found (not running on a RasQberry image?)"
fi

# --- 2. Install patched rq_led_utils.py ---

echo "2. Installing patched rq_led_utils.py ..."

if [ -f "$LED_UTILS_DEST" ]; then
    backup_and_copy "$SRC_LED_UTILS" "$LED_UTILS_DEST"
    $DRY_RUN || info "Installed $LED_UTILS_DEST"
else
    # File doesn't exist yet (main branch image) -- install anyway
    if $DRY_RUN; then
        echo "  would create: $LED_UTILS_DEST"
    else
        cp "$SRC_LED_UTILS" "$LED_UTILS_DEST"
        info "Created $LED_UTILS_DEST (was not present)"
    fi
fi

# --- 3. Patch LED Painter ---

echo "3. Patching LED Painter pixel mapping ..."

if [ -d "$PAINTER_DIR" ]; then
    backup_and_copy "$SRC_ARRAY_INDICES" "$PAINTER_DIR/LED_array_indices.py"
    $DRY_RUN || info "LED Painter patched"
else
    skip "LED Painter not installed at $PAINTER_DIR (run it once to install, then re-run this script)"
fi

# --- 4. Patch virtual LED GUI ---

echo "4. Patching virtual LED GUI ..."

if [ -f "$VIRTUAL_GUI_DEST" ]; then
    backup_and_copy "$SRC_VIRTUAL_GUI" "$VIRTUAL_GUI_DEST"
    $DRY_RUN || info "Virtual LED GUI patched at $VIRTUAL_GUI_DEST"
else
    if $DRY_RUN; then
        echo "  would create: $VIRTUAL_GUI_DEST"
    else
        cp "$SRC_VIRTUAL_GUI" "$VIRTUAL_GUI_DEST"
        info "Created $VIRTUAL_GUI_DEST (was not present)"
    fi
fi

# --- 5. Copy IBM demo to /usr/bin/ (where RQB2-bin/* is installed) ---

echo "5. Installing adapted IBM demo ..."

if $DRY_RUN; then
    echo "  would copy: $SRC_IBM_DEMO -> $IBM_DEMO_DEST"
else
    backup_and_copy "$SRC_IBM_DEMO" "$IBM_DEMO_DEST"
    info "IBM demo installed to $IBM_DEMO_DEST"
fi

# --- Done ---

echo ""
if $DRY_RUN; then
    echo "Dry run complete. No files were changed."
else
    info "All done! Your 3x WS2812B-64 (8x8) panels are configured."
    echo ""
    echo "  Test with:  python3 $IBM_DEMO_DEST"
    echo "  Revert:     sudo bash $SCRIPT_DIR/apply.sh --revert"
    echo ""
    echo "  If LED Painter was not installed yet, install it first then re-run:"
    echo "      sudo bash apply.sh"
fi
