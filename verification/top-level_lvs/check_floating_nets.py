#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025-2026 The TinyWhisper Team
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

"""Check for floating (unconnected) nets and unconnected ports in a SPICE netlist.

Traced hierarchically through subcircuit instances.

Checks performed:
  1. Floating nets:  internal nets connected to only 1 device pin
  2. Unconnected ports (internal): subcircuit ports with no device connection inside
  3. Unconnected ports (external): instance ports wired to a floating net in the parent,
     reported with the full hierarchical instance path

Usage:
    python check_floating_nets.py <netlist.spice> [--top <subckt_name>] [--verbose]
"""

import argparse
import sys
from collections import defaultdict

# Primitive device prefixes (SPICE convention: first letter of instance name)
# These are terminals, not subcircuit calls.
PRIMITIVE_PREFIXES = set("RrCcLlDdMmQqJjKkEeFfGgHhVvIi")

# Known primitive model names (IHP SG13G2 PDK)
KNOWN_PRIMITIVES = {
    "sg13_lv_nmos", "sg13_lv_pmos", "sg13_hv_nmos", "sg13_hv_pmos",
    "dantenna", "dpantenna", "dnantenna",
    "sg13_lv_nmos_dss", "sg13_lv_pmos_dss",
    "npn13G2", "npn13G2L", "npn13G2V",
    "pnpMPA", "rsil", "rhigh", "rppd", "cap_cmim",
    "SG13_MOSCAP_1", "SG13_MOSCAP_2",
    "inductor2", "inductor3",
}


class Subcircuit:
    """Represents a parsed .subckt definition."""
    __slots__ = ("name", "ports", "nets", "instances")

    def __init__(self, name, ports):
        self.name = name
        self.ports = list(ports)
        # net_name -> set of (instance_name, pin_index) connections
        self.nets = defaultdict(set)
        self.instances = []  # (inst_name, conn_nets, subckt_or_model_name)

    def add_instance(self, inst_name, conn_nets, model_name):
        self.instances.append((inst_name, conn_nets, model_name))
        for i, net in enumerate(conn_nets):
            self.nets[net].add((inst_name, i))

    def mark_ports_connected(self):
        """Ports are connected to the outside world by definition."""
        for p in self.ports:
            self.nets[p].add(("__PORT__", 0))


def parse_netlist(filepath):
    """Parse a SPICE netlist file and return a dict of subcircuit definitions."""
    subcircuits = {}
    current_subckt = None
    continuation_line = ""

    with open(filepath, "r") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n\r")

            # Handle continuation lines (start with +)
            if line.startswith("+"):
                continuation_line += " " + line[1:].strip()
                continue

            # Process any accumulated line
            if continuation_line:
                _process_line(continuation_line, current_subckt, subcircuits)
                continuation_line = ""

            stripped = line.strip()
            if not stripped or stripped.startswith("*"):
                continue

            continuation_line = stripped

    # Process last accumulated line
    if continuation_line:
        _process_line(continuation_line, current_subckt, subcircuits)

    return subcircuits


def _process_line(line, current_subckt, subcircuits):
    """Process a single logical line (with continuations merged)."""
    lower = line.lower()

    # .subckt definition
    if lower.startswith(".subckt"):
        tokens = line.split()
        name = tokens[1]
        ports = tokens[2:]
        subckt = Subcircuit(name, ports)
        subckt.mark_ports_connected()
        subcircuits[name] = subckt
        # Update the mutable reference via dict
        subcircuits["__current__"] = subckt
        return

    # .ends
    if lower.startswith(".ends"):
        subcircuits.pop("__current__", None)
        return

    current_subckt = subcircuits.get("__current__")
    if current_subckt is None:
        return

    # Skip directives
    if lower.startswith("."):
        return

    tokens = line.split()
    if not tokens:
        return

    inst_name = tokens[0]

    # Subcircuit instance (Xname ...)
    if inst_name[0] in ("X", "x"):
        _parse_x_instance(tokens, current_subckt, subcircuits)
    elif inst_name[0] in PRIMITIVE_PREFIXES:
        _parse_primitive(tokens, current_subckt)


