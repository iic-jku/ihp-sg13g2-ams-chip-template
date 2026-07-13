#!/usr/bin/env python3
# =============================================================================
# run_bondplan.py - automated bondplan generation
#
# Reads a LibreLane-style config.yaml and:
#   1. extracts the top-metal view (Passiv, TopVia2, TopMetal2) from the
#      die GDS and detects the bondpads with their label names,
#   2. generates the package sheet from the EUROPRACTICE package library
#      and detects its lead frame, pin numbers and inner border,
#   3. places the die into the package cavity,
#   4. draws the bondwires and exposed-pad downbonds on Exchange0.drawing,
#      plus a bond table and re-aligned pin numbers,
#   5. fills the title block of the drawing sheet and converts all texts
#      to polygon glyphs,
#   6. checks lengths, crossings, spacing, skew and guard clearances,
#   7. writes the bondplan GDS, a bond report (Markdown or CSV) and
#      zero-border PNG / SVG images.
#
# Usage (from the packaging folder):
#   python3 scripts/run_bondplan.py config.yaml
#   klayout -b -r scripts/run_bondplan.py -rd config=config.yaml
# =============================================================================

import sys
import os
import csv
import math
import fnmatch
import datetime

import yaml

try:
    import pya                      # KLayout batch mode or pymod on PYTHONPATH
except ImportError:
    import klayout.db as pya        # pip install klayout


# ---------------------------------------------------------------------------
# Config handling
# ---------------------------------------------------------------------------

DEFAULTS = {
    "DESIGN_NAME": "design",
    "VERSION": None,                # pass VERSION=<v> or set it in the env
    "DIE_CELL": None,                   # default: top cell of DIE_GDS
    "DIE_EXTRACT_CELL": None,           # default: keep original cell name
    "DIE_KEEP_LABELS": True,
    "DIE_PAD_LAYER": "9/0",
    "DIE_PAD_MIN_SIZE": 40.0,
    "DIE_PAD_LABEL_LAYER": "134/25",
    "PACKAGE_LIBRARY_GDS": None,        # package library (e.g. EP_PACKAGES_*.gds)
    "PACKAGE_NAME": None,               # sheet cell to generate PACKAGE_GDS from
    "PACKAGE_GDS": None,                # default: <library dir>/<PACKAGE_NAME>.gds
    "PACKAGE_DELETE_TEXTS": [],         # glob patterns of sheet texts to remove
    "PACKAGE_CELL": None,               # default: top cell of PACKAGE_GDS
    "PACKAGE_FOOTPRINT_CELL": None,     # default: auto-detect the lead frame
    "PACKAGE_LEAD_LAYER": "210/0",
    "PACKAGE_PIN_LABEL_LAYER": "211/0",
    "PACKAGE_PIN_LABEL_OFFSET": 250.0,  # um, pin number outside the outline
    "PACKAGE_PIN_LABEL_SIZE": None,     # um; default: size of the sheet pin texts
    "TABLE_TEXT_SIZE": 100.0,           # um, bond table font size
    "TABLE_GAP": 400.0,                 # um, between the plan and the bond table
    "BONDPLAN_TEXT_POLYGONS": True,     # render all texts as polygon glyphs
    "SHEET_KEEP": False,                # keep drawing frame / title block decor
    "SHEET_FIELDS": {},                 # title block label --> value (see README)
    "SHEET_TEXT_SCALE": {},             # sheet text --> font scale factor
    "SHEET_NOTES": [],                  # free-text lines, stacked below anchor
    "SHEET_NOTES_ANCHOR": "Extra Info",
    "LID": "Glued",                     # Taped | Sealed | Glued | Glass (or null)
    "BONDWIRE_LAYER": "190/0",
    "BONDWIRE_TEXT_LAYER": "190/25",
    "BONDWIRE_WIDTH": 25.0,             # standard gold wire diameter
    "BONDWIRE_LABELS": True,
    "BONDWIRE_LEAD_SITE": 0.5,
    "BONDWIRE_MAX_LENGTH": 3500.0,
    "BONDWIRE_MAX_SKEW": 30.0,          # deg, wire vs. lead axis
    "GUARDED_PINS": [],                 # pins or [groups] needing extra clearance
    "GUARD_SPACING": 100.0,             # um, min gap around guarded wires
    "EPAD_WIRE_LENGTH": 500.0,
    "BONDPLAN_CELL": "bondplan",
    "BONDPLAN_DELETE_LAYERS": [],
    "BONDPLAN_REPORT": None,
    "BONDPLAN_PNG": None,
    "BONDPLAN_SVG": None,
    "IMAGE_WIDTH": 2000,
    "IMAGE_OVERSAMPLING": 2,
    "IMAGE_REGION": "package",      # package | full
}

REQUIRED = ["DIE_GDS", "DIE_EXTRACT_LAYERS", "DIE_EXTRACT_GDS",
            "BONDPLAN_GDS", "PINOUT"]

KNOWN = set(DEFAULTS) | set(REQUIRED) | {"meta", "DIE_PLACEMENT"}


def info(msg):
    print("[INFO] %s" % msg)


def warn(msg):
    print("[WARNING] %s" % msg)


def die(msg):
    print("[ERROR] %s" % msg)
    sys.exit(1)


def _subst(obj, mapping):
    """Expand {design} and {version} in every config string."""
    if isinstance(obj, str):
        for key, value in mapping.items():
            obj = obj.replace("{%s}" % key, value)
        return obj
    if isinstance(obj, dict):
        return {k: _subst(v, mapping) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_subst(v, mapping) for v in obj]
    return obj


def load_config(path, overrides=None):
    if not os.path.isfile(path):
        die("config file not found: %s" % path)
    with open(path) as f:
        cfg = yaml.safe_load(f)
    for key in cfg:
        if key not in KNOWN:
            warn("unknown config key: %s" % key)
    for key in REQUIRED:
        if key not in cfg:
            die("missing required config key: %s" % key)
    merged = dict(DEFAULTS)
    merged.update(cfg)
    merged.update(overrides or {})              # command line KEY=VALUE
    if not merged["VERSION"]:                   # the Makefile exports it
        merged["VERSION"] = os.environ.get("VERSION")

    subst = {"design": str(merged["DESIGN_NAME"])}
    if merged["VERSION"]:
        subst["version"] = str(merged["VERSION"])
    elif "{version}" in str(merged.get("SHEET_FIELDS", "")):
        die("the config uses {version} but no version is set - run "
            "'make bondplan' or pass VERSION=<version>")
    for key in list(merged):
        if key not in ("DESIGN_NAME", "VERSION"):
            merged[key] = _subst(merged[key], subst)
    if not merged["PACKAGE_GDS"] and not (merged["PACKAGE_LIBRARY_GDS"]
                                          and merged["PACKAGE_NAME"]):
        die("set PACKAGE_GDS, or PACKAGE_LIBRARY_GDS + PACKAGE_NAME")
    merged["_dir"] = os.path.dirname(os.path.abspath(path))
    return merged


def resolve(cfg, value):
    """Resolve a path; `dir::` (or a relative path) is relative to config."""
    if value.startswith("dir::"):
        value = value[len("dir::"):]
    if not os.path.isabs(value):
        value = os.path.join(cfg["_dir"], value)
    return os.path.normpath(value)


def parse_layer(spec):
    layer, dtype = str(spec).split("/")
    return int(layer), int(dtype)


