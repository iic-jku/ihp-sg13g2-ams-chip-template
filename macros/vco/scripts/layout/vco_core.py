# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the VCO core layout/vco_core.gds: coil, pair, varactors, Cct and Mtop.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_core.py [-rd out=<file.gds>], or make klayout-script CELL=vco_core
# Needs layout/vco_ind.gds and layout/vco_var.gds, which stay subcells so LVS compares the hierarchy of the schematic.
#
# A vertical chain under the coil's feeds (the coil cell's origin, feed ends at y = -1), symmetric about x = 0 where the
# circuit is: the feeds LA and LB drop to Metal3 at x = -8 and 8, the center tap LC goes to a TopMetal1 spine (vct) down
# the middle, the pair sits right below the feeds with its cross-coupling on Metal2 (rf_n) and Metal4 (rf_p), then the
# varactor array (turned so rf_p is on its left, rf_n on its right), Cct under the spine and Mtop at the bottom.
# rf_p and rf_n leave on Metal5 at x = -18 and 18 for the buffer. A Metal1 spine at x = -13 collects VSS.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

XF = 8.0  # x of the feeds LA (-XF) and LB (XF), the rf_p and rf_n nodes
Y_FV = -6.0  # y of the feed via stacks down to Metal3
Y_PAIR = -11.0  # top of the pair's active areas
GAP = 5.0  # half the gap between the pair's active areas
Y_XN, Y_XP = -9.0, -8.0  # cross-coupling lines: rf_n on Metal2, rf_p on Metal4
Y_VAR = -17.5  # top edge of the varactor array
Y_VR = -19.0  # y of the Metal3 taps onto the varactor buses
XM5 = 18.0  # x of the rf_p (-XM5) and rf_n (XM5) Metal5 lines
Y_M5 = -16.0  # y where rf_p and rf_n go up to Metal5
XS = -13.0  # x of the VSS spine
CCT, Y_CCT = 25.0, -57.0  # side and top edge of Cct
Y_MTOP = -87.0  # top of Mtop's active area
Y_BOT = -96.0  # bottom edge of the cell

ly = vl.new_layout()
top = vl.Block(ly, "vco_core")

# Coil, and its feeds extended below its keep-out
ind = vl.read_cell(ly, "vco_ind", __file__)
ti = top.add(ind, 0, 0)
ipins = vl.cell_pins(ly, ind, ti)
for x in (-XF, XF):
    top.rect("TopMetal1", x - 2.0, Y_FV - 1.5, x + 2.0, -0.5)
    top.via(x, Y_FV, "Metal3", "TopMetal1", cols=4, rows=4, tcols=3, trows=3)
top.rect("TopMetal2", -2.0, -5.5, 2.0, -0.5)
top.via(0, -4.0, "TopMetal1", "TopMetal2", tcols=2, trows=2)

# Cross-coupled pair, gates on top: M1 (drain rf_p) left, M2 (drain rf_n) its image in x
pair = vl.mos(ly, "Mpair", "nmos", 20.0, 0.13, 10, tap="merge")
paw = pair.ports["ACT"][1].width()
m1 = top.place(pair, -GAP - paw, Y_PAIR, mirror=True)
m2 = top.place(pair, GAP + paw, Y_PAIR, rot=180)
for x, p in ((-XF, m1), (XF, m2)):
    d = p["D"][1]
    top.rect("Metal3", x - 0.5, Y_VR - 0.3, x + 0.5, Y_FV + 0.5)
    top.via(x, d.center().y, "Metal2", "Metal3", cols=2, rows=3)
# M1's gate is rf_n: up to a Metal2 line over to the rf_n node
g1 = m1["G"][1]
x1 = g1.right - 0.4
top.via(x1, g1.center().y, "Metal1", "Metal2")
top.rect("Metal2", x1 - 0.2, g1.center().y, x1 + 0.2, Y_XN + 0.2)
top.rect("Metal2", x1 - 0.2, Y_XN - 0.2, XF + 0.3, Y_XN + 0.2)
top.via(XF, Y_XN, "Metal2", "Metal3")
# M2's gate is rf_p: up on Metal4 to a line over to the rf_p node
g2 = m2["G"][1]
x2 = g2.left + 0.4
top.via(x2, g2.center().y, "Metal1", "Metal4")
top.rect("Metal4", x2 - 0.2, g2.center().y, x2 + 0.2, Y_XP + 0.2)
top.rect("Metal4", -XF - 0.3, Y_XP - 0.2, x2 + 0.2, Y_XP + 0.2)
top.via(-XF, Y_XP, "Metal3", "Metal4")

