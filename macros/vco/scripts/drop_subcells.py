# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Write a cell of a layout without the instances of its subcells, so only its own shapes are extracted.

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Write a cell of a layout without the instances of its subcells.")
    parser.add_argument("layout", help="input layout (GDS)")
    parser.add_argument("cell", help="cell to write")
    parser.add_argument("out", help="output layout (GDS)")
    args = parser.parse_args()

    try:
        import klayout.db as kdb
    except ImportError:
        import pya as kdb

    ly = kdb.Layout()
    ly.read(args.layout)
    cell = ly.cell(args.cell)
    if cell is None:
        sys.exit(f"drop_subcells.py: no cell {args.cell} in {args.layout}")
    names = sorted({inst.cell.name for inst in cell.each_inst()})
    for inst in list(cell.each_inst()):
        inst.delete()
    opt = kdb.SaveLayoutOptions()
    opt.select_cell(cell.cell_index())
    opt.write_context_info = False
    opt.gds2_write_timestamps = False
    ly.write(args.out, opt)
    print(f"drop_subcells.py: wrote {args.cell} without {', '.join(names) or 'subcells'} to {args.out}")


if __name__ == "__main__":
    main()
