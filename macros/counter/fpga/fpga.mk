# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Shared FPGA emulation flow (lint, synthesis, place-and-route, bitstream).
#
# Included last by the per-board Makefiles in <board>/, which set the sources,
# the pin constraint file and the board configuration first. The board's ARCH
# names the toolchain, which comes from arch/<arch>.mk, included below.
#
# Variables the including Makefile must set:
#   TOP           - synthesis top module / instance name
#   MODULES_SYNTH - explicit ordered source file list for TOP
#   PCF_FILE      - board pin constraint file
#   ARCH          - FPGA architecture, selects arch/<arch>.mk

# Fail fast when a mandatory variable is missing, so a board Makefile with a
# wrong include order errors here instead of misbehaving further down.
$(foreach v,TOP MODULES_SYNTH PCF_FILE ARCH,$(if $(strip $($(v))),,$(error $(v) is not set, set it in the board Makefile before including fpga.mk)))

FPGA_MK_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

BUILD_DIR ?= build

# Cell name for the lint targets (default: top-level cell)
# Override with: make <target> CELL=<cellname>
CELL ?= $(TOP)

include $(FPGA_MK_DIR)arch/$(ARCH).mk

# Source files for lint-verilog: full module list for TOP, constants.sv plus the
# single file (auto-detecting .sv/.v) otherwise
_LINT_SRCS = $(if $(filter $(CELL),$(TOP)),$(MODULES_SYNTH),$(SRC_DIR)/constants.sv $(or $(wildcard $(SRC_DIR)/$(CELL).sv),$(SRC_DIR)/$(CELL).v))

# Full synthesis command. Only override this wholesale (instead of TARGET/
# SYNTH_OPTS) for a toolchain whose synth_* pass does not fit the
# "$(TARGET) $(SYNTH_OPTS) -top $(TOP)" shape.
SYNTH_CMD ?= yosys -DFPGA -p '$(TARGET) $(SYNTH_OPTS) -top $(TOP); write_json $(BUILD_DIR)/$(TOP).json;' $(MODULES_SYNTH)

# Extra prerequisites for the place-and-route step beyond $(TOP).json and
# $(PCF_FILE), for example a one-time-generated chip database.
PNR_DEPS ?=

# Interactive place-and-route. Arch fragments whose place-and-route has a GUI
# set this, the others leave it empty and pr-gui then refuses to run.
PNR_GUI_CMD ?=

.DEFAULT_GOAL := help


# Help Target
help: ## Show this help message
	@echo 'Usage: make <target> [CELL=<cellname>]'
	@echo ''
	@echo 'Available targets:'
	@grep -hE '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ''
	@echo 'Board $(notdir $(CURDIR)): ARCH=$(ARCH), TOP=$(TOP), constraints $(PCF_FILE).'
	@echo 'CELL defaults to $(TOP). Override to lint subcells.'
	@echo 'Build outputs go to $(BUILD_DIR)/.'
.PHONY: help
# ================================================================================================


# Clean Target
clean: ## Remove the generated files of this board
	rm -rf $(BUILD_DIR)
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
synthesis: $(BUILD_DIR)/$(TOP).json ## Run technology-mapped synthesis for this board's architecture
.PHONY: synthesis

$(BUILD_DIR)/$(TOP).json: $(MODULES_SYNTH) | $(BUILD_DIR)
	$(SYNTH_CMD)

synthesis_generic: $(BUILD_DIR)/$(TOP)_generic.json ## Run generic synthesis and generate a Yosys graph
.PHONY: synthesis_generic

$(BUILD_DIR)/$(TOP)_generic.json: $(MODULES_SYNTH) | $(BUILD_DIR)
	yosys -p 'hierarchy -top $(TOP); proc; write_json $(BUILD_DIR)/$(TOP)_generic.json; show -format svg -prefix $(BUILD_DIR)/$(TOP)_generic_yosys $(TOP);' $(MODULES_SYNTH)
# ================================================================================================


