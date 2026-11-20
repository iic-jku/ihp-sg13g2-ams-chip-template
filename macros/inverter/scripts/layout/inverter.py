# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the inverter unit cell layout/inverter.gds.
# ============================================
#
# Usage: klayout -b -r scripts/layout/inverter.py [-rd out=<file.gds>], or make klayout-script CELL=inverter
#
# Draws the same cell as the hand-drawn layout. The nmos row (M1) sits below the pmos row (M2), each one SG13_dev PCell
# whose outer fingers are the dummies Mdummy1 and Mdummy2. The VSS rail runs below and the VDD rail above the rows, on
# Metal1 to Metal3. Sources and dummies reach their rail on Metal1 and Metal2, the drains rise to Metal3 combs joined by
# the vout bar between the rows, and the gates join on two poly straps that Metal2 risers tie to the vin bar.
# The PCells stay live, so the file opens editable in KLayout. inverter_top.py imports this file for build().

import importlib
import os
import sys

import pya

TECH = "sg13g2"
LAYERS = {
    "Activ": (1, 0), "GatPoly": (5, 0), "NWell": (31, 0), "Metal1": (8, 0), "Metal2": (10, 0), "Metal3": (30, 0),
    "Metal4": (50, 0), "Metal5": (67, 0), "TopMetal1": (126, 0), "prBoundary": (189, 0),
}
PIN_DT, TEXT_DT = 2, 25

# Device sizes, identical to schematic/xschem/inverter.sch. Each PCell holds M1 or M2 (NG fingers) and its dummy (one
# finger at each end), so it has NG + 2 fingers and NG + 3 source and drain stripes.
NG = 20
L = 1.0
WF_N, WF_P = 1.0, 6.0  # finger widths of the nmos and the pmos in um

# Floorplan in um
CELL_W, CELL_H = 33.38, 15.28  # the outline inverter_top.py stacks the cells on
X_DEV = 1.36  # left edge of both active areas
Y_N, Y_P = 2.69, 6.77  # bottom edges of the nmos and the pmos active area
RAIL_H = 1.5  # height of the VSS and VDD rails
RAIL_INSET = 0.35  # the rails end this far inside the outline
W_M2 = 0.21  # width of the Metal1 and Metal2 strips over the gate contact rows and of the Metal2 risers to the vin bar
STRIP_INSET = 0.39  # those strips end this far inside their poly strap
VIN_H, VOUT_H = 1.0, 1.5  # heights of the vin bar (Metal2) and the vout bar (Metal3)
W_COMB = 1.0  # width of the Metal3 combs over the drains
PIN_SIGNAL = 0.4  # vin and vout pins: squares at the outer end of their bar
# Contacts and vias per row, as drawn: the rail stacks, the gate straps, the dummy gates
RAIL_VIAS = (78, 3)
GATE_CONTS, GATE_VIAS, DUMMY_CONTS = 78, 64, 3
# As drawn: the 1 um supply pins sit 10 nm off the centre lines, and the pmos drain via stacks right of the centre
# 0.19 um higher than the ones left of it
PINS_SUPPLY = {"VSS": (16.69, 0.76), "VDD": (16.70, 14.53)}
DY_DRAIN_RIGHT = 0.19


def load_pdk():
    # Batch mode does not run the PDK's autorun macros, so register the SG13_dev library here
    kl = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], "libs.tech", "klayout", "python")
    for d in (kl, os.path.join(kl, "pycell4klayout-api", "source", "python")):
        if d not in sys.path:
            sys.path.append(d)
    if pya.Library.library_by_name("SG13_dev", TECH) is None:
        importlib.import_module(f"{TECH}_pycell_lib")


def new_layout():
    load_pdk()
    ly = pya.Layout()
    ly.dbu = 0.001
    ly.technology_name = TECH
    return ly


def um(v):
    return f"{v:.1f}u"


def rect(cell, layer, x1, y1, x2, y2):
    box = pya.DBox(round(min(x1, x2), 3), round(min(y1, y2), 3), round(max(x1, x2), 3), round(max(y1, y2), 3))
    cell.shapes(cell.layout().layer(*LAYERS[layer])).insert(box)
    return box


def pin(cell, layer, name, box):
    """A pin shape and its label at the box centre."""
    lay, _ = LAYERS[layer]
    cell.shapes(cell.layout().layer(lay, PIN_DT)).insert(box)
    cell.shapes(cell.layout().layer(lay, TEXT_DT)).insert(pya.DText(name, box.center().x, box.center().y))