# Layer palette for PNG/SVG export: (layer source, color, visible, style).
# Later entries are drawn on top. Style "outline" draws no fill, which is
# needed for the A4 paper rectangle on the sheet frame layer.
IMAGE_LAYERS = [
    ("207/0", "#00b0b0", False, "outline"),  # A4 paper rect (render artifact)
    ("208/0", "#3a2a10", True, "fill"),      # package body
    ("210/0", "#c87820", True, "fill"),      # package leads
    ("133/0", "#b36b00", False, "fill"),     # TopVia2
    ("9/0",   "#ffffff", False, "fill"),     # Passiv
    ("134/0", "#ff9900", True, "fill"),      # TopMetal2
    ("190/0", "#00e070", True, "fill"),      # bondwires
    ("211/0", "#00ccff", True, "fill"),      # pin numbers + sheet texts
    ("190/25", "#00e070", True, "fill"),     # bond table (texts)
]

# KLayout text halign --> SVG text-anchor (default/left --> "start")
SVG_ANCHOR = {1: "middle", 2: "end"}

# LibreLane/DEF orientation --> KLayout fixpoint transformation
ORIENT = {
    "N": pya.DTrans.R0,  "S": pya.DTrans.R180,
    "W": pya.DTrans.R90, "E": pya.DTrans.R270,
    "FN": pya.DTrans.M90, "FS": pya.DTrans.M0,
    "FW": pya.DTrans.M45, "FE": pya.DTrans.M135,
}


# ---------------------------------------------------------------------------
# Small 2D geometry helpers (all in um)
# ---------------------------------------------------------------------------

def _pt_seg_dist(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    l2 = vx * vx + vy * vy
    if l2 == 0.0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / l2))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


def seg_cross(a, b, c, d):
    """True if segments a-b and c-d properly intersect."""
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2 = orient(a, b, c), orient(a, b, d)
    o3, o4 = orient(c, d, a), orient(c, d, b)
    return o1 * o2 < 0 and o3 * o4 < 0


def seg_seg_dist(a, b, c, d):
    if seg_cross(a, b, c, d):
        return 0.0
    return min(_pt_seg_dist(c, a, b), _pt_seg_dist(d, a, b),
               _pt_seg_dist(a, c, d), _pt_seg_dist(b, c, d))


def ray_polygon_hits(pts, origin, direction):
    """Parameters t > 0 where origin + t*direction crosses the polygon edge."""
    ts = []
    n = len(pts)
    ox, oy = origin
    dx, dy = direction
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        det = ex * dy - ey * dx
        if abs(det) < 1e-12:
            continue
        t = (ex * (ay - oy) - ey * (ax - ox)) / det
        s = (dx * (ay - oy) - dy * (ax - ox)) / det
        if t > 1e-9 and -1e-9 <= s <= 1.0 + 1e-9:
            ts.append(t)
    return sorted(ts)


# ---------------------------------------------------------------------------
# Step 1: die - load, detect pads, extract top-metal view
# ---------------------------------------------------------------------------

def pick_cell(layout, name, what):
    if name:
        cell = layout.cell(name)
        if cell is None:
            die("%s cell '%s' not found" % (what, name))
        return cell
    tops = layout.top_cells()
    if len(tops) != 1:
        die("%s has %d top cells, set the cell name in the config "
            "(found: %s)" % (what, len(tops), ", ".join(c.name for c in tops)))
    return tops[0]


def detect_die_pads(cfg):
    """Return (pads, die_bbox). Pads: dicts with name/x/y/w/h in die um."""
    ly = pya.Layout()
    ly.read(resolve(cfg, cfg["DIE_GDS"]))
    cell = pick_cell(ly, cfg["DIE_CELL"], "die")
    dbu = ly.dbu

    li = ly.find_layer(*parse_layer(cfg["DIE_PAD_LAYER"]))
    if li is None:
        die("die pad layer %s not present in %s"
            % (cfg["DIE_PAD_LAYER"], cfg["DIE_GDS"]))
    region = pya.Region(cell.begin_shapes_rec(li))
    region.merge()

    min_size = float(cfg["DIE_PAD_MIN_SIZE"]) / dbu
    pads = []
    for poly in region.each():
        bb = poly.bbox()
        if bb.width() >= min_size and bb.height() >= min_size:
            pads.append({"name": None,
                         "x": bb.center().x * dbu, "y": bb.center().y * dbu,
                         "w": bb.width() * dbu, "h": bb.height() * dbu})

    # Name the pads from labels that fall inside the pad opening
    li = ly.find_layer(*parse_layer(cfg["DIE_PAD_LABEL_LAYER"]))
    if li is None:
        warn("die pad label layer %s not present - pads stay unnamed"
             % cfg["DIE_PAD_LABEL_LAYER"])
    else:
        labels = []
        it = cell.begin_shapes_rec(li)
        while not it.at_end():
            shape = it.shape()
            if shape.is_text():
                t = shape.text.transformed(it.trans())
                labels.append((shape.text.string, t.x * dbu, t.y * dbu))
            it.next()
        for pad in pads:
            best = None
            for name, x, y in labels:
                if (abs(x - pad["x"]) <= pad["w"] / 2.0
                        and abs(y - pad["y"]) <= pad["h"] / 2.0):
                    d = math.hypot(x - pad["x"], y - pad["y"])
                    if best is None or d < best[0]:
                        best = (d, name)
            if best:
                pad["name"] = best[1]

    pads.sort(key=lambda p: (p["x"], p["y"]))
    named = sum(1 for p in pads if p["name"])
    info("die: %d bondpads detected on %s (%d named via %s)"
         % (len(pads), cfg["DIE_PAD_LAYER"], named, cfg["DIE_PAD_LABEL_LAYER"]))
    return pads, cell.dbbox()


def extract_die(cfg):
    """Extract DIE_EXTRACT_LAYERS (+ labels) into DIE_EXTRACT_GDS."""
    layers = [parse_layer(l) for l in cfg["DIE_EXTRACT_LAYERS"]]
    if cfg["DIE_KEEP_LABELS"]:
        label_layer = parse_layer(cfg["DIE_PAD_LABEL_LAYER"])
        if label_layer not in layers:
            layers.append(label_layer)

    lmap = pya.LayerMap()
    for i, (layer, dtype) in enumerate(layers):
        lmap.map(pya.LayerInfo(layer, dtype), i)
    opt = pya.LoadLayoutOptions()
    opt.set_layer_map(lmap, False)   # False: create mapped layers only

    ly = pya.Layout()
    ly.read(resolve(cfg, cfg["DIE_GDS"]), opt)
    cell = pick_cell(ly, cfg["DIE_CELL"], "die")
    if cfg["DIE_EXTRACT_CELL"]:
        cell.name = cfg["DIE_EXTRACT_CELL"]

    out = resolve(cfg, cfg["DIE_EXTRACT_GDS"])
    ly.write(out)
    info("die: extracted %s --> %s (top cell: %s)"
         % (", ".join(cfg["DIE_EXTRACT_LAYERS"]), out, cell.name))
    return ly, cell


# ---------------------------------------------------------------------------
# Step 2: package - leads, pin numbers, bond points, inner border
# ---------------------------------------------------------------------------

def find_cell_transforms(parent, target):
    """All accumulated transformations of `target` instances under `parent`."""
    if parent.cell_index() == target.cell_index():
        return [pya.DCplxTrans()]
    found = []

    def walk(cell, trans):
        for inst in cell.each_inst():
            t = trans * inst.dcplx_trans
            if inst.cell.cell_index() == target.cell_index():
                found.append(t)
            else:
                walk(inst.cell, t)

    walk(parent, pya.DCplxTrans())
    return found


def count_lead_frame(cfg, ly, cell):
    """(lead polygons, numeric pin texts) of a candidate footprint cell."""
    nlead = npin = 0
    li = ly.find_layer(*parse_layer(cfg["PACKAGE_LEAD_LAYER"]))
    if li is not None:
        region = pya.Region(cell.begin_shapes_rec(li))
        region.merge()
        nlead = region.count()
    li = ly.find_layer(*parse_layer(cfg["PACKAGE_PIN_LABEL_LAYER"]))
    if li is not None:
        it = cell.begin_shapes_rec(li)
        while not it.at_end():
            shape = it.shape()
            if shape.is_text():
                try:
                    int(shape.text.string.strip())
                    npin += 1
                except ValueError:
                    pass
            it.next()
    return nlead, npin