def _parse_x_instance(tokens, current_subckt, subcircuits):
    """Parse an X (subcircuit) instance line."""
    inst_name = tokens[0]
    # Find the subcircuit/model name: it's the last token before any key=value params
    # Format: Xname net1 net2 ... netN subckt_name [param=val ...]
    conn_nets = []
    model_name = None

    for i in range(1, len(tokens)):
        tok = tokens[i]
        if "=" in tok:
            # This and everything after are parameters
            break
        conn_nets.append(tok)

    # The last net token is actually the model/subcircuit name
    if conn_nets:
        model_name = conn_nets.pop()

    if model_name:
        current_subckt.add_instance(inst_name, conn_nets, model_name)


def _parse_primitive(tokens, current_subckt):
    """Parse a primitive device instance (M, R, C, etc.)."""
    inst_name = tokens[0]
    first_char = inst_name[0].upper()

    # Determine how many net tokens based on device type
    # MOSFET (M): 4 nets (D G S B), then model, then params
    # Resistor (R): 2 nets, then value/model
    # Capacitor (C): 2 nets, then value/model
    # Diode (D): 2 nets, then model
    # BJT (Q): 3-4 nets, then model
    # Inductor (L): 2 nets, then value
    # Voltage/Current source (V, I): 2 nets

    conn_nets = []
    for i in range(1, len(tokens)):
        tok = tokens[i]
        if "=" in tok:
            break
        # Check if it looks like a number (value for R, C, L)
        try:
            _parse_spice_value(tok)
            break
        except ValueError:
            pass
        # Check if it's a known model name
        if tok in KNOWN_PRIMITIVES:
            break
        conn_nets.append(tok)

    current_subckt.add_instance(inst_name, conn_nets, first_char + "_primitive")


def _parse_spice_value(s):
    """Try to parse a SPICE numeric value. Raises ValueError if not a number."""
    suffixes = {
        "t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3,
        "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18,
    }
    s_lower = s.lower().rstrip()
    for suf in suffixes:
        if s_lower.endswith(suf):
            float(s_lower[: -len(suf)])
            return
    float(s)


def find_floating_nets(subcircuits, subckt_name, hierarchy_path="", visited=None):
    """
    Find floating nets and unconnected ports in a subcircuit, recursing
    into sub-instances.

    Checks:
      - Internal floating nets (connected to <= 1 device pin)
      - Ports with no internal device connection
      - Instance ports wired to floating nets in the parent (hierarchical trace)

    Returns a list of (hierarchy_path, message, count, kind) tuples.
    """
    if visited is None:
        visited = set()

    if subckt_name in visited:
        return []
    visited.add(subckt_name)

    subckt = subcircuits.get(subckt_name)
    if subckt is None:
        return []

    results = []
    port_set = set(subckt.ports)
    prefix = f"{hierarchy_path}/{subckt_name}" if hierarchy_path else subckt_name

    # --- Check 1 & 2: floating nets and internally unconnected ports ---
    # Pre-compute device connection counts per net
    net_device_count = {}  # net -> number of device connections (excl. __PORT__)
    for net_name, connections in subckt.nets.items():
        device_conns = sum(1 for c in connections if c[0] != "__PORT__")
        net_device_count[net_name] = device_conns

    for net_name in subckt.nets:
        dc = net_device_count[net_name]
        is_port = net_name in port_set

        if is_port:
            if dc == 0:
                results.append((prefix, net_name, 0, "port_internal"))
        else:
            if dc <= 1:
                results.append((prefix, net_name, dc, "floating"))

    # --- Check 3: instance ports wired to floating/single-use nets ---
    for inst_name, conn_nets, model_name in subckt.instances:
        child_subckt = subcircuits.get(model_name)
        if child_subckt is None:
            continue
        child_ports = child_subckt.ports
        for pin_idx, net_name in enumerate(conn_nets):
            if pin_idx >= len(child_ports):
                break
            port_name = child_ports[pin_idx]
            is_port = net_name in port_set
            total_conns = net_device_count.get(net_name, 0)
            if is_port:
                # Net is a port of the current subcircuit — it connects upward,
                # so don't flag it here.
                continue
            # Internal net: if it connects to only this one instance pin, the
            # child port is effectively unconnected from the parent side.
            if total_conns <= 1:
                inst_path = f"{prefix}/{inst_name}"
                results.append(
                    (inst_path, port_name, total_conns, "port_external")
                )

    # --- Recurse into sub-instances (once per unique model) ---
    seen_models = set()
    for inst_name, conn_nets, model_name in subckt.instances:
        if model_name in subcircuits and model_name not in seen_models:
            seen_models.add(model_name)
            sub_results = find_floating_nets(
                subcircuits, model_name, prefix, visited.copy()
            )
            results.extend(sub_results)

    return results


