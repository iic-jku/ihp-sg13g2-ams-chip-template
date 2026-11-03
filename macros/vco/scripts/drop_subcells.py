# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Write a cell without the instances of some of its subcells, with a port label where each of their pins lands.
"""The post-layout testbench simulates some subcells by a model of their own, the coil by its EM model and the varactor
array by its schematic, and the extraction has to leave them out. Dropping them alone would put the models at the
cell's pins, away from where they connect, so every pin of a dropped instance becomes a pin of the cell, named
<subcell>_<pin>: a pin shape and its label where the pin overlaps the metal it lands on. Magic keeps such a label as
a port of its own and extracts the resistance between it and the other ports of the net.

    python3 scripts/drop_subcells.py layout/vco_top.gds vco_top netlist/pex/vco_top_leads.gds \\
        --drop vco_ind vco_var --skip vco_var_vtune vco_ind_VSS --name vco_top_leads

The instances are searched at every depth. Without --drop every subcell of the cell is dropped. Magic builds no
resistor network on some nets, one that carries no current or one whose only devices are capacitors, and then keeps
only one of its ports, the others left unconnected. --ties writes, for every added pin, the other pins on its net, from
the metal connectivity of the written layout, and pex_caps.py joins such a port to them. --skip names pins that get no
port at all, a pin the model has no terminal for, or one that carries no current.
"""

import argparse
import json
import sys

try:
    import klayout.db as kdb
except ImportError:
    import pya as kdb

METALS = {"Metal1": 8, "Metal2": 10, "Metal3": 30, "Metal4": 50, "Metal5": 67, "TopMetal1": 126, "TopMetal2": 134}
VIAS = {"Via1": 19, "Via2": 29, "Via3": 49, "Via4": 66, "TopVia1": 125, "TopVia2": 133}
PIN_DT, TEXT_DT = 2, 25
REACH = 0.5  # um around a pin box searched for the metal it lands on


def net_ids(ly, top, points):
    """For (name, metal, DPoint) triples, an id per name that is equal for points on one net, through the metal stack.
    TopVia1 lands on Metal5 where the layout has Metal5 (ihp-sg13g2), on Metal4 otherwise (ihp-sg13cmos5l)."""
    flat = kdb.Layout()
    flat.assign(ly)
    cell = flat.cell(top.name)
    cell.flatten(True)
    l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(flat, cell, []))
    m5 = flat.find_layer(METALS["Metal5"], 0)
    has_m5 = m5 is not None and not cell.shapes(m5).is_empty()
    chain = ["Metal1", "Via1", "Metal2", "Via2", "Metal3", "Via3", "Metal4"]
    chain += (["Via4", "Metal5"] if has_m5 else []) + ["TopVia1", "TopMetal1", "TopVia2", "TopMetal2"]
    regions = {}
    for name in chain:
        lay = METALS.get(name, VIAS.get(name))
        regions[name] = l2n.make_layer(flat.layer(lay, 0), name)
        l2n.connect(regions[name])
    for a, b in zip(chain, chain[1:]):
        l2n.connect(regions[a], regions[b])
    l2n.extract_netlist()
    ids = {}
    for name, metal, pt in points:
        net = l2n.probe_net(regions[metal], pt)
        ids[name] = None if net is None else net.cluster_id
    return ids


def cell_pins(ly, cell):
    """{label: [(metal, Box)]} from the cell's own pin shapes and the labels on them."""
    pins = {}
    for metal, lay in METALS.items():
        pli, tli = ly.find_layer(lay, PIN_DT), ly.find_layer(lay, TEXT_DT)
        if pli is None or tli is None:
            continue
        boxes = [p.bbox() for p in kdb.Region(cell.shapes(pli)).merged().each()]
        for s in cell.shapes(tli).each():
            if s.is_text():
                pt = s.text.trans.disp.to_p()
                for b in boxes:
                    if b.contains(pt):
                        pins.setdefault(s.text_string, []).append((metal, b))
    return pins


