# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Builds the EM layout of the tank coil and its AWS Palace model with gds2palace.
# ============================================
#
# Usage: python3 verification/em/scripts/palace_vco_ind.py, or make sim-em, which also runs Palace and combines the results.
#
# Input:  layout/vco_ind.gds, the coil as drawn.
# Output: verification/em/layout/vco_ind.gds, the coil metals plus the EM ground and the port markers, and the
#         Palace model in verification/em/palace_model/vco_ind_data/.
#
# The EM ground follows the PDK's inductor synthesis example: a Metal1 frame half a coil diameter away from the
# windings and a Metal1 tongue under the feeds. The ports are vertical sheets at the ends of the feed pins, from the
# tongue up to the pin metal: port 1 at LA, port 2 at LB, port 3 at the center tap LC.

import os
import sys

import klayout.db as kdb
from gds2palace import gds_reader, simulation_setup, stackup_reader, utilities

NAME = "vco_ind"
STACKUP = "SG13G2_200um.xml"

# Frequency sweep in Hz. With fstart = 0, gds2palace solves from fstep and adds 10 MHz and 20 MHz for the fit to DC.
FSTART, FSTOP, FSTEP = 0, 60e9, 0.75e9

# Mesh: cell size in um along the conductors, and the order of the FEM basis functions
REFINED_CELLSIZE = 3
ORDER = 2

# Conductor model. "volume" meshes the coil metals as solids with their bulk conductivity, so the skin and proximity
# effects in the 4 um wide, 2 to 3 um thick traces come out of the field solution. "surface" models each metal as a
# hollow shell with a surface impedance. It is cheaper, but it counts the side walls as extra cross-section, which
# for traces about as thick as they are wide puts the resistance too low.
METALS = "volume"
# Cell size in um inside the coil metals in volume mode, near the skin depth of TopMetal2 at 20 GHz (0.65 um).
# 0.5 um changes Q at 20 GHz by 1.6 % for twice the unknowns.
METAL_CELLSIZE = 1

# GDS layers (layer, datatype)
COIL_LAYERS = {"TopMetal1": (126, 0), "TopVia2": (133, 0), "TopMetal2": (134, 0)}
GROUND = (8, 0)
PORTS = [  # port number, pin label, label layer, pin layer, metal the port connects to
    (1, "LA", (126, 25), (126, 2), "TopMetal1"),
    (2, "LB", (126, 25), (126, 2), "TopMetal1"),
    (3, "LC", (134, 25), (134, 2), "TopMetal2"),
]
PORT_DEPTH = 0.1  # um, extent of a port marker along the feed
TONGUE_OVERLAP = 2  # um, how far the tongue reaches under the feed pins


def resolve_stackup(name):
    # The stackups ship with the PDK. Newer PDKs keep them in XML_stackup/legacy, older ones in workflow.
    base = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], "libs.tech", "palace")
    for sub in ("XML_stackup/legacy", "workflow"):
        path = os.path.join(base, sub, name)
        if os.path.isfile(path):
            return path
    sys.exit(f"palace_{NAME}.py: stackup {name} not found in {base}")


