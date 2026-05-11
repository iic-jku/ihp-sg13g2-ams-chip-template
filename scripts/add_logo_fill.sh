# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0

#!/bin/bash
#
# Chip top finishing script: Logo addition and fill pattern generation
# Input is a top GDS without filling
# Output is a top GDS with the logo added and filling on all layers

DESIGN="chip_top"
SCRIPTS_DIR="../flow/artistic/scripts"
GDS_DIR="../layout"
IMG_DIR="../flow/logo"
TOP_METAL_LAYER=134

GDS_IN="${GDS_DIR}/${DESIGN}.gds.gz"
GDS_TM2="${GDS_DIR}/${DESIGN}_tm2.gds"
GDS_LOGO="${GDS_DIR}/${DESIGN}_logo.gds"
GDS_OUT="${GDS_DIR}/${DESIGN}_logo.gds.gz"
GDS_OUT_FILL="${GDS_DIR}/${DESIGN}_logo_fill.gds.gz"
LOGO_IMG="${IMG_DIR}/chip_logo_mono.png"

# ─── Logo sizing guide ────────────────────────────────────────────────────────
# meerkat.py maps each image pixel to one GDS pixel of size PIXSZ = 2 µm.
# The logo image must therefore satisfy:
#
#   img_width  [px] = logo_width  [µm] / 2 ≤ (die_width  - margin_left)   / 2
#   img_height [px] = logo_height [µm] / 2 ≤ (die_height - margin_bottom) / 2
#
# For this chip (die = 1600×1600 µm, -m left=250, bottom=475):
#
#   max img_width  = (1600 - 250) / 2 = 675 px → logo spans up to x = 1600 µm
#   max img_height = (1600 - 475) / 2 = 562 px → logo spans up to y = 1600 µm
#
# Current logo (chip_logo_mono.png): 675×495 px → 1350×990 µm on-chip
#   placed at bottom-left corner (250, 475) µm, top-right corner (1600, 1465) µm
# ─────────────────────────────────────────────────────────────────────────────

echo "[INFO] Adding logo and fill to ${GDS_IN}"

# Export top metal layer TM2
# meerkat_interface.py arguments:
#   -i  Input GDS (vanilla chip without logo)
#   -m  Output top-metal-only GDS used as mask for logo placement
#   -g  Output logo GDS (will be written by meerkat.py)
#   -o  Merged output GDS (chip + logo)
#   -w  Work directory for the generated meerkat_design.py interface file
#   -l  Logo layer number (TM2 = 134)
#   -n  Name of the new merged top-level cell in the output GDS
python3 "${SCRIPTS_DIR}/meerkat_interface.py" \
    -i "$GDS_IN" \
    -m "$GDS_TM2" \
    -g "$GDS_LOGO" \
    -o "$GDS_OUT" \
    -w "$PWD" \
    -l "$TOP_METAL_LAYER" \
    -n "${DESIGN}_logo_fill" \
    > /dev/null
klayout -zz -rm "${SCRIPTS_DIR}/export_top_metal.py"

# Transform logo to GDS
# meerkat.py arguments:
#   -m  Logo placement margins from bottom-left corner in um: left,bottom
#   -i  Input logo image (monochrome PNG, 1-bit b/w)
#   -g  Top-metal GDS used as mask (existing metal is excluded from logo)
#   -l  Target layer number for the logo geometry
#   -n  Name of the logo cell written into the output GDS
#   -o  Output logo GDS file
python3 "${SCRIPTS_DIR}/meerkat.py" \
    -m 250,475 \
    -i "$LOGO_IMG" \
    -g "$GDS_TM2" \
    -l "$TOP_METAL_LAYER" \
    -n "$DESIGN" \
    -o "$GDS_LOGO" \
    > /dev/null

# Add rectangles around the logo on specified layers
# RECT_LAYERx: layer/datatype tuple, RECT_MARGINx: extra space in um
RECT_LAYER1="134/23"
RECT_MARGIN1=20
RECT_LAYER2="126/23"
RECT_MARGIN2=0

for RECT_LAYER_VAR in 1 2; do
    eval "RECT_LAYER=\$RECT_LAYER${RECT_LAYER_VAR}"
    eval "RECT_MARGIN=\$RECT_MARGIN${RECT_LAYER_VAR}"
    klayout -zz \
        -rd "gds_file=$GDS_LOGO" \
        -rd "layer=$RECT_LAYER" \
        -rd "margin=$RECT_MARGIN" \
        -r add_rectangle.py
done

# Merge logo into chip
klayout -zz -rm "${SCRIPTS_DIR}/merge_logo.py"

echo "[INFO] Logo added. Now adding fill patterns..."

# Add fill patterns
klayout -zz \
    -rd output_file="${GDS_OUT_FILL}" \
    -r $PDKPATH/libs.tech/klayout/tech/scripts/filler.py \
    "${GDS_OUT}"

# Cleanup intermediate files
rm -f "$GDS_TM2" "$GDS_LOGO" "$GDS_OUT" meerkat_design.py

echo "[INFO] Finished. Output GDS: ${GDS_OUT_FILL}"
