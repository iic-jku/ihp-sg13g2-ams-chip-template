#!/bin/bash

# SPDX-FileCopyrightText: 2025-2026 The Chip Team
# SPDX-License-Identifier: Apache-2.0

# =====================================================
# Author: Simon Dorrer
# Last Modified: 05.12.2024
# Description: This .sh file takes a synthesized gate-level Verilog file (e.g. 1_synth for ORFS) and converts it into a .xspice file for the IHP SG13G2 PDK.
# This .xspice file can be included in Xschem and simulated with Ngspice + Xyce.
# The conversion is done with scripts from qflow (vlog2Verilog, vlog2Spice and spi2xspice.py).
# =====================================================

set -e -x

cd $(dirname "$0")

name=$1

ORFS=${ORFS:-../orfs/flow/results/ihp-sg13g2/${name}/base}
SRC_FOLDER=${SRC_FOLDER:-.}

# Create directory
mkdir -p "$name"

# Convert Verilog (.v) file to Vlog (.vp) file
vlog2Verilog "$ORFS"/1_2_yosys.v -o "$name"/"$name".vp -l $PDKPATH/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef -v "VPWR,VPB" -g "VGND,VNB"

# Convert Vlog (.vp) file to spice (.spi or .spice) file
vlog2Spice "$name"/"$name".vp -l $PDKPATH/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice -o "$name"/"$name".spice

# Convert spice (.spi or .spice) file to Xspice (.xspice) file:
python3 spi2xspice.py $PDKPATH/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p50V_25C.lib -io_time=500p -time=50p -idelay=5p -odelay=50p -cload=250f "$name"/"$name".spice "$name"/"$name".xspice

# Finish
echo "------ The synthesized gate-level Verilog file was successfully converted into a .xspice file! ------"