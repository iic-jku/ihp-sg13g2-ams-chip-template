# SPDX-FileCopyrightText: 2025-2026 The Chip Team
# SPDX-License-Identifier: Apache-2.0

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

# Folder structure
SCH_DIR         := schematic
LAY_DIR         := layout
SCRIPTS_DIR     := scripts
XSCHEM_TB_DIR   := testbenches
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

sim-cace: ## Run CACE simulations and collect result plots
	cd $(CACE_DIR) && \
	mkdir -p results/iqmod_mfb_lpf results/iqmod_mfb_lpf_ota_core && \
	\
	cace iqmod_mfb_lpf.yaml -p ac_mm_params && \
	cp _runs/RUN_*/parameters/ac_mm_params/Adc_cl_dB_mm.png results/iqmod_mfb_lpf/ && \
	cp _runs/RUN_*/parameters/ac_mm_params/CMRR_dc_dB_mm.png results/iqmod_mfb_lpf/ && \
	cp _runs/RUN_*/parameters/ac_mm_params/fcu_mm.png results/iqmod_mfb_lpf/ && \
	rm -rf _runs/RUN_* && \
	\
	cace iqmod_mfb_lpf.yaml -p ac_mc_params && \
	cp _runs/RUN_*/parameters/ac_mc_params/Adc_cl_dB_mc.png results/iqmod_mfb_lpf/ && \
	cp _runs/RUN_*/parameters/ac_mc_params/CMRR_dc_dB_mc.png results/iqmod_mfb_lpf/ && \
	cp _runs/RUN_*/parameters/ac_mc_params/fcu_mc.png results/iqmod_mfb_lpf/ && \
	rm -rf _runs/RUN_* && \
	\
	cace iqmod_mfb_lpf.yaml -p ac_params && \
	cp _runs/RUN_*/parameters/ac_params/Adc_cl_dB_vs_vdd.png results/iqmod_mfb_lpf/ && \
	cp _runs/RUN_*/parameters/ac_params/CMRR_dc_dB_vs_vdd.png results/iqmod_mfb_lpf/ && \
	cp _runs/RUN_*/parameters/ac_params/fcu_vs_vdd.png results/iqmod_mfb_lpf/ && \
	rm -rf _runs/RUN_* && \
	\
	cace iqmod_mfb_lpf_ota_core.yaml -p ac_mm_params && \
	cp _runs/RUN_*/parameters/ac_mm_params/Adc_ol_dB_mm.png results/iqmod_mfb_lpf_ota_core/ && \
	cp _runs/RUN_*/parameters/ac_mm_params/CMRR_dc_dB_mm.png results/iqmod_mfb_lpf_ota_core/ && \
	cp _runs/RUN_*/parameters/ac_mm_params/fcu_mm.png results/iqmod_mfb_lpf_ota_core/ && \
	rm -rf _runs/RUN_* && \
	\
	cace iqmod_mfb_lpf_ota_core.yaml -p ac_mc_params && \
	cp _runs/RUN_*/parameters/ac_mc_params/Adc_ol_dB_mc.png results/iqmod_mfb_lpf_ota_core/ && \
	cp _runs/RUN_*/parameters/ac_mc_params/CMRR_dc_dB_mc.png results/iqmod_mfb_lpf_ota_core/ && \
	cp _runs/RUN_*/parameters/ac_mc_params/fcu_mc.png results/iqmod_mfb_lpf_ota_core/ && \
	rm -rf _runs/RUN_* && \
	\
	cace iqmod_mfb_lpf_ota_core.yaml -p ac_params && \
	cp _runs/RUN_*/parameters/ac_params/Adc_ol_dB_vs_vdd.png results/iqmod_mfb_lpf_ota_core/ && \
	cp _runs/RUN_*/parameters/ac_params/CMRR_dc_dB_vs_vdd.png results/iqmod_mfb_lpf_ota_core/ && \
	cp _runs/RUN_*/parameters/ac_params/fcu_vs_vdd.png results/iqmod_mfb_lpf_ota_core/ && \
	rm -rf _runs/RUN_* && \
	\
	rm -rf _runs _docs netlist
