#!/bin/bash
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# Chip top finishing script: Logo addition and fill pattern generation
# Input is a top GDS without filling
# Output is a top GDS with the logo added and filling on all layers
# Usage: ./add_logo_fill.sh <top cell>, make add-logo-fill passes TOP from the Makefile

# Abort on the first failing step instead of reporting success at the end.
set -eo pipefail

DESIGN="$1"
if [ -z "$DESIGN" ]; then
    echo "[ERROR] Usage: ./add_logo_fill.sh <top cell>"
    exit 1
fi
SCRIPTS_DIR="../flow/artistic/scripts"
GDS_DIR="../layout"
IMG_DIR="../flow/logo"
TOP_METAL_LAYER=134

# Floorplan coordinates in um
DIE_LLX=0      # Die lower-left X coordinate (layout origin)
DIE_LLY=0      # Die lower-left Y coordinate (layout origin)
DIE_URX=1600   # Die upper-right X coordinate
DIE_URY=1600   # Die upper-right Y coordinate
CORE_LLX=365   # Core lower-left X coordinate
CORE_LLY=365   # Core lower-left Y coordinate
CORE_URX=1235  # Core upper-right X coordinate
CORE_URY=1235  # Core upper-right Y coordinate

# Logo placement relative to the core lower-left corner in um
LOGO_CORE_MARGIN_LEFT=35
LOGO_CORE_MARGIN_BOTTOM=165

# Fill distances in um between the generated filler shapes (smaller distance = higher fill density).
# The PDK defaults (M1/M2: 1.5, M3-M5: 2.0, TM1/TM2: 3.05) leave the top level too sparse and the
# KLayout DRC min-density checks fail. The global density windows of the regular KLayout DRC are
# 35 to 60 percent on Metal1 to Metal5, 35 to 55 percent on Activ, at least 15 percent on GatPoly and
# 25 to 70 percent on TopMetal1 and TopMetal2. Measured on this chip with the values below: Activ 46.6,
# GatPoly 19.7, Metal1 54.9, Metal2 51.8, Metal3 55.5, Metal4 56.5, Metal5 56.8, TopMetal1 43.4 and
# TopMetal2 43.4 percent. Metal3 to Metal5 get a larger distance than Metal1 and Metal2, because
# 0.75 um puts them at 61.0, 62.0 and 62.3 percent.
# DRC limits: M1Fil.b-M5Fil.b min filler space = 0.42 um. TM1Fil.b/TM2Fil.b min filler space = 3.0 um,
# so TopMetal stays at the PDK default of 3.05 (2.0 gave 70279 TM1Fil.b/TM2Fil.b violations).
# TM1Fil.c/TM2Fil.c (filler to drawn TopMetal, 3.0 um) is unaffected as it is handled by the exclusion
# sizing in the fill macro.
FILL_DIST_M1=0.75
FILL_DIST_M2=0.75
FILL_DIST_M3=1.25
FILL_DIST_M4=1.25
FILL_DIST_M5=1.25
FILL_DIST_TM=3.05  # shared by TopMetal1 and TopMetal2

# meerkat.py expects die-relative margins from layout origin (0,0)
LOGO_MARGIN_LEFT=$((CORE_LLX + LOGO_CORE_MARGIN_LEFT))
LOGO_MARGIN_BOTTOM=$((CORE_LLY + LOGO_CORE_MARGIN_BOTTOM))

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
#   img_width  [px] = logo_width  [µm] / 2 ≤ (die_width  - 2 * die_margin_left)   / 2
#   img_height [px] = logo_height [µm] / 2 ≤ (die_height - 2 * die_margin_bottom) / 2
#
# This uses symmetric margins on both sides:
#   left margin = right margin = die_margin_left
#   bottom margin = top margin = die_margin_bottom
#
# Core-relative margins are converted to die-relative margins using:
#   die_margin_left   = CORE_LLX + LOGO_CORE_MARGIN_LEFT
#   die_margin_bottom = CORE_LLY + LOGO_CORE_MARGIN_BOTTOM
#
# For this chip (die = 1600 x 1600 µm, core LL = (365,365) µm,
# logo core-relative margins = (35,165) µm):
#
#   die margins = (LOGO_MARGIN_LEFT, LOGO_MARGIN_BOTTOM) = (400,530) µm
#   max img_width  = (1600 - 2*400) / 2 = 400 px → 800 µm on-chip
#   max img_height = (1600 - 2*530) / 2 = 270 px → 540 µm on-chip
#
# Current image (chip_logo_mono.png): 400x270 px → 800x540 µm on-chip
#   placed symmetrically with die margins (left,right,bottom,top)
#   = (400,400,530,530) µm
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
#   -m  Logo placement margins in um from die origin (0,0): left,bottom
#       (computed from core-relative placement variables above)
#   -i  Input logo image (monochrome PNG, 1-bit b/w)
#   -g  Top-metal GDS used as mask (existing metal is excluded from logo)
#   -l  Target layer number for the logo geometry
#   -n  Name of the logo cell written into the output GDS
#   -o  Output logo GDS file
python3 "${SCRIPTS_DIR}/meerkat.py" \
    -m "${LOGO_MARGIN_LEFT},${LOGO_MARGIN_BOTTOM}" \
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

