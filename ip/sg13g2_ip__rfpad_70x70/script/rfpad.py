# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

"""RF pad generator for the IHP SG13G2 PDK.

Draws the fixed cell ``sg13g2_ip__rfpad_70x70``, an 80 x 250 um pad cell that takes the slot of ``sg13g2_IOPadAnalog`` plus its 70 x 70 bondpad.
y = 0 is the die edge, the IO library's own convention.

    y 0..70     the ``bondpad`` PCell, octagon, ``bottomMetal='3'``, over a solid Metal1 shield on core ``vss``
    y 70..250   the IO row: the library's rail bands shifted by +70, the PDK's ``diodevss_2kv`` and ``diodevdd_2kv`` on the core rails, and an RC-triggered ``vdd`` to ``vss`` clamp under the bands

The output leaves the plate through a teardrop and runs on TopMetal2 through a corridor cut in the TopMetal2 and TopMetal1 rails.
``iovss`` and ``iovdd`` cross it on Metal3 to Metal5 and the Metal2 strips under them.
The script checks its own geometry and connectivity before it writes anything, because DRC and LVS both miss a pad shorted to a rail.

Must be executed inside KLayout's batch mode (``klayout -zz``) because it relies on the KLayout PCell engine and the SG13_dev library.

Command-line arguments are passed with ``-rd key=value``, at least one of them is required:
    gds_output   Output path for the GDS file.
    lef_output   Output path for the LEF file.
    lib_output   Output path for the Liberty file.

Example (single-line, copy-paste friendly):

    klayout -n sg13g2 -zz -r rfpad.py -rd gds_output=gds/rfpad.gds -rd lef_output=lef/rfpad.lef -rd lib_output=lib/rfpad.lib
"""
# pylint: disable=import-error
import pathlib
import re
import sys
import pya

# IHP SG13_dev PCell library ships with the PDK and contains the ``bondpad`` and ``esd`` PCells.
LIB = 'SG13_dev'
PCELL = 'bondpad'


def write_gds(layout, path):
    """Write a GDS without timestamps, so that a rebuild of the same geometry gives the same bytes."""
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    opt = pya.SaveLayoutOptions()
    opt.format = 'GDS2'
    opt.gds2_write_timestamps = False
    layout.write(path, opt)
    print(f"GDS written to: {path}")


# ---------------------------------------------------------------------------
# Dimensions, all in um
# ---------------------------------------------------------------------------

RF_CELL = 'sg13g2_ip__rfpad_70x70'
# The rail bands the cell abuts are read from this LEF, never written down here.
IO_LEF = pathlib.Path(__file__).resolve().parents[2] / 'sg13g2_io_custom' / 'lef' / 'sg13g2_io.lef'
IO_CELL = 'sg13g2_IOPadAnalog'
RF_SITE = 'sg13g2_ioSite'
# Metal capacitance on the pad node plus both junctions at 0.6 V reverse, written into the Liberty for the resizer.
RF_PAD_CAP_PF = 0.204

RF_W, RF_H = 80.0, 250.0
PAD_D = 70.0
PAD_CX, PAD_CY = 40.0, 35.0
PAD_PIN = 49.0            # the octagon's inscribed square is 49.5 across
IO_Y0 = 70.0              # the IO row starts at the pad height
# TRACE_W carries the ESD strike from the pad to the tap, TRACE_W_OUT only the output (TM2.a).
TRACE_W = 4.92
TRACE_W_OUT = 2.00
TRACE_X = 40.0
CORRIDOR_LAYERS = ('TopMetal2', 'TopMetal1')
# Rail to RF line. TopMetal1 is cut in the same corridor because the rail right under the line is what costs capacitance.
TM2_RAIL_GAP = 5.0
TM1_B = 1.64              # TM1.b, the top of the pad's TopMetal1 bar keeps it from the core band above
# Passiv edge to pad edge: the PCell's 2.1 leaves all TopVia2 under the opening (Pad.kR), the diagonal cuts need 2.7, and its passEncl parameter changes nothing.
PAD_PASS_ENCL = 2.7
SHIELD_OVER = 3.0         # shield collar past the pad
NOFILL_HALO = 5.0
# The exit: 7 um of unchanged metal past dfpad for Pad.fR, then a 45 degree taper, because TopMetal1 is 0/45/90 only.
TEAR_W = 14.92
PAD_FR = 7.0
TEAR_R = (TEAR_W - TRACE_W) / 2.0

# The ESD pair straddles this gap below the core bands, which carry no TopMetal1.
ESD_GAP = (204.0, 210.0)
ESD_MODELS = ('diodevss_2kv', 'diodevdd_2kv')
ESD_PAD_FINGER = 18.53    # local y centre of the pad finger in the gap
ESD_PAD_TAB_X = -0.30     # local x centre of the pad tab, placed under TRACE_X
M2_KEEPOUT = 0.80         # strip clearance to the ESD pair, Mn.f is 0.6
ESD_KEEP = 0.60           # Mn.f, the rail bands are wider than 10 um
TV1_M5_ENC = 0.10         # TV1.c, the TopMetal1 side is ESD_ENC's TV1.d
VIA = {'Via1': 0.19, 'Via2': 0.19, 'Via3': 0.19, 'Via4': 0.19, 'TopVia1': 0.42, 'TopVia2': 0.90}
# Vn.b1 asks for 0.29 beyond 3 vias, so arrays pitch 0.48 and not 0.41.
ESD_ENC = {'Via1': 0.06, 'Via2': 0.06, 'Via3': 0.06, 'Via4': 0.06, 'TopVia1': 0.42, 'TopVia2': 0.50}
ESD_PITCH = {'Via1': 0.48, 'Via2': 0.48, 'Via3': 0.48, 'Via4': 0.48, 'TopVia1': 0.90, 'TopVia2': 1.96}
TIE_PITCH = {'Via1': 0.48, 'Via2': 0.48, 'Via3': 0.48, 'Via4': 0.48, 'TopVia1': 0.84, 'TopVia2': 1.96}
# A regression has to stay above these, far under what the arrays place.
ESD_VIA_FLOOR = {'Via1': 24, 'Via2': 24, 'Via3': 12, 'Via4': 12, 'TopVia1': 6, 'TopVia2': 4}
STRIP_VIA2_FLOOR = 100
CLAMP_VIA_FLOOR = 200

# The shield reaches core vss on Metal1, Slt.c allows 30 um without slits.
STRAP_X = ((2.0, 29.0), (51.0, 78.0))
STRAP_Y = (50.0, 80.5)
# Metal2 strips stay inside the cell, a strip run to the edge could merge with a neighbour's metal of another net.
STRIP_INSET = 1.0
STRIP_MIN = 2.0           # a strip piece narrower than this is dropped

RF_LAYERS = {
    'Metal1': (8, 0), 'Metal2': (10, 0), 'Metal3': (30, 0), 'Metal4': (50, 0), 'Metal5': (67, 0),
    'TopMetal1': (126, 0), 'TopMetal2': (134, 0), 'Via1': (19, 0), 'Via2': (29, 0), 'Via3': (49, 0), 'Via4': (66, 0),
    'TopVia1': (125, 0), 'TopVia2': (133, 0), 'NoMetFiller': (160, 0), 'prBoundary': (189, 4),
    'RecogEsd': (99, 30),
    'Text': (63, 0),
    'dfpad': (41, 0),
    'Activ': (1, 0), 'GatPoly': (5, 0), 'Cont': (6, 0), 'pSD': (14, 0),
    'NWell': (31, 0), 'Substrate': (40, 0), 'ThickGateOx': (44, 0),
    'SalBlock': (28, 0), 'EXTBlock': (111, 0),
    # LVS reads labels from datatype 25, the LEF reads pins from datatype 2 around a label.
    'Metal1.text': (8, 25), 'Metal2.text': (10, 25),
    'Metal3.text': (30, 25), 'Metal4.text': (50, 25), 'Metal5.text': (67, 25),
    'TopMetal1.text': (126, 25), 'TopMetal2.text': (134, 25),
    'Metal3.pin': (30, 2), 'Metal4.pin': (50, 2), 'Metal5.pin': (67, 2),
    'TopMetal1.pin': (126, 2), 'TopMetal2.pin': (134, 2),
}

# Supply clamp: IHP's IOPadVdd clamp with its source on vss and the NMOS doubled, redrawn on FEOL, Metal1 and Metal2 because IHP's cell would cut the Metal3 that carries iovss and iovdd across the corridor.
#   y 132..200  clamp halves, x 1..27 and 53..79, mirrored about x = 40
#   y 137..185  resistor, centre column
#   y 76..123   capacitor x 5..51, inverter x 55..74
CLAMP_GRID = 0.005
# vss lane down each cell edge: the shield's way to vss and the tap of every p+ ring on that side.
LANE_M1 = (1.0, 4.8)
LANE_M2 = (1.0, 4.0)
LANE_Y = (50.0, 228.0)
LANE_M2_Y0 = 74.0          # Metal2 stays off the pad, it is 2.91 um under TopMetal1

CONT, CONT_PITCH = 0.16, 0.34
V1, V1_PITCH = 0.19, 0.48
TAP_RING_GAP, TAP_RING_W = 0.70, 0.80
TGO_X, TGO_Y = 0.30, 0.34  # beyond poly in x, TGO.c beyond the gate in y
TGO_RING = 0.30            # TGO.b is 0.27
PSD_X = 0.45               # pSD past a p+ gate's end, pSD.i1 is 0.40

# Clamp NMOS: IHP's finger, L 0.6, two 9 um activ columns (the 10 um finger limit), gates contacted between them.
CL_COLS = ((5.8, 14.8), (16.6, 25.6))
CL_GATE_X = 15.7
CL_Y0 = 134.4
CL_GATES = 42
# Metal2 over the fingers, each stripe running straight up into its core band.
CL_STRIPES = ((5.8, 7.4, 'vss'), (8.2, 9.8, 'vdd'), (10.6, 12.2, 'vss'),
              (13.0, 14.6, 'vdd'), (16.8, 18.4, 'vss'), (19.2, 20.8, 'vdd'),
              (21.6, 23.2, 'vss'), (24.0, 25.6, 'vdd'))
STRIPE_TOP = {'vss': 228.0, 'vdd': 248.0}
# vdd Metal3 and vdd Metal4 are two conductors here, each vdd stripe ties them through a Metal3 island cut out of the vss band.
ISLAND_Y = (210.0, 218.0)
ISLAND_KEEP = 0.60         # Mn.f
GATE_BUS = 0.50
GATE_LINE = (129.0, 130.0)

# Trigger, starting 11.2 um from the pad for Pad.d1R.
TR_Y0 = 81.3
RES_LINE = (126.0, 127.0)
CAP = ({'cols': ((6.6, 15.6), (17.4, 26.4)), 'gate_x': 16.5, 'gates': 4},
       {'cols': ((29.2, 38.2), (40.0, 49.0)), 'gate_x': 39.1, 'gates': 3})
