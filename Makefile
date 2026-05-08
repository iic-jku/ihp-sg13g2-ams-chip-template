# Makefile for an Open-Source Analog-Mixed Signal Chip Design Template for the ihp-sg13g2 Open-PDK.
#
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# Johannes Kepler University, Department for Integrated Circuits
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0
# ========================================================================

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

RUN_TAG = $(shell ls -1 $(LIBRELANE_DIR)/runs 2>/dev/null | tail -n 1)

# Variables
TOP = chip_top

.DEFAULT_GOAL := help

# Version for release target
# Override with: make <target> VERSION=<version>
VERSION ?= 1.0.0

# Cell name for verification targets (default: top-level cell)
# Override with: make <target> CELL=<cellname>
CELL ?= $(TOP)

# PEX mode (1 = C-decoupled, 2 = C-coupled, 3 = full-RC)
# Override with: make <target> EXT_MODE=<1|2|3>
EXT_MODE ?= 3

# Floating-point precision (significant digits) for xschem's ev function
# Override with: make <target> EV_PRECISION=<digits>
EV_PRECISION ?= 5

# Set the waveform viewer GTKWave or Surfer (default: gtkwave)
# Override with: make <target> WAVEFORM_VIEWER=<gtkwave|surfer>
WAVEFORM_VIEWER ?= gtkwave

# Folder structure
SCH_DIR     		 	:= schematic
LAY_DIR     		 	:= layout
SCRIPTS_DIR     	 	:= scripts
SRC_DIR 			    := rtl
IP_DIR 			    	:= ip
MACROS_DIR 		    	:= macros
RELEASE_DIR		 		:= release
RENDER_IMG_DIR  	 	:= render/img
COCOTB_DIR      	 	:= testbenches/cocotb
XSCHEM_TB_DIR         	:= testbenches/xschem
NET_SCH_DIR 		 	:= netlist/schematic
NET_LAY_DIR 		 	:= netlist/layout
NET_PEX_DIR 		 	:= netlist/pex
NET_PNL_DIR			 	:= netlist/pnl
NET_NL_DIR			 	:= netlist/nl
NET_SPICE_DIR		 	:= netlist/spice
LVS_RPT_DIR 		 	:= verification/lvs
DRC_RPT_DIR 		 	:= verification/drc
LIBRELANE_DIR   	 	:= flow/librelane
FLOW_REPORT_DIR 	 	:= flow/reports
FLOW_FINAL_DIR 		 	:= flow/final
FLOW_FINAL_GDS_DIR 	 	:= flow/final/gds
FLOW_FINAL_PNL_DIR 	 	:= flow/final/pnl
FLOW_FINAL_NL_DIR 	 	:= flow/final/nl
FLOW_FINAL_SPICE_DIR 	:= flow/final/spice
FLOW_FINAL_RENDER_DIR	:= flow/final/render


# Help Target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
.PHONY: help
# ================================================================================================


# GIT Submodule Target
init-submodules: ## Initialize and update git submodules (e.g. ihp130/artistic)
	git -C $(MAKEFILE_DIR) submodule update --init
.PHONY: init-submodules
# ================================================================================================


# Simulation Targets
sim-rtl-cocotb: ## Run RTL simulation of CELL cell with cocotb (usage: make sim-rtl-cocotb [CELL=<cellname>])
	cd $(COCOTB_DIR); python3 $(CELL)_tb.py
.PHONY: sim-rtl-cocotb

sim-gl-cocotb: ## Run gate-level simulation of CELL cell with cocotb (usage: make sim-gl-cocotb [CELL=<cellname>])
	cd $(COCOTB_DIR); GL=1 python3 $(CELL)_tb.py
.PHONY: sim-gl-cocotb

sim-view-cocotb: ## View CELL cell cocotb simulation waveforms (usage: make sim-view-cocotb [CELL=<cellname>] [WAVEFORM_VIEWER=<gtkwave|surfer>])
	@if [ "$(WAVEFORM_VIEWER)" = "gtkwave" ]; then \
		$(WAVEFORM_VIEWER) $(COCOTB_DIR)/sim_build/$(CELL).fst $(COCOTB_DIR)/$(CELL)_tb.gtkw; \
	elif [ "$(WAVEFORM_VIEWER)" = "surfer" ]; then \
		$(WAVEFORM_VIEWER) -s $(COCOTB_DIR)/$(CELL)_tb.surf.ron $(COCOTB_DIR)/sim_build/$(CELL).fst; \
	else \
		$(WAVEFORM_VIEWER) $(COCOTB_DIR)/sim_build/$(CELL).fst; \
	fi
