# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the macro layout/vco_top.gds from the bias, core and buffer cells.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_top.py [-rd out=<file.gds>], or make klayout-script CELL=vco_top
# Needs layout/vco_bias.gds, vco_core.gds and vco_buf.gds. They stay subcells, as in the schematic.
#
# Built around the core's origin (the coil above, its column below), then moved so the PR boundary starts at (0, 0).
# The buffer is centered under the column and fed by the core's Metal5 lines rf_p and rf_n. The bias, turned by
# 270 degrees, fills the space left of the column: its outputs end at its bottom next to Mtop and the buffer, its inputs
# at its top. Power runs on trunks to two straps along the bottom, VSS on Metal5 and VDD on Metal4. Nothing closes a loop
# around the coil.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

BIAS_RIGHT, BIAS_TOP = -23.0, -3.7  # right and top edge of the turned bias cell
YB = -127.0  # origin of the buffer cell, its top edge ends up at YB + 25.1
X_LEFT, X_RIGHT, Y_BOTTOM = -86.0, 75.0, -142.0  # macro edges, the top edge is the coil's keep-out
X_VSS = -84.0  # VSS trunk on Metal5
Y_VSSL = -3.0  # VSS line on Metal5 above the bias, joins the core's spine and the bias
Y_VSS_STRAP, Y_VDD_STRAP = -136.0, -140.0  # bottom straps, VSS on Metal5, VDD on Metal4
Y_IN = -0.9  # y of the input line ibias_100u on Metal3, di_en runs 1.05 um lower, both clear the VSS via stacks

ly = vl.new_layout()
top = vl.Block(ly, "vco_top")

core = vl.read_cell(ly, "vco_core", __file__)
tc = top.add(core, 0, 0)
cp = vl.cell_pins(ly, core, tc)

buf = vl.read_cell(ly, "vco_buf", __file__)
tb = top.add(buf, 0, YB)
bp = vl.cell_pins(ly, buf, tb)

bias = vl.read_cell(ly, "vco_bias", __file__)
bb = bias.dbbox()
tbias = top.add(bias, BIAS_RIGHT - bb.top, BIAS_TOP - (-bb.left), rot=270)
ap = vl.cell_pins(ly, bias, tbias)


def box(pins, name):
    return pins[name][1]


# rf_p, rf_n: the core's Metal5 lines down to the buffer's input tabs
for name in ("rf_p", "rf_n"):
    c, b = box(cp, name), box(bp, name)
    y = b.center().y
    top.rect("Metal5", c.left, y - 0.5, c.right, c.bottom + 0.5)
    top.rect("Metal5", min(c.left, b.center().x), y - 0.5, max(c.right, b.center().x), y + 0.5)

# vbp_core: bias output up on Metal5 and over to the core's pin at Mtop's gate
a, c = box(ap, "vbp_core"), box(cp, "vbp_core")
xa, ya = a.center().x, a.bottom + 0.3
top.via(xa, ya, "Metal3", "Metal5")
top.rect("Metal5", xa - 0.3, ya - 0.3, xa + 0.3, c.center().y + 0.3)
top.rect("Metal5", xa - 0.3, c.center().y - 0.3, c.center().x + 0.3, c.center().y + 0.3)
top.via(c.center().x, c.center().y, "Metal3", "Metal5")

# vbg_buf: bias output down on Metal3 and over to the buffer's pin
a, b = box(ap, "vbg_buf"), box(bp, "vbg_buf")
xa, yb = a.center().x, b.center().y
top.rect("Metal3", xa - 0.3, yb - 0.3, xa + 0.3, a.bottom + 0.5)
top.rect("Metal3", xa - 0.3, yb - 0.3, b.center().x, yb + 0.3)

# vbn_buf: bias output down on Metal4, so it crosses the vbg_buf line, then over to the buffer's pin on Metal3
a, b = box(ap, "vbn_buf"), box(bp, "vbn_buf")
xa, yb = a.center().x, b.center().y
top.via(xa, a.bottom + 0.3, "Metal3", "Metal4")
top.rect("Metal4", xa - 0.3, yb - 0.3, xa + 0.3, a.bottom + 0.6)
top.via(xa, yb, "Metal3", "Metal4")
top.rect("Metal3", xa - 0.3, yb - 0.3, b.center().x, yb + 0.3)