CAP_L = 9.5
INV_GATE_X = 56.8
INV_NMOS = {'cols': ((57.65, 64.4), (65.2, 71.95)), 'gates': 8}
INV_PMOS = {'cols': ((57.4, 64.4), (65.2, 72.2)), 'gates': 25}
INV_L = 0.5
OUT_STRIPE = (66.2, 67.8)
VSS_STRIPE = (69.9, 71.5)
VDD_STRIPE = (RF_W - 9.8, RF_W - 8.2)
NW_TIE = 0.24              # NW.e
NW_SPACE = 1.00
# rppd 1 x 20 um, 13 + 12 in series, heads clear of the band gaps at y 130..136 and 161.5..163.5.
RES_X0, RES_PITCH = 28.5, 1.8
RES_Y = (137.5, 164.3)
RES_N = (13, 12)
RES_L = 20.0
RES_HEAD = (-0.43, -0.13)  # Metal1 head below the body, the one above is body top + (0.13, 0.43)

# LEF abstract
LEF_METALS = {'Metal1': (8, 0), 'Metal2': (10, 0), 'Metal3': (30, 0), 'Metal4': (50, 0), 'Metal5': (67, 0), 'TopMetal1': (126, 0), 'TopMetal2': (134, 0)}
LEF_PINS = ('vss', 'vdd', 'iovss', 'iovdd', 'pad', 'padbare')
LEF_USE = {'vss': 'GROUND', 'vdd': 'POWER', 'iovss': 'GROUND', 'iovdd': 'POWER'}
# padbare is the inner end of the pad conductor. It carries no label, because the CDL has no such node, so a box names it.
LEF_PADBARE_BOX = (36.0, 239.0, 44.0, 250.0)
LEF_GRID = 5               # dbu
LEF_SLANT_STEP = 1000      # dbu, band height where an edge is not axis-parallel
# Mn.e: the router keeps Mn.b from an obstruction, the real shape under a wide one asks for 0.24.
WIDE_W, WIDE_SP, MIN_SP = 0.39, 0.24, 0.21

RF_LIB = '''/*
 * Liberty view of %(cell)s, written by script/rfpad.py.
 * The capacitance on pad and padbare is measured, see the README.
 * No timing arc: a pad is not a delay element, there is nothing for STA to time.
 */
library (%(cell)s) {
  delay_model : table_lookup;
  capacitive_load_unit (1,pf);
  current_unit : "1uA";
  leakage_power_unit : "1pW";
  pulling_resistance_unit : "1kohm";
  time_unit : "1ns";
  voltage_unit : "1V";

  input_threshold_pct_fall : 50;
  input_threshold_pct_rise : 50;
  output_threshold_pct_fall : 50;
  output_threshold_pct_rise : 50;
  slew_derate_from_library : 1;
  slew_lower_threshold_pct_fall : 10;
  slew_lower_threshold_pct_rise : 10;
  slew_upper_threshold_pct_fall : 90;
  slew_upper_threshold_pct_rise : 90;

  nom_process : 1.0;
  nom_temperature : 25.0;
  nom_voltage : 1.20;

  operating_conditions (typ) {
    process : 1.0;
    temperature : 25.0;
    voltage : 1.20;
    tree_type : balanced_tree;
  }
  default_operating_conditions : typ;

  cell (%(cell)s) {
    area : 20000;
    dont_touch : true;
    dont_use : true;
    pad_cell : true;
    timing_model_type : abstracted;

    pg_pin (vss)   { pg_type : primary_ground; voltage_name : "vss"; }
    pg_pin (vdd)   { pg_type : primary_power;  voltage_name : "vdd"; }
    pg_pin (iovss) { pg_type : primary_ground; voltage_name : "iovss"; }
    pg_pin (iovdd) { pg_type : primary_power;  voltage_name : "iovdd"; }

    pin (pad) {
      direction : inout;
      capacitance : %(cap).4f;
      related_ground_pin : vss;
      related_power_pin : vdd;
    }
    pin (padbare) {
      direction : inout;
      capacitance : %(cap).4f;
      related_ground_pin : vss;
      related_power_pin : vdd;
    }
  }
}
'''


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rails(lef_path, macro):
    """Supply rail bands of ``macro``, as {net: [(layer, y0, y1), ...]}.

    Only full-width rects on Metal3 and up count, the others are substrate and well.
    """
    with open(lef_path, encoding='utf-8') as fh:
        text = fh.read()
    body = re.search(r"^MACRO %s$(.*?)^END %s$" % (macro, macro), text, re.S | re.M)
    if body is None:
        raise KeyError("no MACRO %s in %s" % (macro, lef_path))
    width = float(re.search(r"SIZE\s+([\d.]+)\s+BY", body.group(1)).group(1))

    out = {n: set() for n in ('iovss', 'iovdd', 'vss', 'vdd')}
    net = layer = None
    for line in body.group(1).splitlines():
        line = line.strip()
        if line.startswith('#'):
            continue
        m = re.match(r"PIN\s+(\S+)", line)
        if m:
            net, layer = m.group(1), None
            continue
        # A bare END closes a PORT, "END <name>" closes the PIN.
        if line == 'END':
            layer = None
            continue
        if line.startswith('END '):
            net = layer = None
            continue
        m = re.match(r"LAYER\s+(\S+)\s*;", line)
        if m:
            layer = m.group(1)
            continue
        m = re.match(r"RECT\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s*;", line)
        if m and net in out and layer in ('Metal3', 'Metal4', 'Metal5', 'TopMetal1', 'TopMetal2'):
            x0, y0, x1, y1 = (float(v) for v in m.groups())
            if x0 == 0.0 and x1 == width:
                out[net].add((layer, y0, y1))
    return {n: sorted(v) for n, v in out.items()}


def _snap(v):
    return round(round(v / CLAMP_GRID) * CLAMP_GRID, 3)


# ---------------------------------------------------------------------------
# Supply clamp
# ---------------------------------------------------------------------------

class Mos:
    """One MOS: activ columns, horizontal gates, S/D strips.

    ``sd`` alternates nets from the bottom, regions are ``sd_w`` wide (``drain_w`` per net overrides) and the two end ones ``sd_end``.
    ``m1`` gives per net the S/D Metal1 width and its contact rows, ``m1_ext`` per column the x extent of the S/D Metal1.
    """

    def __init__(self, cols, y0, gates, L, sd, sd_w=0.64, sd_end=0.47,
                 m1=None, drain_w=None, pmos=False, poly_x=None, gate_x=None,
                 m1_ext=None):
        self.cols, self.y0, self.gates, self.L = cols, y0, gates, L
        self.sd, self.sd_w, self.sd_end = sd, sd_w, sd_end
        self.m1 = m1 or {}
        self.pmos = pmos
        self.gate_x = gate_x
        self.poly_x = poly_x or (cols[0][0] - 0.4, cols[-1][1] + 0.4)
        self.m1_ext = m1_ext or [(c0 + 0.05, c1 - 0.05) for c0, c1 in cols]
        self.regions, self.gate_ys = [], []
        y = y0
        for i in range(gates + 1):
            net = sd[i % 2]
            w = sd_end if i in (0, gates) else (drain_w or {}).get(net, sd_w)
            self.regions.append((net, _snap(y), _snap(y + w), i))
            y += w
            if i < gates:
                self.gate_ys.append((_snap(y), _snap(y + L)))
                y += L
        self.y1 = _snap(y)

    def tgo(self):
        return (self.poly_x[0] - TGO_X, self.y0 - TGO_Y,
                self.poly_x[1] + TGO_X, self.y1 + TGO_Y)


