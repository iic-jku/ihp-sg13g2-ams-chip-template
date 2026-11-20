# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Lattice ECP5: Yosys (synth_ecp5) -> nextpnr-ecp5 -> ecppack.

# Yosys synthesis pass and its options
# Override with: make <target> TARGET=<synth_pass> SYNTH_OPTS=<options>
TARGET     ?= synth_ecp5
SYNTH_OPTS ?=

# nextpnr device and package
# Override with: make <target> ECP5_DEVICE=<options>
ECP5_DEVICE ?= --85k --package CABGA381

# Place-and-route options, output file and commands
# Override with: make <target> PNR_ARGS=<options> PNR_OUT=<file> PNR_CMD=<command> PNR_GUI_CMD=<command>
PNR_ARGS    ?= $(ECP5_DEVICE) --lpf-allow-unconstrained
PNR_OUT     ?= $(BUILD_DIR)/$(TOP).config
PNR_CMD     ?= nextpnr-ecp5 $(PNR_ARGS) --json $(BUILD_DIR)/$(TOP).json --lpf $(PCF_FILE) --textcfg $(PNR_OUT)
PNR_GUI_CMD ?= nextpnr-ecp5 $(PNR_ARGS) --json $(BUILD_DIR)/$(TOP).json --lpf $(PCF_FILE) --textcfg $(PNR_OUT) --gui

# Bitstream file and the commands that pack, load and flash it
# Override with: make <target> BITSTREAM=<file> PACK_CMD=<command> LOAD_CMD=<command> FLASH_CMD=<command>
BITSTREAM ?= $(BUILD_DIR)/$(TOP).bit
PACK_CMD  ?= ecppack $(PNR_OUT) $(BITSTREAM) --compress
LOAD_CMD  ?= openFPGALoader --board=$(OPENFPGALOADER_BOARD) $(OPENFPGALOADER_FLAGS) $(BITSTREAM)
FLASH_CMD ?= openFPGALoader --board=$(OPENFPGALOADER_BOARD) $(OPENFPGALOADER_FLAGS) --write-flash $(BITSTREAM)
