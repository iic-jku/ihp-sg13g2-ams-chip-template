# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Tie the substrate port of a kpex 2.5D netlist to a port net of the cell.

import argparse
import sys


def tie(path, net, sub):
    """Drop port `sub` from the .subckt card and move its node onto port `net`, in place."""
    lines = open(path, encoding="utf-8").read().splitlines()
    out, moved, dropped, found = [], 0, 0, False
    i = 0
    while i < len(lines):
        first = i
        line = lines[i]
        i += 1
        tokens = line.split()
        if tokens and tokens[0].lower() == ".subckt":
            # kpex wraps a long port list over "+" lines
            while i < len(lines) and lines[i].startswith("+"):
                tokens += lines[i][1:].split()
                i += 1
            if sub not in tokens[2:]:
                out += lines[first:i]
                continue
            if net not in tokens[2:]:
                sys.exit(f"[ERROR] {path}: '{net}' is not a port of subcircuit '{tokens[1]}'.")
            found = True
            out.append(" ".join(t for t in tokens if t != sub))
            continue
        if not tokens or line.startswith("*") or sub not in tokens[1:]:
            out.append(line)
            continue
        tokens = [tokens[0]] + [net if t == sub else t for t in tokens[1:]]
        # an R or C with both ends on the tied net does nothing
        if tokens[0][0].lower() in "rc" and tokens[1] == tokens[2]:
            dropped += 1
            continue
        moved += 1
        out.append(" ".join(tokens))
    if not found:
        print(f"[INFO] {path} has no port '{sub}', nothing to tie.")
        return
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"[INFO] Tied port '{sub}' to '{net}' in {path}: {moved} element lines moved, "
          f"{dropped} elements between '{sub}' and '{net}' dropped.")


def main():
    parser = argparse.ArgumentParser(
        description="Tie the substrate port of a kpex 2.5D netlist to a port net of the cell."
    )
    parser.add_argument("netlist", help="SPICE netlist, rewritten in place")
    parser.add_argument("--net", required=True, help="port net the substrate is tied to, e.g. VSS")
    parser.add_argument("--sub", default="sub!", help="substrate port name (default: sub!)")
    args = parser.parse_args()
    tie(args.netlist, args.net, args.sub)
    return 0


if __name__ == "__main__":
    sys.exit(main())