class Clamp:
    """Draws the supply clamp into ``RfPad`` ``g``, ``m2[net]`` collects each net's Metal2 so the supply strips can keep off it."""

    def __init__(self, g):
        self.g = g
        self.dbu = g.ly.dbu
        self.m2 = {}
        self.counts = {}

    def rect(self, layer, x0, y0, x1, y1, net=None, mirror=False):
        boxes = [(x0, x1)]
        if mirror:
            boxes.append((RF_W - x1, RF_W - x0))
        for a, b in boxes:
            box = pya.DBox(_snap(a), _snap(y0), _snap(b), _snap(y1))
            self.g.box(layer, box.left, box.bottom, box.right, box.top)
            if layer == 'Metal2':
                if net is None:
                    raise AssertionError("Metal2 without a net at %s" % box)
                self.m2.setdefault(net, pya.Region()).insert(box.to_itype(self.dbu))

    def cut(self, layer, cx, cy, size, mirror=False):
        a = size / 2.0
        self.rect(layer, cx - a, cy - a, cx + a, cy + a, mirror=mirror)

    def count(self, key, n=1):
        self.counts[key] = self.counts.get(key, 0) + n

    def cut_row(self, layer, x0, cy, n, pitch, size, mirror=False, vertical=False):
        """``n`` cuts from centre (x0, cy) on ``pitch``, as one array reference of a one-cut cell to keep the GDS small."""
        if n <= 0:
            return
        name = "%s_%s" % (self.g.top.name, layer.lower())
        ly = self.g.ly
        if ly.has_cell(name):
            cell = ly.cell(name)
        else:
            cell = ly.create_cell(name)
            h = int(round(size / 2.0 / self.dbu))
            cell.shapes(self.g.lay(layer)).insert(pya.Box(-h, -h, h, h))
        step = pya.Vector(0, int(round(pitch / self.dbu))) if vertical else pya.Vector(int(round(pitch / self.dbu)), 0)
        xs = [x0]
        if mirror:
            xs.append(RF_W - x0 - (0 if vertical else (n - 1) * pitch))
        for x in xs:
            org = pya.Vector(int(round(_snap(x) / self.dbu)), int(round(_snap(cy) / self.dbu)))
            self.g.top.insert(pya.CellInstArray(cell.cell_index(), pya.Trans(org), step, pya.Vector(0, 0), n, 1))

    def via_row(self, x0, x1, cy, key, mirror=False):
        """Via1 along y = cy wherever a cut fits 0.155 inside x0..x1."""
        n = int((x1 - 0.155 - V1 / 2.0 - (x0 + 0.25)) / V1_PITCH + 1e-9) + 1
        self.cut_row('Via1', x0 + 0.25, cy, n, V1_PITCH, V1, mirror)
        self.count(key, n * (2 if mirror else 1))

    def ring(self, inner, ptype, mirror=False, skip=()):
        """A tap ring around ``inner``: p+ on the substrate (vss) or n+ in the well (vdd). ``skip`` names sides another ring already has."""
        x0, y0, x1, y1 = inner
        o = (x0 - TAP_RING_W, y0 - TAP_RING_W, x1 + TAP_RING_W, y1 + TAP_RING_W)
        sides = {'b': (o[0], o[1], o[2], y0), 't': (o[0], y1, o[2], o[3]),
                 'l': (o[0], y0, x0, y1), 'r': (x1, y0, o[2], y1)}
        for key, (a, b, c, d) in sides.items():
            if key in skip:
                continue
            self.rect('Activ', a, b, c, d, mirror=mirror)
            self.rect('Metal1', a, b, c, d, mirror=mirror)
            if ptype:
                self.rect('Substrate', a, b, c, d, mirror=mirror)
                self.rect('pSD', a - 0.03, b - 0.03, c + 0.03, d + 0.03, mirror=mirror)
            horiz = (c - a) > (d - b)
            lo, hi = (a, c) if horiz else (b, d)
            if horiz and 'l' in skip:   # the other ring's corner has contacts
                lo += TAP_RING_W
            mid = ((b + d) if horiz else (a + c)) / 2.0
            n = int((hi - 0.30 - (lo + 0.30)) / 0.50 + 1e-9) + 1
            if horiz:
                self.cut_row('Cont', lo + 0.30, mid, n, 0.50, CONT, mirror)
            else:
                self.cut_row('Cont', mid, lo + 0.30, n, 0.50, CONT, mirror, vertical=True)
            self.count('Cont ring', n * (2 if mirror else 1))
        return o

    def mos(self, m, stripes, gate_via=True, mirror=False, tag=''):
        """Draw Mos ``m``, with Via1 from each S/D strip to every stripe of its net."""
        for c0, c1 in m.cols:
            self.rect('Activ', c0, m.y0, c1, m.y1, mirror=mirror)
        if m.pmos:
            self.rect('pSD', m.cols[0][0] - PSD_X, m.y0 - 0.30,
                      m.cols[-1][1] + PSD_X, m.y1 + 0.30, mirror=mirror)
        self.rect('ThickGateOx', *m.tgo(), mirror=mirror)
        for a, b in m.gate_ys:
            self.rect('GatPoly', m.poly_x[0], a, m.poly_x[1], b, mirror=mirror)
            self.gate_contact(m.gate_x, a, b, gate_via, mirror, tag)
        for net, a, b, i in m.regions:
            mw, rows = m.m1.get(net, (0.21, (0.0,)))
            # The contact keeps half a region from the gates it faces.
            if i == 0:
                cy = b - m.sd_w / 2.0
            elif i == m.gates:
                cy = a + m.sd_w / 2.0
            else:
                cy = (a + b) / 2.0
            for (c0, c1), (e0, e1) in zip(m.cols, m.m1_ext):
                self.rect('Metal1', e0, cy - mw / 2.0, e1, cy + mw / 2.0, mirror=mirror)
                n = int((c1 - 0.20 - (c0 + 0.20)) / CONT_PITCH + 1e-9) + 1
                for dy in rows:
                    self.cut_row('Cont', c0 + 0.20, cy + dy, n, CONT_PITCH, CONT, mirror)
                    self.count('Cont ' + tag, n * (2 if mirror else 1))
            for s0, s1, n in stripes:
                if n == net:
                    self.via_row(s0, s1, cy, 'Via1 %s %s' % (tag, net), mirror)

    def gate_contact(self, x, a, b, via, mirror, tag):
        """Contacts down the gate at x, a Metal1 pad, and a Via1 at its centre."""
        cy = (a + b) / 2.0
        n = max(1, int(((b - a) - 0.30) / CONT_PITCH) + 1)
        y = cy - (n - 1) * CONT_PITCH / 2.0
        for _ in range(n):
            self.cut('Cont', x, y, CONT, mirror)
            y += CONT_PITCH
        pad = 0.25 if (b - a) < 1.0 else (b - a) / 2.0 - 0.05
        self.rect('Metal1', x - 0.20, cy - pad, x + 0.20, cy + pad, mirror=mirror)
        if via:
            self.cut('Via1', x, cy, V1, mirror)
            self.count('Via1 gate ' + tag, 2 if mirror else 1)

    def clamp(self):
        m = Mos(CL_COLS, CL_Y0, CL_GATES, 0.6, ('vss', 'vdd'),
                drain_w={'vdd': 1.18}, m1={'vdd': (0.62, (-0.17, 0.17))},
                gate_x=CL_GATE_X)
        self.mos(m, CL_STRIPES, mirror=True, tag='clamp')
        t = m.tgo()
        self.ring((t[0] - 0.40, m.y0 - TAP_RING_GAP, t[2] + TGO_RING, m.y1 + TAP_RING_GAP), True, mirror=True)
        for s0, s1, net in CL_STRIPES:
            self.rect('Metal2', s0, m.y0, s1, STRIPE_TOP[net], net=net, mirror=True)
        g0, g1 = CL_GATE_X - GATE_BUS / 2.0, CL_GATE_X + GATE_BUS / 2.0
        self.rect('Metal2', g0, GATE_LINE[0], g1, m.gate_ys[-1][1], net='gate', mirror=True)
        self.rect('Metal2', g0, GATE_LINE[0], OUT_STRIPE[1], GATE_LINE[1], net='gate')

    def islands(self):
        """Record the Metal3 holes before ``RfPad.io_rails`` draws the band."""
        self.isl = []
        for s0, s1, net in CL_STRIPES:
            if net != 'vdd':
                continue
            for a, b in ((s0, s1), (RF_W - s1, RF_W - s0)):
                self.isl.append(pya.DBox(a, ISLAND_Y[0], b, ISLAND_Y[1]))
                self.g.m3_holes.append(pya.DBox(a - ISLAND_KEEP, ISLAND_Y[0], b + ISLAND_KEEP,
                                                ISLAND_Y[1] + ISLAND_KEEP))
        return self

    def island_vias(self):
        R = lambda b: pya.Region(b.to_itype(self.dbu))  # noqa: E731
        for isl in self.isl:
            self.g.box('Metal3', isl.left, isl.bottom, isl.right, isl.top)
            self.count('Via2 island', self.g._fill_vias('Via2', R(isl)))
            self.count('Via3 island', self.g._fill_vias('Via3', R(isl)))

    def lanes(self):
        self.rect('Metal1', LANE_M1[0], LANE_Y[0], LANE_M1[1], LANE_Y[1], mirror=True)
        self.rect('Metal2', LANE_M2[0], LANE_M2_Y0, LANE_M2[1], LANE_Y[1], net='vss', mirror=True)
        core = pya.Region()
        for x0, x1 in (LANE_M2, (RF_W - LANE_M2[1], RF_W - LANE_M2[0])):
            core.insert(pya.DBox(x0, LANE_M2_Y0, x1, LANE_Y[1]).to_itype(self.dbu))
        e = int(round((V1 / 2.0 + 0.06) / self.dbu))
        self.counts['Via1 lane'] = self.g._lattice('Via1', core.sized(-e))

    def capacitor(self):
        """hv_nmos, gate on the RC node, source, drain and bulk on vss. Its S/D Metal1 runs out to the rings, it carries no current."""
        y0 = TR_Y0 + TAP_RING_W + TAP_RING_GAP
        for k, c in enumerate(CAP):
            (a0, a1), (b0, b1) = c['cols']
            m = Mos(c['cols'], y0, c['gates'], CAP_L, ('vss', 'vss'), sd_end=0.64,
                    gate_x=c['gate_x'],
                    m1_ext=((a0 - 1.2, a1 - 0.05), (b0 + 0.05, b1 + 1.2)))
            self.mos(m, (), gate_via=False, tag='cap')
            t = m.tgo()
            inner = (t[0] - TGO_RING, TR_Y0 + TAP_RING_W, t[2] + TGO_RING, m.y1 + TAP_RING_GAP)
            self.ring(inner, True, skip=('l',) if k else ())
            gx = c['gate_x']
            self.rect('Metal2', gx - GATE_BUS / 2.0, m.gate_ys[0][0], gx + GATE_BUS / 2.0,
                      RES_LINE[1], net='res_cap')
            for a, b in m.gate_ys:          # a column of Via1 on each long gate
                y = a + 0.40
                while y <= b - 0.40 + 1e-9:
                    self.cut('Via1', gx, y, V1)
                    self.count('Via1 gate cap')
                    y += V1_PITCH
        self.rect('Metal2', CAP[0]['gate_x'] - GATE_BUS / 2.0, RES_LINE[0],
                  INV_GATE_X + GATE_BUS / 2.0, RES_LINE[1], net='res_cap')

    def inverter(self):
        def dev(spec, y, sd, pmos):
            (c0, c1), (d0, d1) = spec['cols']
            return Mos(spec['cols'], y, spec['gates'], INV_L, sd, sd_end=0.64,
                       pmos=pmos, gate_x=INV_GATE_X,
                       poly_x=(INV_GATE_X - 0.30, d1 + 0.4),
                       m1_ext=((c0 + 0.05, d1 - 0.05), (d0, d1 - 0.05)))

        n = dev(INV_NMOS, TR_Y0 + TAP_RING_W + TAP_RING_GAP, ('vss', 'out'), False)
        self.mos(n, ((OUT_STRIPE[0], OUT_STRIPE[1], 'out'),
                     (VSS_STRIPE[0], VSS_STRIPE[1], 'vss')), tag='inv')
        t = n.tgo()
        n_ring = self.ring((t[0] - TGO_RING, TR_Y0 + TAP_RING_W, t[2] + TGO_RING,
                            n.y1 + TAP_RING_GAP), True)
        # The PMOS sits in its own well, NW_SPACE above the NMOS ring.
        py = n_ring[3] + NW_SPACE + NW_TIE + TAP_RING_W + TAP_RING_GAP
        p = dev(INV_PMOS, py, ('vdd', 'out'), True)
        self.mos(p, ((OUT_STRIPE[0], OUT_STRIPE[1], 'out'),
                     (VDD_STRIPE[0], VDD_STRIPE[1], 'vdd')), tag='inv')
        t = p.tgo()
        p_ring = self.ring((t[0] - TGO_RING, py - TAP_RING_GAP, t[2] + TGO_RING,
                            p.y1 + TAP_RING_GAP), False)
        self.rect('NWell', p_ring[0] - NW_TIE, p_ring[1] - NW_TIE,
                  p_ring[2] + NW_TIE, p_ring[3] + NW_TIE)
        self.rect('Metal2', INV_GATE_X - GATE_BUS / 2.0, n.gate_ys[0][0],
                  INV_GATE_X + GATE_BUS / 2.0, RES_LINE[1], net='res_cap')
        self.rect('Metal2', OUT_STRIPE[0], n.y0, OUT_STRIPE[1], GATE_LINE[1], net='out')
        self.rect('Metal2', VSS_STRIPE[0], TR_Y0, VSS_STRIPE[1], n.y1, net='vss')
        self.rect('Metal2', VSS_STRIPE[0], TR_Y0, RF_W - LANE_M2[1], TR_Y0 + TAP_RING_W, net='vss')
        self.via_row(VSS_STRIPE[0], VSS_STRIPE[1], TR_Y0 + TAP_RING_W / 2.0, 'Via1 ring')
        self.rect('Metal2', VDD_STRIPE[0], p_ring[1], VDD_STRIPE[1], CL_Y0, net='vdd')
        for yc in (p_ring[1] + TAP_RING_W / 2.0, p_ring[3] - TAP_RING_W / 2.0):
            self.via_row(VDD_STRIPE[0], VDD_STRIPE[1], yc, 'Via1 ring')

    def resistor(self):
        """25 rppd in series, a serpentine closed by Metal1 bars on the heads, vdd at the upper tier's left end, the RC node at the lower tier's."""
        # Calculate: the default recomputes l from R and ignores the l given here.
        var = self.g._variant('rppd', {'w': '1u', 'l': '%gu' % RES_L, 'Calculate': 'w&l'})
        xs1 = [RES_X0 + k * RES_PITCH for k in range(RES_N[0])]
        xs2 = [xs1[-1] - j * RES_PITCH for j in range(RES_N[1])]
        insts = []
        for xs, y0 in ((xs1, RES_Y[0]), (xs2, RES_Y[1])):
            for x in xs:
                insts.append(self.g.top.insert(pya.DCellInstArray(var, pya.DTrans(pya.DVector(x, y0)))))
        for i in insts:
            i.flatten()
        # One SalBlock, EXTBlock and pSD per tier: per strip they would sit under Sal.b.
        for xs, y0 in ((xs1, RES_Y[0]), (xs2, RES_Y[1])):
            x0, x1 = min(xs), max(xs) + 1.0
            self.rect('SalBlock', x0 - 0.2, y0, x1 + 0.2, y0 + RES_L)
            self.rect('EXTBlock', x0 - 0.2, y0 - 0.61, x1 + 0.2, y0 + RES_L + 0.61)
            self.rect('pSD', x0 - 0.18, y0 - 0.61, x1 + 0.18, y0 + RES_L + 0.61)
        self.g.top.shapes(self.g.ly.layer(8, 2)).clear()   # the PCell's pins

        def head(x, y0, top):
            h0, h1 = (RES_L + 0.13, RES_L + 0.43) if top else RES_HEAD
            return (x + 0.02, y0 + h0, x + 0.98, y0 + h1)

        def bar(x_a, x_b, y0, top):
            a, b = head(x_a, y0, top), head(x_b, y0, top)
            self.rect('Metal1', min(a[0], b[0]), a[1], max(a[2], b[2]), a[3])

        for k in range(RES_N[0] - 1, 0, -1):
            bar(xs1[k], xs1[k - 1], RES_Y[0], top=(RES_N[0] - 1 - k) % 2 == 1)
        for j in range(RES_N[1] - 1, 0, -1):
            bar(xs2[j], xs2[j - 1], RES_Y[1], top=(RES_N[1] - 1 - j) % 2 == 0)
        # The tiers meet on the right.
        lo, hi = head(xs1[-1], RES_Y[0], True), head(xs2[0], RES_Y[1], False)
        self.rect('Metal1', lo[0], lo[1], lo[2], hi[3])
        # vdd: a Metal2 jog from the left half's corridor-side stripe.
        h = head(xs2[-1], RES_Y[1], False)
        cy = (h[1] + h[3]) / 2.0
        self.rect('Metal2', CL_STRIPES[-1][0], cy - 0.30, h[2], cy + 0.30, net='vdd')
        self.via_row(h[0] - 0.10, h[2] + 0.10, cy, 'Via1 res')
        # RC node: Metal1 down from the lower tier's first head, under the gate line.
        h = head(xs1[0], RES_Y[0], False)
        self.rect('Metal1', h[0], RES_LINE[0], h[2], h[3])
        self.via_row(h[0] - 0.10, h[2] + 0.10, (RES_LINE[0] + RES_LINE[1]) / 2.0, 'Via1 res')

    def build(self):
        self.lanes()
        self.clamp()
        self.island_vias()
        self.capacitor()
        self.inverter()
        self.resistor()
        return self


