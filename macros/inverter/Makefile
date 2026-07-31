# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Variables
TOP = inverter_top

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

# KLayout DRC level: precheck, macro, or regular (sak-drc.sh -l, only used by klayout-drc; default: macro)
# Override with: make <target> DRC_LEVEL=<precheck|macro|regular>
DRC_LEVEL ?= macro

# Floating-point precision (significant digits) for Xschem's ev function
# Override with: make <target> EV_PRECISION=<digits>
EV_PRECISION ?= 5

# Preferred GDS extension: use .gds when available for the CELL, otherwise .klay.gds
# Resolved per CELL (CELL defaults to TOP), so cells can mix .gds and .klay.gds within one macro.
# All DRC, LVS and PEX targets (KLayout and Magic) work with either .gds or .klay.gds.
_GDS_EXT = $(if $(wildcard $(LAY_DIR)/$(CELL).gds),gds,klay.gds)

# Folder structure
XSCHEM_SCH_DIR  := schematic/xschem
XSCHEM_TB_DIR   := testbenches/xschem
LAY_DIR         := layout
SCRIPTS_DIR     := scripts
SIM_PLOT_DIR    := testbenches/xschem/plot_simulations
GDS_DIR         := final/gds
LEF_DIR         := final/lef
LIB_DIR         := final/lib
VH_DIR          := final/vh
RENDER_IMG_DIR  := render/img
NET_SCH_DIR     := netlist/schematic
NET_LAY_DIR     := netlist/layout
NET_PEX_DIR     := netlist/pex
CACE_DIR        := verification/cace
LVS_RPT_DIR     := verification/lvs
DRC_RPT_DIR     := verification/drc


# Help Target
help: ## Show this help message
	@echo 'Usage: make <target> [CELL=<cellname>] [EXT_MODE=<1|2|3>] [THRESHOLD=<mOhm>] [MINRES=<mOhm>] [MINDELAY=<ps>] [DRC_LEVEL=<precheck|macro|regular>] [EV_PRECISION=<digits>]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ''
	@echo 'CELL defaults to $(TOP). Override to verify subcells.'
	@echo 'EXT_MODE defaults to 3 (full-RC). 1=C-decoupled, 2=C-coupled.'
	@echo 'THRESHOLD/MINRES/MINDELAY are full-RC (EXT_MODE=3) extresist settings for magic-pex (defaults 10000 mOhm / 1000 mOhm / 1 ps).'
	@echo 'DRC_LEVEL defaults to macro. Sets the KLayout DRC level for klayout-drc (precheck|macro|regular).'
	@echo 'EV_PRECISION defaults to 5 significant digits for xschem ev function.'
	@echo 'TB selects the Xschem testbench for sim-xschem (e.g. inverter_tb_tran).'
	@echo 'SCRIPT selects the plotting script for sim-view-xschem (e.g. plot_inverter_top).'
.PHONY: help
# ================================================================================================


# Simulation Targets
# Testbench name for sim-xschem target (required: make sim-xschem TB=<testbenchname>)
TB ?= $(error TB is not set. Usage: make sim-xschem TB=<testbenchname>)
SCRIPT ?= $(error SCRIPT is not set. Usage: make sim-view-xschem SCRIPT=<scriptname>)

sim-xschem: ## Run TB simulation with Xschem in batch mode (usage: make sim-xschem TB=<testbenchname>)
	mkdir -p $(XSCHEM_TB_DIR)/simulations
	cd $(XSCHEM_TB_DIR) && xschem -r -x -q --rcfile xschemrc --command ' \
		xschem set netlist_type spice; \
		set netlist_dir $(abspath $(XSCHEM_TB_DIR)/simulations); \
		xschem save; \
		xschem netlist \
	' $(TB).sch
	cd $(XSCHEM_TB_DIR)/simulations && ngspice -b $(TB).spice
.PHONY: sim-xschem

