# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

RUN_TAG = $(shell ls -1 $(LIBRELANE_DIR)/runs 2>/dev/null | tail -n 1)

# Variables
TOP = counter_top

.DEFAULT_GOAL := help

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
COCOTB_DIR      	  := testbenches/cocotb
VERILOG_TB_DIR        := testbenches/verilog
XSCHEM_TB_DIR         := testbenches/xschem
SCH_DIR               := schematic
SCRIPTS_DIR     	  := scripts
SRC_DIR 			  := rtl
RENDER_IMG_DIR        := render/img
NET_LAY_DIR           := netlist/layout
NET_PEX_DIR           := netlist/pex
NET_NL_DIR            := netlist/nl
NET_PNL_DIR           := netlist/pnl
NET_SPICE_DIR         := netlist/spice
XSPICE_DIR            := netlist/xspice
LVS_RPT_DIR           := verification/lvs
DRC_RPT_DIR           := verification/drc
LIBRELANE_DIR         := flow/librelane
FLOW_REPORT_DIR       := flow/reports
FLOW_FINAL_DIR        := flow/final
FLOW_FINAL_GDS_DIR    := flow/final/gds
FLOW_FINAL_LEF_DIR    := flow/final/lef
FLOW_FINAL_LIB_DIR    := flow/final/lib
FLOW_FINAL_NL_DIR     := flow/final/nl
FLOW_FINAL_PNL_DIR    := flow/final/pnl
FLOW_FINAL_SPEF_DIR   := flow/final/spef
FLOW_FINAL_SPICE_DIR  := flow/final/spice
FLOW_FINAL_VH_DIR     := flow/final/vh
FLOW_FINAL_RENDER_DIR := flow/final/render
FINAL_GDS_DIR         := final/gds
FINAL_LEF_DIR         := final/lef
FINAL_LIB_DIR         := final/lib
FINAL_NL_DIR          := final/nl
FINAL_PNL_DIR         := final/pnl
FINAL_SPEF_DIR        := final/spef
FINAL_VH_DIR          := final/vh

# Variables for simulation and linting targets
# constants.sv defines the counter_pkg and must compile before any module that imports it,
# so it is always prepended in MODULES_SIM and in the single-cell branches below.
MODULES_SYNTH := \
	$(SRC_DIR)/counter.sv \
	$(SRC_DIR)/counter_top.sv

MODULES_SIM :=  \
	$(SRC_DIR)/constants.sv \
	$(MODULES_SYNTH)

# Source files for sim-rtl-verilog: auto-selects MODULES_SIM when CELL == TOP, single-file otherwise (auto-detecting .sv/.v)
_SIM_SRCS = $(if $(filter $(CELL),$(TOP)),$(MODULES_SIM),$(or $(wildcard $(SRC_DIR)/$(CELL).sv),$(SRC_DIR)/$(CELL).v))

# Source files for lint-verilog: constants + all synthesis sources for TOP, single-file (auto-detecting .sv/.v) otherwise
_LINT_SRCS = $(if $(filter $(CELL),$(TOP)),$(SRC_DIR)/constants.sv $(MODULES_SYNTH),$(SRC_DIR)/constants.sv $(or $(wildcard $(SRC_DIR)/$(CELL).sv),$(SRC_DIR)/$(CELL).v))

# Testbench extension: sv for TOP, v otherwise (dot is added at use site)
_TB_EXT = $(if $(filter $(CELL),$(TOP)),sv,v)


# Help Target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
.PHONY: help
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


# Simulation Targets
sim-rtl-verilog: ## Run RTL simulation of CELL cell with Icarus Verilog (usage: make sim-rtl-verilog [CELL=<cellname>])
	iverilog -g2012 -DSIM -o $(VERILOG_TB_DIR)/test_$(CELL) $(_SIM_SRCS) $(VERILOG_TB_DIR)/$(CELL)_tb.$(_TB_EXT)
	cd $(VERILOG_TB_DIR) && vvp test_$(CELL)
	rm -f $(VERILOG_TB_DIR)/test_$(CELL)
.PHONY: sim-rtl-verilog

sim-view-verilog: ## View CELL cell Verilog simulation waveforms (usage: make sim-view-verilog [CELL=<cellname>] [WAVEFORM_VIEWER=<gtkwave|surfer>])
	@if [ "$(WAVEFORM_VIEWER)" = "gtkwave" ]; then \
		$(WAVEFORM_VIEWER) $(VERILOG_TB_DIR)/$(CELL)_tb.vcd $(VERILOG_TB_DIR)/$(CELL)_tb.gtkw; \
	elif [ "$(WAVEFORM_VIEWER)" = "surfer" ]; then \
		$(WAVEFORM_VIEWER) -s $(VERILOG_TB_DIR)/$(CELL)_tb.surf.ron $(VERILOG_TB_DIR)/$(CELL)_tb.vcd; \
	else \
		$(WAVEFORM_VIEWER) $(VERILOG_TB_DIR)/$(CELL)_tb.vcd; \
	fi
