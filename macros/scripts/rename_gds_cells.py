# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

"""Renames the cells inside the GDS files of a layout folder after a macro was copied under a new name.

Every cell whose name carries the old macro name (as old, Old or OLD) is renamed with the new name substituted in the same case.
A cell that is a library reference is relinked instead of renamed: a `.klay.gds` pulls cells from the libraries that its `.klay.klib` maps to other GDS files (KLayout Library Manager plugin convention), and each link is stored inside the GDS by library name and cell name, where no text edit reaches it.
The files are processed in dependency order, libraries before the layouts that use them, and every reference is pointed at the renamed cell of the renamed library.
The libraries of a map are registered the way the plugin registers them, nested maps included.
A reference that the maps do not resolve in the source stays as it is, KLayout keeps its frozen geometry either way.

Run it in batch mode without the PDK. The PCells then stay frozen exactly as the source saved them instead of being re-evaluated against the installed PDK, and they resolve again as soon as the layout is opened with the PDK.

    klayout -b -r rename_gds_cells.py -rd layout=<folder> -rd old=<name> -rd new=<name>

Expected KLayout -rd parameters:
    layout: folder with the GDS files (read and written in-place)
    old:    name of the macro the files were copied from
    new:    name of the new macro
"""

import glob
import json
import os
import sys

import pya

# Libraries registered in this run by name, each read once from its renamed file
registry = {}


def rename(text, old_name, new_name):
    """Substitutes the new name for the old one in the three spellings old, Old and OLD."""
    for o, n in ((old_name, new_name), (old_name.capitalize(), new_name.capitalize()), (old_name.upper(), new_name.upper())):
        text = text.replace(o, n)
    return text


def library_map(gds_path):
    """Returns the path of the library map next to a GDS file, or None."""
    klib_path = gds_path[: -len(".gds")] + ".klib"
    return klib_path if os.path.exists(klib_path) else None


def library_definitions(klib_path, seen=()):
    """Returns the (lib_name, lib_path) pairs of a library map, following its includes."""
    if klib_path in seen:
        sys.exit(f"ERROR: {klib_path} includes itself")
    with open(klib_path) as f:
        config = json.load(f)
    base = os.path.dirname(klib_path)
    definitions = []
    for statement in config.get("statements", []):
        if "lib_name" in statement:
            definitions.append((statement["lib_name"], os.path.normpath(os.path.join(base, os.path.expandvars(statement["lib_path"])))))
        elif "include_path" in statement:
            definitions += library_definitions(os.path.normpath(os.path.join(base, os.path.expandvars(statement["include_path"]))), seen + (klib_path,))
    return definitions


def register_libraries(klib_path, seen=()):
    """Registers the libraries of a map, nested maps first so that every library reads with live references."""
    if klib_path in seen:
        sys.exit(f"ERROR: the library maps below {klib_path} reference each other in a cycle")
    for lib_name, lib_path in library_definitions(klib_path):
        if lib_path.endswith(".gds") and library_map(lib_path):
            register_libraries(library_map(lib_path), seen + (klib_path,))
        if lib_name in registry:
            if registry[lib_name][1] != lib_path:
                print(f"WARNING: library '{lib_name}' is mapped to {lib_path} in {os.path.basename(klib_path)} and to {registry[lib_name][1]} elsewhere, keeping the first")
            continue
        lib = pya.Library()
        lib.layout().read(lib_path)
        lib.register(lib_name)
        registry[lib_name] = (lib, lib_path)


def processing_order(gds_files):
    """Orders the files so that every library precedes the layouts that reference it."""
    files = set(gds_files)
    dependencies = {}
    for gds_path in gds_files:
        klib_path = library_map(gds_path)
        dependencies[gds_path] = {p for _, p in library_definitions(klib_path) if p in files} if klib_path else set()
    order = []
    while len(order) < len(gds_files):
        ready = [p for p in gds_files if p not in order and dependencies[p] <= set(order)]
        if not ready:
            sys.exit("ERROR: the library maps reference each other in a cycle: " + ", ".join(sorted(set(gds_files) - set(order))))
        order += ready
    return order


def process(gds_path):
    """Renames the plain cells of one GDS file and relinks its library references."""
    klib_path = library_map(gds_path)
    if klib_path:
        register_libraries(klib_path)

    layout = pya.Layout()
    layout.read(gds_path)

    changed = False
    stale = []
    for ci in [c.cell_index() for c in layout.each_cell()]:
        if not layout.is_valid_cell_index(ci):
            continue  # pruned with a reference relinked earlier in this loop
        cell = layout.cell(ci)
        name = cell.name
        new_name = rename(name, old, new)
        if cell.is_cold_proxy():
            lib_name = rename(cell.library_name(), old, new)
            cell_name = rename(cell.library_cell_name(), old, new)
            if lib_name not in registry:
                # A PCell or a library outside the maps, frozen here and resolved by the PDK later, unless the maps dropped it
                if lib_name != cell.library_name():
                    stale.append(ci)
                continue
            # The library or the cell it names was renamed on disk: point it at the renamed cell of the renamed library
            lib_cell = registry[lib_name][0].layout().cell(cell_name)
            if lib_cell is None:
                stale.append(ci)
                continue
            lib = registry[lib_name][0]
            new_ci = layout.add_lib_cell(lib, lib_cell.cell_index())
            count = 0
            for pi in list(cell.each_parent_cell()):
                for inst in [i for i in layout.cell(pi).each_inst() if i.cell_index == ci]:
                    inst.cell_index = new_ci
                    count += 1
            layout.prune_cell(ci, -1)
            print(f"relinked {count} instance(s) of '{name}' to cell '{lib_cell.name}' of library '{lib.name()}'")
        elif new_name == name:
            continue
        elif cell.is_proxy():
            print(f"WARNING: cell '{name}' of {os.path.basename(gds_path)} is a library reference and keeps its name")
            continue
        else:
            cell.name = new_name
            print(f"renamed cell '{name}' to '{new_name}'")
        changed = True

    for ci in stale:
        # Still there after the relinks, so not a frozen child of a reference that was replaced: unresolved in the source as well
        if layout.is_valid_cell_index(ci):
            cell = layout.cell(ci)
            print(f"WARNING: cell '{cell.name}' of {os.path.basename(gds_path)} references cell '{cell.library_cell_name()}' of library '{cell.library_name()}', which the library maps do not resolve, it stays as it is")

    if changed:
        layout.write(gds_path)
        print(f"written {gds_path}")
    else:
        print(f"no cell of {os.path.basename(gds_path)} carries '{old}', file untouched")


def main():
    for parameter in ("layout", "old", "new"):
        if parameter not in globals():
            sys.exit(f"ERROR: missing -rd {parameter}=<value>")
    gds_files = sorted(os.path.abspath(p) for p in glob.glob(os.path.join(layout, "*.gds")))
    if not gds_files:
        sys.exit(f"ERROR: no GDS file in {layout}")
    for gds_path in processing_order(gds_files):
        print(f"--- {os.path.basename(gds_path)}")
        process(gds_path)


main()
