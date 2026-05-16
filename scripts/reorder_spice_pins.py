#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

"""
Reorder the .subckt pin list in a PEX SPICE file to match the pin order
of an Xschem .sym symbol file.

Pin names are identical in both files.  The order is taken from the
B 5 (pin) lines in the .sym file.  Two ordering modes are supported:

  - ``sim_pinnumber`` mode: if *every* B 5 pin line carries a
    ``sim_pinnumber=<n>`` property, the pins are sorted by that number.
    This is useful when the physical layout of pins in the symbol file
    does not reflect the intended electrical pin order (e.g. the IHP
    bipolar symbols).
  - Appearance-order mode (default): if no pin (or only some pins) carry
    ``sim_pinnumber``, the order of appearance in the .sym file is used,
    matching the original behaviour.

Usage:
    python reorder_spice_pins.py <sym_file> <spice_file> [-o <output_file>]

If -o is not given, the spice file is overwritten in-place.
"""

import argparse
import re


def parse_sym_pins(sym_path: str) -> list[str]:
    """Extract pin names from .sym file in order of appearance.

    Pins are defined as: B 5 ... {name=<pin_name> dir=<dir> [sim_pinnumber=<n>]}
    If every pin carries a ``sim_pinnumber`` property, the list is sorted
    by that number instead of by order of appearance.
    """
    pin_pattern = re.compile(r'^B\s+5\s+.*\{name=(\S+)\s+dir=\w+[^}]*\}')
    sim_num_pattern = re.compile(r'sim_pinnumber=(\d+)')
    raw = []  # list of (sim_pinnumber | None, name)
    with open(sym_path, 'r') as f:
        for line in f:
            stripped = line.strip()
            m = pin_pattern.match(stripped)
            if not m:
                continue
            name = m.group(1)
            sn = sim_num_pattern.search(stripped)
            raw.append((int(sn.group(1)) if sn else None, name))
    if raw and all(n is not None for n, _ in raw):
        raw.sort(key=lambda x: x[0])
    return [name for _, name in raw]


def parse_spice_subckt(spice_path: str) -> tuple[str, list[str], int, int]:
    """Extract the subcircuit name and pin list from the .subckt line.

    Handles continuation lines starting with '+'.
    Returns (subckt_name, pin_list, first_line_number, last_line_number).
    """
    with open(spice_path, 'r') as f:
        all_lines = f.readlines()
    for i, line in enumerate(all_lines):
        stripped = line.strip()
        if stripped.startswith('.subckt'):
            parts = stripped.split()
            subckt_name = parts[1]
            pins = parts[2:]
            last = i
            for j in range(i + 1, len(all_lines)):
                cont = all_lines[j].strip()
                if cont.startswith('+'):
                    pins.extend(cont[1:].split())
                    last = j
                else:
                    break
            return subckt_name, pins, i, last
    raise ValueError(f"No .subckt line found in {spice_path}")


def reorder_spice(spice_path: str, ordered_pins: list[str],
                  output_path: str) -> None:
    """Rewrite the SPICE file with the .subckt pins reordered to match .sym."""
    with open(spice_path, 'r') as f:
        lines = f.readlines()

    subckt_name, old_pins, first_idx, last_idx = parse_spice_subckt(spice_path)

    if set(ordered_pins) != set(old_pins):
        missing_in_new = set(old_pins) - set(ordered_pins)
        missing_in_old = set(ordered_pins) - set(old_pins)
        msg = "Pin set mismatch!\n"
        if missing_in_new:
            msg += f"  SPICE pins not in symbol: {missing_in_new}\n"
        if missing_in_old:
            msg += f"  Symbol pins not in SPICE: {missing_in_old}\n"
        raise ValueError(msg)

    max_width = 80
    header = f".subckt {subckt_name}"
    subckt_lines = []
    current = header
    for pin in ordered_pins:
        if len(current) + 1 + len(pin) > max_width:
            subckt_lines.append(current + "\n")
            current = "+ " + pin
        else:
            current += " " + pin
    subckt_lines.append(current + "\n")
    lines[first_idx:last_idx + 1] = subckt_lines

    with open(output_path, 'w') as f:
        f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Reorder PEX SPICE .subckt pins to match Xschem .sym pin order."
    )
    parser.add_argument("sym_file", help="Path to the Xschem .sym file")
    parser.add_argument("spice_file", help="Path to the PEX .spice file")
    parser.add_argument("-o", "--output", default=None,
                        help="Output file path (default: overwrite spice in-place)")
    args = parser.parse_args()

    output_path = args.output if args.output else args.spice_file

    # 1. Parse pin lists
    sym_pins = parse_sym_pins(args.sym_file)
    subckt_name, spice_pins, _, _ = parse_spice_subckt(args.spice_file)

    print(f"Symbol file:  {args.sym_file}")
    print(f"SPICE file:   {args.spice_file}")
    print(f"Subcircuit:   {subckt_name}")
    print(f"Sym pins:     {len(sym_pins)}")
    print(f"SPICE pins:   {len(spice_pins)}")

    # 2. Show initial pin orders
    print(f"\n  .sym order:   {sym_pins}")
    print(f"  .spice order: {spice_pins}")

    # 3. Reorder and write
    reorder_spice(args.spice_file, sym_pins, output_path)

    # 4. Show result
    print(f"\nPin mapping (sym -> spice):")
    for sp in sym_pins:
        old_idx = spice_pins.index(sp)
        new_idx = sym_pins.index(sp)
        marker = "" if new_idx == old_idx else " *REORDERED*"
        print(f"  {sp:25s} -> {sp:25s}{marker}")

    print(f"\nReordered SPICE written to: {output_path}")


if __name__ == "__main__":
    main()
