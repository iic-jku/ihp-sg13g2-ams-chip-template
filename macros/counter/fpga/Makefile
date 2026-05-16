# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Variables
TOP = counter_top
TARGET ?= synth_ice40
CELL ?= $(TOP)

.DEFAULT_GOAL := help

# Folder structure
SRC_DIR     := ../rtl
PCF_FILE    := pico-ice.pcf

# Variables for linting and synthesis targets
# constants.sv defines the `COUNTER_MAX_DEFAULT / `CLK_FREQ_DEFAULT macros and must
# compile before any module that references them, so it is the first entry in MODULES_SYNTH
# (Yosys 0.64 cannot parse `import pkg::*` in a module header — see rtl/constants.sv).
MODULES_SYNTH := \
	$(SRC_DIR)/constants.sv \
	$(SRC_DIR)/counter.sv \
	$(SRC_DIR)/counter_top.sv

# Source files for lint-verilog: full module list for TOP, single-file (with constants.sv, auto-detecting .sv/.v) otherwise
_LINT_SRCS = $(if $(filter $(CELL),$(TOP)),$(MODULES_SYNTH),$(SRC_DIR)/constants.sv $(or $(wildcard $(SRC_DIR)/$(CELL).sv),$(SRC_DIR)/$(CELL).v))


# Help Target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
.PHONY: help
# ================================================================================================


# Clean Target
clean: ## Remove generated files
	rm -f test_pre *.vcd $(TOP).json* $(TOP).asc $(TOP).bin $(TOP).pdf $(TOP).svg
	rm -f $(TOP)_generic.json* $(TOP)_generic.pdf $(TOP)_generic.svg
	rm -f $(TOP)_yosys.svg $(TOP)_yosys.dot $(TOP)_generic_yosys.svg $(TOP)_generic_yosys.dot
	rm -rf $(TOP) $(TOP)_basic $(TOP)_cover
.PHONY: clean
# ================================================================================================


# Linter Targets
lint-verilog: ## Lint Verilog source files with Verilator (usage: make lint-verilog [CELL=<cellname>])
	verilator --lint-only -I"$(SRC_DIR)" $(_LINT_SRCS)
.PHONY: lint-verilog

lint-verilog-all: ## Lint all Verilog source files (counter, counter_top)
	$(MAKE) lint-verilog CELL=counter
	$(MAKE) lint-verilog
.PHONY: lint-verilog-all
# ================================================================================================


# Synthesis Targets
synthesis: $(TOP).json ## Run technology-mapped synthesis for iCE40
.PHONY: synthesis

$(TOP).json: $(MODULES_SYNTH)
	yosys -DFPGA -p '$(TARGET) -dsp -spram -top $(TOP); write_json $(TOP).json;' $(MODULES_SYNTH)

synthesis_generic: $(TOP)_generic.json ## Run generic synthesis and generate Yosys graph
.PHONY: synthesis_generic

$(TOP)_generic.json: $(MODULES_SYNTH)
	yosys -p 'hierarchy -top $(TOP); proc; write_json $(TOP)_generic.json; show -format svg -prefix $(TOP)_generic_yosys $(TOP);' $(MODULES_SYNTH)
# ================================================================================================


# Visualization Targets
visualize_ice40: $(TOP).pdf ## Generate visualization PDF from iCE40 netlist
.PHONY: visualize_ice40

$(TOP).pdf: $(TOP).json
	sed -i -e 's/inout/output/g' $(TOP).json
	netlistsvg $(TOP).json -o $(TOP).svg
	svgo $(TOP).svg
	rsvg-convert -f pdf -o $(TOP).pdf $(TOP).svg

visualize_generic: $(TOP)_generic.pdf ## Generate visualization PDF from generic netlist
.PHONY: visualize_generic

$(TOP)_generic.pdf: $(TOP)_generic.json
	sed -i -e 's/inout/output/g' $(TOP)_generic.json
	netlistsvg $(TOP)_generic.json -o $(TOP)_generic.svg
	svgo $(TOP)_generic.svg
	rsvg-convert -f pdf -o $(TOP)_generic.pdf $(TOP)_generic.svg
# ================================================================================================


# Place-and-Route Targets
pr: $(TOP).asc ## Run place-and-route with nextpnr
.PHONY: pr

$(TOP).asc: $(TOP).json $(PCF_FILE)
	nextpnr-ice40 --up5k --package sg48 --pcf-allow-unconstrained --asc $(TOP).asc --pcf $(PCF_FILE) --json $(TOP).json

pr-gui: $(TOP).json ## Run place-and-route in GUI mode
	nextpnr-ice40 --up5k --package sg48 --asc $(TOP).asc --json $(TOP).json --gui
.PHONY: pr-gui

gen_bitstream: $(TOP).bin ## Generate FPGA bitstream
.PHONY: gen_bitstream

$(TOP).bin: $(TOP).asc
	icepack $(TOP).asc $(TOP).bin

flash_bitstream: $(TOP).bin ## Flash FPGA bitstream
	dfu-util --alt 0 --download $(TOP).bin
#	iceprog ${name}.bin
.PHONY: flash_bitstream
# ================================================================================================


# Conversion Target
convert: $(TOP).v ## Convert SystemVerilog top to Verilog
.PHONY: convert

$(TOP).v: $(MODULES_SYNTH)
	yosys -DFPGA -p 'hierarchy -top $(TOP); proc; write_verilog $(TOP).v;' $(MODULES_SYNTH)
# ================================================================================================


# All Target
all: ## Run full FPGA flow (lint, synthesis, place-and-route, bitstream)
	$(MAKE) clean
	$(MAKE) lint-verilog-all
	$(MAKE) synthesis
	$(MAKE) pr
	$(MAKE) gen_bitstream
.PHONY: all
# ================================================================================================
