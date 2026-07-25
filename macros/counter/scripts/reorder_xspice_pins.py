#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
"""
Reorder the .subckt pin list in an XSPICE file to match the pin order
of an Xschem .sym symbol file.

Symbol and XSPICE pin names do not need to follow a shared naming
convention. Two matching modes are supported:

  - **Name mode (preferred, order-independent):** if *every* symbol pin
    carries a ``sim_pinname=<netlist_name>`` property, that property is
    the pin's real name in the source netlist. The XSPICE pin is derived
    by prefixing ``a_`` and replacing ``[``/``]`` with ``_`` (matching
    what ``spi2xspice.py`` does), e.g. ``sim_pinname=clock_i`` ->
    ``a_clock_i`` and ``sim_pinname=counter_value_o[0]`` ->
    ``a_counter_value_o_0_``. Because pins are matched by name, this mode
    is immune to how the netlister ordered the ``.subckt`` ports (Magic,
    for instance, sorts them alphabetically). Use this mode when feeding a
    LibreLane-extracted / place-and-routed netlist whose port order does
    not match the symbol.
  - **Positional mode (fallback):** if the pins do *not* all carry
    ``sim_pinname``, power pins are matched by name (``VDD`` <->
    ``a_VPWR``, ``VSS`` <-> ``a_VGND``) and every other pin is matched by
    *position*: the i-th non-power symbol pin maps to the i-th non-power
    XSPICE pin. This is only correct when the netlist keeps the symbol's
    port order (e.g. the yosys ``.nl.v`` via ``vlog2Verilog``).

Bus pins in the symbol use the xschem range syntax ``name[A..B]`` and
are expanded into individual indexed pins (``name[A]``, ``name[A+1]``,
..., ``name[B]``) before matching. A bus ``sim_pinname`` may be given as
a bare base (``counter_value_o``) or with a range; the symbol bus indices
are applied to it.

Pin ordering from the symbol supports two modes:

  - ``sim_pinnumber`` mode: if *every* B 5 pin line (or bus group) in
    the .sym file carries a ``sim_pinnumber=<n>`` property, the entries
    are sorted by that number before positional matching against the
    XSPICE pins. Expanded bus pins keep their intra-bus order.
  - Appearance-order mode (default): if no pin (or only some pins) carry
    ``sim_pinnumber``, the order of appearance in the .sym file is used,
    matching the original behaviour.

Usage:
    python reorder_xspice_pins.py <sym_file> <xspice_file> [-o <output_file>]

If -o is not given, the xspice file is overwritten in-place.
"""

import argparse
import re


POWER_MAP = {'VDD': 'a_VPWR', 'VSS': 'a_VGND'}
XSPICE_POWER = set(POWER_MAP.values())


def parse_sym_pins(sym_path: str) -> list[tuple[str, str | None]]:
    """Extract pins from a .sym file as ``(display_name, real_name)`` pairs.

    Pins are defined as:
    ``B 5 ... {name=<pin_name> dir=<dir> [sim_pinnumber=<n>] [sim_pinname=<net>]}``

    ``real_name`` is the netlist-side name declared by ``sim_pinname=`` (or
    ``None`` when the pin has no such property). A bus pin written as
    ``name[A..B]`` is expanded into individual indexed pins; ``A`` and ``B``
    may be in either order. A bus ``sim_pinname`` may be a bare base or carry
    its own range - either way the display bus indices are applied to it, so
    ``name[A..B]`` with ``sim_pinname=net`` yields ``net[A]..net[B]``.

    If every pin (or bus group) carries a ``sim_pinnumber`` property, the
    entries are sorted by that number instead of by order of appearance;
    expanded bus pins keep their intra-bus order.
    """
    pin_pattern = re.compile(r'^B\s+5\s+.*\{name=(\S+)\s+dir=\w+[^}]*\}')
    bus_range_pattern = re.compile(r'^(.+)\[(\d+)\.\.(\d+)\]$')
    sim_num_pattern = re.compile(r'sim_pinnumber=(\d+)')
    sim_name_pattern = re.compile(r'sim_pinname=([^\s}]+)')
    raw = []  # list of (sim_pinnumber | None, [(display, real|None), ...])
    with open(sym_path, 'r') as f:
        for line in f:
            stripped = line.strip()
            m = pin_pattern.match(stripped)
            if not m:
                continue
            name = m.group(1)
            sn = sim_num_pattern.search(stripped)
            sim_num = int(sn.group(1)) if sn else None
            pn = sim_name_pattern.search(stripped)
            real = pn.group(1) if pn else None
            bm = bus_range_pattern.match(name)
            if bm:
                base = bm.group(1)
                a, b = int(bm.group(2)), int(bm.group(3))
                step = 1 if a <= b else -1
                idxs = list(range(a, b + step, step))
                if real is not None:
                    rbm = bus_range_pattern.match(real)
                    rbase = rbm.group(1) if rbm else real
                    expanded = [(f'{base}[{i}]', f'{rbase}[{i}]') for i in idxs]
                else:
                    expanded = [(f'{base}[{i}]', None) for i in idxs]
            else:
                expanded = [(name, real)]
            raw.append((sim_num, expanded))
    if raw and all(n is not None for n, _ in raw):
        raw.sort(key=lambda x: x[0])
    pins = []
    for _, expanded in raw:
        pins.extend(expanded)
    return pins