def find_instances(ly, cell, names, trans, found):
    """Instances of the cells in names below cell, with their transformation into the top cell's coordinates."""
    for inst in list(cell.each_inst()):
        sub = ly.cell(inst.cell_index)
        if inst.is_regular_array():
            sys.exit(f"drop_subcells.py: instance array of {sub.name} in {cell.name} is not supported")
        t = trans * inst.cplx_trans
        if names is None or sub.name in names:
            found.append((cell, inst, sub, t))
        elif names is not None:
            find_instances(ly, sub, names, t, found)


def main():
    parser = argparse.ArgumentParser(description="Write a cell without some of its subcells, with port labels where their pins land.")
    parser.add_argument("layout", help="input layout (GDS)")
    parser.add_argument("cell", help="cell to write")
    parser.add_argument("out", help="output layout (GDS)")
    parser.add_argument("--drop", nargs="+", help="subcells to drop, at any depth (default: every direct subcell)")
    parser.add_argument("--skip", nargs="+", default=[], help="pins of dropped cells that get no port, as <subcell>_<pin>")
    parser.add_argument("--name", help="name of the written cell (default: the cell's own)")
    parser.add_argument("--ties", help="JSON file: for every added pin, the other pins of the cell on its net")
    args = parser.parse_args()

    ly = kdb.Layout()
    ly.read(args.layout)
    top = ly.cell(args.cell)
    if top is None:
        sys.exit(f"drop_subcells.py: no cell {args.cell} in {args.layout}")

    found = []
    find_instances(ly, top, set(args.drop) if args.drop else None, kdb.ICplxTrans(), found)
    missing = set(args.drop or []) - {sub.name for _, _, sub, _ in found}
    if missing:
        sys.exit(f"drop_subcells.py: no instance of {', '.join(sorted(missing))} below {args.cell}")
    ports, names = [], set()
    for parent, inst, sub, t in found:
        for name, boxes in cell_pins(ly, sub).items():
            names.add(f"{sub.name}_{name}")
            if f"{sub.name}_{name}" not in args.skip:
                ports.append((f"{sub.name}_{name}", [(metal, b.transformed(t)) for metal, b in boxes]))
        inst.delete()
    unknown = set(args.skip) - names
    if unknown:
        sys.exit(f"drop_subcells.py: --skip names no pin of a dropped cell: {', '.join(sorted(unknown))}")

    points = [(name, metal, b.to_dtype(ly.dbu).center()) for name, pins in cell_pins(ly, top).items() for metal, b in pins[:1]]
    for name, boxes in ports:
        land = []
        for metal, b in boxes:
            li = ly.find_layer(METALS[metal], 0)
            if li is None:
                continue
            reach = kdb.Region(b.enlarged(round(REACH / ly.dbu), round(REACH / ly.dbu)))
            land += [(metal, p) for p in (kdb.Region(top.begin_shapes_rec(li)) & reach).merged().each()]
        if not land:
            sys.exit(f"drop_subcells.py: pin {name} lands on no metal of {args.cell}")
        metal, p = max(land, key=lambda m: m[1].area())
        pt = max(p.decompose_trapezoids(), key=lambda q: q.area()).bbox().center()
        if not p.inside(pt):
            sys.exit(f"drop_subcells.py: no label point inside the landing of pin {name}")
        top.shapes(ly.layer(METALS[metal], PIN_DT)).insert(p)
        top.shapes(ly.layer(METALS[metal], TEXT_DT)).insert(kdb.Text(name, kdb.Trans(pt)))
        points.append((name, metal, pt.to_dtype(ly.dbu)))

    if args.ties:
        ids = net_ids(ly, top, points)
        added = {name for name, _ in ports}
        ties = {a: [b for b in ids if b != a and ids[b] is not None and ids[b] == ids[a]] for a in sorted(added)}
        with open(args.ties, "w", encoding="utf-8") as f:
            json.dump(ties, f, indent=1)
    if args.name:
        top.name = args.name
    opt = kdb.SaveLayoutOptions()
    opt.select_cell(top.cell_index())
    opt.write_context_info = False
    opt.gds2_write_timestamps = False
    ly.write(args.out, opt)
    dropped = ", ".join(sorted({sub.name for _, _, sub, _ in found})) or "no subcells"
    print(f"drop_subcells.py: wrote {top.name} without {dropped}, {len(ports)} pins added, to {args.out}")


if __name__ == "__main__":
    main()
