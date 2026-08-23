# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

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

# full-RC extresist threshold in mOhm (sak-pex.sh -t, only used in EXT_MODE=3; default: 10000 = 10 Ohm)
# Override with: make <target> THRESHOLD=<mOhm>
THRESHOLD ?= 10000

# full-RC extresist minres in mOhm (sak-pex.sh -r, only used in EXT_MODE=3; default: 1000 = 1 Ohm)
# Override with: make <target> MINRES=<mOhm>
MINRES ?= 1000

# full-RC extresist mindelay in ps (sak-pex.sh -y, only used in EXT_MODE=3; default: 1; 0 = gate by resistance)
# Override with: make <target> MINDELAY=<ps>
MINDELAY ?= 1

# Floating-point precision (significant digits) for xschem's ev function
# Override with: make <target> EV_PRECISION=<digits>
EV_PRECISION ?= 5

# Set the waveform viewer GTKWave or Surfer (default: gtkwave)
# Override with: make <target> WAVEFORM_VIEWER=<gtkwave|surfer>
WAVEFORM_VIEWER ?= gtkwave

# Extra options for the sak-open.py file browser (e.g. --all to include build outputs)
# Override with: make open OPEN_ARGS=<options>
OPEN_ARGS ?=

# Folder structure
COCOTB_DIR      := testbenches/cocotb
VERILOG_TB_DIR 	:= testbenches/verilog
XSCHEM_TB_DIR  	:= testbenches/xschem
XSCHEM_SCH_DIR  := schematic/xschem
SCRIPTS_DIR   	:= scripts
SIM_PLOT_DIR  	:= testbenches/xschem/plot_simulations
RENDER_IMG_DIR 	:= render/img
REPORT_DIR     	:= verification
SRC_DIR 		:= rtl
NET_NL_DIR    	:= netlist/nl
NET_PNL_DIR  	:= netlist/pnl
NET_SPICE_DIR 	:= netlist/spice
XSPICE_DIR  	:= netlist/xspice
NET_PEX_DIR   	:= netlist/pex
LIBRELANE_DIR 	:= flow/librelane
FLOW_FINAL_DIR 	:= flow/final
FINAL_DIR      	:= final
LAY_DIR        	:= final/gds

# Variables for simulation and linting targets
# constants.sv defines the `COUNTER_MAX_DEFAULT / `CLK_FREQ_DEFAULT macros and must
# compile before any module that references them, so it is the first entry in MODULES_SIM
# and in both branches of _SIM_SRCS / _LINT_SRCS below (Yosys 0.64 cannot parse
# `import pkg::*` in a module header, see rtl/constants.sv).
MODULES_SYNTH := \
	$(SRC_DIR)/counter.sv \
	$(SRC_DIR)/counter_top.sv

MODULES_SIM :=  \
	$(SRC_DIR)/constants.sv \
	$(MODULES_SYNTH)

# Source files for sim-rtl-verilog: auto-selects MODULES_SIM when CELL == TOP, constants.sv + single-file otherwise (auto-detecting .sv/.v)
_SIM_SRCS = $(if $(filter $(CELL),$(TOP)),$(MODULES_SIM),$(SRC_DIR)/constants.sv $(or $(wildcard $(SRC_DIR)/$(CELL).sv),$(SRC_DIR)/$(CELL).v))

# Source files for lint-verilog: constants + all synthesis sources for TOP, constants.sv + single-file (auto-detecting .sv/.v) otherwise
_LINT_SRCS = $(if $(filter $(CELL),$(TOP)),$(SRC_DIR)/constants.sv $(MODULES_SYNTH),$(SRC_DIR)/constants.sv $(or $(wildcard $(SRC_DIR)/$(CELL).sv),$(SRC_DIR)/$(CELL).v))

# Testbench extension: prefers <CELL>_tb.sv, falls back to <CELL>_tb.v (dot is added at use site)
_TB_EXT = $(if $(wildcard $(VERILOG_TB_DIR)/$(CELL)_tb.sv),sv,v)


# Help Target
help: ## Show this help message
	@echo 'Usage: make <target> [CELL=<cellname>] [EXT_MODE=<1|2|3>] [THRESHOLD=<mOhm>] [MINRES=<mOhm>] [MINDELAY=<ps>] [WAVEFORM_VIEWER=<gtkwave|surfer>] [TB=<testbenchname>] [SCRIPT=<scriptname>] [OPEN_ARGS=<options>]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ''
	@echo 'CELL defaults to $(TOP). Override to lint or simulate subcells.'
	@echo 'EXT_MODE defaults to 3 (full-RC). 1=C-decoupled, 2=C-coupled.'
	@echo 'THRESHOLD/MINRES/MINDELAY are full-RC (EXT_MODE=3) extresist settings for magic-pex (defaults 10000 mOhm / 1000 mOhm / 1 ps).'
	@echo 'WAVEFORM_VIEWER defaults to gtkwave. Use surfer to launch Surfer instead.'
	@echo 'TB selects the Xschem testbench for sim-gl-xschem (default: <CELL>_tb_tran).'
	@echo 'SCRIPT selects the plotting script for sim-view-xschem (default: plot_<CELL>).'
	@echo 'OPEN_ARGS passes extra options to sak-open.py for the open target (e.g. --all).'
