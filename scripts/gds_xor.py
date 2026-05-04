#!/usr/bin/env python3
# ========================================================================
# XOR two GDS files and write differences to an output GDS
#
# SPDX-FileCopyrightText: 2026 Harald Pretl
# Johannes Kepler University, Department for Integrated Circuits
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0
# ========================================================================

import argparse
import sys
import klayout.db as pya


def gds_xor(file_a, file_b, output, top_cell=None):
    layout_a = pya.Layout()
    layout_a.read(file_a)

    layout_b = pya.Layout()
    layout_b.read(file_b)

    if top_cell:
        cell_a = layout_a.cell(top_cell)
        cell_b = layout_b.cell(top_cell)
        if cell_a is None:
            sys.exit(f"Error: cell '{top_cell}' not found in {file_a}")
        if cell_b is None:
            sys.exit(f"Error: cell '{top_cell}' not found in {file_b}")
    else:
        cell_a = layout_a.top_cell()
        cell_b = layout_b.top_cell()
        if cell_a is None:
            sys.exit(f"Error: no top cell found in {file_a}")
        if cell_b is None:
            sys.exit(f"Error: no top cell found in {file_b}")

    out_layout = pya.Layout()
    out_cell = out_layout.create_cell("XOR")

    # Collect all layer/datatype pairs from both layouts
    layer_pairs = set()
    for li in layout_a.layer_indices():
        info = layout_a.get_info(li)
        layer_pairs.add((info.layer, info.datatype))
    for li in layout_b.layer_indices():
        info = layout_b.get_info(li)
        layer_pairs.add((info.layer, info.datatype))

    diff_count = 0

    for layer_num, datatype in sorted(layer_pairs):
        li_a = layout_a.find_layer(layer_num, datatype)
        li_b = layout_b.find_layer(layer_num, datatype)

        region_a = pya.Region()
        region_b = pya.Region()

        if li_a is not None:
            region_a = pya.Region(cell_a.begin_shapes_rec(li_a))
        if li_b is not None:
            region_b = pya.Region(cell_b.begin_shapes_rec(li_b))

        xor_region = region_a ^ region_b

        if not xor_region.is_empty():
            out_li = out_layout.layer(layer_num, datatype)
            out_cell.shapes(out_li).insert(xor_region)
            diff_count += xor_region.count()
            print(f"  Layer {layer_num}/{datatype}: {xor_region.count()} difference(s)")

    out_layout.write(output)

    if diff_count == 0:
        print("No differences found.")
    else:
        print(f"Total: {diff_count} difference(s) written to {output}")

    return diff_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XOR two GDS files and write differences to output GDS.")
    parser.add_argument("gds_a", help="First GDS file")
    parser.add_argument("gds_b", help="Second GDS file")
    parser.add_argument("-o", "--output", default="xor_result.gds", help="Output GDS file (default: xor_result.gds)")
    parser.add_argument("-c", "--cell", default=None, help="Top cell name (default: auto-detect)")
    args = parser.parse_args()

    gds_xor(args.gds_a, args.gds_b, args.output, args.cell)
