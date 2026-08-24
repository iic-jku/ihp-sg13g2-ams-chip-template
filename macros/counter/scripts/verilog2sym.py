# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Scaffold an Xschem symbol from the ports of a Verilog netlist,
# or check an existing symbol against them.

"""Build or check the Xschem symbol of a hardened digital macro.

A digital macro has no schematic, so its symbol cannot be generated with
Xschem's own "make symbol from schematic" (key `a`). It is written by hand
instead, and it is the reference the rest of the gate-level flow bends to:
`sak-pin-reorder.py` reorders the ports of the XSPICE model and of the
extracted PEX netlists to the symbol's pin order, matching them by the
`sim_pinname` property of each pin.

That makes the symbol a source file, not a build product. This script
therefore has two modes, and neither of them rewrites a symbol in a build:

  generate (default)
      Write a first-cut `<cell>.sym` from the ports of a Verilog netlist.
      For a new macro this is the tedious part done right: every port
      becomes a pin with its direction, its bus range and its
      `sim_pinname`, on grid and in house style. Beautify it afterwards
      (rename pins to `di_*` / `do_*`, move them, redraw the body) and
      commit it. Refuses to overwrite an existing symbol without --force,
      because hand work lives in that file.

  --check
      Verify that an existing symbol still describes those ports. This is
      the mode a build runs. It is cheap and it fails early with the pin
      name in the message.

The reference netlist is the powered gate-level netlist
`netlist/pnl/<top>.pnl.v` from LibreLane: it is elaborated (so bus ranges
are plain numbers) and it carries the supply ports, which the unpowered
`netlist/nl/<top>.nl.v` does not.

Geometry follows Xschem's own symbol generator (`make_sym.awk`): inputs on
the left edge, outputs and remaining bidirectional ports on the right,
5x5 pin boxes, 20-unit stubs, pin labels inside the body at text size 0.2.
Two house rules are added on top: supplies leave the body at the top and
the bottom rather than the sides, and the pin pitch is 40 so that every
pin lands on a multiple of 20 whatever the pin count. That matters because
a testbench wire has to end exactly on a pin, with no tolerance.

Usage:
    verilog2sym.py <netlist.v> <symbol.sym> [--force]
    verilog2sym.py <netlist.v> <symbol.sym> --check
"""

import argparse
import os
import re
import sys

# Xschem symbol constants, taken from make_sym.awk so a generated symbol
# looks like one Xschem would have written itself.
PIN_HALF = 2.5      # half edge of the 5x5 pin box
STUB = 20           # pin stub length outside the body
TEXTDIST = 5        # gap between body edge and pin label
LABSIZE = 0.2       # pin label text size
LAB_VOFFSET = 4     # label sits this far above its pin
CHAR_W = 30 * LABSIZE   # width of one label character, Xschem's own factor

# House additions.
PITCH = 40          # pin pitch, keeps every pin on a multiple of 20
MIN_WIDTH = 150     # pin x, Xschem's default symbol width
LABEL_GAP = 20      # clearance between a left and a right pin label

# Layer numbers: 4 = symbol drawing, 5 = pin boxes, 7 = inout stubs.
LAYER_BODY = 4
LAYER_PIN = 5
LAYER_INOUT = 7

SYM_HEADER = "v {xschem version=3.4.8RC file_version=1.3}"

DIR_OF_KEYWORD = {"input": "in", "output": "out", "inout": "inout"}
KEYWORD_OF_DIR = {v: k for k, v in DIR_OF_KEYWORD.items()}

# Pin lines are `B 5 x1 y1 x2 y2 {name=<n> dir=<d> ...}`. The same pattern
# sak-pin-reorder.py uses, so both tools see the same pins.
PIN_RE = re.compile(r"^B\s+5\s+.*\{name=(\S+)\s+dir=(\w+)([^}]*)\}")
SIM_PINNAME_RE = re.compile(r"sim_pinname=([^\s}]+)")
BUS_RANGE_RE = re.compile(r"^(.+)\[(\d+)\.\.(\d+)\]$")


