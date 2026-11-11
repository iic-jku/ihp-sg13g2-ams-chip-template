# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Check that the top cell of a layout carries the PR boundary box the chip flow needs.

import argparse
import sys

# GDS layer of prBoundary. Magic maps every datatype of it to its boundary layer (cifin: calma BOUND 189 *),
# and LibreLane's Magic.StreamOut reads the FIXED_BBOX derived from it for every macro it places.
BOUNDARY_LAYER = 189


def boundary_shapes(kdb, layout, cell, layer):
    """Return (datatype, count, bbox) for every datatype of the boundary layer drawn in the cell itself."""
    found = []
    for index in layout.layer_indexes():
        info = layout.get_info(index)
        if info.layer != layer:
            continue
        shapes = cell.shapes(index)
        if shapes.size():
            bbox = kdb.Box()
            for shape in shapes.each():
                bbox = bbox + shape.bbox()
            found.append((info.datatype, shapes.size(), bbox))
    return found


def main():
    parser = argparse.ArgumentParser(
        description="Check that the top cell of a layout carries the PR boundary box the chip flow needs."
    )
    parser.add_argument("layout", help="layout file (GDS or OASIS)")
    parser.add_argument("cell", help="name of the top cell")
    parser.add_argument("--layer", type=int, default=BOUNDARY_LAYER,
                        help=f"GDS layer of the PR boundary (default: {BOUNDARY_LAYER})")
    args = parser.parse_args()

    try:
        import klayout.db as kdb
    except ImportError:
        print("[ERROR] The klayout Python module is not available. Run this inside the "
              "IIC-OSIC-TOOLS container.", file=sys.stderr)
        return 2

    layout = kdb.Layout()
    layout.read(args.layout)
    cell = layout.cell(args.cell)
    if cell is None:
        print(f"[ERROR] {args.layout}: no cell '{args.cell}' found.", file=sys.stderr)
        return 1

    print(f"[INFO] Checking the PR boundary of {args.cell} in {args.layout} ...", flush=True)
    found = boundary_shapes(kdb, layout, cell, args.layer)
    if not found:
        print(f"[ERROR] {args.layout}: cell '{args.cell}' draws no shape on the PR boundary layer "
              f"{args.layer}. The chip flow derives the macro bounding box from it and fails without "
              f"it ('Failed to extract PR boundary from GDSII view of macro'). Draw the boundary box "
              f"on prBoundary ({args.layer}/0) in the layout source and re-export the GDS.",
              file=sys.stderr)
        return 1

    dbu = layout.dbu
    boundary = found[0][2]
    for datatype, count, bbox in found:
        boundary = boundary + bbox
        print(f"[INFO] {count} shape(s) on layer {args.layer}/{datatype}, "
              f"{bbox.width() * dbu:.3f} um x {bbox.height() * dbu:.3f} um.")
    if not cell.bbox().inside(boundary):
        print(f"[WARNING] The geometry of '{args.cell}' extends beyond the PR boundary box "
              f"({cell.bbox().width() * dbu:.3f} um x {cell.bbox().height() * dbu:.3f} um versus "
              f"{boundary.width() * dbu:.3f} um x {boundary.height() * dbu:.3f} um). The chip flow "
              f"places the macro by the boundary, so anything outside it may overlap a neighbor.")
    print("[INFO] PR boundary check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
