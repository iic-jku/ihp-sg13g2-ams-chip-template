# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the tank coil layout layout/vco_ind.gds from the PDK inductor3 PCell.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_ind.py [-rd out=<file.gds>], or make klayout-script CELL=vco_ind
# The PCell is flattened into the cell vco_ind, so the GDS carries no PCell context and every tool reads it as drawn.

import importlib
import os
import sys

import pya

# Coil geometry in um. The PCell parameter d is the inner diameter: 58 um inner gives 82 um outer.
W, S, D_INNER, TURNS = 4, 4, 58, 2

# Substrate tap left of the feeds, below the inductor keep-out (y < 0)
TAP_W, TAP_L = 4, 1
TAP_X, TAP_Y = -30, -3

# Pin labels on <metal>.text, at the PCell's feed pins (LA/LB on TopMetal1, LC on TopMetal2).
# They repeat the PCell's IND.text names, because a second name on the same net fails the strict port check of LVS.
# LVS compares names case-insensitively, so LA matches the schematic pin la.
LABELS = [("LA", (126, 25), -8, 0), ("LB", (126, 25), 8, 0), ("LC", (134, 25), 0, 0), ("VSS", (8, 25), TAP_X, TAP_Y)]

CELL = "vco_ind"
here = os.path.dirname(os.path.abspath(__file__))
out_file = globals().get("out") or os.path.join(here, "..", "..", "layout", f"{CELL}.gds")

# Batch mode does not run the PDK's autorun macros, so register the SG13_dev library here
kl = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], "libs.tech", "klayout", "python")
for d in (kl, os.path.join(kl, "pycell4klayout-api", "source", "python")):
    if d not in sys.path:
        sys.path.append(d)
if pya.Library.library_by_name("SG13_dev", "sg13g2") is None:
    importlib.import_module("sg13g2_pycell_lib")

ly = pya.Layout()
ly.dbu = 0.001
ly.technology_name = "sg13g2"
top = ly.create_cell(CELL)

# subE=0, not False: the PCell draws the backside etch layer LBE for the boolean False
ind = ly.create_cell("inductor3", "SG13_dev", {"w": f"{W}u", "s": f"{S}u", "d": f"{D_INNER}u", "nr_r": TURNS, "subE": 0})
tap = ly.create_cell("ptap1", "SG13_dev", {"w": f"{TAP_W}u", "l": f"{TAP_L}u"})
if ind is None or tap is None:
    sys.exit("vco_ind.py: PCell inductor3 or ptap1 not found in library SG13_dev")
top.insert(pya.CellInstArray(ind.cell_index(), pya.Trans()))
tap_box = tap.dbbox()
top.insert(pya.DCellInstArray(tap.cell_index(), pya.DTrans(TAP_X - tap_box.center().x, TAP_Y - tap_box.center().y)))
top.flatten(-1, True)

for text, (layer, datatype), x, y in LABELS:
    top.shapes(ly.layer(layer, datatype)).insert(pya.DText(text, x, y))

opt = pya.SaveLayoutOptions()
opt.write_context_info = False
ly.write(out_file, opt)
print(f"vco_ind.py: wrote {os.path.normpath(out_file)}, cell {CELL}, bbox {top.dbbox()}")
# ==============================================================================
