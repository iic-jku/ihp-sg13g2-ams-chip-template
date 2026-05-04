module iqmod_top (
`ifdef USE_POWER_PINS
    inout VDD,
    inout VSS,
`endif
    input di_analog_en,
    input di_spdt_ctrl_I,
    inout vinp_I,
    input di_ds_I_p,
    inout vinn_I,
    input di_ds_I_n,
    input di_lo_I,
    input di_lo_Ix,
    input di_lo_Qx,
    input di_lo_Q,
    input di_ds_Q_n,
    inout vinn_Q,
    input di_ds_Q_p,
    inout vinp_Q,
    input di_spdt_ctrl_Q,
    inout voutp_I_RF,
    inout voutn_I_RF,
    inout voutn_Q_RF,
    inout voutp_Q_RF
);
endmodule