def pcell(cell, name, x, y, lib="SG13_dev", **params):
    """Places a PDK PCell at (x, y). Returns the PCell and its transformation."""
    pc = cell.layout().create_cell(name, lib, params)
    if pc is None:
        raise RuntimeError(f"inverter: PCell {name} not found in {lib}")
    t = pya.DTrans(round(x, 3), round(y, 3))
    cell.insert(pya.DCellInstArray(pc.cell_index(), t))
    return pc, t


def via(cell, x, y, bottom, top, cols=1, rows=1, **cuts):
    """A via_stack centred at (x, y). Returns the box of its bottom layer."""
    pc, t = pcell(cell, "via_stack", x, y, b_layer=bottom, t_layer=top, vn_columns=cols, vn_rows=rows, **cuts)
    li = cell.layout().layer(*LAYERS[bottom])
    return t * pya.Region(pc.begin_shapes_rec(li)).bbox().to_dtype(cell.layout().dbu)


def device(cell, kind, wf, y, ring, ring_distance):
    """Places the nmos or pmos PCell with its active area at (X_DEV, y). Returns the active area, the x of every source
    and drain stripe, and the gate fingers, in cell coordinates."""
    ng = NG + 2
    pc, t = pcell(cell, kind, X_DEV, y, model=f"sg13_lv_{kind}", w=um(wf * ng), l=um(L), ng=str(ng),
                  guardRingType=ring, guardRingDistance=ring_distance)
    dbu = cell.layout().dbu

    def boxes(layer):
        r = pya.Region(pc.begin_shapes_rec(cell.layout().layer(*LAYERS[layer]))).merged()
        return sorted((t * p.bbox().to_dtype(dbu) for p in r.each() if p.is_box()), key=lambda b: b.left)

    act = [b for b in boxes("Activ") if abs(b.height() - wf) < 1e-6][0]
    xs = [b.center().x for b in boxes("Metal1") if b.bottom >= act.bottom - 1e-6 and b.top <= act.top + 1e-6]
    gates = boxes("GatPoly")
    if len(xs) != ng + 1 or len(gates) != ng:
        raise RuntimeError(f"inverter: {kind} has {len(xs)} stripes and {len(gates)} gates, expected {ng + 1} and {ng}")
    return act, xs, gates