def parse_xspice_subckt(xspice_path: str) -> tuple[str, list[str], int, int]:
    """Extract the subcircuit name and pin list from the .subckt line.

    Handles continuation lines starting with '+'.
    Returns (subckt_name, pin_list, first_line_number, last_line_number).
    """
    with open(xspice_path, 'r') as f:
        all_lines = f.readlines()
    for i, line in enumerate(all_lines):
        stripped = line.strip()
        if stripped.startswith('.subckt'):
            parts = stripped.split()
            subckt_name = parts[1]
            pins = parts[2:]
            last = i
            for j in range(i + 1, len(all_lines)):
                cont = all_lines[j].strip()
                if cont.startswith('+'):
                    pins.extend(cont[1:].split())
                    last = j
                else:
                    break
            return subckt_name, pins, i, last
    raise ValueError(f"No .subckt line found in {xspice_path}")


def sim_pinname_to_xspice(real: str) -> str:
    """Derive the XSPICE .subckt pin name from a netlist name.

    Mirrors ``spi2xspice.py``: prefix ``a_`` and flatten bus brackets,
    so ``clock_i`` -> ``a_clock_i`` and ``counter_value_o[0]`` ->
    ``a_counter_value_o_0_``.
    """
    return 'a_' + real.replace('[', '_').replace(']', '_')


def build_mapping(sym_pins: list[tuple[str, str | None]],
                  xspice_pins: list[str]) -> list[tuple[str, str]]:
    """Pair each sym pin (``(display, real)``) with an XSPICE pin.

    If every sym pin declares a real name (``sim_pinname``), pins are
    matched by name (order-independent). Otherwise the legacy positional
    scheme is used: VDD/VSS by the power name-map, all others by position.
    Returns a list of ``(display_name, xspice_pin)`` pairs in sym order.
    """
    if len(sym_pins) != len(xspice_pins):
        raise ValueError(
            f"Pin count mismatch: sym has {len(sym_pins)}, "
            f"xspice has {len(xspice_pins)} (after bus expansion)"
        )

    # Name mode: every symbol pin carries a sim_pinname property.
    if all(real is not None for _, real in sym_pins):
        xspice_set = set(xspice_pins)
        mapping = []
        for display, real in sym_pins:
            xp = sim_pinname_to_xspice(real)
            if xp not in xspice_set:
                raise ValueError(
                    f"Symbol pin '{display}' (sim_pinname={real}) expects "
                    f"XSPICE pin '{xp}', which is not in the .subckt. "
                    f"XSPICE pins: {sorted(xspice_pins)}"
                )
            mapping.append((display, xp))
        mapped = [xp for _, xp in mapping]
        if len(set(mapped)) != len(mapped):
            dupes = sorted({xp for xp in mapped if mapped.count(xp) > 1})
            raise ValueError(
                f"sim_pinname mapping is not one-to-one; "
                f"multiple symbol pins map to: {dupes}"
            )
        return mapping

    # Positional fallback (some pins lack sim_pinname).
    display_names = [d for d, _ in sym_pins]
    sym_power = {p for p in display_names if p in POWER_MAP}
    xspice_power = {p for p in xspice_pins if p in XSPICE_POWER}
    expected_xspice_power = {POWER_MAP[p] for p in sym_power}
    if expected_xspice_power != xspice_power:
        raise ValueError(
            f"Power pin mismatch: sym {sorted(sym_power)} maps to "
            f"{sorted(expected_xspice_power)}, but xspice has "
            f"{sorted(xspice_power)}"
        )

    signal_xspice = [p for p in xspice_pins if p not in XSPICE_POWER]
    sig_iter = iter(signal_xspice)

    mapping = []
    for display in display_names:
        if display in POWER_MAP:
            mapping.append((display, POWER_MAP[display]))
        else:
            mapping.append((display, next(sig_iter)))
    return mapping


