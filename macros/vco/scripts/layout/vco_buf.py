# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the output buffer layout/vco_buf.gds.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_buf.py [-rd out=<file.gds>], or make klayout-script CELL=vco_buf
#
# Mirror-symmetric about x = 0, bottom to top: the VSS rail, the tail MBt (30 fingers, gate on top, its taps also bias
# the pair's substrate), the pair MB1/MB2 (gates on top), the 50 Ohm loads at the outer sides, the VDD rail, the
# coupling caps with the gate bias resistors outside them. The caps' Metal5 bottom plates are the inputs rf_p/rf_n.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

Y1 = 4.5  # top of the pair's active areas
GAP = 1.5  # half the gap between the pair's active areas
XO = 12.0  # x of the output nodes, outside the pair
W_STUB = 1.0  # width of the Metal2 stubs from the tail to each side of the pair
W_OUT = 3.0  # width of the Metal3 from the drain strap up to the load
RL_Y = 6.5  # bottom of the load resistor bodies
VDD_Y = 9.1  # bottom of the VDD rail
CC_X, CC_Y, CC = 4.5, 11.5, 10.0  # inner edge, bottom and side of the coupling caps
XG = 2.5  # x of the gate lines from the caps' top plates down to the pair
RB_X = 24.0  # x of the gate bias resistors
TOP_Y = 21.1  # y of the vbg_buf track over the caps
X_EDGE = 26.0  # pins on the left edge sit at -X_EDGE

ly = vl.new_layout()
top = vl.Block(ly, "vco_buf")

# Tail, mirrored so its gate pad faces the pair
S_TAIL = 0.8  # Metal1 width of the tail's source stripes
mbt = vl.mos(ly, "MBt", "nmos", 150.0, 0.5, 30, tap="merge", s_width=S_TAIL)
aw = mbt.ports["ACT"][1].width()
pt = top.place(mbt, -aw / 2, 0.0, mirror=True)
vss_s = pt["S"][1]
vss = top.rect("Metal1", vss_s.left, vss_s.bottom - 1.2, vss_s.right, vss_s.bottom - 0.4)
top.rect("Metal1", vss_s.left, vss.top - 0.1, vss_s.right, vss_s.bottom + 0.1)
top.pin("Metal1", "VSS", pya.DBox(vss.left, vss.bottom, vss.left + 2.0, vss.top))
y_bot = vss.bottom  # the outputs end on the bottom edge, level with the VSS rail

# vbn_buf: the tail's gate pad to the left edge on Metal3
g = pt["G"][1]
top.via(g.left + 0.4, g.center().y, "Metal1", "Metal3")
vbn = top.rect("Metal3", -X_EDGE, g.center().y - 0.2, g.left + 0.6, g.center().y + 0.2)
top.pin("Metal3", "vbn_buf", pya.DBox(vbn.left, vbn.bottom, vbn.left + 1.0, vbn.top))

