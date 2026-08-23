# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Board: Tang Nano 9K (Gowin GW1NR-9C). The counter_top ports (clock_i,
# reset_n_i, enable_i, counter_value_o) are mapped straight onto board pins,
# no board-top wrapper. See ../README.md.

TOP := counter_top

include ../dut.mk
MODULES_SYNTH := $(DUT_SRCS)

PCF_FILE := nano9k.cst

include $(TOP_FPGA_DIR)/boards/nano9k.mk
include $(TOP_FPGA_DIR)/fpga.mk
