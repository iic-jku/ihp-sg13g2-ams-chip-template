# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: KLayout batch script that writes the quad inverter layout/inverter_top.gds and its editing source.
# ============================================
#
# Usage: klayout -b -r scripts/layout/inverter_top.py [-rd out=<file.gds>], or make klayout-script CELL=inverter_top
# Needs layout/inverter.gds, written by inverter.py, in the folder of the output file.
#
# Draws the same macro as the hand-drawn layout and writes it twice: inverter_top.klay.gds pulls the unit cell in as the
# KLayout library "inverter" that inverter_top.klay.klib maps to inverter.gds, so every device stays editable, and
# inverter_top.gds is its static export (File > Export Layout For Tapeout), which every build and sign-off target reads.
# Four unit cells are stacked, every second one mirrored so that neighbours share a rail, inside a VSS ring (outer) and
# a VDD ring (inner) on Metal5 (horizontal bars) and TopMetal1 (vertical bars). The rails reach the vertical bars on
# Metal3, vin<n> leaves at the left edge on Metal2, vout<n> at the right edge on Metal3, and NWell straps bridge the
# facing pmos rows.

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pya  # noqa: E402
import inverter as unit  # noqa: E402

ROWS = 4
RING_W, RING_GAP = 2.2, 2.0  # width of a ring bar, gap between the two rings
MARGIN = 4.0  # from the inner ring to the unit cells
H_METAL, V_METAL = "Metal5", "TopMetal1"  # the horizontal and the vertical ring bars
X0 = 2 * RING_W + RING_GAP + MARGIN  # left and bottom edge of the unit cells
W_TOP, H_TOP = 2 * X0 + unit.CELL_W, 2 * X0 + ROWS * unit.CELL_H


def row_y(i, y):
    """The macro's y of a unit cell's y in row i: even rows upright, odd rows mirrored onto the row below."""
    return X0 + i * unit.CELL_H + y if i % 2 == 0 else X0 + (i + 1) * unit.CELL_H - y


out = unit.out_path("inverter_top")
unit_gds = os.path.join(os.path.dirname(out), "inverter.gds")
if not os.path.isfile(unit_gds):
    raise RuntimeError(f"inverter_top: {unit_gds} not found, run make klayout-script CELL=inverter first")

ly = unit.new_layout()
top = ly.create_cell("inverter_top")

# The positions the macro connects to, from a copy of the unit cell drawn in a scratch layout
_, iface = unit.build(unit.new_layout())

# The unit cell comes from inverter.gds as the KLayout library "inverter", as inverter_top.klay.klib maps it
lib = pya.Library()
lib.description = "inverter unit cell"
lib.layout().technology_name = unit.TECH
lib.layout().read(unit_gds)
lib.register("inverter")
ui = ly.add_lib_cell(lib, lib.layout().cell_by_name("inverter"))
for i in range(ROWS):
    t = pya.DTrans(pya.DTrans.R0 if i % 2 == 0 else pya.DTrans.M0, X0, X0 + (i + i % 2) * unit.CELL_H)
    top.insert(pya.DCellInstArray(ui, t))

# Rings: VSS outside, VDD inside, each ring bar a pin, a via array at every corner
ring_off = {"VSS": 0.0, "VDD": RING_W + RING_GAP}
for name, off in ring_off.items():
    l, b, r, t = off, off, W_TOP - off, H_TOP - off
    for y in (b, t - RING_W):
        unit.pin(top, H_METAL, name, unit.rect(top, H_METAL, l, y, r, y + RING_W))
    for x in (l, r - RING_W):
        unit.pin(top, V_METAL, name, unit.rect(top, V_METAL, x, b, x + RING_W, t))
        for y in (b, t - RING_W):
            unit.pcell(top, "Via", x + RING_W / 2, y + RING_W / 2, lib="SG13_native_pcell_lib",
                       via="SG13G2_VIA_M5_TM1", nx=2, ny=2)

# Rails: the rails of neighbouring rows merge into one strip, which Metal3 extends on both sides onto its ring's
# vertical bars, with a via stack on each bar, two Via3 and Via4 rows and one TopVia1 row per rail
x_in, x_out = iface["rail_x"]
for name, (r0, r1) in iface["rails"].items():
    strips = sorted(tuple(sorted((row_y(i, r0), row_y(i, r1)))) for i in range(ROWS))
    merged = [list(strips[0])]
    for y0, y1 in strips[1:]:
        if y0 <= merged[-1][1] + 1e-6:
            merged[-1][1] = y1
        else:
            merged.append([y0, y1])
    off = ring_off[name]
    for y0, y1 in merged:
        n = round((y1 - y0) / unit.RAIL_H)
        unit.rect(top, "Metal3", off, y0, X0 + x_in, y1)
        unit.rect(top, "Metal3", X0 + x_out, y0, W_TOP - off, y1)
        for x in (off + RING_W / 2, W_TOP - off - RING_W / 2):
            unit.via(top, x, (y0 + y1) / 2, "Metal3", V_METAL, cols=2, rows=2 * n, vt1_columns=1, vt1_rows=n)

# Signals: vin<n> on Metal2 from the left edge to the unit's vin bar, vout<n> on Metal3 from the unit's vout bar to the
# right edge, as tall as the bars, each with a square pin at the macro edge
vin, vout = iface["vin"], iface["vout"]
for i in range(ROWS):
    y, h = row_y(i, vin.center().y), vin.height()
    unit.rect(top, "Metal2", 0.0, y - h / 2, X0 + vin.left, y + h / 2)
    unit.pin(top, "Metal2", f"vin{i + 1}", pya.DBox(0.0, y - h / 2, h, y + h / 2))
    y, h = row_y(i, vout.center().y), vout.height()
    unit.rect(top, "Metal3", X0 + vout.right, y - h / 2, W_TOP, y + h / 2)
    unit.pin(top, "Metal3", f"vout{i + 1}", pya.DBox(W_TOP - h, y - h / 2, W_TOP, y + h / 2))

# NWell straps across the full cell width between the wells of two facing pmos rows, read from the placed PCells
nw = pya.Region(ly.cell(ui).begin_shapes_rec(ly.layer(*unit.LAYERS["NWell"]))).bbox().to_dtype(ly.dbu)
for i in range(0, ROWS, 2):
    unit.rect(top, "NWell", X0, row_y(i, nw.top), X0 + unit.CELL_W, row_y(i + 1, nw.top))

unit.rect(top, "prBoundary", 0.0, 0.0, W_TOP, H_TOP)

klay = out[: -len(".gds")] + ".klay.gds"
ly.write(klay, unit.save_options())
with open(klay[: -len(".gds")] + ".klib", "w", encoding="utf-8", newline="\n") as f:
    json.dump({"technology": "", "statements": [{"lib_name": "inverter", "lib_path": "inverter.gds"}]}, f, indent=4)
ly.write(out, unit.save_options(context=False))
print(f"inverter_top: wrote {os.path.normpath(klay)}, its .klib and {os.path.basename(out)}, bbox {top.dbbox()}")
# ==============================================================================
