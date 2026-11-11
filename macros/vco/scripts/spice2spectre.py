# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Translate a flat extracted SPICE subcircuit of R, C, L and PDK devices into a VACASK subcircuit.

import argparse
import re
import sys

# SPICE reads M as milli and VACASK as mega, so the output carries plain numbers only
SCALE = {"t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18}
NUMBER = re.compile(r"([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)(meg|[tgkmunpfa])?", re.I)
PRIMITIVES = {"R": ("resistor", "r"), "C": ("capacitor", "c"), "L": ("inductor", "l")}
R_TIE = 1e12  # Ohm from a node with only capacitors to the ground pin, which VACASK needs to factorize the matrix


def number(text):
    m = NUMBER.fullmatch(text)
    if not m:
        sys.exit(f"spice2spectre.py: {text!r} is not a number")
    return f"{float(m.group(1)) * SCALE.get((m.group(2) or '').lower(), 1.0):.12g}"


def logical_lines(path):
    lines = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("+") and lines:
                lines[-1] += " " + line[1:].strip()
            elif line:
                lines.append(line)
    return lines


class Names:
    """VACASK identifiers allow neither . nor #. Two names that would come out the same would short two nets, so they stop the run."""

    def __init__(self):
        self.source = {}

    def __call__(self, name):
        clean = re.sub(r"\W", "_", name, flags=re.A)
        if self.source.setdefault(clean, name) != name:
            sys.exit(f"spice2spectre.py: {name} and {self.source[clean]} both become {clean}")
        return clean


def translate(lines, ground):
    nodes, instances = Names(), Names()
    head, body, touched, name, ports = [], [], {}, None, []
    for line in lines:
        tok = line.split()
        first = tok[0].lower()
        if line.startswith("*"):
            head.append("//" + line[1:])
        elif first == ".subckt":
            if name:
                sys.exit("spice2spectre.py: more than one .subckt, the netlist is not flat")
            name, ports = tok[1], [nodes(p) for p in tok[2:]]
        elif first == ".ends":
            pass
        elif line.startswith(".") or not name:
            sys.exit(f"spice2spectre.py: cannot translate {line!r}")
        elif tok[0][0] in PRIMITIVES:
            model, par = PRIMITIVES[tok[0][0]]
            a, b = nodes(tok[1]), nodes(tok[2])
            for n in (a, b):
                touched.setdefault(n, set()).add(tok[0][0])
            body.append(f"  {instances(tok[0])} ({a} {b}) {model} {par}={number(tok[3])}")
        elif tok[0][0] == "X":
            positional = [t for t in tok[1:] if "=" not in t]
            pins = [nodes(n) for n in positional[:-1]]
            for n in pins:
                touched.setdefault(n, set()).add("X")
            params = [f"{k}={number(v)}" for k, v in (t.split("=") for t in tok[1:] if "=" in t)]
            body.append(f"  {instances(tok[0])} ({' '.join(pins)}) {positional[-1]} {' '.join(params)}")
        else:
            sys.exit(f"spice2spectre.py: cannot translate {line!r}")
    if ground not in ports:
        sys.exit(f"spice2spectre.py: the ground pin {ground} is not a pin of {name}")
    # A node 0 inside a VACASK subckt would be local, so the ties name the ground pin
    floating = sorted(n for n, kinds in touched.items() if kinds == {"C"} and n not in ports)
    ties = [f"  Rtie{i} ({n} {ground}) resistor r={R_TIE:g}" for i, n in enumerate(floating)]
    return head + [f"subckt {name} ({' '.join(ports)})"] + body + ties + ["ends"], len(body), len(floating)


def main():
    parser = argparse.ArgumentParser(description="Translate a flat extracted SPICE subcircuit into a VACASK subcircuit.")
    parser.add_argument("spice", help="extracted netlist")
    parser.add_argument("spectre", help="VACASK netlist to write")
    parser.add_argument("--ground", default="VSS", help="ground pin of the subcircuit (default: VSS)")
    args = parser.parse_args()
    out, n, tied = translate(logical_lines(args.spice), args.ground)
    with open(args.spectre, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print(f"spice2spectre.py: {n} instances, {tied} capacitor-only nodes tied, wrote {args.spectre}")


if __name__ == "__main__":
    main()