def detect_footprint(cfg, ly, pkg_cell):
    """Find the lead frame cell: N merged lead polygons on the lead layer
    matching N numeric pin texts on the pin label layer."""
    best = None
    for ci in [pkg_cell.cell_index()] + list(pkg_cell.called_cells()):
        cell = ly.cell(ci)
        nlead, npin = count_lead_frame(cfg, ly, cell)
        if nlead > 0 and nlead == npin:
            area = cell.dbbox().area()
            if best is None or (npin, -area) > (best[0], -best[1]):
                best = (npin, area, cell)
    if best is None:
        die("no usable lead frame in package '%s': the flow needs a cell "
            "with N lead polygons on %s and N pin number texts on %s "
            "(this package drawing is not supported)"
            % (pkg_cell.name, cfg["PACKAGE_LEAD_LAYER"],
               cfg["PACKAGE_PIN_LABEL_LAYER"]))
    info("package: footprint cell auto-detected: %s (%d pins)"
         % (best[2].name, best[0]))
    return best[2]


def generate_package(cfg):
    """Extract the PACKAGE_NAME sheet cell from the package library GDS
    into PACKAGE_GDS, dropping the template paper layer 207/0."""
    lib_path, name = cfg["PACKAGE_LIBRARY_GDS"], cfg["PACKAGE_NAME"]
    if not lib_path and not name:
        return                              # pre-made PACKAGE_GDS provided
    if not (lib_path and name):
        die("PACKAGE_LIBRARY_GDS and PACKAGE_NAME must be set together")
    path = resolve(cfg, lib_path)
    if not os.path.isfile(path):
        die("package library not found: %s" % path)
    lib = pya.Layout()
    lib.read(path)
    cell = lib.cell(name)
    if cell is None:
        avail = sorted({inst.cell.name for t in lib.top_cells()
                        for inst in t.each_inst()}
                       | {t.name for t in lib.top_cells()})
        die("package '%s' not found in %s - available cells:\n  %s"
            % (name, os.path.basename(path), "\n  ".join(avail)))

    out = pya.Layout()
    out.dbu = lib.dbu
    top = out.create_cell(name)
    top.copy_tree(cell)
    li = out.find_layer(207, 0)             # template paper rectangle
    if li is not None:
        out.clear_layer(li)
        out.delete_layer(li)

    # Remove unwanted template texts, e.g. old revision notes. Patterns
    # are case-insensitive globs matched against the whole text string.
    patterns = [str(p).casefold() for p in cfg["PACKAGE_DELETE_TEXTS"] or []]
    if patterns:
        removed = 0
        for c in out.each_cell():
            for li in out.layer_indexes():
                stale = [s for s in c.shapes(li).each() if s.is_text()
                         and any(fnmatch.fnmatchcase(
                             " ".join(s.text.string.split()).casefold(), p)
                             for p in patterns)]
                for s in stale:
                    c.shapes(li).erase(s)
                    removed += 1
        info("package: removed %d template text(s)" % removed)
    if not cfg["PACKAGE_GDS"]:              # default: next to the library
        cfg["PACKAGE_GDS"] = os.path.join(os.path.dirname(path),
                                          name + ".gds")
    dest = resolve(cfg, cfg["PACKAGE_GDS"])
    out.write(dest)
    info("package: '%s' generated from %s --> %s"
         % (name, os.path.basename(path), dest))


def analyze_package(cfg):
    ly = pya.Layout()
    ly.read(resolve(cfg, cfg["PACKAGE_GDS"]))
    dbu = ly.dbu
    pkg_cell = pick_cell(ly, cfg["PACKAGE_CELL"], "package")
    if cfg["PACKAGE_FOOTPRINT_CELL"]:
        fp_cell = pick_cell(ly, cfg["PACKAGE_FOOTPRINT_CELL"],
                            "package footprint")
    else:
        fp_cell = detect_footprint(cfg, ly, pkg_cell)

    transforms = find_cell_transforms(pkg_cell, fp_cell)
    if len(transforms) == 0:
        die("footprint cell %s not instantiated under %s"
            % (fp_cell.name, pkg_cell.name))
    if len(transforms) > 1:
        warn("footprint cell %s placed %d times under %s - using the first"
             % (fp_cell.name, len(transforms), pkg_cell.name))
    fp_trans = transforms[0]

    # Lead polygons, in footprint um coordinates
    li = ly.find_layer(*parse_layer(cfg["PACKAGE_LEAD_LAYER"]))
    if li is None:
        die("package lead layer %s not present" % cfg["PACKAGE_LEAD_LAYER"])
    region = pya.Region(fp_cell.begin_shapes_rec(li))
    region.merge()
    leads = []
    for poly in region.each():
        bb = poly.bbox()
        leads.append({
            "pts": [(p.x * dbu, p.y * dbu) for p in poly.each_point_hull()],
            "cx": bb.center().x * dbu, "cy": bb.center().y * dbu,
        })

    bb = region.bbox()
    center = (bb.center().x * dbu, bb.center().y * dbu)
    inner = min(max(abs(x - center[0]), abs(y - center[1]))
                for lead in leads for (x, y) in lead["pts"])

    # Pin number labels --> nearest lead
    li = ly.find_layer(*parse_layer(cfg["PACKAGE_PIN_LABEL_LAYER"]))
    if li is None:
        die("package pin label layer %s not present"
            % cfg["PACKAGE_PIN_LABEL_LAYER"])
    pins = {}
    used_leads = {}
    sizes = {}
    it = fp_cell.begin_shapes_rec(li)
    while not it.at_end():
        shape = it.shape()
        if shape.is_text():
            try:
                num = int(shape.text.string.strip())
            except ValueError:
                it.next()
                continue
            t = shape.text.transformed(it.trans())
            x, y = t.x * dbu, t.y * dbu
            sizes[num] = t.size * dbu if t.size > 0 else 120.0
            idx = min(range(len(leads)),
                      key=lambda i: (leads[i]["cx"] - x) ** 2
                                  + (leads[i]["cy"] - y) ** 2)
            if idx in used_leads:
                warn("pins %d and %d map to the same lead" % (used_leads[idx], num))
            used_leads[idx] = num
            pins[num] = leads[idx]
        it.next()

    site = float(cfg["BONDWIRE_LEAD_SITE"])
    label_off = float(cfg["PACKAGE_PIN_LABEL_OFFSET"])

    # In sheet mode the bond table sits between the plan and the drawing
    # frame. Shift the lead frame (and with it die, wires and labels)
    # inside the sheet so that plan, gap and table are balanced with equal
    # side margins. The frame lines live on the pin label layer.
    fp_shift = 0.0
    if cfg["SHEET_KEEP"] and cfg["BONDWIRE_LABELS"]:
        frame = pya.Region(pkg_cell.begin_shapes_rec(li)).bbox()
        table_rows = []
        for pin, value in cfg["PINOUT"].items():
            table_rows += ["%s %s" % (pin, n)
                           for n in normalize_targets(value)]
        if not frame.empty() and table_rows:
            table_w = (max(map(len, table_rows))
                       * float(cfg["TABLE_TEXT_SIZE"]) * 0.70)
            pin_size = float(cfg["PACKAGE_PIN_LABEL_SIZE"]
                             or max(sizes.values(), default=120.0))
            ring = label_off + 0.7 * pin_size    # pin number ring extent
            plan_w = (bb.right - bb.left) * dbu + 2 * ring
            frame_w = (frame.right - frame.left) * dbu
            margin = (frame_w - plan_w - float(cfg["TABLE_GAP"])
                      - table_w) / 2.0
            if margin < 100.0:
                warn("little room for the bond table inside the frame "
                     "(side margin %.0f um)" % margin)
                margin = 100.0
            plan_left = fp_trans.disp.x + bb.left * dbu - ring
            fp_shift = frame.left * dbu + margin - plan_left
            if abs(fp_shift) > 0.5:
                info("package: lead frame shifted %.0f um (side margins "
                     "%.0f um)" % (fp_shift, margin))
                fp_trans = pya.DCplxTrans(1.0, 0.0, False,
                                          fp_shift, 0.0) * fp_trans

    # Per pin, on the ray center --> lead: the bond point (between lead tip,
    # site 0, and far end, site 1) and the pin number label position
    bond_pts = {}
    lead_dirs = {}
    pin_labels = {}
    text_box = None
    for num, lead in pins.items():
        direction = (lead["cx"] - center[0], lead["cy"] - center[1])
        norm = math.hypot(*direction)
        direction = (direction[0] / norm, direction[1] / norm)
        ts = ray_polygon_hits(lead["pts"], center, direction)
        if len(ts) >= 2:
            t = ts[0] + site * (ts[-1] - ts[0])
            pt = (center[0] + t * direction[0], center[1] + t * direction[1])
        else:                                   # degenerate: use lead center
            pt = (lead["cx"], lead["cy"])
        bond_pts[num] = fp_trans * pya.DPoint(*pt)
        dir_t = fp_trans * pya.DVector(*direction)   # lead axis, for skew
        lead_dirs[num] = (dir_t.x, dir_t.y)

        # Pin number centered on the bond point coordinate, in a row /
        # column PACKAGE_PIN_LABEL_OFFSET outside the package outline
        size = float(cfg["PACKAGE_PIN_LABEL_SIZE"] or sizes.get(num, 120.0))
        if abs(direction[0]) >= abs(direction[1]):   # east / west side
            lx = (bb.right * dbu + label_off if direction[0] > 0
                  else bb.left * dbu - label_off)
            ly_ = pt[1]
        else:                                        # north / south side
            lx = pt[0]
            ly_ = (bb.top * dbu + label_off if direction[1] > 0
                   else bb.bottom * dbu - label_off)
        pin_labels[num] = {"pt": fp_trans * pya.DPoint(lx, ly_),
                           "size": size}
        half_w = len(str(num)) * size * 0.35     # centered glyph extent
        glyph_box = pya.DBox(lx - half_w, ly_ - size * 0.55,
                             lx + half_w, ly_ + size * 0.55)
        text_box = glyph_box if text_box is None else text_box + glyph_box

    center = fp_trans * pya.DPoint(*center)
    inner *= fp_trans.mag
    # Footprint extent incl. pin-number glyphs (for zero-border image crops)
    view_box = pya.DBox(bb.left * dbu, bb.bottom * dbu,
                        bb.right * dbu, bb.top * dbu)
    if text_box is not None:
        view_box += text_box
    view_box = view_box.transformed(fp_trans)

    info("package: %d leads, %d numbered pins, inner border %.1f x %.1f um"
         % (len(leads), len(pins), 2 * inner, 2 * inner))
    return {"layout": ly, "cell": pkg_cell, "footprint": fp_cell.name,
            "fp_shift": fp_shift, "bond_pts": bond_pts,
            "lead_dirs": lead_dirs, "pin_labels": pin_labels,
            "center": center, "inner": inner, "view_box": view_box}