# Varactor array, turned by 270 degrees: its rf_p bus ends up on the left, rf_n on the right, vtune in the middle
var = vl.read_cell(ly, "vco_var", __file__)
vb = var.dbbox()
tv = top.add(var, -(vb.bottom + vb.top) / 2, Y_VAR + vb.left, rot=270)
vpins = vl.cell_pins(ly, var, tv)
for name, x in (("rf_p", -XF), ("rf_n", XF)):
    bus = vpins[name][1]
    xb = bus.center().x
    top.rect("Metal3", min(x, xb) - 0.3, Y_VR - 0.3, max(x, xb) + 0.3, Y_VR + 0.3)
    top.via(xb, Y_VR, "Metal2", "Metal3", cols=2, rows=1)

# rf_p and rf_n up to Metal5 and down the sides to the bottom edge
for name, x in (("rf_p", -XF), ("rf_n", XF)):
    xm = XM5 if x > 0 else -XM5
    top.via(x, Y_M5, "Metal3", "Metal5", cols=2, rows=2)
    top.rect("Metal5", min(x, xm) - 0.5, Y_M5 - 0.5, max(x, xm) + 0.5, Y_M5 + 0.5)
    line = top.rect("Metal5", xm - 0.5, Y_BOT, xm + 0.5, Y_M5 + 0.5)
    top.pin("Metal5", name, pya.DBox(line.left, line.bottom, line.right, line.bottom + 1.0))

# vtune: the array's Metal3 line on down to the bottom edge
vt = vpins["vtune"][1]
vline = top.rect("Metal3", vt.left, Y_BOT, vt.right, vt.bottom + 0.5)
top.pin("Metal3", "vtune", pya.DBox(vline.left, vline.bottom, vline.right, vline.bottom + 1.0))

# Cct under the spine: its TopMetal1 top plate is vct, its Metal5 bottom plate VSS
cct = top.pcell("cmim", Calculate="C", w=vl.um(CCT), l=vl.um(CCT))
tc = top.add(cct, -CCT / 2, Y_CCT - CCT)
cm5 = top.shapes(cct, tc, "Metal5")[0]
ctm1 = top.shapes(cct, tc, "TopMetal1")[0]
top.rect("TopMetal1", -2.0, ctm1.top - 0.5, 2.0, -5.0)

# Mtop below Cct, its drain lifted to a TopMetal1 bar that joins the spine
mtop = vl.mos(ly, "Mtop", "pmos", 150.0, 0.5, 30, tap="merge")
taw = mtop.ports["ACT"][1].width()
pm = top.place(mtop, -taw / 2, Y_MTOP - mtop.ports["ACT"][1].height())
dm = pm["D"][1]
bar = top.rect("TopMetal1", -10.5, dm.center().y - 1.1, 10.5, dm.center().y + 1.1)
top.rect("TopMetal1", -2.0, bar.bottom, 2.0, ctm1.bottom + 0.5)
for x in (-9.0, -4.0, 4.0, 9.0):
    top.via(x, dm.center().y, "Metal2", "TopMetal1", cols=1, rows=3, tcols=2, trows=2)
gm = pm["G"][1]
top.via(gm.left + 0.4, gm.center().y, "Metal1", "Metal3")
vbp = top.rect("Metal3", -XM5 - 4.0, gm.center().y - 0.3, gm.left + 0.7, gm.center().y + 0.3)
top.pin("Metal3", "vbp_core", pya.DBox(vbp.left, vbp.bottom, vbp.left + 1.0, vbp.top))
sm = pm["S"][1]
top.pin("Metal1", "VDD", pya.DBox(sm.left, sm.bottom, sm.left + 2.0, sm.top))

# VSS spine on Metal1: the coil's tap, the pair's taps, the varactor array's tap and Cct's bottom plate
spine = top.rect("Metal1", XS - 0.5, cm5.bottom, XS + 0.5, -2.5)
tap = ipins["VSS"][1]
top.rect("Metal1", tap.left, tap.bottom, XS + 0.5, tap.top)
for p in (m1, m2):
    s = p["S"][1]
    top.rect("Metal1", XS - 0.5, s.bottom, s.right, s.top)
vss_var = vpins["VSS"][1]
for y in (vss_var.bottom + 2.0, vss_var.center().y, vss_var.top - 2.0):
    top.rect("Metal1", XS - 0.5, y - 0.4, vss_var.right, y + 0.4)
tab = top.rect("Metal5", XS - 1.0, cm5.bottom + 2.0, cm5.left + 0.1, cm5.bottom + 6.0)
for y in (tab.bottom + 1.0, tab.top - 1.0):
    top.via(XS, y, "Metal1", "Metal5", cols=2, rows=2)
top.pin("Metal1", "VSS", pya.DBox(spine.left, spine.bottom, spine.right, spine.bottom + 1.0))

vl.write(top, vl.out_path("vco_core", __file__), keep=("vco_ind", "vco_var"))
# ==============================================================================