def find_top_subcircuit(subcircuits):
    """Find the top-level subcircuit (last defined, or largest)."""
    all_names = [k for k in subcircuits if k != "__current__"]
    if not all_names:
        return None

    # Heuristic: the last subcircuit defined is usually the top
    # But also check which subcircuits are NOT instantiated by others
    instantiated = set()
    for name in all_names:
        subckt = subcircuits[name]
        for _, _, model in subckt.instances:
            instantiated.add(model)

    top_candidates = [n for n in all_names if n not in instantiated]
    if top_candidates:
        # Return the one with the most instances (likely top)
        return max(top_candidates, key=lambda n: len(subcircuits[n].instances))

    return all_names[-1]


def find_removable_ports(subcircuits, top_name):
    """
    Iteratively find all PORT-INT ports (ports with no internal device connection)
    across the hierarchy reachable from top_name, handling cascading: removing a
    port from a child may cause the parent net to become floating, which may turn
    a parent port into PORT-INT as well.

    Returns: dict  subckt_name -> set of port indices to remove
    """
    # Collect subcircuits reachable from top
    reachable = set()
    _collect_reachable(subcircuits, top_name, reachable)

    # Work on a copy so we don't mutate the original parsed data
    subs = {}
    for name in reachable:
        subckt = subcircuits[name]
        s = Subcircuit(name, subckt.ports[:])
        s.nets = defaultdict(set)
        for net, conns in subckt.nets.items():
            s.nets[net] = set(conns)
        s.instances = list(subckt.instances)
        subs[name] = s

    removal_map = defaultdict(set)  # subckt_name -> set of port indices

    changed = True
    while changed:
        changed = False
        for name, subckt in subs.items():
            # Build port_name -> index map once per iteration
            port_index = {p: i for i, p in enumerate(subckt.ports)}
            for port_name, port_idx in port_index.items():
                if port_idx in removal_map.get(name, set()):
                    continue  # already marked for removal
                conns = subckt.nets.get(port_name, set())
                device_conns = sum(1 for c in conns if c[0] != "__PORT__")
                if device_conns == 0:
                    removal_map[name].add(port_idx)
                    changed = True
                    # Now cascade: in every parent, remove the connection
                    # that this port contributed
                    _cascade_port_removal(subs, name, port_idx)

    return {k: v for k, v in removal_map.items() if v}


def _collect_reachable(subcircuits, name, visited):
    """Recursively collect all subcircuit names reachable from 'name'."""
    if name in visited or name not in subcircuits:
        return
    visited.add(name)
    for _, _, model_name in subcircuits[name].instances:
        _collect_reachable(subcircuits, model_name, visited)


def _cascade_port_removal(subcircuits, child_name, port_idx):
    """
    When a port is removed from child_name at port_idx, update all parent
    subcircuits: remove the net connection from instances of child_name.
    """
    for parent_name, parent in subcircuits.items():
        for inst_name, conn_nets, model_name in parent.instances:
            if model_name != child_name:
                continue
            if port_idx >= len(conn_nets):
                continue
            net_name = conn_nets[port_idx]
            # Remove this (inst_name, port_idx) from the net's connections
            parent.nets[net_name].discard((inst_name, port_idx))