class Port:
    """One port of the Verilog module."""

    def __init__(self, name, direction, msb=None, lsb=None):
        self.name = name
        self.direction = direction      # 'in', 'out' or 'inout'
        self.msb = msb
        self.lsb = lsb

    @property
    def is_bus(self):
        return self.msb is not None

    @property
    def indices(self):
        """Bus indices in ascending order, empty for a scalar port."""
        if not self.is_bus:
            return []
        lo, hi = min(self.msb, self.lsb), max(self.msb, self.lsb)
        return list(range(lo, hi + 1))

    @property
    def display(self):
        """The pin name to put in the symbol, in Xschem range syntax."""
        if not self.is_bus:
            return self.name
        idx = self.indices
        return f"{self.name}[{idx[0]}..{idx[-1]}]"

    @property
    def nets(self):
        """The netlist-side names this port expands to."""
        if not self.is_bus:
            return [self.name]
        return [f"{self.name}[{i}]" for i in self.indices]


# --------------------------------------------------------------------------
# Verilog side
# --------------------------------------------------------------------------

def strip_comments(text):
    """Remove // and /* */ comments and `directives, keeping line count."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"//.*$", "", line)
        if line.lstrip().startswith("`"):
            line = ""
        lines.append(line)
    return "\n".join(lines)


def split_header(text):
    """Return (module_name, header_text, body_text) of the first module.

    The port list is taken with a balanced-parenthesis scan, so a parameter
    list `#(...)` and defaults containing parentheses do not truncate it.
    """
    m = re.search(r"\bmodule\s+(\w+)", text)
    if not m:
        raise ValueError("no `module` declaration found")
    name = m.group(1)
    i = m.end()

    # Skip an optional parameter list.
    while i < len(text) and text[i].isspace():
        i += 1
    if i < len(text) and text[i] == "#":
        i = skip_parens(text, text.index("(", i))

    start = text.find("(", i)
    if start < 0:
        raise ValueError(f"module '{name}' has no port list")
    end = skip_parens(text, start)
    return name, text[start + 1:end - 1], text[end:]


def skip_parens(text, open_idx):
    """Return the index just past the parenthesis opened at open_idx."""
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError("unbalanced parentheses in the module header")


def parse_range(decl, port_name):
    """Return (msb, lsb) of a packed range in decl, or (None, None)."""
    m = re.search(r"\[([^\]]*)\]", decl)
    if not m:
        return None, None
    span = m.group(1)
    nums = re.fullmatch(r"\s*(\d+)\s*:\s*(\d+)\s*", span)
    if not nums:
        raise ValueError(
            f"port '{port_name}' has the unresolved bus range '[{span}]'. "
            f"Read the elaborated netlist netlist/pnl/<top>.pnl.v instead of "
            f"parameterised RTL."
        )
    return int(nums.group(1)), int(nums.group(2))


def parse_declarations(text, into, order=None):
    """Collect `input`/`output`/`inout` declarations from text into a dict."""
    for m in re.finditer(
        r"\b(input|output|inout)\b([^;,)]*?)((?:\s*,\s*\w+)*)\s*(?=[;,)]|$)",
        text,
    ):
        keyword, decl, extra = m.group(1), m.group(2), m.group(3)
        names = re.findall(r"(\w+)\s*$", decl)
        if not names:
            continue
        first = names[-1]
        rest = re.findall(r"\w+", extra)
        msb, lsb = parse_range(decl, first)
        for name in [first] + rest:
            into[name] = Port(name, DIR_OF_KEYWORD[keyword], msb, lsb)
            if order is not None and name not in order:
                order.append(name)


def parse_verilog_ports(path):
    """Return (module_name, [Port, ...]) in module-header order."""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = strip_comments(f.read())

    name, header, body = split_header(text)
    body = body.split("endmodule")[0]

    declared = {}
    if re.search(r"\b(input|output|inout)\b", header):
        # ANSI header: directions live in the port list itself.
        order = []
        parse_declarations(header, declared, order)
        ports = [declared[n] for n in order]
    else:
        # Non-ANSI header (what Yosys and LibreLane write): names in the
        # header, directions and ranges in the body.
        order = re.findall(r"\w+", header)
        parse_declarations(body, declared)
        missing = [n for n in order if n not in declared]
        if missing:
            raise ValueError(
                f"module '{name}' lists {missing} in its header but never "
                f"declares their direction"
            )
        ports = [declared[n] for n in order]

    if not ports:
        raise ValueError(f"module '{name}' has no ports")
    return name, ports


# --------------------------------------------------------------------------
# Symbol side
# --------------------------------------------------------------------------

class SymPin:
    """One `B 5` pin line of a .sym file, bus range not yet expanded."""

    def __init__(self, display, direction, sim_pinname, lineno):
        self.display = display
        self.direction = direction
        self.sim_pinname = sim_pinname
        self.lineno = lineno

    @property
    def base(self):
        """Display name without its bus range."""
        m = BUS_RANGE_RE.match(self.display)
        return m.group(1) if m else self.display

    def nets(self):
        """Netlist-side names this pin covers, [] if it declares none.

        Mirrors sak-pin-reorder.py: a bus `sim_pinname` may be given as a
        bare base, and the symbol's own bus indices are applied to it.
        """
        if self.sim_pinname is None:
            return []
        m = BUS_RANGE_RE.match(self.display)
        if not m:
            return [self.sim_pinname]
        a, b = int(m.group(2)), int(m.group(3))
        step = 1 if a <= b else -1
        rm = BUS_RANGE_RE.match(self.sim_pinname)
        rbase = rm.group(1) if rm else self.sim_pinname
        return [f"{rbase}[{i}]" for i in range(a, b + step, step)]


def parse_sym_pins(path):
    """Return the pins of a .sym file as [SymPin, ...] in file order."""
    pins = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            m = PIN_RE.match(line.strip())
            if not m:
                continue
            props = SIM_PINNAME_RE.search(m.group(3))
            pins.append(SymPin(m.group(1), m.group(2),
                               props.group(1) if props else None, lineno))
    return pins


# --------------------------------------------------------------------------
# Generate
# --------------------------------------------------------------------------

def num(value):
    """Format a coordinate the way Xschem writes it."""
    value = round(value + 0.0, 4)
    return str(int(value)) if float(value).is_integer() else str(value)


def place(ports, power, ground):
    """Split the ports over the four edges of the body."""
    top = [p for p in ports if p.direction == "inout" and p.name in power]
    bottom = [p for p in ports if p.direction == "inout" and p.name in ground]
    left = [p for p in ports if p.direction == "in"]
    right = [p for p in ports if p.direction == "out"]
    right += [p for p in ports if p.direction == "inout"
              and p.name not in power and p.name not in ground]
    return top, bottom, left, right


def body_width(left, right, top, bottom):
    """Smallest on-grid half-width that keeps the pin labels apart."""
    def longest(side):
        return max((len(p.display) for p in side), default=0)

    needed = 35 + (longest(left) + longest(right)) * CHAR_W / 2 + LABEL_GAP / 2
    # A row of supply stubs must fit between the body corners as well.
    spread = (max(len(top), len(bottom), 1) - 1) * PITCH / 2 + STUB + PITCH / 2
    width = max(MIN_WIDTH, needed, spread + STUB)
    return int(-(-width // 20) * 20)


def emit_symbol(cell, ports, power, ground, sym_type):
    """Return the .sym file content for one module as a list of lines."""
    top, bottom, left, right = place(ports, power, ground)

    rows = max(len(left), len(right), 1)
    y0 = -(rows - 1) / 2 * PITCH
    box_top = y0 - PITCH / 2
    box_bottom = y0 + rows * PITCH - PITCH / 2

    width = body_width(left, right, top, bottom)
    box_right = width - STUB
    box_left = -box_right

    def row_y(i):
        return y0 + i * PITCH

    def col_x(count, i):
        return (i - (count - 1) / 2) * PITCH

    # (port, pin x, pin y, stub start, label x, label flip)
    placed = []
    for i, p in enumerate(top):
        x = col_x(len(top), i)
        placed.append((p, x, box_top - STUB, (x, box_top),
                       x - TEXTDIST, 1))
    for i, p in enumerate(bottom):
        x = col_x(len(bottom), i)
        placed.append((p, x, box_bottom + STUB, (x, box_bottom),
                       x - TEXTDIST, 1))
    for i, p in enumerate(left):
        y = row_y(i)
        placed.append((p, -width, y, (box_left, y),
                       box_left + TEXTDIST, 0))
    for i, p in enumerate(right):
        y = row_y(i)
        placed.append((p, width, y, (box_right, y),
                       box_right - TEXTDIST, 1))

    out = [SYM_HEADER, "G {}"]
    out.append(f"K {{type={sym_type}")
    out.append('format="@name @pinlist @symname"')
    out.append('spectre_format="@name ( @pinlist ) @symname"')
    out.append('template="name=x1"}')
    out += ["V {}", "S {}", "F {}", "E {}"]

    # L: the pin stubs. Xschem draws bidirectional stubs on layer 7.
    for p, px, py, (sx, sy), _, _ in placed:
        layer = LAYER_INOUT if p.direction == "inout" else LAYER_BODY
        out.append(f"L {layer} {num(px)} {num(py)} {num(sx)} {num(sy)} {{}}")

    # B 5: the pins. This order is the @pinlist order.
    for p, px, py, _, _, _ in placed:
        out.append(
            f"B {LAYER_PIN} {num(px - PIN_HALF)} {num(py - PIN_HALF)} "
            f"{num(px + PIN_HALF)} {num(py + PIN_HALF)} "
            f"{{name={p.display} dir={p.direction} sim_pinname={p.name}}}"
        )

    # P: the body outline.
    corners = [(box_left, box_top), (box_right, box_top),
               (box_right, box_bottom), (box_left, box_bottom),
               (box_left, box_top)]
    out.append(f"P {LAYER_BODY} {len(corners)} "
               + " ".join(f"{num(x)} {num(y)}" for x, y in corners) + " {}")

    # T: the instance texts above the body, then one label per pin.
    out.append(f"T {{@symname}} 20 {num(box_top - 21)} 0 0 "
               f"{LABSIZE} {LABSIZE} {{}}")
    out.append(f"T {{@name}} 20 {num(box_top - 37)} 0 0 "
               f"{LABSIZE} {LABSIZE} {{}}")
    for p, _, py, _, lx, flip in placed:
        out.append(f"T {{{p.display}}} {num(lx)} {num(py - LAB_VOFFSET)} "
                   f"0 {flip} {LABSIZE} {LABSIZE} {{}}")

    return out


# --------------------------------------------------------------------------
# Check
# --------------------------------------------------------------------------

def check_symbol(sym_path, module, ports, pins):
    """Return the list of problems found in one symbol."""
    problems = []

    if not pins:
        return [f"{sym_path}: no `B 5 ... {{name=... dir=...}}` pin lines found"]

    # 1. The house rule that makes name matching work at all. Without
    #    sim_pinname on every pin, sak-pin-reorder.py falls back to matching
    #    pins by position, and the ports of an extracted netlist are sorted
    #    alphabetically, so the fallback mis-wires the macro.
    unnamed = [p for p in pins if p.sim_pinname is None]
    for p in unnamed:
        problems.append(
            f"{sym_path}:{p.lineno}: pin '{p.display}' has no sim_pinname. "
            f"Every pin needs sim_pinname=<netlist name>, otherwise "
            f"sak-pin-reorder.py matches pins by position instead of by name."
        )
    if unnamed:
        return problems  # the rest of the comparison would be meaningless

    # 2. The pin set has to be the port set, in both directions.
    sym_nets, owner = [], {}
    for p in pins:
        for net in p.nets():
            sym_nets.append(net)
            owner.setdefault(net, p)
    netlist_nets = [n for p in ports for n in p.nets]

    duplicates = sorted({n for n in sym_nets if sym_nets.count(n) > 1})
    for net in duplicates:
        problems.append(
            f"{sym_path}: several pins map to the netlist port '{net}'"
        )

    for net in sorted(set(netlist_nets) - set(sym_nets)):
        problems.append(
            f"{sym_path}: module '{module}' has the port '{net}', but no pin "
            f"declares sim_pinname={net}. Add the pin to the symbol."
        )
    for net in sorted(set(sym_nets) - set(netlist_nets)):
        pin = owner[net]
        problems.append(
            f"{sym_path}:{pin.lineno}: pin '{pin.display}' expects the port "
            f"'{net}', which module '{module}' does not have."
        )

    # 3. Directions, which nothing downstream checks.
    by_name = {p.name: p for p in ports}
    for pin in pins:
        base = pin.sim_pinname
        m = BUS_RANGE_RE.match(base)
        if m:
            base = m.group(1)
        port = by_name.get(base)
        if port and port.direction != pin.direction:
            problems.append(
                f"{sym_path}:{pin.lineno}: pin '{pin.display}' is dir="
                f"{pin.direction}, but '{port.name}' is an "
                f"{KEYWORD_OF_DIR[port.direction]} port of module "
                f"'{module}'."
            )

    return problems


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build or check an Xschem symbol from Verilog netlist ports."
    )
    parser.add_argument("netlist", help="Verilog netlist, e.g. netlist/pnl/<top>.pnl.v")
    parser.add_argument("symbol", help="Xschem symbol to write or to check")
    parser.add_argument("--check", action="store_true",
                        help="check the existing symbol instead of writing one")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing symbol (discards hand edits)")
    parser.add_argument("--power", default="VDD",
                        help="comma-separated supply ports, drawn on top "
                             "(default: VDD)")
    parser.add_argument("--ground", default="VSS",
                        help="comma-separated ground ports, drawn at the "
                             "bottom (default: VSS)")
    parser.add_argument("--type", default="primitive",
                        choices=["primitive", "subcircuit"],
                        help="symbol type (default: primitive, because the "
                             "subcircuit comes from an included netlist)")
    args = parser.parse_args()

    if not os.path.isfile(args.netlist):
        print(f"[ERROR] {args.netlist} not found. Harden the macro and run "
              f"'make copy-netlist' to bring its netlists into the tree.",
              file=sys.stderr)
        return 1
    if args.check and not os.path.isfile(args.symbol):
        print(f"[ERROR] {args.symbol} not found. Run 'make symbol-gl' to "
              f"scaffold it from the ports of {args.netlist}, then arrange "
              f"it in Xschem and commit it.", file=sys.stderr)
        return 1

    module, ports = parse_verilog_ports(args.netlist)

    if args.check:
        print(f"[INFO] Checking {args.symbol} against the ports of "
              f"'{module}' in {args.netlist} ...")
        pins = parse_sym_pins(args.symbol)
        problems = check_symbol(args.symbol, module, ports, pins)
        for problem in problems:
            print(f"[ERROR] {problem}", file=sys.stderr)
        if problems:
            print(f"[ERROR] {len(problems)} problem(s) found. The symbol does "
                  f"not describe module '{module}'.", file=sys.stderr)
            return 1
        print(f"[INFO] {len(pins)} pins match the {len(ports)} ports of "
              f"'{module}'.")
        return 0

    if os.path.exists(args.symbol) and not args.force:
        print(f"[ERROR] {args.symbol} already exists. The symbol is a source "
              f"file: beautified pin positions, house pin names and the body "
              f"drawing live in it and would be lost. Use --check to verify "
              f"it, or --force to overwrite it anyway.", file=sys.stderr)
        return 1

    power = {s for s in args.power.split(",") if s}
    ground = {s for s in args.ground.split(",") if s}
    lines = emit_symbol(module, ports, power, ground, args.type)

    directory = os.path.dirname(args.symbol)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(args.symbol, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[INFO] Wrote {args.symbol}: {len(ports)} ports of '{module}' as "
          f"{sum(1 for line in lines if line.startswith('B 5'))} pins.")
    print("[INFO] It is a scaffold. Open it in Xschem, rename the pins to "
          "house style, arrange them and draw the body, then commit it.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
