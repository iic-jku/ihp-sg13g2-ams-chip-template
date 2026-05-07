// SPDX-FileCopyrightText: 2026 Simon Dorrer
// SPDX-License-Identifier: Apache-2.0
// Description: This file implements a SystemVerilog testbench for the counter_top entity.

`timescale 1ns / 1ps

module counter_top_tb;
  // Constants
  parameter real CLK_FREQ         = `CLK_FREQ_DEFAULT;
  parameter int  COUNTER_MAX      = `COUNTER_MAX_DEFAULT;
  parameter int  COUNTER_BITWIDTH = $clog2(COUNTER_MAX + 1);

  // Inputs
  reg clock   = 0;
  reg reset_n = 1; // active-low reset
  reg enable  = 0;

  // Outputs
  wire [COUNTER_BITWIDTH-1:0] counter_value;

  // DUT
  counter_top #(
    .COUNTER_MAX(COUNTER_MAX)
  ) dut_counter (
    .clock_i(clock),
    .reset_n_i(reset_n),
    .enable_i(enable),
    .counter_value_o(counter_value)
  );

  // Generate clock
  /* verilator lint_off STMTDLY */
  always begin
    #(1e9 / (2 * CLK_FREQ)); // half-period in ns
    clock = ~clock;
  end
  /* verilator lint_on STMTDLY */

  // Simple self-check: counter must be 0 right after reset deassertion
  initial begin
    $dumpfile("counter_top_tb.vcd");
    $dumpvars;

    // Reset pulse
    reset_n = 0;
    #(2 * (1e9 / CLK_FREQ));
    reset_n = 1;
    #(1e9 / CLK_FREQ);

    if (counter_value !== {COUNTER_BITWIDTH{1'b0}}) begin
      $display("FAIL: counter not zero after reset (got %0d)", counter_value);
      $fatal;
    end

    // Hold disabled for a few cycles, value must not change
    #(5 * (1e9 / CLK_FREQ));
    if (counter_value !== {COUNTER_BITWIDTH{1'b0}}) begin
      $display("FAIL: counter changed while disabled (got %0d)", counter_value);
      $fatal;
    end

    // Enable counter, run for one full wrap + a few extra cycles
    enable = 1;
    #((COUNTER_MAX + 5) * (1e9 / CLK_FREQ));
    enable = 0;

    // Disabled hold check
    #(5 * (1e9 / CLK_FREQ));

    // Re-enable, run another batch
    enable = 1;
    #(10 * (1e9 / CLK_FREQ));
    enable = 0;
    #(2 * (1e9 / CLK_FREQ));

    /* verilator lint_off STMTDLY */
    $display("End of simulation.");
    $finish;
    /* verilator lint_on STMTDLY */
  end
endmodule // counter_top_tb
