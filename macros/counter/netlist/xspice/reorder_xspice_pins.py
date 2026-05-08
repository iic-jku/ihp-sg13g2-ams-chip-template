# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
"""
Reorder the .subckt pin list in an XSPICE file to match the pin order
of an Xschem .sym symbol file.

The pin names differ slightly between the two files:
  - XSPICE uses an ``a_`` prefix on every pin, ``a_VPWR``/``a_VGND``
    for power, and underscores instead of brackets for buses
    (e.g. ``a_gpio_in_0_``).
  - .sym uses plain names without the ``a_`` prefix, ``VDD``/``VSS``
    for power, and brackets for buses (e.g. ``gpio_in[0]``).

This script converts sym names to XSPICE names and then rewrites the
.subckt line with the pins reordered to match the .sym order.

Usage:
    python reorder_xspice_pins.py <sym_file> <xspice_file> [-o <output_file>]

If -o is not given, the xspice file is overwritten in-place.
"""

import argparse
import re


def parse_sym_pins(sym_path: str) -> list[str]:
    """Extract pin names from .sym file in order of appearance.

    Pins are defined as: B 5 ... {name=<pin_name> dir=<dir>}
    """
    pins = []
    pattern = re.compile(r'^B\s+5\s+.*\{name=(\S+)\s+dir=\w+\}')
    with open(sym_path, 'r') as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                pins.append(m.group(1))
    return pins


def parse_xspice_subckt(xspice_path: str) -> tuple[str, list[str], int, int]:
    """Extract the subcircuit name and pin list from the .subckt line.

    Handles continuation lines starting with '+'.
    Returns (subckt_name, pin_list, first_line_number, last_line_number).
    """
    with open(xspice_path, 'r') as f:
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
    raise ValueError(f"No .subckt line found in {xspice_path}")


def sym_to_xspice_name(sym_pin: str) -> str:
    """Convert a sym pin name to its XSPICE equivalent.

    Rules:
      - VDD -> a_VPWR, VSS -> a_VGND
      - name[N] -> a_name_N_  (bus pins with brackets)
      - name -> a_name        (everything else)
    """
    if sym_pin == 'VDD':
        return 'a_VPWR'
    if sym_pin == 'VSS':
        return 'a_VGND'
    # Bus pins: gpio_in[0] -> a_gpio_in_0_
    m = re.match(r'^(.+)\[(\d+)\]$', sym_pin)
    if m:
        return f'a_{m.group(1)}_{m.group(2)}_'
    return f'a_{sym_pin}'


def reorder_xspice(xspice_path: str, ordered_pins: list[str],
                   output_path: str) -> None:
    """Rewrite the XSPICE file with the .subckt pins reordered to match .sym."""
    with open(xspice_path, 'r') as f:
        lines = f.readlines()

    subckt_name, old_pins, first_idx, last_idx = parse_xspice_subckt(xspice_path)

    if set(ordered_pins) != set(old_pins):
        missing_in_new = set(old_pins) - set(ordered_pins)
        missing_in_old = set(ordered_pins) - set(old_pins)
        msg = "Pin set mismatch!\n"
        if missing_in_new:
            msg += f"  XSPICE pins not in symbol: {missing_in_new}\n"
        if missing_in_old:
            msg += f"  Symbol pins not in XSPICE: {missing_in_old}\n"
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
        description="Reorder XSPICE .subckt pins to match Xschem .sym pin order."
    )
    parser.add_argument("sym_file", help="Path to the Xschem .sym file")
    parser.add_argument("xspice_file", help="Path to the .xspice file")
    parser.add_argument("-o", "--output", default=None,
                        help="Output file path (default: overwrite xspice in-place)")
    args = parser.parse_args()

    output_path = args.output if args.output else args.xspice_file

    # 1. Parse pin lists
    sym_pins = parse_sym_pins(args.sym_file)
    subckt_name, xspice_pins, _, _ = parse_xspice_subckt(args.xspice_file)

    print(f"Symbol file:  {args.sym_file}")
    print(f"XSPICE file:  {args.xspice_file}")
    print(f"Subcircuit:   {subckt_name}")
    print(f"Sym pins:     {len(sym_pins)}")
    print(f"XSPICE pins:  {len(xspice_pins)}")

    # 2. Convert sym pin names to xspice names
    xspice_ordered = [sym_to_xspice_name(sp) for sp in sym_pins]

    # 3. Show mapping
    print("\nPin mapping (sym -> xspice):")
    for sp, xp in zip(sym_pins, xspice_ordered):
        old_idx = xspice_pins.index(xp)
        new_idx = xspice_ordered.index(xp)
        marker = "" if new_idx == old_idx else " *REORDERED*"
        print(f"  {sp:25s} -> {xp:25s}{marker}")

    # 4. Reorder and write
    reorder_xspice(args.xspice_file, xspice_ordered, output_path)
    print(f"\nReordered XSPICE written to: {output_path}")


if __name__ == "__main__":
    main()
