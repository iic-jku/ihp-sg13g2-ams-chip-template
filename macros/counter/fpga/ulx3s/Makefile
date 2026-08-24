# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Board: ULX3S (Lattice ECP5-85F). The counter_top ports (clock_i, reset_n_i,
# enable_i, counter_value_o) are mapped straight onto board pins, no board-top
# wrapper. See ../README.md.

TOP := counter_top

include ../dut.mk
MODULES_SYNTH := $(DUT_SRCS)

PCF_FILE := ulx3s.lpf

include $(TOP_FPGA_DIR)/boards/ulx3s.mk
include $(TOP_FPGA_DIR)/fpga.mk
