# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the varactor array layout/vco_var.gds: three sg13_hv_svaricap side by side.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_var.py [-rd out=<file.gds>], or make klayout-script CELL=vco_var
# The PCell's gate combs end in a Metal1 strip at its bottom (G1) and top (G2), and its well contact (W) sits on the left.
# A Metal2 bus over the bottom strips is rf_p, one over the top strips rf_n, a Metal3 line over the well contacts vtune.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

N, W, L, NX = 3, 3.74, 0.3, 8
PITCH = 12.0  # device pitch in x, leaves about 2 um between the thick-oxide regions
BUS_W = 1.0  # width of the rf_p and rf_n Metal2 buses

ly = vl.new_layout()
top = vl.Block(ly, "vco_var")
g1s, g2s, ws, tg = [], [], [], []
for i in range(N):
    cell = top.pcell("SVaricap", model="sg13_hv_svaricap", w=vl.um(W), l=vl.um(L), Nx=NX)
    t = top.add(cell, i * PITCH, 0)
    tg.append(t * cell.dbbox())
    # The PCell's Metal1 pin shapes: the bottom strip is G1, the top strip G2, the narrow one the well contact W
    for p in pya.Region(cell.begin_shapes_rec(ly.layer(8, vl.PIN_DT))).merged().each():
        box = t * p.bbox().to_dtype(ly.dbu)
        if box.width() < 1.0:
            ws.append(box)
        elif box.center().y < 1.0:
            g1s.append(box)
        else:
            g2s.append(box)

x0, x1 = min(b.left for b in g1s), max(b.right for b in g1s)
# Gate strips to the buses: one via row per strip, the bus centered on the strip
for strips, name in ((g1s, "rf_p"), (g2s, "rf_n")):
    yc = strips[0].center().y
    for s in strips:
        cols = int((s.width() - 0.2) / 0.41)
        top.via(s.center().x, yc, "Metal1", "Metal2", cols=cols, rows=1)
    bus = top.rect("Metal2", x0, yc - BUS_W / 2, x1, yc + BUS_W / 2)
    top.pin("Metal2", name, pya.DBox(x0, bus.bottom, x0 + 2.0, bus.top))

# Well contacts to the vtune line on Metal3
yw = ws[0].center().y
for w in ws:
    top.via(w.center().x, yw, "Metal1", "Metal3", cols=1, rows=2)
vt = top.rect("Metal3", ws[0].left - 0.2, yw - 0.5, x1, yw + 0.5)
top.pin("Metal3", "vtune", pya.DBox(vt.left, vt.bottom, vt.left + 2.0, vt.top))

# Substrate tap below the array, clear of the thick-oxide regions
ty = min(b.bottom for b in tg) - 2.0
tap = top.pcell("ptap1", w=vl.um(x1 - x0), l=vl.um(1.0))
tt = top.add(tap, x0, ty - 1.0)
tm1 = top.shapes(tap, tt, "Metal1")[0]
top.pin("Metal1", "VSS", pya.DBox(tm1.left, tm1.bottom, tm1.left + 2.0, tm1.top))

vl.write(top, vl.out_path("vco_var", __file__), drop_texts=("G1", "G2", "W"))
# ==============================================================================
