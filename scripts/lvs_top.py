#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Top-level LVS: builds the transistor-level reference netlist of the chip, runs Magic + Netgen on it, and checks the result of KLayout or Netgen.
#
# LibreLane's own LVS compares the DEF with every cell and macro as a LEF abstract.
# This one compares the GDS with a reference netlist assembled from the netlists the GDS was made from (flow/lvs/config.yaml): the powered Verilog of the chip and of every digital macro, the cell netlists of the PDK and the LVS netlist of every analog macro.
# Every cell is compared at device level, except a black box that config.yaml lists with its reason.
# Each change made to the input netlists is printed and written into the header of the reference netlist.
#
# usage: lvs_top.py netlist --engine klayout|magic --top <top> --cell <cell> [-o <file>] [--plant <spec>]
#        lvs_top.py magic --top <top> --cell <cell> [--gds <file>] [--ref <file>] [--work <dir>]
#        lvs_top.py check --engine klayout|magic [--top <top>] --cell <cell> [--work <dir>]
# <cell> is the top cell of layout/<cell>.gds.gz: <top> itself, or a wrapper cell that holds <top>.
import argparse
import collections
import gzip
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(ROOT, "flow", "lvs", "config.yaml")
SUFFIX = {"klayout": "_klayout.cdl", "magic": "_magic.spice"}
TAPS = ("ptap1", "ntap1")

log = []


def say(msg):
    log.append(msg)
    print("[lvs_top] " + msg, flush=True)


def die(msg):
    sys.exit("[lvs_top] ERROR: " + msg)


def rel(path):
    """A path as written into reports: relative to the repo, or under $PDK_ROOT."""
    pdk_root = os.environ.get("PDK_ROOT", "")
    if pdk_root and path.startswith(pdk_root + "/"):
        return "$PDK_ROOT/" + path[len(pdk_root) + 1:]
    return os.path.relpath(path, ROOT)


def md5(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# --- configuration -------------------------------------------------------------------------------------------------
def load_config():
    import yaml
    with open(CONFIG, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    for key in ("verilog", "cells"):
        if key not in cfg:
            die("%s has no '%s'" % (rel(CONFIG), key))
    return cfg


def path_of(entry):
    """pdk_dir::<path> is relative to the PDK, every other path to the repo."""
    if entry.startswith("pdk_dir::"):
        return os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], entry[len("pdk_dir::"):])
    return os.path.join(ROOT, entry)


# --- netlist cards -------------------------------------------------------------------------------------------------
class Block:
    """One subcircuit: its ports and its cards, each card a list of tokens."""

    def __init__(self, name, ports, cards, src):
        self.name, self.ports, self.cards, self.src = name, list(ports), cards, src
        self.orig_ports = list(ports)
        self.mapped = {}
        self.sub_net = None


def x_parts(t):
    """(nodes, cell, params) of an X card."""
    plain = [i for i, x in enumerate(t) if "=" not in x]
    last = plain[-1]
    return t[1:last], t[last], t[last + 1:]


def node_slots(t):
    """Indices of the node tokens of a card."""
    k = t[0][0].upper()
    if k == "X":
        last = [i for i, x in enumerate(t) if "=" not in x][-1]
        return list(range(1, last))
    if k == "M":
        return [1, 2, 3, 4]
    if k in "DRC":
        return [1, 2]
    if k == "Q":
        last = [i for i, x in enumerate(t) if "=" not in x][-1]
        return list(range(1, last))
    die("unknown card " + " ".join(t))


def to_x(t):
    """A CDL device card in the X form Magic writes, for Netgen, None if there is none."""
    k = t[0][0].upper()
    name = "X" + t[0]
    if k == "M":
        return [name] + t[1:]
    if k == "D":
        return [name] + t[1:4] + [p for p in t[4:] if not p.lower().startswith(("a=", "p="))]
    if k == "C" and len(t) > 3 and "=" not in t[3]:
        return [name] + t[1:]
    if k == "R":
        sub = [x[5:] for x in t if x.upper().startswith("$SUB=")]
        model = [x[2:-1] for x in t if x.startswith("$[")]
        if sub and model:
            rest = [x for x in t[3:] if not x.upper().startswith("$SUB=") and not x.startswith("$[")]
            return [name, t[1], t[2], sub[0], model[0]] + [x for x in rest if "=" in x]
        if len(t) > 3 and "=" not in t[3] and not re.match(r"[-+.\d]", t[3]):
            return [name] + t[1:]
    return None


