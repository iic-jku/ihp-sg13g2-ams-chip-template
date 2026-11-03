# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the macro layout/vco_top.gds from the bias, core and buffer cells.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_top.py [-rd out=<file.gds>], or make klayout-script CELL=vco_top
# Needs layout/vco_bias.gds, vco_core.gds and vco_buf.gds. They stay subcells, as in the schematic.
#
# Built around the core's origin (the coil above, its column below), then moved so the PR boundary starts at (0, 0).
# The macro is as wide as the coil's keep-out. Below it, the core's column sits on the axis with Cct1 and Cct2 to its
# right, the buffer is centered under the column, and the bias fills the left side. Power runs on two straps along the
# bottom edge, VSS on Metal5 and VDD on Metal4 below it. di_en and ibias_100u leave at the left edge, everything else at
# the bottom edge. Nothing closes a loop around the coil.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

X_LEFT, X_RIGHT = -71.5, 71.5  # macro edges, the coil's keep-out is 142.04 um wide
XB, YB = -65.7, -4.5  # origin of the bias cell, its left edge ends up at -71
YBUF = -68.6  # origin of the buffer cell, its top edge ends up at -45
X_BB = -25.5  # x of the Metal4 risers from the bias outputs to the buffer's bias pins
Y_VSS = (-77.0, -75.0)  # VSS strap on Metal5
Y_VDD = (-79.5, -77.5)  # VDD strap on Metal4, its bottom is the macro's bottom edge
Y_BOTTOM = Y_VDD[0]
X_BVSS, X_BVDD = -67.5, -70.4  # x of the bias's VSS (Metal5) and VDD (Metal4) risers down to the straps

ly = vl.new_layout()
top = vl.Block(ly, "vco_top")

core = vl.read_cell(ly, "vco_core", __file__)
cp = vl.cell_pins(ly, core, top.add(core, 0, 0))
buf = vl.read_cell(ly, "vco_buf", __file__)
bp = vl.cell_pins(ly, buf, top.add(buf, 0, YBUF))
bias = vl.read_cell(ly, "vco_bias", __file__)
ap = vl.cell_pins(ly, bias, top.add(bias, XB, YB))


def box(pins, name):
    return pins[name][1]


# rf_p, rf_n: the core's Metal3 lines down onto the buffer's input tabs on Metal5
for name in ("rf_p", "rf_n"):
    c, b = box(cp, name), box(bp, name)
    x, y = c.center().x, b.center().y
    top.rect("Metal3", c.left, y - 0.5, c.right, c.bottom + 0.1)
    top.via(x, y, "Metal3", "Metal5", cols=2, rows=2)

# vbn_buf, vbg_buf: the bias tracks on to a Metal4 riser each, which lands on the buffer's pin
for name in ("vbn_buf", "vbg_buf"):
    a, b = box(ap, name), box(bp, name)
    ya, yb = a.center().y, b.center().y
    top.rect("Metal3", a.right - 0.1, ya - 0.2, X_BB + 0.3, ya + 0.2)
    top.via(X_BB, ya, "Metal3", "Metal4")
    top.rect("Metal4", X_BB - 0.2, min(ya, yb) - 0.2, X_BB + 0.2, max(ya, yb) + 0.2)
    top.via(X_BB, yb, "Metal3", "Metal4")
    top.rect("Metal3", b.left - 0.1, yb - 0.2, X_BB + 0.3, yb + 0.2)

# Inputs: the bias tracks on to the left edge
for name in ("di_en", "ibias_100u"):
    a = box(ap, name)
    line = top.rect("Metal3", X_LEFT, a.bottom, a.left + 0.1, a.top)
    top.pin("Metal3", name, pya.DBox(X_LEFT, line.bottom, X_LEFT + 1.0, line.top))

# vtune: the core's line down the axis through the buffer on Metal4, onto Metal3 above the VDD strap, to the bottom edge
c = box(cp, "vtune")
yv = Y_VSS[0] + 0.5
top.rect("Metal4", c.left, yv - 0.3, c.right, c.bottom + 0.1)
top.via(c.center().x, yv, "Metal3", "Metal4", cols=1, rows=2)
vt = top.rect("Metal3", c.left, Y_BOTTOM, c.right, yv + 0.3)
top.pin("Metal3", "vtune", pya.DBox(vt.left, vt.bottom, vt.right, vt.bottom + 1.0))

# Outputs: the buffer's lines on down to the bottom edge
for name in ("rf_out_p", "rf_out_n"):
    b = box(bp, name)
    line = top.rect("Metal3", b.left, Y_BOTTOM, b.right, b.bottom + 0.1)
    top.pin("Metal3", name, pya.DBox(line.left, line.bottom, line.right, line.bottom + 1.0))

# vdd_core: the core's TopMetal1 tab on down to the bottom edge
c = box(cp, "vdd_core")
line = top.rect("TopMetal1", c.left, Y_BOTTOM, c.right, c.bottom + 0.1)
top.pin("TopMetal1", "vdd_core", pya.DBox(line.left, line.bottom, line.right, line.bottom + 1.0))

# VSS strap: the core's pin on Cct2's bottom plate reaches it, the buffer's rail drops onto it through via stacks
# between the outputs and vtune, the bias's rail on a Metal5 riser at the left edge
vss = top.rect("Metal5", X_LEFT, Y_VSS[0], X_RIGHT, Y_VSS[1])
top.pin("Metal5", "VSS", pya.DBox(X_LEFT, vss.bottom, X_LEFT + 2.0, vss.top))
c = box(cp, "VSS")
top.rect("Metal5", c.left, Y_VSS[1] - 0.1, c.right, c.bottom + 0.1)
b = box(bp, "VSS")
for x in (-6.0, 6.0):
    top.via(x, b.center().y, "Metal1", "Metal5", cols=2, rows=2)
a = box(ap, "VSS")
top.rect("Metal1", X_BVSS - 0.6, a.bottom, a.left + 0.1, a.top)
top.via(X_BVSS, a.center().y, "Metal1", "Metal5", cols=2, rows=2)
top.rect("Metal5", X_BVSS - 0.5, Y_VSS[1] - 0.1, X_BVSS + 0.5, a.center().y)

# VDD strap: the buffer's rail and the bias's rail drop onto it on Metal4 risers
vdd = top.rect("Metal4", X_LEFT, Y_VDD[0], X_RIGHT, Y_VDD[1])
top.pin("Metal4", "VDD", pya.DBox(X_LEFT, vdd.bottom, X_LEFT + 2.0, vdd.top))
for pins, xr in ((bp, box(bp, "VDD").left + 0.5), (ap, X_BVDD)):
    p = box(pins, "VDD")
    top.rect("Metal1", min(xr - 0.6, p.left), p.bottom, max(xr + 0.6, p.left + 0.1), p.top)
    top.via(xr, p.center().y, "Metal1", "Metal4", cols=2, rows=1)
    top.rect("Metal4", xr - 0.5, Y_VDD[1] - 0.1, xr + 0.5, p.center().y)

# PR boundary around the macro, its top edge is the coil's keep-out
ind_top = top.cell.dbbox().top
top.rect("prBoundary", X_LEFT, Y_BOTTOM, X_RIGHT, ind_top)

# Origin at the lower-left corner of the PR boundary, as in the template's other macros (LEF ORIGIN 0 0)
top.cell.transform(pya.Trans(pya.Vector(round(-X_LEFT / ly.dbu), round(-Y_BOTTOM / ly.dbu))))

vl.write(top, vl.out_path("vco_top", __file__), keep=("vco_core", "vco_buf", "vco_bias"))
# ==============================================================================
