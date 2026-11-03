# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the bias and enable cell layout/vco_bias.gds.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_bias.py [-rd out=<file.gds>], or make klayout-script CELL=vco_bias
#
# Floorplan, top to bottom: the four NMOS gate capacitors of the bias filters, two mirrored row pairs that share their
# tap band (MCn1 and MCn2 on vbn_buf, MCg1 and MCg2 on vbg_buf), then the transistor block as in a plain bias cell: the
# VDD rail, the PMOS row (gates at the bottom), a channel of Metal3 tracks with one net each, the NMOS row (mirrored,
# gates on top), the VSS rail, and below it the two long filter resistors Rn and Rf. Rg lies in the channel right of
# the rows. Gates and drains reach their track on a vertical Metal2 stub, the resistors and the capacitors' gate columns
# on Metal4. The capacitor block is wider than the transistor block, because the buffer sits below it in the macro.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

# Capacitor block: row k mirrored (gate on top) for k = 0 and 2, upright (gate below) for k = 1 and 3. Rows 0 and 1 and
# rows 2 and 3 abut their taps, the two pairs keep 0.6 um between the facing gate pads.
CAPS = [("MCn1", "vbn_buf"), ("MCn2", "vbn_buf"), ("MCg1", "vbg_buf"), ("MCg2", "vbg_buf")]
CAP_W, CAP_L, CAP_NG = 40.0, 10.0, 5
X_VSS, X_VBN, X_VBG = -3.5, -2.0, -0.6  # x of the VSS column (Metal2) and the two gate columns (Metal4)

Y_LB = -60.4  # offset of the transistor block, whose rails end up below the capacitor block
YP = 9.6  # bottom of the PMOS active areas within the block, the NMOS ones end at its y = 0
TRACKS = ["di_en", "en_b", "en", "ibias_100u", "vbp_ref", "vbg_int", "nbg", "vbn_buf", "vbg_buf"]
TY = {n: Y_LB + 1.7 + 0.8 * i for i, n in enumerate(TRACKS)}

# name: (kind, w, l, ng, x, gate net, drain net), every source is on its rail (VSS or VDD)
NMOS = {
    "MNi1": ("nmos", 0.5, 0.13, 1, 0.0, "di_en", "en_b"),
    "MNi2": ("nmos", 0.5, 0.13, 1, 3.5, "en_b", "en"),
    "MNd0": ("nmos", 1.0, 0.13, 1, 7.0, "en_b", "ibias_100u"),
    "MN0": ("nmos", 2.5, 0.5, 1, 10.5, "ibias_100u", "ibias_100u"),
    "MN1": ("nmos", 2.5, 0.5, 1, 14.0, "ibias_100u", "vbp_ref"),
    "MNd1": ("nmos", 1.0, 0.13, 1, 17.5, "en_b", "vbn_buf"),
    "MN3": ("nmos", 2.5, 0.5, 1, 21.0, "nbg", "nbg"),
}
PMOS = {
    "MPi1": ("pmos", 1.0, 0.13, 1, 0.0, "di_en", "en_b"),
    "MPi2": ("pmos", 1.0, 0.13, 1, 3.5, "en_b", "en"),
    "MPd": ("pmos", 1.0, 0.13, 1, 7.0, "en", "vbp_ref"),
    "MP1": ("pmos", 5.0, 0.5, 1, 14.0, "vbp_ref", "vbp_ref"),
    "MP2": ("pmos", 5.0, 0.5, 1, 24.5, "vbp_ref", "vbg_int"),
}
# name: (PCell, w, l, x of the left end, body center y, net of the left head, net of the right head)
RES = {
    "Rg": ("rppd", 0.5, 8.5, 28.0, Y_LB + 6.9, "vbg_int", "nbg"),
    "Rn": ("rhigh", 0.5, 32.0, 0.0, Y_LB - 7.4, "ibias_100u", "vbn_buf"),
    "Rf": ("rhigh", 0.5, 32.0, 2.0, Y_LB - 8.9, "vbg_int", "vbg_buf"),
}
X_LEFT, X_RIGHT = -5.0, 38.5  # input pins on the left end of their tracks, output pins on the right end

ly = vl.new_layout()
top = vl.Block(ly, "vco_bias")
stubs = []  # (net, layer, x, y0, y1) for the collision check
xs = {n: [] for n in TRACKS}


def add_stub(net, port, x, layer="Metal2"):
    vl.stub(top, port, x, TY[net], layer=layer)
    stubs.append((net, layer, x, min(port[1].center().y, TY[net]), max(port[1].center().y, TY[net])))
    xs[net].append(x)


# Capacitor block. The pad of each gate reaches 1 um left of its row, a Metal1 piece takes the vbn_buf pads on to the
# vbn_buf column. The two taps of a row pair lie 0.3 um apart, so their contact rows keep Cnt.b, and one Metal1 band
# covers both. The bands go left onto the VSS column.
TAP_GAP = 0.3
cap = vl.mos(ly, "MCap", "nmos", CAP_W, CAP_L, CAP_NG, tap="merge", cap=True)
s_local = cap.ports["S"][1].top - cap.ports["ACT"][1].bottom  # from the active area's edge to the tap's far edge
y_row = -0.85  # the first row's gate pad ends at y = 0
cap_s, cap_g = [], {"vbn_buf": [], "vbg_buf": []}
for k, (name, net) in enumerate(CAPS):
    mirror = k % 2 == 0
    p = top.place(cap, 0.0, y_row, mirror=mirror)
    cap_g[net].append(p["G"][1])
    s = p["S"][1]
    if mirror:
        # the next, upright row's tap ends TAP_GAP below this one's
        y_row = s.bottom - TAP_GAP - s_local
        s_upper = s
    else:
        band = top.rect("Metal1", s.left, s.bottom, s.right, s_upper.top)
        cap_s.append(band)
        # the next, mirrored row keeps 0.6 um between the facing gate pads
        g = p["G"][1]
        y_row = g.bottom - 0.6 - (g.top - g.bottom) - 0.25
