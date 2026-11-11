# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Check that every port of a PEX netlist is really connected to the circuit.

import argparse
import re
import sys

# Elements whose first two nodes are the only nodes.
TWO_NODE = ("r", "c", "l", "v", "i", "d")


def logical_lines(path):
    """Yield the netlist lines with SPICE continuation lines ("+") joined."""
    out = []
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.rstrip("\n").rstrip()
        if not line or line.startswith("*"):
            continue
        if line.startswith("+") and out:
            out[-1] += " " + line[1:].strip()
        else:
            out.append(line.strip())
    return out


def nodes_of(tokens):
    """Return the node names of one element line."""
    params = len(tokens)
    for i, t in enumerate(tokens):
        if "=" in t:
            params = i
            break
    fields = tokens[1:params]
    if tokens[0][0].lower() in TWO_NODE:
        return fields[:2]
    # x (subcircuit call) and m/q (device): the last field is the model or subcircuit name
    return fields[:-1] if len(fields) > 1 else fields


def subcircuits(path):
    """Split the netlist into (name, ports, elements) blocks."""
    blocks, name, ports, elements = [], None, [], []
    for line in logical_lines(path):
        low = line.lower()
        if low.startswith(".subckt"):
            tokens = line.split()
            name, ports, elements = tokens[1], tokens[2:], []
        elif low.startswith(".ends"):
            if name:
                blocks.append((name, ports, elements))
            name, ports, elements = None, [], []
        elif name and not line.startswith("."):
            elements.append(line.split())
    return blocks


class Union:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb

    def same(self, a, b):
        return self.find(a) == self.find(b)


def check(path, verbose=False):
    """Return the list of problems found in one netlist."""
    problems = []
    for name, ports, elements in subcircuits(path):
        if not elements:
            continue  # black-box stub, nothing to check

        used, dc = set(), Union()
        for tokens in elements:
            nodes = nodes_of(tokens)
            used.update(nodes)
            # only resistors carry DC current, capacitors do not
            if tokens[0][0].lower() == "r" and len(nodes) == 2:
                dc.union(nodes[0], nodes[1])

        for port in ports:
            if port not in used:
                problems.append(
                    f"{path}: subcircuit '{name}' declares port '{port}', but no element "
                    f"connects to it. Anything wired to this pin is left floating."
                )
                continue
            # extresist splits a net into <net>.t<n> and <net>.n<n> fragments. If those
            # fragments exist, the port has to reach at least one of them through resistors.
            frags = [n for n in used if n.startswith(port + ".")]
            if frags and not any(dc.same(port, f) for f in frags):
                problems.append(
                    f"{path}: subcircuit '{name}' has {len(frags)} resistance fragments "
                    f"'{port}.*', but none of them is connected to port '{port}'."
                )

        if verbose:
            res = sum(1 for t in elements if t[0][0].lower() == "r")
            print(f"    {name}: {len(ports)} ports, {len(elements)} elements, "
                  f"{res} resistors, {len(used)} nodes")
    return problems


def main():
    parser = argparse.ArgumentParser(
        description="Check that every port of a PEX netlist is connected to the circuit."
    )
    parser.add_argument("netlist", nargs="+", help="SPICE netlist(s) to check")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the size of every subcircuit")
    args = parser.parse_args()

    problems = []
    for path in args.netlist:
        print(f"[INFO] Checking PEX netlist ports in {path} ...")
        problems += check(path, args.verbose)

    for problem in problems:
        print(f"[ERROR] {problem}", file=sys.stderr)
    if problems:
        print(f"[ERROR] {len(problems)} dangling port(s) found. The netlist is not usable "
              f"for simulation.", file=sys.stderr)
        return 1
    print("[INFO] All ports are connected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
