#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Harald Pretl
# Johannes Kepler University, Department for Integrated Circuits
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
"""
merge_spice.py - Merge SPICE subcircuits from library files into a main netlist.

Usage:
    python3 merge_spice.py <main.spice> <lib1.spice> [lib2.spice ...] [-o output.spice]

Features:
- Resolves all subcircuit dependencies transitively
- Replaces empty (black-box) stubs with full definitions from libraries
- Validates pin names and order between stubs and library definitions
- Removes remaining empty subcircuit definitions and their instantiations
- Prefers full definitions over black-box stubs
"""

import sys
import os
from collections import OrderedDict

# PDK primitive device types that do not need subcircuit definitions
PDK_PRIMITIVES = {
    'sg13_lv_nmos', 'sg13_lv_pmos',
    'sg13_hv_nmos', 'sg13_hv_pmos',
    'cap_cmim', 'cap_rfcmim',
    'ptap1', 'ntap1',
    'dantenna', 'dpantenna',
    'rppd', 'rhigh', 'rsil',
    'npn13G2', 'npn13G2l', 'npn13G2v',
    'pnpMPA', 'ind_mim',
}


class SpiceSubckt:
    """Represents a parsed .subckt definition."""
    def __init__(self, name, pins, body_lines, is_blackbox=False):
        self.name = name
        self.pins = list(pins)
        self.body_lines = list(body_lines)
        self.is_blackbox = is_blackbox


def parse_spice_file(filepath):
    """Parse a SPICE file, extracting subcircuit definitions and remaining lines.

    Returns:
        subckts: OrderedDict of name -> SpiceSubckt
        other_lines: list of lines outside any .subckt
    """
    with open(filepath, 'r') as f:
        raw_lines = f.readlines()

    subckts = OrderedDict()
    other_lines = []

    in_subckt = False
    current_name = None
    current_pins = []
    current_body = []

    i = 0
    while i < len(raw_lines):
        line = raw_lines[i].rstrip('\n')
        stripped = line.strip()

        # Detect .subckt start (case-insensitive)
        if stripped.lower().startswith('.subckt ') or stripped.lower().startswith('.subckt\t'):
            # Collect continuation lines belonging to the .subckt header
            full_line = stripped
            j = i + 1
            while j < len(raw_lines) and raw_lines[j].lstrip().startswith('+'):
                full_line += ' ' + raw_lines[j].strip()[1:].strip()
                j += 1

            tokens = full_line.split()
            current_name = tokens[1]
            current_pins = tokens[2:]
            current_body = []
            in_subckt = True
            i = j
            continue

        if in_subckt:
            if stripped.lower().startswith('.ends'):
                is_bb = all(
                    not bl.strip() or bl.strip().startswith('*')
                    for bl in current_body
                )
                subckts[current_name] = SpiceSubckt(
                    current_name, current_pins, current_body, is_bb
                )
                in_subckt = False
                current_name = None
                i += 1
                continue
            else:
                # Skip *.PININFO lines and their *+ continuations
                if stripped.startswith('*.PININFO'):
                    i += 1
                    while i < len(raw_lines) and raw_lines[i].strip().startswith('*+'):
                        i += 1
                    continue
                current_body.append(line)
                i += 1
                continue

        other_lines.append(line)
        i += 1

    # Handle truncated file (no .ends before EOF)
    if in_subckt and current_name:
        is_bb = all(
            not bl.strip() or bl.strip().startswith('*')
            for bl in current_body
        )
        subckts[current_name] = SpiceSubckt(
            current_name, current_pins, current_body, is_bb
        )
        print(f"  WARNING: '{current_name}' in {os.path.basename(filepath)} "
              f"has no .ends (truncated file?)", file=sys.stderr)

    return subckts, other_lines


def parse_x_line(joined_line):
    """Parse a subcircuit instantiation line (X line).

    Returns (instance_name, nets_list, subckt_type) or (None, [], None).
    The subckt_type is the last non-parameter token after the instance name.
    Parameter tokens contain '=' or start with '$'.
    """
    tokens = joined_line.split()
    if not tokens:
        return None, [], None

    inst_name = tokens[0]

    # Collect tokens until we hit a parameter (contains '=' or starts with '$')
    non_param = []
    for t in tokens[1:]:
        if '=' in t or t.startswith('$'):
            break
        non_param.append(t)

    if not non_param:
        return inst_name, [], None

    subckt_type = non_param[-1]
    nets = non_param[:-1]
    return inst_name, nets, subckt_type


def find_used_subckt_types(subckt):
    """Return the set of subcircuit type names instantiated in a subcircuit body."""
    used = set()
    # Join continuation lines for parsing
    joined_lines = _join_continuations(subckt.body_lines)
    for line in joined_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('*'):
            continue
        tokens = stripped.split()
        if tokens and tokens[0][0].lower() == 'x':
            _, _, stype = parse_x_line(stripped)
            if stype:
                used.add(stype)
    return used


