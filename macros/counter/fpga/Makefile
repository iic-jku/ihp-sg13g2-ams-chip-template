# SPDX-FileCopyrightText: 2025-2026 Simon Dorrer
# SPDX-License-Identifier: Apache-2.0

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Variables
TOP = counter_top
TARGET ?= synth_ice40

.DEFAULT_GOAL := help

# Folder structure
VERILOG_DIR := ../verilog
SRC_DIR     := $(VERILOG_DIR)/src
TB_DIR      := $(VERILOG_DIR)/tb
PCF_FILE    := pico-ice.pcf

MODULES_SYNTH := \
	$(SRC_DIR)/uart_tx.v \
	$(SRC_DIR)/uart_rx.v \
	$(SRC_DIR)/i2c_master.sv \
	$(SRC_DIR)/i2c_master_mc.sv \
	$(SRC_DIR)/spi_master.sv \
	$(SRC_DIR)/dsmod.v \
	$(SRC_DIR)/cordic_slice.v \
	$(SRC_DIR)/cordic_iterative.v \
	$(SRC_DIR)/lo_gen.v \
	$(SRC_DIR)/freq_generator.sv \
	$(SRC_DIR)/memory.sv \
	$(SRC_DIR)/regs.sv \
	$(SRC_DIR)/alu.sv \
	$(SRC_DIR)/control.sv \
	$(SRC_DIR)/instructioncounter.sv \
	$(SRC_DIR)/csr.sv \
	$(SRC_DIR)/imm_gen.sv

MODULES_SIM :=  \
	$(VERILOG_DIR)/constants.sv \
	$(MODULES_SYNTH) \
	$(SRC_DIR)/sram_sim.sv


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

lint: ## Run Verilator lint checks
	verilator --lint-only -Wall -I$(SRC_DIR) $(SRC_DIR)/$(TOP).sv
.PHONY: lint
# ================================================================================================


# Synthesis Targets
synthesis: $(TOP).json ## Run technology-mapped synthesis for iCE40
.PHONY: synthesis

$(TOP).json: $(SRC_DIR)/$(TOP).sv $(MODULES_SYNTH)
	yosys -DFPGA -p '$(TARGET) -dsp -spram -top $(TOP); write_json $(TOP).json;' $(SRC_DIR)/$(TOP).sv $(MODULES_SYNTH)

synthesis_generic: $(TOP)_generic.json ## Run generic synthesis and generate Yosys graph
.PHONY: synthesis_generic

$(TOP)_generic.json: $(SRC_DIR)/$(TOP).sv $(MODULES_SYNTH)
	yosys -p 'hierarchy -top $(TOP); proc; write_json $(TOP)_generic.json; show -format svg -prefix $(TOP)_generic_yosys $(TOP);' $(SRC_DIR)/$(TOP).sv $(MODULES_SYNTH)
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
.PHONY: flash_bitstream
# ================================================================================================


# Conversion Target
convert: $(TOP).v ## Convert SystemVerilog top to Verilog
.PHONY: convert

$(TOP).v: $(SRC_DIR)/$(TOP).sv $(MODULES_SYNTH)
	yosys -DFPGA -p 'hierarchy -top $(TOP); proc; write_verilog $(TOP).v;' $(SRC_DIR)/$(TOP).sv $(MODULES_SYNTH)
# ================================================================================================


# All Target
all: ## Run full FPGA flow (simulation, synthesis, place-and-route, bitstream, flash)
	$(MAKE) simulation
	$(MAKE) synthesis
	$(MAKE) pr
	$(MAKE) gen_bitstream
	$(MAKE) flash_bitstream
.PHONY: all
# ================================================================================================