# Add fill patterns with adjusted fill distances.
# The PDK filler macros hard-code the distances (only a GUI dialog can change them, which is
# unavailable in batch mode). Therefore copy the macros into a temporary fake PDK tree, patch
# the distances in the copies, and run the unmodified PDK filler.py with PDK_ROOT pointing at
# the fake tree (filler.py locates the macros via $PDK_ROOT/$PDK).
FILL_PDK_DIR="${PWD}/fill_pdk_patched"
MACRO_SRC="${PDKPATH}/libs.tech/klayout/tech/macros"
MACRO_DST="${FILL_PDK_DIR}/${PDK}/libs.tech/klayout/tech/macros"
rm -rf "$FILL_PDK_DIR"
mkdir -p "$MACRO_DST"
cp "${MACRO_SRC}/sg13g2_filler_ActGatP.lym" \
   "${MACRO_SRC}/sg13g2_filler_Metal.lym" \
   "${MACRO_SRC}/sg13g2_filler_TopMetal.lym" \
   "$MACRO_DST/"

# Patch the batch-mode fill distances (Metal: per-layer map, TopMetal: shared variable)
sed -i \
    -e "s/'distance_m1' => [0-9.]*/'distance_m1' => ${FILL_DIST_M1}/" \
    -e "s/'distance_m2' => [0-9.]*/'distance_m2' => ${FILL_DIST_M2}/" \
    -e "s/'distance_m3' => [0-9.]*/'distance_m3' => ${FILL_DIST_M3}/" \
    -e "s/'distance_m4' => [0-9.]*/'distance_m4' => ${FILL_DIST_M4}/" \
    -e "s/'distance_m5' => [0-9.]*/'distance_m5' => ${FILL_DIST_M5}/" \
    "${MACRO_DST}/sg13g2_filler_Metal.lym"
sed -i \
    -e "s/^\(\s*\)distance = [0-9.]*/\1distance = ${FILL_DIST_TM}/" \
    "${MACRO_DST}/sg13g2_filler_TopMetal.lym"

# Guard: fail loudly if the PDK macro text changed and the patches did not apply
for PATCHED in "'distance_m1' => ${FILL_DIST_M1}" "'distance_m5' => ${FILL_DIST_M5}"; do
    grep -qF "$PATCHED" "${MACRO_DST}/sg13g2_filler_Metal.lym" || {
        echo "[ERROR] Failed to patch Metal fill distances (PDK macro changed?)"; exit 1; }
done
grep -qE "^\s*distance = ${FILL_DIST_TM}" "${MACRO_DST}/sg13g2_filler_TopMetal.lym" || {
    echo "[ERROR] Failed to patch TopMetal fill distance (PDK macro changed?)"; exit 1; }

echo "[INFO] Fill distances: M1-M5 = ${FILL_DIST_M1}/${FILL_DIST_M2}/${FILL_DIST_M3}/${FILL_DIST_M4}/${FILL_DIST_M5} um, TM1/TM2 = ${FILL_DIST_TM} um"

PDK_ROOT="$FILL_PDK_DIR" klayout -zz \
    -rd output_file="${GDS_OUT_FILL}" \
    -r $PDKPATH/libs.tech/klayout/tech/scripts/filler.py \
    "${GDS_OUT}"

# Add the die outline on prBoundary.drawing (189/0) to the finished top cell.
# The density checks of the regular KLayout DRC deck take the chip area from the 189/0 polygons
# whenever any exist. A LibreLane chip carries 189/0 only inside the macros it places (its own die
# area is on 189/4), so without the outline the deck divides the layer areas of the whole die by the
# bounding box of the macro boundaries and reports false maximum-density violations on every layer.
echo "[INFO] Adding the die outline on prBoundary.drawing (189/0)..."
klayout -zz \
    -rd "gds_file=$GDS_OUT_FILL" \
    -rd "layer=189/0" \
    -rd "margin=0" \
    -r add_rectangle.py

# Cleanup intermediate files
rm -rf "$FILL_PDK_DIR"
rm -f "$GDS_TM2" "$GDS_LOGO" "$GDS_OUT" meerkat_design.py

echo "[INFO] Finished. Output GDS: ${GDS_OUT_FILL}"