def _join_continuations(lines):
    """Join SPICE continuation lines (starting with '+') with their predecessor."""
    result = []
    for line in lines:
        if line.lstrip().startswith('+') and result:
            result[-1] += ' ' + line.lstrip()[1:].strip()
        else:
            result.append(line)
    return result


def build_merged_library(main_subckts, lib_subckts_list):
    """Build a unified lookup of subcircuit definitions from all sources.

    Priority: full definitions over black-box stubs.
    Main file definitions win over library ones when both are full.
    """
    merged = OrderedDict()

    # Add library definitions (earlier libs have lower priority)
    for lib in lib_subckts_list:
        for name, sub in lib.items():
            if name not in merged or (merged[name].is_blackbox and not sub.is_blackbox):
                merged[name] = sub

    # Main file definitions have highest priority (unless blackbox and lib has full)
    for name, sub in main_subckts.items():
        if name not in merged:
            merged[name] = sub
        elif not sub.is_blackbox:
            merged[name] = sub
        # else: main has blackbox, keep the (possibly full) library version

    return merged


def resolve_dependencies(main_subckts, merged_lib):
    """Starting from the main file subcircuits, find all transitively needed definitions."""
    needed = OrderedDict()

    # Seed with main file subcircuits (use full defs from merged_lib when available)
    for name in main_subckts:
        if name in merged_lib and not merged_lib[name].is_blackbox:
            needed[name] = merged_lib[name]
        else:
            needed[name] = main_subckts[name]

    # BFS to collect all transitive dependencies
    queue = set()
    for sub in needed.values():
        queue.update(find_used_subckt_types(sub))

    while queue:
        next_queue = set()
        for stype in queue:
            if stype in needed or stype in PDK_PRIMITIVES:
                continue
            if stype in merged_lib:
                needed[stype] = merged_lib[stype]
                next_queue.update(find_used_subckt_types(merged_lib[stype]))
            else:
                print(f"  WARNING: No definition found for subcircuit '{stype}'",
                      file=sys.stderr)
        queue = next_queue - set(needed.keys())

    return needed


def check_pin_compatibility(main_subckts, merged_lib):
    """Check that stub pins match the full library definition pins.

    For every subcircuit that exists in the main file as a black-box stub
    and is being replaced by a full definition from a library, verify that
    the pin names and their order are identical.

    Returns a list of warning/error message strings (empty if all match).
    """
    messages = []
    for name, main_sub in main_subckts.items():
        if not main_sub.is_blackbox:
            continue
        if name not in merged_lib or merged_lib[name].is_blackbox:
            continue
        lib_sub = merged_lib[name]
        stub_pins = main_sub.pins
        lib_pins = lib_sub.pins

        if stub_pins == lib_pins:
            continue

        stub_set = set(stub_pins)
        lib_set = set(lib_pins)

        missing = stub_set - lib_set
        extra = lib_set - stub_set

        if stub_set == lib_set:
            messages.append(
                f"Pin order mismatch for '{name}': "
                f"stub has [{', '.join(stub_pins)}] "
                f"but library has [{', '.join(lib_pins)}]"
            )
        else:
            parts = [f"Pin mismatch for '{name}':"]
            if missing:
                parts.append(f"  pins in stub but not in library: {', '.join(sorted(missing))}")
            if extra:
                parts.append(f"  pins in library but not in stub: {', '.join(sorted(extra))}")
            if len(stub_pins) != len(lib_pins):
                parts.append(f"  stub has {len(stub_pins)} pin(s), library has {len(lib_pins)}")
            messages.append('\n'.join(parts))

    return messages


def format_spice_line(text, max_width=132):
    """Format a long SPICE line using '+' continuation lines."""
    if len(text) <= max_width:
        return text

    tokens = text.split()
    if not tokens:
        return text

    lines = [tokens[0]]
    for tok in tokens[1:]:
        if len(lines[-1]) + 1 + len(tok) > max_width:
            lines.append('+ ' + tok)
        else:
            lines[-1] += ' ' + tok
    return '\n'.join(lines)


