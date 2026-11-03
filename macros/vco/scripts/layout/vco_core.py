# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the VCO core layout/vco_core.gds: coil, pair, varactors, Cct1 and Cct2.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_core.py [-rd out=<file.gds>], or make klayout-script CELL=vco_core
# Needs layout/vco_ind.gds and layout/vco_var.gds, which stay subcells so LVS compares the hierarchy of the schematic.
#
# A column under the coil's feeds (the coil cell's origin, feed ends at y = -1), symmetric about x = 0 where the circuit
# is: the feeds LA and LB drop to Metal3 lines at x = -8 and 8, which run down the whole column as rf_p and rf_n. The pair
# sits right below the feeds with its cross-coupling on Metal2 (rf_n) and Metal4 (rf_p), the varactor array below it with
# its buses on the same lines. The center tap LC goes to vdd_core on a TopMetal1 spine, which turns right into the top
# plate of Cct1. Cct1 fills the space right of the column, Cct2 the space right of the buffer below it. Their Metal5 bottom
# plates are VSS, joined to a Metal1 spine at x = -12 that collects the coil's, the pair's and the array's taps.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

XF = 8.0  # x of the feeds LA (-XF) and LB (XF), the rf_p and rf_n lines
Y_FV = -6.0  # y of the feed via stacks down to Metal3
Y_PAIR = -11.0  # top of the pair's active areas
GAP = 5.0  # half the gap between the pair's active areas
Y_XN, Y_XP = -9.0, -8.0  # cross-coupling lines: rf_n on Metal2, rf_p on Metal4
Y_SP = -11.0  # y of the vdd_core bar from the spine into Cct1, 3 um wide on TopMetal1
Y_VAR = -16.0  # top edge of the varactor array cell
Y_BOT = -44.0  # bottom edge of the column, where rf_p, rf_n and vtune leave for the buffer
Y_VT = -42.0  # y of vtune's Metal4 jog from the array's line onto the axis
XS = -12.0  # x of the VSS spine
Y_VSS = -43.0  # y of the Metal5 VSS strap from the spine to Cct1's bottom plate
CCT1 = (14.0, -43.0, 56.0, 39.0)  # Cct1 MIM: x, y of the lower-left corner, w, l
CCT2 = (28.0, -72.5, 42.0, 25.5)  # Cct2 MIM, right of the buffer
Y_CELL_BOT = -75.0  # bottom edge of the cell, where vdd_core and VSS leave

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

# rf_p and rf_n: Metal3 lines from the feed via stacks down the whole column
for name, x in (("rf_p", -XF), ("rf_n", XF)):
    line = top.rect("Metal3", x - 0.5, Y_BOT, x + 0.5, Y_FV + 0.5)
    top.pin("Metal3", name, pya.DBox(line.left, line.bottom, line.right, line.bottom + 1.0))

# Cross-coupled pair, gates on top: M1 (drain rf_p) left, M2 (drain rf_n) its image in x
pair = vl.mos(ly, "Mpair", "nmos", 20.0, 0.13, 10, tap="merge")
paw = pair.ports["ACT"][1].width()
m1 = top.place(pair, -GAP - paw, Y_PAIR, mirror=True)
m2 = top.place(pair, GAP + paw, Y_PAIR, rot=180)
for x, p in ((-XF, m1), (XF, m2)):
    top.via(x, p["D"][1].center().y, "Metal2", "Metal3", cols=2, rows=3)
# M1's gate is rf_n: up to a Metal2 line over to the rf_n line
g1 = m1["G"][1]
x1 = g1.right - 0.4
top.via(x1, g1.center().y, "Metal1", "Metal2")
top.rect("Metal2", x1 - 0.2, g1.center().y, x1 + 0.2, Y_XN + 0.2)
top.rect("Metal2", x1 - 0.2, Y_XN - 0.2, XF + 0.3, Y_XN + 0.2)
top.via(XF, Y_XN, "Metal2", "Metal3")
# M2's gate is rf_p: up on Metal4 to a line over to the rf_p line
g2 = m2["G"][1]
x2 = g2.left + 0.4
top.via(x2, g2.center().y, "Metal1", "Metal4")
top.rect("Metal4", x2 - 0.2, g2.center().y, x2 + 0.2, Y_XP + 0.2)
top.rect("Metal4", -XF - 0.3, Y_XP - 0.2, x2 + 0.2, Y_XP + 0.2)
top.via(-XF, Y_XP, "Metal3", "Metal4")

