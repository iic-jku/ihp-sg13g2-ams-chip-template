// SPDX-FileCopyrightText: 2026 Simon Dorrer
// SPDX-License-Identifier: Apache-2.0
// Description: This file implements an N-Bit counter with synchronous reset & enable in SystemVerilog.

module counter_top #(
  parameter COUNTER_BITWIDTH = 8,
  parameter COUNTER_MAX = 255
)(
  input wire clock_i,
  input wire reset_n_i,
  input wire enable_i,
  
  output wire [COUNTER_BITWIDTH-1:0] counter_value_o
);
	
  // Internal signals
  wire reset;
  reg [COUNTER_BITWIDTH-1:0] counter_value;
  // =====================================================
  
  // Inverting Input Logic
  assign reset = ~reset_n_i;

  // Counter Implementation
  always @(posedge clock_i) begin 
		if (reset == 1'b1) begin
			// if reset is enabled
			counter_value <= {COUNTER_BITWIDTH{1'b0}}; //reset the counter value
		end else if (enable_i == 1'b1) begin
			// increment the counter value by 1, wrap around at COUNTER_MAX
			if (counter_value == COUNTER_MAX[COUNTER_BITWIDTH-1:0])
				counter_value <= {COUNTER_BITWIDTH{1'b0}};
			else
				counter_value <= counter_value + 1'b1;
		end
	end
  // =====================================================
  
  // Concurrent statement
	// assign the counter value to the output
  assign counter_value_o = counter_value;
  // =====================================================
endmodule // counter_top