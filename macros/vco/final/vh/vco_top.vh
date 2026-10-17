module vco_top (
`ifdef USE_POWER_PINS
    inout VDD,
    inout VSS,
`endif
    input di_en,
    inout ibias_100u,
    inout rf_out_n,
    inout rf_out_p,
    inout vtune
);
endmodule
