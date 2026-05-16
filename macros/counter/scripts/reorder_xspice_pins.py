#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
"""
Reorder the .subckt pin list in an XSPICE file to match the pin order
of an Xschem .sym symbol file.

Symbol and XSPICE pin names do not need to follow a shared naming
convention. The mapping is built with two rules:

  - Power pins are matched by name: ``VDD`` <-> ``a_VPWR``,
    ``VSS`` <-> ``a_VGND``.
  - All other pins are matched by *position*: the i-th non-power pin
    in the symbol maps to the i-th non-power pin in the XSPICE
    .subckt. This way the symbol may rename pins (e.g. ``di_clock``
    while XSPICE has ``a_clock_i``) without breaking the script.

Bus pins in the symbol use the xschem range syntax ``name[A..B]`` and
are expanded into individual indexed pins (``name[A]``, ``name[A+1]``,
..., ``name[B]``) before matching.

Pin ordering from the symbol supports two modes:

  - ``sim_pinnumber`` mode: if *every* B 5 pin line (or bus group) in
    the .sym file carries a ``sim_pinnumber=<n>`` property, the entries
    are sorted by that number before positional matching against the
    XSPICE pins. Expanded bus pins keep their intra-bus order.
  - Appearance-order mode (default): if no pin (or only some pins) carry
    ``sim_pinnumber``, the order of appearance in the .sym file is used,
    matching the original behaviour.

Usage:
    python reorder_xspice_pins.py <sym_file> <xspice_file> [-o <output_file>]

If -o is not given, the xspice file is overwritten in-place.
"""

import argparse
import re


POWER_MAP = {'VDD': 'a_VPWR', 'VSS': 'a_VGND'}
XSPICE_POWER = set(POWER_MAP.values())


def parse_sym_pins(sym_path: str) -> list[str]:
    """Extract pin names from .sym file in order of appearance.

    Pins are defined as: B 5 ... {name=<pin_name> dir=<dir> [sim_pinnumber=<n>]}
    A bus pin written as ``name[A..B]`` is expanded into individual
    indexed pins. ``A`` and ``B`` may be in either order.
    If every pin (or bus group) carries a ``sim_pinnumber`` property, the
    entries are sorted by that number instead of by order of appearance;
    expanded bus pins keep their intra-bus order.
    """
    pin_pattern = re.compile(r'^B\s+5\s+.*\{name=(\S+)\s+dir=\w+[^}]*\}')
    bus_range_pattern = re.compile(r'^(.+)\[(\d+)\.\.(\d+)\]$')
    sim_num_pattern = re.compile(r'sim_pinnumber=(\d+)')
    raw = []  # list of (sim_pinnumber | None, [expanded pin names])
    with open(sym_path, 'r') as f:
        for line in f:
            stripped = line.strip()
            m = pin_pattern.match(stripped)
            if not m:
                continue
            name = m.group(1)
            sn = sim_num_pattern.search(stripped)
            sim_num = int(sn.group(1)) if sn else None
            bm = bus_range_pattern.match(name)
            if bm:
                base = bm.group(1)
                a, b = int(bm.group(2)), int(bm.group(3))
                step = 1 if a <= b else -1
                expanded = [f'{base}[{i}]' for i in range(a, b + step, step)]
            else:
                expanded = [name]
            raw.append((sim_num, expanded))
    if raw and all(n is not None for n, _ in raw):
        raw.sort(key=lambda x: x[0])
    pins = []
    for _, expanded in raw:
        pins.extend(expanded)
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


def build_mapping(sym_pins: list[str],
                  xspice_pins: list[str]) -> list[tuple[str, str]]:
    """Pair each sym pin with an XSPICE pin.

    VDD/VSS are matched to a_VPWR/a_VGND by name. All other sym pins
    are matched to the remaining XSPICE pins in the order they appear
    in the .subckt line.
    """
    if len(sym_pins) != len(xspice_pins):
        raise ValueError(
            f"Pin count mismatch: sym has {len(sym_pins)}, "
            f"xspice has {len(xspice_pins)} (after bus expansion)"
        )

    sym_power = {p for p in sym_pins if p in POWER_MAP}
    xspice_power = {p for p in xspice_pins if p in XSPICE_POWER}
    expected_xspice_power = {POWER_MAP[p] for p in sym_power}
    if expected_xspice_power != xspice_power:
        raise ValueError(
            f"Power pin mismatch: sym {sorted(sym_power)} maps to "
            f"{sorted(expected_xspice_power)}, but xspice has "
            f"{sorted(xspice_power)}"
        )

    signal_xspice = [p for p in xspice_pins if p not in XSPICE_POWER]
    sig_iter = iter(signal_xspice)

    mapping = []
    for sp in sym_pins:
        if sp in POWER_MAP:
            mapping.append((sp, POWER_MAP[sp]))
        else:
            mapping.append((sp, next(sig_iter)))
    return mapping


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
            msg += f"  XSPICE pins not in mapping: {missing_in_new}\n"
        if missing_in_old:
            msg += f"  Mapped pins not in XSPICE: {missing_in_old}\n"
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

    # 1. Parse pin lists (sym pins come back with bus ranges already expanded)
    sym_pins = parse_sym_pins(args.sym_file)
    subckt_name, xspice_pins, _, _ = parse_xspice_subckt(args.xspice_file)

    print(f"Symbol file:  {args.sym_file}")
    print(f"XSPICE file:  {args.xspice_file}")
    print(f"Subcircuit:   {subckt_name}")
    print(f"Sym pins:     {len(sym_pins)}")
    print(f"XSPICE pins:  {len(xspice_pins)}")

    # 2. Pair sym pins with xspice pins (power by name, others by position)
    mapping = build_mapping(sym_pins, xspice_pins)
    ordered_xspice = [xp for _, xp in mapping]

    # 3. Show mapping
    print("\nPin mapping (sym -> xspice):")
    for sp, xp in mapping:
        old_idx = xspice_pins.index(xp)
        new_idx = ordered_xspice.index(xp)
        marker = "" if new_idx == old_idx else " *REORDERED*"
        print(f"  {sp:25s} -> {xp:25s}{marker}")

    # 4. Reorder and write
    reorder_xspice(args.xspice_file, ordered_xspice, output_path)
    print(f"\nReordered XSPICE written to: {output_path}")


if __name__ == "__main__":
    main()
