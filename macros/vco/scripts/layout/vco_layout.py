# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Helpers shared by the KLayout layout scripts of the vco macro: PDK cells, blocks with ports, vias, metal, pins.
# ============================================
#
# Coordinates are in um. A Block is a cell built from PDK PCells and shapes, with named ports (layer, box) that move with
# it when it is placed in another block. write() flattens the cell, so its GDS holds plain shapes and no PCell context,
# and cells read from several GDS files cannot clash by name.

import importlib
import os
import sys

import pya

LAYERS = {
    "Activ": (1, 0), "GatPoly": (5, 0), "Cont": (6, 0), "pSD": (14, 0), "NWell": (31, 0),
    "Metal1": (8, 0), "Metal2": (10, 0), "Metal3": (30, 0), "Metal4": (50, 0), "Metal5": (67, 0),
    "TopMetal1": (126, 0), "TopMetal2": (134, 0), "prBoundary": (189, 0),
}
METALS = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5", "TopMetal1", "TopMetal2"]
PIN_DT, TEXT_DT = 2, 25
GRID = 0.005  # manufacturing grid in um


def snap(v):
    return round(v / GRID) * GRID


def load_pdk():
    # Batch mode does not run the PDK's autorun macros, so register the SG13_dev library here
    kl = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], "libs.tech", "klayout", "python")
    for d in (kl, os.path.join(kl, "pycell4klayout-api", "source", "python")):
        if d not in sys.path:
            sys.path.append(d)
    if pya.Library.library_by_name("SG13_dev", "sg13g2") is None:
        importlib.import_module("sg13g2_pycell_lib")


def new_layout():
    load_pdk()
    ly = pya.Layout()
    ly.dbu = 0.001
    ly.technology_name = "sg13g2"
    return ly


def um(v):
    return f"{v:.4g}u"


class Block:
    """A cell with named ports. Ports are (layer, DBox) in the block's own coordinates."""

    def __init__(self, ly, name):
        self.ly = ly
        self.cell = ly.create_cell(name)
        self.ports = {}

    def li(self, layer):
        return self.ly.layer(*LAYERS[layer])

    def pcell(self, name, **params):
        cell = self.ly.create_cell(name, "SG13_dev", params)
        if cell is None:
            raise RuntimeError(f"vco_layout: PCell {name} not found in SG13_dev")
        return cell

    def add(self, cell, x=0.0, y=0.0, rot=0, mirror=False):
        t = pya.DCplxTrans(1.0, rot, mirror, snap(x), snap(y))
        self.cell.insert(pya.DCellInstArray(cell.cell_index(), t))
        return t

    def rect(self, layer, x1, y1, x2, y2):
        box = pya.DBox(snap(min(x1, x2)), snap(min(y1, y2)), snap(max(x1, x2)), snap(max(y1, y2)))
        self.cell.shapes(self.li(layer)).insert(box)
        return box

    def shapes(self, cell, t, layer):
        """Merged boxes of one layer of a placed cell, in this block's coordinates, sorted by x then y."""
        r = pya.Region(cell.begin_shapes_rec(self.li(layer))).merged()
        boxes = [t * p.bbox().to_dtype(self.ly.dbu) for p in r.each()]
        return sorted(boxes, key=lambda b: (round(b.left, 3), round(b.bottom, 3)))

    def via(self, x, y, bottom, top, cols=1, rows=1, tcols=1, trows=1):
        """A PDK via_stack centered at (x, y). Returns the boxes of its bottom and top layer."""
        cell = self.pcell("via_stack", b_layer=bottom, t_layer=top, vn_columns=cols, vn_rows=rows,
                          vt1_columns=tcols, vt1_rows=trows, vt2_columns=tcols, vt2_rows=trows)
        t = self.add(cell, x, y)
        return self.shapes(cell, t, bottom)[0], self.shapes(cell, t, top)[0]

    def place(self, block, x=0.0, y=0.0, rot=0, mirror=False):
        """Places a block and returns its ports in this block's coordinates."""
        t = self.add(block.cell, x, y, rot, mirror)
        return {k: (layer, t * box) for k, (layer, box) in block.ports.items()}

    def pin(self, layer, name, box):
        """A pin shape and its label at the box center, the convention of the template's macros."""
        lay, _ = LAYERS[layer]
        self.cell.shapes(self.ly.layer(lay, PIN_DT)).insert(box)
        self.label(layer, name, box.center().x, box.center().y)

    def label(self, layer, name, x, y):
        lay, _ = LAYERS[layer]
        self.cell.shapes(self.ly.layer(lay, TEXT_DT)).insert(pya.DText(name, x, y))

    def bbox(self):
        return self.cell.dbbox()


