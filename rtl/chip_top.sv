// SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module chip_top #(
    // Power / ground pads for digital core / analog front-end
    parameter NUM_VDD_PADS = 7, 		// 7 x VDD = 1.5V
	parameter NUM_VSS_PADS = 9, 		// 9 x VSS

    // Power/ground pads for I/O
    parameter NUM_IOVDD_PADS = 3, 		// 3 x IOVDD = 3.3V
    parameter NUM_IOVSS_PADS = 3, 		// 3 x IOVSS
    
    // Signal pads
    parameter NUM_INPUT_PADS  = 6,		// 4 x GPIO inputs, so, rx
    parameter NUM_OUTPUT_PADS = 9,		// 4 x GPIO outputs, si, sclk, sram_ce, scl, tx
    parameter NUM_BIDIR_PADS  = 9,		// sda_i / sda_o, lo_I_i / lo_I_o, lo_Ix_i / lo_Ix_o, lo_Q_i / lo_Q_o, lo_Qx_i / lo_Qx_o, Q_p_i / Q_p_o, Q_n_i / Q_n_o, I_p_i / I_p_o, I_n_i / I_n_o
    parameter NUM_ANALOG_PADS = 8 		// Vinp_I, Vinn_I, Voutp_I_RF, Voutn_I_RF, Voutn_Q_RF, Voutp_Q_RF, Vinn_Q, Vinp_Q
    )(
    `ifdef USE_POWER_PINS
    inout wire IOVDD,
    inout wire IOVSS,
    inout wire VDD,
    inout wire VSS,
    `endif
    inout  wire clk_PAD,
    inout  wire rst_n_PAD,
    inout  wire [NUM_INPUT_PADS-1 :0] input_PAD,
    inout  wire [NUM_OUTPUT_PADS-1:0] output_PAD,
    inout  wire [NUM_BIDIR_PADS-1 :0] bidir_PAD,
    inout  wire [NUM_ANALOG_PADS-1:0] analog_PAD
);
	
	// ======================================================
    // Wires
	// ======================================================
	// Clock
    wire clk_PAD2CORE;
	
	// Reset
    wire rst_n_PAD2CORE;
	
	// Inputs
    wire [NUM_INPUT_PADS-1 :0] input_PAD2CORE;

    // Outputs
    wire [NUM_OUTPUT_PADS-1:0] output_CORE2PAD;
	
	// Bidirectionals
    wire [NUM_BIDIR_PADS-1 :0] bidir_PAD2CORE;
    wire [NUM_BIDIR_PADS-1 :0] bidir_CORE2PAD;
    wire [NUM_BIDIR_PADS-1 :0] bidir_CORE2PAD_OE;
	
	// Analog
    wire [NUM_ANALOG_PADS-1:0] analog_PADRES;   // Vinp_I, Vinn_I, Vinn_Q, Vinp_Q
    wire [NUM_ANALOG_PADS-1:0] analog_PADBARE;  // Voutp_I_RF, Voutn_I_RF, Voutn_Q_RF, Voutp_Q_RF
	// ======================================================
	
	// ======================================================
    // VDD - PAD INSTANCES
	// ======================================================
    generate
    for (genvar i=0; i<NUM_VDD_PADS; i++) begin : vdd_pads
        (* keep *)
        sg13g2_IOPadVdd vdd_pad  (
            `ifdef USE_POWER_PINS
            .iovdd  (IOVDD),
            .iovss  (IOVSS),
            .vdd    (VDD),
            .vss    (VSS)
            `endif
        );
    end
    endgenerate
	// ======================================================
	
	// ======================================================
    // VSS - PAD INSTANCES
	// ======================================================
    generate
    for (genvar i=0; i<NUM_VSS_PADS; i++) begin : vss_pads
        (* keep *)
        sg13g2_IOPadVss vss_pad  (
            `ifdef USE_POWER_PINS
            .iovdd  (IOVDD),
            .iovss  (IOVSS),
			.vdd    (VDD),
            .vss    (VSS)
            `endif
        );
    end
    endgenerate
	// ======================================================
	
	// ======================================================
    // IOVDD - PAD INSTANCES
	// ======================================================
    generate
    for (genvar i=0; i<NUM_IOVDD_PADS; i++) begin : iovdd_pads
        (* keep *)
        sg13g2_IOPadIOVdd iovdd_pad  (
            `ifdef USE_POWER_PINS
            .iovdd  (IOVDD),
            .iovss  (IOVSS),
            .vdd    (VDD),
            .vss    (VSS)
            `endif
        );
    end
    endgenerate
	// ======================================================
	
	// ======================================================
	// VSS IO - PAD INSTANCES
	// ======================================================
    generate
    for (genvar i=0; i<NUM_IOVSS_PADS; i++) begin : iovss_pads
        (* keep *)
        sg13g2_IOPadIOVss iovss_pad  (
            `ifdef USE_POWER_PINS
            .iovdd  (IOVDD),
            .iovss  (IOVSS),
            .vdd    (VDD),
            .vss    (VSS)
            `endif
        );
    end
	endgenerate
	// ======================================================
	
    // ======================================================
    // CLOCK - PAD INSTANCE
	// ======================================================
    sg13g2_IOPadIn clk_pad (
        `ifdef USE_POWER_PINS
        .iovdd  (IOVDD),
        .iovss  (IOVSS),
        .vdd    (VDD),
        .vss    (VSS),
        `endif
        .p2c    (clk_PAD2CORE),
        .pad    (clk_PAD)
    );
    // ======================================================
	
	// ======================================================
    // RESET - PAD INSTANCE (active low)
	// ======================================================
    sg13g2_IOPadIn rst_n_pad (
        `ifdef USE_POWER_PINS
        .iovdd  (IOVDD),
        .iovss  (IOVSS),
        .vdd    (VDD),
        .vss    (VSS),
        `endif
        .p2c    (rst_n_PAD2CORE),
        .pad    (rst_n_PAD)
    );
	// ======================================================
	
	// ======================================================
    // SIGNAL INPUTS - PAD INSTANCES
	// ======================================================
    generate
    for (genvar i=0; i<NUM_INPUT_PADS; i++) begin : inputs
        sg13g2_IOPadIn input_pad (
            `ifdef USE_POWER_PINS
            .iovdd  (IOVDD),
            .iovss  (IOVSS),
            .vdd    (VDD),
            .vss    (VSS),
            `endif
            .p2c    (input_PAD2CORE[i]),
            .pad    (input_PAD[i])
        );
    end
    endgenerate
	// ======================================================
	
	// ======================================================
    // SIGNAL OUTPUTS - PAD INSTANCES
	// ======================================================
    generate
    for (genvar i=0; i<NUM_OUTPUT_PADS; i++) begin : outputs
        sg13g2_IOPadOut30mA output_pad (
            `ifdef USE_POWER_PINS
            .iovdd  (IOVDD),
            .iovss  (IOVSS),
            .vdd    (VDD),
            .vss    (VSS),
            `endif
            .c2p    (output_CORE2PAD[i]),
            .pad    (output_PAD[i])
        );
    end
    endgenerate
	// ======================================================
	
	// ======================================================
    // SIGNAL BIDIRECTIONALS - PAD INSTANCES
	// ======================================================
    generate
    for (genvar i=0; i<NUM_BIDIR_PADS; i++) begin : bidirs
        sg13g2_IOPadInOut30mA bidir_pad (
            `ifdef USE_POWER_PINS
            .iovdd  (IOVDD),
            .iovss  (IOVSS),
            .vdd    (VDD),
            .vss    (VSS),
            `endif
            .c2p    (bidir_CORE2PAD[i]),
            .c2p_en (bidir_CORE2PAD_OE[i]),
            .p2c    (bidir_PAD2CORE[i]),
            .pad    (bidir_PAD[i])
        );
    end
    endgenerate
    // ======================================================
	
	// ======================================================
    // SIGNAL ANALOG - PAD INSTANCES
	// ======================================================
    generate
    for (genvar i=0; i<NUM_ANALOG_PADS; i++) begin : analogs
        (* keep *)
        sg13g2_IOPadAnalog analog_pad (
            `ifdef USE_POWER_PINS
            .iovdd  (IOVDD),
            .iovss  (IOVSS),
			.vdd    (VDD),
            .vss    (VSS),
            `endif
            .pad    (analog_PAD[i]), // Analog (direct pad connection with primary ESD protection) --> SPECIAL net in OpenROAD and will be ignored during detailed routing. --> analog_PADBARE
            .padres (analog_PADRES[i]),
            .padbare(analog_PADBARE[i])
        );
    end
    endgenerate
	// ======================================================
	
    // ======================================================
    // CORE DESIGN
	// ======================================================
	chip_core #(
        .NUM_INPUT_PADS  (NUM_INPUT_PADS),
        .NUM_OUTPUT_PADS (NUM_OUTPUT_PADS),
        .NUM_BIDIR_PADS  (NUM_BIDIR_PADS),
        .NUM_ANALOG_PADS (NUM_ANALOG_PADS)
    ) i_chip_core (
		`ifdef USE_POWER_PINS
        .VDD   		    (VDD),
        .VSS            (VSS),
        `endif
		
        .clk            (clk_PAD2CORE),
        .rst_n          (rst_n_PAD2CORE),
		
        .input_in       (input_PAD2CORE),
		
        .output_out     (output_CORE2PAD),
        .bidir_in       (bidir_PAD2CORE),
        .bidir_out      (bidir_CORE2PAD),
        .bidir_oe       (bidir_CORE2PAD_OE),
		
        .analog_padres  (analog_PADRES),
        .analog_padbare (analog_PADBARE)
    );
	// ======================================================
	
	// ======================================================
    // LOGOS
	// ======================================================
    // JKU logo
    (* keep *)
    sg13g2_ip__jku jku_logo ();
	// ======================================================

    // JKU names
    (* keep *)
    sg13g2_ip__jku_names jku_names ();
	// ======================================================
	
    // JMU CE logo
	(* keep *)
    sg13g2_ip__ce ce_logo ();
	// ======================================================
    
    // JMU CE names
	(* keep *)
    sg13g2_ip__ce_names ce_names ();
	// ======================================================
endmodule

`default_nettype wire