# ---------------------------------------------------------------------------
# Step 3: die placement transformation
# ---------------------------------------------------------------------------

def die_transform(cfg, die_bbox, pkg):
    placement = cfg.get("DIE_PLACEMENT") or {}
    orient = placement.get("orientation", "N")
    if orient not in ORIENT:
        die("unknown orientation '%s' (use %s)"
            % (orient, "/".join(ORIENT)))
    t0 = pya.DCplxTrans(ORIENT[orient])
    bb0 = die_bbox.transformed(t0)

    inner_ll = (pkg["center"].x - pkg["inner"], pkg["center"].y - pkg["inner"])
    location = placement.get("location")
    if location is None:                        # default: center the die
        location = [pkg["inner"] - bb0.width() / 2.0,
                    pkg["inner"] - bb0.height() / 2.0]

    dx = inner_ll[0] + float(location[0]) - bb0.left
    dy = inner_ll[1] + float(location[1]) - bb0.bottom
    trans = pya.DCplxTrans(1.0, 0.0, False, dx, dy) * t0

    # Feasibility: the placed die must fit into the package inner area
    placed = die_bbox.transformed(trans)
    side = 2 * pkg["inner"]
    if (placed.width() > side + 1e-6 or placed.height() > side + 1e-6
            or placed.left < inner_ll[0] - 1e-6
            or placed.bottom < inner_ll[1] - 1e-6
            or placed.right > inner_ll[0] + side + 1e-6
            or placed.top > inner_ll[1] + side + 1e-6):
        die("die (%.0f x %.0f um, oriented %s, at location [%.1f, %.1f]) "
            "does not fit the package inner area (%.0f x %.0f um)"
            % (placed.width(), placed.height(), orient,
               float(location[0]), float(location[1]), side, side))

    info("die: placed at inner border + (%.1f, %.1f) um, orientation %s"
         % (float(location[0]), float(location[1]), orient))
    return trans


# ---------------------------------------------------------------------------
# Step 4: pinout --> wire list
# ---------------------------------------------------------------------------

def normalize_targets(value):
    if value is None or value == "NC":
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def wire_geometry(wire, lead_dir=None):
    """Annotate a wire with its bearing and its skew vs. the lead axis."""
    dx = wire["p1"][0] - wire["p0"][0]
    dy = wire["p1"][1] - wire["p0"][1]
    wire["angle"] = math.degrees(math.atan2(dy, dx))
    if lead_dir:
        cos_v = ((dx * lead_dir[0] + dy * lead_dir[1])
                 / (math.hypot(dx, dy) or 1.0))
        wire["skew"] = math.degrees(math.acos(max(-1.0, min(1.0, cos_v))))


def guard_groups(cfg):
    """GUARDED_PINS entries are pins or lists of pins (a guard group);
    wires within one group are exempt from each other's spacing check."""
    groups = {}
    for gid, entry in enumerate(cfg["GUARDED_PINS"]):
        for pin in (entry if isinstance(entry, (list, tuple)) else [entry]):
            groups[int(pin)] = gid
    return groups