for g in cap_g["vbn_buf"]:
    top.rect("Metal1", X_VBN - 0.35, g.bottom, g.left + 0.1, g.top)
    top.via(X_VBN, g.center().y, "Metal1", "Metal4", cols=1, rows=1)
for g in cap_g["vbg_buf"]:
    top.via(X_VBG, g.center().y, "Metal1", "Metal4", cols=1, rows=1)
for s in cap_s:
    top.rect("Metal1", X_VSS - 0.35, s.bottom, s.left + 0.1, s.top)
    top.via(X_VSS, s.center().y, "Metal1", "Metal2", cols=1, rows=2)
cap_bottom = min(g.bottom for g in cap_g["vbg_buf"])

# Transistor rows and their rails
rails = {"VSS": [], "VDD": []}
for rows, mirror, y in ((NMOS, True, Y_LB), (PMOS, False, Y_LB + YP)):
    for name, (kind, w, l, ng, x, gnet, dnet) in rows.items():
        p = top.place(vl.mos(ly, name, kind, w, l, ng, tap="merge"), x, y, mirror=mirror)
        g, d = p["G"][1], p["D"][1]
        add_stub(gnet, p["G"], g.left + 0.25)
        add_stub(dnet, p["D"], d.center().x if d.width() < 0.6 else d.right - 0.2)
        rails["VSS" if kind == "nmos" else "VDD"].append(p["S"][1])

vss_y = min(s.bottom for s in rails["VSS"]) - 1.0
vdd_y = max(s.top for s in rails["VDD"]) + 1.0
if vdd_y + 0.8 > cap_bottom - 0.5:
    raise RuntimeError(f"vco_bias.py: the VDD rail ({vdd_y + 0.8:.2f}) runs into the capacitor block ({cap_bottom:.2f})")
vss = top.rect("Metal1", X_VSS - 0.5, vss_y - 0.8, X_RIGHT - 9.0, vss_y)
vdd = top.rect("Metal1", X_VBN + 0.5, vdd_y, max(s.right for s in rails["VDD"]), vdd_y + 0.8)
for s in rails["VSS"]:
    top.rect("Metal1", s.left, vss_y - 0.1, s.right, s.bottom + 0.1)
for s in rails["VDD"]:
    top.rect("Metal1", s.left, s.top - 0.1, s.right, vdd_y + 0.1)

# VSS column: from the capacitors' tap bands down to the VSS rail
top.rect("Metal2", X_VSS - 0.3, vss.center().y, X_VSS + 0.3, max(s.top for s in cap_s))
top.via(X_VSS, vss.center().y, "Metal1", "Metal2", cols=1, rows=2)

# Gate columns of the capacitors down to their tracks
for x, net in ((X_VBN, "vbn_buf"), (X_VBG, "vbg_buf")):
    top.rect("Metal4", x - 0.15, TY[net] - 0.15, x + 0.15, max(g.top for g in cap_g[net]))
    top.via(x, TY[net], "Metal3", "Metal4")
    stubs.append((net, "Metal4", x, TY[net], max(g.top for g in cap_g[net])))
    xs[net].append(x)

# Resistors, rotated so the body runs along x, heads to their tracks: Rg on Metal2 in the channel, the long ones under the
# VSS rail on Metal4, which crosses the NMOS row
for name, (pc, w, l, x0, yc, na, nb) in RES.items():
    cell = top.pcell(pc, Calculate="R", w=vl.um(w), l=vl.um(l), b=0)
    t = top.add(cell, x0, yc + w / 2, rot=270)
    heads = sorted(top.shapes(cell, t, "Metal1"), key=lambda h: h.left)
    for net, h in zip((na, nb), heads):
        add_stub(net, ("Metal1", h), h.center().x, layer="Metal2" if name == "Rg" else "Metal4")

# Tracks, and the pins: inputs on the left end, outputs on the right end of their track
for net in TRACKS:
    if net in ("di_en", "ibias_100u"):
        xs[net].append(X_LEFT)
    if net in ("vbn_buf", "vbg_buf"):
        xs[net].append(X_RIGHT)
    tr = vl.track(top, TY[net], xs[net])
    if net in ("di_en", "ibias_100u"):
        top.pin("Metal3", net, pya.DBox(tr.left, tr.bottom, tr.left + 1.0, tr.top))
    if net in ("vbn_buf", "vbg_buf"):
        top.pin("Metal3", net, pya.DBox(tr.right - 1.0, tr.bottom, tr.right, tr.top))
top.pin("Metal1", "VSS", pya.DBox(vss.left, vss.bottom, vss.left + 2.0, vss.top))
top.pin("Metal1", "VDD", pya.DBox(vdd.left, vdd.bottom, vdd.left + 2.0, vdd.top))

# Two stubs of different nets on the same layer must not touch: same span in y and less than 0.6 um apart in x
for i, (na, la, xa, a0, a1) in enumerate(stubs):
    for nb, lb, xb, b0, b1 in stubs[i + 1:]:
        if na != nb and la == lb and abs(xa - xb) < 0.6 and a0 < b1 + 0.3 and b0 < a1 + 0.3:
            raise RuntimeError(f"vco_bias.py: stubs of {na} and {nb} collide at x = {xa:.2f} and {xb:.2f}")

vl.write(top, vl.out_path("vco_bias", __file__))
# ==============================================================================
