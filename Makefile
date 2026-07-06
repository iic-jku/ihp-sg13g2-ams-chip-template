# Makefile for an Open-Source Analog-Mixed Signal Chip Design Template for the ihp-sg13g2 Open-PDK.
#
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# Johannes Kepler University, Department for Integrated Circuits
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# ========================================================================

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

RUN_TAG = $(shell ls -1 $(LIBRELANE_DIR)/runs 2>/dev/null | tail -n 1)

# Variables
TOP = chip_top

.DEFAULT_GOAL := help

# Cell name for verification targets (default: top-level cell)
# Override with: make <target> CELL=<cellname>
CELL ?= $(TOP)

# PEX mode (1 = C-decoupled, 2 = C-coupled, 3 = full-RC)
# Override with: make <target> EXT_MODE=<1|2|3>
EXT_MODE ?= 1

# Floating-point precision (significant digits) for Xschem's ev function
# Override with: make <target> EV_PRECISION=<digits>
EV_PRECISION ?= 5

# Set the waveform viewer GTKWave or Surfer (default: gtkwave)
# Override with: make <target> WAVEFORM_VIEWER=<gtkwave|surfer>
WAVEFORM_VIEWER ?= gtkwave

# Version for release target
# Override with: make <target> VERSION=<version>
VERSION ?= 1.0.0

# Folder structure
XSCHEM_SCH_DIR  := schematic/xschem
XSCHEM_TB_DIR   := testbenches/xschem
COCOTB_DIR      := testbenches/cocotb
LAY_DIR         := layout
SCRIPTS_DIR     := scripts
SIM_PLOT_DIR    := scripts/plot_simulations
RENDER_IMG_DIR  := render/img
SRC_DIR         := rtl
IP_DIR          := ip
MACROS_DIR      := macros
RELEASE_DIR     := release
NET_SCH_DIR     := netlist/schematic
NET_LAY_DIR     := netlist/layout
NET_PEX_DIR     := netlist/pex
NET_PNL_DIR     := netlist/pnl
NET_NL_DIR      := netlist/nl
NET_SPICE_DIR   := netlist/spice
LVS_RPT_DIR     := verification/lvs
DRC_RPT_DIR     := verification/drc
REPORT_DIR      := verification/reports
LIBRELANE_DIR   := flow/librelane
FLOW_FINAL_DIR  := flow/final


# Help Target
help: ## Show this help message
	@echo 'Usage: make <target> [CELL=<cellname>] [EXT_MODE=<1|2|3>] [EV_PRECISION=<digits>] [WAVEFORM_VIEWER=<gtkwave|surfer>] [VERSION=<version>]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ''
	@echo 'CELL defaults to $(TOP). Override to verify subcells.'
	@echo 'EXT_MODE defaults to 3 (full-RC). 1=C-decoupled, 2=C-coupled.'
	@echo 'EV_PRECISION defaults to 5 significant digits for Xschem ev function.'
	@echo 'WAVEFORM_VIEWER defaults to gtkwave. Use surfer to launch Surfer instead.'
	@echo 'VERSION defaults to $(VERSION). Used by the release target.'
.PHONY: help
# ================================================================================================


# Git Submodule Target
init-submodules: ## Initialize and update git submodules (e.g. flow/artistic)
	git -C $(MAKEFILE_DIR) submodule update --init
.PHONY: init-submodules
# ================================================================================================


# Simulation Targets
sim-rtl-cocotb: ## Run RTL simulation of CELL cell with cocotb (usage: make sim-rtl-cocotb [CELL=<cellname>])
	cd $(COCOTB_DIR) && python3 $(CELL)_tb.py
.PHONY: sim-rtl-cocotb

sim-gl-cocotb: ## Run gate-level simulation of CELL cell with cocotb (usage: make sim-gl-cocotb [CELL=<cellname>])
	cd $(COCOTB_DIR) && GL=1 python3 $(CELL)_tb.py
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
	cd $(XSCHEM_TB_DIR) && xschem -s -r -x -q --rcfile xschemrc --command ' \
		set netlist_dir $(abspath $(XSCHEM_TB_DIR)/simulations); \
		xschem save; \
		xschem netlist; \
		xschem simulate \
	' $(CELL)_tb_tran.sch
