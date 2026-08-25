# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Check that the pins of an Xschem symbol match the ports of the layout SPICE netlist.

# The layout netlist is written by LibreLane from the RTL port list, so it is the authoritative
# pin list of the chip. A pad added in the RTL that never reached the symbol (or a pin whose name
# drifted apart, e.g. IOVSS labelled VSS) shows up here instead of failing much later in PEX.

import argparse
import os
import re
import sys

# B 5 <x1> <y1> <x2> <y2> {name=<pin> dir=<dir> ...}
PIN_PATTERN = re.compile(r'^B\s+5\s+.*\{name=(\S+)\s+dir=\w+[^}]*\}')
# Xschem bus pins are written as <base>[<a>..<b>]
BUS_RANGE_PATTERN = re.compile(r'^(.+)\[(\d+)\.\.(\d+)\]$')
BUS0_PATTERN = re.compile(r'^(.+)\[0\]$')


def sym_pins(path):
    """Return the pin names of a .sym file, bus ranges expanded, in file order."""
    pins = []
    for line in open(path, encoding="utf-8", errors="replace"):
        match = PIN_PATTERN.match(line.strip())
        if not match:
            continue
        name = match.group(1)
        bus = BUS_RANGE_PATTERN.match(name)
        if bus:
            base, first, last = bus.group(1), int(bus.group(2)), int(bus.group(3))
            step = 1 if first <= last else -1
            pins += [f"{base}[{i}]" for i in range(first, last + step, step)]
        else:
            pins.append(name)
    return pins


def subckt_ports(path, cell):
    """Return the port names of the .subckt <cell> card, continuation lines joined."""
    lines = open(path, encoding="utf-8", errors="replace").readlines()
    for i, line in enumerate(lines):
        tokens = line.strip().split()
        if len(tokens) < 2 or tokens[0].lower() != ".subckt" or tokens[1] != cell:
            continue
        ports = tokens[2:]
        for cont in lines[i + 1:]:
            if not cont.strip().startswith("+"):
                break
            ports += cont.strip()[1:].split()
        return ports
    return None


def reconcile_scalar_buses(pins, ports):
    """Rename a scalar port <X> to <X>[0] when the symbol declares the bus-of-one form.

    Yosys flattens 1-bit Verilog buses, so `input_PAD [0:0]` in the RTL becomes the scalar
    `input_PAD` in the layout netlist while the symbol keeps `input_PAD[0]`.
    """
    port_set = set(ports)
    rename = {}
    for pin in pins:
        bus0 = BUS0_PATTERN.match(pin)
        if bus0 and bus0.group(1) in port_set and pin not in port_set:
            rename[bus0.group(1)] = pin
    return [rename.get(p, p) for p in ports], sorted(rename.items())


def main():
    parser = argparse.ArgumentParser(
        description="Check that the pins of an Xschem symbol match the ports of a SPICE netlist."
    )
    parser.add_argument("sym_file", help="Path to the Xschem .sym file")
    parser.add_argument("netlist_file", help="Path to the layout .spice netlist")
    parser.add_argument("-c", "--cell", default=None,
                        help="Subcircuit name (default: basename of the symbol file)")
    args = parser.parse_args()

    cell = args.cell if args.cell else os.path.splitext(os.path.basename(args.sym_file))[0]

    if not os.path.isfile(args.sym_file):
        print(f"[INFO] No symbol {args.sym_file}, skipping the port check.")
        return 0
    if not os.path.isfile(args.netlist_file):
        print(f"[INFO] No layout netlist {args.netlist_file}, skipping the port check. "
              f"Run the LibreLane flow first.")
        return 0

    pins = sym_pins(args.sym_file)
    ports = subckt_ports(args.netlist_file, cell)
    if ports is None:
        print(f"[ERROR] No '.subckt {cell}' card in {args.netlist_file}.", file=sys.stderr)
        return 1

    ports, renamed = reconcile_scalar_buses(pins, ports)
    for scalar, bus0 in renamed:
        print(f"[INFO] Netlist port '{scalar}' matched to symbol pin '{bus0}' "
              f"(1-bit bus flattened by Yosys).")

    print(f"Symbol file:   {args.sym_file}")
    print(f"Netlist file:  {args.netlist_file}")
    print(f"Subcircuit:    {cell}")
    print(f"Sym pins:      {len(pins)}")
    print(f"Netlist ports: {len(ports)}")

    problems = []
    duplicates = sorted({p for p in pins if pins.count(p) > 1})
    if duplicates:
        problems.append(
            f"Symbol declares these pins more than once: {duplicates}. A .subckt port list "
            f"cannot carry a name twice, one pin per net is needed."
        )
    missing_in_sym = sorted(set(ports) - set(pins))
    if missing_in_sym:
        problems.append(f"Netlist ports without a symbol pin: {missing_in_sym}")
    missing_in_netlist = sorted(set(pins) - set(ports))
    if missing_in_netlist:
        problems.append(f"Symbol pins without a netlist port: {missing_in_netlist}")

    for problem in problems:
        print(f"[ERROR] {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"[INFO] Symbol and layout netlist agree on all {len(pins)} ports.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
