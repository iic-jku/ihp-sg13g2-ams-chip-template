# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

"""Renames the cells of a GDS file after a macro was copied under a new name.

Every cell whose name carries the old macro name (as old, Old or OLD) is renamed with the new name substituted in the same case.
A cell that is a library reference is relinked instead of renamed: `<layout>.klay.gds` pulls its unit cell from a library that `<layout>.klay.klib` maps to the unit cell GDS (KLayout Library Manager plugin convention), and that link is stored inside the GDS by library name and cell name, where no text edit reaches it.
The script registers the libraries of that map, which the text pass of `make macro` has already renamed, and points every instance of the old reference at the renamed cell of the renamed library.

Run it through KLayout with the PDK technology on KLAYOUT_PATH, so that the PCells of the layout resolve and keep their context on the save.
`klayout -b` does not run the autorun macros of the PDK, so the PCell library is missing there.

    klayout -z -nc -r rename_gds_cells.py -rd gds=<file> -rd old=<name> -rd new=<name>

Expected KLayout -rd parameters:
    gds: path to the GDS file (read and written in-place)
    old: name of the macro the file was copied from
    new: name of the new macro
"""

import json
import os
import sys

import pya


def rename(text, old_name, new_name):
    """Substitutes the new name for the old one in the three spellings old, Old and OLD."""
    for o, n in ((old_name, new_name), (old_name.capitalize(), new_name.capitalize()), (old_name.upper(), new_name.upper())):
        text = text.replace(o, n)
    return text


def select_technology():
    """Returns the technology installed below a KLAYOUT_PATH entry, or the only named one, or none."""
    names = [n for n in pya.Technology.technology_names() if n]
    roots = [os.path.realpath(p) for p in os.environ.get("KLAYOUT_PATH", "").split(":") if p]
    for name in names:
        base = os.path.realpath(pya.Technology.technology_by_name(name).base_path())
        if any(base == root or base.startswith(root + os.sep) for root in roots):
            return name
    return names[0] if len(names) == 1 else ""


def library_definitions(klib_path):
    """Returns the (lib_name, lib_path) pairs of a library map, following its includes."""
    with open(klib_path) as f:
        config = json.load(f)
    base = os.path.dirname(klib_path)
    definitions = []
    for statement in config.get("statements", []):
        if "lib_name" in statement:
            definitions.append((statement["lib_name"], os.path.join(base, os.path.expandvars(statement["lib_path"]))))
        elif "include_path" in statement:
            definitions += library_definitions(os.path.join(base, os.path.expandvars(statement["include_path"])))
    return definitions


def register_libraries(klib_path, tech):
    """Registers every library of the map. The technology on the library layout keeps its PCells live."""
    libraries = []
    for lib_name, lib_path in library_definitions(klib_path):
        lib = pya.Library()
        lib.technology = tech
        lib.layout().technology_name = tech
        lib.layout().read(lib_path)
        lib.register(lib_name)
        libraries.append(lib)
        print(f"registered library '{lib_name}' from {lib_path}")
    return libraries


def main():
    for parameter in ("gds", "old", "new"):
        if parameter not in globals():
            sys.exit(f"ERROR: missing -rd {parameter}=<value>")
    gds_path = os.path.abspath(gds)
    tech = select_technology()
    if not tech:
        print("WARNING: no PDK technology found, is KLAYOUT_PATH set? The PCells will not resolve.")
    klib_path = gds_path[: -len(".gds")] + ".klib" if gds_path.endswith(".gds") else ""
    libraries = register_libraries(klib_path, tech) if klib_path and os.path.exists(klib_path) else []

    layout = pya.Layout()
    layout.technology_name = tech
    layout.read(gds_path)

    changed = False
    for ci in [c.cell_index() for c in layout.each_cell()]:
        cell = layout.cell(ci)
        name = cell.name
        new_name = rename(name, old, new)
        if new_name == name:
            continue
        if cell.is_proxy() and cell.library() is None and not cell.is_pcell_variant():
            # An unresolved library reference: relink every instance to the renamed cell of a registered library
            target = next(((lib, lib.layout().cell(new_name)) for lib in libraries if lib.layout().cell(new_name) is not None), None)
            if target is None:
                sys.exit(f"ERROR: cell '{name}' is a library reference, but no library of {klib_path} has a cell '{new_name}'")
            lib, lib_cell = target
            new_ci = layout.add_lib_cell(lib, lib_cell.cell_index())
            count = 0
            for pi in list(cell.each_parent_cell()):
                for inst in [i for i in layout.cell(pi).each_inst() if i.cell_index == ci]:
                    inst.cell_index = new_ci
                    count += 1
            layout.prune_cell(ci, -1)
            print(f"relinked {count} instance(s) of '{name}' to cell '{lib_cell.name}' of library '{lib.name()}'")
        elif cell.is_proxy():
            print(f"WARNING: cell '{name}' is a library or PCell reference and keeps its name")
            continue
        else:
            cell.name = new_name
            print(f"renamed cell '{name}' to '{new_name}'")
        changed = True

    if changed:
        layout.write(gds_path)
        print(f"written {gds_path}")
    else:
        print(f"no cell of {gds_path} carries '{old}', file untouched")


main()