.PHONY: sim-view-cocotb

sim-gl-xschem: ## Run gate-level simulation of CELL cell with Xschem (usage: make sim-gl-xschem [CELL=<cellname>])
	cd $(XSCHEM_TB_DIR); xschem -s -r -x -q --rcfile xschemrc --command ' \
		set netlist_dir $(abspath $(XSCHEM_TB_DIR)/simulations); \
		xschem save; \
		xschem netlist; \
		xschem simulate \
	' $(CELL)_tb_tran.sch
.PHONY: sim-gl-xschem

sim-all: ## Simulate the top-level
	$(MAKE) sim-rtl-cocotb
	$(MAKE) sim-gl-cocotb
	$(MAKE) sim-gl-xschem
.PHONY: sim-all
# ================================================================================================


# LibreLane Targets
librelane: ## Run LibreLane with Magic and KLayout DRC checks
	librelane $(LIBRELANE_DIR)/config.yaml --pdk ${PDK} --pdk-root ${PDK_ROOT} --manual-pdk --save-views-to $(FLOW_FINAL_DIR)/
.PHONY: librelane

librelane-nodrc: ## Run LibreLane without DRC checks
	librelane $(LIBRELANE_DIR)/config.yaml --pdk ${PDK} --pdk-root ${PDK_ROOT} --manual-pdk --save-views-to $(FLOW_FINAL_DIR)/ --skip KLayout.DRC --skip Magic.DRC --skip KLayout.Antenna --skip KLayout.Density
.PHONY: librelane-nodrc

librelane-magicdrc: ## Run LibreLane with only Magic DRC checks
	librelane $(LIBRELANE_DIR)/config.yaml --pdk ${PDK} --pdk-root ${PDK_ROOT} --manual-pdk --save-views-to $(FLOW_FINAL_DIR)/ --skip KLayout.DRC
.PHONY: librelane-magicdrc

librelane-klayoutdrc: ## Run LibreLane with only KLayout DRC checks
	librelane $(LIBRELANE_DIR)/config.yaml --pdk ${PDK} --pdk-root ${PDK_ROOT} --manual-pdk --save-views-to $(FLOW_FINAL_DIR)/ --skip Magic.DRC
.PHONY: librelane-klayoutdrc

librelane-openroad: ## Open the last LibreLane run in OpenROAD GUI
	librelane $(LIBRELANE_DIR)/config.yaml --pdk ${PDK} --pdk-root ${PDK_ROOT} --manual-pdk --last-run --flow OpenInOpenROAD
.PHONY: librelane-openroad

librelane-klayout: ## Open the last LibreLane run in KLayout
	librelane $(LIBRELANE_DIR)/config.yaml --pdk ${PDK} --pdk-root ${PDK_ROOT} --manual-pdk --last-run --flow OpenInKLayout
.PHONY: librelane-klayout
# ================================================================================================


# Copy Targets
# TODO: Antenna and DRC reports are temporarily commented out until IHP fixes the `metal1_pin_offgrid` errors.
# For now, `make librelane-nodrc` must be used.
# https://github.com/IHP-GmbH/IHP-Open-PDK/issues/683#issuecomment-4065791975
copy-reports: ## Copy yosys, antenna violations, hold & setup timing, DRC, LVS and manufacturability reports
	rm -rf $(FLOW_REPORT_DIR)/
	mkdir -p $(FLOW_REPORT_DIR)/
	# Using * wildcard to ignore step numbers
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/pre_synth_chk.rpt $(FLOW_REPORT_DIR)/yosys_synth_check.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/pre_techmap.rpt $(FLOW_REPORT_DIR)/yosys_pre_techmap.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/post_dff.rpt $(FLOW_REPORT_DIR)/yosys_post_dff.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/stat.rpt $(FLOW_REPORT_DIR)/stat.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-checkantennas-1/reports/antenna.rpt $(FLOW_REPORT_DIR)/antenna_violations.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-checkantennas-1/reports/antenna_summary.rpt $(FLOW_REPORT_DIR)/antenna_summary.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/summary.rpt $(FLOW_REPORT_DIR)/hold_setup_timing.rpt
# 	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-klayout-antenna/reports/antenna.klayout.json $(FLOW_REPORT_DIR)/antenna.klayout.json
# 	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-magic-drc/reports/drc.magic.rpt $(FLOW_REPORT_DIR)/drc.magic.rpt
# 	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-klayout-drc/reports/drc.klayout.json $(FLOW_REPORT_DIR)/drc.klayout.json
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-netgen-lvs/reports/lvs.netgen.rpt $(FLOW_REPORT_DIR)/lvs.netgen.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-misc-reportmanufacturability/manufacturability.rpt $(FLOW_REPORT_DIR)/manufacturability.rpt
.PHONY: copy-reports