def assign_wires(cfg, pads, pkg, die_center):
    pinout = cfg["PINOUT"]
    epad_names = normalize_targets(pinout.get("EPAD"))

    pads_by_name = {}
    for pad in pads:
        if pad["name"]:
            pads_by_name.setdefault(pad["name"], []).append(pad)

    # Collect lead-bond requests: (pin, name)
    requests = {}
    for pin, value in pinout.items():
        if pin == "EPAD":
            continue
        if not isinstance(pin, int):
            die("PINOUT key must be a pin number or EPAD, got: %r" % pin)
        if pin not in pkg["bond_pts"]:
            die("pin %d not found on the package (numbered pins: %d..%d)"
                % (pin, min(pkg["bond_pts"]), max(pkg["bond_pts"])))
        for name in normalize_targets(value):
            requests.setdefault(name, []).append(pin)

    # Shortest-wire assignment per pad name (handles VDD/VSS/... groups)
    wires = []
    for name, pin_list in sorted(requests.items()):
        candidates = pads_by_name.get(name, [])
        if len(candidates) < len(pin_list):
            die("pinout requests %d x pad '%s' but the die has %d "
                "(known pads: %s)"
                % (len(pin_list), name, len(candidates),
                   ", ".join(sorted(pads_by_name)) or "none"))
        pairs = []
        for i, pin in enumerate(pin_list):
            bp = pkg["bond_pts"][pin]
            for j, pad in enumerate(candidates):
                pairs.append((math.hypot(pad["x"] - bp.x, pad["y"] - bp.y),
                              i, j))
        pairs.sort()
        done_pins, done_pads = set(), set()
        for dist, i, j in pairs:
            if i in done_pins or j in done_pads:
                continue
            done_pins.add(i)
            done_pads.add(j)
            pad = candidates[j]
            pad["used"] = True
            bp = pkg["bond_pts"][pin_list[i]]
            wire = {"pin": pin_list[i], "name": name,
                    "p0": (pad["x"], pad["y"]), "p1": (bp.x, bp.y),
                    "length": dist}
            wire_geometry(wire, pkg["lead_dirs"].get(pin_list[i]))
            wires.append(wire)

    # Exposed-pad downbonds: stubs from leftover pads, oriented parallel
    # to the neighboring bondwires (radial from die center as fallback)
    def stub_direction(pad):
        near = sorted(wires, key=lambda w: (w["p0"][0] - pad["x"]) ** 2
                                         + (w["p0"][1] - pad["y"]) ** 2)[:2]
        vx = vy = 0.0
        for w in near:
            dx, dy = w["p1"][0] - w["p0"][0], w["p1"][1] - w["p0"][1]
            norm = math.hypot(dx, dy)
            vx += dx / norm
            vy += dy / norm
        norm = math.hypot(vx, vy)
        if norm < 1e-9:
            vx, vy = pad["x"] - die_center[0], pad["y"] - die_center[1]
            norm = math.hypot(vx, vy) or 1.0
        return vx / norm, vy / norm

    stub = float(cfg["EPAD_WIRE_LENGTH"])
    for name in epad_names:
        left = [p for p in pads_by_name.get(name, []) if not p.get("used")]
        if not left:
            die("EPAD requests pad '%s' but no unused pad of that name is left"
                % name)
        pad = sorted(left, key=lambda p: (p["x"], p["y"]))[0]
        pad["used"] = True
        direction = stub_direction(pad)
        p1 = (pad["x"] + stub * direction[0],
              pad["y"] + stub * direction[1])
        wire = {"pin": "EPAD", "name": name,
                "p0": (pad["x"], pad["y"]), "p1": p1, "length": stub}
        wire_geometry(wire)                     # bearing only, no lead skew
        wires.append(wire)

    unbonded = [p["name"] for p in pads if p["name"] and not p.get("used")]
    if unbonded:
        info("unbonded named pads: %s" % ", ".join(sorted(unbonded)))
    nc = sorted(set(pkg["bond_pts"]) - {w["pin"] for w in wires})
    if nc:
        info("NC package pins: %s" % ", ".join(map(str, nc)))
    return wires


# ---------------------------------------------------------------------------
# Step 5: build the bondplan layout
# ---------------------------------------------------------------------------

