# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the varactor array layout/vco_var.gds: three sg13_hv_svaricap in a column.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_var.py [-rd out=<file.gds>], or make klayout-script CELL=vco_var
#
# The three devices are stacked in y. Each one has its gate strip G1 at the bottom and G2 at the top, so G1 reaches the
# rf_p bus on the left and G2 the rf_n bus on the right over Metal2 stubs of equal length. The buses run on Metal3, 8 um
# left and right of the column's axis, where the core's tank lines come down. The well contacts W (the narrow bars on
# the left) join the vtune line on Metal3. A p+ tap closes the column on three sides for the substrate terminal.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

N, W, L, NX = 3, 3.74, 0.3, 8
PITCH = 8.35  # device pitch in y: 6.35 um of thick-oxide region and 2 um between two
XAXIS = 4.925  # x of the column's axis, the middle of a device's NWell
XBUS = 8.0  # distance of the rf_p and rf_n buses from the axis
BUS_W = 1.0  # width of the buses and of the Metal2 stubs
TAP_GAP, TAP_W = 1.0, 0.6  # distance of the tap from the thick-oxide region, tap width

ly = vl.new_layout()
top = vl.Block(ly, "vco_var")
g1s, g2s, ws, tg = [], [], [], []
for i in range(N):
    cell = top.pcell("SVaricap", model="sg13_hv_svaricap", w=vl.um(W), l=vl.um(L), Nx=NX)
    t = top.add(cell, 0, i * PITCH)
    tg.append(t * cell.dbbox())
    # The PCell's Metal1 pin shapes: the bottom strip is G1, the top strip G2, the narrow one the well contact W
    for p in pya.Region(cell.begin_shapes_rec(ly.layer(8, vl.PIN_DT))).merged().each():
        box = t * p.bbox().to_dtype(ly.dbu)
        if box.width() < 1.0:
            ws.append(box)
        elif box.center().y < i * PITCH + 1.0:
            g1s.append(box)
        else:
            g2s.append(box)
if not (len(g1s) == len(g2s) == len(ws) == N):
    raise RuntimeError(f"vco_var.py: expected {N} G1, G2 and W strips, found {len(g1s)}, {len(g2s)}, {len(ws)}")

# Gate strips: a via row on each strip, a Metal2 stub out to the bus, the bus on Metal3
xl, xr = XAXIS - XBUS, XAXIS + XBUS
for strips, name, xb in ((g1s, "rf_p", xl), (g2s, "rf_n", xr)):
    for s in strips:
        yc = s.center().y
        cols = int((s.width() - 0.2) / 0.41)
        top.via(s.center().x, yc, "Metal1", "Metal2", cols=cols, rows=1)
        top.rect("Metal2", min(s.left, xb - BUS_W / 2), yc - BUS_W / 2, max(s.right, xb + BUS_W / 2), yc + BUS_W / 2)
        top.via(xb, yc, "Metal2", "Metal3", cols=2, rows=2)
    ys = [s.center().y for s in strips]
    bus = top.rect("Metal3", xb - BUS_W / 2, min(ys) - BUS_W / 2, xb + BUS_W / 2, max(ys) + BUS_W / 2)
    top.pin("Metal3", name, bus)

# Well contacts to the vtune line on Metal3
xw = ws[0].center().x
for w in ws:
    top.via(xw, w.center().y, "Metal1", "Metal3", cols=1, rows=2)
vt = top.rect("Metal3", xw - 0.25, ws[0].center().y - 0.5, xw + 0.25, ws[-1].center().y + 0.5)
top.pin("Metal3", "vtune", vt)

# Substrate tap on three sides of the column: a strip below it and one up each side
x0, x1 = min(b.left for b in tg), max(b.right for b in tg)
y0, y1 = min(b.bottom for b in tg), max(b.top for b in tg)
xa, xb_ = x0 - TAP_GAP - TAP_W, x1 + TAP_GAP + TAP_W
ya = y0 - TAP_GAP - TAP_W
# Three separate taps, so their contact grids cannot collide at the corners, joined on Metal1
yu = ya + TAP_W + 0.3
for bx0, by0, bx1, by1 in ((xa, ya, xb_, ya + TAP_W), (xa, yu, xa + TAP_W, y1), (xb_ - TAP_W, yu, xb_, y1)):
    tap = top.pcell("ptap1", w=vl.um(bx1 - bx0), l=vl.um(by1 - by0))
    top.add(tap, bx0, by0)
for bx0, bx1 in ((xa, xa + TAP_W), (xb_ - TAP_W, xb_)):
    top.rect("Metal1", bx0, ya, bx1, y1)
top.rect("Metal1", xa, ya, xb_, ya + TAP_W)
top.pin("Metal1", "VSS", pya.DBox(xa, ya, xb_, ya + TAP_W))

vl.write(top, vl.out_path("vco_var", __file__), drop_texts=("G1", "G2", "W"))
# ==============================================================================
