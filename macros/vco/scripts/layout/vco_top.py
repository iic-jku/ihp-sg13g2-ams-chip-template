# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the macro layout/vco_top.gds from the bias, core and buffer cells.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_top.py [-rd out=<file.gds>], or make klayout-script CELL=vco_top
# Needs layout/vco_bias.gds, vco_core.gds, vco_buf.gds and vco_feed.gds. They stay subcells, as in the schematic.
#
# Built around the core's origin (the coil above, its column below), then moved so the PR boundary starts at (0, 0).
# The macro is as wide as the coil's keep-out. Below it, the core's column sits on the axis with Cct1 and Cct2 to its
# right, the buffer is centered under the column, the bias fills the left side, and the tap feed sits under the core's
# Cct1 and Cct2 on the bottom edge. Power runs on two straps along the bottom edge, VDD on TopMetal1 and VSS on Metal5
# under a TopMetal2 strap above it. di_en leaves at the left edge, everything else at the bottom edge. Nothing closes a
# loop around the coil.

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
Y_VSS2 = (-79.0, -74.2)  # VSS strap on TopMetal2 over it
Y_VDD = (-79.5, -77.86)  # VDD strap on TopMetal1, its bottom is the macro's bottom edge
Y_VIA2 = -75.2  # y of the via stacks from Metal5 to TopMetal2, their TopMetal1 1.64 um above the VDD strap
Y_VC = -74.05  # y of the tap's via stack from Metal3 to TopMetal1, in the Metal5 gap between the strap and Cct's plate
X_FEED = 31.2  # left edge of the tap feed, Rct under the tap
Y_BOTTOM = Y_VDD[0]
X_BVSS, X_BVDD = -67.5, -70.4  # x of the bias's VSS (Metal5) and VDD (Metal4) risers down to the straps
X_ENB, Y_ENB = -26.5, -76.7  # en_b: Metal4 from the bias down beside the buffer, Metal2 under it to the tap feed

ly = vl.new_layout()
top = vl.Block(ly, "vco_top")

core = vl.read_cell(ly, "vco_core", __file__)
cp = vl.cell_pins(ly, core, top.add(core, 0, 0))
buf = vl.read_cell(ly, "vco_buf", __file__)
bp = vl.cell_pins(ly, buf, top.add(buf, 0, YBUF))
bias = vl.read_cell(ly, "vco_bias", __file__)
ap = vl.cell_pins(ly, bias, top.add(bias, XB, YB))
feed = vl.read_cell(ly, "vco_feed", __file__)
fp = vl.cell_pins(ly, feed, top.add(feed, X_FEED, Y_BOTTOM))


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

# di_en: the bias track on to the left edge
a = box(ap, "di_en")
line = top.rect("Metal3", X_LEFT, a.bottom, a.left + 0.1, a.top)
top.pin("Metal3", "di_en", pya.DBox(X_LEFT, line.bottom, X_LEFT + 1.0, line.top))

# en_b: the bias output to the tap feed's gate, away from the RF lines except for crossing the outputs and vtune
a, f = box(ap, "en_b"), box(fp, "en_b")
ya, xf = a.center().y, f.center().x
top.rect("Metal3", a.right - 0.1, a.bottom, X_ENB + 0.3, a.top)
top.via(X_ENB, ya, "Metal3", "Metal4", cols=1, rows=2)
top.rect("Metal4", X_ENB - 0.15, Y_ENB - 0.2, X_ENB + 0.15, ya + 0.3)
top.via(X_ENB, Y_ENB, "Metal2", "Metal4", cols=2, rows=1)
top.rect("Metal2", X_ENB - 0.3, Y_ENB - 0.15, xf + 0.15, Y_ENB + 0.15)
top.rect("Metal2", xf - 0.15, min(Y_ENB, f.center().y) - 0.15, xf + 0.15, max(Y_ENB, f.center().y) + 0.15)

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

# The tap: the core's TopMetal1 tab down to a via stack onto Metal3, which reaches the tap feed's bottom head
c, f = box(cp, "vdd_core"), box(fp, "vdd_core")
xc = c.center().x
top.rect("TopMetal1", xc - 4.0, Y_VC - 0.85, xc + 4.0, Y_VC + 1.8)  # into Cct2's top plate
top.via(xc, Y_VC, "Metal3", "TopMetal1", cols=16, rows=2, tcols=8, trows=1)
top.rect("Metal3", max(xc - 4.0, f.left), f.bottom, min(xc + 4.0, f.right), Y_VC + 0.5)