def sheet_stats(cfg, pads, die_bbox, wires):
    """Computed values available as {placeholders} in SHEET_FIELDS."""
    lengths = [w["length"] for w in wires if w["pin"] != "EPAD"]
    gaps = [w["min_gap"] for w in wires if w.get("min_gap") is not None]
    openings = sorted(p["w"] for p in pads)
    pitches = sorted(
        min((math.hypot(p["x"] - q["x"], p["y"] - q["y"])
             for q in pads if q is not p), default=0.0) for p in pads)

    def med(values):
        return values[len(values) // 2] if values else 0.0

    return {
        "design": cfg["DESIGN_NAME"],
        "version": str(cfg["VERSION"] or ""),
        "date": datetime.date.today().isoformat(),
        "bondwire_width_um": "%g" % float(cfg["BONDWIRE_WIDTH"]),
        "wire_count": len(wires),
        "max_wire_length_um": "%.0f" % (max(lengths) if lengths else 0),
        "max_wire_length_mm": "%.2f" % ((max(lengths) if lengths else 0) / 1e3),
        "min_wire_length_um": "%.0f" % (min(lengths) if lengths else 0),
        "min_gap_um": "%.0f" % (min(gaps) if gaps else 0),
        "die_width_um": "%.0f" % die_bbox.width(),
        "die_height_um": "%.0f" % die_bbox.height(),
        "die_width_mm": "%.2f" % (die_bbox.width() / 1e3),
        "die_height_mm": "%.2f" % (die_bbox.height() / 1e3),
        "pad_pitch_um": "%.0f" % med(pitches),
        "pad_opening_um": "%.1f" % med(openings),
    }


def _norm_label(s):
    """'Max. wire length :' --> 'max. wire length' for tolerant matching."""
    s = " ".join(str(s).split())
    if s.endswith(":"):
        s = s[:-1].rstrip()
    return s.casefold()


class _SafePlaceholders(dict):
    def __missing__(self, key):
        warn("unknown placeholder {%s} in SHEET_FIELDS" % key)
        return "{%s}" % key


def fill_sheet_fields(cfg, ly, top, stats):
    """Write SHEET_FIELDS values next to their title block labels."""
    fields = cfg["SHEET_FIELDS"] or {}
    if not fields:
        return
    # Collect all text labels on the sheet: normalized string --> position
    labels = {}
    for li in ly.layer_indexes():
        it = top.begin_shapes_rec(li)
        while not it.at_end():
            shape = it.shape()
            if shape.is_text():
                t = shape.text.transformed(it.trans())
                size = t.size * ly.dbu if t.size > 0 else 120.0
                labels.setdefault(_norm_label(t.string), []).append(
                    (t.x * ly.dbu, t.y * ly.dbu, size, len(t.string), li))
            it.next()

    scales = {_norm_label(k): float(v)
              for k, v in (cfg["SHEET_TEXT_SCALE"] or {}).items()}
    filled = 0
    for key, raw in fields.items():
        dx = dy = vsize = None
        if isinstance(raw, dict):        # {value: ..., dx: ..., dy: ..., size: ...}
            dx, dy, vsize = raw.get("dx"), raw.get("dy"), raw.get("size")
            raw = raw.get("value", "")
        value = str(raw).format_map(_SafePlaceholders(stats)).strip()
        if not value:
            continue
        found = labels.get(_norm_label(key))
        if not found:
            warn("sheet field '%s': no matching label on the drawing sheet"
                 % key)
            continue
        if len(found) > 1:
            warn("sheet field '%s' matches %d labels - using the first"
                 % (key, len(found)))
        x, y, size, label_len, li = sorted(found)[0]
        # the label may be rescaled at textify time - indent from its
        # rendered width, and let the value inherit the rendered size
        size *= scales.get(_norm_label(key), 1.0)
        if dx is None:
            # stroke-font advance is ~0.70 * size per character
            dx = label_len * size * 0.70 + size * 1.2
        text = pya.DText(value,
                         pya.DTrans(pya.DVector(x + dx, y + (dy or 0.0))),
                         float(vsize or size), 0)
        top.shapes(li).insert(text)
        filled += 1
    info("sheet: filled %d/%d title block fields" % (filled, len(fields)))

    # LID: put an X into the checkbox next to the chosen lid option
    if cfg["LID"]:
        found = labels.get(_norm_label(str(cfg["LID"])))
        if not found:
            warn("LID option '%s' not found on the drawing sheet" % cfg["LID"])
        else:
            x, y, size, _len, li = sorted(found)[0]
            boxes = []
            it = top.begin_shapes_rec(li)
            while not it.at_end():
                shape = it.shape()
                if shape.is_polygon() or shape.is_box() or shape.is_path():
                    bb = shape.bbox().transformed(it.trans())
                    w, h = bb.width() * ly.dbu, bb.height() * ly.dbu
                    cx, cy = bb.center().x * ly.dbu, bb.center().y * ly.dbu
                    if (80 <= w <= 600 and 80 <= h <= 600
                            and cx > x and abs(cy - y) < 3 * size):
                        boxes.append((cx - x, cx, cy, h))
                it.next()
            if not boxes:
                warn("LID '%s': no checkbox found next to the label"
                     % cfg["LID"])
            else:
                _d, cx, cy, h = min(boxes)
                mark = pya.DText("X", pya.DTrans(pya.DVector(cx, cy)),
                                 h * 0.7, 0)
                mark.halign = pya.HAlign.HAlignCenter
                mark.valign = pya.VAlign.VAlignCenter
                top.shapes(li).insert(mark)
                info("sheet: lid option '%s' checked" % cfg["LID"])

    # Free-text notes, stacked below the anchor label
    notes = cfg["SHEET_NOTES"] or []
    if notes:
        found = labels.get(_norm_label(cfg["SHEET_NOTES_ANCHOR"]))
        if not found:
            warn("SHEET_NOTES anchor '%s' not found on the drawing sheet"
                 % cfg["SHEET_NOTES_ANCHOR"])
        else:
            ax, ay, asize, _len, ali = sorted(found)[0]
            for i, note in enumerate(notes):
                dx = dy = nsize = None
                if isinstance(note, dict):
                    dx, dy, nsize = (note.get("dx"), note.get("dy"),
                                     note.get("size"))
                    note = note.get("value", "")
                text = str(note).format_map(_SafePlaceholders(stats)).strip()
                if not text:
                    continue
                nsize = float(nsize or asize * 0.5)
                top.shapes(ali).insert(pya.DText(
                    text,
                    pya.DTrans(pya.DVector(ax + (dx or 0.0),
                                           ay - 1.7 * nsize * (i + 1)
                                           + (dy or 0.0))),
                    nsize, 0))
            info("sheet: %d note lines added" % len(notes))


def textify(cfg, ly):
    """Replace all text objects with polygon glyphs (KLayout stroke font).
    KLayout draws text objects at a fixed screen font size, so polygon
    glyphs are the only way to get properly scaled text in images and
    prints - and the GDS becomes viewer-independent."""
    if not cfg["BONDPLAN_TEXT_POLYGONS"]:
        return
    gen = pya.TextGenerator.default_generator()
    if gen is None:
        warn("no TextGenerator - texts kept as text objects")
        return
    dbu = ly.dbu
    scales = {_norm_label(k): float(v)
              for k, v in (cfg["SHEET_TEXT_SCALE"] or {}).items()}
    unused_scales = set(scales)
    count = 0
    for cell in ly.each_cell():
        for li in ly.layer_indexes():
            stale = [s for s in cell.shapes(li).each() if s.is_text()]
            for shape in stale:
                t = shape.text
                size = t.size * dbu if t.size > 0 else 120.0
                norm = _norm_label(t.string)
                size *= scales.get(norm, 1.0)
                unused_scales.discard(norm)
                region = gen.text(t.string, dbu, size / gen.dheight())
                bb = region.bbox()
                dx = {1: -bb.width() // 2, 2: -bb.width()}.get(
                    int(t.halign), 0)
                dy = {1: -bb.height() // 2, 0: -bb.height()}.get(
                    int(t.valign), 0)                     # 0 = top, 2 = bottom
                region.move(dx - bb.left, dy - bb.bottom)
                region = region.transformed(t.trans)   # rotation + position
                cell.shapes(li).insert(region)
                cell.shapes(li).erase(shape)
                count += 1
    for key in sorted(unused_scales):
        warn("SHEET_TEXT_SCALE entry '%s' matched no text (package "
             "changed?)" % key)
    info("textify: %d texts converted to polygon glyphs" % count)


def build_bondplan(cfg, pkg, die_layout, die_cell, die_trans, wires, stats):
    if abs(die_layout.dbu - pkg["layout"].dbu) > 1e-12:
        die("die dbu (%g) != package dbu (%g) - not supported"
            % (die_layout.dbu, pkg["layout"].dbu))

    ly = pya.Layout()
    ly.dbu = pkg["layout"].dbu
    top = ly.create_cell(cfg["BONDPLAN_CELL"])

    # Bond table rows and font metrics
    rows = None
    if cfg["BONDWIRE_LABELS"]:
        size = float(cfg["TABLE_TEXT_SIZE"])
        spacing = 1.3 * size

        def key(w):
            return (1, 0) if w["pin"] == "EPAD" else (0, w["pin"])
        rows = ["%s %s" % (w["pin"], w["name"]) for w in sorted(wires, key=key)]
        width_est = max(map(len, rows)) * size * 0.70

    pkg_copy = ly.create_cell(pkg["cell"].name)
    pkg_copy.copy_tree(pkg["cell"])
    top.insert(pya.DCellInstArray(pkg_copy.cell_index(), pya.DCplxTrans()))

    # Match the lead frame shift applied during package analysis, so wires
    # and labels land on the (shifted) leads
    if pkg["fp_shift"]:
        fp_cell = ly.cell(pkg["footprint"])
        shift = pya.DCplxTrans(1.0, 0.0, False, pkg["fp_shift"], 0.0)
        moved = 0
        if fp_cell is not None:
            for cell in ly.each_cell():
                for inst in [i for i in cell.each_inst()
                             if i.cell.cell_index() == fp_cell.cell_index()]:
                    inst.transform(shift)
                    moved += 1
        if moved != 1:
            warn("lead frame shift applied to %d instances (expected 1)"
                 % moved)

    die_copy = ly.create_cell(die_cell.name)
    die_copy.copy_tree(die_cell)
    top.insert(pya.DCellInstArray(die_copy.cell_index(), die_trans))

    wire_li = ly.layer(*parse_layer(cfg["BONDWIRE_LAYER"]))
    width = float(cfg["BONDWIRE_WIDTH"])
    for wire in wires:
        top.shapes(wire_li).insert(
            pya.DPath([pya.DPoint(*wire["p0"]), pya.DPoint(*wire["p1"])],
                      width))

    table_box = None
    if rows:
        text_li = ly.layer(*parse_layer(cfg["BONDWIRE_TEXT_LAYER"]))
        x = pkg["view_box"].right + float(cfg["TABLE_GAP"])
        y_first = pkg["center"].y + (len(rows) - 1) * spacing / 2.0
        y = y_first
        for row in rows:
            top.shapes(text_li).insert(
                pya.DText(row, pya.DTrans(pya.DVector(x, y)), size, 0))
            y -= spacing
        table_box = pya.DBox(x, y + spacing - size * 0.6,
                             x + width_est, y_first + size * 0.6)

    # The lead layer is only authoritative inside the footprint cell. Unless
    # the drawing sheet is kept, drop sheet decor (frame rulers, logos) on it.
    fp_cell = ly.cell(pkg["footprint"])
    keep = set()
    if fp_cell is not None:
        keep = {fp_cell.cell_index()} | set(fp_cell.called_cells())
        if not cfg["SHEET_KEEP"]:
            li = ly.find_layer(*parse_layer(cfg["PACKAGE_LEAD_LAYER"]))
            if li is not None:
                for cell in ly.each_cell():
                    if cell.cell_index() not in keep:
                        cell.shapes(li).clear()

    # Replace the package pin numbers: drop the footprint's own number texts
    # (they sit offset from their leads) and re-insert each number centered
    # on its wire attach coordinate, just outside the package outline.
    # Only numeric texts inside the footprint subtree are removed, so sheet
    # texts (title block labels, frame rulers) survive in SHEET_KEEP mode.
    pin_li = ly.layer(*parse_layer(cfg["PACKAGE_PIN_LABEL_LAYER"]))
    for cell in ly.each_cell():
        if not keep or cell.cell_index() in keep:      # footprint subtree
            stale = [s for s in cell.shapes(pin_li).each()
                     if s.is_text() and s.text.string.strip().isdigit()]
            for s in stale:
                cell.shapes(pin_li).erase(s)
        elif not cfg["SHEET_KEEP"]:                    # sheet decor
            cell.shapes(pin_li).clear()
    for num, label in sorted(pkg["pin_labels"].items()):
        pt = label["pt"]
        text = pya.DText(str(num), pya.DTrans(pya.DVector(pt.x, pt.y)),
                         label["size"], 0)
        text.halign = pya.HAlign.HAlignCenter
        text.valign = pya.VAlign.VAlignCenter
        top.shapes(pin_li).insert(text)

    fill_sheet_fields(cfg, ly, top, stats)
    textify(cfg, ly)

    # Drop unwanted layers (e.g. drawing frame, die pad labels)
    for spec in cfg["BONDPLAN_DELETE_LAYERS"]:
        li = ly.find_layer(*parse_layer(spec))
        if li is not None:
            ly.clear_layer(li)
            ly.delete_layer(li)
            info("deleted layer %s from the bondplan" % spec)

    out = resolve(cfg, cfg["BONDPLAN_GDS"])
    ly.write(out)
    info("bondplan: %d bondwires (w=%g um on %s) --> %s"
         % (len(wires), width, cfg["BONDWIRE_LAYER"], out))
    return out, ly, top, table_box


# ---------------------------------------------------------------------------
# Step 6: checks and report
# ---------------------------------------------------------------------------

def check_wires(cfg, wires):
    max_len = float(cfg["BONDWIRE_MAX_LENGTH"])
    width = float(cfg["BONDWIRE_WIDTH"])
    for wire in wires:
        if wire["length"] > max_len:
            warn("wire pin %s (%s) is %.0f um long (> %.0f um)"
                 % (wire["pin"], wire["name"], wire["length"], max_len))

    guards = guard_groups(cfg)
    guard_gap = float(cfg["GUARD_SPACING"])
    min_gap, min_pair = None, None
    for i in range(len(wires)):
        for j in range(i + 1, len(wires)):
            a, b = wires[i], wires[j]
            # ignore wires bonded to the same lead (deliberate double bonds)
            if a["pin"] == b["pin"] and a["pin"] != "EPAD":
                continue
            if seg_cross(a["p0"], a["p1"], b["p0"], b["p1"]):
                warn("wires cross: pin %s (%s) x pin %s (%s)"
                     % (a["pin"], a["name"], b["pin"], b["name"]))
            gap = seg_seg_dist(a["p0"], a["p1"], b["p0"], b["p1"]) - width
            if min_gap is None or gap < min_gap:
                min_gap, min_pair = gap, (a, b)
            for wire in (a, b):
                wire["min_gap"] = min(gap, wire.get("min_gap", float("inf")))
            # guarded wires need GUARD_SPACING to everything outside
            # their own guard group
            ga, gb = guards.get(a["pin"]), guards.get(b["pin"])
            if ((ga is not None or gb is not None) and ga != gb
                    and gap < guard_gap):
                warn("guard spacing: pin %s (%s) has only %.1f um to "
                     "pin %s (%s) (< %.0f um)"
                     % (a["pin"], a["name"], gap, b["pin"], b["name"],
                        guard_gap))
    if min_pair:
        a, b = min_pair
        level = warn if min_gap < 0 else info
        level("minimum wire-to-wire gap: %.1f um (pin %s %s / pin %s %s)"
              % (min_gap, a["pin"], a["name"], b["pin"], b["name"]))

    max_skew = float(cfg["BONDWIRE_MAX_SKEW"])
    skews = [w for w in wires if w.get("skew") is not None]
    for wire in skews:
        if wire["skew"] > max_skew:
            warn("wire pin %s (%s) lands %.1f deg skewed on its lead "
                 "(> %.0f deg)" % (wire["pin"], wire["name"], wire["skew"],
                                   max_skew))
    if skews:
        worst = max(skews, key=lambda w: w["skew"])
        info("wire lead skew: max %.1f deg (pin %s %s)"
             % (worst["skew"], worst["pin"], worst["name"]))

    lengths = [w["length"] for w in wires if w["pin"] != "EPAD"]
    if lengths:
        info("wire lengths: min %.0f / max %.0f um"
             % (min(lengths), max(lengths)))


def write_report(cfg, wires, stats):
    """Bond report; Markdown or CSV depending on the file extension."""
    if not cfg["BONDPLAN_REPORT"]:
        return
    out = resolve(cfg, cfg["BONDPLAN_REPORT"])

    def key(w):
        return (1, 0) if w["pin"] == "EPAD" else (0, w["pin"])
    rows = sorted(wires, key=key)

    if out.lower().endswith(".md"):
        _write_markdown_report(cfg, rows, stats, out)
    else:
        _write_csv_report(rows, out)
    info("bond report --> %s" % out)


def _write_csv_report(rows, out):
    with open(out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pin", "die_pad", "die_x_um", "die_y_um",
                         "pkg_x_um", "pkg_y_um", "length_um", "angle_deg",
                         "lead_skew_deg", "min_gap_um"])
        for w in rows:
            writer.writerow([w["pin"], w["name"],
                             "%.3f" % w["p0"][0], "%.3f" % w["p0"][1],
                             "%.3f" % w["p1"][0], "%.3f" % w["p1"][1],
                             "%.1f" % w["length"],
                             "%.1f" % w["angle"],
                             "" if w.get("skew") is None else "%.1f" % w["skew"],
                             "" if w.get("min_gap") is None
                                else "%.1f" % w["min_gap"]])