def build(ly):
    """Draws the unit cell into ly. Returns the cell and the positions inverter_top.py connects to."""
    cell = ly.create_cell("inverter")
    rails = {"VSS": (0.0, RAIL_H), "VDD": (CELL_H - RAIL_H, CELL_H)}
    y_mid = (Y_N + WF_N + Y_P) / 2  # the vin and vout bars run halfway between the active areas
    src = range(3, NG, 2)  # sources apart from the two stripes each device shares with its dummy
    drn = range(2, NG + 1, 2)

    y_gate, stripes = {}, {}
    for kind, wf, y, ring, dist, rail_y in (("nmos", WF_N, Y_N, "psub", "1.01um", RAIL_H),
                                           ("pmos", WF_P, Y_P, "nwell", "0.7u", CELL_H - RAIL_H)):
        act, xs, gates = device(cell, kind, wf, y, ring, dist)
        stripes[kind] = xs
        y0, y1, yc = act.bottom, act.top, act.center().y
        span = (min(y0, rail_y), max(y1, rail_y))  # from the rail over the whole finger
        n = int((act.height() + 0.12) / 0.41)  # Via1 rows on a finger: 0.19 um cuts, 0.41 um pitch, 0.05 um enclosure

        # Every stripe gets a via stack and is widened to its pad over the full finger. The outer dummy stripes and the
        # stripes the dummies share with the device lie in one block of Metal1 and Metal2 that reaches the rail, the
        # sources run on to the rail as well, and the drains rise to Metal3.
        for k in (0, NG + 2):
            via(cell, xs[k], yc, "Metal1", "Metal2", cols=2, rows=n)
        for k in (1, NG + 1):
            pad = via(cell, xs[k], yc, "Metal1", "Metal2", cols=1, rows=n)
            x0, x1 = (RAIL_INSET, pad.right) if k == 1 else (pad.left, CELL_W - RAIL_INSET)
            for layer in ("Metal1", "Metal2"):
                rect(cell, layer, x0, span[0], x1, span[1])
        for k in src:
            pad = via(cell, xs[k], yc, "Metal1", "Metal2", cols=2, rows=n)
            for layer in ("Metal1", "Metal2"):
                rect(cell, layer, pad.left, span[0], pad.right, span[1])
        for k in drn:
            dy = DY_DRAIN_RIGHT if kind == "pmos" and xs[k] > CELL_W / 2 else 0.0
            pad = via(cell, xs[k], yc + dy, "Metal1", "Metal3", cols=2, rows=n)
            for layer in ("Metal1", "Metal2"):
                rect(cell, layer, pad.left, y0, pad.right, y1)

        # Gates: poly straps 0.18 um to 0.48 um past the active area with a contact row in the middle, the NG active
        # fingers towards the other row, each dummy finger towards the rail
        yg = y1 + 0.33 if kind == "nmos" else y0 - 0.33
        yd = y0 - 0.33 if kind == "nmos" else y1 + 0.33
        g0, g1 = gates[1].left, gates[NG].right
        rect(cell, "GatPoly", g0, yg - 0.15, g1, yg + 0.15)
        via(cell, (g0 + g1) / 2, yg, "GatPoly", "Metal1", cols=GATE_CONTS)
        via(cell, (g0 + g1) / 2, yg, "Metal1", "Metal2", cols=GATE_VIAS)
        for layer in ("Metal1", "Metal2"):
            rect(cell, layer, g0 + STRIP_INSET, yg - W_M2 / 2, g1 - STRIP_INSET, yg + W_M2 / 2)
        for g in (gates[0], gates[NG + 1]):
            rect(cell, "GatPoly", g.left, yd - 0.15, g.right, yd + 0.15)
            via(cell, g.center().x, yd, "GatPoly", "Metal2", cols=DUMMY_CONTS)
        y_gate[kind] = yg

    # The combs and risers below run over both rows, so their stripes have to line up
    xs = stripes["nmos"]
    if any(abs(a - b) > 1e-6 for a, b in zip(xs, stripes["pmos"])):
        raise RuntimeError("inverter: the nmos and pmos stripes do not line up")

    # vin: Metal2 risers from one gate strap to the other at every stripe between the outer drains, and a bar across
    for k in range(2, NG + 1):
        rect(cell, "Metal2", xs[k] - W_M2 / 2, y_gate["nmos"] + 0.1, xs[k] + W_M2 / 2, y_gate["pmos"] - 0.1)
    vin = rect(cell, "Metal2", xs[2] - W_M2 / 2, y_mid - VIN_H / 2, xs[NG] + W_M2 / 2, y_mid + VIN_H / 2)
    p = PIN_SIGNAL / 2
    pin(cell, "Metal2", "vin", pya.DBox(vin.left, y_mid - p, vin.left + PIN_SIGNAL, y_mid + p))

    # vout: Metal3 combs over the drains of both rows, and the bar across them
    for k in drn:
        rect(cell, "Metal3", xs[k] - W_COMB / 2, Y_N, xs[k] + W_COMB / 2, Y_P + WF_P)
    vout = rect(cell, "Metal3", xs[2] - W_COMB / 2, y_mid - VOUT_H / 2, xs[NG] + W_COMB / 2, y_mid + VOUT_H / 2)
    pin(cell, "Metal3", "vout", pya.DBox(vout.right - PIN_SIGNAL, y_mid - p, vout.right, y_mid + p))

    # Rails on Metal1 to Metal3, stacked in the middle, pins on Metal3
    for name, (r0, r1) in rails.items():
        for layer in ("Metal1", "Metal2", "Metal3"):
            rect(cell, layer, RAIL_INSET, r0, CELL_W - RAIL_INSET, r1)
        via(cell, CELL_W / 2, (r0 + r1) / 2, "Metal1", "Metal3", cols=RAIL_VIAS[0], rows=RAIL_VIAS[1])
        x, y = PINS_SUPPLY[name]
        pin(cell, "Metal3", name, pya.DBox(x - 0.5, y - 0.5, x + 0.5, y + 0.5))

    return cell, {"rails": rails, "rail_x": (RAIL_INSET, CELL_W - RAIL_INSET), "vin": vin, "vout": vout}


def save_options(context=True):
    opt = pya.SaveLayoutOptions()
    opt.write_context_info = context  # False writes every PCell as a plain cell, as File > Export Layout For Tapeout
    opt.gds2_write_timestamps = False  # a rerun writes the same bytes
    return opt


def out_path(name):
    """The -rd out=... path of the batch call, or layout/<name>.gds next to the scripts folder."""
    out = sys.modules["__main__"].__dict__.get("out")
    here = os.path.dirname(os.path.abspath(__file__))
    return out if isinstance(out, str) else os.path.join(here, "..", "..", "layout", f"{name}.gds")


if __name__ == "__main__":
    ly = new_layout()
    cell, _ = build(ly)
    path = out_path("inverter")
    ly.write(path, save_options())
    print(f"inverter: wrote {os.path.normpath(path)}, bbox {cell.dbbox()}")
# ==============================================================================