def read_cell(ly, name, script):
    """Reads layout/<name>.gds, written by the cell's own script, and returns its cell."""
    path = os.path.join(os.path.dirname(os.path.abspath(script)), "..", "..", "layout", f"{name}.gds")
    ly.read(path)
    cell = ly.cell(name)
    if cell is None:
        raise RuntimeError(f"vco_layout: no cell {name} in {path}, run its layout script first")
    return cell


def cell_pins(ly, cell, t):
    """The pins of a placed cell: {label: (metal, DBox)} from its own pin shapes and the labels on them.
    Subcells are not searched, their pins of the same name are not the cell's."""
    pins = {}
    for metal in METALS:
        lay, _ = LAYERS[metal]
        boxes = [p.bbox() for p in pya.Region(cell.shapes(ly.layer(lay, PIN_DT))).merged().each()]
        for s in cell.shapes(ly.layer(lay, TEXT_DT)).each():
            if s.is_text():
                pt = s.text.trans.disp.to_p()
                for b in boxes:
                    if b.contains(pt):
                        pins[s.text_string] = (metal, t * b.to_dtype(ly.dbu))
    return pins


def write(block, path, drop_texts=(), keep=()):
    """Flattens the block, except instances of the cells named in keep, and writes it alone without PCell context.

    drop_texts: terminal names a PCell writes on TEXT 63/0. KLayout LVS names a net after them, and a net with a second
    name fails the strict port check, so they go once the cell is flat. Device recognition texts stay.
    """
    for inst in list(block.cell.each_inst()):
        if inst.cell.name not in keep:
            inst.flatten(-1)
    texts = block.cell.shapes(block.ly.layer(63, 0))
    for s in [s for s in texts.each() if s.is_text() and s.text_string in drop_texts]:
        texts.erase(s)
    # ntap1 also writes "well" on the NWell drawing layer, which Magic, and so KPEX, turns into a dangling port.
    # KLayout LVS reads the tap labels from TEXT 63/0 only.
    nwell = block.cell.shapes(block.ly.layer(*LAYERS["NWell"]))
    for s in [s for s in nwell.each() if s.is_text()]:
        nwell.erase(s)
    opt = pya.SaveLayoutOptions()
    opt.write_context_info = False
    opt.gds2_write_timestamps = False  # a rerun with the same geometry writes the same bytes
    opt.select_cell(block.cell.cell_index())
    block.ly.write(path, opt)
    print(f"{block.cell.name}: wrote {os.path.normpath(path)}, bbox {block.cell.dbbox()}")


def out_path(name, script):
    """The -rd out=... path of the batch call, or layout/<name>.gds next to the scripts folder."""
    out = sys.modules["__main__"].__dict__.get("out")
    return out if isinstance(out, str) else os.path.join(os.path.dirname(os.path.abspath(script)), "..", "..", "layout", f"{name}.gds")


