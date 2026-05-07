// SPDX-FileCopyrightText: 2026 Simon Dorrer
// SPDX-License-Identifier: Apache-2.0
// Description: This file implements the top-level wrapper module in SystemVerilog.

`default_nettype none
`ifndef __COUNTER_TOP__
`define __COUNTER_TOP__

module counter_top
  import counter_pkg::*;
#(
  parameter  int COUNTER_MAX      = COUNTER_MAX_DEFAULT,
  localparam int COUNTER_BITWIDTH = $clog2(COUNTER_MAX + 1)
)(
  input  wire clock_i,
  input  wire reset_n_i,  // Active-low reset ('1' not pressed, '0' pressed)
  input  wire enable_i,

  output wire [COUNTER_BITWIDTH-1:0] counter_value_o
);

  // Internal active-high reset (wrapper handles polarity conversion)
  wire reset;
  assign reset = ~reset_n_i;

  // Embed Counter
  counter #(
    .COUNTER_BITWIDTH(COUNTER_BITWIDTH),
    .COUNTER_MAX(COUNTER_MAX)
  ) counter_0 (
    .clock_i(clock_i),
    .reset_i(reset),
    .enable_i(enable_i),
    .counter_value_o(counter_value_o)
  );
  // =====================================================
endmodule // counter_top

`endif
`default_nettype wire
