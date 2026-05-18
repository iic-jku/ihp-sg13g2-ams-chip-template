# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Variables
TOP = sg13g2_ip__bondpad_70x70

.DEFAULT_GOAL := help

# Cell name for verification targets (default: top-level cell)
# Override with: make <target> CELL=<cellname>
CELL ?= $(TOP)

# Folder structure
GDS_DIR   	:= final/gds
LEF_DIR   	:= final/lef
VH_DIR    	:= final/vh
DRC_RPT_DIR := verification/drc

# Bondpad parameters
DIAMETER     ?= 70.0
SHAPE        ?= square
BOTTOM_METAL ?= 3


# Help Target
help: ## Show this help message
	@echo 'Usage: make <target> [DIAMETER=<um>] [SHAPE=<square|octagon|circle>] [BOTTOM_METAL=<1-6>] [CELL=<cellname>]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ''
	@echo 'DIAMETER defaults to $(DIAMETER) (µm).'
	@echo 'SHAPE defaults to $(SHAPE). Allowed: square, octagon, circle.'
	@echo 'BOTTOM_METAL defaults to $(BOTTOM_METAL) (1=Metal1 .. 5=Metal5, 6=TopMetal1). Top is fixed to TopMetal2.'
	@echo 'CELL defaults to $(TOP). Override to verify subcells.'
.PHONY: help
# ================================================================================================


# Clean Target
clean: ## Remove generated outputs and reports
	rm -rf $(GDS_DIR)
	rm -rf $(LEF_DIR)
	rm -rf $(VH_DIR)
	rm -rf $(DRC_RPT_DIR)
.PHONY: clean
# ================================================================================================


# Build Target
bondpad: ## Generate bondpad GDS and LEF (usage: make bondpad [DIAMETER=<um>] [SHAPE=<square|octagon|circle>] [BOTTOM_METAL=<1-6>])
	KLAYOUT_PATH=$(PDK_ROOT)/$(PDK)/libs.tech/klayout:$(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech klayout -n sg13g2 -zz -r script/bondpad.py -rd diameter=$(DIAMETER) -rd shape=$(SHAPE) -rd bottom_metal=$(BOTTOM_METAL) -rd gds_output=$(GDS_DIR)/$(TOP).gds -rd lef_output=$(LEF_DIR)/$(TOP).lef
.PHONY: bondpad
# ================================================================================================


# DRC Targets
klayout-drc: ## Run KLayout DRC of the CELL cell (usage: make klayout-drc [CELL=<cellname>])
	mkdir -p $(DRC_RPT_DIR)
	python3 $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/run_drc.py \
		--path=$(GDS_DIR)/$(CELL).gds \
		--topcell=$(CELL) \
		--run_dir=$(DRC_RPT_DIR) \
		--no_feol \
		--no_density \
		--disable_extra_rules \
		--mp=32 \
		--density_thr=32
	sleep 4
.PHONY: klayout-drc

magic-drc: ## Run Magic DRC of the CELL cell (usage: make magic-drc [CELL=<cellname>])
	mkdir -p $(DRC_RPT_DIR)
	sak-drc.sh -d -m -f "*" -w $(DRC_RPT_DIR) $(GDS_DIR)/$(CELL).gds $(CELL)
	rm -f $(DRC_RPT_DIR)/drc_$(CELL).tcl
	sleep 4
.PHONY: magic-drc
# ================================================================================================


# Verilog Target
verilog: ## Generate a minimal Verilog wrapper for the bondpad
	mkdir -p $(VH_DIR)
	@printf 'module $(TOP) (\n    inout pad\n);\nendmodule\n' > $(VH_DIR)/$(TOP).v
.PHONY: verilog
# ================================================================================================


# Build and Verify All Target
all: ## Build and verify the bondpad
	$(MAKE) clean
	$(MAKE) bondpad
	$(MAKE) verilog
	$(MAKE) klayout-drc
	$(MAKE) magic-drc
.PHONY: all
# ================================================================================================