# The pair: MB1 on the left (mirrored), MB2 its image in x (rotated by 180 degrees)
mb = vl.mos(ly, "MB", "nmos", 24.0, 0.13, 12, d_metal="Metal3", s_strap=True)
paw = mb.ports["ACT"][1].width()
pairs = {
    "left": top.place(mb, -GAP - paw, Y1, mirror=True),
    "right": top.place(mb, GAP + paw, Y1, rot=180),
}
td = pt["D"][1]
for side, sgn in (("left", -1), ("right", 1)):
    p = pairs[side]
    s, d = p["S"][1], p["D"][1]
    # Tail: three Metal2 stubs from the tail's drain strap up onto the pair's Metal2 source rail
    for f in (0.15, 0.5, 0.85):
        x = s.left + f * s.width()
        top.rect("Metal2", x - W_STUB / 2, td.center().y, x + W_STUB / 2, s.top)
    # Output node on Metal3: the drain strap out past x = sgn * XO, up over the load's bottom head and Rl, down to the
    # bottom edge. The buffer's DC current takes the first two, the output line carries none.
    xo = sgn * XO
    x_out = xo + sgn * (W_OUT - 1.0)
    strap = top.rect("Metal3", min(x_out, d.left), s.bottom, max(x_out, d.right), d.top)
    rl = top.pcell("rppd", Calculate="R", w=vl.um(10.0), l=vl.um(1.65), b=0)
    trl = top.add(rl, xo - 9.0 if sgn < 0 else xo - 1.0, RL_Y)
    bot_head, top_head = sorted(top.shapes(rl, trl, "Metal1"), key=lambda b: b.bottom)
    plate = top.rect("Metal3", bot_head.left + 0.2, bot_head.bottom, bot_head.right - 0.2, VDD_Y - 0.9)
    top.via(bot_head.center().x, bot_head.center().y, "Metal1", "Metal3", cols=20, rows=1)
    top.rect("Metal3", min(x_out, xo - sgn), d.bottom, max(x_out, xo - sgn), plate.top)
    oline = top.rect("Metal3", xo - 0.3, y_bot, xo + 0.3, d.top)
    top.pin("Metal3", "rf_out_n" if sgn < 0 else "rf_out_p", pya.DBox(oline.left, oline.bottom, oline.right, oline.bottom + 1.0))
    top.rect("Metal1", top_head.left, top_head.bottom, top_head.right, VDD_Y + 0.1)
    # Coupling cap: top plate (TopMetal1) is the gate node, bottom plate (Metal5) the input
    cc = top.pcell("cmim", Calculate="C", w=vl.um(CC), l=vl.um(CC))
    tcc = top.add(cc, -CC_X - CC if sgn < 0 else CC_X, CC_Y)
    m5 = top.shapes(cc, tcc, "Metal5")[0]
    tm1 = top.shapes(cc, tcc, "TopMetal1")[0]
    tab = top.rect("Metal5", m5.left, m5.top - 0.1, m5.right, m5.top + 1.5)
    top.pin("Metal5", "rf_p" if sgn < 0 else "rf_n", pya.DBox(tab.left, tab.top - 1.0, tab.right, tab.top))
    xg = sgn * XG
    yg = tm1.center().y
    top.rect("TopMetal1", min(xg - 1.05 * sgn, tm1.left if sgn < 0 else tm1.right),
             yg - 1.05, max(xg - 1.05 * sgn, tm1.left if sgn < 0 else tm1.right), yg + 1.05)
    top.rect("TopMetal1", xg - 1.05, yg - 1.05, xg + 1.05, yg + 1.05)
    top.via(xg, yg, "Metal2", "TopMetal1", cols=2, rows=5, tcols=2, trows=2)
    # The tank drives the gates through the cap and this line, so its resistance is tank loss: two via rows along the pad.
    gpad = p["G"][1]
    gy0, gy1 = gpad.bottom, gpad.top + 0.5
    top.rect("Metal1", gpad.left, gy0, gpad.right, gy1)
    top.rect("Metal2", gpad.left, gy0, gpad.right, gy1)
    top.via(gpad.center().x, (gy0 + gy1) / 2, "Metal1", "Metal2", cols=12, rows=2)
    top.rect("Metal2", xg - 0.5, gy0, xg + 0.5, yg)
    # Gate bias resistor outside the cap: bottom head to the gate line on Metal2, top head to the vbg_buf track
    rb = top.pcell("rhigh", Calculate="R", w=vl.um(0.5), l=vl.um(8.0), b=0)
    trb = top.add(rb, sgn * RB_X - 0.25, CC_Y)
    rb_bot, rb_top = sorted(top.shapes(rb, trb, "Metal1"), key=lambda b: b.bottom)
    top.via(rb_bot.center().x, rb_bot.center().y, "Metal1", "Metal2")
    top.rect("Metal2", min(rb_bot.center().x, xg) - 0.3, rb_bot.center().y - 0.3,
             max(rb_bot.center().x, xg) + 0.3, rb_bot.center().y + 0.3)
    top.via(rb_top.center().x, rb_top.center().y, "Metal1", "Metal3")
    top.rect("Metal3", rb_top.center().x - 0.3, rb_top.center().y, rb_top.center().x + 0.3, TOP_Y)

vbg = top.rect("Metal3", -X_EDGE, TOP_Y - 0.3, RB_X + 0.3, TOP_Y + 0.3)
top.pin("Metal3", "vbg_buf", pya.DBox(vbg.left, vbg.bottom, vbg.left + 1.0, vbg.top))
vdd = top.rect("Metal1", -XO - 10.0, VDD_Y, XO + 10.0, VDD_Y + 0.8)
top.pin("Metal1", "VDD", pya.DBox(vdd.left, vdd.bottom, vdd.left + 2.0, vdd.top))

i_side = vl.I_TAIL / 2
vl.check_wire("tail source stripe", "Metal1", S_TAIL, vl.I_TAIL / 30 * 2)
vl.check_wire("tail to pair, each stub", "Metal2", W_STUB, i_side / 3)
vl.check_source_strip("pair source strip", i_side / 12 * 2)
vl.check_wire("pair drain strap", "Metal3", strap.height(), i_side)
vl.check_wire("drain to load", "Metal3", W_OUT, i_side)
vl.check_cuts("load's bottom head", "Via1", 20, i_side)

vl.write(top, vl.out_path("vco_buf", __file__))
# ==============================================================================
