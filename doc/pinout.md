# Pinout

This file provides an overview of the project pinout.

## Pin Table

| Pin | Type   | Direction | Domain | Description | Notes |
| --- | ------ | --------- | ------ | ----------- | ----- |
| VDD | power  | in        | 1.5    | main supply |       |
| VSS | ground | in        | gnd    | ground      |       |
| IN  | signal | in        | analog | input       |       |
| OUT | signal | out       | digital | output     |       |

ToDo

## Notes

- 7 x VDD = 1.5V
- 9 x VSS
- 3 x IOVDD = 3.3V
- 3 x IOVSS
- 1 x clk
- 1 x reset_n
- 6 x Input Pads
    - 4 x GPIO inputs
    - so
    - rx
- 9 x Output Pads
    - 4 x GPIO outputs
    - si
    - sclk
    - sram_ce
    - scl
    - tx
- 9 x Bidirectional Pads
    - sda_i / sda_o
    - lo_I_i / lo_I_o
    - lo_Ix_i / lo_Ix_o
    - lo_Q_i / lo_Q_o
    - lo_Qx_i / lo_Qx_o
    - Q_p_i / Q_p_o
    - Q_n_i / Q_n_o
    - I_p_i / I_p_o
    - I_n_i / I_n_o
- 8 x Analog Pads
    - Vinp_I
    - Vinn_I
    - Voutp_I_RF
    - Voutn_I_RF
    - Voutn_Q_RF
    - Voutp_Q_RF
    - Vinn_Q
    - Vinp_Q
- Total: 56 pins
- Note: 8 x VSS will be connected to package GND --> QFN-48 package