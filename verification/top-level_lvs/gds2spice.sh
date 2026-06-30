#!/bin/sh
# SPDX-FileCopyrightText: 2026 Harald Pretl
# Johannes Kepler University, Department for Integrated Circuits
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

ERR_FILE_NOT_FOUND=2
ERR_NO_PARAM=3
ERR_NO_VAR=4
ERR_NO_RESULT=5

if [ $# -eq 0 ]; then
	echo
	echo "GDS-to-SPICE netlist extraction (ICD@JKU)"
	echo
	echo "Usage: $0 [-f] [-o <output.spice>] -c <topcell> <layout.gds|.gds.gz>"
	echo
	echo "       -c Name of <topcell> in the GDS"
	echo "       -f Flatten the layout before extraction"
	echo "       -o Output SPICE netlist (default: <topcell>.ext.spice)"
	echo
	exit $ERR_NO_PARAM
fi

# defaults
RESDIR=$PWD
FLATTEN=0
TOPCELL=""
OUTPUT=""

# check PDK variables
if [ -z ${PDK_ROOT+x} ]; then
	echo "[ERROR] Variable PDK_ROOT not set!"
	exit $ERR_NO_VAR
fi

if [ -z ${PDK+x} ]; then
	echo "[ERROR] Variable PDK not set!"
	exit $ERR_NO_VAR
fi

PDKPATH="$PDK_ROOT/$PDK"

if [ ! -f "$PDKPATH/libs.tech/magic/$PDK.magicrc" ]; then
	echo "[ERROR] Magic RC file not found: $PDKPATH/libs.tech/magic/$PDK.magicrc"
	exit $ERR_FILE_NOT_FOUND
fi

# parse flags
while getopts "c:fo:" flag; do
	case $flag in
		c)
			TOPCELL="$OPTARG"
			;;
		f)
			FLATTEN=1
			;;
		o)
			OUTPUT="$OPTARG"
			;;
		*)
			;;
	esac
done
shift $((OPTIND-1))

# remaining argument is the GDS file
if [ $# -lt 1 ]; then
	echo "[ERROR] No GDS file specified!"
	exit $ERR_NO_PARAM
fi

CELL_LAY="$1"

if [ -z "$TOPCELL" ]; then
	echo "[ERROR] No topcell specified (-c)!"
	exit $ERR_NO_PARAM
fi

if [ ! -f "$CELL_LAY" ]; then
	echo "[ERROR] GDS file not found: $CELL_LAY"
	exit $ERR_FILE_NOT_FOUND
fi

# derive output path
if [ -z "$OUTPUT" ]; then
	OUTPUT="$RESDIR/$TOPCELL.ext.spice"
fi

# define paths
EXT_SCRIPT="$RESDIR/ext_${TOPCELL}.tcl"
CELL_LAY_ABS=$(realpath "$CELL_LAY")

# remove old output
[ -f "$OUTPUT" ] && rm -f "$OUTPUT"

# generate extract script for magic
{
	echo "crashbackups stop"
	echo "drc off"
	echo "gds read $CELL_LAY_ABS"
	echo "load $TOPCELL"
	[ $FLATTEN -eq 1 ] && echo "flatten"
	echo "select top cell"
	echo "extract path $RESDIR"
	echo "extract no capacitance"
	echo "extract no coupling"
	echo "extract no resistance"
	echo "extract no length"
	echo "extract all"
	echo "ext2spice lvs"
	echo "ext2spice -p $RESDIR -o $OUTPUT"
	echo "quit -noprompt"
} > "$EXT_SCRIPT"

# run magic
echo "[INFO] Extracting SPICE netlist from <$CELL_LAY> (topcell: $TOPCELL)..."
magic -dnull -noconsole \
	-rcfile "$PDKPATH/libs.tech/magic/$PDK.magicrc" \
	"$EXT_SCRIPT" \
	> /dev/null 2> /dev/null

# cleanup
rm -f "$EXT_SCRIPT"
rm -f *.ext

# check result
if [ ! -f "$OUTPUT" ]; then
	echo "[ERROR] No SPICE netlist produced!"
	exit $ERR_NO_RESULT
fi

echo "[DONE] SPICE netlist written to <$OUTPUT>."
