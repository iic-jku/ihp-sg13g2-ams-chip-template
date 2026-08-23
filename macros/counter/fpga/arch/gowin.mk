# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Gowin: Yosys (synth_gowin) -> nextpnr-himbaechel -> gowin_pack.

TARGET     ?= synth_gowin
SYNTH_OPTS ?=

GOWIN_DEVICE ?= GW1NR-LV9QN88PC6/I5
GOWIN_FAMILY ?= GW1N-9C

PNR_ARGS    ?= --device $(GOWIN_DEVICE) --vopt family=$(GOWIN_FAMILY) --vopt cst=$(PCF_FILE)
PNR_OUT     ?= $(BUILD_DIR)/$(TOP)_pnr.json
PNR_CMD     ?= nextpnr-himbaechel $(PNR_ARGS) --json $(BUILD_DIR)/$(TOP).json --write $(PNR_OUT)
PNR_GUI_CMD ?= nextpnr-himbaechel $(PNR_ARGS) --json $(BUILD_DIR)/$(TOP).json --write $(PNR_OUT) --gui

BITSTREAM ?= $(BUILD_DIR)/$(TOP).fs
PACK_CMD  ?= gowin_pack -d $(GOWIN_FAMILY) -o $(BITSTREAM) $(PNR_OUT)
LOAD_CMD  ?= openFPGALoader --board=$(OPENFPGALOADER_BOARD) $(OPENFPGALOADER_FLAGS) $(BITSTREAM)
FLASH_CMD ?= openFPGALoader --board=$(OPENFPGALOADER_BOARD) $(OPENFPGALOADER_FLAGS) --write-flash $(BITSTREAM)
