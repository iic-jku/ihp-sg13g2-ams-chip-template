// SPDX-FileCopyrightText: 2025-2026 The Chip Team
// SPDX-License-Identifier: Apache-2.0

`timescale 1ns / 1ps;

module riscv_top_tb ();
  localparam real F_CLK = 12_000_000;
  realtime PERIOD_NS = (1 / F_CLK) * 1_000_000_000;
  realtime HALFPERIOD_NS = PERIOD_NS / 2;

  logic clk, reset, memwrite, valid, busy, ce;
  logic so, si, sclk, sram_ce;
  logic rst_n;
  logic intr_ext;
  logic [3:0] gpio_in;

  logic rx;
  logic uart_en;
  riscv_top dut (
      .clk(clk),
      .reset(rst_n),
      .so(so),
      .si(si),
      .sclk(sclk),
      .sram_ce(sram_ce),
      .gpio_in(gpio_in),
      .rx(rx)
  );

  assign gpio_in = {3'b0, intr_ext};
  sram_sim #(
      .INIT_FILE("demo.txt")
  ) sram (
      .sclk(sclk),
      .reset(reset),
      .ce(sram_ce),
      .si(si),
      .so(so)
  );

  uart_tx uart_tx (
      .clk(clk),
      .resetn(rst_n),
      .uart_txd(rx),
      .uart_tx_data(8'hA5),
      .uart_tx_en(uart_en)
  );

  always begin
    clk   = 0;
    reset = 1;
    rst_n = 0;

    forever #HALFPERIOD_NS clk = ~clk;
  end

  logic [7:0] memory_content[200];
  generate
    genvar i;
    for (i = 0; i < 200; i = i + 1) begin
      assign memory_content[i] = sram.mem[i];
    end
  endgenerate

  initial begin
    $dumpfile("riscv_top_tb.vcd");
    $dumpvars(0, dut, sram, uart_tx);

    intr_ext = 0;
    uart_en  = 0;

    // Uncomment and adjust the name to your own instance names for regs
    // and registers
    for (int i = 0; i < 200; i++) $dumpvars(1, memory_content[i]);

    #PERIOD_NS;
    #PERIOD_NS;
    reset = 0;
    rst_n = 1;
    // for (int i = 0; i < 300000; i++) #PERIOD_NS;
    #20_000_000;
    // intr_ext = 1;
    uart_en = 1;
    #PERIOD_NS;
    #PERIOD_NS;
    #PERIOD_NS;
    #PERIOD_NS;
    #PERIOD_NS;
    #PERIOD_NS;
    intr_ext = 0;
    uart_en  = 0;

    #20_000_000;
    #20_000_000;
    #20_000_000;
    #20_000_000;
    #20_000_000;
    #20_000_000;
    $display("\033[32mTestbench finished running! Verify with the waveform\033[0m");
    $finish;
  end

  // initial begin : ext_interrupt
  //     intr_ext = 0;
  //     #10000;
  //     intr_ext = 0;
  //     // intr_ext = 1;
  //     #2;
  //     intr_ext = 0;
  // end

endmodule  // cputb
