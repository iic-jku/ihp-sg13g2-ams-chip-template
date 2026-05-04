# SPDX-FileCopyrightText: 2025-2026 Simon Dorrer
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

echo "[INFO] Adding logo and fill to ${GDS_IN}"

# Export top metal layer TM2
python3 "${SCRIPTS_DIR}/meerkat_interface.py" \
    -i "$GDS_IN" \
    -m "$GDS_TM2" \
    -g "$GDS_LOGO" \
    -o "$GDS_OUT" \
    -w "$PWD" \
    -l "$TOP_METAL_LAYER" \
    > /dev/null
klayout -zz -rm "${SCRIPTS_DIR}/export_top_metal.py"

# Transform logo to GDS
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
