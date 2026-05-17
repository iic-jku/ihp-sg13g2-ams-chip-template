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

# Floating-point precision (significant digits) for Xschem's ev function
# Override with: make <target> EV_PRECISION=<digits>
EV_PRECISION ?= 5

# Preferred GDS extension: use .gds when available, otherwise .klay.gds
# This checks both TOP and CELL names so it can be used as: $(LAY_DIR)/$(TOP).$(_GDS_EXT) or $(LAY_DIR)/$(CELL).$(_GDS_EXT)
# KLayout LVS, DRC and PEX work with either .gds or .klay.gds, but Magic LVS, DRC and PEX require .gds.
_GDS_EXT = $(if $(wildcard $(LAY_DIR)/$(TOP).gds)$(wildcard $(LAY_DIR)/$(CELL).gds),gds,klay.gds)

# Folder structure
XSCHEM_SCH_DIR  := schematic/xschem
XSCHEM_TB_DIR   := testbenches/xschem
LAY_DIR         := layout
SCRIPTS_DIR     := scripts
SIM_PLOT_DIR    := scripts/plot_simulations
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
	@echo 'Usage: make <target> [CELL=<cellname>] [EXT_MODE=<1|2|3>] [EV_PRECISION=<digits>]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ''
	@echo 'CELL defaults to $(TOP). Override to verify subcells.'
	@echo 'EXT_MODE defaults to 3 (full-RC). 1=C-decoupled, 2=C-coupled.'
	@echo 'EV_PRECISION defaults to 5 significant digits for xschem ev function.'
.PHONY: help
# ================================================================================================


# Simulation Targets
# Testbench name for sim-xschem target (required: make sim-xschem TB=<testbenchname>)
TB ?= $(error TB is not set. Usage: make sim-xschem TB=<testbenchname>)

sim-xschem: ## Run TB simulation with Xschem (usage: make sim-xschem TB=<testbenchname>)
	cd $(XSCHEM_TB_DIR) && xschem -x -q --rcfile xschemrc --command ' \
		set netlist_dir $(abspath $(XSCHEM_TB_DIR)/simulations); \
		xschem save; \
		xschem netlist; \
		xschem simulate \
	' $(TB).sch
.PHONY: sim-xschem

sim-view-xschem: ## Plot Xschem simulation results (usage: make sim-view-xschem CELL=<cellname>)
	python3 $(SIM_PLOT_DIR)/plot_$(CELL).py
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
#	$(MAKE) sim-view-xschem CELL=inverter
#	$(MAKE) sim-view-xschem CELL=inverter_top
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
		--layout=$(LAY_DIR)/$(CELL).$(_GDS_EXT) \
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
	sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(NET_SCH_DIR)/$(CELL)_magic.spice -l $(LAY_DIR)/$(CELL).gds -c $(CELL)
# 	Alternative using sak-lvs.sh for netlist export and LVS in one step (replaces magic-lvs-netlist target):
#   sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(XSCHEM_SCH_DIR)/$(CELL).sch -l $(LAY_DIR)/$(CELL).gds -c $(CELL)
	mv $(LVS_RPT_DIR)/$(CELL).ext.spc $(NET_LAY_DIR)/$(CELL)_magic.ext.spc
	rm -f $(LVS_RPT_DIR)/$(CELL).sch.spc
	rm -f $(LVS_RPT_DIR)/ext_$(CELL).tcl
	rm -f $(LVS_RPT_DIR)/*.ext
	sleep 4
.PHONY: magic-lvs
# ================================================================================================


# DRC Targets
klayout-drc: ## Run KLayout DRC of the CELL cell (usage: make klayout-drc [CELL=<cellname>])
	mkdir -p $(DRC_RPT_DIR)
	python3 $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/run_drc.py \
		--path=$(LAY_DIR)/$(CELL).$(_GDS_EXT) \
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
	sak-drc.sh -d -m -f "*" -w $(DRC_RPT_DIR) $(LAY_DIR)/$(CELL).gds $(CELL)
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
		python3 $(SCRIPTS_DIR)/reorder_spice_pins.py $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_klayout_pex_$(EXT_MODE).spice; \
	else \
		echo "No symbol $(XSCHEM_SCH_DIR)/$(CELL)_pex.sym found, skipping pin reorder."; \
	fi
	sleep 4
.PHONY: klayout-pex

magic-pex: ## Run Parasitic Extraction with Magic of the CELL cell (usage: make magic-pex [CELL=<cellname>] [EXT_MODE=<1|2|3>])
	mkdir -p $(NET_PEX_DIR)
	sak-pex.sh -d -m $(EXT_MODE) -w $(NET_PEX_DIR) $(LAY_DIR)/$(CELL).gds
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

klayout-verify-all: ## Verify all main subcells with KLayout (LVS, DRC, PEX)
#	$(MAKE) klayout-verify CELL=inverter
	$(MAKE) klayout-verify CELL=inverter_top
.PHONY: klayout-verify-all

magic-verify: ## Verify CELL cell with Magic (usage: make magic-verify [CELL=<cellname>])
	$(MAKE) magic-lvs CELL=$(CELL)
	$(MAKE) magic-drc CELL=$(CELL)
	$(MAKE) magic-pex CELL=$(CELL)
.PHONY: magic-verify

magic-verify-all: ## Verify all main subcells with Magic (LVS, DRC, PEX)
	$(MAKE) magic-verify CELL=inverter
	$(MAKE) magic-verify CELL=inverter_top
.PHONY: magic-verify-all
# ================================================================================================


# Simulate, Build and Verify All Target
all: ## Simulate, build and verify the TOP cell
	$(MAKE) sim-all
	$(MAKE) klayout-verify-all
	$(MAKE) magic-verify-all
	$(MAKE) build-top
.PHONY: all