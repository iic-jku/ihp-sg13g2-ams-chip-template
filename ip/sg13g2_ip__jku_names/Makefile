# SPDX-FileCopyrightText: 2025-2026 The Chip Team
# SPDX-License-Identifier: Apache-2.0

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Variables
TOP = sg13g2_ip__jku_names

.DEFAULT_GOAL := help

# Cell name for verification targets (default: top-level cell)
# Override with: make <target> CELL=<cellname>
CELL ?= $(TOP)

# Folder structure
GDS_DIR     := final/gds
LEF_DIR     := final/lef
LIB_DIR     := final/lib
VH_DIR      := final/vh
DRC_RPT_DIR := verification/drc

# Logo parameters
IMG_FILE    := logo/jku_names.png
IMG_SIZE_PX ?= 750
BLOCK_SIZE  ?= 100
PIXEL_SIZE  ?= 0.25 	# Pixel size in microns. Must be >= minimum layer width to avoid DRC violations.
# scale = BLOCK_SIZE / (IMG_SIZE_PX * PIXEL_SIZE)
SCALE       := $(shell python3 -c "print($(BLOCK_SIZE) / ($(IMG_SIZE_PX) * $(PIXEL_SIZE)))")


# Help Target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
.PHONY: help
# ================================================================================================


# Clean Target
clean: ## Remove generated outputs and reports
	rm -rf $(GDS_DIR)
	rm -rf $(LEF_DIR)
	rm -rf $(LIB_DIR)
	rm -rf $(VH_DIR)
	rm -rf $(DRC_RPT_DIR)
.PHONY: clean
# ================================================================================================


# Build Target
# Layers (IHP SG13G2):
# (8, 0),      # Metal1
# (10, 0),     # Metal2
# (30, 0),     # Metal3
# (50, 0),     # Metal4
# (67, 0),     # Metal5
# (126, 0),    # TopMetal1
# (134, 0),    # TopMetal2
# (189, 0),    # prBoundary
# (160, 0),    # NoMetFiller
logo: ## Generate GDS from image using Python script
	mkdir -p $(GDS_DIR)
	python3 script/make_gds.py $(IMG_FILE) $(GDS_DIR)/$(TOP).gds --cellname $(TOP) --invert --merge --pixel-size $(PIXEL_SIZE) --scale $(SCALE) --foreground "67/0" --boundary "189/0" "160/0"
.PHONY: logo
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


# LEF Target
lef: ## Generate LEF macro definition for the logo
	mkdir -p $(LEF_DIR)
	@printf 'VERSION 5.8 ;\n  NOWIREEXTENSIONATPIN ON ;\n  DIVIDERCHAR "/" ;\n  BUSBITCHARS "[]" ;\nMACRO $(TOP)\n  CLASS BLOCK ;\n  FOREIGN $(TOP) ;\n  ORIGIN 0.000 0.000 ;\n  SIZE $(BLOCK_SIZE) BY $(BLOCK_SIZE) ;\n  OBS\n      LAYER TopMetal2 ;\n        RECT 0.0 0.0 $(BLOCK_SIZE) $(BLOCK_SIZE) ;\n  END\nEND $(TOP)\nEND LIBRARY\n' > $(LEF_DIR)/$(TOP).lef
.PHONY: lef
# ================================================================================================


# LIB Target
lib: ## Generate LIB timing library for the logo
	mkdir -p $(LIB_DIR)
	@printf 'library ($(TOP)) {\n  input_threshold_pct_fall: 50.0;\n  input_threshold_pct_rise: 50.0;\n  output_threshold_pct_fall: 50.0;\n  output_threshold_pct_rise: 50.0;\n  slew_lower_threshold_pct_fall: 20.0;\n  slew_lower_threshold_pct_rise: 20.0;\n  slew_upper_threshold_pct_fall: 80.0;\n  slew_upper_threshold_pct_rise: 80.0;\n  \n  cell ($(TOP)) {\n  }\n}\n' > $(LIB_DIR)/$(TOP).lib
.PHONY: lib
# ================================================================================================


# Verilog Target
verilog: ## Generate a minimal Verilog wrapper for the logo
	mkdir -p $(VH_DIR)
	@printf 'module $(TOP);\nendmodule\n' > $(VH_DIR)/$(TOP).v
.PHONY: verilog
# ================================================================================================


# Build and Verify All Target
all: ## Build and verify the logo
	$(MAKE) clean
	$(MAKE) logo
	$(MAKE) lef
	$(MAKE) lib
	$(MAKE) verilog
	$(MAKE) klayout-drc
	$(MAKE) magic-drc
.PHONY: all
# ================================================================================================
