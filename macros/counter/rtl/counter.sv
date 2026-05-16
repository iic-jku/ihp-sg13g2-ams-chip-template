// SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
// Description: This file implements an N-bit up counter with
// synchronous reset & enable in SystemVerilog.

`default_nettype none
`ifndef __COUNTER__
`define __COUNTER__

module counter #(
  parameter int unsigned       CTR_BW  = 8,
  parameter logic [CTR_BW-1:0] CTR_MAX = 2**CTR_BW - 1
)(
  input logic               clock_i,
  input logic               reset_i,
  input logic               enable_i,

  output logic [CTR_BW-1:0] counter_value_o
);

  // Counter implementation
  always_ff @(posedge clock_i) begin
    if (reset_i) begin
      // Synchronous reset clears the counter value
      counter_value_o <= '0;
    end else if (enable_i) begin
      // Increment the counter value by 1, wrap around at CTR_MAX
      if (counter_value_o == CTR_MAX) begin
        counter_value_o <= '0;
      end else begin
        counter_value_o <= counter_value_o + 1;
      end
    end
  end

endmodule // counter

`endif
`default_nettype wire