def _write_markdown_report(cfg, rows, stats, out):
    epad = sum(1 for w in rows if w["pin"] == "EPAD")
    skews = [w["skew"] for w in rows if w.get("skew") is not None]
    title = cfg["DESIGN_NAME"]
    if cfg["VERSION"]:
        title += " v.%s" % cfg["VERSION"]
    lines = ["# Bondplan Report - %s" % title, ""]
    lines += ["Generated by `scripts/run_bondplan.py` on %s." % stats["date"],
              ""]
    if cfg["BONDPLAN_PNG"]:
        png = os.path.splitext(resolve(cfg, cfg["BONDPLAN_PNG"]))[0] + \
            "_white.png"
        rel = os.path.relpath(png, os.path.dirname(out)).replace(os.sep, "/")
        lines += ["![Bondplan](%s)" % rel, ""]

    lines += ["## Summary", "", "| | |", "|---|---|"]
    for name, value in [
            ("Design", cfg["DESIGN_NAME"]),
            ("Package", cfg["PACKAGE_NAME"]
             or os.path.basename(resolve(cfg, cfg["PACKAGE_GDS"]))),
            ("Die size", "%s x %s mm" % (stats["die_width_mm"],
                                         stats["die_height_mm"])),
            ("Pad pitch / opening", "%s / %s um" % (stats["pad_pitch_um"],
                                                    stats["pad_opening_um"])),
            ("Bondwires", "%d (%d to leads, %d exposed-pad downbonds)"
             % (len(rows), len(rows) - epad, epad)),
            ("Wire width", "%g um" % float(cfg["BONDWIRE_WIDTH"])),
            ("Wire length", "%s .. %s um" % (stats["min_wire_length_um"],
                                             stats["max_wire_length_um"])),
            ("Min wire-to-wire gap", "%s um" % stats["min_gap_um"]),
            ("Max lead skew", "%.1f deg" % max(skews) if skews else "-")]:
        lines.append("| %s | %s |" % (name, value))

    lines += ["", "## Bond Table", "",
              "| Pin | Die pad | Die x/y (um) | Package x/y (um) | "
              "Length (um) | Angle (deg) | Skew (deg) | Min gap (um) |",
              "|---|---|---|---|---|---|---|---|"]
    for w in rows:
        lines.append(
            "| %s | %s | %.1f / %.1f | %.1f / %.1f | %.1f | %.1f | %s | %s |"
            % (w["pin"], w["name"], w["p0"][0], w["p0"][1],
               w["p1"][0], w["p1"][1], w["length"], w["angle"],
               "-" if w.get("skew") is None else "%.1f" % w["skew"],
               "-" if w.get("min_gap") is None else "%.1f" % w["min_gap"]))
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Step 7: PNG / SVG export (PNG follows ihp130/scripts/lay2img.py)
# ---------------------------------------------------------------------------

