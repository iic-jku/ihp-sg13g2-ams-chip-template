// SPDX-FileCopyrightText: 2025-2026 The Chip Team
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module chip_core #(
    parameter NUM_INPUT_PADS,
    parameter NUM_OUTPUT_PADS,
    parameter NUM_BIDIR_PADS,
    parameter NUM_ANALOG_PADS
    )(
	`ifdef USE_POWER_PINS
    inout  wire VDD,
    inout  wire VSS,
    `endif
	
    input  logic clk,       // clock
    input  logic rst_n,     // reset (active low)
    
    input  wire [NUM_INPUT_PADS-1 :0] input_in,   		// Input value
    output wire [NUM_OUTPUT_PADS-1:0] output_out, 		// Output value
    input  wire [NUM_BIDIR_PADS-1 :0] bidir_in,   		// Input value
    output wire [NUM_BIDIR_PADS-1 :0] bidir_out,  		// Output value
    output wire [NUM_BIDIR_PADS-1 :0] bidir_oe,   		// Output enable

    inout  wire [NUM_ANALOG_PADS-1:0] analog_padres, 	// Analog (via pad secondary ESD protection)
	inout  wire [NUM_ANALOG_PADS-1:0] analog_padbare    // Analog (direct pad connection with primary ESD protection)
);
	// ======================================================
	// Counter (Digital)
	// ======================================================
	logic si;
	logic sclk;
	logic sram_ce;
	logic sda_o;
	logic sda_oe;
	logic scl;
	logic tx;
	logic [3:0] gpio_out;
	logic analog_en;
	logic I_ae;
	logic ds_I_oe;
	logic ds_I_p_o;
    logic ds_I_n_o;
	logic lo_I_oe;
    logic lo_I_o;
	logic lo_Ix_o;
    logic lo_Qx_o;
	logic lo_Q_o;
	logic lo_Q_oe;
	logic ds_Q_n_o;
	logic ds_Q_p_o;
	logic ds_Q_oe;
	logic Q_ae;
	
	counter_top counter_top (
		`ifdef USE_POWER_PINS
        .VDD(VDD),
		.VSS(VSS),
		`endif
		.clk(clk),
		.reset(rst_n),
		.so(input_in[5]),
		.si(si),
		.sclk(sclk),
		.sram_ce(sram_ce),
		.sda_i(bidir_in[8]),
		.sda_o(sda_o),
		.sda_oe(sda_oe),
		.scl(scl),
		.rx(input_in[4]),
		.tx(tx),
		.gpio_in(input_in[3:0]),
		.gpio_out(gpio_out),
		.analog_en(analog_en),
		.I_ae(I_ae),
		.ds_I_oe(ds_I_oe),
		.ds_I_p_i(bidir_in[0]),
		.ds_I_p_o(ds_I_p_o),
		.ds_I_n_i(bidir_in[1]),
		.ds_I_n_o(ds_I_n_o),
		.lo_I_oe(lo_I_oe),
		.lo_I_i(bidir_in[2]),
		.lo_I_o(lo_I_o),
		.lo_Ix_i(bidir_in[3]),
		.lo_Ix_o(lo_Ix_o),
		.lo_Qx_i(bidir_in[7]),
		.lo_Qx_o(lo_Qx_o),
		.lo_Q_i(bidir_in[6]),
		.lo_Q_o(lo_Q_o),
		.lo_Q_oe(lo_Q_oe),
		.ds_Q_n_i(bidir_in[5]),
		.ds_Q_n_o(ds_Q_n_o),
		.ds_Q_p_i(bidir_in[4]),
		.ds_Q_p_o(ds_Q_p_o),
		.ds_Q_oe(ds_Q_oe),
		.Q_ae(Q_ae)
	);
	// ======================================================
	
	// ======================================================
	// Inverter (Analog)
	// ======================================================
	wire voutp_I_RF;
	wire voutn_I_RF;
	wire voutn_Q_RF;
	wire voutp_Q_RF;
	
	inverter_top inverter_top (
		`ifdef USE_POWER_PINS
		.VDD(VDD),
		.VSS(VSS),
		`endif
		.di_analog_en(analog_en),
		.di_spdt_ctrl_I(I_ae),
		.vinp_I(analog_padres[7]),
		.di_ds_I_p(ds_I_p_o),
		.vinn_I(analog_padres[6]),
		.di_ds_I_n(ds_I_n_o),
		.di_lo_I(lo_I_o),
		.di_lo_Ix(lo_Ix_o),
		.di_lo_Qx(lo_Qx_o),
		.di_lo_Q(lo_Q_o),
		.di_ds_Q_n(ds_Q_n_o),
		.vinn_Q(analog_padres[1]),
		.di_ds_Q_p(ds_Q_p_o),
		.vinp_Q(analog_padres[0]),
		.di_spdt_ctrl_Q(Q_ae),
		.voutp_I_RF(voutp_I_RF),
		.voutn_I_RF(voutn_I_RF),
		.voutn_Q_RF(voutn_Q_RF),
		.voutp_Q_RF(voutp_Q_RF)
	);
	// ======================================================
	
	// ======================================================
	// Assignments
    // ======================================================
	// counter
	// Outputs
	assign output_out[8] = si;
	assign output_out[7] = sclk;
	assign output_out[6] = sram_ce;
	assign output_out[5] = scl;
	assign output_out[4] = tx;
	assign output_out[3] = gpio_out[3];
	assign output_out[2] = gpio_out[2];
	assign output_out[1] = gpio_out[1];
	assign output_out[0] = gpio_out[0];
	
	// Bidirectionals
	// [8] sda
	assign bidir_out[8] = sda_o;
	assign bidir_oe[8]  = sda_oe;

	// [7] lo_Qx
	assign bidir_out[7] = lo_Qx_o;
	assign bidir_oe[7]  = lo_Q_oe;

	// [6] lo_Q
	assign bidir_out[6] = lo_Q_o;
	assign bidir_oe[6]  = lo_Q_oe;
	
	// [5] ds_Q_n
	assign bidir_out[5] = ds_Q_n_o;
	assign bidir_oe[5]  = ds_Q_oe;
	
	// [4] ds_Q_p
	assign bidir_out[4] = ds_Q_p_o;
	assign bidir_oe[4]  = ds_Q_oe;

	// [3] lo_Ix
	assign bidir_out[3] = lo_Ix_o;
	assign bidir_oe[3]  = lo_I_oe;
	
	// [2] lo_I
	assign bidir_out[2] = lo_I_o;
	assign bidir_oe[2]  = lo_I_oe;
	
	// [1] ds_I_n
	assign bidir_out[1] = ds_I_n_o;
	assign bidir_oe[1]  = ds_I_oe;
	
	// [0] ds_I_p
	assign bidir_out[0] = ds_I_p_o;
	assign bidir_oe[0]  = ds_I_oe;

	// Inverter
	// Not connected analog pads (only padres or padbare is connected per analog pad)
	// - analog_padres[2], analog_padres[3], analog_padres[4], analog_padres[5]
	// - analog_padbare[0], analog_padbare[1], analog_padbare[6], analog_padbare[7]
	
	assign analog_padbare[5] = voutp_I_RF;
	assign analog_padbare[4] = voutn_I_RF;
	assign analog_padbare[3] = voutn_Q_RF;
	assign analog_padbare[2] = voutp_Q_RF;
	// ======================================================
endmodule

`default_nettype wire
