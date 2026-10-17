# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the bias and enable cell layout/vco_bias.gds.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_bias.py [-rd out=<file.gds>], or make klayout-script CELL=vco_bias
#
# Floorplan, bottom to top: the three MIM filter caps, the VSS rail, the NMOS row (mirrored, gates on top), a channel of
# Metal3 tracks with one net each, the PMOS row (gates at the bottom), the VDD rail. The resistors lie in the channel
# right of the rows. Gates and drains reach their track on a vertical Metal2 stub, the caps on a Metal4 stub.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import vco_layout as vl  # noqa: E402

YP = 9.6  # bottom of the PMOS active areas, the NMOS ones end at y = 0
TRACKS = ["di_en", "en_b", "en", "ibias_100u", "vbp_ref", "vbp_core", "vbg_buf", "nbg", "vbn_buf"]
TY = {n: 1.7 + 0.8 * i for i, n in enumerate(TRACKS)}

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
    "MPd": ("pmos", 1.0, 0.13, 1, 7.0, "en", "vbp_core"),
    "MP1": ("pmos", 5.0, 0.5, 1, 14.0, "vbp_ref", "vbp_ref"),
    "MP2": ("pmos", 5.0, 0.5, 1, 24.5, "vbp_core", "vbg_buf"),
}
XR = 28.0  # left end of the resistor bodies
# name: (PCell, w, l, x offset, body center y, net of the left head, net of the right head)
RES = {
    "Rn": ("rhigh", 0.5, 16.0, 0.0, 2.1, "ibias_100u", "vbn_buf"),
    "Rp": ("rhigh", 0.5, 16.0, 1.0, 4.5, "vbp_ref", "vbp_core"),
    "Rg": ("rppd", 0.5, 8.5, 2.0, 6.9, "vbg_buf", "nbg"),
}
CAP_TOP = -7.0  # top edge of the MIM areas
# name: (side, x, net of the top plate on TopMetal1, net of the bottom plate on Metal5)
CAPS = {"Cn": (30.0, 0.0, "vbn_buf", "VSS"), "Cg": (20.0, 35.0, "vbg_buf", "VSS"), "Cp": (30.0, 60.0, "VDD", "vbp_core")}

ly = vl.new_layout()
top = vl.Block(ly, "vco_bias")
stubs = []  # (net, layer, x, y0, y1) for the collision check
xs = {n: [] for n in TRACKS}


def add_stub(net, port, x, layer="Metal2"):
    vl.stub(top, port, x, TY[net], layer=layer)
    stubs.append((net, layer, x, min(port[1].center().y, TY[net]), max(port[1].center().y, TY[net])))
    xs[net].append(x)


# Transistor rows and their rails
rails = {"VSS": [], "VDD": []}
for rows, mirror, y in ((NMOS, True, 0.0), (PMOS, False, YP)):
    for name, (kind, w, l, ng, x, gnet, dnet) in rows.items():
        p = top.place(vl.mos(ly, name, kind, w, l, ng, tap="merge"), x, y, mirror=mirror)
        g, d = p["G"][1], p["D"][1]
        add_stub(gnet, p["G"], g.left + 0.25)
        add_stub(dnet, p["D"], d.center().x if d.width() < 0.6 else d.right - 0.2)
        rails["VSS" if kind == "nmos" else "VDD"].append(p["S"][1])

xr_max = XR + max(r[3] + r[2] for r in RES.values()) + 1.0
vss_y = min(s.bottom for s in rails["VSS"]) - 1.0
vdd_y = max(s.top for s in rails["VDD"]) + 1.0
vss = top.rect("Metal1", -3.0, vss_y - 0.8, 56.0, vss_y)
vdd = top.rect("Metal1", -3.0, vdd_y, 88.0, vdd_y + 0.8)
for s in rails["VSS"]:
    top.rect("Metal1", s.left, vss_y - 0.1, s.right, s.bottom + 0.1)
for s in rails["VDD"]:
    top.rect("Metal1", s.left, s.top - 0.1, s.right, vdd_y + 0.1)

# Resistors, rotated so the body runs along x, heads to their tracks
for name, (pc, w, l, dx, yc, na, nb) in RES.items():
    cell = top.pcell(pc, Calculate="R", w=vl.um(w), l=vl.um(l), b=0)
    t = top.add(cell, XR + dx, yc + w / 2, rot=270)
    heads = top.shapes(cell, t, "Metal1")
    for net, h in zip((na, nb), heads):
        add_stub(net, ("Metal1", h), h.center().x)

# MIM caps below the VSS rail. A bottom plate on VSS joins the rail through via stacks on a Metal5 tab above the cap,
# any other plate reaches its track on a Metal4 stub.
for name, (side, x, ntop, nbot) in CAPS.items():
    cell = top.pcell("cmim", Calculate="C", w=vl.um(side), l=vl.um(side))
    t = top.add(cell, x, CAP_TOP - side)
    m5 = top.shapes(cell, t, "Metal5")[0]
    tab = top.rect("Metal5", m5.left, m5.top - 0.1, m5.right, vss_y - 1.6)
    if nbot == "VSS":
        for xv in (m5.left + 2.0, m5.center().x, m5.right - 2.0):
            _, m1 = top.via(xv, tab.center().y, "Metal1", "Metal5", cols=2, rows=2)
            top.rect("Metal1", xv - 0.35, m1.bottom, xv + 0.35, vss_y - 0.7)
    else:
        xv = m5.center().x
        m4, _ = top.via(xv, tab.center().y, "Metal4", "Metal5", cols=2, rows=2)
        add_stub(nbot, ("Metal4", m4), xv, layer="Metal4")
    tm1 = top.shapes(cell, t, "TopMetal1")[0]
    if ntop == "VDD":
        # A TopMetal1 strap from the top plate up to the VDD rail on the right
        xs_ = tm1.right - 1.5
        top.rect("TopMetal1", xs_ - 1.0, tm1.center().y, xs_ + 1.0, vdd.top)
        top.via(xs_, vdd.center().y, "Metal1", "TopMetal1", cols=2, rows=2, tcols=1, trows=1)
    else:
        # TopMetal1 tab left of the cap to an island clear of the bottom plate, then a Metal4 stub
        xi = m5.left - 2.2
        top.rect("TopMetal1", xi - 1.05, tm1.center().y - 1.05, tm1.left + 0.5, tm1.center().y + 1.05)
        m4, _ = top.via(xi, tm1.center().y, "Metal4", "TopMetal1", cols=2, rows=2, tcols=2, trows=2)
        add_stub(ntop, ("Metal4", m4), xi, layer="Metal4")

# Tracks, and the pins: inputs on the left end, outputs on the right end of their track
x_left, x_right = -4.0, 92.0
for net in TRACKS:
    if net in ("di_en", "ibias_100u"):
        xs[net].append(x_left)
    if net in ("vbp_core", "vbg_buf", "vbn_buf"):
        xs[net].append(x_right)
    tr = vl.track(top, TY[net], xs[net])
    if net in ("di_en", "ibias_100u"):
        top.pin("Metal3", net, pya.DBox(tr.left, tr.bottom, tr.left + 1.0, tr.top))
    if net in ("vbp_core", "vbg_buf", "vbn_buf"):
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