# Inputs: from the top of the bias up to a line each and out to the left edge. di_en's line is the lower one and ends
# before ibias_100u's riser.
for name, yi in (("di_en", Y_IN - 1.05), ("ibias_100u", Y_IN)):
    a = box(ap, name)
    xa = a.center().x
    top.rect("Metal3", xa - 0.3, a.center().y, xa + 0.3, yi + 0.3)
    line = top.rect("Metal3", X_LEFT, yi - 0.3, xa + 0.3, yi + 0.3)
    top.pin("Metal3", name, pya.DBox(line.left, line.bottom, line.left + 1.0, line.top))

# vtune: the core's line down to below Mtop and over to the right edge on Metal4
c = box(cp, "vtune")
yv = c.bottom + 0.5
top.via(c.center().x, yv, "Metal3", "Metal4")
vt = top.rect("Metal4", c.center().x - 0.3, yv - 0.3, X_RIGHT, yv + 0.3)
top.pin("Metal4", "vtune", pya.DBox(vt.right - 1.0, vt.bottom, vt.right, vt.top))

# Outputs: the buffer's lines on down to the bottom edge
for name in ("rf_out_p", "rf_out_n"):
    b = box(bp, name)
    line = top.rect("Metal3", b.left, Y_BOTTOM, b.right, b.top)
    top.pin("Metal3", name, pya.DBox(line.left, line.bottom, line.right, line.bottom + 1.0))

# VSS: a Metal5 line above the bias from the core's spine and the bias to the trunk at the left edge, the buffer's rail
# over to the trunk, the trunk down to the bottom strap
spine = box(cp, "VSS")
xs = spine.center().x
vline = top.rect("Metal5", X_VSS - 1.0, Y_VSSL - 0.8, xs + 0.5, Y_VSSL + 0.8)
top.rect("Metal1", spine.left, spine.top - 0.1, spine.right, Y_VSSL + 0.4)  # the spine's top reaches the line
top.via(xs, Y_VSSL, "Metal1", "Metal5", cols=2, rows=2)
a = box(ap, "VSS")
top.rect("Metal1", a.left, a.center().y, a.right, Y_VSSL + 0.4)
top.via(a.center().x, Y_VSSL, "Metal1", "Metal5", cols=2, rows=2)
b = box(bp, "VSS")
top.via(b.left + 0.5, b.center().y, "Metal1", "Metal5", cols=2, rows=2)
top.rect("Metal5", X_VSS - 1.0, b.center().y - 0.5, b.left + 0.85, b.center().y + 0.5)
top.rect("Metal5", X_VSS - 1.0, Y_VSS_STRAP - 1.0, X_VSS + 1.0, Y_VSSL + 0.8)
vss = top.rect("Metal5", X_LEFT, Y_VSS_STRAP - 1.0, X_RIGHT, Y_VSS_STRAP + 1.0)
top.pin("Metal5", "VSS", pya.DBox(vss.left, vss.bottom, vss.left + 2.0, vss.top))

# VDD: a Metal4 trunk over the bias's VDD rail, Mtop's source rail and the buffer's rail join it, down to the strap
a = box(ap, "VDD")
xv = a.center().x
for y in (a.top - 1.0, a.top - 30.0, a.top - 60.0):
    top.via(xv, y, "Metal1", "Metal4", cols=2, rows=2)
c = box(cp, "VDD")
top.rect("Metal1", a.left, c.bottom, c.right, c.top)
top.via(xv, c.center().y, "Metal1", "Metal4", cols=2, rows=1)
b = box(bp, "VDD")
top.rect("Metal1", a.left, b.bottom, b.right, b.top)
top.via(xv, b.center().y, "Metal1", "Metal4", cols=2, rows=2)
top.rect("Metal4", a.left, Y_VDD_STRAP - 1.0, a.right, a.top - 0.5)
vdd = top.rect("Metal4", X_LEFT, Y_VDD_STRAP - 1.0, X_RIGHT, Y_VDD_STRAP + 1.0)
top.pin("Metal4", "VDD", pya.DBox(vdd.left, vdd.bottom, vdd.left + 2.0, vdd.top))

# PR boundary around the macro, its top edge is the coil's keep-out
ind_top = top.cell.dbbox().top
top.rect("prBoundary", X_LEFT, Y_BOTTOM, X_RIGHT, ind_top)

# Origin at the lower-left corner of the PR boundary, as in the template's other macros (LEF ORIGIN 0 0)
top.cell.transform(pya.Trans(pya.Vector(round(-X_LEFT / ly.dbu), round(-Y_BOTTOM / ly.dbu))))

vl.write(top, vl.out_path("vco_top", __file__), keep=("vco_core", "vco_buf", "vco_bias"))
# ==============================================================================
