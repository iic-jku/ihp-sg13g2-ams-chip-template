module inverter_top (
`ifdef USE_POWER_PINS
    inout VDD,
    inout VSS,
`endif
    inout vin1,
    inout vin2,
    inout vin3,
    inout vin4,
    inout vout1,
    inout vout2,
    inout vout3,
    inout vout4
);
endmodule
