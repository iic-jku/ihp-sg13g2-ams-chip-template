# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Lattice iCE40: Yosys (synth_ice40) -> nextpnr-ice40 -> icepack.
# LOAD_CMD/FLASH_CMD are per-board: iCE40 boards differ in programmer (iceprog, dfu-util).

# Yosys synthesis pass and its options
# Override with: make <target> TARGET=<synth_pass> SYNTH_OPTS=<options>
TARGET     ?= synth_ice40
SYNTH_OPTS ?= -dsp -spram

# nextpnr device and package
# Override with: make <target> ICE40_DEVICE=<options>
ICE40_DEVICE ?= --up5k --package sg48

# Place-and-route options, output file and commands
# Override with: make <target> PNR_ARGS=<options> PNR_OUT=<file> PNR_CMD=<command> PNR_GUI_CMD=<command>
PNR_ARGS    ?= $(ICE40_DEVICE) --pcf-allow-unconstrained
PNR_OUT     ?= $(BUILD_DIR)/$(TOP).asc
PNR_CMD     ?= nextpnr-ice40 $(PNR_ARGS) --json $(BUILD_DIR)/$(TOP).json --pcf $(PCF_FILE) --asc $(PNR_OUT)
PNR_GUI_CMD ?= nextpnr-ice40 $(PNR_ARGS) --json $(BUILD_DIR)/$(TOP).json --pcf $(PCF_FILE) --asc $(PNR_OUT) --gui

# Bitstream file and the command that packs it
# Override with: make <target> BITSTREAM=<file> PACK_CMD=<command>
BITSTREAM ?= $(BUILD_DIR)/$(TOP).bin
PACK_CMD  ?= icepack $(PNR_OUT) $(BITSTREAM)
