# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the bias and enable cell layout/vco_bias.gds.
# ============================================
#
# Usage: klayout -b -r scripts/layout/vco_bias.py [-rd out=<file.gds>], or make klayout-script CELL=vco_bias
#
# Floorplan, top to bottom: the four NMOS gate capacitors of the bias filters, two mirrored row pairs that share their
# tap band (MCn1 and MCn2 on vbn_buf, MCg1 and MCg2 on vbg_buf). Below them a rectangle over the buffer's height, with
# the transistors in its top right corner, next to the buffer's bias pins and with the mirrors closest to MBt, Rg beside
# them, the two RF decaps Cg1 and Cg2 of vbg_buf as an L around them, and the filter resistors Rn and Rf along the bottom.
# The two rows share their columns and face each other with their gates. All wiring runs over them, on Metal2 stubs up to
# Metal3 tracks at the minimum pitch. The decaps are cap_cmim, with their Metal5 plates on VSS. The floorplan is that of
# the ihp-sg13cmos5l macro, whose MoM decaps block the lower metals: the lines that pass them run in a band of Metal3
# tracks above them, VDD on Metal1 under that band, VSS on Metal1 below them, and Rn and Rf reach the rows on Metal4
# risers at the right edge and the capacitors' gate columns on the left.

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

X_LEFT, X_RIGHT = -5.0, 38.5  # input pins on the left end of their tracks, output pins on the right end
ROW_H = 12.4  # from the VSS tap band to the VDD tap band, 0.4 um between the facing gate pads
GAP_CAP = 0.4  # from the VDD tap band to MCg2's gate pad, which puts the band's nBuLay 1 um from MCg2's Activ (Magic's NBL.e)
X_ROWS = 38.2  # right edge of the rows

# Columns: the Activ's left edge relative to the first column, 1.55 um for the short devices, 1.85 um for the long ones.
# The mirrors MN0 and MN1, MP1 and MP2 sit between end dummies. MDp3 and MDp4 fill the PMOS row to the rectangle.
COLS = (0.0, 1.55, 3.1, 4.65, 6.15, 8.0, 9.85, 11.7, 13.55)
# column: (name, w, l, gate net, drain net), every source is on its rail, a dummy has no nets
NMOS = {
    0: ("MNi2", 0.5, 0.13, "en_b", "en"),
    1: ("MNi1", 0.5, 0.13, "di_en", "en_b"),
    2: ("MNd0", 1.0, 0.13, "en_b", "ibias_100u"),
    3: ("MNd1", 1.0, 0.13, "en_b", "vbn_buf"),
    4: ("MN3", 2.5, 0.5, "nbg", "nbg"),
    5: ("MDn2", 2.5, 0.5, None, None),
    6: ("MN1", 2.5, 0.5, "ibias_100u", "vbp_ref"),
    7: ("MN0", 2.5, 0.5, "ibias_100u", "ibias_100u"),
    8: ("MDn1", 2.5, 0.5, None, None),
}
PMOS = {
    0: ("MPi2", 1.0, 0.13, "en_b", "en"),
    1: ("MPi1", 1.0, 0.13, "di_en", "en_b"),
    2: ("MPd", 1.0, 0.13, "en", "vbp_ref"),
    3: ("MDp4", 1.0, 0.13, None, None),
    4: ("MDp3", 5.0, 0.5, None, None),
    5: ("MDp2", 5.0, 0.5, None, None),
    6: ("MP2", 5.0, 0.5, "vbp_ref", "vbg_int"),
    7: ("MP1", 5.0, 0.5, "vbp_ref", "vbp_ref"),
    8: ("MDp1", 5.0, 0.5, None, None),
}

# Metal3 tracks at 0.51 um, 0.3 um wide, under the Metal3 pad of MCg2's gate via. vbg_buf lies on the buffer's pin, vbn_buf
# 0.8 um below that pin, as they share the macro's riser at X_BB.
BAND = {"ibias_100u": -41.75, "di_en": -42.26, "vbg_buf": -43.0, "vbn_buf": -43.8}
ROW_TRACKS = ("nbg", "ibias_100u", "en_b", "en", "vbp_ref", "vbg_int")  # NMOS nets low, PMOS nets high, from Y_RT up
TRACK_W, TRACK_P = 0.3, 0.51