# Visualization Targets
visualize: $(BUILD_DIR)/$(TOP).pdf ## Generate a visualization PDF from the technology-mapped netlist
.PHONY: visualize

# netlistsvg cannot render inout ports, so visualise a COPY of the netlist:
# rewriting $(TOP).json in place would corrupt the netlist that the place-and-route uses in `pr`.
$(BUILD_DIR)/$(TOP).pdf: $(BUILD_DIR)/$(TOP).json
	sed -e 's/inout/output/g' $(BUILD_DIR)/$(TOP).json > $(BUILD_DIR)/$(TOP)_viz.json
	netlistsvg $(BUILD_DIR)/$(TOP)_viz.json -o $(BUILD_DIR)/$(TOP).svg
	svgo $(BUILD_DIR)/$(TOP).svg
	rsvg-convert -f pdf -o $(BUILD_DIR)/$(TOP).pdf $(BUILD_DIR)/$(TOP).svg

visualize_generic: $(BUILD_DIR)/$(TOP)_generic.pdf ## Generate a visualization PDF from the generic netlist
.PHONY: visualize_generic

$(BUILD_DIR)/$(TOP)_generic.pdf: $(BUILD_DIR)/$(TOP)_generic.json
	sed -e 's/inout/output/g' $(BUILD_DIR)/$(TOP)_generic.json > $(BUILD_DIR)/$(TOP)_generic_viz.json
	netlistsvg $(BUILD_DIR)/$(TOP)_generic_viz.json -o $(BUILD_DIR)/$(TOP)_generic.svg
	svgo $(BUILD_DIR)/$(TOP)_generic.svg
	rsvg-convert -f pdf -o $(BUILD_DIR)/$(TOP)_generic.pdf $(BUILD_DIR)/$(TOP)_generic.svg
# ================================================================================================


# Place-and-Route Targets
pr: $(PNR_OUT) ## Run place-and-route
.PHONY: pr

$(PNR_OUT): $(BUILD_DIR)/$(TOP).json $(PCF_FILE) $(PNR_DEPS) | $(BUILD_DIR)
	$(PNR_CMD)

pr-gui: $(BUILD_DIR)/$(TOP).json ## Run place-and-route in GUI mode
ifeq ($(strip $(PNR_GUI_CMD)),)
	@echo "The $(ARCH) place-and-route has no GUI mode, use 'make pr' instead."; exit 1
else
	$(PNR_GUI_CMD)
endif
.PHONY: pr-gui
# ================================================================================================


# Bitstream Targets
gen_bitstream: $(BITSTREAM) ## Generate the FPGA bitstream
.PHONY: gen_bitstream

$(BITSTREAM): $(PNR_OUT) | $(BUILD_DIR)
	$(PACK_CMD)

load_bitstream: $(BITSTREAM) ## Load the bitstream into FPGA SRAM (lost on power cycle)
	$(LOAD_CMD)
.PHONY: load_bitstream

flash_bitstream: $(BITSTREAM) ## Write the bitstream to flash (persistent)
	$(FLASH_CMD)
.PHONY: flash_bitstream
# ================================================================================================


# Conversion Target
convert: $(BUILD_DIR)/$(TOP).v ## Convert the SystemVerilog top to Verilog
.PHONY: convert

$(BUILD_DIR)/$(TOP).v: $(MODULES_SYNTH) | $(BUILD_DIR)
	yosys -DFPGA -p 'hierarchy -top $(TOP); proc; write_verilog $(BUILD_DIR)/$(TOP).v;' $(MODULES_SYNTH)
# ================================================================================================


$(BUILD_DIR):
	mkdir -p $@


# All Target
all: ## Run the full FPGA flow (lint, synthesis, place-and-route, bitstream)
	$(MAKE) clean
	$(MAKE) lint-verilog-all
	$(MAKE) synthesis
	$(MAKE) pr
	$(MAKE) gen_bitstream
.PHONY: all
# ================================================================================================