copy-gds: ## Copy and compress final output GDS from the last LibreLane run (no logo & fillers) to the layout/ directory
	rm -f $(LAY_DIR)/${TOP}.gds.gz
	mkdir -p $(LAY_DIR)/
	cp -r $(FLOW_FINAL_GDS_DIR)/${TOP}.gds $(LAY_DIR)/${TOP}.gds
	gzip $(LAY_DIR)/${TOP}.gds
.PHONY: copy-gds

copy-netlist: ## Copy final output spice, pnl and nl netlists from the last LibreLane run to the netlist/ directory
	rm -rf $(NET_SPICE_DIR)/
	mkdir -p $(NET_SPICE_DIR)/
	cp -r $(FLOW_FINAL_SPICE_DIR)/${TOP}.spice $(NET_SPICE_DIR)/${TOP}.spice
	rm -rf $(NET_PNL_DIR)/
	mkdir -p $(NET_PNL_DIR)/
	cp -r $(FLOW_FINAL_PNL_DIR)/${TOP}.pnl.v $(NET_PNL_DIR)/${TOP}.pnl.v
	mkdir -p $(NET_NL_DIR)/
	cp -r $(FLOW_FINAL_NL_DIR)/${TOP}.nl.v $(NET_NL_DIR)/${TOP}.nl.v
.PHONY: copy-netlist

copy-render: ## Copy chip render from the last LibreLane run (no logo & fillers) to the render/img/ directory
	mkdir -p $(RENDER_IMG_DIR)/
	cp -r $(FLOW_FINAL_RENDER_DIR)/${TOP}.png $(RENDER_IMG_DIR)/${TOP}_librelane.png
.PHONY: copy-render
# ================================================================================================


# Render Target
render-gds: ## Render an image from the final GDS with logo and fillers using lay2img.py
	mkdir -p $(RENDER_IMG_DIR)/
	python3 $(SCRIPTS_DIR)/lay2img.py $(LAY_DIR)/${TOP}_logo_fill.gds.gz $(RENDER_IMG_DIR)/${TOP}.png --width 2048 --oversampling 4
.PHONY: render-gds
# ================================================================================================


# Build Targets
build-bondpad: ## Build the bondpad
	@$(MAKE) -C $(IP_DIR)/sg13g2_ip__bondpad_70x70 all
.PHONY: build-bondpad

build-logos: ## Build the logos
	@$(MAKE) -C $(IP_DIR)/sg13g2_ip__jku all
	@$(MAKE) -C $(IP_DIR)/sg13g2_ip__jku_names all
	@$(MAKE) -C $(IP_DIR)/sg13g2_ip__ce all
	@$(MAKE) -C $(IP_DIR)/sg13g2_ip__ce_names all
.PHONY: build-logos

build-counter: ## Build the counter macro
	@$(MAKE) -C $(MACROS_DIR)/counter all
.PHONY: build-counter

build-inverter: ## Build the inverter macro
	@$(MAKE) -C $(MACROS_DIR)/inverter all
.PHONY: build-inverter

build-macros: build-counter build-inverter ## Build macros (counter and inverter)
.PHONY: build-macros

# This target adds the Chip logo and fill structures on all layers.
# TODO: This step is temporary and will be replaced by a custom LibreLane step in the future.
add-logo-fill: ## Call add_logo_fill.sh to add the Chip logo and fill structures
	cd $(SCRIPTS_DIR) && ./add_logo_fill.sh
.PHONY: add-logo-fill