def reorder_xspice(xspice_path: str, ordered_pins: list[str],
                   output_path: str) -> None:
    """Rewrite the XSPICE file with the .subckt pins reordered to match .sym."""
    with open(xspice_path, 'r') as f:
        lines = f.readlines()

    subckt_name, old_pins, first_idx, last_idx = parse_xspice_subckt(xspice_path)

    if set(ordered_pins) != set(old_pins):
        missing_in_new = set(old_pins) - set(ordered_pins)
        missing_in_old = set(ordered_pins) - set(old_pins)
        msg = "Pin set mismatch!\n"
        if missing_in_new:
            msg += f"  XSPICE pins not in mapping: {missing_in_new}\n"
        if missing_in_old:
            msg += f"  Mapped pins not in XSPICE: {missing_in_old}\n"
        raise ValueError(msg)

    max_width = 80
    header = f".subckt {subckt_name}"
    subckt_lines = []
    current = header
    for pin in ordered_pins:
        if len(current) + 1 + len(pin) > max_width:
            subckt_lines.append(current + "\n")
            current = "+ " + pin
        else:
            current += " " + pin
    subckt_lines.append(current + "\n")
    lines[first_idx:last_idx + 1] = subckt_lines

    with open(output_path, 'w') as f:
        f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Reorder XSPICE .subckt pins to match Xschem .sym pin order."
    )
    parser.add_argument("sym_file", help="Path to the Xschem .sym file")
    parser.add_argument("xspice_file", help="Path to the .xspice file")
    parser.add_argument("-o", "--output", default=None,
                        help="Output file path (default: overwrite xspice in-place)")
    args = parser.parse_args()

    output_path = args.output if args.output else args.xspice_file

    # 1. Parse pin lists (sym pins come back with bus ranges already expanded)
    sym_pins = parse_sym_pins(args.sym_file)
    subckt_name, xspice_pins, _, _ = parse_xspice_subckt(args.xspice_file)

    mode = "name" if sym_pins and all(r is not None for _, r in sym_pins) else "positional"
    print(f"Symbol file:  {args.sym_file}")
    print(f"XSPICE file:  {args.xspice_file}")
    print(f"Subcircuit:   {subckt_name}")
    print(f"Sym pins:     {len(sym_pins)}")
    print(f"XSPICE pins:  {len(xspice_pins)}")
    print(f"Match mode:   {mode}")

    # 2. Pair sym pins with xspice pins (by sim_pinname, or positionally)
    mapping = build_mapping(sym_pins, xspice_pins)
    ordered_xspice = [xp for _, xp in mapping]

    # 3. Show mapping
    print("\nPin mapping (sym -> xspice):")
    for sp, xp in mapping:
        old_idx = xspice_pins.index(xp)
        new_idx = ordered_xspice.index(xp)
        marker = "" if new_idx == old_idx else " *REORDERED*"
        print(f"  {sp:25s} -> {xp:25s}{marker}")

    # 4. Reorder and write
    reorder_xspice(args.xspice_file, ordered_xspice, output_path)
    print(f"\nReordered XSPICE written to: {output_path}")


if __name__ == "__main__":
    main()
