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

Before the pin-set check the SPICE file is also reconciled against the
symbol for 1-bit-bus name flattening: if the symbol declares a port
``X[0]`` but the SPICE file has the scalar ``X`` (a common
Yosys/LibreLane side-effect when a Verilog bus has width 1), the scalar
is renamed to ``X[0]`` throughout the whole SPICE file (subckt header
*and* body) so all internal references stay consistent.

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


def parse_subckt_from_lines(lines: list[str]) -> tuple[str, list[str], int, int]:
    """Extract the subcircuit name and pin list from the first .subckt in lines.

    Handles continuation lines starting with '+'.
    Returns (subckt_name, pin_list, first_line_index, last_line_index).
    """
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('.subckt'):
            parts = stripped.split()
            subckt_name = parts[1]
            pins = parts[2:]
            last = i
            for j in range(i + 1, len(lines)):
                cont = lines[j].strip()
                if cont.startswith('+'):
                    pins.extend(cont[1:].split())
                    last = j
                else:
                    break
            return subckt_name, pins, i, last
    raise ValueError("No .subckt line found")


def reconcile_scalar_buses(
    lines: list[str],
    sym_pins: list[str],
    spice_pins: list[str],
) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """Rename flattened scalar pins (``X``) to bus-of-one form (``X[0]``).

    Yosys/LibreLane flatten 1-bit Verilog buses, so a port declared
    ``[0:0] input_PAD`` in RTL becomes the scalar ``input_PAD`` in the
    extracted SPICE, while the schematic-side symbol still uses
    ``input_PAD[0]``.  This pass detects such pairs and rewrites the
    scalar to the bus-of-one form throughout the whole SPICE file so
    the subsequent pin-set check and reorder succeed and internal
    element/connection references stay consistent.

    Returns (rewritten_lines, updated_spice_pins, [(scalar, bus0), ...]).
    If no renames are needed, the inputs are returned unchanged.
    """
    spice_set = set(spice_pins)
    bus0_pattern = re.compile(r'^(.+)\[0\]$')
    rename: dict[str, str] = {}
    for s in sym_pins:
        m = bus0_pattern.match(s)
        if m:
            scalar = m.group(1)
            if scalar in spice_set and s not in spice_set:
                rename[scalar] = s
    if not rename:
        return lines, spice_pins, []

    # Token-boundary regex: require non-word and non-'[' on both sides so that
    # 'input_PAD[0]' (already bus-of-one) and identifiers like 'input_PAD2CORE'
    # are left untouched.
    alternation = '|'.join(re.escape(k) for k in rename)
    token_pattern = re.compile(
        r'(?<![\w\[])(' + alternation + r')(?![\w\[])'
    )
    new_lines = [
        token_pattern.sub(lambda m: rename[m.group(1)], ln)
        for ln in lines
    ]
    _, new_spice_pins, _, _ = parse_subckt_from_lines(new_lines)
    return new_lines, new_spice_pins, sorted(rename.items())


def rewrite_subckt_header(
    lines: list[str],
    subckt_name: str,
    ordered_pins: list[str],
    first_idx: int,
    last_idx: int,
) -> list[str]:
    """Return a copy of ``lines`` with the .subckt header replaced by one
    listing ``ordered_pins``, wrapped to ~80 columns with '+' continuations."""
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
    return lines[:first_idx] + subckt_lines + lines[last_idx + 1:]


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
    with open(args.spice_file, 'r') as f:
        lines = f.readlines()
    subckt_name, spice_pins, _, _ = parse_subckt_from_lines(lines)

    print(f"Symbol file:  {args.sym_file}")
    print(f"SPICE file:   {args.spice_file}")
    print(f"Subcircuit:   {subckt_name}")
    print(f"Sym pins:     {len(sym_pins)}")
    print(f"SPICE pins:   {len(spice_pins)}")

    # 2. Show initial pin orders
    print(f"\n  .sym order:   {sym_pins}")
    print(f"  .spice order: {spice_pins}")

    # 3. Reconcile flattened 1-bit buses (scalar 'X' -> bus 'X[0]') across
    #    the whole SPICE file, not just the .subckt header.
    lines, spice_pins, renames = reconcile_scalar_buses(lines, sym_pins, spice_pins)
    if renames:
        print(f"\nRenamed flattened scalar pins to match symbol bus notation:")
        for scalar, bus0 in renames:
            print(f"  {scalar} -> {bus0}")

    # 4. Check pin sets match
    if set(sym_pins) != set(spice_pins):
        missing_in_sym = set(spice_pins) - set(sym_pins)
        missing_in_spice = set(sym_pins) - set(spice_pins)
        msg = "Pin set mismatch!\n"
        if missing_in_sym:
            msg += f"  SPICE pins not in symbol: {missing_in_sym}\n"
        if missing_in_spice:
            msg += f"  Symbol pins not in SPICE: {missing_in_spice}\n"
        raise ValueError(msg)

    # 5. Reorder subckt header (operate on the possibly-rewritten lines)
    _, _, first_idx, last_idx = parse_subckt_from_lines(lines)
    lines = rewrite_subckt_header(lines, subckt_name, sym_pins, first_idx, last_idx)

    # 6. Write back (subckt + body, all in one pass)
    with open(output_path, 'w') as f:
        f.writelines(lines)

    # 7. Show result
    print(f"\nPin mapping (sym -> spice):")
    for sp in sym_pins:
        old_idx = spice_pins.index(sp)
        new_idx = sym_pins.index(sp)
        marker = "" if new_idx == old_idx else " *REORDERED*"
        print(f"  {sp:25s} -> {sp:25s}{marker}")

    print(f"\nReordered SPICE written to: {output_path}")


if __name__ == "__main__":
    main()
