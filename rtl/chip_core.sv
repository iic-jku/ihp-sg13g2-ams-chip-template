// SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
// Description: Top-level chip core.
// Instantiates and connects the digital and analog macros.

`default_nettype none

module chip_core #(
    parameter int unsigned NUM_INPUT_PADS,
    parameter int unsigned NUM_OUTPUT_PADS,
    parameter int unsigned NUM_BIDIR_PADS,
    parameter int unsigned NUM_ANALOG_PADS
)(
    `ifdef USE_POWER_PINS
    inout  wire VDD,
    inout  wire VSS,
    `endif

    input  logic clk,       // clock
    input  logic rst_n,     // reset (active low)

    input  logic [NUM_INPUT_PADS-1 :0] input_in,        // Input value
    output logic [NUM_OUTPUT_PADS-1:0] output_out,      // Output value
    input  logic [NUM_BIDIR_PADS-1 :0] bidir_in,        // Bidir input value
    output logic [NUM_BIDIR_PADS-1 :0] bidir_out,       // Bidir output value
    output logic [NUM_BIDIR_PADS-1 :0] bidir_oe,        // Bidir output enable

    inout  wire  [NUM_ANALOG_PADS-1:0] analog_padres,   // Analog (via pad secondary ESD protection)
    inout  wire  [NUM_ANALOG_PADS-1:0] analog_padbare   // Analog (direct pad connection with primary ESD protection)
);

    // ======================================================
    // Input Assignments
    // ======================================================
    logic enable;
    assign enable = input_in[0];

    // Inverter 1 (vin* are inout ports on inverter_top -> must be wire)
    wire inv1_din1 = bidir_in[0];
    wire inv1_din2 = bidir_in[1];
    wire inv1_din3 = bidir_in[2];
    wire inv1_din4 = bidir_in[3];

    // Inverter 2 (analog inputs tapped from the pad ring)
    wire inv2_vin1 = analog_padres[0];
    wire inv2_vin2 = analog_padres[1];
    // ======================================================

    // ======================================================
    // Counter 1 (digital macro)
    // ======================================================
    logic [7:0] counter1_value;

    counter_top counter1 (
        `ifdef USE_POWER_PINS
        .VDD(VDD),
        .VSS(VSS),
        `endif
        .clock_i        (clk),
        .reset_n_i      (rst_n),
        .enable_i       (enable),
        .counter_value_o(counter1_value)
    );
    // ======================================================

    // ======================================================
    // Counter 2 (digital macro)
    // ======================================================
    logic [7:0] counter2_value;

    counter_top counter2 (
        `ifdef USE_POWER_PINS
        .VDD(VDD),
        .VSS(VSS),
        `endif
        .clock_i        (clk),
        .reset_n_i      (rst_n),
        .enable_i       (enable),
        .counter_value_o(counter2_value)
    );
    // ======================================================

    // ======================================================
    // Inverter 1 (analog macro, used as digital inverter)
    // ======================================================
    wire inv1_dout1;
    wire inv1_dout2;
    wire inv1_dout3;
    wire inv1_dout4;

    inverter_top inverter1 (
        `ifdef USE_POWER_PINS
        .VDD  (VDD),
        .VSS  (VSS),
        `endif
        .vin1 (inv1_din1),
        .vin2 (inv1_din2),
        .vin3 (inv1_din3),
        .vin4 (inv1_din4),
        .vout1(inv1_dout1),
        .vout2(inv1_dout2),
        .vout3(inv1_dout3),
        .vout4(inv1_dout4)
    );
    // ======================================================

    // ======================================================
    // Inverter 2 (analog macro)
    // ======================================================
    `ifdef USE_POWER_PINS
    wire vss_tie = VSS;
    `else
    wire vss_tie = 1'b0;
    `endif

    wire inv2_vout1;
    wire inv2_vout2;

    inverter_top inverter2 (
        `ifdef USE_POWER_PINS
        .VDD  (VDD),
        .VSS  (VSS),
        `endif
        .vin1 (inv2_vin1),
        .vin2 (inv2_vin2),
        .vin3 (vss_tie),
        .vin4 (vss_tie),
        .vout1(inv2_vout1),
        .vout2(inv2_vout2),
        .vout3(vss_tie),
        .vout4(vss_tie)
    );
    // ======================================================

    // ======================================================
    // 1024 x 32 SRAM (digital macro)
    // ======================================================
    logic [31:0] sram_0_out;

    RM_IHPSG13_1P_1024x32_c2_bm_bist sram_0 (
        .A_CLK  (clk),
        .A_MEN  (1'b1),
        .A_WEN  (1'b0),
        .A_REN  (1'b1),
        .A_ADDR ('0),
        .A_DIN  ('0),
        .A_DLY  (1'b1), // tie high!
        .A_DOUT (sram_0_out),
        .A_BM   ('0),

        // Built-in self test port
        .A_BIST_CLK   ('0),
        .A_BIST_EN    ('0),
        .A_BIST_MEN   ('0),
        .A_BIST_WEN   ('0),
        .A_BIST_REN   ('0),
        .A_BIST_ADDR  ('0),
        .A_BIST_DIN   ('0),
        .A_BIST_BM    ('0)
    );
    // ======================================================

    // ======================================================
    // Output Assignments
    // ======================================================
    // Digital outputs
    // Counter 1
    assign output_out[0]  = counter1_value[0];
    assign output_out[1]  = counter1_value[1];
    assign output_out[2]  = counter1_value[2];
    assign output_out[3]  = counter1_value[3];

    // Counter 2
    assign output_out[4]  = counter2_value[0];
    assign output_out[5]  = counter2_value[1];
    assign output_out[6]  = counter2_value[2];
    assign output_out[7]  = counter2_value[3];
    assign output_out[8]  = counter2_value[4];
    assign output_out[9]  = counter2_value[5];
    assign output_out[10] = counter2_value[6];
    assign output_out[11] = counter2_value[7];

    // Inverter 1
    assign output_out[12] = inv1_dout1;
    assign output_out[13] = inv1_dout2;
    assign output_out[14] = inv1_dout3;
    assign output_out[15] = inv1_dout4;

    // SRAM
    // Reduce the 32-bit SRAM output to a single bit by computing the parity.
    // output_out[16] = 1 when an odd number of bits in sram_0_out are 1.
    // output_out[16] = 0 when an even number of bits in sram_0_out are 1.
    assign output_out[16] = ^sram_0_out;

    // Digital bidirectionals (output side)
    // Bidir output enable: drive when `enable` is high (counter visible),
    // float as input when low (so external stimuli can drive inverter1).
    assign bidir_out[0] = counter1_value[4];
	assign bidir_oe[0]  = enable;

    assign bidir_out[1] = counter1_value[5];
	assign bidir_oe[1]  = enable;

    assign bidir_out[2] = counter1_value[6];
	assign bidir_oe[2]  = enable;

    assign bidir_out[3] = counter1_value[7];
	assign bidir_oe[3]  = enable;

    // Analog outputs
    assign analog_padbare[2] = inv2_vout1;
    assign analog_padbare[3] = inv2_vout2;
    // ======================================================
endmodule

`default_nettype wire