# ---------------------------------------------------------------------------
# The cell
# ---------------------------------------------------------------------------

class RfPad:
    """Draws the RF pad into a new layout, ``build()`` returns (layout, top cell)."""

    def __init__(self):
        self.ly = pya.Layout(True)
        self.ly.dbu = 0.001
        self.top = self.ly.cell(self.ly.add_cell(RF_CELL))

    def lay(self, name):
        return self.ly.layer(*RF_LAYERS[name])

    def box(self, name, x0, y0, x1, y1):
        self.top.shapes(self.lay(name)).insert(pya.DBox(x0, y0, x1, y1))

    def pin_box(self, layer, x0, y0, x1, y1):
        """Pin shape: the wanted rectangle intersected with the drawn metal, because a pin past its conductor is Pin.g."""
        drawn = pya.Region(self.top.begin_shapes_rec(self.lay(layer)))
        want = pya.Region(pya.DBox(x0, y0, x1, y1).to_itype(self.ly.dbu))
        got = (want & drawn).merged()
        if got.is_empty():
            raise AssertionError("no %s under the intended pin box (%.3f %.3f %.3f %.3f)" % (layer, x0, y0, x1, y1))
        self.top.shapes(self.lay(layer + '.pin')).insert(got)

    def _variant(self, name, params):
        lib = pya.Library.library_by_name(LIB, 'sg13g2')
        ids = {lib.layout().pcell_declaration(i).name(): i for i in lib.layout().pcell_ids()}
        return self.ly.add_pcell_variant(lib, ids[name], params)

    def _place(self, var, x, y):
        """Place a PCell variant by its bbox, because the bondpad octagon is 70.010 tall and centring it would hang 5 nm off the cell."""
        bb = self.ly.cell(var).dbbox()
        self.top.insert(pya.DCellInstArray(var, pya.DTrans(pya.DVector(x - bb.left, y - bb.bottom))))

    def pad_stack(self):
        var = self._variant(PCELL, {'diameter': '%.1fu' % PAD_D, 'shape': 'octagon', 'bottomMetal': '3'})
        self._place(var, PAD_CX - PAD_D / 2.0, 0.0)
        self.pad_top = self.ly.cell(var).dbbox().height()
        self.tear_top = self.pad_top + PAD_FR + TEAR_R
        self.tap_top = ESD_GAP[1]

    def pad_opening(self):
        """Redraw the Passiv opening PAD_PASS_ENCL inside dfpad, the 5 nm snap because sizing moves the 45 degree edges off the grid."""
        dfpad = pya.Region(self.top.shapes(self.ly.layer(41, 0)))
        li = self.ly.layer(9, 0)
        self.top.shapes(li).clear()
        self.top.shapes(li).insert(dfpad.sized(-int(PAD_PASS_ENCL * 1000)).snapped(5, 5))

    def shield(self):
        """Solid Metal1 on core vss, dfpad grown by SHIELD_OVER and not a rectangle, whose corners would cross dfpad's diagonal edges."""
        dfpad = pya.Region(self.top.begin_shapes_rec(self.ly.layer(41, 0)))
        shield = dfpad.sized(int(SHIELD_OVER * 1000)) if SHIELD_OVER else dfpad.dup()
        # Sizing moves the 45 degree edges off the 5 nm grid.
        shield = shield.snapped(5, 5)
        shield &= pya.Region(pya.Box(0, 0, int(RF_W * 1000), int(RF_H * 1000)))
        self.top.shapes(self.lay('Metal1')).insert(shield)

    def nofill(self):
        """NoMetFiller over the pad and the line. No front-end keep-out, the shield leaves nothing for Activ fill to couple to."""
        self.box('NoMetFiller', 0.0, 0.0, RF_W, IO_Y0 + NOFILL_HALO)
        self.box('NoMetFiller', TRACE_X - TRACE_W / 2.0 - NOFILL_HALO, IO_Y0,
                 TRACE_X + TRACE_W / 2.0 + NOFILL_HALO, RF_H)

    def esd(self):
        """The diode pair, diodevdd mirrored about TRACE_X so that both pad tabs land under the trace."""
        self.diodes = {}
        gap_c = (ESD_GAP[0] + ESD_GAP[1]) / 2.0
        y = gap_c - ESD_PAD_FINGER
        for model, mirror in zip(ESD_MODELS, (False, True)):
            var = self._variant('esd', {'model': model})
            if mirror:
                t = pya.DTrans(pya.DTrans.M90, pya.DVector(TRACE_X + ESD_PAD_TAB_X, y))
            else:
                t = pya.DTrans(pya.DVector(TRACE_X - ESD_PAD_TAB_X, y))
            self.top.insert(pya.DCellInstArray(var, t))
            body = pya.DBox(0.0, 0.0, 9.72, 37.05).transformed(t)
            self.diodes[model] = {'body': body, 'bbox': self.ly.cell(var).dbbox().transformed(t)}

    def strip_device_labels(self):
        """Drop the ESD PCells' pin shapes and labels: they name device terminals, not this cell's nets."""
        for ld in ((8, 2), (10, 2), (63, 0)):
            self.top.shapes(self.ly.layer(*ld)).clear()

    def io_rails(self):
        """The library's rail bands shifted by +70, with the corridor cut around the widest pad-net top metal near each piece of an IO band."""
        g = TM2_RAIL_GAP
        bands = rails(IO_LEF, IO_CELL)
        # No break below the ESD bar: a step inside the last iovss band would leave a sliver under TM2.a.
        breaks = (self.tear_top + g, self.tap_top + g, self.top_bar.top + g)
        holes = pya.Region()
        for h in self.m3_holes:
            holes.insert(h.to_itype(self.ly.dbu))
        for net in ('iovss', 'iovdd', 'vss', 'vdd'):
            for layer, y0, y1 in bands[net]:
                # TopMetal1 on the core bands stays whole under the narrow line, the corridor is for the IO bands.
                cut = net in ('iovss', 'iovdd') and layer in CORRIDOR_LAYERS
                y0 += IO_Y0
                y1 += IO_Y0
                if not cut:
                    band = pya.Region(pya.DBox(0.0, y0, RF_W, y1).to_itype(self.ly.dbu))
                    if layer == 'Metal3':
                        band -= holes
                    self.top.shapes(self.lay(layer)).insert(band)
                    continue
                cuts = [y0] + sorted(b for b in breaks if y0 < b < y1) + [y1]
                for s0, s1 in zip(cuts, cuts[1:]):
                    half = self._pad_half(s0 - g, s1 + g) + g
                    self.box(layer, 0.0, s0, TRACE_X - half, s1)
                    self.box(layer, TRACE_X + half, s0, RF_W, s1)

    def _pad_half(self, y0, y1):
        """Widest half width of the pad-net top metal anywhere in [y0, y1]."""
        half = self._trace_half(y0)
        bar = self.top_bar
        if y0 < bar.top and y1 > bar.bottom:
            half = max(half, TRACE_X - bar.left, bar.right - TRACE_X)
        return half

    def _trace_half(self, y):
        """Half width of the teardrop and trace at y. Non-increasing in y, so its value at the bottom of an interval is the maximum."""
        if y < self.tear_top - TEAR_R:
            return TEAR_W / 2.0
        if y < self.tear_top:
            return TRACE_W / 2.0 + (self.tear_top - y)
        if y < self.tap_top:
            return TRACE_W / 2.0
        return TRACE_W_OUT / 2.0

    def rf_trace(self):
        """TopMetal2 from the pad to the cell's inner edge: teardrop, TRACE_W up to the ESD tap, TRACE_W_OUT from there on."""
        c, hw, ht = TRACE_X, TEAR_W / 2.0, TRACE_W / 2.0
        y_flank = self.pad_top + PAD_FR
        tear = pya.DPolygon([
            pya.DPoint(c - hw, PAD_CY), pya.DPoint(c + hw, PAD_CY),
            pya.DPoint(c + hw, y_flank), pya.DPoint(c + ht, self.tear_top),
            pya.DPoint(c - ht, self.tear_top), pya.DPoint(c - hw, y_flank)])
        r = pya.Region(tear.to_itype(self.ly.dbu))
        r += pya.Region(pya.DBox(c - ht, PAD_CY, c + ht, self.tap_top).to_itype(self.ly.dbu))
        r += pya.Region(pya.DBox(c - TRACE_W_OUT / 2.0, self.tap_top - 1.0,
                                 c + TRACE_W_OUT / 2.0, RF_H).to_itype(self.ly.dbu))
        self.top.shapes(self.lay('TopMetal2')).insert(r.merged())

    def _cut(self, name, cx, cy):
        a = VIA[name] / 2.0
        self.box(name, cx - a, cy - a, cx + a, cy + a)

    def _raw(self, layer, within):
        """Raw polygons on ``layer`` inside ``within``. Not a Region, which would merge the two overlapping pad combs into one terminal."""
        ib = within.to_itype(self.ly.dbu)
        out = []
        for sh in self.top.shapes(self.lay(layer)).each():
            if sh.is_box() or sh.is_polygon():
                p = sh.polygon
                if p.bbox().inside(ib):
                    out.append(p)
        return out

    def wire_diodes(self):
        """Pad up to the trace in the gap, every other terminal onto a core rail.

        Runs after the flatten, so terminals are measured off the PCell's own metal, and before ``io_rails``, which cuts the islands recorded here out of the vss band.
        """
        dbu = self.ly.dbu
        R = lambda b: pya.Region(b.to_itype(dbu))  # noqa: E731
        self.m2_cutouts = []
        self.m3_holes = []
        self.esd_via_counts = {}
        g0, g1 = ESD_GAP
        bands = rails(IO_LEF, IO_CELL)
        vss_m3 = [pya.DBox(0.0, b[1] + IO_Y0, RF_W, b[2] + IO_Y0) for b in bands['vss'] if b[0] == 'Metal3'][0]
        vdd_m4 = [pya.DBox(0.0, b[1] + IO_Y0, RF_W, b[2] + IO_Y0) for b in bands['vdd'] if b[0] == 'Metal4'][0]
        if abs(vss_m3.bottom - g1) > 1e-6 or abs(vdd_m4.bottom - g1) > 1e-6:
            raise AssertionError("ESD_GAP does not end where vss Metal3 and vdd Metal4 start")
        centre = pya.DPoint(TRACE_X, (g0 + g1) / 2.0).to_itype(dbu)

        # The pad terminal, shared: both tabs and their gap fingers.
        pad_m2 = pya.Region()
        for d in self.diodes.values():
            for p in self._raw('Metal2', d['bbox']):
                if p.bbox().contains(centre):
                    pad_m2.insert(p)
        if pad_m2.is_empty():
            raise AssertionError("no pad comb under the trace in the gap")
        pad_m2.merge()
        m_lo, m_hi = g0 + ESD_KEEP, g1 - ESD_KEEP
        pb = (pad_m2 & R(pya.DBox(0.0, m_lo, RF_W, m_hi))).bbox().to_dtype(dbu)
        bar = pya.DBox(pb.left, m_lo, pb.right, m_hi)
        for lay in ('Metal3', 'Metal4', 'Metal5'):
            self.box(lay, bar.left, bar.bottom, bar.right, bar.top)
        # TopMetal1 encloses the Metal5 bar by TV1.d less TV1.c and keeps TM1.b from the core band above. TopMetal2 is the same box.
        e = ESD_ENC['TopVia1'] - TV1_M5_ENC
        self.top_bar = pya.DBox(bar.left - e, bar.bottom - e, bar.right + e, g1 - TM1_B)
        t = self.top_bar
        for lay in ('TopMetal1', 'TopMetal2'):
            self.box(lay, t.left, t.bottom, t.right, t.top)
        self.esd_via_counts['pad'] = {
            'Via2': self._fill_vias('Via2', pad_m2 & R(bar)),
            'Via3': self._fill_vias('Via3', R(bar)),
            'Via4': self._fill_vias('Via4', R(bar)),
            'TopVia1': self._fill_vias('TopVia1', R(t)),
            'TopVia2': self._fill_vias('TopVia2', R(t)),
        }

        # Per device: the comb, and the ring, told apart by its bbox because the PCell draws it as one keyhole contour.
        parts = {}
        for model in ESD_MODELS:
            d = self.diodes[model]
            body = d['body']
            combs = [p for p in self._raw('Metal2', d['bbox']) if not p.bbox().contains(centre)]
            if len(combs) != 1:
                raise AssertionError("%s: %d rail combs, want 1" % (model, len(combs)))
            rings = [p for p in self._raw('Metal1', body.enlarged(0.001, 0.001)) if p.bbox() == body.to_itype(dbu)]
            if len(rings) != 1:
                raise AssertionError("%s: %d outer rings, want 1" % (model, len(rings)))
            comb = pya.Region(combs[0])
            cb = comb.bbox().to_dtype(dbu)
            plate = pya.DBox(body.left, cb.top + ESD_KEEP, body.right, body.top)
            if not (vss_m3.bottom < plate.bottom and plate.top < vdd_m4.top):
                raise AssertionError("%s: ring plate %s is not under both vss Metal3 and vdd Metal4" % (model, plate))
            self.box('Metal2', plate.left, plate.bottom, plate.right, plate.top)
            self.m2_cutouts.append(plate)
            parts[model] = (comb, pya.Region(rings[0]), plate)

        # The two vdd connections come up through Metal3 islands in the vss band.
        up = {}
        cvdd = parts['diodevdd_2kv'][0]
        up['diodevdd_2kv'] = (cvdd & R(vss_m3)).bbox().to_dtype(dbu)
        up['diodevss_2kv'] = parts['diodevss_2kv'][2]
        holes = pya.Region()
        for isl in up.values():
            self.box('Metal3', isl.left, isl.bottom, isl.right, isl.top)
            hole = isl.enlarged(ESD_KEEP, ESD_KEEP) & vss_m3
            self.m3_holes.append(hole)
            holes.insert(hole.to_itype(dbu))
        vss_ok = R(vss_m3) - holes

        for model in ESD_MODELS:
            comb, ring, plate = parts[model]
            n = {'ring Via1': self._fill_vias('Via1', ring & R(plate), enc=0.05)}
            isl = R(up[model])
            if model == 'diodevss_2kv':      # comb to vss, ring to vdd
                n['comb Via2'] = self._fill_vias('Via2', comb & vss_ok)
                n['ring Via2'] = self._fill_vias('Via2', R(plate) & isl)
                n['ring Via3'] = self._fill_vias('Via3', isl & R(vdd_m4))
            else:                            # comb to vdd, ring to vss
                n['comb Via2'] = self._fill_vias('Via2', comb & isl)
                n['comb Via3'] = self._fill_vias('Via3', isl & R(vdd_m4))
                n['ring Via2'] = self._fill_vias('Via2', R(plate) & vss_ok)
            self.esd_via_counts[model] = n

    def _rail(self, layer, y0, y1):
        """The supply rail on ``layer`` in band y0..y1: every piece that reaches a cell edge, which islands and the RF trace never do."""
        dbu = self.ly.dbu
        band = pya.Region(pya.DBox(0.0, y0, RF_W, y1).to_itype(dbu))
        edges = (pya.Region(pya.DBox(0.0, y0, 0.001, y1).to_itype(dbu))
                 + pya.Region(pya.DBox(RF_W - 0.001, y0, RF_W, y1).to_itype(dbu)))
        drawn = pya.Region(self.top.shapes(self.lay(layer))).merged()
        return (drawn & band).interacting(edges)

    def _lattice(self, name, core):
        """Cuts of ``name`` on the TIE_PITCH lattice inside the shrunk Manhattan region ``core``.

        One lattice for the whole cell keeps cuts of neighbouring pieces a pitch apart, and array references keep the GDS small.
        A lattice row on the edge two rectangles share belongs to the upper one.
        """
        p = int(round(TIE_PITCH[name] * 1000))
        off = p // 2
        cname = '%s_%s' % (RF_CELL, name.lower())
        if self.ly.has_cell(cname):
            cell = self.ly.cell(cname)
        else:
            cell = self.ly.create_cell(cname)
            h = int(round(VIA[name] * 500))
            cell.shapes(self.lay(name)).insert(pya.Box(-h, -h, h, h))
        boxes = [t.bbox() for t in core.decompose_trapezoids_to_region().each()]
        starts = {(bx.bottom, bx.left, bx.right) for bx in boxes}
        n = 0
        for bx in boxes:
            kx0 = -((off - bx.left) // p)
            ky0 = -((off - bx.bottom) // p)
            kx1 = (bx.right - off) // p
            ky1 = (bx.top - off) // p
            if ky1 * p + off == bx.top and any(
                    y == bx.top and l < bx.right and r > bx.left
                    for y, l, r in starts):
                ky1 -= 1
            nx, ny = kx1 - kx0 + 1, ky1 - ky0 + 1
            if nx <= 0 or ny <= 0:
                continue
            self.top.insert(pya.CellInstArray(
                cell.cell_index(), pya.Trans(kx0 * p + off, ky0 * p + off),
                pya.Vector(p, 0), pya.Vector(0, p), nx, ny))
            n += nx * ny
        return n

    def tie_rails(self):
        """Stitch each iovss and iovdd band's Metal3 to TopMetal2 into one conductor, which the IO library leaves to the ring."""
        um = lambda v: int(round(v * 1000))  # noqa: E731
        bands = rails(IO_LEF, IO_CELL)
        # lower metal, upper metal, cut, enclosure in each, floor
        stack = (('Metal3', 'Metal4', 'Via3', 0.06, 0.06, 1000), ('Metal4', 'Metal5', 'Via4', 0.06, 0.06, 1000),
                 ('Metal5', 'TopMetal1', 'TopVia1', TV1_M5_ENC, ESD_ENC['TopVia1'], 100),
                 ('TopMetal1', 'TopMetal2', 'TopVia2', ESD_ENC['TopVia2'], ESD_ENC['TopVia2'], 20))
        for net in ('iovss', 'iovdd'):
            for layer, y0, y1 in bands[net]:
                if layer != 'Metal3':
                    continue
                y0 += IO_Y0
                y1 += IO_Y0
                for lo, hi, cut, enc_lo, enc_hi, floor in stack:
                    core = (self._rail(lo, y0, y1).sized(-um(VIA[cut] / 2 + enc_lo))
                            & self._rail(hi, y0, y1).sized(-um(VIA[cut] / 2 + enc_hi)))
                    n = self._lattice(cut, core)
                    # The third iovss band is 8 um tall, less room than the others.
                    if n < (floor / 4 if y1 - y0 < 10.0 else floor):
                        raise AssertionError("%s %.1f: only %d %s tie the band" % (net, y0, n, cut))

    def check_esd_vias(self):
        """Every ESD terminal keeps a via array. Per terminal, because a sum hid a rail side with no Via1 at all."""
        for name, counts in self.esd_via_counts.items():
            for key, got in counts.items():
                floor = ESD_VIA_FLOOR[key.split()[-1]]
                if got < floor:
                    raise AssertionError("%s %s: %d cuts on the ESD path, floor is %d" % (name, key, got, floor))

    def _esd_keepout(self):
        keep = pya.Region()
        for bb in [d['bbox'] for d in self.diodes.values()] + self.m2_cutouts:
            keep.insert(bb.enlarged(M2_KEEPOUT, M2_KEEPOUT).to_itype(self.ly.dbu))
        return keep

    def supply_strips(self):
        """Metal2 under every Metal3 supply band of the IO row with Via2 between them, less the ESD pair and the clamp's Metal2 of every other net."""
        dbu = self.ly.dbu
        keep_esd = self._esd_keepout()
        ko = int(round(M2_KEEPOUT / dbu))
        sliver = int(round(STRIP_MIN / 2.0 / dbu))
        enc = int(round((VIA['Via2'] / 2 + ESD_ENC['Via2']) * 1000))
        bands = rails(IO_LEF, IO_CELL)
        for net in ('iovss', 'iovdd', 'vss', 'vdd'):
            for layer, y0, y1 in bands[net]:
                if layer != 'Metal3':
                    continue
                y0 += IO_Y0
                y1 += IO_Y0
                other = pya.Region()
                for n, r in self.clamp.m2.items():
                    if n != net:
                        other += r
                keep = keep_esd + other.merged().sized(ko)
                strip = (pya.Region(pya.DBox(STRIP_INSET, y0, RF_W - STRIP_INSET, y1).to_itype(dbu)) - keep).merged()
                strip = strip.sized(-sliver).sized(sliver) & strip
                if strip.is_empty():    # iovss band 3, the clamp owns its Metal2
                    continue
                self.top.shapes(self.lay('Metal2')).insert(strip)
                n = self._lattice('Via2', (strip & self._rail('Metal3', y0, y1)).sized(-enc))
                if n < STRIP_VIA2_FLOOR:
                    raise AssertionError("%s strip at y %.1f: %d Via2" % (net, y0, n))

    def shield_straps(self):
        """Metal1 from the shield to the vss lanes, a wider path than the collar's own overlap with them. Metal2 over the pad would add a layer between the pad and the shield, and capacitance with it."""
        dbu = self.ly.dbu
        straps = pya.Region()
        for x0, x1 in STRAP_X:
            straps.insert(pya.DBox(x0, STRAP_Y[0], x1, STRAP_Y[1]).to_itype(dbu))
        self.top.shapes(self.lay('Metal1')).insert(straps.merged())
        lanes = pya.Region()
        for x0, x1 in (LANE_M1, (RF_W - LANE_M1[1], RF_W - LANE_M1[0])):
            lanes.insert(pya.DBox(x0, LANE_Y[0], x1, LANE_Y[1]).to_itype(dbu))
        if (straps & lanes).merged().count() != 2:
            raise AssertionError("shield straps do not both land on a vss lane")

    def _fill_vias(self, name, area, pitch=None, enc=None):
        """Cuts on a grid, kept only where the cut plus its enclosure lies wholly inside ``area``."""
        if pitch is None:
            pitch = ESD_PITCH[name]
        a = VIA[name] / 2.0 + (ESD_ENC[name] if enc is None else enc)
        bb = area.bbox()
        n = 0
        y = bb.bottom * self.ly.dbu + a
        while y < bb.top * self.ly.dbu - a:
            x = bb.left * self.ly.dbu + a
            while x < bb.right * self.ly.dbu - a:
                probe = pya.Region(pya.DBox(x - a, y - a, x + a, y + a).to_itype(self.ly.dbu))
                if (probe - area).is_empty():
                    self._cut(name, x, y)
                    n += 1
                x += pitch
            y += pitch
        return n

    def labels(self):
        """One label per net, on the band this cell ties to.

        ``padbare`` gets no label, the CDL has no such node and LVS would fail on the extra port.
        ``pad`` and ``padbare`` are one conductor and two disjoint LEF pins as on IOPadAnalog, because the global router crashes when two nets share one pin geometry.
        The ``pad`` pin is one square on the plate, the chip's terminal is placed from it.
        """
        bands = rails(IO_LEF, IO_CELL)
        put = [('pad', 'TopMetal2.text', PAD_CX, PAD_CY)]
        # The bands of one supply are separate conductors inside a pad cell, they meet at the chip.
        tied = {'iovss': ('Metal3', 34.5), 'iovdd': ('Metal3', 66.0),
                'vss': ('Metal3', ESD_GAP[1] - IO_Y0),
                'vdd': ('Metal4', ESD_GAP[1] - IO_Y0)}
        for net in ('iovss', 'iovdd', 'vss', 'vdd'):
            layer, y_lib = tied[net]
            b = [x for x in bands[net] if x[0] == layer and abs(x[1] - y_lib) < 0.01][0]
            put.append((net, layer + '.text', 70.0, (b[1] + b[2]) / 2.0 + IO_Y0))
            self.pin_box(layer, 0.0, b[1] + IO_Y0, RF_W, b[2] + IO_Y0)
        for net, layer, x, y in put:
            self.top.shapes(self.lay(layer)).insert(pya.DText(net, pya.DTrans(pya.DVector(x, y))))
        h = PAD_PIN / 2.0
        self.pin_box('TopMetal2', PAD_CX - h, PAD_CY - h, PAD_CX + h, PAD_CY + h)
        self.pin_box('TopMetal2', TRACE_X - TRACE_W_OUT / 2.0, RF_H - 10.0, TRACE_X + TRACE_W_OUT / 2.0, RF_H)

    def build(self):
        self.pad_stack()
        self.shield()
        self.esd()
        self.rf_trace()
        # Flatten first: the wiring measures the PCells' own metal rather than assuming where they put it.
        self.ly.flatten(self.top.cell_index(), -1, True)
        self.pad_opening()
        self.strip_device_labels()
        self.wire_diodes()
        self.clamp = Clamp(self).islands()
        self.io_rails()
        self.tie_rails()
        self.clamp.build()
        c = self.clamp.counts
        if min(c.get('Via1 clamp vss', 0), c.get('Via1 clamp vdd', 0), c.get('Via3 island', 0)) < CLAMP_VIA_FLOOR:
            raise AssertionError("clamp: a supply side is down to %s cuts" % c)
        self.check_esd_vias()
        self.supply_strips()
        self.shield_straps()
        self.labels()
        self.nofill()
        self.box('prBoundary', 0.0, 0.0, RF_W, RF_H)
        return self.ly, self.top


# ---------------------------------------------------------------------------
# Checks that DRC and LVS cannot make
# ---------------------------------------------------------------------------

def check_rfpad_geometry(ly, top):
    """Assert what the cell promises. The numbers are written down here on purpose, so that a changed generator constant fails."""
    rail_gap = 5.0
    spec = {'Metal1': (8, 0), 'Metal3': (30, 0), 'Metal4': (50, 0), 'Metal5': (67, 0),
            'TopMetal1': (126, 0), 'TopMetal2': (134, 0), 'TopVia1': (125, 0), 'TopVia2': (133, 0), 'Via3': (49, 0), 'Via4': (66, 0),
            'Passiv': (9, 0), 'dfpad': (41, 0), 'NoMetFiller': (160, 0),
            'Activ_nofill': (1, 23), 'GatPoly_nofill': (5, 23)}

    def region(name):
        return pya.Region(top.shapes(ly.layer(*spec[name])))

    bb = top.dbbox()
    assert abs(bb.width() - 80.0) < 0.001, bb.to_s()
    assert abs(bb.height() - 250.0) < 0.001, bb.to_s()
    assert abs(bb.left) < 0.001 and abs(bb.bottom) < 0.001, bb.to_s()

    # The pad stack: the TopMetal2 plate over the PCell's rings, every TopVia2 meeting Pad.gR and off the Passiv opening (Pad.kR).
    tm1 = region('TopMetal1')
    tm2 = region('TopMetal2')
    pad = pya.Region(pya.Box(5000, 0, 75000, 70000)) & tm2
    assert abs(pad.area() * 1e-6 - 4060.20) < 0.5, pad.area() * 1e-6
    for name in ('Metal3', 'Metal4', 'Metal5', 'TopMetal1'):
        ring = pya.Region(pya.Box(0, 0, 80000, 70000)) & region(name)
        assert abs(ring.area() * 1e-6 - 889.85) < 0.5, (name, ring.area() * 1e-6)
    assert region('Via3').count() >= 488
    assert region('Via4').count() >= 488
    assert region('dfpad').count() == 1
    dfpad = region('dfpad')
    pad_tv2 = region('TopVia2').inside(dfpad)
    assert pad_tv2.count() >= 96, pad_tv2.count()
    gr = (tm1 & dfpad).enclosing_check(pad_tv2, 1400, False, pya.Metrics.Euclidian)
    assert gr.is_empty(), "Pad.gR: %d" % gr.count()
    assert pad_tv2.overlapping(region('Passiv')).is_empty(), "Pad.kR"

    # The shield: one solid polygon that covers dfpad with a collar and merges with the straps to vss.
    shield = region('Metal1')
    under = (pya.Region(pya.Box(0, 0, 80000, 75000)) & shield).merged()
    assert under.count() == 1, under.count()
    poly = list(under.each())[0]
    assert poly.holes() == 0, poly.holes()
    assert (dfpad - under).is_empty(), "shield does not cover the pad"
    # 2.99 um and not 3: the drawn collar is snapped to the 5 nm grid on its diagonal edges.
    collar = dfpad.sized(2990) & pya.Region(pya.Box(0, 0, 80000, 75000))
    assert (collar - under).is_empty(), "shield collar is under 3 um"

    # Metal fill stays off the pad, front-end fill is allowed.
    r = region('NoMetFiller')
    assert not r.is_empty()
    assert (pya.Region(pya.Box(5000, 0, 75000, 70000)) - r).is_empty()
    for marker in ('Activ_nofill', 'GatPoly_nofill'):
        assert region(marker).is_empty(), "%s is drawn" % marker

    # Every iovss and iovdd band is solid on Metal3, Metal4 and Metal5.
    bands = rails(IO_LEF, IO_CELL)
    for net in ('iovss', 'iovdd'):
        for layer, y0, y1 in bands[net]:
            if layer not in ('Metal3', 'Metal4', 'Metal5'):
                continue
            strip = pya.Region(pya.Box(0, int((y0 + 70.0) * 1000), 80000, int((y1 + 70.0) * 1000)))
            got = strip & region(layer)
            assert abs(got.area() - strip.area()) < 1000, "%s %s %.1f..%.1f not solid" % (net, layer, y0, y1)

    edge = pya.Region(pya.Box(-1, 0, 1, 250000)) + pya.Region(pya.Box(79999, 0, 80001, 250000))
    for net in ('iovss', 'iovdd'):
        for layer, y0, y1 in bands[net]:
            if layer != 'TopMetal2':
                continue
            strip = pya.Region(pya.Box(0, int((y0 + 70.0) * 1000), 80000, int((y1 + 70.0) * 1000)))
            got = (strip & tm2).merged()
            missing = strip - got
            # TopMetal1 is cut exactly where TopMetal2 is.
            tm1_gap = strip - (strip & tm1).merged()
            tm2_gap = strip - (strip & tm2).merged().interacting(edge)
            assert (tm1_gap ^ tm2_gap).is_empty(), "%s %.1f: TopMetal1 is not cut where TopMetal2 is" % (net, y0)
            assert missing.count() == 2, "%s %.1f: %d gaps" % (net, y0, missing.count())
            rail = got.interacting(edge)
            trace = got - rail
            assert rail.count() == 2 and trace.count() == 1, "%s %.1f: %d rail pieces, %d trace" % (net, y0, rail.count(), trace.count())
            # The rail gap, and no more.
            gap = int(round(rail_gap * 1000))
            assert rail.separation_check(trace, gap, False, pya.Metrics.Projection).is_empty(), \
                "%s TopMetal2 %.1f..%.1f under %.2f of the RF line" % (net, y0, y1, rail_gap)
            # The last iovss band clears the ESD bar above it, so it sits further from the line.
            if (net, y0) != ('iovss', max(b[1] for b in bands['iovss'] if b[0] == 'TopMetal2')):
                assert not rail.separation_check(trace, gap + 10, False, pya.Metrics.Projection).is_empty(), \
                    "%s TopMetal2 %.1f..%.1f cut wider than %.2f" % (net, y0, y1, rail_gap)

    # The RF line reaches the cell's inner edge unbroken.
    trace = pya.Region(pya.Box(int((40.0 - 1.0) * 1000), 60000, int((40.0 + 1.0) * 1000), 250000)) & tm2
    merged = trace.merged()
    assert merged.count() == 1, "RF trace is in %d pieces" % merged.count()
    assert merged.bbox().top == 250000, merged.bbox().to_s()

    # Past the ESD tap it is TM2.a, before it the teardrop and the strike width.
    out = pya.Region(pya.Box(38000, 210000, 42000, 250000)) & tm2
    assert abs(out.area() * 1e-6 - 2.0 * 40.0) < 0.01, out.area() * 1e-6
    for y, x0, want in ((71.0, 30.0, 14.92), (76.9, 30.0, 14.92), (90.0, 33.0, 4.92), (200.0, 33.0, 4.92)):
        cut = pya.Region(pya.Box(int(x0 * 1000), int(y * 1000), int((80.0 - x0) * 1000), int(y * 1000) + 10)) & tm2
        w = cut.bbox().width() * 0.001
        assert abs(w - want) < 0.002, "trace %.3f wide at y %.1f, want %.2f" % (w, y, want)

    # Two ESD devices: diodevss's emitter outside NWell (x > 40), diodevdd's inside it (x < 40).
    recog = pya.Region(top.shapes(ly.layer(99, 30)))
    assert recog.count() == 2, "want 2 ESD devices, got %d" % recog.count()
    for p in recog.each():
        assert abs(p.area() * 1e-6 - 360.126) < 0.01, p.area() * 1e-6
    activ = pya.Region(top.shapes(ly.layer(1, 0)))
    nwell = pya.Region(top.shapes(ly.layer(31, 0)))
    for p in recog.each():
        b = p.bbox()
        cx, cy = b.center().x, b.center().y
        emitter = activ & pya.Region(pya.Box(cx - 300, cy - 5000, cx + 300, cy + 5000))
        assert not emitter.is_empty(), "no emitter at x %.2f" % (cx * 0.001)
        if cx > 40000:
            assert (emitter & nwell).is_empty(), "diodevss emitter in NWell"
        else:
            assert (emitter & nwell).area() == emitter.area(), "diodevdd emitter not in NWell"

    # The pad pin is one centred rectangle on the plate.
    pins = pya.Region(top.shapes(ly.layer(134, 2))) & pya.Region(pya.Box(0, 0, 80000, 75000))
    assert pins.count() == 1, "pad pin is %d shapes, want 1" % pins.count()
    b = pins.bbox()
    assert pins.area() == b.area() and b.center() == pya.Point(40000, 35000) and b.width() >= 45000, \
        "pad pin %s is not a centred square" % b


def check_rfpad_nets(ly, top):
    """Probe the connectivity.

    LVS compares devices, and the rails, the shield and the rings are none, so a pad shorted to a rail or a floating shield passes it.
    DRC reads two touching shapes of different nets as one polygon.
    """
    spec = {'m1': (8, 0), 'm2': (10, 0), 'm3': (30, 0), 'm4': (50, 0), 'm5': (67, 0),
            'tm1': (126, 0), 'tm2': (134, 0), 'v1': (19, 0), 'v2': (29, 0), 'v3': (49, 0), 'v4': (66, 0), 'tv1': (125, 0), 'tv2': (133, 0)}
    l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
    L = {n: l2n.make_layer(ly.layer(l, d), n) for n, (l, d) in spec.items()}
    for a in ('m1', 'm2', 'm3', 'm4', 'm5', 'tm1', 'tm2'):
        l2n.connect(L[a])
    for lo, via, hi in (('m1', 'v1', 'm2'), ('m2', 'v2', 'm3'), ('m3', 'v3', 'm4'), ('m4', 'v4', 'm5'), ('m5', 'tv1', 'tm1'), ('tm1', 'tv2', 'tm2')):
        l2n.connect(L[lo], L[via])
        l2n.connect(L[via], L[hi])
    l2n.extract_netlist()

    bands = rails(IO_LEF, IO_CELL)
    bad = []

    def net_at(layer, x, y):
        return l2n.probe_net(L[layer], pya.DPoint(x, y))

    def nid(layer, x, y):
        n = net_at(layer, x, y)
        return None if n is None else n.cluster_id

    def shapes(net, layer):
        r = l2n.shapes_of_net(net, L[layer], True)
        return r if r is not None else pya.Region()

    pad = net_at('tm2', 40.0, 35.0)
    if pad is None:
        raise AssertionError("no net under the pad")

    # The pad net is the whole pad stack and the output.
    for layer, want, what in (('m3', 889.85, 'Metal3 ring'), ('m4', 889.85, 'Metal4 ring'), ('m5', 889.85, 'Metal5 ring'), ('tm1', 889.85, 'TopMetal1 ring')):
        inpad = (shapes(pad, layer) & pya.Region(pya.DBox(0, 0, 80, 75).to_itype(ly.dbu))).area() * 1e-6
        if abs(inpad - want) > 0.5:
            bad.append("%s is %.2f um2 on the pad net, want %.2f" % (what, inpad, want))
    trace = shapes(pad, 'tm2') & pya.Region(pya.DBox(38.0, 200.0, 42.0, 250.0).to_itype(ly.dbu))
    if trace.is_empty() or trace.bbox().top != 250000:
        bad.append("the output does not reach the cell's inner edge on the pad net")

    # Both diodes' emitter strips are on it.
    if len(list(shapes(pad, 'm1').merged().each())) < 2:
        bad.append("fewer than two ESD emitters on the pad net")

    # The pad touches no supply: every rail runs edge to edge, and nothing on the pad net reaches a cell edge.
    for layer in ('m1', 'm2', 'm3', 'm4', 'm5', 'tm1', 'tm2'):
        for p in shapes(pad, layer).each():
            b = p.bbox()
            if b.left <= 0 or b.right >= 80000:
                bad.append("the pad net reaches the cell edge on %s at y %.1f..%.1f: it is shorted to a rail" % (layer, b.bottom * 0.001, b.top * 0.001))
                break

    # The shield reaches core vss.
    shield = net_at('m1', 40.0, 6.0)
    vss_m3 = [b for b in bands['vss'] if b[0] == 'Metal3'][0]
    vss = net_at('m3', 70.0, (vss_m3[1] + vss_m3[2]) / 2.0 + 70.0)
    if shield is None:
        bad.append("no net under the shield")
    elif vss is None or shield.cluster_id != vss.cluster_id:
        bad.append("the Metal1 shield does not reach the core vss rail")
    elif shield.cluster_id == pad.cluster_id:
        bad.append("the shield is shorted to the pad")

    # The ESD pair is on the core rails: each reaches one comb and one ring (37.05 um tall), the IO rails reach none.
    rails_at = {'vss': ('m3', 70.0, 219.0), 'vdd': ('m4', 70.0, 218.0),
                'iovss': ('m3', 70.0, 200.0), 'iovdd': ('m3', 70.0, 176.0)}
    nets = {}
    for name, (layer, x, y) in rails_at.items():
        rail = net_at(layer, x, y)
        if rail is None:
            bad.append("no net on the %s band" % name)
            continue
        nets[name] = rail.cluster_id
        if rail.cluster_id == pad.cluster_id:
            bad.append("%s is shorted to the pad" % name)
        rings = [p for p in shapes(rail, 'm1').merged().each() if 37000 <= p.bbox().height() <= 37100]
        combs = [p for p in shapes(rail, 'm2').merged().each() if 28000 < p.bbox().left < 52000 and p.bbox().height() > 29000]
        want = 1 if name in ('vss', 'vdd') else 0
        if len(rings) != want or (len(combs) > 0) != bool(want):
            bad.append("the %s band reaches %d ESD rings and %d combs, want %d of each" % (name, len(rings), len(combs), want))
    if len(set(nets.values())) != len(nets):
        bad.append("two of vss, vdd, iovss, iovdd are one net: %s" % nets)

    # Every iovss and iovdd band is one conductor from Metal3 to TopMetal2, at both cell edges.
    for name in ('iovss', 'iovdd'):
        for layer, y0, y1 in bands[name]:
            if layer != 'Metal3':
                continue
            yc = (y0 + y1) / 2.0 + 70.0
            ids = set()
            for lay in ('m3', 'm4', 'm5', 'tm1', 'tm2'):
                for x in (1.0, 79.0):
                    ids.add(nid(lay, x, yc))
            if len(ids) != 1 or None in ids:
                bad.append("%s band at y %.1f is %d nets across Metal3 to TopMetal2, want 1" % (name, yc, len(ids)))

    # The clamp: stripes, lanes and rings on their rails, both gate buses and the inverter output one net, the RC node its own.
    s_vss, s_vdd = CL_STRIPES[0], CL_STRIPES[1]
    yc = (CL_Y0 + GATE_LINE[1] + 60.0) / 2.0 + 20.0
    gate = nid('m2', 40.0, sum(GATE_LINE) / 2.0)
    rc = nid('m2', 40.0, sum(RES_LINE) / 2.0)
    want = {
        'left vss stripe': (('m2', sum(s_vss[:2]) / 2.0, yc), nets.get('vss')),
        'right vss stripe': (('m2', 80.0 - sum(s_vss[:2]) / 2.0, yc), nets.get('vss')),
        'left vdd stripe': (('m2', sum(s_vdd[:2]) / 2.0, yc), nets.get('vdd')),
        'right vdd stripe': (('m2', 80.0 - sum(s_vdd[:2]) / 2.0, yc), nets.get('vdd')),
        'left vss lane': (('m2', sum(LANE_M2) / 2.0, yc), nets.get('vss')),
        'right vss lane': (('m2', 80.0 - sum(LANE_M2) / 2.0, yc), nets.get('vss')),
        'left clamp ring': (('m1', CL_COLS[1][1] + 1.4, yc), nets.get('vss')),
        'right clamp ring': (('m1', 80.0 - CL_COLS[1][1] - 1.4, yc), nets.get('vss')),
        'left gate bus': (('m2', CL_GATE_X, yc), gate),
        'right gate bus': (('m2', 80.0 - CL_GATE_X, yc), gate),
        'inverter output': (('m2', sum(OUT_STRIPE) / 2.0, 100.0), gate),
        'inverter gate bus': (('m2', INV_GATE_X, 110.0), rc),
    }
    for what, ((layer, x, y), net) in want.items():
        got = nid(layer, x, y)
        if got is None or got != net:
            bad.append("the %s at (%.1f, %.1f) is not on its net" % (what, x, y))
    if gate is None or rc is None or len({gate, rc} | set(nets.values())) != len(nets) + 2:
        bad.append("the clamp gate or its RC node is missing or shorted to a rail")

    # Every Metal2 piece under an IO band is on that band's net or the clamp's, so no strip floats.
    known = set(nets.values()) | {gate, rc, pad.cluster_id}
    for name in ('iovss', 'iovdd'):
        for layer, y0, y1 in bands[name]:
            if layer != 'Metal3':
                continue
            band = pya.Region(pya.DBox(0, y0 + 70.0, 80, y1 + 70.0).to_itype(ly.dbu))
            m2 = pya.Region(top.begin_shapes_rec(ly.layer(10, 0))).merged() & band
            this = nid('m3', 1.0, (y0 + y1) / 2.0 + 70.0)
            own = 0
            for poly in m2.each():
                c = next(pya.Region(poly).decompose_trapezoids_to_region().each()).bbox().center()
                n = nid('m2', c.x * ly.dbu, c.y * ly.dbu)
                if n == this:
                    own += 1
                elif n not in known:
                    bad.append("a Metal2 piece at %s under the %s band is on no known net" % (poly.bbox().to_dtype(ly.dbu), name))
            if own == 0 and (name, y0) != ('iovss', 126.0):
                bad.append("the %s band at y %.1f has no Metal2 strip" % (name, y0 + 70.0))

    if bad:
        raise AssertionError("RF pad connectivity:\n  " + "\n  ".join(bad))


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def _lef_inscribed(tz):
    """The widest axis-aligned box inside one horizontal trapezoid, snapped inward to the manufacturing grid."""
    b = tz.bbox()
    spans = []
    for y in (b.bottom, b.top):
        xs = [x for e in tz.each_edge() if e.y1 == e.y2 == y for x in (e.x1, e.x2)]
        if not xs:
            return None
        spans.append((min(xs), max(xs)))
    left = max(spans[0][0], spans[1][0])
    right = min(spans[0][1], spans[1][1])
    left = -((-left) // LEF_GRID) * LEF_GRID
    right = (right // LEF_GRID) * LEF_GRID
    if right <= left or b.top <= b.bottom:
        return None
    return pya.Box(left, b.bottom, right, b.top)


def _lef_rects(region, inside=True):
    """Non-overlapping rectangles of ``region``. Slanted edges round inward for a pin, which must not claim missing metal, and outward for an obstruction."""
    out = []
    for poly in region.merged().each():
        for tz in poly.decompose_trapezoids(pya.Polygon.TD_htrapezoids):
            b = tz.bbox()
            if tz.area() == b.area() or not inside:
                out.append(b)
                continue
            y = b.bottom
            while y < b.top:
                y2 = min(y + LEF_SLANT_STEP, b.top)
                band = pya.Region(tz) & pya.Region(pya.Box(b.left, y, b.right, y2))
                for sub in band.merged().each():
                    for part in sub.decompose_trapezoids(pya.Polygon.TD_htrapezoids):
                        ib = _lef_inscribed(part)
                        if ib is not None:
                            out.append(ib)
                y = y2
    return out


def write_rfpad_lef(ly, top, output):
    """Write the LEF abstract: pins from datatype 2 around their datatype 25 labels, all other metal as OBS."""
    dbu = ly.dbu

    def rect(b, ind):
        return "%sRECT %.3f %.3f %.3f %.3f ;\n" % (ind, b.left * dbu, b.bottom * dbu, b.right * dbu, b.top * dbu)

    def pin_shapes(layer):
        return [s.polygon for s in top.shapes(ly.layer(layer, 2)).each() if s.is_box() or s.is_polygon() or s.is_path()]

    pin_map = {m: {} for m in LEF_METALS}
    for lname, (layer, _) in LEF_METALS.items():
        polys = pin_shapes(layer)
        for s in top.shapes(ly.layer(layer, 25)).each():
            if s.is_text():
                pt = pya.Point(s.text.trans.disp.x, s.text.trans.disp.y)
                for p in polys:
                    if p.inside(pt):
                        pin_map[lname].setdefault(s.text.string, []).append(p)
    box = pya.DBox(*LEF_PADBARE_BOX)
    hits = [p for p in pin_shapes(134) if box.contains(p.bbox().to_dtype(dbu).p1) and box.contains(p.bbox().to_dtype(dbu).p2)]
    if not hits:
        raise AssertionError("no TopMetal2 pin shape for padbare")
    pin_map['TopMetal2'].setdefault('padbare', []).extend(hits)

    bb = None
    for s in top.shapes(ly.layer(*RF_LAYERS['prBoundary'])).each():
        bb = s.bbox()
        break

    lef = ["VERSION 5.8 ;\nBUSBITCHARS \"[]\" ;\nDIVIDERCHAR \"/\" ;\n\n"]
    lef.append("MACRO %s\n  CLASS PAD INOUT ;\n  ORIGIN 0 0 ;\n" % RF_CELL)
    lef.append("  FOREIGN %s 0 0 ;\n" % RF_CELL)
    lef.append("  SIZE %.3f BY %.3f ;\n" % (bb.width() * dbu, bb.height() * dbu))
    # Mirroring in x would put the pad zone on the core side.
    lef.append("  SYMMETRY Y ;\n  SITE %s ;\n" % RF_SITE)

    emitted = {m: pya.Region() for m in LEF_METALS}
    for name in LEF_PINS:
        lef.append("  PIN %s\n    DIRECTION INOUT ;\n" % name)
        if name in LEF_USE:
            lef.append("    USE %s ;\n    SHAPE ABUTMENT ;\n" % LEF_USE[name])
        else:
            lef.append("    USE SIGNAL ;\n")
        lef.append("    PORT\n")
        found = False
        for lname in LEF_METALS:
            shapes = pin_map[lname].get(name)
            if not shapes:
                continue
            found = True
            r = pya.Region()
            for p in shapes:
                r.insert(p)
            emitted[lname] += r
            lef.append("      LAYER %s ;\n" % lname)
            for b in _lef_rects(r):
                lef.append(rect(b, "      "))
        if not found:
            raise AssertionError("LEF pin %s has no geometry" % name)
        lef.append("    END\n  END %s\n" % name)

    lef.append("  OBS\n")
    for lname, spec in LEF_METALS.items():
        obs = pya.Region(top.begin_shapes_rec(ly.layer(*spec))).merged() - emitted[lname]
        if obs.is_empty():
            continue
        # Wide OBS grows by the Mn.e difference, the pins stay reachable and the abstract stays inside the cell.
        wide_half = int(round(WIDE_W / 2 / dbu))
        wide = obs.sized(-wide_half).sized(wide_half) & obs
        if not wide.is_empty():
            obs = (obs + wide.sized(int(round((WIDE_SP - MIN_SP) / dbu)))) - emitted[lname]
        obs &= pya.Region(bb)
        lef.append("    LAYER %s ;\n" % lname)
        for b in _lef_rects(obs, inside=False):
            lef.append(rect(b, "    "))
    lef.append("  END\nEND %s\n\nEND LIBRARY\n" % RF_CELL)

    pathlib.Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        f.write("".join(lef))
    print(f"LEF written to: {output}")


def generate_rfpad(gds_path, lef_path, lib_path):
    """Build the RF pad, check it, and only then write the requested views."""
    ly, top = RfPad().build()
    check_rfpad_geometry(ly, top)
    check_rfpad_nets(ly, top)
    print(f"RF pad checks passed: {RF_CELL}")
    if gds_path:
        write_gds(ly, gds_path)
    if lef_path:
        write_rfpad_lef(ly, top, lef_path)
    if lib_path:
        pathlib.Path(lib_path).parent.mkdir(parents=True, exist_ok=True)
        with open(lib_path, 'w', encoding='utf-8') as f:
            f.write(RF_LIB % {'cell': RF_CELL, 'cap': RF_PAD_CAP_PF})
        print(f"Liberty written to: {lib_path}")


# ---------------------------------------------------------------------------
# CLI entry point, arguments injected by ``klayout -rd key=value``
# ---------------------------------------------------------------------------

rf_outputs = [globals().get(k) for k in ('gds_output', 'lef_output', 'lib_output')]
if not any(rf_outputs):
    print("Missing output argument. Please define at least one of gds_output, lef_output, lib_output.")
    sys.exit(1)
generate_rfpad(*rf_outputs)