.PHONY: sim-gl-xschem

sim-view-xschem: ## Plot Xschem simulation results (usage: make sim-view-xschem CELL=<cellname>)
	python3 $(SIM_PLOT_DIR)/plot_$(CELL).py
.PHONY: sim-view-xschem

sim-all: ## Simulate the chip (RTL/GL cocotb + GL Xschem)
	$(MAKE) sim-rtl-cocotb
#	$(MAKE) sim-view-cocotb
	$(MAKE) sim-gl-cocotb
#	$(MAKE) sim-view-cocotb
#	$(MAKE) sim-gl-xschem
#	$(MAKE) sim-view-xschem
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
# TODO: KLayout antenna and DRC reports are temporarily commented out until
# IHP fixes the `metal1_pin_offgrid` errors. For now, `make librelane-nodrc` must be used.
# https://github.com/IHP-GmbH/IHP-Open-PDK/issues/683#issuecomment-4065791975
copy-reports: ## Copy yosys, antenna, hold & setup timing, LVS and manufacturability reports from the last LibreLane run to verification/reports/
	rm -rf $(REPORT_DIR)/
	mkdir -p $(REPORT_DIR)/
	# Using * wildcard to ignore step numbers
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/pre_synth_chk.rpt $(REPORT_DIR)/yosys_synth_check.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/pre_techmap.rpt $(REPORT_DIR)/yosys_pre_techmap.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/post_dff.rpt $(REPORT_DIR)/yosys_post_dff.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/stat.rpt $(REPORT_DIR)/stat.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-checkantennas-1/reports/antenna.rpt $(REPORT_DIR)/antenna_violations.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-checkantennas-1/reports/antenna_summary.rpt $(REPORT_DIR)/antenna_summary.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/summary.rpt $(REPORT_DIR)/hold_setup_timing.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/summary.rpt $(REPORT_DIR)/stapostpnr_summary.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_fast_1p32V_m40C/power.rpt $(REPORT_DIR)/stapostpnr_nom_fast_1p32V_m40C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_fast_1p65V_m40C/power.rpt $(REPORT_DIR)/stapostpnr_nom_fast_1p65V_m40C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_slow_1p08V_125C/power.rpt $(REPORT_DIR)/stapostpnr_nom_slow_1p08V_125C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_slow_1p35V_125C/power.rpt $(REPORT_DIR)/stapostpnr_nom_slow_1p35V_125C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_typ_1p20V_25C/power.rpt $(REPORT_DIR)/stapostpnr_nom_typ_1p20V_25C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_typ_1p50V_25C/power.rpt $(REPORT_DIR)/stapostpnr_nom_typ_1p50V_25C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-irdropreport/irdrop.rpt $(REPORT_DIR)/irdrop.rpt
# 	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-magic-drc/reports/drc.magic.rpt $(REPORT_DIR)/drc.magic.rpt
# 	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-klayout-drc/reports/drc.klayout.json $(REPORT_DIR)/drc.klayout.json
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-netgen-lvs/reports/lvs.netgen.rpt $(REPORT_DIR)/lvs.netgen.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-misc-reportmanufacturability/manufacturability.rpt $(REPORT_DIR)/manufacturability.rpt
.PHONY: copy-reports

copy-gds: ## Copy and compress final GDS from the last LibreLane run to layout/ (no logo & filler)
	rm -f $(LAY_DIR)/$(TOP).gds.gz
	mkdir -p $(LAY_DIR)/
	cp -r $(FLOW_FINAL_DIR)/gds/$(TOP).gds $(LAY_DIR)/$(TOP).gds
	gzip $(LAY_DIR)/$(TOP).gds
.PHONY: copy-gds