# Varactor array, its axis on x = 0, so its rf_p and rf_n buses lie on the column's lines
var = vl.read_cell(ly, "vco_var", __file__)
vb = var.dbbox()
tv = top.add(var, -4.925, Y_VAR - vb.top)
vpins = vl.cell_pins(ly, var, tv)

# vtune: the array's line down, a Metal4 jog onto the axis, down to the bottom edge
vt = vpins["vtune"][1]
xv = vt.center().x
top.rect("Metal3", vt.left, Y_VT - 0.5, vt.right, vt.bottom + 0.5)
top.via(xv, Y_VT, "Metal3", "Metal4", cols=1, rows=2)
top.rect("Metal4", xv - 0.3, Y_VT - 0.3, 0.3, Y_VT + 0.3)
vline = top.rect("Metal4", -0.3, Y_BOT, 0.3, Y_VT + 0.3)
top.pin("Metal4", "vtune", pya.DBox(vline.left, vline.bottom, vline.right, vline.bottom + 1.0))

# Cct1 and Cct2: TopMetal1 top plates on vdd_core, Metal5 bottom plates on VSS
plates = []
for x0, y0, w, l in (CCT1, CCT2):
    cell = top.pcell("cmim", Calculate="C", w=vl.um(w), l=vl.um(l))
    tc = top.add(cell, x0, y0)
    plates.append((top.shapes(cell, tc, "Metal5")[0], top.shapes(cell, tc, "TopMetal1")[0]))
(m5a, tma), (m5b, tmb) = plates
# The plates of the two caps joined at the right edge, the top plates over a TopMetal1 tab inside both MIM areas
top.rect("Metal5", m5b.right - 2.0, m5b.top - 0.1, m5b.right, m5a.bottom + 0.1)
top.rect("TopMetal1", tmb.right - 8.0, tmb.top - 0.1, tmb.right - 1.0, tma.bottom + 0.1)

# vdd_core: the center tap's TopMetal1 spine down to a bar into Cct1's top plate, and a pin under Cct2
top.rect("TopMetal1", -2.0, Y_SP - 1.5, 2.0, -2.5)
top.rect("TopMetal1", -2.0, Y_SP - 1.5, tma.left + 0.5, Y_SP + 1.5)
xp = tmb.right - 6.0
vdc = top.rect("TopMetal1", xp - 2.0, Y_CELL_BOT, xp + 2.0, tmb.bottom + 0.1)
top.pin("TopMetal1", "vdd_core", pya.DBox(vdc.left, vdc.bottom, vdc.right, vdc.bottom + 1.0))

# VSS: the coil's tap over to a Metal1 spine, the pair's and the array's taps onto it, a Metal5 strap from its foot into
# Cct1's bottom plate. The cell's VSS pin sits on Cct2's bottom plate, which reaches the bottom edge.
tap = ipins["VSS"][1]
spine = top.rect("Metal1", XS - 0.5, Y_VSS - 0.5, XS + 0.5, tap.top)
top.rect("Metal1", tap.left, tap.bottom, XS + 0.5, tap.top)
s1, s2 = m1["S"][1], m2["S"][1]
sbar = top.rect("Metal1", XS - 0.5, s1.bottom, s2.right, s1.top)
# The pair's sources carry the whole core current, and its 2 f0 pulses: via stacks all along the source bar, clear of the
# rf lines, up to a Metal5 bar that runs straight into Cct1's bottom plate, the cell's widest VSS conductor
for x in (-11.5, -6.0, -3.0, 0.0, 3.0, 6.0, 10.0):
    top.via(x, sbar.center().y, "Metal1", "Metal5", cols=2, rows=2)
top.rect("Metal5", XS - 0.5, sbar.bottom, CCT1[0], sbar.top)
vss_var = vpins["VSS"][1]
top.rect("Metal1", XS - 0.5, vss_var.bottom, vss_var.left + 0.1, vss_var.top)
top.rect("Metal5", XS - 0.5, Y_VSS - 0.5, m5a.left + 0.1, Y_VSS + 0.5)
top.via(XS, Y_VSS, "Metal1", "Metal5", cols=2, rows=2)
vss = top.rect("Metal5", m5b.left, Y_CELL_BOT, m5b.left + 4.0, m5b.bottom + 0.1)
top.pin("Metal5", "VSS", pya.DBox(vss.left, vss.bottom, vss.right, vss.bottom + 1.0))

vl.write(top, vl.out_path("vco_core", __file__), keep=("vco_ind", "vco_var"))
# ==============================================================================