.PHONY: sim-cace

sim-all: ## Simulate the macro
	$(MAKE) sim-xschem TB=iqmod_mfb_lpf_ota_core_tb_ac_ol
	$(MAKE) sim-xschem TB=iqmod_mfb_lpf_tb_ac_cl
	$(MAKE) sim-xschem TB=iqmod_mixer_se2diff_tb_tran
	$(MAKE) sim-xschem TB=iqmod_mixer_tb_tran
	$(MAKE) sim-xschem TB=iqmod_top_tb_ac
	$(MAKE) sim-xschem TB=iqmod_top_tb_tran
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
verilog: ## Generate a Verilog stub of the TOP cell from PEX netlist pins
	rm -rf $(VH_DIR)
	mkdir -p $(VH_DIR)
	@echo 'module $(TOP) (' > $(VH_DIR)/$(TOP).v
	@echo '`ifdef USE_POWER_PINS' >> $(VH_DIR)/$(TOP).v
	@echo '    inout VDD,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout VSS,' >> $(VH_DIR)/$(TOP).v
	@echo '`endif' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_analog_en,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_spdt_ctrl_I,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout vinp_I,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_ds_I_p,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout vinn_I,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_ds_I_n,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_lo_I,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_lo_Ix,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_lo_Qx,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_lo_Q,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_ds_Q_n,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout vinn_Q,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_ds_Q_p,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout vinp_Q,' >> $(VH_DIR)/$(TOP).v
	@echo '    input di_spdt_ctrl_Q,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout voutp_I_RF,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout voutn_I_RF,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout voutn_Q_RF,' >> $(VH_DIR)/$(TOP).v
	@echo '    inout voutp_Q_RF' >> $(VH_DIR)/$(TOP).v
	@echo ');' >> $(VH_DIR)/$(TOP).v
	@echo 'endmodule' >> $(VH_DIR)/$(TOP).v
	@echo "Checking PEX pins against Verilog stub..."
	@pex_pins=$$(awk '/^\.subckt $(TOP)_pex/{sub(/^\.subckt [^ ]+ /,"");p=$$0;next} p&&/^[+]/{sub(/^[+] */,"");p=p" "$$0;next} p{exit} END{print p}' $(NET_PEX_DIR)/$(TOP)_pex.spice); \
	vh_pins=$$(grep -oP '(?<=inout |input )\w+' $(VH_DIR)/$(TOP).v | tr '\n' ' '); \
	fail=0; \
	for pin in $$pex_pins; do \
		if ! echo " $$vh_pins " | grep -qw "$$pin"; then \
			echo "ERROR: PEX pin '$$pin' missing from Verilog stub!"; \
			fail=1; \
		fi; \
	done; \
	for pin in $$vh_pins; do \
		if ! echo " $$pex_pins " | grep -qw "$$pin"; then \
			echo "ERROR: Verilog pin '$$pin' not found in PEX netlist!"; \
			fail=1; \
		fi; \
	done; \
	if [ "$$fail" -ne 0 ]; then exit 1; fi; \
	echo "All pins match between PEX netlist and Verilog stub."
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
		--layout=$(LAY_DIR)/$(CELL).klay.gds \
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
	sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(NET_SCH_DIR)/$(CELL)_magic.spice -l $(LAY_DIR)/$(CELL).gds -c $(CELL)