def image_size(cfg, crop):
    width = int(cfg["IMAGE_WIDTH"])
    return width, max(1, int(round(width * crop.height() / crop.width())))


def export_png(cfg, gds_path, crop):
    try:
        import klayout.lay as klay
    except ImportError:
        klay = pya if hasattr(pya, "LayoutView") else None
    if klay is None:
        warn("PNG export skipped: klayout.lay (LayoutView) not available")
        return

    lv = klay.LayoutView()
    lv.set_config("grid-visible", "false")
    lv.set_config("grid-show-ruler", "false")
    lv.set_config("text-visible", "true")
    lv.load_layout(gds_path, 0)
    lv.max_hier()

    lv.clear_layers()
    for source, color, visible, style in IMAGE_LAYERS:     # later = drawn on top
        props = klay.LayerProperties()
        props.source = source + "@1"
        rgb = int(color[1:], 16)
        props.fill_color = rgb
        props.frame_color = rgb
        props.dither_pattern = 1 if style == "outline" else 0  # 1 = hollow
        props.visible = visible
        lv.insert_layer(lv.end_layers(), props)

    width, height = image_size(cfg, crop)
    base, ext = os.path.splitext(resolve(cfg, cfg["BONDPLAN_PNG"]))
    for suffix, bg in (("_white", "#FFFFFF"), ("_black", "#000000")):
        lv.set_config("background-color", bg)
        lv.save_image_with_options(
            base + suffix + ext, width, height,
            oversampling=int(cfg["IMAGE_OVERSAMPLING"]),
            target=crop)                            # exact box, zero border
        info("image --> %s" % (base + suffix + ext))


def svg_escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))


def export_svg(cfg, ly, top, crop):
    dbu = ly.dbu
    clip = pya.Region(pya.Box(int(crop.left / dbu), int(crop.bottom / dbu),
                              int(crop.right / dbu), int(crop.top / dbu)))
    shapes, texts = [], []
    for source, color, visible, style in IMAGE_LAYERS:
        if not visible:
            continue
        li = ly.find_layer(*parse_layer(source))
        if li is None:
            continue

        region = pya.Region(top.begin_shapes_rec(li)) & clip
        if not region.is_empty():
            parts = []
            for poly in region.each():
                rings = [poly.each_point_hull()]
                rings += [poly.each_point_hole(h) for h in range(poly.holes())]
                for ring in rings:
                    parts.append("M" + "L".join(
                        "%.2f %.2f" % (p.x * dbu, -p.y * dbu) for p in ring) + "Z")
            if style == "outline":
                paint = 'fill="none" stroke="%s" stroke-width="8"' % color
            else:
                paint = 'fill="%s" fill-rule="evenodd"' % color
            shapes.append('<path d="%s" %s/>' % ("".join(parts), paint))

        it = top.begin_shapes_rec(li)
        while not it.at_end():
            shape = it.shape()
            if shape.is_text():
                t = shape.text.transformed(it.trans())
                x, y = t.x * dbu, t.y * dbu
                if crop.contains(pya.DPoint(x, y)):
                    size = t.size * dbu if t.size > 0 else 120.0
                    anchor = SVG_ANCHOR.get(int(t.halign), "start")
                    texts.append(
                        '<text x="%.1f" y="%.1f" font-size="%.0f" '
                        'font-family="monospace" text-anchor="%s" fill="%s">'
                        '%s</text>' % (x, -y + size * 0.35, size, anchor,
                                       color, svg_escape(shape.text.string)))
            it.next()

    width, height = image_size(cfg, crop)
    base, ext = os.path.splitext(resolve(cfg, cfg["BONDPLAN_SVG"]))
    for suffix, bg in (("_white", "#FFFFFF"), ("_black", "#000000")):
        with open(base + suffix + ext, "w") as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" '
                    'viewBox="%.2f %.2f %.2f %.2f" width="%d" height="%d">\n'
                    % (crop.left, -crop.top, crop.width(), crop.height(),
                       width, height))
            f.write('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" '
                    'fill="%s"/>\n' % (crop.left, -crop.top, crop.width(),
                                       crop.height(), bg))
            f.write("\n".join(shapes + texts))
            f.write("\n</svg>\n")
        info("image --> %s" % (base + suffix + ext))


def export_images(cfg, pkg, gds_path, ly, top, table_box):
    if not (cfg["BONDPLAN_PNG"] or cfg["BONDPLAN_SVG"]):
        return
    # Zero-border crop: exact content extent, no margin. In full mode this
    # is the union of all visible drawn layers - the paper rectangle
    # ("outline" style) is excluded, so the crop lands on the frame border
    # instead of the blank A4 paper margins.
    if cfg["IMAGE_REGION"] == "full":
        crop = None
        for source, _color, visible, style in IMAGE_LAYERS:
            if not visible or style == "outline":
                continue
            li = ly.find_layer(*parse_layer(source))
            if li is None:
                continue
            bb = pya.Region(top.begin_shapes_rec(li)).bbox()
            if bb.empty():
                continue
            dbb = pya.DBox(bb.left * ly.dbu, bb.bottom * ly.dbu,
                           bb.right * ly.dbu, bb.top * ly.dbu)
            crop = dbb if crop is None else crop + dbb
        if crop is None:
            crop = top.dbbox()
    else:
        crop = pkg["view_box"]
    if table_box:
        crop += table_box
    if cfg["BONDPLAN_PNG"]:
        export_png(cfg, gds_path, crop)
    if cfg["BONDPLAN_SVG"]:
        export_svg(cfg, ly, top, crop)


# ---------------------------------------------------------------------------

def main():
    cfg_path = globals().get("config")          # klayout -rd config=...
    overrides = {}
    for arg in sys.argv[1:]:
        if arg.endswith((".yaml", ".yml")) and not cfg_path:
            cfg_path = arg
        elif "=" in arg:                        # e.g. VERSION=2.0.0
            key, _, value = arg.partition("=")
            overrides[key.strip()] = value.strip()
    cfg = load_config(cfg_path or "config.yaml", overrides)
    info("bondplan flow for design '%s'%s"
         % (cfg["DESIGN_NAME"],
            " v.%s" % cfg["VERSION"] if cfg["VERSION"] else ""))

    pads, die_bbox = detect_die_pads(cfg)
    die_layout, die_cell = extract_die(cfg)
    generate_package(cfg)
    pkg = analyze_package(cfg)

    trans = die_transform(cfg, die_bbox, pkg)
    for pad in pads:                            # die --> bondplan coordinates
        p = trans * pya.DPoint(pad["x"], pad["y"])
        pad["x"], pad["y"] = p.x, p.y
    center = trans * die_bbox.center()

    wires = assign_wires(cfg, pads, pkg, (center.x, center.y))
    check_wires(cfg, wires)                     # also fills per-wire min_gap
    stats = sheet_stats(cfg, pads, die_bbox, wires)
    out, bp_layout, bp_top, table_box = build_bondplan(
        cfg, pkg, die_layout, die_cell, trans, wires, stats)
    write_report(cfg, wires, stats)
    export_images(cfg, pkg, out, bp_layout, bp_top, table_box)
    info("done!")


main()