# VSS strap: the core's pin on Cct2's bottom plate reaches it, the buffer's rail drops onto it through via stacks
# between the outputs and vtune, the bias's rail on a Metal5 riser at the left edge, the tap feed's substrate tap through
# a via stack. Metal5 is a thin metal here: alone, the 2 um strap put 4.4 Ohm between the core and the pin at the left
# edge. The TopMetal2 strap over it carries the current, joined to it through via stacks clear of the tap's TopMetal1.
vss = top.rect("Metal5", X_LEFT, Y_VSS[0], X_RIGHT, Y_VSS[1])
vss2 = top.rect("TopMetal2", X_LEFT, Y_VSS2[0], X_RIGHT, Y_VSS2[1])
top.pin("TopMetal2", "VSS", pya.DBox(X_LEFT, vss2.bottom, X_LEFT + 2.0, vss2.top))
c = box(cp, "VSS")
top.rect("Metal5", c.left, Y_VSS[1] - 0.1, c.right + 4.0, Y_VC + 1.0)  # 8 um into Cct2's bottom plate, for the core current
for x in range(int(X_LEFT) + 3, int(X_RIGHT) - 2, 6):
    if xc - 7.6 < x < xc + 7.6:
        continue
    top.via(x, Y_VIA2, "Metal5", "TopMetal2", tcols=2, trows=1)
b = box(bp, "VSS")
for x in (-8.5, -3.0, 3.0, 8.5):
    top.via(x, b.center().y, "Metal1", "Metal5", cols=6, rows=2)
t = box(fp, "VSS")
top.via(t.center().x, (Y_VSS[0] + Y_VSS[1]) / 2, "Metal1", "Metal5", cols=1, rows=2)
a = box(ap, "VSS")
top.rect("Metal1", X_BVSS - 0.6, a.bottom, a.left + 0.1, a.top)
top.via(X_BVSS, a.center().y, "Metal1", "Metal5", cols=2, rows=2)
top.rect("Metal5", X_BVSS - 0.5, Y_VSS[1] - 0.1, X_BVSS + 0.5, a.center().y)

# VDD strap: the tap feed's source rail through a via stack straight up, the bias's rail on a Metal4 riser, each of the
# buffer's loads on a Metal4 riser of its own, since the buffer's 0.8 um rail is for the pin only
ym = (Y_VDD[0] + Y_VDD[1]) / 2
p = box(fp, "VDD")
vdd = top.rect("TopMetal1", X_LEFT, Y_VDD[0], p.right, Y_VDD[1])
top.pin("TopMetal1", "VDD", pya.DBox(X_LEFT, vdd.bottom, X_LEFT + 2.0, vdd.top))
top.via(p.center().x, ym, "Metal2", "TopMetal1", cols=40, rows=2, tcols=10, trows=1)
p = box(ap, "VDD")
top.rect("Metal1", X_BVDD - 0.6, p.bottom, p.left + 0.1, p.top)
top.via(X_BVDD, p.center().y, "Metal1", "Metal4", cols=2, rows=1)
top.rect("Metal4", X_BVDD - 0.5, ym - 0.5, X_BVDD + 0.5, p.center().y)
top.via(X_BVDD, ym, "Metal4", "TopMetal1", tcols=2, trows=1)
yl = box(bp, "VDD").center().y - 0.6
for xr in (-16.0, 16.0):
    top.via(xr, yl, "Metal1", "Metal4", cols=12, rows=2)
    top.rect("Metal4", xr - 2.5, ym - 0.7, xr + 2.5, yl + 0.35)
    top.via(xr, ym, "Metal4", "TopMetal1", tcols=6, trows=1)
vl.check_wire("VDD strap", "TopMetal1", vdd.height(), vl.I_CORE + vl.I_TAIL + vl.I_BIAS)
vl.check_cuts("VDD to the tap feed", "TopVia1", 10, vl.I_CORE)
vl.check_wire("VDD riser of a load", "Metal4", 5.0, vl.I_TAIL / 2)
vl.check_cuts("VDD riser of a load, top", "TopVia1", 6, vl.I_TAIL / 2)
vl.check_cuts("VDD riser of a load, bottom", "Via1", 24, vl.I_TAIL / 2)
vl.check_cuts("VSS of the buffer", "Via1", 4 * 12, vl.I_TAIL)

# PR boundary around the macro, its top edge is the coil's keep-out
ind_top = top.cell.dbbox().top
top.rect("prBoundary", X_LEFT, Y_BOTTOM, X_RIGHT, ind_top)

# Origin at the lower-left corner of the PR boundary, as in the template's other macros (LEF ORIGIN 0 0)
top.cell.transform(pya.Trans(pya.Vector(round(-X_LEFT / ly.dbu), round(-Y_BOTTOM / ly.dbu))))

vl.check_cuts("tap to Rct", "Via3", 32, vl.I_CORE)
vl.check_cuts("tap to Rct, top", "TopVia1", 8, vl.I_CORE)
vl.check_wire("VSS from the core", "Metal5", c.width() + 4.0, vl.I_CORE)

vl.write(top, vl.out_path("vco_top", __file__), keep=("vco_core", "vco_buf", "vco_bias", "vco_feed"))
# ==============================================================================
