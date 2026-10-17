# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the output buffer layout/vco_buf.gds.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_buf.py [-rd out=<file.gds>], or make klayout-script CELL=vco_buf
#
# Mirror-symmetric about x = 0, bottom to top: the VSS rail, the tail MBt (60 fingers, gate on top, its taps also bias
# the pair's substrate), the pair MB1/MB2 (gates on top), the 50 Ohm loads at the outer sides, the VDD rail, the
# coupling caps with the gate bias resistors outside them. The caps' Metal5 bottom plates are the inputs rf_p/rf_n.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

Y1 = 6.0  # top of the pair's active areas
GAP = 1.5  # half the gap between the pair's active areas
XO = 12.0  # x of the output nodes, outside the pair
RL_Y = 8.0  # bottom of the load resistor bodies
VDD_Y = 10.6  # bottom of the VDD rail
CC_X, CC_Y, CC = 4.5, 13.0, 10.0  # inner edge, bottom and side of the coupling caps
XG = 2.5  # x of the gate lines from the caps' top plates down to the pair
RB_X = 24.0  # x of the gate bias resistors
TOP_Y = 22.6  # y of the vbg_buf track over the caps
X_EDGE = 29.0  # pins on the left edge sit at -X_EDGE
Y_BOT = -6.5  # bottom edge, the outputs end there

ly = vl.new_layout()
top = vl.Block(ly, "vco_buf")

# Tail, mirrored so its gate pad faces the pair
mbt = vl.mos(ly, "MBt", "nmos", 150.0, 0.5, 60, tap="merge")
aw = mbt.ports["ACT"][1].width()
pt = top.place(mbt, -aw / 2, 0.0, mirror=True)
vss_s = pt["S"][1]
vss = top.rect("Metal1", vss_s.left, vss_s.bottom - 1.2, vss_s.right, vss_s.bottom - 0.4)
top.rect("Metal1", vss_s.left, vss.top - 0.1, vss_s.right, vss_s.bottom + 0.1)
top.pin("Metal1", "VSS", pya.DBox(vss.left, vss.bottom, vss.left + 2.0, vss.top))

# vbn_buf: the tail's gate pad to the left edge on Metal3
g = pt["G"][1]
top.via(g.left + 0.4, g.center().y, "Metal1", "Metal3")
vbn = top.rect("Metal3", -X_EDGE, g.center().y - 0.2, g.left + 0.6, g.center().y + 0.2)
top.pin("Metal3", "vbn_buf", pya.DBox(vbn.left, vbn.bottom, vbn.left + 1.0, vbn.top))

# The pair: MB1 on the left (mirrored), MB2 its image in x (rotated by 180 degrees)
mb = vl.mos(ly, "MB", "nmos", 24.0, 0.13, 12)
paw = mb.ports["ACT"][1].width()
pairs = {
    "left": top.place(mb, -GAP - paw, Y1, mirror=True),
    "right": top.place(mb, GAP + paw, Y1, rot=180),
}
td = pt["D"][1]
for side, sgn in (("left", -1), ("right", 1)):
    p = pairs[side]
    s, d = p["S"][1], p["D"][1]
    # Tail: three Metal2 stubs from the tail's drain strap up to the pair's source rail
    for f in (0.15, 0.5, 0.85):
        x = s.left + f * s.width()
        top.rect("Metal2", x - 0.3, td.center().y, x + 0.3, s.center().y + 0.15)
        top.via(x, s.center().y, "Metal1", "Metal2", cols=1, rows=1)
    # Output node: the drain strap out to x = sgn * XO, up to the load's bottom head, down to the bottom edge on Metal3
    xo = sgn * XO
    top.rect("Metal2", min(xo - 0.3, d.left), d.center().y - 0.3, max(xo + 0.3, d.right), d.center().y + 0.3)
    rl = top.pcell("rppd", Calculate="R", w=vl.um(10.0), l=vl.um(1.65), b=0)
    trl = top.add(rl, xo - 9.0 if sgn < 0 else xo - 1.0, RL_Y)
    bot_head, top_head = sorted(top.shapes(rl, trl, "Metal1"), key=lambda b: b.bottom)
    top.rect("Metal2", bot_head.left + 0.2, bot_head.bottom, bot_head.right - 0.2, bot_head.top)
    top.via(bot_head.center().x, bot_head.center().y, "Metal1", "Metal2", cols=20, rows=1)
    top.rect("Metal2", xo - 0.3, d.center().y, xo + 0.3, bot_head.top)
    top.via(xo, d.center().y, "Metal2", "Metal3", cols=1, rows=2)
    oline = top.rect("Metal3", xo - 0.3, Y_BOT, xo + 0.3, d.center().y + 0.3)
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
    top.via(xg, yg, "Metal2", "TopMetal1", cols=2, rows=2, tcols=2, trows=2)
    gpad = p["G"][1]
    top.rect("Metal2", xg - 0.3, gpad.center().y, xg + 0.3, yg)
    top.via(xg, gpad.center().y, "Metal1", "Metal2", cols=1, rows=1)
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

vl.write(top, vl.out_path("vco_buf", __file__))
# ==============================================================================