Y_RN, Y_RF = -67.8, -69.3  # body centers of the filter resistors
RES_L = 32.0
Y_JOG = -65.2  # y of the Metal3 jog from Rn's left head to the vbn_buf column, above the macro's VSS riser
Y_VSS_RAIL = (-66.75, -65.0)  # Metal1, 0.25 um above the heads of Rn, wide because the bias reference hangs on it
Y_VSS_PIN = (-66.75, -66.15)  # the rail's lower part, where the macro's riser and the decaps' via stacks land
X_RISE_I, X_RISE_G = 37.3, 38.2  # Metal4 risers from Rn and Rf to the rows
X_LANE = 21.4  # Metal1 lane from the rows' VSS band down to the rail, between the decaps
MIM_ENC = 0.6  # the Metal5 plate past the MIM area
Y_DECAP, Y_DECAP_TOP = -64.4, -44.1
# The Metal5 plates' extents. Cg2's top follows the rows.
X_CG1, X_CG2 = (0.2, 20.9), (21.9, 36.7)

ly = vl.new_layout()
top = vl.Block(ly, "vco_bias")
stubs = []  # (net, layer, x, y0, y1) for the collision check


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

# The rows: every device sits on its row's tap band, so the short ones leave room for the tracks in the middle
y_top = cap_bottom - GAP_CAP
y_bot = y_top - ROW_H
y_nlo, y_phi = y_bot + 1.4, y_top - 1.4  # the Activ edges next to the tap bands
x0 = X_ROWS - COLS[-1] - 1.18  # the last column's Activ is 1.18 um wide
y_rt = y_bot + 4.45  # lowest row track, on the long NMOS devices' gate pads
TY = dict(BAND)
TY.update({n: y_rt + TRACK_P * i for i, n in enumerate(ROW_TRACKS)})
xs = {n: [] for n in TY}


def add_stub(net, port, x, joint=True):
    """A Metal2 stub from a port up or down to its net's track, two cuts per via. joint=False leaves out the via to the
    track, for neighbouring stubs of one net, whose two-cut joints would overlap."""
    layer, box = port
    y, yp = TY[net], box.center().y
    if layer == "Metal1":
        top.via(x, yp, "Metal1", "Metal2", cols=2)
    top.rect("Metal2", x - 0.15, min(yp, y) - 0.1, x + 0.15, max(yp, y) + 0.1)
    if joint:
        top.via(x, y, "Metal2", "Metal3", cols=2)
    stubs.append((net, "Metal2", x, min(yp, y), max(yp, y)))
    xs[net].append(x)


def dummy_gate_tie(g, rail_y):
    """The dummy's gate pad to its rail on Metal1, past the Activ's left edge."""
    top.rect("Metal1", g.left, min(g.bottom, rail_y), g.left + 0.25, max(g.top, rail_y))


for rows, mirror in ((NMOS, True), (PMOS, False)):
    for k, (name, w, l, gnet, dnet) in rows.items():
        y = y_nlo + w if mirror else y_phi - w
        x = x0 + COLS[k]
        if gnet is None:
            p = top.place(vl.mos(ly, name, "nmos" if mirror else "pmos", w, l, 1, gext=0.75, cap=True), x, y, mirror=mirror)
            dummy_gate_tie(p["G"][1], p["S"][1].center().y)
            continue
        p = top.place(vl.mos(ly, name, "nmos" if mirror else "pmos", w, l, 1, gext=0.75), x, y, mirror=mirror)
        g, d = p["G"][1], p["D"][1]
        xd = d.center().x
        if not mirror and l > 0.2:
            # The gate of MP1 and MP2 on the vbp_ref stub of its column: its own drain's in MP1, MN1's drain's in MP2
            xg, yg = g.right - 0.35, g.center().y
            top.via(xg, yg, "Metal1", "Metal2", cols=2)
            top.rect("Metal2", xg - 0.35, yg - 0.15, xd + 0.15, yg + 0.15)
            if name == "MP1":
                top.rect("Metal2", xd - 0.15, yg - 0.15, xd + 0.15, TY[gnet])
        else:
            add_stub(gnet, p["G"], g.left + 0.35, joint=name != "MNd0")
        add_stub(dnet, p["D"], xd, joint=name not in ("MNi1", "MPi1"))
        if name == "MNi1":
            xd_en_b = xd
        elif name == "MNd0":
            # MNi1's and MPi1's drain stub and MNd0's gate stub are neighbours on en_b: one joint between them
            xg = g.left + 0.35
            top.rect("Metal2", xd_en_b, TY["en_b"] - 0.15, xg, TY["en_b"] + 0.15)
            top.via((xd_en_b + xg) / 2, TY["en_b"], "Metal2", "Metal3", cols=2)

x_right, x_left = x0 + COLS[-1] + 1.18, x0 - 0.55
tap_w = x_right - x0
top.add(top.pcell("ptap1", w=vl.um(tap_w), l=vl.um(0.6)), x0, y_bot)
top.add(top.pcell("ntap1", w=vl.um(tap_w), l=vl.um(0.6)), x0, y_top - 0.6)
band_vss = top.rect("Metal1", x_left, y_bot, x_right, y_nlo - 0.25)
band_vdd = top.rect("Metal1", x_left, y_phi + 0.25, x_right, y_top)
top.rect("NWell", x0 - 0.31, y_phi - 5.0 - 0.31, x_right + 0.31, y_top + 0.31)

