# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

"""Automated bondpad generator for the IHP SG13G2 PDK.

Instantiates the ``bondpad`` PCell from IHP's SG13_dev library, writes the
layout as a GDS file, and optionally produces a LEF macro description for
place-and-route tools (e.g. OpenROAD / LibreLane).

Must be executed inside KLayout's batch mode (``klayout -zz``) because it
relies on the KLayout PCell engine and the SG13_dev library.

Command-line arguments are passed with ``-rd key=value``.

Required arguments:
    diameter     Pad diameter in microns (e.g. 70.0).

Optional arguments:
    shape        Pad geometry: 'octagon' (default), 'square', or 'circle'.
    gds_output   Output path for the GDS file.
    lef_output   Output path for the LEF file.
    bottom_metal Lowest metal layer in the pad stack (1-6, default 1).

At least one of ``gds_output`` or ``lef_output`` must be specified.

Examples (single-line — copy-paste friendly):

    # GDS only (octagon, default metal stack):
    klayout -n sg13g2 -zz -r bondpad.py -rd diameter=70.0 -rd gds_output=gds/bondpad_70x70.gds

    # Both GDS and LEF (square shape):
    klayout -n sg13g2 -zz -r bondpad.py -rd diameter=70.0 -rd shape=square -rd gds_output=gds/bondpad_70x70.gds -rd lef_output=lef/bondpad_70x70.lef

    # LEF only, bottom metal starting at Metal3:
    klayout -n sg13g2 -zz -r bondpad.py -rd diameter=70.0 -rd bottom_metal=3 -rd lef_output=lef/bondpad_70x70.lef

LEF output features:
    - MACRO with CLASS COVER (identifies the cell as a cover/pad macro)
    - PIN ``pad`` exposed on Metal2 through TopMetal2 (multi-layer port)
    - OBS (obstructions) on every metal from ``bottom_metal`` up to TopMetal2,
      blocking the router from using those layers under the pad
    - Layer names matching the IHP SG13G2 tech.lef
"""
# pylint: disable=import-error
import pathlib
import sys
import pya
import klayout.db

# IHP SG13_dev PCell library ships with the PDK and contains the ``bondpad`` PCell.
LIB = 'SG13_dev'
PCELL = 'bondpad'

# Full IHP SG13G2 metal stack from bottom to top (indices 0-6).
METAL_LAYERS = ['Metal1', 'Metal2', 'Metal3', 'Metal4', 'Metal5', 'TopMetal1', 'TopMetal2']

# Mapping from the wrapper's int bottom_metal (1..6) to the value the
# SG13_dev ``bondpad`` PCell expects on its ``bottomMetal`` parameter
# (ChoiceConstraint ['1','2','3','4','5','TM1']). Passing the wrong key
# (e.g. ``bottom_metal``) is silently ignored by ``add_pcell_variant``,
# which then falls back to the PDK default of '3' (Metal3).
PCELL_BOTTOM_METAL = {1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: 'TM1'}