copy-netlist: ## Copy final spice, pnl and nl netlists from the last LibreLane run to netlist/
	rm -rf $(NET_SPICE_DIR)/
	mkdir -p $(NET_SPICE_DIR)/
	cp -r $(FLOW_FINAL_DIR)/spice/$(TOP).spice $(NET_SPICE_DIR)/$(TOP).spice

	rm -rf $(NET_PNL_DIR)/
	mkdir -p $(NET_PNL_DIR)/
	cp -r $(FLOW_FINAL_DIR)/pnl/$(TOP).pnl.v $(NET_PNL_DIR)/$(TOP).pnl.v

	rm -rf $(NET_NL_DIR)/
	mkdir -p $(NET_NL_DIR)/
	cp -r $(FLOW_FINAL_DIR)/nl/$(TOP).nl.v $(NET_NL_DIR)/$(TOP).nl.v
.PHONY: copy-netlist

copy-render: ## Copy chip render from the last LibreLane run (no logo & fillers) to render/img/
	mkdir -p $(RENDER_IMG_DIR)/
	cp -r $(FLOW_FINAL_DIR)/render/$(TOP).png $(RENDER_IMG_DIR)/$(TOP)_librelane.png
.PHONY: copy-render
# ================================================================================================


# Render Target
render-gds: ## Render an image from the final GDS (with logo and filler) using lay2img.py
	mkdir -p $(RENDER_IMG_DIR)/
	python3 $(SCRIPTS_DIR)/lay2img.py $(LAY_DIR)/$(TOP)_logo_fill.gds.gz $(RENDER_IMG_DIR)/$(TOP).png --width 2048 --oversampling 4
.PHONY: render-gds
# ================================================================================================


# Build Targets
build-bondpad: ## Build the bondpad in ip/sg13g2_ip__bondpad_70x70/
	@$(MAKE) -C $(IP_DIR)/sg13g2_ip__bondpad_70x70 all
.PHONY: build-bondpad

build-logos: ## Build the logos in ip/sg13g2_ip__jku/ and ip/sg13g2_ip__jku_names/
	@$(MAKE) -C $(IP_DIR)/sg13g2_ip__jku all
	@$(MAKE) -C $(IP_DIR)/sg13g2_ip__jku_names all
.PHONY: build-logos

build-counter: ## Build the counter macro
	@$(MAKE) -C $(MACROS_DIR)/counter all
.PHONY: build-counter

build-inverter: ## Build the inverter macro
	@$(MAKE) -C $(MACROS_DIR)/inverter all
.PHONY: build-inverter

build-macros: ## Build all enabled macros (counter and inverter)
	$(MAKE) build-counter
	$(MAKE) build-inverter
.PHONY: build-macros

# Adds the chip logo and fill structures to the final GDS.
# TODO: This step is temporary and will be replaced by a custom LibreLane step in the future.
add-logo-fill: ## Run scripts/add_logo_fill.sh to add the chip logo and fill structures
	cd $(SCRIPTS_DIR) && ./add_logo_fill.sh
.PHONY: add-logo-fill

# TODO: `make librelane-nodrc` is used for now until IHP fixes the `metal1_pin_offgrid` errors.
# Once fixed, switch back to `make librelane`.
build-top: ## Build the chip (LibreLane, copy reports/GDS/netlist/render, add logo & filler, render final GDS)
	$(MAKE) librelane-nodrc
	$(MAKE) copy-reports
	$(MAKE) copy-gds
	$(MAKE) copy-netlist
	$(MAKE) copy-render
	$(MAKE) add-logo-fill
	$(MAKE) render-gds
#	$(MAKE) librelane-openroad
.PHONY: build-top

build-all: ## Build the bondpad, logos, macros and the chip top-level
	$(MAKE) init-submodules
	$(MAKE) build-bondpad
	$(MAKE) build-logos
	$(MAKE) build-macros
	$(MAKE) build-top
.PHONY: build-all
# ================================================================================================