def mos(ly, name, kind, w, l, ng, tap=None, d_metal="Metal2", gext=1.0):
    """A MOSFET with its wiring: gate contacts on a poly strap below the fingers (port G, Metal1), sources up to a
    Metal1 rail above (port S), drains joined by a strap across the middle (port D, d_metal).

    tap: None, "merge" (substrate or well tap under the source rail, so S is also the body) or "separate"
    (a tap of its own above the source rail, port B). Even stripes are sources, odd ones drains.
    gext: how far the gate pad reaches left of the device, so a via on it clears the drain's via column.
    """
    b = Block(ly, name)
    model = "sg13_lv_nmos" if kind == "nmos" else "sg13_lv_pmos"
    dev = b.pcell(kind, model=model, w=um(w), l=um(l), ng=ng)
    t = b.add(dev)
    act = b.shapes(dev, t, "Activ")[0]
    stripes = [s for s in b.shapes(dev, t, "Metal1")]
    gates = b.shapes(dev, t, "GatPoly")
    wf = act.height()

    # Gate: a poly strap joins the finger ends below the active area, contacts on it, a Metal1 pad below them.
    # The contacts sit 0.25 um from the active area (Cnt.e 0.14) and the pad keeps 0.25 um from the drain stripes.
    gy1, gy0 = act.bottom - 0.18, act.bottom - 0.48
    b.rect("GatPoly", gates[0].left, gy0, gates[-1].right, gy1)
    glen = gates[-1].right - gates[0].left
    cols = max(1, int((glen - 0.14) / 0.34))
    b.via((gates[0].left + gates[-1].right) / 2, act.bottom - 0.33, "GatPoly", "Metal1", cols=cols, rows=1)
    gx0 = min(gates[0].left, (gates[0].left + gates[-1].right) / 2 - cols * 0.17)
    gx1 = max(gates[-1].right, (gates[0].left + gates[-1].right) / 2 + cols * 0.17)
    b.ports["G"] = ("Metal1", b.rect("Metal1", gx0 - gext, act.bottom - 0.85, gx1, act.bottom - 0.25))

    # Sources: every even stripe up to a Metal1 rail 0.25 um above the active area
    rail_y0, rail_y1 = act.top + 0.25, act.top + 0.85
    for s in stripes[0::2]:
        b.rect("Metal1", s.left, s.top, s.right, rail_y0)
    b.ports["S"] = ("Metal1", b.rect("Metal1", act.left, rail_y0, act.right, rail_y1))

    # Drains: a via column on every odd stripe and a strap across them, inside the active area's height
    rows = max(1, min(8, int((wf - 0.1 + 0.22) / 0.41)))
    dboxes = [b.via(s.center().x, act.center().y, "Metal1", d_metal, cols=1, rows=rows)[1] for s in stripes[1::2]]
    d = dboxes[0]
    for x in dboxes[1:]:
        d = d + x
    b.ports["D"] = (d_metal, b.rect(d_metal, d.left, d.bottom, d.right, d.top))

    # Tap: a ptap1 (nmos) or ntap1 (pmos) strip over the full device length
    if tap:
        ty0 = rail_y0 + 0.55 if tap == "merge" else rail_y1 + 0.45
        tcell = b.pcell("ptap1" if kind == "nmos" else "ntap1", w=um(act.width()), l=um(0.6))
        tt = b.add(tcell, act.left, ty0)
        tm1 = b.shapes(tcell, tt, "Metal1")[0]
        if tap == "merge":
            b.rect("Metal1", act.left, rail_y0, act.right, tm1.top)
            b.ports["S"] = ("Metal1", pya.DBox(act.left, rail_y0, act.right, tm1.top))
        else:
            b.ports["B"] = ("Metal1", tm1)
        if kind == "pmos":
            b.rect("NWell", act.left - 0.31, act.bottom - 0.31, act.right + 0.31, ty0 + 0.6 + 0.31)
    b.ports["ACT"] = ("Activ", act)
    return b


def stub(b, port, x, y, layer="Metal2", track="Metal3"):
    """Joins a Metal1 or Metal2 port at x to a horizontal track at height y: a vertical strip on layer from the port's
    center to y, with the vias at both ends. Returns x for sizing the track."""
    player, box = port
    yp = box.center().y
    if player == "Metal1":
        b.via(x, yp, "Metal1", layer)
    elif player != layer:
        raise RuntimeError(f"stub: port on {player}, expected Metal1 or {layer}")
    b.rect(layer, x - 0.15, min(yp, y) - 0.1, x + 0.15, max(yp, y) + 0.1)
    b.via(x, y, *sorted((layer, track), key=METALS.index))
    return x


def track(b, y, xs, layer="Metal3", w=0.4, ext=0.3):
    """A horizontal track at height y over all x in xs."""
    return b.rect(layer, min(xs) - ext, y - w / 2, max(xs) + ext, y + w / 2)