def generate_bondpad_lef(size: float, shape: str, output: str,
                         bottom_metal: int = 1):
    """Generate a LEF macro description for the bondpad.

    The macro name is derived from the output filename (stem before the first
    dot), e.g. ``lef/bondpad_70x70.lef`` -> macro name ``bondpad_70x70``.

    The generated LEF follows the same conventions as the hand-crafted reference:
    - PIN ``pad`` exposed on Metal2 through TopMetal2 (multi-layer port)
    - OBS covering the full pad area on every metal from ``bottom_metal``
      (default Metal1) up to TopMetal2
    - SYMMETRY X Y R90 and SITE sg13g2_ioSite for padring placement

    :param size: Pad side length / diameter in microns.
    :param shape: Pad geometry ('square', 'octagon', or 'circle').
        Only affects the GDS; the LEF always uses full-size rectangles.
    :param output: Filesystem path for the LEF file to write.
    :param bottom_metal: Lowest metal layer in the stack (1-6, default 1).
    """
    cell_name = pathlib.Path(output).resolve().name.split('.')[0]

    # Create directory
    pathlib.Path(output).parent.mkdir(parents=True, exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        # --- LEF header ---
        f.write("VERSION 5.8 ;\n")
        f.write("\n")

        # --- MACRO definition ---
        f.write(f"MACRO {cell_name}\n")
        f.write("  CLASS COVER ;\n")
        f.write("  ORIGIN 0 0 ;\n")
        f.write(f"  FOREIGN {cell_name} 0 0 ;\n")
        f.write(f"  SIZE {size:.1f} BY {size:.1f} ;\n")
        f.write("  SYMMETRY X Y R90 ;\n")
        f.write("  SITE sg13g2_ioSite ;\n")

        # --- PIN pad – exposed on Metal2 through TopMetal2 so the router can
        #     connect at any upper-metal level.  Uses lowercase ``pad`` to
        #     match the Verilog module port name. ---
        f.write("  PIN pad\n")
        f.write("    USE SIGNAL ;\n")
        f.write("    PORT\n")
        # Expose pin on Metal2 up to TopMetal2 (skip Metal1 – typically not
        # routed to for a bondpad connection).
        for layer in METAL_LAYERS[1:]:  # Metal2 .. TopMetal2
            f.write(f"      LAYER {layer} ;\n")
            f.write(f"        RECT 0 0 {size:.1f} {size:.1f} ;\n")
        f.write("    END\n")
        f.write("  END pad\n")
        f.write("\n")

        # --- OBS – conservatively block the full pad area on every metal
        #     from bottom_metal up to TopMetal2 to prevent DRC violations
        #     from routes running underneath the pad. ---
        f.write("  OBS\n")
        for i in range(bottom_metal - 1, len(METAL_LAYERS)):
            layer_name = METAL_LAYERS[i]
            f.write(f"    LAYER {layer_name} ;\n")
            f.write(f"      RECT 0 0 {size:.1f} {size:.1f} ;\n")
        f.write("  END\n")

        f.write(f"END {cell_name}\n")

    print(f"LEF written to: {output}")


def generate_bondpad_gds(diameter: float, shape: str, output: str,
                         bottom_metal: int = 1):
    """Instantiate the SG13_dev ``bondpad`` PCell and write the result as GDS.

    A new KLayout layout is created, the PCell is placed at the centre of a
    top cell whose name matches the output filename stem, and the layout is
    saved to *output*.

    :param diameter: Pad diameter / side-length in microns.
    :param shape: Pad geometry ('square', 'octagon', or 'circle').
    :param output: Filesystem path for the GDS file to write.
    :param bottom_metal: Lowest metal layer (1-6, default 1).  Passed to the
        PCell but the actual layer stack depends on the PCell definition.
    """
    layout = klayout.db.Layout(True)
    layout.dbu = 0.001  # 1 nm database unit – standard for SG13G2
    # Centre the PCell origin: offset = half the pad size in database units.
    offset = int(diameter / 2 / layout.dbu)

    # Look up the PCell declaration from the SG13_dev library.
    lib = pya.Library.library_by_name(LIB, 'sg13g2')
    pcell_decl = lib.layout().pcell_declaration(PCELL)

    # Derive the top-cell name from the output filename (e.g. 'bondpad_70x70').
    cell_name = pathlib.Path(output).resolve().name.split('.')[0]
    top_cell = layout.cell(layout.add_cell(cell_name))
    pcell = layout.add_pcell_variant(lib, pcell_decl.id(),
        {'diameter': f'{diameter}u', 'shape': shape,
         'bottomMetal': PCELL_BOTTOM_METAL[bottom_metal]})
    top_cell.insert(klayout.db.CellInstArray(pcell, klayout.db.Trans(klayout.db.Vector(offset, offset))))

    # Ensure the output directory exists.
    pathlib.Path(output).parent.mkdir(parents=True, exist_ok=True)

    layout.write(output)
    print(f"GDS written to: {output}")


# ---------------------------------------------------------------------------
# CLI entry point – parse arguments injected by ``klayout -rd key=value``
# ---------------------------------------------------------------------------

try:
    diameter  # noqa: F821 - defined by klayout -rd
except NameError:
    print("Missing diameter argument. Please define '-rd diameter=<diameter>'")
    sys.exit(1)

try:
    shape  # noqa: F821 - defined by klayout -rd
except NameError:
    shape = 'octagon'  # pylint: disable=invalid-name

allowed_shapes = ('octagon', 'square', 'circle')
if shape not in allowed_shapes:
    print(f"Illegal bondpad shape. Allowed are {','.join(allowed_shapes)}")
    sys.exit(1)

try:
    gds_output  # noqa: F821 - defined by klayout -rd
except NameError:
    gds_output = None  # pylint: disable=invalid-name

# Optional LEF output
try:
    lef_output  # noqa: F821 - defined by klayout -rd
except NameError:
    lef_output = None  # pylint: disable=invalid-name

if gds_output is None and lef_output is None:
    print("Missing GDS or LEF output argument. Please define at least one of:")
    print("  '-rd gds_output=<path-to-bondpad/bondpad.gds>'")
    print("or")
    print("  '-rd lef_output=<path-to-bondpad/bondpad.lef>'")
    sys.exit(1)

# Optional bottom metal (default: Metal1)
try:
    bottom_metal  # noqa: F821 - defined by klayout -rd
    bottom_metal = int(bottom_metal)
except NameError:
    bottom_metal = 1  # pylint: disable=invalid-name

if bottom_metal < 1 or bottom_metal > 6:
    print(f"Invalid bottom_metal={bottom_metal}. Must be 1-6.")
    sys.exit(1)

if gds_output:
    generate_bondpad_gds(float(diameter), shape, gds_output,  # pylint: disable=undefined-variable
                         bottom_metal=bottom_metal)

if lef_output:
    generate_bondpad_lef(float(diameter), shape, lef_output,  # pylint: disable=undefined-variable
                         bottom_metal=bottom_metal)