sim-view-xschem: ## Plot Xschem simulation results (usage: make sim-view-xschem SCRIPT=<scriptname>)
	SHOW_PLOTS=1 python3 $(SIM_PLOT_DIR)/$(SCRIPT).py
.PHONY: sim-view-xschem

sim-cace: ## Run CACE simulations and collect result plots
	cd $(CACE_DIR) && \
	mkdir -p results/inverter && \
	\
	cace inverter.yaml -p ac_mm_params && \
	cp _runs/RUN_*/parameters/ac_mm_params/Adc_ol_dB_mm.png results/inverter/ && \
	cp _runs/RUN_*/parameters/ac_mm_params/fcu_mm.png results/inverter/ && \
	rm -rf _runs/RUN_* && \
	\
	cace inverter.yaml -p ac_mc_params && \
	cp _runs/RUN_*/parameters/ac_mc_params/Adc_ol_dB_mc.png results/inverter/ && \
	cp _runs/RUN_*/parameters/ac_mc_params/fcu_mc.png results/inverter/ && \
	rm -rf _runs/RUN_* && \
	\
	cace inverter.yaml -p ac_params && \
	cp _runs/RUN_*/parameters/ac_params/Adc_ol_dB_vs_vdd.png results/inverter/ && \
	cp _runs/RUN_*/parameters/ac_params/fcu_vs_vdd.png results/inverter/ && \
	rm -rf _runs/RUN_* && \
	\
	rm -rf _runs _docs netlist
.PHONY: sim-cace

sim-all: ## Simulate the macro
	$(MAKE) sim-xschem TB=inverter_tb_ac_ol
	$(MAKE) sim-xschem TB=inverter_tb_tran
	$(MAKE) sim-xschem TB=inverter_tb_dc_vout
	$(MAKE) sim-xschem TB=inverter_top_tb_tran
	$(MAKE) sim-cace
.PHONY: sim-all
# ================================================================================================


# Build Target
build-top: ## Build TOP cell (Verilog, LEF, LIB, copy GDS, and render image)
	$(MAKE) lef
	$(MAKE) lib
	$(MAKE) verilog
	$(MAKE) copy-gds
	$(MAKE) render-gds
.PHONY: build-top
# ================================================================================================


# LEF Target
lef: ## Export LEF from the TOP cell layout using Magic
	rm -rf $(LEF_DIR)
	mkdir -p $(LEF_DIR)
	printf '%s\n' \
		'gds read $(LAY_DIR)/$(TOP).gds' \
		'load $(TOP)' \
		'lef write $(LEF_DIR)/$(TOP).lef -hide -pinonly 2um' | \
		magic -dnull -noconsole \
		-rcfile $(PDK_ROOT)/$(PDK)/libs.tech/magic/ihp-sg13g2.magicrc
.PHONY: lef
# ================================================================================================


# LIB Target
lib: ## Generate a Liberty timing library for the TOP cell
	rm -rf $(LIB_DIR)
	mkdir -p $(LIB_DIR)
	@printf 'library ($(TOP)) {\n  input_threshold_pct_fall: 50.0;\n  input_threshold_pct_rise: 50.0;\n  output_threshold_pct_fall: 50.0;\n  output_threshold_pct_rise: 50.0;\n  slew_lower_threshold_pct_fall: 20.0;\n  slew_lower_threshold_pct_rise: 20.0;\n  slew_upper_threshold_pct_fall: 80.0;\n  slew_upper_threshold_pct_rise: 80.0;\n  \n  cell ($(TOP)) {\n  }\n}\n' > $(LIB_DIR)/$(TOP).lib
.PHONY: lib
# ================================================================================================