# TODO: See above, `make librelane-nodrc` must be used for now until IHP fixes the `metal1_pin_offgrid` errors. Once fixed, `make librelane` can be used again.
# TODO: Add `make build-macros`. For now, this is not possible. counter is built with nix-shell. Top-Level is built with `next` release of IIC-OSIC-TOOLS due to https://github.com/FPGA-Research/heichips25-tapeout/blob/8944926f1f49e382616fbdd150e356bbdcf23b8c/nix/disable_auto_taper.patch#L4.
build-all: ## Build the whole chip (build bondpad, build logos, build macros, run LibreLane, copy reports, copy GDS, copy netlist, render gds, open GDS in OpenROAD GUI)
	$(MAKE) init-submodules
	$(MAKE) build-bondpad
	$(MAKE) build-logos
# 	$(MAKE) build-macros
	$(MAKE) librelane-nodrc
	$(MAKE) copy-reports
	$(MAKE) copy-gds
	$(MAKE) copy-netlist
	$(MAKE) copy-render
	$(MAKE) add-logo-fill
	$(MAKE) render-gds
	$(MAKE) librelane-openroad
.PHONY: build-all
# ================================================================================================


# LVS Targets
klayout-lvs-netlist: ## Export CDL schematic netlist from Xschem for KLayout LVS (usage: make klayout-lvs-netlist [CELL=<cellname>] [EV_PRECISION=<digits>])
	mkdir -p $(NET_SCH_DIR)
	xschem -s -r -x -q --rcfile $(SCH_DIR)/xschemrc --command ' \
		set spiceprefix 1; \
		set lvs_netlist 1; \
		set top_is_subckt 1; \
		set lvs_ignore 0; \
		set ev_precision $(EV_PRECISION); \
		set netlist_dir $(NET_SCH_DIR); \
		xschem set netlist_name [file tail [file rootname [xschem get current_name]]]_klayout.cdl; \
		xschem netlist \
	' $(SCH_DIR)/$(CELL).sch
.PHONY: klayout-lvs-netlist

klayout-lvs: ## Run KLayout LVS of the CELL cell (usage: make klayout-lvs [CELL=<cellname>])
	$(MAKE) klayout-lvs-netlist CELL=$(CELL)
	mkdir -p $(LVS_RPT_DIR)
	mkdir -p $(NET_LAY_DIR)
	python3 $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/lvs/run_lvs.py \
		--layout=$(LAY_DIR)/$(CELL).gds.gz \
		--netlist=$(NET_SCH_DIR)/$(CELL)_klayout.cdl \
		--topcell=$(CELL) \
		--run_dir=$(LVS_RPT_DIR) \
		--run_mode=deep
	mv $(LVS_RPT_DIR)/$(CELL)_extracted.cir $(NET_LAY_DIR)/$(CELL)_klayout.cir
	sleep 4
.PHONY: klayout-lvs

magic-lvs-netlist: ## Export SPICE schematic netlist from Xschem for Magic + Netgen LVS (usage: make magic-lvs-netlist [CELL=<cellname>] [EV_PRECISION=<digits>])
	mkdir -p $(NET_SCH_DIR)
	xschem -s -r -x -q --rcfile $(SCH_DIR)/xschemrc --command ' \
		set spiceprefix 1; \
		set lvs_netlist 0; \
		set top_is_subckt 1; \
		set lvs_ignore 1; \
		set ev_precision $(EV_PRECISION); \
		set netlist_dir $(NET_SCH_DIR); \
		xschem set netlist_name [file tail [file rootname [xschem get current_name]]]_magic.spice; \
		xschem netlist \
	' $(SCH_DIR)/$(CELL).sch
.PHONY: magic-lvs-netlist

magic-lvs: ## Run Magic + Netgen LVS of the CELL cell (usage: make magic-lvs [CELL=<cellname>])
	mkdir -p $(LVS_RPT_DIR)
	mkdir -p $(NET_LAY_DIR)
	$(MAKE) magic-lvs-netlist CELL=$(CELL)
	sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(NET_SCH_DIR)/$(CELL)_magic.spice -l $(LAY_DIR)/$(CELL).gds.gz -c $(CELL)
