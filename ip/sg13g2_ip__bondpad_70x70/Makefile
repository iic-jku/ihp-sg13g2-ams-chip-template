# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Variables
TOP = sg13g2_ip__bondpad_70x70

.DEFAULT_GOAL := help

# PDK Guard
# Override with: make <target> REQUIRED_PDK=<pdk>, an empty value skips the check
REQUIRED_PDK ?= ihp-sg13g2

# Goals that do not read the PDK
PDK_FREE_GOALS = help clean

ifneq ($(REQUIRED_PDK),)
ifneq ($(filter-out $(PDK_FREE_GOALS),$(or $(MAKECMDGOALS),$(.DEFAULT_GOAL))),)
ifneq ($(PDK),$(REQUIRED_PDK))
$(error PDK is "$(PDK)", but this IP needs "$(REQUIRED_PDK)". Run `sak-pdk $(REQUIRED_PDK)` in this shell and retry, or pass REQUIRED_PDK= to skip this check)
endif
endif
endif
# ================================================================================================


# Cell name for verification targets (default: top-level cell)
# Override with: make <target> CELL=<cellname>
CELL ?= $(TOP)

# KLayout/gdscheck DRC level: precheck, macro, or regular (sak-drc.sh -l, only used by klayout-drc and gdscheck-drc; default: macro)
# Override with: make <target> DRC_LEVEL=<precheck|macro|regular>
DRC_LEVEL ?= macro

# gdscheck suite, replaces the one DRC_LEVEL selects (sak-drc.sh -s, only used by gdscheck-drc; default: empty = precheck runs precheck, macro core, regular main)
# Override with: make <target> GDSCHECK_SUITE=<precheck|core|main|density|antenna|recommended>
GDSCHECK_SUITE ?=

# Parallel DRC jobs, the KLayout processes and gdscheck threads (sak-drc.sh -j, only used by klayout-drc and gdscheck-drc; default: empty = 4 KLayout processes or fewer, gdscheck on every CPU)
# Override with: make <target> DRC_JOBS=<n>
DRC_JOBS ?=

# sak-drc.sh options for the two variables above, left out when empty so that the script defaults apply
_GDSCHECK_SUITE_OPT = $(if $(GDSCHECK_SUITE),-s $(GDSCHECK_SUITE))
_DRC_JOBS_OPT = $(if $(DRC_JOBS),-j $(DRC_JOBS))

# Extra options for the sak-open.py file browser (e.g. --all to include build outputs)
# Override with: make open OPEN_ARGS=<options>
OPEN_ARGS ?=

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
	@echo 'REQUIRED_PDK defaults to $(REQUIRED_PDK). Every target except help and clean aborts if $$PDK differs.'
.PHONY: help
# ================================================================================================


# Open Target
open: ## Open the design files of this folder in the sak-open.py file browser (needs the VNC/X11 desktop)
	sak-open.py $(OPEN_ARGS) .
.PHONY: open
# ================================================================================================


# Clean Target
clean: ## Remove generated outputs and reports
	rm -rf $(GDS_DIR)
	rm -rf $(LEF_DIR)
	rm -rf $(VH_DIR)
	rm -rf $(DRC_RPT_DIR)
	rm -rf script/__pycache__
.PHONY: clean
# ================================================================================================


# Build Target
bondpad: ## Generate bondpad GDS and LEF (usage: make bondpad [DIAMETER=<um>] [SHAPE=<square|octagon|circle>] [BOTTOM_METAL=<1-6>])
	KLAYOUT_PATH=$(PDK_ROOT)/$(PDK)/libs.tech/klayout:$(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech klayout -n sg13g2 -zz -r script/bondpad.py -rd diameter=$(DIAMETER) -rd shape=$(SHAPE) -rd bottom_metal=$(BOTTOM_METAL) -rd gds_output=$(GDS_DIR)/$(TOP).gds -rd lef_output=$(LEF_DIR)/$(TOP).lef
.PHONY: bondpad
# ================================================================================================


# DRC Targets
klayout-drc: ## Run KLayout DRC of the CELL cell (usage: make klayout-drc [CELL=<cellname>] [DRC_LEVEL=<precheck|macro|regular>] [DRC_JOBS=<n>])
	mkdir -p $(DRC_RPT_DIR)
	sak-drc.sh -d -k -l $(DRC_LEVEL) $(_DRC_JOBS_OPT) -w $(DRC_RPT_DIR) $(GDS_DIR)/$(CELL).gds
.PHONY: klayout-drc

magic-drc: ## Run Magic DRC of the CELL cell (usage: make magic-drc [CELL=<cellname>])
	mkdir -p $(DRC_RPT_DIR)
	sak-drc.sh -d -m -f "*" -w $(DRC_RPT_DIR) $(GDS_DIR)/$(CELL).gds
.PHONY: magic-drc

gdscheck-drc: ## Run gdscheck DRC of the CELL cell (usage: make gdscheck-drc [CELL=<cellname>] [DRC_LEVEL=<precheck|macro|regular>] [GDSCHECK_SUITE=<suite>] [DRC_JOBS=<n>])
	mkdir -p $(DRC_RPT_DIR)
	sak-drc.sh -d -g -l $(DRC_LEVEL) $(_GDSCHECK_SUITE_OPT) $(_DRC_JOBS_OPT) -w $(DRC_RPT_DIR) $(GDS_DIR)/$(CELL).gds
.PHONY: gdscheck-drc
# ================================================================================================


# Verilog Target
verilog: ## Generate a minimal Verilog wrapper for the bondpad
	mkdir -p $(VH_DIR)
	@printf 'module $(TOP) (\n    inout pad\n);\nendmodule\n' > $(VH_DIR)/$(TOP).vh
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