// SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
// Description: Top-level chip wrapper.
// Instantiates the padframe, the chip core and custom logos.
// The padframe with bondpads, I/O cells, power ring, corners and fillers is handled by LibreLane.
// The specifications can be found in doc/specifications.md.
// The pinout mapping can be found in doc/pinout.md.
// The floorplan can be found in doc/floorplan.md.

`default_nettype none

module chip_top #(
    // Power / ground pads for digital core / analog front-end
    parameter int unsigned NUM_VDD_PADS    = 1,
    parameter int unsigned NUM_VSS_PADS    = 1,

    // Power / ground pads for I/O
    parameter int unsigned NUM_IOVDD_PADS  = 1,
    parameter int unsigned NUM_IOVSS_PADS  = 1,

    // Signal pads
    parameter int unsigned NUM_INPUT_PADS  = 1,  // excluding clock and reset pads
    parameter int unsigned NUM_OUTPUT_PADS = 17,
    parameter int unsigned NUM_BIDIR_PADS  = 4,
    parameter int unsigned NUM_ANALOG_PADS = 4
) (
    `ifdef USE_POWER_PINS
    inout wire IOVDD,
    inout wire IOVSS,
    inout wire VDD,
    inout wire VSS,
    `endif
    inout wire                       clk_PAD,
    inout wire                       rst_n_PAD,
    inout wire [NUM_INPUT_PADS-1 :0] input_PAD,
    inout wire [NUM_OUTPUT_PADS-1:0] output_PAD,
    inout wire [NUM_BIDIR_PADS-1 :0] bidir_PAD,
    inout wire [NUM_ANALOG_PADS-1:0] analog_PAD
);

    // ======================================================
    // Internal nets
    // ======================================================
    // Clock
    logic                       clk_PAD2CORE;

    // Reset
    logic                       rst_n_PAD2CORE;

    // Inputs
    logic [NUM_INPUT_PADS-1 :0] input_PAD2CORE;

    // Outputs
    logic [NUM_OUTPUT_PADS-1:0] output_CORE2PAD;

    // Bidirectionals
    logic [NUM_BIDIR_PADS-1 :0] bidir_PAD2CORE;
    logic [NUM_BIDIR_PADS-1 :0] bidir_CORE2PAD;
    logic [NUM_BIDIR_PADS-1 :0] bidir_CORE2PAD_OE;

    // Analog (must remain wire: connected to inout pad/macro ports)
    wire  [NUM_ANALOG_PADS-1:0] analog_PADRES;
    wire  [NUM_ANALOG_PADS-1:0] analog_PADBARE;
    // ======================================================

    // ======================================================
    // VDD - PAD INSTANCES
    // ======================================================
    generate
        for (genvar i = 0; i < NUM_VDD_PADS; i++) begin : g_vdd_pads
            (* keep *)
            sg13g2_IOPadVdd vdd_pad (
                `ifdef USE_POWER_PINS
                .iovdd (IOVDD),
                .iovss (IOVSS),
                .vdd   (VDD),
                .vss   (VSS)
                `endif
            );
        end
    endgenerate
    // ======================================================

    // ======================================================
    // VSS - PAD INSTANCES
    // ======================================================
    generate
        for (genvar i = 0; i < NUM_VSS_PADS; i++) begin : g_vss_pads
            (* keep *)
            sg13g2_IOPadVss vss_pad (
                `ifdef USE_POWER_PINS
                .iovdd (IOVDD),
                .iovss (IOVSS),
                .vdd   (VDD),
                .vss   (VSS)
                `endif
            );
        end
    endgenerate
    // ======================================================

    // ======================================================
    // IOVDD - PAD INSTANCES
    // ======================================================
    generate
        for (genvar i = 0; i < NUM_IOVDD_PADS; i++) begin : g_iovdd_pads
            (* keep *)
            sg13g2_IOPadIOVdd iovdd_pad (
                `ifdef USE_POWER_PINS
                .iovdd (IOVDD),
                .iovss (IOVSS),
                .vdd   (VDD),
                .vss   (VSS)
                `endif
            );
        end
    endgenerate
    // ======================================================

    // ======================================================
    // IOVSS - PAD INSTANCES
    // ======================================================
    generate
        for (genvar i = 0; i < NUM_IOVSS_PADS; i++) begin : g_iovss_pads
            (* keep *)
            sg13g2_IOPadIOVss iovss_pad (
                `ifdef USE_POWER_PINS
                .iovdd (IOVDD),
                .iovss (IOVSS),
                .vdd   (VDD),
                .vss   (VSS)
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
        .iovdd (IOVDD),
        .iovss (IOVSS),
        .vdd   (VDD),
        .vss   (VSS),
        `endif
        .p2c   (clk_PAD2CORE),
        .pad   (clk_PAD)
    );
    // ======================================================

    // ======================================================
    // RESET - PAD INSTANCE (active low)
    // ======================================================
    sg13g2_IOPadIn rst_n_pad (
        `ifdef USE_POWER_PINS
        .iovdd (IOVDD),
        .iovss (IOVSS),
        .vdd   (VDD),
        .vss   (VSS),
        `endif
        .p2c   (rst_n_PAD2CORE),
        .pad   (rst_n_PAD)
    );
    // ======================================================

    // ======================================================
    // SIGNAL INPUTS - PAD INSTANCES
    // ======================================================
    generate
        for (genvar i = 0; i < NUM_INPUT_PADS; i++) begin : g_inputs
            sg13g2_IOPadIn input_pad (
                `ifdef USE_POWER_PINS
                .iovdd (IOVDD),
                .iovss (IOVSS),
                .vdd   (VDD),
                .vss   (VSS),
                `endif
                .p2c   (input_PAD2CORE[i]),
                .pad   (input_PAD[i])
            );
        end
    endgenerate
    // ======================================================

    // ======================================================
    // SIGNAL OUTPUTS - PAD INSTANCES
    // ======================================================
    generate
        for (genvar i = 0; i < NUM_OUTPUT_PADS; i++) begin : g_outputs
            sg13g2_IOPadOut30mA output_pad (
                `ifdef USE_POWER_PINS
                .iovdd (IOVDD),
                .iovss (IOVSS),
                .vdd   (VDD),
                .vss   (VSS),
                `endif
                .c2p   (output_CORE2PAD[i]),
                .pad   (output_PAD[i])
            );
        end
    endgenerate
    // ======================================================

    // ======================================================
    // SIGNAL BIDIRECTIONALS - PAD INSTANCES
    // ======================================================
    generate
        for (genvar i = 0; i < NUM_BIDIR_PADS; i++) begin : g_bidirs
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
        for (genvar i = 0; i < NUM_ANALOG_PADS; i++) begin : g_analogs
            (* keep *)
            sg13g2_IOPadAnalog analog_pad (
                `ifdef USE_POWER_PINS
                .iovdd   (IOVDD),
                .iovss   (IOVSS),
                .vdd     (VDD),
                .vss     (VSS),
                `endif
                // Analog (direct pad connection with primary ESD protection).
                // SPECIAL net in OpenROAD; ignored during detailed routing -> analog_PADBARE.
                .pad     (analog_PAD[i]),
                .padres  (analog_PADRES[i]),
                .padbare (analog_PADBARE[i])
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
        .VDD            (VDD),
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

    // JKU names
    (* keep *)
    sg13g2_ip__jku_names jku_names ();
    // ======================================================

endmodule

`default_nettype wire
