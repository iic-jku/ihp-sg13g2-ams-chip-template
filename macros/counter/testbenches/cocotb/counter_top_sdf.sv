// SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
// Description: Wrapper for the timed gate-level simulation of the
// counter_top netlist. Icarus Verilog annotates the delays of the SDF
// file that the plusarg +SDF=<file> names.

`default_nettype none

module counter_top_sdf (
  input  wire                                        clock_i,
  input  wire                                        reset_n_i,
  input  wire                                        enable_i,
  output wire [$clog2(`COUNTER_MAX_DEFAULT + 1)-1:0] counter_value_o
);

  counter_top u_counter_top (.*);

  string sdf_file;

  initial begin
    if ($value$plusargs("SDF=%s", sdf_file)) begin
      $sdf_annotate(sdf_file, u_counter_top);
    end
  end

endmodule

`default_nettype wire
