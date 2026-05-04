# SPDX-FileCopyrightText: 2025-2026 The Chip Team
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
LAY_DIR               := final/gds
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
FLOW_FINAL_NL_DIR     := flow/final/nl
FLOW_FINAL_PNL_DIR    := flow/final/pnl
FLOW_FINAL_SPICE_DIR  := flow/final/spice
FLOW_FINAL_RENDER_DIR := flow/final/render

# Variables for running the testbenches
RISCV_MODULES_SYNTH := \
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
	$(SRC_DIR)/imm_gen.sv \
	$(SRC_DIR)/riscv_top.sv

RISCV_MODULES_SIM :=  \
	$(SRC_DIR)/constants.sv \
	$(RISCV_MODULES_SYNTH) \
	$(SRC_DIR)/sram_sim.sv

# Source files for sim-rtl-verilog: auto-selects RISCV_MODULES_SIM when CELL == TOP, single-file otherwise
_SIM_SRCS = $(if $(filter $(CELL),$(TOP)),$(RISCV_MODULES_SIM),$(SRC_DIR)/$(CELL).v)

# Source files for lint-verilog: constants + all synthesis sources for TOP, single-file (auto-detecting .sv/.v) otherwise
_LINT_SRCS = $(if $(filter $(CELL),$(TOP)),$(SRC_DIR)/constants.sv $(RISCV_MODULES_SYNTH),$(SRC_DIR)/constants.sv $(or $(wildcard $(SRC_DIR)/$(CELL).sv),$(SRC_DIR)/$(CELL).v))

# Testbench extension: sv for TOP, v otherwise (dot is added at use site)
_TB_EXT   = $(if $(filter $(CELL),$(TOP)),sv,v)


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

lint-verilog-all: ## Lint all Verilog source files
	$(MAKE) lint-verilog CELL=dsmod
	$(MAKE) lint-verilog CELL=cordic_iterative
	$(MAKE) lint-verilog CELL=lo_gen
	$(MAKE) lint-verilog
.PHONY: lint-verilog-all
# ================================================================================================


# Simulation Targets
sim-rtl-verilog: ## Run RTL simulation of CELL cell with Verilog (usage: make sim-rtl-verilog [CELL=<cellname>])
	mkdir -p $(VERILOG_TB_DIR)/$(CELL)
	iverilog -g2012 -DSIM -o $(VERILOG_TB_DIR)/$(CELL)/test_$(CELL) $(_SIM_SRCS) $(VERILOG_TB_DIR)/$(CELL)/$(CELL)_tb.$(_TB_EXT)
	cd $(VERILOG_TB_DIR)/$(CELL) && vvp test_$(CELL)
	rm -f $(VERILOG_TB_DIR)/$(CELL)/test_$(CELL)
.PHONY: sim-rtl-verilog

sim-view-verilog: ## View CELL cell Verilog simulation waveforms (usage: make sim-view-verilog [CELL=<cellname>] [WAVEFORM_VIEWER=<gtkwave|surfer>])
	@if [ "$(WAVEFORM_VIEWER)" = "gtkwave" ]; then \
		$(WAVEFORM_VIEWER) $(VERILOG_TB_DIR)/$(CELL)/$(CELL)_tb.vcd $(VERILOG_TB_DIR)/$(CELL)/$(CELL)_tb.gtkw; \
	elif [ "$(WAVEFORM_VIEWER)" = "surfer" ]; then \
		$(WAVEFORM_VIEWER) -s $(VERILOG_TB_DIR)/$(CELL)/$(CELL)_tb.surf.ron $(VERILOG_TB_DIR)/$(CELL)/$(CELL)_tb.vcd; \
	else \
		$(WAVEFORM_VIEWER) $(VERILOG_TB_DIR)/$(CELL)/$(CELL)_tb.vcd; \
	fi
.PHONY: sim-view-verilog

sim-rtl-cocotb: ## Run RTL simulation of CELL cell with cocotb (usage: make sim-rtl-cocotb [CELL=<cellname>])
	@if [ "$(CELL)" = "dsmod" ]; then \
		$(MAKE) -C $(COCOTB_DIR)/$(CELL) all; \
	else \
		cd $(COCOTB_DIR)/$(CELL); python3 $(CELL)_tb.py; \
	fi
.PHONY: sim-rtl-cocotb

sim-gl-cocotb: ## Run gate-level simulation of CELL cell with cocotb (usage: make sim-gl-cocotb [CELL=<cellname>])
	cd $(COCOTB_DIR)/$(CELL); GL=1 python3 $(CELL)_tb.py
.PHONY: sim-gl-cocotb

sim-view-cocotb: ## View CELL cell cocotb simulation waveforms (usage: make sim-view-cocotb [CELL=<cellname>] [WAVEFORM_VIEWER=<gtkwave|surfer>])
	@if [ "$(WAVEFORM_VIEWER)" = "gtkwave" ]; then \
		$(WAVEFORM_VIEWER) $(COCOTB_DIR)/$(CELL)/sim_build/$(CELL).fst $(COCOTB_DIR)/$(CELL)/$(CELL)_tb.gtkw; \
	elif [ "$(WAVEFORM_VIEWER)" = "surfer" ]; then \
		$(WAVEFORM_VIEWER) -s $(COCOTB_DIR)/$(CELL)/$(CELL)_tb.surf.ron $(COCOTB_DIR)/$(CELL)/sim_build/$(CELL).fst; \
	else \
		$(WAVEFORM_VIEWER) $(COCOTB_DIR)/$(CELL)/sim_build/$(CELL).fst; \
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