# Verilog Target
verilog: ## Generate a Verilog stub of the TOP cell from Magic or KLayout PEX netlist pins
	rm -rf $(VH_DIR)
	mkdir -p $(VH_DIR)
	@pex_netlist=""; \
	for f in \
		$(NET_PEX_DIR)/$(TOP)_magic_pex_1.spice \
		$(NET_PEX_DIR)/$(TOP)_magic_pex_2.spice \
		$(NET_PEX_DIR)/$(TOP)_magic_pex_3.spice \
		$(NET_PEX_DIR)/$(TOP)_klayout_pex_1.spice \
		$(NET_PEX_DIR)/$(TOP)_klayout_pex_2.spice \
		$(NET_PEX_DIR)/$(TOP)_klayout_pex_3.spice; do \
		if [ -f "$$f" ]; then \
			pex_netlist="$$f"; \
			break; \
		fi; \
	done; \
	if [ -z "$$pex_netlist" ]; then \
		echo "ERROR: No PEX netlist found for $(TOP). Expected one of:"; \
		echo "  $(NET_PEX_DIR)/$(TOP)_magic_pex_{1,2,3}.spice"; \
		echo "  $(NET_PEX_DIR)/$(TOP)_klayout_pex_{1,2,3}.spice"; \
		echo "Run 'make magic-pex' or 'make klayout-pex' first."; \
		exit 1; \
	fi; \
	echo "Reading pins from $$pex_netlist..."; \
	pex_pins=$$(awk '/^\.subckt $(TOP)_pex/{sub(/^\.subckt [^ ]+ /,"");p=$$0;next} p&&/^[+]/{sub(/^[+] */,"");p=p" "$$0;next} p{exit} END{print p}' "$$pex_netlist"); \
	power_pins=$$(echo "$$pex_pins" | tr ' ' '\n' | grep -E '^(VDD|VSS|VPWR|VGND|VNB|VPB)$$' | sort -u | tr '\n' ' '); \
	signal_pins=$$(echo "$$pex_pins" | tr ' ' '\n' | grep -vE '^(VDD|VSS|VPWR|VGND|VNB|VPB)$$' | grep -v '^$$' | sort | tr '\n' ' '); \
	{ \
		echo 'module $(TOP) ('; \
		if [ -n "$$(echo $$power_pins | xargs)" ]; then \
			echo '`ifdef USE_POWER_PINS'; \
			for p in $$power_pins; do echo "    inout $$p,"; done; \
			echo '`endif'; \
		fi; \
		last=$$(echo $$signal_pins | awk '{print $$NF}'); \
		for p in $$signal_pins; do \
			case "$$p" in \
				di_*) t=input ;; \
				do_*) t=output ;; \
				*) t=inout ;; \
			esac; \
			if [ "$$p" = "$$last" ]; then echo "    $$t $$p"; else echo "    $$t $$p,"; fi; \
		done; \
		echo ');'; \
		echo 'endmodule'; \
	} > $(VH_DIR)/$(TOP).v
.PHONY: verilog
# ================================================================================================


# Copy Target
copy-gds: ## Copy the TOP cell GDS from layout/ to final/gds/
	rm -rf $(GDS_DIR)
	mkdir -p $(GDS_DIR)
	cp $(LAY_DIR)/$(TOP).gds $(GDS_DIR)/$(TOP).gds
.PHONY: copy-gds
# ================================================================================================


# Render Target
render-gds: ## Render an image from the final GDS using lay2img.py
	rm -rf $(RENDER_IMG_DIR)/
	mkdir -p $(RENDER_IMG_DIR)/
	python3 $(SCRIPTS_DIR)/lay2img.py $(LAY_DIR)/$(TOP).gds $(RENDER_IMG_DIR)/$(TOP).png --width 2048 --oversampling 4
.PHONY: render-gds
# ================================================================================================


# DRC Targets
klayout-drc: ## Run KLayout DRC of the CELL cell (usage: make klayout-drc [CELL=<cellname>] [DRC_LEVEL=<precheck|macro|regular>])
	mkdir -p $(DRC_RPT_DIR)
	sak-drc.sh -d -k -l $(DRC_LEVEL) -w $(DRC_RPT_DIR) $(LAY_DIR)/$(CELL).$(_GDS_EXT)