def remove_empty_subckts(needed):
    """Iteratively remove empty (black-box) subcircuit definitions and their instantiations.

    After removing instances of empty subcircuits, other subcircuits may become
    empty too, so the process repeats until stable.
    Returns a list of removed subcircuit names.
    """
    removed_names = []

    while True:
        # Find empty subcircuits in this iteration
        empty_names = {name for name, sub in needed.items() if sub.is_blackbox}
        if not empty_names:
            break

        removed_names.extend(sorted(empty_names, key=str.lower))

        # Remove instantiations of empty subcircuits from all remaining bodies
        for name, sub in needed.items():
            if name in empty_names:
                continue
            sub.body_lines = _strip_instances_of(sub.body_lines, empty_names)

        # Remove the empty definitions themselves
        for name in empty_names:
            del needed[name]

        # Re-evaluate: some subcircuits may now be empty after instance removal
        for sub in needed.values():
            sub.is_blackbox = all(
                not bl.strip() or bl.strip().startswith('*')
                for bl in sub.body_lines
            )

    return removed_names


def _strip_instances_of(body_lines, targets):
    """Remove X-instantiation lines that call any subcircuit in *targets*."""
    result = []
    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        # Collect continuation lines forming one logical statement
        group = [line]
        j = i + 1
        while j < len(body_lines) and body_lines[j].lstrip().startswith('+'):
            group.append(body_lines[j])
            j += 1

        # Join into a single logical line
        joined = line
        for g in group[1:]:
            joined += ' ' + g.lstrip()[1:].strip()
        stripped = joined.strip()

        skip = False
        if stripped and not stripped.startswith('*'):
            tokens = stripped.split()
            if tokens and tokens[0][0].lower() == 'x':
                _, _, stype = parse_x_line(stripped)
                if stype in targets:
                    skip = True

        if not skip:
            result.extend(group)
        i = j

    return result


def topological_sort(subckts):
    """Return subcircuit names in dependency order (leaves first, roots last)."""
    visited = set()
    order = []

    def visit(name):
        if name in visited:
            return
        visited.add(name)
        if name in subckts:
            for dep in find_used_subckt_types(subckts[name]):
                if dep in subckts:
                    visit(dep)
        order.append(name)

    for name in subckts:
        visit(name)
    return order


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <main.spice> <lib1> [lib2 ...] [-o output.spice]",
              file=sys.stderr)
        sys.exit(1)

    # --- Parse command-line arguments ---
    main_file = sys.argv[1]
    lib_files = []
    output_file = None

    idx = 2
    while idx < len(sys.argv):
        if sys.argv[idx] == '-o' and idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
            idx += 2
        else:
            lib_files.append(sys.argv[idx])
            idx += 1

    if output_file is None:
        base, ext = os.path.splitext(main_file)
        output_file = base + '_merged' + ext

    print(f"Main file:     {main_file}")
    print(f"Library files: {', '.join(lib_files)}")
    print(f"Output file:   {output_file}")
    print()

    # --- Step 1: Parse all files ---
    main_subckts, main_other = parse_spice_file(main_file)
    print(f"  {os.path.basename(main_file)}: {len(main_subckts)} subcircuit(s)")

    lib_subckts_list = []
    for lf in lib_files:
        subs, _ = parse_spice_file(lf)
        lib_subckts_list.append(subs)
        n_bb = sum(1 for s in subs.values() if s.is_blackbox)
        print(f"  {os.path.basename(lf)}: {len(subs)} subcircuit(s) "
              f"({n_bb} black-box)")

    # --- Step 2: Build merged library and resolve dependencies ---
    merged = build_merged_library(main_subckts, lib_subckts_list)
    needed = resolve_dependencies(main_subckts, merged)
    print(f"\n  Total resolved subcircuits: {len(needed)}")

    # --- Step 3: Check pin compatibility between stubs and library definitions ---
    pin_messages = check_pin_compatibility(main_subckts, merged)
    if pin_messages:
        print(file=sys.stderr)
        for msg in pin_messages:
            print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(1)

    # --- Step 4: Remove empty subcircuit definitions and their instantiations ---
    removed = remove_empty_subckts(needed)
    if removed:
        print(f"\n  WARNING: Removed {len(removed)} empty subcircuit(s):")
        for rn in removed:
            print(f"    - {rn}")

    # --- Step 5: Write merged output in dependency order ---
    order = topological_sort(needed)

    with open(output_file, 'w') as f:
        f.write(f"* Merged SPICE netlist\n")
        f.write(f"* Main: {os.path.basename(main_file)}\n")
        f.write(f"* Libraries: {', '.join(os.path.basename(l) for l in lib_files)}\n")
        f.write(f"* Empty stubs replaced with full definitions from libraries\n\n")

        for name in order:
            sub = needed[name]
            header = f".subckt {name} " + " ".join(sub.pins)
            f.write(format_spice_line(header) + '\n')
            for bl in sub.body_lines:
                f.write(bl + '\n')
            f.write(f".ends {name}\n\n")

        # Preserve .GLOBAL and .END statements from the main file
        for line in main_other:
            stripped = line.strip().lower()
            if stripped.startswith('.global') or stripped == '.end':
                f.write(line.strip() + '\n')

    print(f"\n  Output written to {output_file}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