.PHONY: sim-view-verilog

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
	cd $(XSCHEM_TB_DIR) && xschem -x -q --rcfile xschemrc --command ' \
		set netlist_dir $(abspath $(XSCHEM_TB_DIR)/simulations); \
		xschem save; \
		xschem netlist; \
		xschem simulate \
	' $(CELL)_tb_tran.sch
.PHONY: sim-gl-xschem

sim-plot-xschem: ## Plot Xschem simulation results (usage: make sim-plot-xschem CELL=<cellname>)
	python3 $(SIM_PLOT_DIR)/plot_$(CELL).py
.PHONY: sim-plot-xschem

sim-all: ## Simulate the macro (RTL Verilog + RTL/GL cocotb + GL Xschem for counter_top)
	$(MAKE) sim-rtl-verilog
#	$(MAKE) sim-view-verilog
	$(MAKE) sim-rtl-cocotb
#	$(MAKE) sim-view-cocotb
	$(MAKE) sim-gl-cocotb
#	$(MAKE) sim-view-cocotb
	$(MAKE) sim-gl-xschem
#	$(MAKE) sim-plot-xschem
.PHONY: sim-all
# ================================================================================================


# LibreLane Targets
librelane: ## Run LibreLane with Magic and KLayout DRC checks.
	librelane $(LIBRELANE_DIR)/config.yaml --pdk ${PDK} --pdk-root ${PDK_ROOT} --manual-pdk --save-views-to $(FLOW_FINAL_DIR)/
.PHONY: librelane

librelane-nodrc: ## Run LibreLane without DRC checks
	librelane $(LIBRELANE_DIR)/config.yaml --pdk ${PDK} --pdk-root ${PDK_ROOT} --manual-pdk --save-views-to $(FLOW_FINAL_DIR)/ --skip KLayout.DRC --skip Magic.DRC
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
copy-reports: ## Copy yosys, antenna violations, hold & setup timing and manufacturability reports
	rm -rf $(FLOW_REPORT_DIR)/
	mkdir -p $(FLOW_REPORT_DIR)/
	# Using * wildcard to ignore step numbers
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/pre_synth_chk.rpt $(FLOW_REPORT_DIR)/yosys_synth_check.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/pre_techmap.rpt $(FLOW_REPORT_DIR)/yosys_pre_techmap.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/post_dff.rpt $(FLOW_REPORT_DIR)/yosys_post_dff.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/stat.rpt $(FLOW_REPORT_DIR)/stat.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-checkantennas-1/reports/antenna.rpt $(FLOW_REPORT_DIR)/antenna_violations.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-checkantennas-1/reports/antenna_summary.rpt $(FLOW_REPORT_DIR)/antenna_summary.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/summary.rpt $(FLOW_REPORT_DIR)/stapostpnr_summary.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_fast_1p32V_m40C/power.rpt $(FLOW_REPORT_DIR)/stapostpnr_nom_fast_1p32V_m40C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_fast_1p65V_m40C/power.rpt $(FLOW_REPORT_DIR)/stapostpnr_nom_fast_1p65V_m40C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_slow_1p08V_125C/power.rpt $(FLOW_REPORT_DIR)/stapostpnr_nom_slow_1p08V_125C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_slow_1p35V_125C/power.rpt $(FLOW_REPORT_DIR)/stapostpnr_nom_slow_1p35V_125C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_typ_1p20V_25C/power.rpt $(FLOW_REPORT_DIR)/stapostpnr_nom_typ_1p20V_25C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_typ_1p50V_25C/power.rpt $(FLOW_REPORT_DIR)/stapostpnr_nom_typ_1p50V_25C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-irdropreport/irdrop.rpt $(FLOW_REPORT_DIR)/irdrop.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-magic-drc/reports/drc.magic.rpt $(FLOW_REPORT_DIR)/drc.magic.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-klayout-drc/reports/drc.klayout.json $(FLOW_REPORT_DIR)/drc.klayout.json
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-netgen-lvs/reports/lvs.netgen.rpt $(FLOW_REPORT_DIR)/lvs.netgen.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-misc-reportmanufacturability/manufacturability.rpt $(FLOW_REPORT_DIR)/manufacturability.rpt
.PHONY: copy-reports

copy-final: ## Copy final output gds, lef, lib, nl, pnl, spef, and vh folders from the last LibreLane run to final/
	rm -rf $(FINAL_GDS_DIR)/ $(FINAL_LEF_DIR)/ $(FINAL_LIB_DIR)/ $(FINAL_NL_DIR)/ $(FINAL_PNL_DIR)/ $(FINAL_SPEF_DIR)/ $(FINAL_VH_DIR)/
	cp -r $(FLOW_FINAL_GDS_DIR)  $(FINAL_GDS_DIR)
	cp -r $(FLOW_FINAL_LEF_DIR)  $(FINAL_LEF_DIR)
	cp -r $(FLOW_FINAL_LIB_DIR)  $(FINAL_LIB_DIR)
	cp -r $(FLOW_FINAL_NL_DIR)   $(FINAL_NL_DIR)
	cp -r $(FLOW_FINAL_PNL_DIR)  $(FINAL_PNL_DIR)
	cp -r $(FLOW_FINAL_SPEF_DIR) $(FINAL_SPEF_DIR)
	cp -r $(FLOW_FINAL_VH_DIR)   $(FINAL_VH_DIR)
