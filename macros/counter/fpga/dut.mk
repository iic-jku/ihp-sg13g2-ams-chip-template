# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# RTL of the design under test, shared by all boards.
#
# constants.sv defines the `COUNTER_MAX_DEFAULT / `CLK_FREQ_DEFAULT macros and must
# compile before any module that references them, so it is the first entry
# (Yosys 0.64 cannot parse `import pkg::*` in a module header, see rtl/constants.sv).

# Path from a <board>/ folder back to the shared flow (fpga.mk, arch/)
TOP_FPGA_DIR := ..

SRC_DIR := ../../rtl

DUT_SRCS := \
	$(SRC_DIR)/constants.sv \
	$(SRC_DIR)/counter.sv \
	$(SRC_DIR)/counter_top.sv