def rewrite_netlist(input_path, output_path, subcircuits, removal_map):
    """
    Read the input netlist and write a new version with PORT-INT ports removed
    from .subckt definitions and the corresponding pins removed from X instances.

    removal_map: subckt_name -> set of port indices to remove
    """
    # Build a lookup: for X instances, we need to know the model name to know
    # which pin indices to drop. We re-parse each line on the fly.

    # Also build reverse map: which subcircuit names have ports to remove
    affected_subckts = set(removal_map.keys())

    # Track which subcircuit we are currently inside (for .ends matching)
    current_subckt_name = None

    lines_out = []
    pending_lines = []  # raw lines accumulating a logical line
    logical_start_idx = 0

    with open(input_path, "r") as f:
        raw_lines = f.readlines()

    i = 0
    while i < len(raw_lines):
        line = raw_lines[i].rstrip("\n\r")

        # Collect continuation lines
        logical_line = line
        cont_count = 0
        while i + 1 + cont_count < len(raw_lines) and raw_lines[i + 1 + cont_count].startswith("+"):
            logical_line += " " + raw_lines[i + 1 + cont_count].rstrip("\n\r")[1:].strip()
            cont_count += 1

        raw_span = [raw_lines[j] for j in range(i, i + 1 + cont_count)]
        i += 1 + cont_count

        stripped = logical_line.strip()
        lower = stripped.lower()

        # --- .subckt line ---
        if lower.startswith(".subckt"):
            tokens = stripped.split()
            subckt_name = tokens[1]
            current_subckt_name = subckt_name
            if subckt_name in removal_map:
                indices_to_remove = removal_map[subckt_name]
                # ports start at tokens[2:]
                new_tokens = [tokens[0], tokens[1]]
                for pidx, port in enumerate(tokens[2:]):
                    if pidx not in indices_to_remove:
                        new_tokens.append(port)
                new_line = _format_spice_line(" ".join(new_tokens))
                lines_out.append(new_line)
            else:
                lines_out.extend(raw_span)
            continue

        # --- .ends line ---
        if lower.startswith(".ends"):
            current_subckt_name = None
            lines_out.extend(raw_span)
            continue

        # --- X instance line ---
        if stripped and stripped[0] in ("X", "x") and current_subckt_name is not None:
            tokens = stripped.split()
            inst_name = tokens[0]
            # Parse: Xname net1 ... netN model [key=val ...]
            conn_and_rest = []
            params_start = None
            for ti in range(1, len(tokens)):
                if "=" in tokens[ti]:
                    params_start = ti
                    break
                conn_and_rest.append(tokens[ti])

            if conn_and_rest:
                model_name = conn_and_rest[-1]
                conn_nets = conn_and_rest[:-1]
                params = tokens[params_start:] if params_start else []

                if model_name in removal_map:
                    indices_to_remove = removal_map[model_name]
                    new_conn = []
                    for pidx, net in enumerate(conn_nets):
                        if pidx not in indices_to_remove:
                            new_conn.append(net)
                    new_tokens = [inst_name] + new_conn + [model_name] + params
                    new_line = _format_spice_line(" ".join(new_tokens))
                    lines_out.append(new_line)
                    continue

            lines_out.extend(raw_span)
            continue

        # --- everything else: pass through ---
        lines_out.extend(raw_span)

    with open(output_path, "w") as f:
        f.writelines(lines_out)