sim-all: ## Simulate the macro
	$(MAKE) sim-rtl-verilog CELL=dsmod
	$(MAKE) sim-rtl-cocotb CELL=dsmod
	$(MAKE) sim-rtl-verilog
	$(MAKE) sim-rtl-cocotb
	$(MAKE) sim-gl-cocotb
	$(MAKE) sim-gl-xschem
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
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/summary.rpt $(FLOW_REPORT_DIR)/hold_setup_timing.rpt
# 	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-klayout-antenna/reports/antenna.klayout.json $(FLOW_REPORT_DIR)/antenna.klayout.json
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-magic-drc/reports/drc.magic.rpt $(FLOW_REPORT_DIR)/drc.magic.rpt
# 	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-klayout-drc/reports/drc.klayout.json $(FLOW_REPORT_DIR)/drc.klayout.json
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-netgen-lvs/reports/lvs.netgen.rpt $(FLOW_REPORT_DIR)/lvs.netgen.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-misc-reportmanufacturability/manufacturability.rpt $(FLOW_REPORT_DIR)/manufacturability.rpt
.PHONY: copy-reports

copy-gds: ## Copy final output GDS from the last LibreLane run to final/gds/
	rm -rf $(LAY_DIR)/
	mkdir -p $(LAY_DIR)/
	cp -r $(FLOW_FINAL_GDS_DIR)/${TOP}.gds $(LAY_DIR)/${TOP}.gds
.PHONY: copy-gds

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
	python3 $(SCRIPTS_DIR)/lay2img.py $(LAY_DIR)/${TOP}.gds $(RENDER_IMG_DIR)/${TOP}.png --width 2048 --oversampling 4
.PHONY: render-gds
# ================================================================================================


# Build Targets
build-fpga: ## Build target for FPGA usage (run simulation, synthesis, place & route, generate bitstream and flash bitstream)
	@$(MAKE) -C fpga all
.PHONY: build-fpga

build-all: ## Build macro (run LibreLane with only Magic DRC checks, copy reports, copy GDS, copy netlists, copy render, and render final GDS)
	$(MAKE) librelane-magicdrc
	$(MAKE) copy-reports
	$(MAKE) copy-gds
	$(MAKE) copy-netlist
	$(MAKE) copy-render
	$(MAKE) render-gds
#	$(MAKE) librelane-openroad
.PHONY: build-all
# ================================================================================================


# LVS & DRC Verification Targets
# The LibreLane flow already includes LVS and DRC checks with Magic and KLayout, and they are saved in the flow/reports folder.
# ================================================================================================


# Simulate, Build and Verify All Target
all: ## Simulate, build and verify the macro
	$(MAKE) lint-verilog-all
	$(MAKE) sim-all
	$(MAKE) build-all
.PHONY: all
# ================================================================================================


# The following commands are for generating an XSPICE file for mixed-signal simulation in Xschem.
# Note that these commands should not be run in `all`, since this XSPICE file is generated once with specific CPU settings for a more convenient simulation.
# Note that this method does not work with the .pnl.v file in the flow/final/ folder. The .nl.v file from the LibreLane step yosys-synthesis has to be used.
# Conversion pipeline: Copy gate-level Verilog (.nl.v) -> Verilog with power pins (.vp) -> SPICE (.spice) -> XSPICE (.xspice) -> Reorder pins in XSPICE file according to the Xschem symbol
generate-xspice: ## Generate XSPICE model from gate-level Verilog netlist
	rm -rf $(XSPICE_DIR)/${TOP}
	mkdir -p $(XSPICE_DIR)/${TOP}
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/${TOP}.nl.v $(XSPICE_DIR)/${TOP}/${TOP}_xspice.nl.v
	vlog2Verilog $(XSPICE_DIR)/${TOP}/${TOP}_xspice.nl.v -o $(XSPICE_DIR)/${TOP}/${TOP}.vp -l $(PDK_ROOT)/$(PDK)/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef -v "VPWR,VPB" -g "VGND,VNB"
	vlog2Spice $(XSPICE_DIR)/${TOP}/${TOP}.vp -l $(PDK_ROOT)/$(PDK)/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice -o $(XSPICE_DIR)/${TOP}/${TOP}.spice
	python3 $(XSPICE_DIR)/spi2xspice.py $(PDK_ROOT)/$(PDK)/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p50V_25C.lib -io_time=500p -time=50p -idelay=5p -odelay=50p -cload=250f $(XSPICE_DIR)/${TOP}/${TOP}.spice $(XSPICE_DIR)/${TOP}/${TOP}.xspice
	python3 $(XSPICE_DIR)/reorder_xspice_pins.py $(SCH_DIR)/${TOP}.sym $(XSPICE_DIR)/${TOP}/${TOP}.xspice
.PHONY: generate-xspice
# ================================================================================================
