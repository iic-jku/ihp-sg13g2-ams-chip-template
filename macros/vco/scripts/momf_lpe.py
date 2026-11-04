# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Put the MoM capacitors cut out of a PEX netlist back as PDK devices with the parasitics their model lacks.
"""Magic extracts no cap_cmomf device and reads its comb as plain metal, so its capacitance in a PEX netlist is Magic's
estimate of the comb and not the PDK model. drop_subcells.py --cut removes the combs before the extraction and leaves
a port <name>_A and <name>_B where each plate is fed. This script puts every cap back between its two ports: the PDK
cap_cmomf at the drawn size, so the model sets C, plus what the model lacks, from the table of --parasitics: in series
from port_A to port_B rs/2 and ls/2, the cap_cmomf from node a to node b, ls/2 and rs/2, and cs from a and from b to
the substrate node. The ports become internal nodes of the subcircuit.

    python3 scripts/momf_lpe.py <pex.spice> <cut.json> --parasitics <table.json> --sub VSS -o <out.spice>

The table lists one entry per cap geometry: w, l, mmin, mmax (um and metal levels, as drop_subcells.py records them)
and rs (Ohm), ls (H) and cs (F per plate). A geometry the table does not list stops the script.
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Put cut MoM caps back into a PEX netlist as PDK devices.")
    parser.add_argument("netlist", help="PEX netlist with the cut ports")
    parser.add_argument("cut", help="JSON file of drop_subcells.py --cut-json")
    parser.add_argument("--parasitics", required=True, help="JSON table of rs, ls and cs per cap geometry")
    parser.add_argument("--sub", default="VSS", help="port of the subcircuit the plates' substrate capacitance returns to")
    parser.add_argument("-o", "--out", required=True, help="output netlist")
    args = parser.parse_args()

    caps = json.load(open(args.cut, encoding="utf-8"))
    table = json.load(open(args.parasitics, encoding="utf-8"))
    lines = open(args.netlist, encoding="utf-8").read().splitlines()

    # subcircuit header, possibly continued on + lines
    head = next(i for i, line in enumerate(lines) if line.lower().startswith(".subckt"))
    end = head + 1
    while end < len(lines) and lines[end].startswith("+"):
        end += 1
    words = " ".join([lines[head]] + [line[1:] for line in lines[head + 1:end]]).split()
    name, ports = words[1], words[2:]
    if args.sub not in ports:
        sys.exit(f"momf_lpe.py: {args.sub} is no port of {name}")
    body = {t for line in lines[end:] if line[:1].isalpha() for t in line.split()[1:] if "=" not in t}

    cut_ports, devices = set(), []
    for c in caps:
        geo = (c["w"], c["l"], c["mmin"], c["mmax"])
        hit = [p for p in table if (p["w"], p["l"], p["mmin"], p["mmax"]) == geo]
        if len(hit) != 1:
            sys.exit(f"momf_lpe.py: {len(hit)} entries of {args.parasitics} for {c['name']}, w {geo[0]} l {geo[1]} um, Metal{geo[2]} to Metal{geo[3]}")
        p = hit[0]
        pa, pb = c["ports"]["A"]["name"], c["ports"]["B"]["name"]
        for n in (pa, pb):
            if n not in ports:
                sys.exit(f"momf_lpe.py: {n} is no port of {name}")
            if n not in body:
                sys.exit(f"momf_lpe.py: nothing in {args.netlist} is connected to {n}")
        cut_ports |= {pa, pb}
        n = c["name"]
        devices += [
            f"* {n}: cap_cmomf w={c['w']}u l={c['l']}u Metal{c['mmin']} to Metal{c['mmax']} in {c['cell']}, {p['source']}",
            f"R{n}a {pa} {n}_ra {p['rs'] / 2:.6g}",
            f"L{n}a {n}_ra {n}_a {p['ls'] / 2:.6g}",
            f"X{n} {n}_a {n}_b cap_cmomf w={c['w']}e-6 l={c['l']}e-6 mmin={c['mmin']} mmax={c['mmax']} subblock=0 m=1 mm_ok=1",
            f"L{n}b {n}_b {n}_rb {p['ls'] / 2:.6g}",
            f"R{n}b {n}_rb {pb} {p['rs'] / 2:.6g}",
            f"C{n}a {n}_a {args.sub} {p['cs']:.6g}",
            f"C{n}b {n}_b {args.sub} {p['cs']:.6g}",
        ]

    kept = [q for q in ports if q not in cut_ports]
    out = lines[:head] + [f".subckt {name} " + " ".join(kept)]
    ends = max(i for i, line in enumerate(lines) if line.lower().startswith(".ends"))
    out += lines[end:ends] + [f"* MoM caps cut out of the extraction (drop_subcells.py --cut), back as PDK devices by momf_lpe.py"]
    out += devices + lines[ends:]
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print(f"momf_lpe.py: {len(caps)} cap_cmomf with their parasitics into {name}, {len(cut_ports)} ports made internal, to {args.out}")


if __name__ == "__main__":
    main()