.PHONY: help
# ================================================================================================


# Open Target
open: ## Open the design files of this folder in the sak-open.py file browser (needs the VNC/X11 desktop)
	sak-open.py $(OPEN_ARGS) .
.PHONY: open
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
# Testbench for the Xschem simulation targets (default: <CELL>_tb_tran)
# Override with: make <target> TB=<testbenchname>
TB ?= $(CELL)_tb_tran
# Plotting script for sim-view-xschem (default: plot_<CELL>)
# Override with: make <target> SCRIPT=<scriptname>
SCRIPT ?= plot_$(CELL)

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

sim-gl-xschem: ## Run gate-level simulation of CELL cell with Xschem in batch mode (usage: make sim-gl-xschem [CELL=<cellname>] [TB=<testbenchname>])
	mkdir -p $(XSCHEM_TB_DIR)/simulations
	mkdir -p $(SIM_PLOT_DIR)/data
	cd $(XSCHEM_TB_DIR) && xschem -r -x -q --rcfile xschemrc --command ' \
		xschem set netlist_type spice; \
		set netlist_dir $(abspath $(XSCHEM_TB_DIR)/simulations); \
		xschem save; \
		write_data [save_params] $(abspath $(XSCHEM_TB_DIR)/simulations)/$(TB).save; \
		xschem netlist \
	' $(TB).sch
	cd $(XSCHEM_TB_DIR)/simulations && ngspice -b $(TB).spice
.PHONY: sim-gl-xschem

sim-view-xschem: ## Plot Xschem simulation results (usage: make sim-view-xschem [SCRIPT=<scriptname>])
	SHOW_PLOTS=1 python3 $(SIM_PLOT_DIR)/$(SCRIPT).py
.PHONY: sim-view-xschem