# LVS Targets
klayout-lvs-netlist: ## Export CDL schematic netlist from Xschem for KLayout LVS (usage: make klayout-lvs-netlist [CELL=<cellname>] [EV_PRECISION=<digits>])
	mkdir -p $(NET_SCH_DIR)
	xschem -s -r -x -q --rcfile $(XSCHEM_SCH_DIR)/xschemrc --command ' \
		set spiceprefix 1; \
		set lvs_netlist 1; \
		set top_is_subckt 1; \
		set lvs_ignore 0; \
		set ev_precision $(EV_PRECISION); \
		set netlist_dir $(NET_SCH_DIR); \
		xschem set netlist_name [file tail [file rootname [xschem get current_name]]]_klayout.cdl; \
		xschem netlist \
	' $(XSCHEM_SCH_DIR)/$(CELL).sch
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
	xschem -s -r -x -q --rcfile $(XSCHEM_SCH_DIR)/xschemrc --command ' \
		set spiceprefix 1; \
		set lvs_netlist 0; \
		set top_is_subckt 1; \
		set lvs_ignore 1; \
		set ev_precision $(EV_PRECISION); \
		set netlist_dir $(NET_SCH_DIR); \
		xschem set netlist_name [file tail [file rootname [xschem get current_name]]]_magic.spice; \
		xschem netlist \
	' $(XSCHEM_SCH_DIR)/$(CELL).sch
.PHONY: magic-lvs-netlist

magic-lvs: ## Run Magic + Netgen LVS of the CELL cell (usage: make magic-lvs [CELL=<cellname>])
	mkdir -p $(LVS_RPT_DIR)
	mkdir -p $(NET_LAY_DIR)
	$(MAKE) magic-lvs-netlist CELL=$(CELL)
	sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(NET_SCH_DIR)/$(CELL)_magic.spice -l $(LAY_DIR)/$(CELL).gds.gz -c $(CELL)