.PHONY: copy-final

copy-netlist: ## Copy final output spice, pnl and nl netlists from the last LibreLane run to netlist/
	rm -rf $(NET_SPICE_DIR)/
	mkdir -p $(NET_SPICE_DIR)/
	cp -r $(FLOW_FINAL_SPICE_DIR)/${TOP}.spice $(NET_SPICE_DIR)/${TOP}.spice

	rm -rf $(NET_PNL_DIR)/
	mkdir -p $(NET_PNL_DIR)/
	cp -r $(FLOW_FINAL_PNL_DIR)/${TOP}.pnl.v $(NET_PNL_DIR)/${TOP}.pnl.v

	rm -rf $(NET_NL_DIR)/
	mkdir -p $(NET_NL_DIR)/
	cp -r $(FLOW_FINAL_NL_DIR)/${TOP}.nl.v $(NET_NL_DIR)/${TOP}.nl.v
.PHONY: copy-netlist

copy-render: ## Copy macro render from the last LibreLane run to render/img/
	mkdir -p $(RENDER_IMG_DIR)/
	cp -r $(FLOW_FINAL_RENDER_DIR)/${TOP}.png $(RENDER_IMG_DIR)/${TOP}_librelane.png
.PHONY: copy-render
# ================================================================================================

# Render Target
render-gds: ## Render an image from the final GDS using lay2img.py
	mkdir -p $(RENDER_IMG_DIR)/
	python3 $(SCRIPTS_DIR)/lay2img.py $(FINAL_GDS_DIR)/${TOP}.gds $(RENDER_IMG_DIR)/${TOP}.png --width 2048 --oversampling 4
.PHONY: render-gds
# ================================================================================================


# Build Targets
build-fpga: ## Build target for FPGA usage
	@$(MAKE) -C fpga all
.PHONY: build-fpga

build-top: ## Build macro (run LibreLane with KLayout & Magic DRC checks, copy reports, copy final files, copy netlists, copy render, and render final GDS)
	$(MAKE) librelane
	$(MAKE) copy-reports
	$(MAKE) copy-final
	$(MAKE) copy-netlist
	$(MAKE) copy-render
	$(MAKE) render-gds
#	$(MAKE) librelane-openroad
.PHONY: build-top
# ================================================================================================


# LVS & DRC Verification Targets
# The LibreLane flow already includes LVS and DRC checks with Magic and KLayout, and they are saved in the flow/reports folder.
# ================================================================================================


# Simulate, Build and Verify All Target
all: ## Simulate, build and verify the macro
	$(MAKE) lint-verilog-all
	$(MAKE) sim-all
	$(MAKE) build-fpga
	$(MAKE) build-top
.PHONY: all
# ================================================================================================


# The following commands are for generating an XSPICE file for mixed-signal simulation in Xschem.
# Note that these commands should not be run in `all`, since this XSPICE file is generated once with specific CPU settings for a more convenient simulation.
# Note that this method does not work with the .pnl.v file in the flow/final/ folder. The .nl.v file from the LibreLane step yosys-synthesis has to be used.
# Conversion pipeline: Copy gate-level Verilog (.nl.v) -> Verilog with power pins (.vp) -> SPICE (.spice) -> XSPICE (.xspice) -> Reorder pins in XSPICE file according to the Xschem symbol
generate-xspice: ## Generate XSPICE model from gate-level Verilog netlist
	mkdir -p $(XSPICE_DIR)
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/${TOP}.nl.v $(XSPICE_DIR)/${TOP}_xspice.nl.v
	vlog2Verilog $(XSPICE_DIR)/${TOP}_xspice.nl.v -o $(XSPICE_DIR)/${TOP}.vp -l $(PDK_ROOT)/$(PDK)/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef -v "VPWR,VPB" -g "VGND,VNB"
	vlog2Spice $(XSPICE_DIR)/${TOP}.vp -l $(PDK_ROOT)/$(PDK)/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice -o $(XSPICE_DIR)/${TOP}.spice
	python3 $(SCRIPTS_DIR)/spi2xspice.py $(PDK_ROOT)/$(PDK)/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p50V_25C.lib -io_time=500p -time=50p -idelay=5p -odelay=50p -cload=250f $(XSPICE_DIR)/${TOP}.spice $(XSPICE_DIR)/${TOP}.xspice
	python3 $(SCRIPTS_DIR)/reorder_xspice_pins.py $(SCH_DIR)/${TOP}.sym $(XSPICE_DIR)/${TOP}.xspice
	rm -f $(XSPICE_DIR)/${TOP}_xspice.nl.v $(XSPICE_DIR)/${TOP}.vp $(XSPICE_DIR)/${TOP}.spice
.PHONY: generate-xspice
# ================================================================================================