sim-all: ## Simulate the macro (RTL Verilog + RTL/GL cocotb + GL Xschem for counter_top)
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
# Using * wildcard to ignore step numbers
copy-reports: ## Copy yosys, antenna, STA, power, IR-drop, DRC, LVS and manufacturability reports from the last LibreLane run to verification/
	rm -rf $(REPORT_DIR)/
	mkdir -p $(REPORT_DIR)/
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/pre_synth_chk.rpt $(REPORT_DIR)/yosys_synth_check.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/pre_techmap.rpt $(REPORT_DIR)/yosys_pre_techmap.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/post_dff.rpt $(REPORT_DIR)/yosys_post_dff.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-yosys-synthesis/reports/stat.rpt $(REPORT_DIR)/stat.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-checkantennas-1/reports/antenna.rpt $(REPORT_DIR)/antenna_violations.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-checkantennas-1/reports/antenna_summary.rpt $(REPORT_DIR)/antenna_summary.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/summary.rpt $(REPORT_DIR)/stapostpnr_summary.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_fast_1p32V_m40C/power.rpt $(REPORT_DIR)/stapostpnr_nom_fast_1p32V_m40C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_fast_1p65V_m40C/power.rpt $(REPORT_DIR)/stapostpnr_nom_fast_1p65V_m40C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_slow_1p08V_125C/power.rpt $(REPORT_DIR)/stapostpnr_nom_slow_1p08V_125C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_slow_1p35V_125C/power.rpt $(REPORT_DIR)/stapostpnr_nom_slow_1p35V_125C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_typ_1p20V_25C/power.rpt $(REPORT_DIR)/stapostpnr_nom_typ_1p20V_25C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-stapostpnr/nom_typ_1p50V_25C/power.rpt $(REPORT_DIR)/stapostpnr_nom_typ_1p50V_25C_power.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-openroad-irdropreport/irdrop.rpt $(REPORT_DIR)/irdrop.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-magic-drc/reports/drc.magic.rpt $(REPORT_DIR)/drc.magic.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-klayout-drc/reports/drc.klayout.json $(REPORT_DIR)/drc.klayout.json
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-netgen-lvs/reports/lvs.netgen.rpt $(REPORT_DIR)/lvs.netgen.rpt
	cp $(LIBRELANE_DIR)/runs/${RUN_TAG}/*-misc-reportmanufacturability/manufacturability.rpt $(REPORT_DIR)/manufacturability.rpt
.PHONY: copy-reports

copy-final: ## Copy final output gds, lef, lib, nl, pnl, spef, and vh folders from the last LibreLane run to final/
	rm -rf $(FINAL_DIR)/
	mkdir -p $(FINAL_DIR)/
	cp -r $(FLOW_FINAL_DIR)/gds  $(FINAL_DIR)/gds
	cp -r $(FLOW_FINAL_DIR)/lef  $(FINAL_DIR)/lef
	cp -r $(FLOW_FINAL_DIR)/lib  $(FINAL_DIR)/lib
	cp -r $(FLOW_FINAL_DIR)/nl   $(FINAL_DIR)/nl
	cp -r $(FLOW_FINAL_DIR)/pnl  $(FINAL_DIR)/pnl
	cp -r $(FLOW_FINAL_DIR)/spef $(FINAL_DIR)/spef
	cp -r $(FLOW_FINAL_DIR)/vh   $(FINAL_DIR)/vh
.PHONY: copy-final

copy-netlist: ## Copy final output spice, pnl and nl netlists from the last LibreLane run to netlist/
	rm -rf $(NET_SPICE_DIR)/
	mkdir -p $(NET_SPICE_DIR)/
	cp -r $(FLOW_FINAL_DIR)/spice/${TOP}.spice $(NET_SPICE_DIR)/${TOP}.spice

	rm -rf $(NET_PNL_DIR)/
	mkdir -p $(NET_PNL_DIR)/
	cp -r $(FLOW_FINAL_DIR)/pnl/${TOP}.pnl.v $(NET_PNL_DIR)/${TOP}.pnl.v

	rm -rf $(NET_NL_DIR)/
	mkdir -p $(NET_NL_DIR)/
	cp -r $(FLOW_FINAL_DIR)/nl/${TOP}.nl.v $(NET_NL_DIR)/${TOP}.nl.v
.PHONY: copy-netlist

copy-render: ## Copy macro render from the last LibreLane run to render/img/
	mkdir -p $(RENDER_IMG_DIR)/
	cp -r $(FLOW_FINAL_DIR)/render/${TOP}.png $(RENDER_IMG_DIR)/${TOP}_librelane.png
.PHONY: copy-render
# ================================================================================================


# Render Target
render-gds: ## Render images from the final GDS using sak-render.py
	mkdir -p $(RENDER_IMG_DIR)/
	sak-render.py -t ihp-sg13g2 -w 2048 -s 4 -o $(RENDER_IMG_DIR)/${TOP} $(FINAL_DIR)/gds/${TOP}.gds
.PHONY: render-gds
# ================================================================================================


# Generate XSPICE Target
# Runs as part of `build-top` (after `copy-netlist`) so the XSPICE model always matches the
# netlists of the current LibreLane run. Can also be run standalone to regenerate the model.
generate-xspice: ## Generate XSPICE model from the LibreLane-extracted SPICE netlist
	mkdir -p $(XSPICE_DIR)
	python3 $(SCRIPTS_DIR)/spi2xspice.py $(PDK_ROOT)/$(PDK)/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p50V_25C.lib -io_time=500p -time=50p -idelay=5p -odelay=50p -cload=250f $(NET_SPICE_DIR)/${TOP}.spice $(XSPICE_DIR)/${TOP}.xspice
	sak-pin-reorder.py $(XSCHEM_SCH_DIR)/${TOP}.sym $(XSPICE_DIR)/${TOP}.xspice --format xspice
.PHONY: generate-xspice
# ================================================================================================


# Build Targets
build-fpga: ## Build target for FPGA usage
	@$(MAKE) -C fpga all
.PHONY: build-fpga

build-top: ## Build macro (run LibreLane with KLayout & Magic DRC checks, copy reports, copy final files, copy netlists, generate XSPICE model, copy render, and render final GDS)
	$(MAKE) librelane
	$(MAKE) copy-reports
	$(MAKE) copy-final
	$(MAKE) copy-netlist
	$(MAKE) generate-xspice
	$(MAKE) copy-render
	$(MAKE) render-gds
#	$(MAKE) librelane-openroad
.PHONY: build-top
# ================================================================================================


# DRC & LVS Verification Targets
# The LibreLane flow already includes DRC and LVS checks with Magic and KLayout, and they are saved in the verification/ folder.
# ================================================================================================


# PEX Targets
symbol-pex: ## Build the Xschem PEX symbol <CELL>_pex.sym from <CELL>.sym (usage: make symbol-pex [CELL=<cellname>])
	@if [ ! -f $(XSCHEM_SCH_DIR)/$(CELL).sym ]; then \
		echo "No symbol $(XSCHEM_SCH_DIR)/$(CELL).sym found, skipping PEX symbol generation."; \
	else \
		sed 's/type=subcircuit/type=primitive/' $(XSCHEM_SCH_DIR)/$(CELL).sym > $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym; \
		if ! grep -q 'type=primitive' $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym; then \
			rm -f $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym; \
			echo "ERROR: $(XSCHEM_SCH_DIR)/$(CELL).sym declares neither type=subcircuit nor type=primitive!"; \
			exit 1; \
		fi; \
		echo "Wrote $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym (copy of $(CELL).sym with type=primitive)."; \
	fi
.PHONY: symbol-pex

klayout-pex: ## Run Parasitic Extraction with KPEX on the final GDS (usage: make klayout-pex [CELL=<cellname>] [EXT_MODE=<1|2|3>])
	@if [ ! -f $(LAY_DIR)/$(CELL).gds ]; then \
		echo "No layout $(LAY_DIR)/$(CELL).gds found. Run 'make build-top' (or 'make copy-final') first."; \
		exit 1; \
	fi
	mkdir -p $(NET_PEX_DIR)
	$(MAKE) symbol-pex CELL=$(CELL)
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
	--schematic $(NET_SPICE_DIR)/$(CELL).spice \
	--gds $(LAY_DIR)/$(CELL).gds \
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
		sak-pin-reorder.py $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice --format spice; \
	else \
		echo "No symbol $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym found, skipping pin reorder."; \
	fi
	python3 $(SCRIPTS_DIR)/check_pex_ports.py $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice
.PHONY: klayout-pex

magic-pex: ## Run Parasitic Extraction with Magic on the final GDS (usage: make magic-pex [CELL=<cellname>] [EXT_MODE=<1|2|3>] [THRESHOLD=<mOhm>] [MINRES=<mOhm>] [MINDELAY=<ps>])
	@if [ ! -f $(LAY_DIR)/$(CELL).gds ]; then \
		echo "No layout $(LAY_DIR)/$(CELL).gds found. Run 'make build-top' (or 'make copy-final') first."; \
		exit 1; \
	fi
	mkdir -p $(NET_PEX_DIR)
	$(MAKE) symbol-pex CELL=$(CELL)
	sak-pex.sh -d -m $(EXT_MODE) -n $(CELL)_pex -t $(THRESHOLD) -r $(MINRES) -y $(MINDELAY) -w $(NET_PEX_DIR) $(LAY_DIR)/$(CELL).gds
	mv $(NET_PEX_DIR)/$(CELL).pex.spice $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice
	rm -f $(NET_PEX_DIR)/pex_$(CELL).tcl
	@if [ -f $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym ]; then \
		echo "Reordering pins in $(CELL)_magic_pex_$(EXT_MODE).spice to match $(CELL)_pex.sym..."; \
		sak-pin-reorder.py $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice --format spice; \
	else \
		echo "No symbol $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym found, skipping pin reorder."; \
	fi
	python3 $(SCRIPTS_DIR)/check_pex_ports.py $(NET_PEX_DIR)/$(CELL)_magic_pex_$(EXT_MODE).spice
.PHONY: magic-pex
# ================================================================================================


# Lint, Build, Verify and Simulate All Target
all: ## Lint, build, verify and simulate the macro
	$(MAKE) lint-verilog-all
	$(MAKE) build-fpga
	$(MAKE) build-top
	$(MAKE) magic-pex
#	$(MAKE) klayout-pex
	$(MAKE) sim-all
.PHONY: all
# ================================================================================================


# Clean Target
clean: ## Delete all generated files and folders (LibreLane runs, final, netlists, render, reports, simulation and FPGA outputs)
	rm -rf $(LIBRELANE_DIR)/runs $(FLOW_FINAL_DIR)
	rm -rf $(FINAL_DIR)
	rm -rf $(NET_NL_DIR) $(NET_PNL_DIR) $(NET_SPICE_DIR) $(XSPICE_DIR) $(NET_PEX_DIR)
	rm -rf $(RENDER_IMG_DIR)
	rm -rf $(REPORT_DIR)
	rm -rf $(XSCHEM_SCH_DIR)/simulations $(XSCHEM_TB_DIR)/simulations
	rm -rf $(SIM_PLOT_DIR)/data $(SIM_PLOT_DIR)/figures $(SIM_PLOT_DIR)/__pycache__
	rm -rf $(COCOTB_DIR)/sim_build
	rm -rf $(SCRIPTS_DIR)/__pycache__ $(COCOTB_DIR)/__pycache__
	rm -f $(VERILOG_TB_DIR)/*.vcd
	$(MAKE) -C fpga clean
.PHONY: clean
# ================================================================================================