# 	Alternative using sak-lvs.sh for netlist export and LVS in one step (replaces magic-lvs-netlist target):
#   sak-lvs.sh -d -w $(LVS_RPT_DIR) -s $(SCH_DIR)/$(CELL).sch -l $(LAY_DIR)/$(CELL).gds -c $(CELL)
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
		--path=$(LAY_DIR)/$(CELL).klay.gds \
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
	--schematic $(SCH_DIR)/$(CELL).sch \
	--gds $(LAY_DIR)/$(CELL).gds \
	--magic \
	--magic_mode $$KPEX_MODE \
	--out_dir $(NET_PEX_DIR) \
	--out_spice $(NET_PEX_DIR)/$(CELL)_klayout_pex.spice
#	--2.5D
#	--mode $$KPEX_MODE
	sed -i 's/$(CELL)_flat/$(CELL)_pex/g' $(NET_PEX_DIR)/$(CELL)_klayout_pex.spice
	rm -rf $(NET_PEX_DIR)/$(CELL)__$(CELL)
	rm -f $(CELL)_flat.nodes $(CELL)_flat.sim
	@if [ -f $(SCH_DIR)/$(CELL)_pex.sym ]; then \
		echo "Reordering pins in $(CELL)_klayout_pex.spice to match $(CELL)_pex.sym..."; \
		python3 $(NET_PEX_DIR)/reorder_spice_pins.py $(SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_klayout_pex.spice; \
	else \
		echo "No symbol $(SCH_DIR)/$(CELL)_pex.sym found, skipping pin reorder."; \
	fi
	sleep 4
.PHONY: klayout-pex

magic-pex: ## Run Parasitic Extraction with Magic of the CELL cell (usage: make magic-pex [CELL=<cellname>] [EXT_MODE=<1|2|3>])
	mkdir -p $(NET_PEX_DIR)
	sak-pex.sh -d -m $(EXT_MODE) -w $(NET_PEX_DIR) $(LAY_DIR)/$(CELL).gds
	mv $(NET_PEX_DIR)/$(CELL).pex.spice $(NET_PEX_DIR)/$(CELL)_magic_pex.spice
	sed -i 's/$(CELL)/$(CELL)_pex/g' $(NET_PEX_DIR)/$(CELL)_magic_pex.spice
	rm -f $(NET_PEX_DIR)/pex_$(CELL).tcl $(NET_PEX_DIR)/$(CELL).ext $(NET_PEX_DIR)/$(CELL)_flat.ext $(NET_PEX_DIR)/$(CELL)_flat.res.ext
	@if [ -f $(SCH_DIR)/$(CELL)_pex.sym ]; then \
		echo "Reordering pins in $(CELL)_magic_pex.spice to match $(CELL)_pex.sym..."; \
		python3 $(NET_PEX_DIR)/reorder_spice_pins.py $(SCH_DIR)/$(CELL)_pex.sym $(NET_PEX_DIR)/$(CELL)_magic_pex.spice; \
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

klayout-verify-all: ## Verify all main subcells with KLayout (LVS, DRC, PEX)
	$(MAKE) klayout-verify CELL=iqmod_mfb_lpf
	$(MAKE) klayout-verify CELL=iqmod_mixer
	$(MAKE) klayout-verify CELL=iqmod_top
.PHONY: klayout-verify-all

magic-verify: ## Verify CELL cell with Magic (usage: make magic-verify [CELL=<cellname>])
	$(MAKE) magic-lvs CELL=$(CELL)
	$(MAKE) magic-drc CELL=$(CELL)
	$(MAKE) magic-pex CELL=$(CELL)
.PHONY: magic-verify

magic-verify-all: ## Verify all main subcells with Magic (LVS, DRC, PEX)
	$(MAKE) magic-verify CELL=iqmod_mfb_lpf
	$(MAKE) magic-verify CELL=iqmod_mixer
	$(MAKE) magic-verify CELL=iqmod_top
.PHONY: magic-verify-all
# ================================================================================================


# Simulate, Build and Verify All Target
all: ## Simulate, build and verify the TOP cell
	$(MAKE) sim-all
	$(MAKE) build-top
	$(MAKE) klayout-verify-all
	$(MAKE) magic-verify-all
.PHONY: all