# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Rebuild the capacitances of a full-RC PEX netlist per net pair from a C-coupled extraction of the same layout.
"""Magic's extresist counts the coupling capacitance of a net that gets a resistor network a second time, as
capacitance to the substrate on the network's nodes (magic#557). In the VCO's post-layout netlist that put about
160 fF from each tank node to VSS, the coupling caps of the buffer counted again, against 15 fF in the C-coupled run.

This script keeps the resistors and devices of the full-RC netlist and sets the capacitance between every pair of nets
to the C-coupled value: the full-RC capacitors of a pair are scaled to its total, which keeps their distribution
over the network's nodes, a pair the full-RC run lacks gets one capacitor between the two nets' port nodes, and
capacitors between pairs the C-coupled run does not have are dropped.

    python3 scripts/pex_caps.py <full_rc.spice> <c_coupled.spice> -o <out.spice>

The nodes of one net carry the net's name plus .t<N> or .n<N> in the full-RC netlist, and the resistors join them,
which is how the nets of the two netlists are matched.
"""

import argparse
import json
import re
import sys
from collections import defaultdict

SUFFIX = re.compile(r"\.[tn]\d+$")
MULT = {"a": 1e-18, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3}


def value(s):
    s = s.lower()
    if s[-1] in MULT:
        return float(s[:-1]) * MULT[s[-1]]
    return float(s)


def base(node):
    return SUFFIX.sub("", node).rstrip("#")


def read(path):
    """The lines of the netlist, the subcircuit's ports, and its capacitors as (line index, node a, node b, value)."""
    lines = open(path, encoding="utf-8").read().splitlines()
    ports, caps, res = [], [], []
    in_header = False
    for i, line in enumerate(lines):
        t = line.split()
        if not t:
            continue
        if t[0].lower() == ".subckt":
            ports, in_header = t[2:], True
        elif t[0] == "+" and in_header:
            ports += t[1:]
        else:
            in_header = False
            if t[0][0] in "Cc" and len(t) >= 4:
                caps.append((i, t[1], t[2], value(t[3])))
            elif t[0][0] in "Rr" and len(t) >= 4:
                res.append((t[1], t[2]))
    return lines, ports, caps, res


class Nets:
    """Union-find of the nodes: the resistors and the base names join the nodes of one net."""

    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def join(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def main():
    parser = argparse.ArgumentParser(description="Rebuild the capacitances of a full-RC PEX netlist from a C-coupled one.")
    parser.add_argument("rc", help="full-RC netlist")
    parser.add_argument("cc", help="C-coupled netlist of the same layout")
    parser.add_argument("-o", "--out", required=True, help="output netlist")
    parser.add_argument("--ties", help="JSON file of drop_subcells.py: the pins that share a net with an added pin")
    args = parser.parse_args()

    lines, ports, caps, res = read(args.rc)
    _, _, cc_caps, _ = read(args.cc)

    # A port that no resistor or device reaches was left behind on a net without a resistor network: joined to another
    # port of its net, which carries the net, with a resistor far below the extraction threshold. On a net with no
    # device at all Magic builds no network at any threshold, and the port its capacitors use carries the net.
    used = {n for a, b in res for n in (a, b)}
    used |= {t for line in lines if line[:1] in ("X", "x") for t in line.split()[1:]}
    body = {t for line in lines if line[:1].isalpha() for t in line.split()[1:] if "=" not in t}
    tie_lines, loose = [], []
    if args.ties:
        for p, others in json.load(open(args.ties, encoding="utf-8")).items():
            group = [n for n in [p] + others if n in ports]
            carrier = next((n for n in group if n in used), None) or next((n for n in group if n in body), None)
            used |= {carrier} - {None}
            for n in group:
                if n in used or n == carrier:
                    continue
                if carrier is None:
                    loose.append(n)
                    continue
                tie_lines.append(f"Rpexcapstie{len(tie_lines)} {n} {carrier} 1m")
                res.append((n, carrier))
                used.add(n)
    if loose:
        sys.exit(f"pex_caps.py: no resistor or device reaches the added port(s) {', '.join(loose)} of {args.rc}")

    nets = Nets()
    for a, b in res:
        nets.join(a, b)
    nodes = {n for _, a, b, _ in caps for n in (a, b)} | {n for ab in res for n in ab} | set(ports)
    for n in nodes:
        nets.join(n, "net:" + base(n))
    net_of = {}  # base name of the C-coupled netlist -> net of the full-RC netlist
    for n in nodes:
        net_of[base(n)] = nets.find(n)
    port_node = {}
    for p in ports:
        port_node.setdefault(nets.find(p), p)
    for n in sorted(nodes):
        port_node.setdefault(nets.find(n), n)

    def pair(a, b):
        return tuple(sorted((a, b)))

    target = defaultdict(float)
    unmatched = 0.0
    for _, a, b, v in cc_caps:
        na, nb = net_of.get(base(a)), net_of.get(base(b))
        if na is None or nb is None:
            unmatched += v
            continue
        if na != nb:
            target[pair(na, nb)] += v
    total_cc = sum(v for _, _, _, v in cc_caps)
    if unmatched > 0.01 * total_cc:
        sys.exit(f"pex_caps.py: {unmatched * 1e15:.1f} fF of the C-coupled netlist match no net of the full-RC one")

    have = defaultdict(float)
    for _, a, b, v in caps:
        have[pair(nets.find(a), nets.find(b))] += v
    out, dropped, added = list(lines), 0.0, []
    for i, a, b, v in caps:
        p = pair(nets.find(a), nets.find(b))
        if p in target:
            t = lines[i].split()
            t[3] = f"{v * target[p] / have[p]:.6g}"
            out[i] = " ".join(t)
        else:
            out[i] = None
            dropped += v
    k = 0
    for p, v in target.items():
        if have.get(p, 0.0) == 0.0:
            added.append(f"Cpexcaps{k} {port_node[p[0]]} {port_node[p[1]]} {v:.6g}")
            k += 1
    ends = max(i for i, line in enumerate(out) if line is not None and line.lower().startswith(".ends"))
    out = out[:ends] + tie_lines + added + out[ends:]
    header = [f"* Capacitances rebuilt per net pair from the C-coupled extraction {args.cc.split('/')[-1]} (magic#557):",
              f"* {sum(target.values()) * 1e12:.4f} pF in {len(target)} net pairs, the full-RC run had "
              f"{sum(v for _, _, _, v in caps) * 1e12:.4f} pF, {dropped * 1e15:.1f} fF of it between pairs without coupling."]
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(header + [line for line in out if line is not None]) + "\n")
    print(f"pex_caps.py: {sum(target.values()) * 1e12:.4f} pF in {len(target)} net pairs "
          f"(full RC {sum(v for _, _, _, v in caps) * 1e12:.4f} pF), {len(added)} capacitors added, wrote {args.out}")


if __name__ == "__main__":
    main()