def _format_spice_line(line, max_width=120):
    """Format a long SPICE line with continuation lines."""
    if len(line) <= max_width:
        return line + "\n"
    tokens = line.split()
    result = tokens[0]
    for tok in tokens[1:]:
        if len(result.split("\n")[-1]) + 1 + len(tok) > max_width:
            result += "\n+ " + tok
        else:
            result += " " + tok
    return result + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Find floating (unconnected) nets in a SPICE netlist, traced hierarchically."
    )
    parser.add_argument("netlist", help="Path to the SPICE netlist file")
    parser.add_argument(
        "--top", default=None,
        help="Name of the top-level subcircuit (auto-detected if omitted)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print detailed information during parsing"
    )
    parser.add_argument(
        "--no-ports", action="store_true",
        help="Suppress unconnected port reports (only show floating nets)"
    )
    parser.add_argument(
        "--max-conns", type=int, default=1,
        help="Report nets with at most this many connections (default: 1)"
    )
    parser.add_argument(
        "--fix-ports", action="store_true",
        help="Remove PORT-INT ports from subcircuit definitions and instances, write to --output"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output file path for --fix-ports (required when --fix-ports is used)"
    )
    args = parser.parse_args()

    print(f"Parsing {args.netlist} ...")
    subcircuits = parse_netlist(args.netlist)

    # Remove internal tracking key
    subcircuits.pop("__current__", None)

    print(f"Found {len(subcircuits)} subcircuit definitions.")

    if args.verbose:
        for name, subckt in subcircuits.items():
            print(f"  {name}: {len(subckt.ports)} ports, "
                  f"{len(subckt.instances)} instances, "
                  f"{len(subckt.nets)} nets")

    top = args.top or find_top_subcircuit(subcircuits)
    if top is None:
        print("ERROR: No subcircuits found in netlist.", file=sys.stderr)
        sys.exit(1)

    print(f"Top-level subcircuit: {top}")
    print(f"Checking for nets with <= {args.max_conns} connection(s) ...\n")

    results = find_floating_nets(subcircuits, top)

    # Filter results
    filtered = []
    for hierarchy, name, count, kind in results:
        if args.no_ports and kind in ("port_internal", "port_external"):
            continue
        if kind == "floating" and count > args.max_conns:
            continue
        filtered.append((hierarchy, name, count, kind))

    # Sort by hierarchy, then kind (floating < port_external < port_internal), then name
    kind_order = {"floating": 0, "port_external": 1, "port_internal": 2}
    filtered.sort(key=lambda x: (x[0], kind_order.get(x[3], 9), x[1]))

    if not filtered:
        print("No issues found.")
    else:
        # Group by hierarchy level
        current_hier = None
        floating_count = 0
        port_int_count = 0
        port_ext_count = 0
        for hierarchy, name, count, kind in filtered:
            if hierarchy != current_hier:
                current_hier = hierarchy
                print(f"--- {hierarchy} ---")
            label = f"[{count} conn]"
            if kind == "port_internal":
                print(f"  PORT-INT  {label}  {name}  (port with no internal connection)")
                port_int_count += 1
            elif kind == "port_external":
                print(f"  PORT-EXT  {label}  .{name}  (instance port wired to floating net)")
                port_ext_count += 1
            else:
                print(f"  FLOAT     {label}  {name}")
                floating_count += 1

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  {floating_count:6d}  floating net(s)")
        print(f"  {port_int_count:6d}  internally unconnected port(s)")
        print(f"  {port_ext_count:6d}  externally unconnected port(s) (instance port -> floating net)")
        print(f"  {floating_count + port_int_count + port_ext_count:6d}  total issue(s)")
        print(f"Checked {len(subcircuits)} subcircuit definitions hierarchically.")

    # --- Fix mode: remove PORT-INT ports ---
    if args.fix_ports:
        if not args.output:
            print("ERROR: --output is required when using --fix-ports.", file=sys.stderr)
            sys.exit(1)

        removal_map = find_removable_ports(subcircuits, top)

        if not removal_map:
            print("\nNo PORT-INT ports to remove.")
        else:
            total_removed = sum(len(v) for v in removal_map.values())
            print(f"\nRemoving {total_removed} PORT-INT port(s) from "
                  f"{len(removal_map)} subcircuit(s):")
            for sname in sorted(removal_map):
                subckt = subcircuits[sname]
                removed_names = [subckt.ports[idx] for idx in sorted(removal_map[sname])]
                print(f"  {sname}: {', '.join(removed_names)}")

        rewrite_netlist(args.netlist, args.output, subcircuits, removal_map)
        print(f"\nFixed netlist written to: {args.output}")


if __name__ == "__main__":
    main()
