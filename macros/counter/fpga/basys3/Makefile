# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Board: Basys 3 (Xilinx Artix-7 xc7a35tcpg236-1). The counter_top ports
# (clock_i, reset_n_i, enable_i, counter_value_o) are mapped straight onto
# board pins, no board-top wrapper. reset_n_i/enable_i are the sw[0]/sw[1]
# toggles, not the momentary buttons: those are active-high on this board,
# which would hold reset_n_i asserted at idle. See ../README.md.

TOP := counter_top

include ../dut.mk
MODULES_SYNTH := $(DUT_SRCS)

PCF_FILE := basys3.xdc

include $(TOP_FPGA_DIR)/boards/basys3.mk
include $(TOP_FPGA_DIR)/fpga.mk
