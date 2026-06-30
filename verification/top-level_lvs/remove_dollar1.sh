#!/bin/sh
# SPDX-FileCopyrightText: 2026 Harald Pretl
# Johannes Kepler University, Department for Integrated Circuits
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# Remove '$1' from subcircuit names (and all references) in a SPICE netlist.
# Usage: ./remove_dollar1.sh input.spc [output.spc]
#   If no output file is given, the input file is modified in-place.

if [ -z "$1" ]; then
    echo "Usage: $0 input.spc [output.spc]" >&2
    exit 1
fi

INPUT="$1"
OUTPUT="${2:-}"

if [ -n "$OUTPUT" ]; then
    sed 's/\$1//g' "$INPUT" > "$OUTPUT"
else
    sed -i '' 's/\$1//g' "$INPUT"
fi
