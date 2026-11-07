# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the center tap feed layout/vco_feed.gds.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_feed.py [-rd out=<file.gds>], or make klayout-script CELL=vco_feed
#
# Sits on the macro's bottom edge. Left to right: the switch MPs with its source rail along the bottom, under the VDD
# strap, then Rct with the coil's side at the bottom, then the tap to VSS. The core's whole current passes here, so every
# wire and via array is sized for it: Metal2 over Rct carries it from the switch's drain to the top head, Metal3 from the
# bottom head to the macro's line up to the coil.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

W_S, L_S, NG_S = 96.0, 0.13, 32  # MPs
W_R, L_R = 17.3, 8.8  # Rct, 0.27 mA/um at TT, the current density the buffer's loads run at
Y_TAP = 0.5  # bottom edge of MPs's tap and so of its source rail
Y_RTOP = 10.05  # top edge of Rct's top head, 0.35 um below the MoM caps of the ihp-sg13cmos5l macro
GAP_D = 2.3  # from MPs's Activ to Rct: the via field from the drain strap on Metal3 down to the Metal2 over Rct
GAP_TAP = 0.9  # from Rct's heads to the tap, for EXTB.c and pSD.b

ly = vl.new_layout()
top = vl.Block(ly, "vco_feed")

# The switch, mirrored so its source rail faces the bottom edge
mps = vl.mos(ly, "MPs", "pmos", W_S, L_S, NG_S, tap="merge", d_metal="Metal3", gext=1.5, s_strap=True)
act = mps.ports["ACT"][1]
s_h = mps.ports["S"][1].top - act.bottom
p = top.place(mps, 1.6, Y_TAP + s_h, mirror=True)
s, d, g, a = p["S"][1], p["D"][1], p["G"][1], p["ACT"][1]

# Metal2 over the whole source band, for the macro's via stack to the VDD strap
top.rect("Metal2", a.left, s.bottom, a.right, s.top)

# The gate on Metal2, on the left end of its pad, clear of the source strips at the macro's en_b line
xg = g.left + 0.35
top.via(xg, g.center().y, "Metal1", "Metal2", cols=2)
top.rect("Metal2", xg - 0.35, g.bottom, xg + 0.35, g.top)

# Rct, its top head on Y_RTOP, its body along y
rct = top.pcell("rppd", Calculate="R", w=vl.um(W_R), l=vl.um(L_R), b=0)
x_r = a.right + GAP_D
heads = top.shapes(rct, pya.DCplxTrans(1.0, 0, False, 0, 0), "Metal1")
y_top = max(h.top for h in heads)
trct = top.add(rct, x_r - min(h.left for h in heads), Y_RTOP - y_top)
h_bot, h_top = sorted(top.shapes(rct, trct, "Metal1"), key=lambda b: b.bottom)
print(f"Rct heads: x {h_bot.left:.3f} to {h_bot.right:.3f}, y {h_bot.bottom:.3f}, {h_bot.top:.3f} and {h_top.bottom:.3f}, {h_top.top:.3f}")
cols = int((h_bot.width() - 0.1) / 0.41)

# The drain: a Metal3 plate over MPs, above the VDD strap's via stack, on to the via field, down to Metal2 over Rct and
# along it to the top head's via row
y_field = (s.top, g.top)
m2_left = a.right + 0.25
top.rect("Metal3", d.left, y_field[0], x_r - 0.1, y_field[1])
fw = x_r - 0.1 - m2_left
fcols, frows = int((fw - 0.1) / 0.41), int((y_field[1] - y_field[0] - 0.1) / 0.41)
top.via((m2_left + x_r - 0.1) / 2, (y_field[0] + y_field[1]) / 2, "Metal2", "Metal3", cols=fcols, rows=frows)
top.rect("Metal2", m2_left, h_bot.top + 0.75, h_bot.right, h_top.top)
top.via(h_top.center().x, h_top.center().y, "Metal1", "Metal2", cols=cols)

# The bottom head: one via row to Metal3, a plate along it
top.via(h_bot.center().x, h_bot.center().y, "Metal1", "Metal3", cols=cols)
m3 = top.rect("Metal3", x_r + 0.25, h_bot.bottom, h_bot.right, h_bot.bottom + 3.5)

# The tap, beside Rct
x_t = h_bot.right + GAP_TAP
tap = top.pcell("ptap1", w=vl.um(0.6), l=vl.um(h_top.top - h_bot.bottom))
tt = top.add(tap, x_t, h_bot.bottom)
t = top.shapes(tap, tt, "Metal1")[0]

top.pin("Metal2", "en_b", pya.DBox(xg - 0.35, g.bottom, xg + 0.35, g.top))
top.pin("Metal1", "VDD", pya.DBox(a.left, s.bottom, a.right, s.top))
top.pin("Metal3", "vdd_core", pya.DBox(m3.left, m3.bottom, m3.right, m3.top))
top.pin("Metal1", "VSS", pya.DBox(t.left, t.bottom, t.right, t.top))

vl.check_source_strip("MPs source strip", vl.I_CORE / NG_S * 2)
vl.check_wire("MPs drain plate", "Metal3", y_field[1] - y_field[0], vl.I_CORE)
vl.check_cuts("drain to the Metal2 over Rct", "Via2", fcols * frows, vl.I_CORE)
vl.check_wire("Metal2 over Rct", "Metal2", h_top.top - h_bot.top - 0.75, vl.I_CORE)
vl.check_cuts("Rct heads", "Via1", cols, vl.I_CORE)
vl.check_wire("Rct bottom head plate", "Metal3", m3.height(), vl.I_CORE * 0.65)

vl.write(top, vl.out_path("vco_feed", __file__))
# ==============================================================================
