// SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
// Description: Shared constants for the counter macro.
//
// Implemented as `define macros (not a SystemVerilog package) for Yosys 0.64
// compatibility — its Verilog frontend cannot parse `import pkg::*;` in a
// module header. Compile constants.sv before any module that references the
// macros (the Makefiles list it first in MODULES_SIM/MODULES_SYNTH).

`ifndef __COUNTER_CONSTANTS__
`define __COUNTER_CONSTANTS__

// Default clock frequency for simulations and testbenches (Hz)
`define CLK_FREQ_DEFAULT      50.0e6

// Default upper bound (inclusive) of the counter range: counts 0 .. COUNTER_MAX
`define COUNTER_MAX_DEFAULT   255

`endif