# 	Alternative using sak-lvs.sh for netlist export and LVS in one step (replaces magic-lvs-netlist target):
#   sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(XSCHEM_SCH_DIR)/$(CELL).sch -l $(LAY_DIR)/$(CELL).gds.gz -c $(CELL)
	mv $(LVS_RPT_DIR)/$(CELL).ext.spc $(NET_LAY_DIR)/$(CELL)_magic.ext.spc
	rm -f $(LVS_RPT_DIR)/$(CELL).sch.spc
	rm -f $(LVS_RPT_DIR)/ext_$(CELL).tcl
	rm -f $(LVS_RPT_DIR)/*.ext
	sleep 4
.PHONY: magic-lvs
# ================================================================================================


# DRC Targets
klayout-drc-minimum: ## Run minimum pre-check KLayout DRC of the TOP cell with logo and filler
	mkdir -p $(DRC_RPT_DIR)
	python3 $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/run_drc.py \
		--path=$(LAY_DIR)/$(TOP)_logo_fill.gds.gz \
		--topcell=$(TOP) \
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

klayout-drc-regular: ## Run regular KLayout DRC of the TOP cell with logo and filler
	mkdir -p $(DRC_RPT_DIR)
	python3 $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/run_drc.py \
		--path=$(LAY_DIR)/$(TOP)_logo_fill.gds.gz \
		--topcell=$(TOP) \
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
	--schematic $(XSCHEM_SCH_DIR)/$(CELL).sch \
	--gds $(LAY_DIR)/$(CELL).gds.gz \
	--magic \
	--magic_mode $$KPEX_MODE \
	--out_dir $(NET_PEX_DIR) \
	--out_spice $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice
#	--2.5D
#	--mode $$KPEX_MODE
	sed -i 's/$(CELL)/$(CELL)_pex/g' $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice
	rm -rf $(NET_PEX_DIR)/$(CELL)__$(CELL)
	rm -f $(CELL).nodes $(CELL).sim
	@if [ -f $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym ]; then \
		echo "Reordering pins in $(CELL)_klayout_pex_$(EXT_MODE).spice to match $(CELL)_pex.sym..."; \
		python3 $(SCRIPTS_DIR)/reorder_spice_pins.py $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice; \
	else \
		echo "No symbol $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym found, skipping pin reorder."; \
	fi
	sleep 4
.PHONY: klayout-pex

magic-pex: ## Run Parasitic Extraction with Magic of the CELL cell (usage: make magic-pex [CELL=<cellname>] [EXT_MODE=<1|2|3>])
	mkdir -p $(NET_PEX_DIR)
	sak-pex.sh -d -m $(EXT_MODE) -w $(NET_PEX_DIR) $(LAY_DIR)/$(CELL).gds.gz
	mv $(NET_PEX_DIR)/$(CELL).pex.spice $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice
	sed -i 's/$(CELL)/$(CELL)_pex/g' $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice
	rm -f $(NET_PEX_DIR)/pex_$(CELL).tcl $(NET_PEX_DIR)/$(CELL).ext $(NET_PEX_DIR)/$(CELL).res.ext
	@if [ -f $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym ]; then \
		echo "Reordering pins in $(CELL)_magic_pex_$(EXT_MODE).spice to match $(CELL)_pex.sym..."; \
		python3 $(SCRIPTS_DIR)/reorder_spice_pins.py $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice; \
	else \
		echo "No symbol $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym found, skipping pin reorder."; \
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
all: ## Simulate, build and verify the chip
	$(MAKE) sim-all
	$(MAKE) build-all
	$(MAKE) magic-drc CELL=$(TOP)
	$(MAKE) magic-drc CELL=$(TOP)_logo_fill
#	$(MAKE) klayout-verify
#	$(MAKE) magic-verify
.PHONY: all
# ================================================================================================


# Release Target
release: ## Copy GDS, netlists and chip renders to release/v.<VERSION>/ (usage: make release [VERSION=<version>])
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


# Regression Target
regression: ## Regression test target for IIC-OSIC-TOOLS
# 	Analog macro: inverter (Xschem + CACE + LVS/DRC/PEX + build-top)
	$(MAKE) -C $(MACROS_DIR)/inverter sim-xschem TB=inverter_tb_dc_vout
	# ONE CACE run: the lightweight AC VDD sweep (no Monte-Carlo) to keep runtime short.
	cd $(MACROS_DIR)/inverter/verification/cace && cace inverter.yaml -p ac_params && rm -rf _runs _docs netlist
# 	KLayout & Magic LVS, DRC and PEX of the inverter_top cell.
	$(MAKE) -C $(MACROS_DIR)/inverter klayout-verify CELL=inverter_top
	$(MAKE) -C $(MACROS_DIR)/inverter magic-verify CELL=inverter_top
	$(MAKE) -C $(MACROS_DIR)/inverter build-top

# 	Digital macro: counter (Verilator, Icarus, cocotb, yosys/FPGA, LibreLane, xspice)
	$(MAKE) -C $(MACROS_DIR)/counter lint-verilog-all
	$(MAKE) -C $(MACROS_DIR)/counter sim-rtl-verilog
	$(MAKE) -C $(MACROS_DIR)/counter sim-rtl-cocotb
	$(MAKE) -C $(MACROS_DIR)/counter build-fpga
# 	librelane-magicdrc: full RTL-to-GDS. KLayout DRC skipped for runtime.
	$(MAKE) -C $(MACROS_DIR)/counter librelane-magicdrc
	$(MAKE) -C $(MACROS_DIR)/counter copy-final
# 	Gate-level flows that depend on the LibreLane outputs above.
	$(MAKE) -C $(MACROS_DIR)/counter sim-gl-cocotb
	$(MAKE) -C $(MACROS_DIR)/counter generate-xspice
	$(MAKE) -C $(MACROS_DIR)/counter sim-gl-xschem

# 	Top-level assembly
	$(MAKE) init-submodules
	$(MAKE) build-bondpad
	$(MAKE) -C $(IP_DIR)/sg13g2_ip__jku all
	# librelane-nodrc: full RTL-to-GDS. DRC is skipped for runtime.
	$(MAKE) librelane-nodrc
.PHONY: regression
# ================================================================================================