# VDD: the band on to the left edge, under the Metal3 tracks. The macro's riser drops a via stack on its left end, whose
# Metal3 keeps clear of the di_en and ibias_100u tracks there.
vdd = top.rect("Metal1", X_VBN + 0.5, band_vdd.bottom - 0.4, x_left + 0.3, band_vdd.bottom + 0.1)

# VSS: a rail above Rn, up to the capacitors' tap bands on the column at the left and to the rows on a lane between the
# decaps, all on Metal1. MN0's source sets the tail current against MBt's: with a Metal4 lane and via stacks, about 30 Ohm
# under the 0.3 mA of the rows raised the tail current by 3 %.
vss = top.rect("Metal1", X_VSS - 0.5, Y_VSS_RAIL[0], 34.0, Y_VSS_RAIL[1])
y_vss = (Y_VSS_PIN[0] + Y_VSS_PIN[1]) / 2
top.rect("Metal2", X_VSS - 0.3, y_vss, X_VSS + 0.3, max(s.top for s in cap_s))
top.via(X_VSS, y_vss, "Metal1", "Metal2", cols=1, rows=2)
top.rect("Metal1", X_LANE - 0.25, vss.top - 0.1, X_LANE + 0.25, y_bot + 0.6)
top.rect("Metal1", X_LANE - 0.25, y_bot, x_left + 0.1, y_bot + 0.6)


# The decaps, the Metal5 plate on the rail below them, the TopMetal1 plate on a strap up to the vbg_buf track
def decap(x, y, h, xs_vss, x_vbg):
    w, l = x[1] - x[0] - 2 * MIM_ENC, h - 2 * MIM_ENC
    cell = top.pcell("cmim", Calculate="C", w=vl.um(w), l=vl.um(l))
    tc = top.add(cell, x[0] + MIM_ENC, y + MIM_ENC)
    m5 = top.shapes(cell, tc, "Metal5")[0]
    tm1 = top.shapes(cell, tc, "TopMetal1")[0]
    for xv in xs_vss:
        top.via(xv, y_vss, "Metal1", "Metal5", cols=2, rows=1)
        top.rect("Metal5", xv - 0.35, y_vss - 0.2, xv + 0.35, m5.bottom + 0.1)
    top.rect("TopMetal1", x_vbg - 1.05, tm1.top - 0.1, x_vbg + 1.05, TY["vbg_buf"] + 1.05)
    top.via(x_vbg, TY["vbg_buf"], "Metal3", "TopMetal1", cols=2, rows=1, tcols=2, trows=2)
    print(f"cmim w {w:.2f} um, l {l:.2f} um")


decap(X_CG1, Y_DECAP, Y_DECAP_TOP - Y_DECAP, (3.0, 10.5, 18.0), 10.5)
# Cg2's strap passes over the rows left of the tap band's center: Magic would give its sub! label to the strap's net
decap(X_CG2, Y_DECAP, y_bot - 1.6 - Y_DECAP, (25.0, 33.0), 26.0)

# Rg stands beside the rows, its body along y, its bottom head on nbg, its top head on vbg_int
rg = top.pcell("rppd", Calculate="R", w=vl.um(0.5), l=vl.um(8.5), b=0)
rb = rg.dbbox()
trg = top.add(rg, 22.25 - rb.center().x, y_bot - 1.25 - rb.bottom)  # its lower head 0.35 um above Cg2
rg_bot, rg_top = sorted(top.shapes(rg, trg, "Metal1"), key=lambda h: h.bottom)
add_stub("nbg", ("Metal1", rg_bot), rg_bot.center().x)
add_stub("vbg_int", ("Metal1", rg_top), rg_top.center().x)

# Rn and Rf: the left heads on the capacitors' gate columns, the right heads on Metal4 risers to the rows
for name, x_0, yc in (("Rn", 0.0, Y_RN), ("Rf", 2.0, Y_RF)):
    cell = top.pcell("rhigh", Calculate="R", w=vl.um(0.5), l=vl.um(RES_L), b=0)
    t = top.add(cell, x_0, yc + 0.25, rot=270)
    left, right = sorted(top.shapes(cell, t, "Metal1"), key=lambda h: h.left)
    top.via(right.center().x, yc, "Metal1", "Metal2", cols=1, rows=1)
    xr = X_RISE_I if name == "Rn" else X_RISE_G
    top.rect("Metal2", right.center().x, yc - 0.15, xr + 0.15, yc + 0.15)
    top.via(xr, yc, "Metal2", "Metal4")
    if name == "Rn":
        # vbn_buf: a Metal2 stub up over the VSS rail, a Metal3 jog to the column
        vl.stub(top, ("Metal1", left), left.center().x, Y_JOG)
        top.rect("Metal3", X_VBN - 0.4, Y_JOG - 0.15, left.center().x + 0.3, Y_JOG + 0.15)
        top.via(X_VBN, Y_JOG, "Metal3", "Metal4", cols=2, rows=1)
    else:
        # vbg_buf: Metal2 under Rn to the column
        top.via(left.center().x, yc, "Metal1", "Metal2", cols=1, rows=1)
        top.rect("Metal2", X_VBG - 0.15, yc - 0.15, left.center().x + 0.15, yc + 0.15)
        top.via(X_VBG, yc, "Metal2", "Metal4")

