# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Lattice ECP5: Yosys (synth_ecp5) -> nextpnr-ecp5 -> ecppack.

TARGET     ?= synth_ecp5
SYNTH_OPTS ?=

ECP5_DEVICE ?= --85k --package CABGA381

PNR_ARGS    ?= $(ECP5_DEVICE) --lpf-allow-unconstrained
PNR_OUT     ?= $(BUILD_DIR)/$(TOP).config
PNR_CMD     ?= nextpnr-ecp5 $(PNR_ARGS) --json $(BUILD_DIR)/$(TOP).json --lpf $(PCF_FILE) --textcfg $(PNR_OUT)
PNR_GUI_CMD ?= nextpnr-ecp5 $(PNR_ARGS) --json $(BUILD_DIR)/$(TOP).json --lpf $(PCF_FILE) --textcfg $(PNR_OUT) --gui

BITSTREAM ?= $(BUILD_DIR)/$(TOP).bit
PACK_CMD  ?= ecppack $(PNR_OUT) $(BITSTREAM) --compress
LOAD_CMD  ?= openFPGALoader --board=$(OPENFPGALOADER_BOARD) $(OPENFPGALOADER_FLAGS) $(BITSTREAM)
FLASH_CMD ?= openFPGALoader --board=$(OPENFPGALOADER_BOARD) $(OPENFPGALOADER_FLAGS) --write-flash $(BITSTREAM)
