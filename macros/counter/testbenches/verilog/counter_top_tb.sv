// SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
// Description: SystemVerilog testbench for the counter_top module.

`timescale 1ns / 1ps

module counter_top_tb;
  // Parameters
  parameter  real CLK_FREQ      = `CLK_FREQ_DEFAULT;
  parameter  int  CTR_MAX       = `COUNTER_MAX_DEFAULT;
  localparam int  CTR_BW        = $clog2(CTR_MAX + 1);
  localparam real CLK_PERIOD_NS = 1e9 / CLK_FREQ;

  // Signals
  logic              clock   = 1'b0;
  logic              reset_n = 1'b1; // active-low reset
  logic              enable  = 1'b0;
  logic [CTR_BW-1:0] counter_value;

  // DUT
  counter_top #(
    .CTR_MAX(CTR_MAX)
  ) dut_counter (
    .clock_i(clock),
    .reset_n_i(reset_n),
    .enable_i(enable),
    .counter_value_o(counter_value)
  );

  // Clock generation
  /* verilator lint_off STMTDLY */
  always #(CLK_PERIOD_NS / 2) clock = ~clock;
  /* verilator lint_on STMTDLY */

  // Self-checking stimulus
  initial begin
    $dumpfile("counter_top_tb.vcd");
    $dumpvars;

    // Reset pulse (2 clock cycles)
    reset_n = 1'b0;
    #(2 * CLK_PERIOD_NS);
    reset_n = 1'b1;
    #(CLK_PERIOD_NS);

    if (counter_value !== '0)
      $fatal(1, "FAIL: counter not zero after reset (got %0d)", counter_value);

    // Hold disabled for a few cycles; value must not change
    #(5 * CLK_PERIOD_NS);
    if (counter_value !== '0)
      $fatal(1, "FAIL: counter changed while disabled (got %0d)", counter_value);

    // Enable counter, run for one full wrap and a few extra cycles
    enable = 1'b1;
    #((CTR_MAX + 5) * CLK_PERIOD_NS);
    enable = 1'b0;

    // Disabled hold check
    #(5 * CLK_PERIOD_NS);

    // Re-enable, run another batch
    enable = 1'b1;
    #(10 * CLK_PERIOD_NS);
    enable = 1'b0;
    #(2 * CLK_PERIOD_NS);

    $display("PASS: simulation complete.");
    $finish;
  end
endmodule // counter_top_tb