# The risers: Rn to ibias_100u, on its row track and its band track, Rf to vbg_int
top.rect("Metal4", X_RISE_I - 0.15, Y_RN - 0.15, X_RISE_I + 0.15, BAND["ibias_100u"] + 0.15)
top.rect("Metal4", X_RISE_G - 0.15, Y_RF - 0.15, X_RISE_G + 0.15, TY["vbg_int"] + 0.15)
xj_i, xj_g = X_RISE_I - 0.15, X_RISE_G + 0.15  # their two-cut joints grow away from each other
top.via(xj_i, TY["ibias_100u"], "Metal3", "Metal4", cols=2, rows=1)
top.via(xj_i, BAND["ibias_100u"], "Metal3", "Metal4", cols=2, rows=1)
top.via(xj_g, TY["vbg_int"], "Metal3", "Metal4", cols=2, rows=1)
xs["vbg_int"].append(xj_g)

# Gate columns of the capacitors, down to their band tracks and on to the resistors
top.rect("Metal4", X_VBN - 0.15, Y_JOG - 0.15, X_VBN + 0.15, max(g.top for g in cap_g["vbn_buf"]))
top.via(X_VBN, BAND["vbn_buf"], "Metal3", "Metal4", cols=2, rows=1)
top.rect("Metal4", X_VBG - 0.15, Y_RF - 0.15, X_VBG + 0.15, max(g.top for g in cap_g["vbg_buf"]))
top.via(X_VBG, BAND["vbg_buf"], "Metal3", "Metal4", cols=2, rows=1)

# Tracks, and the pins: inputs on the left end, outputs on the right end of their track
EXT = 0.4  # past the last joint's center: half a two-cut via plus the endcap
for net in ROW_TRACKS:
    vl.track(top, TY[net], xs[net] + ([xj_i] if net == "ibias_100u" else []), w=TRACK_W, ext=EXT)
# ibias_100u's second track, in the band from the input pin to the riser
xs["di_en"].append(X_LEFT)
tr_di = vl.track(top, BAND["di_en"], xs["di_en"], w=TRACK_W, ext=0.0)
top.rect("Metal3", tr_di.right - 0.1, tr_di.bottom, tr_di.right + EXT, tr_di.top)
top.pin("Metal3", "di_en", pya.DBox(tr_di.left, tr_di.bottom, tr_di.left + 1.0, tr_di.top))
tr_ib = top.rect("Metal3", X_LEFT, BAND["ibias_100u"] - TRACK_W / 2, xj_i + EXT, BAND["ibias_100u"] + TRACK_W / 2)
top.pin("Metal3", "ibias_100u", pya.DBox(tr_ib.left, tr_ib.bottom, tr_ib.left + 1.0, tr_ib.top))
for net, xc in (("vbn_buf", X_VBN), ("vbg_buf", X_VBG)):
    tr = top.rect("Metal3", xc - EXT, BAND[net] - TRACK_W / 2, X_RIGHT, BAND[net] + TRACK_W / 2)
    top.pin("Metal3", net, pya.DBox(tr.right - 1.0, tr.bottom, tr.right, tr.top))
top.pin("Metal1", "VSS", pya.DBox(vss.left, Y_VSS_PIN[0], vss.left + 2.0, Y_VSS_PIN[1]))
top.pin("Metal1", "VDD", pya.DBox(vdd.left, vdd.bottom, vdd.left + 2.0, vdd.top))

# Two stubs of different nets on the same layer must not touch: same span in y and less than 0.6 um apart in x
for i, (na, la, xa, a0, a1) in enumerate(stubs):
    for nb, lb, xb_, b0, b1 in stubs[i + 1:]:
        if na != nb and la == lb and abs(xa - xb_) < 0.6 and a0 < b1 + 0.3 and b0 < a1 + 0.3:
            raise RuntimeError(f"vco_bias.py: stubs of {na} and {nb} collide at x = {xa:.2f} and {xb_:.2f}")

vl.write(top, vl.out_path("vco_bias", __file__))
# ==============================================================================