def logical_lines(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            s = raw.strip()
            if s.startswith("+") and out:
                out[-1] += " " + s[1:].strip()
            else:
                out.append(s)
    return out


def unbang(engine, name):
    """Magic writes a net name that ends in ! (a global net in CDL) without the !."""
    return name[:-1] if engine == "magic" and name.endswith("!") else name


def read_netlist(path, lib, engine):
    cur = None
    for s in logical_lines(path):
        if not s or s[0] in "*$":
            continue
        low = s.lower()
        if low.startswith(".subckt"):
            t = s.split()
            cur = Block(t[1], [unbang(engine, p) for p in t[2:] if "=" not in p], [], path)
        elif low.startswith(".ends"):
            if cur is None:
                continue
            old = lib.get(cur.name)
            if old is not None and old.cards != cur.cards:
                die("%s is defined twice, differently, in %s and %s" % (cur.name, rel(old.src), rel(path)))
            lib[cur.name] = cur
            cur = None
        elif cur is not None and s[0] != ".":
            t = [x for x in s.split() if x != "/"]
            if engine == "magic" and t[0][0].upper() in "MDRC":
                # a card without a Netgen form stays as it is, emit() stops if it ends up in the reference
                t = to_x(t) or t
            for i in node_slots(t):
                t[i] = unbang(engine, t[i])
            cur.cards.append(t)


# --- reference fixes -----------------------------------------------------------------------------------------------
def edit_cards(lib, edits):
    """Token replacements in single cards, per cell and card name.
    An empty value deletes the token, a value with spaces becomes several tokens."""
    for cell, devices in edits.items():
        if cell not in lib:
            die("card_edit: no cell %s" % cell)
        for dev, swap in devices.items():
            hit = [t for t in lib[cell].cards if t[0] == dev]
            if len(hit) != 1:
                die("card_edit: no single card %s in %s" % (dev, cell))
            t = hit[0]
            for old, new in swap.items():
                if old not in t:
                    die("card_edit: %s in %s has no %s" % (dev, cell, old))
                i = t.index(old)
                t[i:i + 1] = new.split()
            say("card edit: %s in %s: %s" % (dev, cell, ", ".join("%s -> %s" % (o, n or "(deleted)") for o, n in swap.items())))


def rename_cells(lib, rules):
    """A cell netlist under the names its GDS uses, connections unchanged.
    A rule swaps the prefix from for to and renames single tails (cells), for library cells only, never for device models."""
    cells = set(lib)

    def new_name(n):
        for r in rules:
            if n in cells and n.startswith(r["from"]):
                tail = n[len(r["from"]):]
                return r["to"] + r.get("cells", {}).get(tail, tail)
        return n
    n = 0
    for old in list(lib):
        b = lib[old]
        for t in b.cards:
            if t[0][0].upper() == "X":
                nodes, cell, params = x_parts(t)
                t[len(nodes) + 1] = new_name(cell)
        if new_name(old) != old:
            del lib[old]
            b.name = new_name(old)
            if b.name in lib:
                die("rename: %s collides with an existing cell" % b.name)
            lib[b.name] = b
            n += 1
    if n:
        say("rename: %d cells take the names of their GDS" % n)


def tap_merge(b, substrate):
    """Removes ptap1/ntap1 cards and merges their two nets, the reference twin of a layout without tap devices."""
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x

    keep, n = [], 0
    for t in b.cards:
        if t[0][0].upper() == "X" and x_parts(t)[1] in TAPS:
            n += 1
            ra, rb = find(t[1]), find(t[2])
            if ra != rb:
                if rb in b.ports and ra not in b.ports:
                    ra, rb = rb, ra
                parent[rb] = ra
            continue
        keep.append(t)
    if not n:
        return
    b.sub_net = find(substrate) if any(substrate in c for c in b.cards) else None
    cards = []
    for t in keep:
        t = list(t)
        for i in node_slots(t):
            t[i] = find(t[i])
        t = [x[:5] + find(x[5:]) if x.upper().startswith("$SUB=") else x for x in t]
        cards.append(t)
    b.cards = cards
    b.ports = [find(p) for p in b.orig_ports]
    b.mapped = dict(zip(b.orig_ports, b.ports))
    b.ports = list(dict.fromkeys(b.ports))
    say("tap merge: %s, %d tap cards removed, ports %s" % (b.name, n, " ".join(b.ports)))


def has_devices(b, lib, no_devices, black=()):
    if b.name in black:
        return True
    for t in b.cards:
        if t[0][0].upper() != "X":
            return True
        _, cell, _ = x_parts(t)
        if cell in no_devices:
            continue
        if cell not in lib or has_devices(lib[cell], lib, no_devices, black):
            return True
    return False


# --- Verilog -------------------------------------------------------------------------------------------------------
TOK = re.compile(r"\\\S+|[A-Za-z_][\w$]*|\d+'[bBhHdD][0-9a-fA-FxXzZ_]+|\d+|[()\[\]{},;.:#=]")


class Module:
    def __init__(self, name):
        self.name, self.header, self.widths, self.insts, self.assigns = name, [], {}, [], []


def read_verilog(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    tk = [t[1:] if t[0] == "\\" else t for t in TOK.findall(text)]
    i, mods = 0, {}

    def expr():
        nonlocal i
        if tk[i] == "{":
            i += 1
            out = []
            while tk[i] != "}":
                out += expr()
                if tk[i] == ",":
                    i += 1
            i += 1
            return out
        name = tk[i]
        i += 1
        if re.match(r"\d+'", name):
            die("constant %s on a pin in %s" % (name, rel(path)))
        if tk[i] == "[":
            msb = tk[i + 1]
            if tk[i + 2] == ":":
                lsb = tk[i + 3]
                i += 5
                step = 1 if int(lsb) >= int(msb) else -1
                return ["%s[%d]" % (name, b) for b in range(int(msb), int(lsb) + step, step)]
            i += 3
            return ["%s[%s]" % (name, msb)]
        return [name]

    while i < len(tk):
        if tk[i] != "module":
            i += 1
            continue
        m = Module(tk[i + 1])
        i += 2
        if tk[i] == "(":
            i += 1
            while tk[i] != ")":
                if tk[i] != ",":
                    m.header.append(tk[i])
                i += 1
            i += 1
        i += 1
        while tk[i] != "endmodule":
            word = tk[i]
            if word in ("input", "output", "inout", "wire"):
                i += 1
                rng = None
                if tk[i] == "[":
                    rng = (int(tk[i + 1]), int(tk[i + 3]))
                    i += 5
                while tk[i] != ";":
                    if tk[i] != "," and word != "wire":
                        m.widths[tk[i]] = rng
                    i += 1
                i += 1
            elif word == "assign":
                i += 1
                a = expr()
                i += 1
                b = expr()
                i += 1
                m.assigns += list(zip(a, b))
            else:
                cell, inst = tk[i], tk[i + 1]
                i += 2
                if tk[i] != "(":
                    die("no port list at %s %s in %s" % (cell, inst, rel(path)))
                i += 1
                con = {}
                while tk[i] != ")":
                    if tk[i] == ",":
                        i += 1
                        continue
                    pin = tk[i + 1]
                    i += 3
                    con[pin] = [] if tk[i] == ")" else expr()
                    i += 1
                i += 2
                m.insts.append((cell, inst, con))
        mods[m.name] = m
        i += 1
    return mods


def bits(name, rng):
    if rng is None:
        return [name]
    a, b = rng
    step = 1 if b >= a else -1
    return ["%s[%d]" % (name, x) for x in range(a, b + step, step)]


def bus_ports(b, pin):
    """The bit ports of a bus pin of a cell netlist (A<3> or A[3]), highest index first, as Verilog connects them."""
    found = []
    for p in b.orig_ports:
        m = re.match(re.escape(pin) + r"[<\[](\d+)[>\]]$", p)
        if m:
            found.append((int(m.group(1)), p))
    return [p for _, p in sorted(found, reverse=True)]


def module_block(m, lib, mods, cfg, engine):
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x

    portbits = [bb for p in m.header for bb in bits(p, m.widths.get(p))]

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            if rb in portbits and ra not in portbits:
                ra, rb = rb, ra
            parent[rb] = ra

    for a, b in m.assigns:
        union(a, b)
    no_devices = set(cfg.get("no_devices", []))
    pin_alias = cfg.get("pin_alias", {}) or {}
    rows, skipped = [], collections.Counter()
    for cell, inst, con in m.insts:
        if cell in no_devices:
            skipped[cell] += 1
            continue
        if cell in mods:
            mod = mods[cell]
            ports = [bb for p in mod.header for bb in bits(p, mod.widths.get(p))]
            flat = {}
            for p in mod.header:
                nets, names = con.get(p, []), bits(p, mod.widths.get(p))
                if nets and len(nets) != len(names):
                    die("%s.%s has %d nets for %d bits" % (inst, p, len(nets), len(names)))
                for k, n in enumerate(names):
                    flat[n] = nets[k] if nets else None
            rows.append((cell, inst, ports, flat))
            continue
        if cell not in lib:
            die("cell %s (instance %s in %s) is in no cell netlist of %s" % (cell, inst, m.name, rel(CONFIG)))
        b = lib[cell]
        con = {unbang(engine, p): nets for p, nets in con.items()}
        for alias, target in pin_alias.get(cell, {}).items():
            if alias in con:
                if con[alias] and con.get(target):
                    union(con[target][0], con[alias][0])
                del con[alias]
        flat = {}
        for p, nets in con.items():
            if len(nets) > 1 or (nets and p not in b.orig_ports and bus_ports(b, p)):
                names = bus_ports(b, p)
                if len(names) != len(nets):
                    die("bus pin %s of %s has %d nets for %d ports of %s" % (p, inst, len(nets), len(names), cell))
                flat.update(zip(names, nets))
                continue
            if p not in b.orig_ports:
                die("pin %s of instance %s is not a port of %s (%s)" % (p, inst, cell, " ".join(b.orig_ports)))
            if nets:
                flat[p] = nets[0]
        rows.append((cell, inst, b.orig_ports, flat))
    if skipped:
        say("%s: cells without devices left out: %s" % (m.name, dict(sorted(skipped.items()))))
    cards = []
    for cell, inst, ports, flat in rows:
        nodes = [find(flat[p]) if flat.get(p) is not None else "_nc_%s_%s" % (inst, p) for p in ports]
        cards.append(["X" + inst] + nodes + [cell])
    ports = list(dict.fromkeys(find(p) for p in portbits))
    return Block(m.name, ports, cards, "verilog")


# --- flatten -------------------------------------------------------------------------------------------------------
def port_map(child, nodes, clashes=None):
    if len(nodes) != len(child.orig_ports):
        die("a call of %s has %d nets for its %d ports" % (child.name, len(nodes), len(child.orig_ports)))
    pm = {}
    for p, n in zip(child.orig_ports, nodes):
        key = child.mapped.get(p, p)
        if key in pm and pm[key] != n:
            if clashes is None:
                die("%s: merged port %s gets two nets, %s and %s" % (child.name, key, pm[key], n))
            clashes.append((n, pm[key]))
            continue
        pm[key] = n
    return pm


def merge_net(b, a, keep):
    """Renames net a to keep in block b, ports included."""
    if a == keep:
        return
    if a in b.ports and keep not in b.ports:
        a, keep = keep, a
    for t in b.cards:
        for i in node_slots(t):
            if t[i] == a:
                t[i] = keep
        for i, x in enumerate(t):
            if x.upper().startswith("$SUB=") and x[5:] == a:
                t[i] = x[:5] + keep
    for orig in b.orig_ports:
        if b.mapped.get(orig, orig) == a:
            b.mapped[orig] = keep
    b.ports = list(dict.fromkeys(keep if p == a else p for p in b.ports))
    if b.sub_net == a:
        b.sub_net = keep
    say("substrate: %s joins %s and %s" % (b.name, a, keep))


def expand(parent, names, lib, substrate):
    """Expands every call of the named cells in parent into their devices, deepest first."""
    again, joins, n = True, [], collections.Counter()
    while again:
        again = False
        out = []
        for t in parent.cards:
            if t[0][0].upper() == "X":
                nodes, cell, params = x_parts(t)
                if cell in names and cell in lib:
                    again = True
                    n[cell] += 1
                    child = lib[cell]
                    pm = port_map(child, nodes, joins)
                    if child.sub_net in pm and parent.sub_net:
                        joins.append((pm[child.sub_net], parent.sub_net))
                    inst = t[0][1:]
                    sub = parent.sub_net or substrate

                    def ren(net):
                        # an unconnected pin of the expanded cell still leaves its child cells in the layout
                        if net in pm and not pm[net].startswith("_nc_"):
                            return pm[net]
                        if net == substrate:
                            return sub
                        return "%s.%s" % (inst, net)

                    for c in child.cards:
                        c = list(c)
                        for i in node_slots(c):
                            c[i] = ren(c[i])
                        c = [x[:5] + ren(x[5:]) if x.upper().startswith("$SUB=") else x for x in c]
                        c[0] = c[0][0] + inst + "." + c[0][1:]
                        out.append(c)
                    continue
            out.append(t)
        parent.cards = out
    for a, keep in joins:
        merge_net(parent, a, keep)
    if n:
        say("flatten: in %s, %s" % (parent.name, ", ".join("%d x %s" % (k, c) for c, k in sorted(n.items()))))


# --- output --------------------------------------------------------------------------------------------------------
def gds_table(path):
    """Child cell names of every cell of the GDS."""
    import klayout.db as db
    ly = db.Layout()
    ly.read(path)
    return {c.name: {ly.cell(i.cell_index).name for i in c.each_inst()} for c in ly.each_cell()}


def base(name):
    return re.sub(r"(\$\d+)+$", "", name)


def emit(top, lib, table, no_devices, black, engine, top_label=None):
    """The subcircuits reachable from top, each library cell under the name of its copy in the GDS parent.
    With top_label the top is written under that name and without pins."""
    out, done, renames = [], set(), collections.Counter()

    def calls(name, gname):
        """(card, child cell, GDS name of the child, net of each child port) for the subcircuit calls of a cell."""
        kids = table.get(gname, set())
        for t in lib[name].cards:
            if t[0][0].upper() != "X":
                continue
            nodes, cell, params = x_parts(t)
            if cell in no_devices or cell not in lib or not has_devices(lib[cell], lib, no_devices, black):
                continue
            gchild = cell
            if cell not in kids:
                cands = sorted(k for k in kids if base(k) == base(cell))
                if len(cands) == 1:
                    gchild = cands[0]
                elif len(cands) > 1:
                    die("%s in %s has several copies in the GDS: %s" % (cell, gname, cands))
            yield t, cell, gchild, port_map(lib[cell], nodes)

    # KLayout gives a layout cell a pin only for a net that leaves the cell, so a port no call connects is no pin
    used, seen = collections.defaultdict(set), set()

    def scan(name, gname, label):
        if label in seen:
            return
        seen.add(label)
        for t, cell, gchild, pm in calls(name, gname):
            used[gchild] |= {p for p in lib[cell].ports if not pm[p].startswith("_nc_")}
            scan(cell, gchild if gchild in table else cell, gchild)

    def ports_of(b, label):
        if engine == "klayout" and label != (top_label or top):
            return [p for p in b.ports if p in used[label]]
        return b.ports

    def write(name, gname, label):
        if label in done:
            return
        done.add(label)
        b = lib[name]
        body = []
        for t in b.cards:
            if t[0][0].upper() == "X":
                continue
            if engine == "magic":
                die("%s holds a card Netgen has no form for: %s" % (name, " ".join(t)))
            body.append(" ".join(t))
        for t in b.cards:
            if t[0][0].upper() == "X" and x_parts(t)[1] not in lib and x_parts(t)[1] not in no_devices:
                body.append(" ".join(t))
        for t, cell, gchild, pm in calls(name, gname):
            if gchild != cell:
                renames[(gname, cell, gchild)] += 1
            write(cell, gchild if gchild in table else cell, gchild)
            body.append(" ".join([t[0]] + [pm[p] for p in ports_of(lib[cell], gchild)] + [gchild] + x_parts(t)[2]))
        dropped = [p for p in b.ports if p not in ports_of(b, label)]
        if dropped:
            say("unconnected ports: %s, no call connects %s" % (label, " ".join(dropped)))
        out.append(".SUBCKT %s" % label if label == top_label else ".SUBCKT %s %s" % (label, " ".join(ports_of(b, label))))
        out.extend(body)
        out.append(".ENDS")
        out.append("")

    scan(top, top, top_label or top)
    write(top, top, top_label or top)
    for (g, c, gc), n in sorted(renames.items()):
        say("copy under the GDS name: in %s, %d x %s called as %s" % (g, n, c, gc))
    return out


def plant(lib, spec):
    """A planted defect for a negative control: <cell>/<instance>:<pin>,<pin> swaps two nets, <cell>/<instance>:<param>=<value> sets a parameter.
    The instance is named without its card letter (M1 for MM1 and XM1), as both engines' netlists differ in it."""
    m = re.match(r"([^/]+)/([^:]+):(.+)$", spec)
    if not m or m.group(1) not in lib:
        die("--plant wants <cell>/<instance>:<pin>,<pin> or <cell>/<instance>:<param>=<value>, got %s" % spec)
    b, inst, what = lib[m.group(1)], m.group(2), m.group(3)
    for t in b.cards:
        if t[0][1:] != inst:
            continue
        if "=" in what:
            key = what.split("=")[0].lower() + "="
            hit = [i for i, x in enumerate(t) if x.lower().startswith(key)]
            if not hit:
                die("--plant: %s has no parameter %s" % (inst, key))
            t[hit[0]] = what
        else:
            pa, pb = what.split(",")
            cell = x_parts(t)[1] if t[0][0].upper() == "X" else None
            # a subcircuit call has the ports of its cell, a transistor (M card, or the X card Magic reads) d g s b
            names = lib[cell].orig_ports if cell in lib else ["d", "g", "s", "b"]
            if pa not in names or pb not in names:
                die("--plant: %s has no pins %s and %s, only %s" % (inst, pa, pb, " ".join(names)))
            ia, ib = names.index(pa) + 1, names.index(pb) + 1
            t[ia], t[ib] = t[ib], t[ia]
        say("PLANTED DEFECT: %s in %s: %s" % (inst, b.name, what))
        return
    die("--plant: no card %s in %s" % (inst, b.name))


def build(args):
    cfg = load_config()
    engine = args.engine
    substrate = unbang(engine, cfg.get("substrate", "sub!"))
    no_devices = set(cfg.get("no_devices", []))
    inputs, lib = [], {}
    for entry in cfg["cells"][engine]:
        path = path_of(entry)
        if not os.path.isfile(path):
            die("cell netlist %s not found" % entry)
        inputs.append(path)
        read_netlist(path, lib, engine)
    edit_cards(lib, (cfg.get("card_edit", {}) or {}).get(engine, {}) or {})
    rename_cells(lib, cfg.get("rename", []) or [])
    mods = {}
    for entry in cfg["verilog"]:
        path = path_of(entry)
        if not os.path.isfile(path):
            die("Verilog netlist %s not found" % entry)
        inputs.append(path)
        mods.update(read_verilog(path))
    if args.top not in mods:
        die("no module %s in %s" % (args.top, ", ".join(cfg["verilog"])))
    # the macros first, so that the chip top can read their ports
    for name in sorted(mods, key=lambda n: n == args.top):
        lib[name] = module_block(mods[name], lib, mods, cfg, engine)
    # only the cells the chip uses, the libraries hold many more
    used, todo = set(), [args.top]
    while todo:
        name = todo.pop()
        if name in used or name not in lib:
            continue
        used.add(name)
        todo += [x_parts(t)[1] for t in lib[name].cards if t[0][0].upper() == "X"]
    lib = {n: b for n, b in lib.items() if n in used}
    # before the expansion, so that a defect in an expanded cell lands in its devices
    if args.plant:
        plant(lib, args.plant)
    for b in lib.values():
        tap_merge(b, substrate)
    top = lib[args.top]
    for group in cfg.get("join", []) or []:
        for net in group[1:]:
            merge_net(top, net, group[0])
        say("join: %s are one net in the layout, the substrate's" % ", ".join(group))
        top.sub_net = group[0]
    flat = set((cfg.get("flatten", {}) or {}).get(engine, []) or [])
    for b in list(lib.values()):
        expand(b, flat, lib, substrate)
    changed = True
    while changed:
        changed = False
        for b in lib.values():
            for t in b.cards:
                if t[0][0].upper() == "X":
                    nodes, cell, _ = x_parts(t)
                    if cell in lib:
                        clashes = []
                        port_map(lib[cell], nodes, clashes)
                        for a, keep in clashes:
                            merge_net(b, a, keep)
                            changed = True
    black = set((cfg.get("black_box", {}) or {}).get(engine, []) or [])
    for name in sorted(black):
        if name not in lib:
            die("black box %s is in no cell netlist" % name)
        lib[name].cards = []
        say("black box: %s is compared by its pin names only" % name)
    if engine == "magic":
        diodes, n = set(cfg.get("diode_wl", []) or []), 0
        for b in lib.values():
            for i, t in enumerate(b.cards):
                b.cards[i], hit = diode_wl(t, diodes)
                n += hit
        if n:
            say("diodes: %d diode cards get the longer side as w, as lvs_top.py magic writes the layout netlist" % n)
    gds = os.path.join(ROOT, "layout", args.cell + ".gds.gz")
    if not os.path.isfile(gds):
        die("layout %s not found" % rel(gds))
    table = gds_table(gds)
    if args.cell == args.top:
        lines = emit(args.top, lib, table, no_devices, black, engine)
    elif args.top not in table.get(args.cell, set()):
        die("the GDS cell %s does not hold %s" % (args.cell, args.top))
    elif engine == "klayout":
        # KLayout gives a cell pins only where its nets reach the parent, and the wrapper reaches none.
        # So the reference holds the chip as the wrapper itself, and the comparer flattens the layout cell of the chip into it.
        lines = emit(args.top, lib, table, no_devices, black, engine, top_label=args.cell)
        say("wrapper: %s holds %s, the reference writes the chip under the wrapper's name, without pins" % (args.cell, args.top))
    else:
        # Magic gives the chip its pins from its labels
        lines = emit(args.top, lib, table, no_devices, black, engine)
        lines += [".SUBCKT %s" % args.cell, " ".join(["X" + args.top] + top.ports + [args.top]), ".ENDS", ""]
        say("wrapper: %s holds %s and has no pins" % (args.cell, args.top))
    out = args.o or os.path.join(ROOT, "netlist", "schematic", args.cell + SUFFIX[engine])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("* Reference netlist of the top-level LVS of %s for %s, written by scripts/lvs_top.py\n" % (args.cell, "KLayout" if engine == "klayout" else "Netgen"))
        fh.write("* Inputs (MD5):\n")
        for p in inputs:
            fh.write("*   %s %s\n" % (md5(p), rel(p)))
        fh.write("*   %s %s\n" % (md5(gds), rel(gds)))
        fh.write("* Changes against the inputs:\n")
        for msg in log:
            fh.write("*   " + msg + "\n")
        fh.write("\n" + "\n".join(lines) + "\n")
    blocks = spice_blocks(out)
    print("[lvs_top] written %s (%d subcircuits, %d devices counted flat)" % (rel(out), len(blocks), flat_devices(blocks, args.cell)))


# --- Magic + Netgen ------------------------------------------------------------------------------------------------
def spice_blocks(path):
    """Subcircuits of a SPICE netlist: name -> (ports, cards)."""
    blocks, cur = {}, None
    for s in logical_lines(path):
        if not s or s[0] == "*":
            continue
        low = s.lower()
        if low.startswith(".subckt"):
            t = s.split()
            cur = t[1]
            blocks[cur] = ([p for p in t[2:] if "=" not in p], [])
        elif low.startswith(".ends"):
            cur = None
        elif cur is not None and s[0] != ".":
            blocks[cur][1].append(s.split())
    return blocks


def flat_devices(blocks, top):
    """Devices of top counted flat: an X card of an undefined cell is a device, as Magic writes them."""
    memo = {}

    def count(name):
        if name in memo:
            return memo[name]
        memo[name] = 0
        n = 0
        for t in blocks[name][1]:
            if t[0][0].upper() == "X":
                _, cell, _ = x_parts(t)
                n += count(cell) if cell in blocks else 1
            else:
                n += 1
        memo[name] = n
        return n

    return count(top) if top in blocks else 0


def si(value):
    """A SPICE number with a unit suffix as float."""
    m = re.match(r"([-+]?[\d.]+(?:[eE][-+]?\d+)?)(meg|[afpnumkgt])?", value.lower())
    scale = {"a": 1e-18, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6, "g": 1e9, "t": 1e12}
    return float(m.group(1)) * scale.get(m.group(2), 1.0)


def diode_wl(t, models):
    """Puts the longer side of a diode into w, Magic writes w and l in the order of the diode's orientation."""
    if t[0][0].upper() != "X" or x_parts(t)[1] not in models:
        return t, False
    iw = [i for i, x in enumerate(t) if x.lower().startswith("w=")]
    il = [i for i, x in enumerate(t) if x.lower().startswith("l=")]
    if not iw or not il or si(t[iw[0]][2:]) >= si(t[il[0]][2:]):
        return t, False
    t = list(t)
    t[iw[0]], t[il[0]] = "w=" + t[il[0]][2:], "l=" + t[iw[0]][2:]
    return t, True


def fix_layout_netlist(path, black, diodes):
    """The Magic netlist as Netgen compares it: black boxes keep only their port lists, diodes get w >= l."""
    out, inside, swapped = [], False, 0
    for s in logical_lines(path):
        t = s.split()
        if t and t[0].lower() == ".subckt":
            inside = t[1] in black
        elif t and t[0].lower() == ".ends":
            inside = False
        elif inside:
            continue
        elif t and diodes:
            t2, hit = diode_wl(t, diodes)
            if hit:
                s, swapped = " ".join(t2), swapped + 1
        out.append(s + "\n")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.writelines(out)
    return swapped


def run_magic(args):
    pdk, pdkpath = os.environ["PDK"], os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"])
    gds = os.path.abspath(args.gds) if args.gds else os.path.join(ROOT, "layout", args.cell + ".gds.gz")
    ref = args.ref or os.path.join(ROOT, "netlist", "schematic", args.cell + SUFFIX["magic"])
    work = args.work or os.path.join(ROOT, "verification", "lvs", args.cell + ".magic.lvs")
    for f in (gds, ref):
        if not os.path.isfile(f):
            die("%s not found" % rel(f))
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    raw = os.path.join(work, args.cell + ".lvstmp.gds")
    with gzip.open(gds, "rb") as fi, open(raw, "wb") as fo:
        shutil.copyfileobj(fi, fo)
    ext = os.path.join(work, args.cell + ".ext.spc")
    tcl = os.path.join(work, "ext_%s.tcl" % args.cell)
    cfg = load_config()
    flatglob = ["gds flatglob %s" % n for n in cfg.get("magic_flatten", []) or []]
    with open(tcl, "w", encoding="utf-8", newline="\n") as fh:
        # hierarchical: a flat extraction of the chip makes a compare that does not finish
        fh.write("\n".join([
            "crashbackups stop", "drc off"] + flatglob + ["gds read %s" % raw, "load %s" % args.cell, "select top cell",
            "extract path %s" % work, "extract no capacitance", "extract no coupling", "extract no resistance",
            "extract no length", "extract unique notopports", "extract all", "ext2spice lvs",
            # the top as a .subckt also when it has no ports (a wrapper), so that Netgen finds it by name
            "ext2spice subcircuit top on",
            "ext2spice -p %s -o %s" % (work, ext), "quit -noprompt", ""]))
    say("Magic extracts %s hierarchically" % rel(gds))
    with open(os.path.join(work, "magic.log"), "w", encoding="utf-8") as lg:
        subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", os.path.join(pdkpath, "libs.tech", "magic", pdk + ".magicrc"), tcl],
                       cwd=work, stdout=lg, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, check=False)
    for f in os.listdir(work):
        if f.endswith(".ext"):
            os.remove(os.path.join(work, f))
    os.remove(raw)
    if not os.path.isfile(ext):
        die("Magic wrote no netlist, see %s" % rel(os.path.join(work, "magic.log")))
    black = set((cfg.get("black_box", {}) or {}).get("magic", []) or [])
    swapped = fix_layout_netlist(ext, black, set(cfg.get("diode_wl", []) or []))
    if black:
        say("black box: %s emptied in the layout netlist, Netgen compares it by its pin names" % " ".join(sorted(black)))
    if swapped:
        say("diodes: %d layout diodes get the longer side as w" % swapped)
    # a layout cell without devices has nothing to compare, Netgen ignores it by its exact name
    blocks = spice_blocks(ext)
    empty = sorted(n for n in blocks if n != args.cell and n not in black and flat_devices(blocks, n) == 0)
    setup = os.path.join(work, "netgen_setup_%s.tcl" % args.cell)
    with open(setup, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Written by scripts/lvs_top.py: the PDK setup, then the changes below.\n")
        fh.write("source {%s}\n" % os.path.join(pdkpath, "libs.tech", "netgen", pdk + "_setup.tcl"))
        fh.write("# the Monte Carlo switch mm_ok of the Xschem netlists does not describe the layout\n")
        fh.write('foreach c [cells list -all -circuit1] { catch {property "-circuit1 $c" delete mm_ok} }\n')
        fh.write('foreach c [cells list -all -circuit2] { catch {property "-circuit2 $c" delete mm_ok} }\n')
        fh.write("# layout cells without devices\n")
        for n in empty:
            fh.write('catch {ignore class "-circuit1 %s"}\n' % n)
        extra = cfg.get("netgen_setup", []) or []
        if extra:
            fh.write("# from %s\n" % rel(CONFIG))
            fh.write("\n".join(extra) + "\n")
    say("Netgen compares, %d layout cells without devices ignored: %s" % (len(empty), " ".join(empty)))
    report = os.path.join(work, args.cell + ".lvs.out")
    env = dict(os.environ, MAGIC_EXT_USE_GDS="1")
    with open(os.path.join(work, args.cell + ".lvs.log"), "w", encoding="utf-8") as lg:
        subprocess.run(["netgen", "-batch", "lvs", "%s %s" % (ext, args.cell), "%s %s" % (ref, args.cell), setup, report]
                       + (["-blackbox"] if black else []),
                       cwd=work, stdout=lg, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env, check=False)
    sys.exit(check(argparse.Namespace(engine="magic", top=args.top, cell=args.cell, work=work)))


# --- verdict -------------------------------------------------------------------------------------------------------
def expected_port_mismatch(msg, cell, top, joins):
    """Why a port mismatch that KLayout reports follows from the reference fixes, or None for a real one."""
    m = re.match(r"Port mismatch '([^']*)' vs\. '([^']*)'$", msg)
    if not m:
        return None
    lay, ref = m.group(1).split(","), m.group(2).upper()
    if cell != top:
        # the chip is flattened into the wrapper, which has no labels: inner nets get no name, pad nets <instance>.<label>, one prefix per level
        lay = [re.sub(r"^(\$\d+\.)+", "", n) for n in lay]
        named = [n for n in lay if not re.fullmatch(r"\$I?\d+", n)]
        if not named:
            return "nets inside the chip, which the wrapper %s gives no name" % cell
        if all(n.upper() == ref for n in named):
            return "pad nets that the wrapper %s names <instance>.<label>, with the label of the reference" % cell
        lay = named
    for group in joins:
        if {n.upper() for n in lay} == {n.upper() for n in group} and ref == group[0].upper():
            return "the layout keeps both labels of the joined nets %s" % ", ".join(group)
    return None


def check(args):
    engine = args.engine
    top = args.top or args.cell
    work = args.work or os.path.join(ROOT, "verification", "lvs", "%s.%s.lvs" % (args.cell, engine))
    rows, ok = [], True
    if engine == "klayout":
        lvsdb = os.path.join(work, args.cell + ".lvsdb")
        if not os.path.isfile(lvsdb):
            die("no %s, the KLayout run failed (see the log in %s)" % (rel(lvsdb), rel(work)))
        status, bad, expected = collections.Counter(), [], collections.Counter()
        joins = load_config().get("join", []) or []
        circuit = None
        # the circuit pairs of the cross-reference section, X(<layout> <reference> <status> ...), () for none
        names = {"1": "Match", "W": "MatchWithWarning", "0": "NoMatch", "X": "Mismatch", "S": "Skipped"}
        with open(lvsdb, encoding="utf-8", errors="replace") as fh:
            xref = False
            for ln in fh:
                if ln.startswith("Z("):
                    xref = True
                elif xref:
                    if re.match(r"\s*M\(E\b", ln):
                        # an error inside a circuit pair, KLayout still counts the pair as matched
                        e = re.search(r"B\('((?:[^'\\]|\\.)*)'\)", ln)
                        if not e:
                            bad.append("%s: unparsed error %s" % (circuit, ln.strip()))
                            continue
                        msg = re.sub(r"\\(.)", r"\1", e.group(1))
                        why = expected_port_mismatch(msg, args.cell, top, joins)
                        if why:
                            expected[why] += 1
                        else:
                            bad.append("%s: %s" % (circuit, msg))
                        continue
                    m = re.match(r" X\((\(\)|\S+) (\(\)|\S+) (\S)", ln)
                    if m:
                        circuit = m.group(1)
                        st = names.get(m.group(3), m.group(3))
                        status[st] += 1
                        if st not in ("Match", "MatchWithWarning"):
                            why = re.search(r"B\('(.*)'\)", ln)
                            bad.append("%s / %s: %s%s" % (m.group(1), m.group(2), st,
                                                          (", " + why.group(1).replace("\\n", " ")) if why else ""))
                    elif ln.startswith(" X("):
                        circuit = None
                        status["unparsed"] += 1
                        bad.append("unparsed circuit pair %s" % ln.strip())
        ok = not bad and status["Match"] + status["MatchWithWarning"] > 0
        rows.append("circuit pairs: %s" % ", ".join("%d %s" % (n, s) for s, n in sorted(status.items())))
        rows += ["expected port mismatches: %d, %s" % (n, why) for why, n in sorted(expected.items())]
        ref = os.path.join(ROOT, "netlist", "schematic", args.cell + SUFFIX["klayout"])
        if os.path.isfile(ref):
            # the deck simplifies the layout netlist before it writes it, so a flat count of that file is no comparison
            rows.append("devices in the reference, counted flat: %d" % flat_devices(spice_blocks(ref), args.cell))
        rows += ["not matched: " + b for b in bad]
    else:
        report = os.path.join(work, args.cell + ".lvs.out")
        if not os.path.isfile(report):
            die("no %s, the Netgen run failed" % rel(report))
        with open(report, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        final = re.findall(r"^Final result: (.*)$", text, flags=re.M)
        prop = re.search(r"^(Property errors were found\.|The following cells had property errors:)", text, flags=re.M)
        nomatch = re.findall(r"^Netlists do not match\.", text, flags=re.M)
        pins = re.findall(r"^(.*failed pin matching.*)$", text, flags=re.M)
        ok = bool(final) and final[-1] == "Circuits match uniquely." and not prop and not pins
        rows.append("final result: %s" % (final[-1] if final else "none"))
        rows.append("cells that did not match on the first try (Netgen then flattens them): %d" % len(nomatch))
        if prop:
            rows.append("property errors found")
        rows += pins
        ref = os.path.join(ROOT, "netlist", "schematic", args.cell + SUFFIX["magic"])
        if os.path.isfile(ref):
            # Magic writes every finger as a device of its own, so a flat count of its netlist is no comparison
            rows.append("devices in the reference, counted flat: %d" % flat_devices(spice_blocks(ref), args.cell))
    verdict = "PASS" if ok else "FAIL"
    summary = os.path.join(work, args.cell + ".lvs.summary")
    with open(summary, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("top-level LVS of %s, %s: %s\n" % (args.cell, engine, verdict))
        for r in rows:
            fh.write(r + "\n")
    for r in rows:
        print("[lvs_top] " + r)
    print("[lvs_top] top-level LVS of %s, %s: %s (%s)" % (args.cell, engine, verdict, rel(summary)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Top-level LVS of the chip, see README.md")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("netlist", help="build the reference netlist")
    p.add_argument("--engine", choices=SUFFIX, required=True)
    p.add_argument("--top", required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("-o", help="output file (default netlist/schematic/<cell>_klayout.cdl or _magic.spice)")
    p.add_argument("--plant", help="a planted defect for a negative control")
    p = sub.add_parser("magic", help="extract the layout with Magic and compare with Netgen")
    p.add_argument("--top", required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("--gds", help="layout (default layout/<cell>.gds.gz)")
    p.add_argument("--ref", help="reference netlist (default netlist/schematic/<cell>_magic.spice)")
    p.add_argument("--work", help="run folder (default verification/lvs/<cell>.magic.lvs)")
    p = sub.add_parser("check", help="read the result of a run and decide")
    p.add_argument("--engine", choices=SUFFIX, required=True)
    p.add_argument("--top", help="the chip, when <cell> is a wrapper that holds it (default <cell>)")
    p.add_argument("--cell", required=True)
    p.add_argument("--work", help="run folder (default verification/lvs/<cell>.<engine>.lvs)")
    args = ap.parse_args()
    if args.cmd == "netlist":
        build(args)
    elif args.cmd == "magic":
        run_magic(args)
    else:
        sys.exit(check(args))


if __name__ == "__main__":
    main()