def build_em_layout(src, dst):
    ly = kdb.Layout()
    ly.read(src)
    top = ly.top_cell()
    um = kdb.CplxTrans(ly.dbu)

    em = kdb.Layout()
    em.dbu = ly.dbu
    cell = em.create_cell(NAME)
    for layer, datatype in COIL_LAYERS.values():
        region = kdb.Region(top.begin_shapes_rec(ly.layer(layer, datatype)))
        cell.shapes(em.layer(layer, datatype)).insert(region.merged())

    # Coil outline from the TopMetal2 windings: the width is the outer diameter, the top edge is the top of the octagon
    windings = kdb.Region(top.begin_shapes_rec(ly.layer(*COIL_LAYERS["TopMetal2"]))).bbox().to_dtype(ly.dbu)
    d_outer = windings.width()
    x0, y0 = windings.center().x, windings.top - d_outer / 2

    # Port markers at the lower edge of each feed pin, found through the pin label
    pins = kdb.DBox()
    trace_w = None
    for number, label, text_layer, pin_layer, _ in PORTS:
        texts = [s.text.to_dtype(ly.dbu) for s in top.shapes(ly.layer(*text_layer)).each() if s.is_text() and s.text.string == label]
        boxes = [p.bbox() for p in kdb.Region(top.begin_shapes_rec(ly.layer(*pin_layer))).each_merged()]
        hits = [b.to_dtype(ly.dbu) for b in boxes for t in texts if b.to_dtype(ly.dbu).contains(t.trans.disp.to_p())]
        if len(hits) != 1:
            sys.exit(f"palace_{NAME}.py: expected one {pin_layer} pin box under label {label}, found {len(hits)}")
        pin = hits[0]
        pins += pin
        trace_w = trace_w or pin.width()
        cell.shapes(em.layer(200 + number, 0)).insert(kdb.DBox(pin.left, pin.bottom, pin.right, pin.bottom + PORT_DEPTH))

    # Metal1 ground: a frame half a diameter around the coil and a tongue from the frame up under the feed pins
    frame_w = min(20, 5 * trace_w)
    inner = kdb.DBox(x0 - d_outer, y0 - d_outer, x0 + d_outer, y0 + d_outer)
    ground = kdb.Region(um.inverted() * inner.enlarged(frame_w, frame_w)) - kdb.Region(um.inverted() * inner)
    tongue = kdb.DBox(pins.left - trace_w / 2, inner.bottom, pins.right + trace_w / 2, pins.bottom + TONGUE_OVERLAP)
    ground += kdb.Region(um.inverted() * tongue)
    cell.shapes(em.layer(*GROUND)).insert(ground.merged())

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    em.write(dst)
    print(f"palace_{NAME}.py: wrote {dst}, outer diameter {d_outer:.2f} um, center ({x0:.2f}, {y0:.2f}) um")


def build_palace_model(gds_file, palace_dir):
    settings = {
        "unit": 1e-6,
        "margin": 50,
        "fstart": FSTART,
        "fstop": FSTOP,
        "fstep": FSTEP,
        "refined_cellsize": REFINED_CELLSIZE,
        "cells_per_wavelength": 10,
        "meshsize_max": 70,
        "adaptive_mesh_iterations": 0,
        "order": ORDER,
        "no_gui": True,
        "no_preview": True,
        "filled_metals": METALS == "volume",
        # A merged via block (see read_gds below) is 2.5 times the area of its 2 x 2 vias. This scales its
        # conductivity by the share the vias cover, so a via field keeps the PDK's 1.1 Ohm per via.
        "fill_factor_correction": True,
    }
    if METALS == "volume":
        settings["refined_cellsize_override"] = [("TopMetal1", METAL_CELLSIZE), ("TopMetal2", METAL_CELLSIZE)]

    ports = simulation_setup.all_simulation_ports()
    for number, _, _, _, metal in PORTS:
        ports.add_port(simulation_setup.simulation_port(
            portnumber=number, voltage=1, port_Z0=50, source_layernum=200 + number,
            from_layername="Metal1", to_layername=metal, direction="z"))

    stackup = resolve_stackup(STACKUP)
    print(f"palace_{NAME}.py: stackup {stackup}, {METALS} metals")
    materials, dielectrics, metals = stackup_reader.read_substrate(stackup)
    layers = metals.getlayernumbers()
    layers.extend(ports.portlayers)
    # merge_polygon_size joins each TopVia2 array into one block, which keeps the mesh small
    polygons = gds_reader.read_gds(gds_file, layers, purposelist=[0], metals_list=metals, merge_polygon_size=1.5)

    sim_path = utilities.create_sim_path(palace_dir, NAME, dirname="")
    settings.update({
        "simulation_ports": ports,
        "materials_list": materials,
        "dielectrics_list": dielectrics,
        "metals_list": metals,
        "layernumbers": layers,
        "allpolygons": polygons,
        "sim_path": sim_path,
        "model_basename": NAME,
    })
    config, _ = simulation_setup.create_palace(ports.all_active_excitations(), settings)
    print(f"palace_{NAME}.py: wrote {os.path.normpath(config)}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    macro_dir = os.path.normpath(os.path.join(script_dir, "..", "..", ".."))
    em_gds = os.path.join(macro_dir, "verification", "em", "layout", f"{NAME}.gds")
    build_em_layout(os.path.join(macro_dir, "layout", f"{NAME}.gds"), em_gds)
    build_palace_model(em_gds, os.path.join(macro_dir, "verification", "em", "palace_model"))


if __name__ == "__main__":
    main()
# ==============================================================================