.PHONY: klayout-drc

magic-drc: ## Run Magic DRC of the CELL cell (usage: make magic-drc [CELL=<cellname>])
	mkdir -p $(DRC_RPT_DIR)
	sak-drc.sh -d -m -f "*" -w $(DRC_RPT_DIR) $(LAY_DIR)/$(CELL).$(_GDS_EXT)
.PHONY: magic-drc
# ================================================================================================


# LVS Targets
klayout-lvs-netlist: ## Export CDL schematic netlist from Xschem for KLayout LVS (usage: make klayout-lvs-netlist [CELL=<cellname>] [EV_PRECISION=<digits>])
	mkdir -p $(NET_SCH_DIR)
	xschem -s -r -x -q --rcfile $(XSCHEM_SCH_DIR)/xschemrc --command ' \
		set spiceprefix 1; \
		set lvs_netlist 1; \
		set top_is_subckt 1; \
		set lvs_ignore 1; \
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
	sak-lvs.sh -d -k -w $(LVS_RPT_DIR) -s $(NET_SCH_DIR)/$(CELL)_klayout.cdl -l $(LAY_DIR)/$(CELL).$(_GDS_EXT) -c $(CELL)
	mv $(LVS_RPT_DIR)/$(CELL).klayout.lvs/$(CELL)_extracted.cir $(NET_LAY_DIR)/$(CELL)_klayout.cir
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
	sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(NET_SCH_DIR)/$(CELL)_magic.spice -l $(LAY_DIR)/$(CELL).$(_GDS_EXT) -c $(CELL)
	mv $(LVS_RPT_DIR)/$(CELL).magic.lvs/$(CELL).ext.spc $(NET_LAY_DIR)/$(CELL)_magic.ext.spc
.PHONY: magic-lvs
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
	--gds $(LAY_DIR)/$(CELL).$(_GDS_EXT) \
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

magic-pex: ## Run Parasitic Extraction with Magic of the CELL cell (usage: make magic-pex [CELL=<cellname>] [EXT_MODE=<1|2|3>] [THRESHOLD=<mOhm>] [MINRES=<mOhm>] [MINDELAY=<ps>])
	mkdir -p $(NET_PEX_DIR)
	sak-pex.sh -d -m $(EXT_MODE) -n $(CELL)_pex -t $(THRESHOLD) -r $(MINRES) -y $(MINDELAY) -w $(NET_PEX_DIR) $(LAY_DIR)/$(CELL).$(_GDS_EXT)
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


# Verify Targets
klayout-verify: ## Verify CELL cell with KLayout (usage: make klayout-verify [CELL=<cellname>])
	$(MAKE) klayout-drc CELL=$(CELL)
	$(MAKE) klayout-lvs CELL=$(CELL)
	$(MAKE) klayout-pex CELL=$(CELL)
.PHONY: klayout-verify

klayout-verify-all: ## Verify all main subcells with KLayout (DRC, LVS, PEX)
	$(MAKE) klayout-verify CELL=inverter
	$(MAKE) klayout-verify CELL=inverter_top
.PHONY: klayout-verify-all

magic-verify: ## Verify CELL cell with Magic (usage: make magic-verify [CELL=<cellname>])
	$(MAKE) magic-drc CELL=$(CELL)
	$(MAKE) magic-lvs CELL=$(CELL)
	$(MAKE) magic-pex CELL=$(CELL)
.PHONY: magic-verify

magic-verify-all: ## Verify all main subcells with Magic (DRC, LVS, PEX)
	$(MAKE) magic-verify CELL=inverter
	$(MAKE) magic-verify CELL=inverter_top
.PHONY: magic-verify-all
# ================================================================================================


# Verify, Build and Simulate All Target
all: ## Verify, build and simulate the TOP cell
	$(MAKE) klayout-verify-all
	$(MAKE) magic-verify-all
	$(MAKE) build-top
	$(MAKE) sim-all
.PHONY: all
# ================================================================================================
