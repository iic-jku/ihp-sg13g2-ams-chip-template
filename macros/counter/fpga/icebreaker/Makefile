# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Board: iCEBreaker (Lattice iCE40UP5K, SG48). The counter_top ports (clock_i,
# reset_n_i, enable_i, counter_value_o) are mapped straight onto board pins,
# no board-top wrapper. See ../README.md.

TOP := counter_top

include ../dut.mk
MODULES_SYNTH := $(DUT_SRCS)

PCF_FILE := icebreaker.pcf

ARCH         := ice40
ICE40_DEVICE := --up5k --package sg48

# openFPGALoader has no dedicated iCEBreaker board profile.
# Must be `=`, not `:=`, since BITSTREAM is only defined later, by fpga.mk.
LOAD_CMD  = iceprog -S $(BITSTREAM)
FLASH_CMD = iceprog $(BITSTREAM)

include $(TOP_FPGA_DIR)/fpga.mk
