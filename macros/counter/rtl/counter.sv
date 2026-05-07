// SPDX-FileCopyrightText: 2026 Simon Dorrer
// SPDX-License-Identifier: Apache-2.0
// Description: This file implements an N-Bit up counter with synchronous reset & enable in SystemVerilog.

`default_nettype none
`ifndef __COUNTER__
`define __COUNTER__

module counter #(
  parameter COUNTER_BITWIDTH = 8,
  parameter COUNTER_MAX = 255
)(
  input wire clock_i,
  input wire reset_i,
  input wire enable_i,
  
  output wire [COUNTER_BITWIDTH-1:0] counter_value_o
);
	
  // Internal signals
  reg [COUNTER_BITWIDTH-1:0] counter_value;
  // =====================================================

  // Counter Implementation
  always @(posedge clock_i) begin 
		if (reset_i == 1'b1) begin
			// if reset is enabled
			counter_value <= {COUNTER_BITWIDTH{1'b0}}; //reset the counter value
		end else if (enable_i == 1'b1) begin
			// increment the counter value by 1, wrap around at COUNTER_MAX
			if (counter_value == COUNTER_MAX[COUNTER_BITWIDTH-1:0])
				counter_value <= {COUNTER_BITWIDTH{1'b0}};
			else
				counter_value <= counter_value + {{(COUNTER_BITWIDTH-1){1'b0}}, 1'b1};
		end
	end
  // =====================================================
  
  // Concurrent statement
	// assign the counter value to the output
  assign counter_value_o = counter_value;
  // =====================================================
endmodule // counter

`endif
`default_nettype wire
