# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Drop the pins of a PEX symbol that the extracted netlist has no port for.

# A chip top-level symbol draws one pin per bond pad, but a `.subckt` port list holds one entry
# per net: pads that share a net share a port, and two supplies that are shorted in the layout
# come out of the extraction as a single node. The PEX symbol therefore keeps the first pin of
# every name, drops the repeats, and drops the pins named with --merged. Only the pin boxes go,
# the text labels stay, so the generated symbol still reads as the full pad ring.

import argparse
import os
import re
import sys

# B 5 <x1> <y1> <x2> <y2> {name=<pin> dir=<dir> ...}
PIN_PATTERN = re.compile(r'^B\s+5\s+.*\{name=(\S+)\s+dir=\w+[^}]*\}')


def prune(lines, merged):
    """Return (kept_lines, dropped_merged, dropped_repeated) for one symbol file."""
    kept, seen, dropped_merged, dropped_repeated = [], set(), [], []
    for line in lines:
        match = PIN_PATTERN.match(line.strip())
        if match:
            name = match.group(1)
            if name in merged:
                dropped_merged.append(name)
                continue
            if name in seen:
                dropped_repeated.append(name)
                continue
            seen.add(name)
        kept.append(line)
    return kept, dropped_merged, dropped_repeated


def main():
    parser = argparse.ArgumentParser(
        description="Drop the pins of a PEX symbol that the extracted netlist has no port for."
    )
    parser.add_argument("sym_file", help="Path to the generated <CELL>_pex.sym")
    parser.add_argument("-m", "--merged", nargs="*", default=[],
                        help="Pins that the extraction merges into another node (e.g. IOVSS)")
    args = parser.parse_args()

    if not os.path.isfile(args.sym_file):
        print(f"[ERROR] No symbol {args.sym_file}.", file=sys.stderr)
        return 1

    with open(args.sym_file, encoding="utf-8", newline="") as handle:
        lines = handle.readlines()

    kept, dropped_merged, dropped_repeated = prune(lines, set(args.merged))

    name = os.path.basename(args.sym_file)
    for pin in sorted(set(dropped_merged)):
        count = dropped_merged.count(pin)
        print(f"Dropped {count} pin(s) '{pin}' from {name}, "
              f"the extraction merges it into another node.")
    for pin in sorted(set(dropped_repeated)):
        count = dropped_repeated.count(pin)
        print(f"Dropped {count} repeated pin(s) '{pin}' from {name}, "
              f"the {count + 1} pads share one port.")
    if dropped_merged or dropped_repeated:
        with open(args.sym_file, "w", encoding="utf-8", newline="") as handle:
            handle.writelines(kept)
    return 0


if __name__ == "__main__":
    sys.exit(main())
