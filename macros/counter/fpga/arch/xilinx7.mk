# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Xilinx 7-series: Yosys (synth_xilinx) -> nextpnr-xilinx -> fasm2frames -> xc7frames2bit.
#
# The toolchain is openXC7 (nextpnr-xilinx + prjxray), shipped in IIC-OSIC-TOOLS,
# which also exports NEXTPNR_XILINX_PYTHON_DIR and PRJXRAY_DB_DIR.

# synth_xilinx's flags do not fit the "$(TARGET) $(SYNTH_OPTS) -top $(TOP)" shape of fpga.mk.
SYNTH_CMD ?= yosys -DFPGA -p "synth_xilinx -flatten -abc9 -arch xc7 -top $(TOP); write_json $(BUILD_DIR)/$(TOP).json;" $(MODULES_SYNTH)

# Generated once per package, then kept. Not removed by `clean`, since building it
# takes minutes (bbaexport runs on CPython, pypy is not in the container) and it
# only depends on the part, not on the design.
$(CHIPDB):
	python3 $${NEXTPNR_XILINX_PYTHON_DIR}/bbaexport.py --device $(PART) --bba $(TOP).bba
	bbasm -l $(TOP).bba $(CHIPDB)
	rm -f $(TOP).bba

# Place-and-route emits FASM, not a bitstream config, so two more steps turn it into one.
PNR_DEPS ?= $(CHIPDB)
PNR_OUT  ?= $(BUILD_DIR)/$(TOP).frames
PNR_CMD  ?= nextpnr-xilinx --chipdb $(CHIPDB) --xdc $(PCF_FILE) --json $(BUILD_DIR)/$(TOP).json --fasm $(BUILD_DIR)/$(TOP).fasm; \
	fasm2frames --part $(PART) --db-root $${PRJXRAY_DB_DIR}/$(XRAY_FAMILY) $(BUILD_DIR)/$(TOP).fasm > $(PNR_OUT)

# PNR_CMD is a two-step pipeline, so there is no single command to hand a --gui flag to.
PNR_GUI_CMD ?=

BITSTREAM ?= $(BUILD_DIR)/$(TOP).bit
PACK_CMD  ?= xc7frames2bit --part_file $${PRJXRAY_DB_DIR}/$(XRAY_FAMILY)/$(PART)/part.yaml --part_name $(PART) --frm_file $(PNR_OUT) --output_file $(BITSTREAM)
LOAD_CMD  ?= openFPGALoader --board=$(OPENFPGALOADER_BOARD) $(OPENFPGALOADER_FLAGS) $(BITSTREAM)
FLASH_CMD ?= openFPGALoader --board=$(OPENFPGALOADER_BOARD) $(OPENFPGALOADER_FLAGS) --write-flash $(BITSTREAM)