# 	Alternative using sak-lvs.sh for netlist export and LVS in one step (replaces magic-lvs-netlist target):
#   sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(SCH_DIR)/$(CELL).sch -l $(LAY_DIR)/$(CELL).gds.gz -c $(CELL)
	mv $(LVS_RPT_DIR)/$(CELL).ext.spc $(NET_LAY_DIR)/$(CELL)_magic.ext.spc
	rm -f $(LVS_RPT_DIR)/$(CELL).sch.spc
	rm -f $(LVS_RPT_DIR)/ext_$(CELL).tcl
	rm -f $(LVS_RPT_DIR)/*.ext
	sleep 4
.PHONY: magic-lvs
# ================================================================================================


# DRC Targets
klayout-drc-minimum: ## Run Minimum pre-check Klayout DRC of the TOP cell with logo and fillers (usage: make klayout-drc-minimum)
	mkdir -p $(DRC_RPT_DIR)
	python3 $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/run_drc.py \
		--path=$(LAY_DIR)/${TOP}_logo_fill.gds.gz \
		--topcell=${TOP} \
		--run_dir=$(DRC_RPT_DIR) \
		--precheck_drc \
		--mp=32 \
		--no_offgrid \
		--density_thr=32 \
		--no_angle \
		--disable_extra_rules \
		--no_recommended
	sleep 4
.PHONY: klayout-drc-minimum

klayout-drc-regular: ## Run Regular Klayout DRC of the TOP cell with logo and fillers (usage: make klayout-drc-regular)
	mkdir -p $(DRC_RPT_DIR)
	python3 $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/run_drc.py \
		--path=$(LAY_DIR)/${TOP}_logo_fill.gds.gz \
		--topcell=${TOP} \
		--run_dir=$(DRC_RPT_DIR) \
		--mp=32 \
		--density_thr=32
	sleep 4
.PHONY: klayout-drc-regular

klayout-drc: ## Run KLayout DRC of the CELL cell (usage: make klayout-drc [CELL=<cellname>])
	mkdir -p $(DRC_RPT_DIR)
	python3 $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/run_drc.py \
		--path=$(LAY_DIR)/$(CELL).gds.gz \
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
	sak-drc.sh -d -m -f "*" -w $(DRC_RPT_DIR) $(LAY_DIR)/$(CELL).gds.gz $(CELL)
	rm -f $(DRC_RPT_DIR)/drc_$(CELL).tcl
	sleep 4
.PHONY: magic-drc
# ================================================================================================


# PEX Targets
klayout-pex: ## Run Parasitic Extraction with KPEX of the CELL cell (usage: make klayout-pex [CELL=<cellname>] [EXT_MODE=<1|2|3>])
	mkdir -p $(NET_PEX_DIR)
	PDK_UNDERSCORED=$$(echo $$PDK | sed -e 's/-/_/g'); \
	case $(EXT_MODE) in \
		1) echo "WARNING: KPEX does not support C-decoupled (C) mode yet, using C-coupled (CC) mode instead."; KPEX_MODE=CC ;; \
		2) KPEX_MODE=CC ;; \
		3) KPEX_MODE=RC ;; \
		*) echo "Invalid EXT_MODE: $(EXT_MODE). Use 1, 2, or 3."; exit 1;; \
	esac; \
	kpex \
	--pdk $$PDK_UNDERSCORED \
	--cell $(CELL) \
	--schematic $(SCH_DIR)/$(CELL).sch \
	--gds $(LAY_DIR)/$(CELL).gds.gz \
	--magic \
	--magic_mode $$KPEX_MODE \
	--out_dir $(NET_PEX_DIR) \
	--out_spice $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice
#	--2.5D
#	--mode $$KPEX_MODE
	sed -i 's/$(CELL)_flat/$(CELL)_pex/g' $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice
	rm -rf $(NET_PEX_DIR)/$(CELL)__$(CELL)
	rm -f $(CELL)_flat.nodes $(CELL)_flat.sim
	@if [ -f $(SCH_DIR)/$(CELL)_pex.sym ]; then \
		echo "Reordering pins in $(CELL)_klayout_pex_$(EXT_MODE).spice to match $(CELL)_pex.sym..."; \
		python3 $(NET_PEX_DIR)/reorder_spice_pins.py $(SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice; \
	else \
		echo "No symbol $(SCH_DIR)/$(CELL)_pex.sym found, skipping pin reorder."; \
	fi
	sleep 4
.PHONY: klayout-pex

magic-pex: ## Run Parasitic Extraction with Magic of the CELL cell (usage: make magic-pex [CELL=<cellname>] [EXT_MODE=<1|2|3>])
	mkdir -p $(NET_PEX_DIR)
	sak-pex.sh -d -m $(EXT_MODE) -w $(NET_PEX_DIR) $(LAY_DIR)/$(CELL).gds.gz
	mv $(NET_PEX_DIR)/$(CELL).pex.spice $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice
	sed -i 's/$(CELL)/$(CELL)_pex/g' $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice
	rm -f $(NET_PEX_DIR)/pex_$(CELL).tcl $(NET_PEX_DIR)/$(CELL).ext $(NET_PEX_DIR)/$(CELL)_flat.ext $(NET_PEX_DIR)/$(CELL)_flat.res.ext
	@if [ -f $(SCH_DIR)/$(CELL)_pex.sym ]; then \
		echo "Reordering pins in $(CELL)_magic_pex_$(EXT_MODE).spice to match $(CELL)_pex.sym..."; \
		python3 $(NET_PEX_DIR)/reorder_spice_pins.py $(SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice; \
	else \
		echo "No symbol $(SCH_DIR)/$(CELL)_pex.sym found, skipping pin reorder."; \
	fi
	sleep 4
.PHONY: magic-pex
# ================================================================================================


# Verify Targets
klayout-verify: ## Verify CELL cell with KLayout (usage: make klayout-verify [CELL=<cellname>])
	$(MAKE) klayout-lvs CELL=$(CELL)
	$(MAKE) klayout-drc CELL=$(CELL)
	$(MAKE) klayout-pex CELL=$(CELL)
.PHONY: klayout-verify

magic-verify: ## Verify CELL cell with Magic (usage: make magic-verify [CELL=<cellname>])
	$(MAKE) magic-lvs CELL=$(CELL)
	$(MAKE) magic-drc CELL=$(CELL)
	$(MAKE) magic-pex CELL=$(CELL)
.PHONY: magic-verify
# ================================================================================================


# Simulate, Build and Verify All Target
all: ## Simulate, build and verify the whole chip
	$(MAKE) sim-all
	$(MAKE) build-all
	$(MAKE) magic-drc CELL=$(TOP)
	$(MAKE) magic-drc CELL=$(TOP)_logo_fill
#	$(MAKE) klayout-verify
#	$(MAKE) magic-verify
.PHONY: all
# ================================================================================================


# Release Target
release: ## Copy the gds, netlist files and chip renders to the release folder (usage: make release VERSION=<version>)
	mkdir -p $(RELEASE_DIR)/v.$(VERSION)/gds
	mkdir -p $(RELEASE_DIR)/v.$(VERSION)/netlist
	mkdir -p $(RELEASE_DIR)/v.$(VERSION)/img
	cp -f $(LAY_DIR)/$(TOP)_logo_fill.gds.gz $(RELEASE_DIR)/v.$(VERSION)/gds/$(TOP)_logo_fill.gds.gz
#	cp -r $(NET_SCH_DIR)/. $(RELEASE_DIR)/v.$(VERSION)/netlist/schematic
	cp -r $(NET_LAY_DIR)/. $(RELEASE_DIR)/v.$(VERSION)/netlist/layout
#	cp -r $(NET_PEX_DIR)/. $(RELEASE_DIR)/v.$(VERSION)/netlist/pex
	cp -r $(NET_PNL_DIR)/. $(RELEASE_DIR)/v.$(VERSION)/netlist/pnl
	cp -r $(NET_SPICE_DIR)/. $(RELEASE_DIR)/v.$(VERSION)/netlist/spice
	cp -f $(RENDER_IMG_DIR)/$(TOP)_black.png $(RELEASE_DIR)/v.$(VERSION)/img/$(TOP)_black.png
	cp -f $(RENDER_IMG_DIR)/$(TOP)_white.png $(RELEASE_DIR)/v.$(VERSION)/img/$(TOP)_white.png
	cp -f $(RENDER_IMG_DIR)/$(TOP)_librelane.png $(RELEASE_DIR)/v.$(VERSION)/img/$(TOP)_librelane.png
.PHONY: release
# ================================================================================================
