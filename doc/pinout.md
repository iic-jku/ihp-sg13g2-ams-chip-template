# Chip Pinout

This document lists every bondpad of the chip together with the top-level `chip_top` port it is attached to and the role it plays inside the core. The padframe layout is **8 pads per side, 32 bondpads total**.

Order convention:
- `PAD_WEST` / `PAD_EAST`: **bottom → top**
- `PAD_NORTH` / `PAD_SOUTH`: **left → right**

Same convention as the four `PAD_*` lists in [config.yaml](../flow/librelane/config.yaml).

Related documents:
- Floorplan: [floorplan.md](floorplan.md)
- Specifications: [specifications.md](specifications.md)


## Top-level ports

Defined in [chip_top.sv](../rtl/chip_top.sv):

| Top-level port    | Direction | Width                 | Role                                            |
| ----------------- | --------- | --------------------- | ----------------------------------------------- |
| `IOVDD`           | inout     | 1                     | I/O supply (3.3 V), under `USE_POWER_PINS`      |
| `IOVSS`           | inout     | 1                     | I/O ground, under `USE_POWER_PINS`              |
| `VDD`             | inout     | 1                     | Core supply (1.5 V), under `USE_POWER_PINS`     |
| `VSS`             | inout     | 1                     | Core ground, under `USE_POWER_PINS`             |
| `clk_PAD`         | inout     | 1                     | main clock                                      |
| `rst_n_PAD`       | inout     | 1                     | active-low reset                                |
| `input_PAD[0]`    | inout     | `NUM_INPUT_PADS=1`    | global enable                                   |
| `output_PAD[16:0]`| inout     | `NUM_OUTPUT_PADS=17`  | digital outputs (counters, inverter1, SRAM)     |
| `bidir_PAD[3:0]`  | inout     | `NUM_BIDIR_PADS=4`    | counter1 MSB nibble / inverter1 vin1..vin4      |
| `analog_PAD[3:0]` | inout     | `NUM_ANALOG_PADS=4`   | inverter2 analog channels 1 and 2               |

The `output_PAD` bit-to-role mapping is fixed inside [chip_core.sv](../rtl/chip_core.sv):

| `output_PAD` bit | Source signal                                            |
| ---------------- | ---------------------------------------------------------|
| `[3:0]`          | `counter1_value[3:0]` (counter1 LSB nibble)              |
| `[11:4]`         | `counter2_value[7:0]` (full 8-bit counter2 value)        |
| `[15:12]`        | `inverter1.vout1..vout4` (digital inverter outputs)      |
| `[16]`           | `^sram_0_out` (parity / XOR-reduction of `A_DOUT[31:0]`) |


## Pad-count overview

| Category                | Count | Pads                                                                       |
| ----------------------- | ----- | -------------------------------------------------------------------------- |
| Clock                   | 1     | `clk_PAD`                                                                  |
| Reset (active-low)      | 1     | `rst_n_PAD`                                                                |
| Enable                  | 1     | `input_PAD[0]`                                                             |
| I/O supply              | 1     | `IOVDD`                                                                    |
| I/O ground              | 1     | `IOVSS`                                                                    |
| Core supply             | 1     | `VDD`                                                                      |
| Core ground             | 1     | `VSS`                                                                      |
| Digital outputs         | 17    | 4 × counter1[3:0] + 8 × counter2[7:0] + 4 × inverter1.vout + 1 × SRAM XOR  |
| Digital bidir           | 4     | counter1[7:4] / inverter1.vin1..vin4                                       |
| Analog                  | 4     | inverter2.vin1, vin2 (padres) + inverter2.vout1, vout2 (padbare)           |
| **Total**               | **32**|                                                                            |


## Location overview

| Side  | Pad count | Function                                                                  |
| ----- | --------- | ------------------------------------------------------------------------- |
| West  | 8         | clk, rst_n, enable, IOVDD/IOVSS, VDD/VSS, SRAM output                     |
| North | 8         | `counter1_value[3:0]` outputs + `counter1_value[7:4]` / inv1.vin bidir    |
| South | 8         | `counter2_value[7:0]` outputs                                             |
| East  | 8         | inverter2 analog ch1/ch2 (4 pads), inverter1 dout1..dout4 (4 pads)        |


## West (bottom → top)

| # | Top-level port      | Pad-cell instance         | Type            | Direction | Domain | Role                                            |
| - | ------------------- | ------------------------- | --------------- | --------- | ------ | ----------------------------------------------- |
| 1 | `output_PAD[16]`    | `g_outputs[16].output_pad`  | digital         | out       | 1.5 V  | XOR-reduced SRAM `A_DOUT[31:0]` (`sram_0_out`)  |
| 2 | —                   | `g_vss_pads[0].vss_pad`     | power           | inout     | gnd    | core ground (VSS)                               |
| 3 | —                   | `g_vdd_pads[0].vdd_pad`     | power           | inout     | 1.5 V  | core supply (VDD)                               |
| 4 | —                   | `g_iovss_pads[0].iovss_pad` | power           | inout     | gnd    | I/O ground (IOVSS / IOGND)                      |
| 5 | —                   | `g_iovdd_pads[0].iovdd_pad` | power           | inout     | 3.3 V  | I/O supply (IOVDD)                              |
| 6 | `input_PAD[0]`      | `g_inputs[0].input_pad`     | digital         | in        | 1.5 V  | global `enable` (gates counters and bidir mode) |
| 7 | `rst_n_PAD`         | `rst_n_pad`               | digital         | in        | 1.5 V  | active-low synchronous reset                    |
| 8 | `clk_PAD`           | `clk_pad`                 | digital         | in        | 1.5 V  | main clock (50 MHz)                             |


## North (left → right)

| # | Top-level port    | Pad-cell instance         | Type            | Direction | Role                                                                       |
| - | ----------------- | ------------------------- | --------------- | --------- | -------------------------------------------------------------------------- |
| 1 | `output_PAD[0]`   | `g_outputs[0].output_pad`   | digital         | out       | `counter1_value[0]` (LSB)                                                  |
| 2 | `output_PAD[1]`   | `g_outputs[1].output_pad`   | digital         | out       | `counter1_value[1]`                                                        |
| 3 | `output_PAD[2]`   | `g_outputs[2].output_pad`   | digital         | out       | `counter1_value[2]`                                                        |
| 4 | `output_PAD[3]`   | `g_outputs[3].output_pad`   | digital         | out       | `counter1_value[3]`                                                        |
| 5 | `bidir_PAD[0]`    | `g_bidirs[0].bidir_pad`     | digital         | bidir     | `counter1_value[4]` (out, when `enable=1`) / `inverter1.vin1` (in)         |
| 6 | `bidir_PAD[1]`    | `g_bidirs[1].bidir_pad`     | digital         | bidir     | `counter1_value[5]` (out, when `enable=1`) / `inverter1.vin2` (in)         |
| 7 | `bidir_PAD[2]`    | `g_bidirs[2].bidir_pad`     | digital         | bidir     | `counter1_value[6]` (out, when `enable=1`) / `inverter1.vin3` (in)         |
| 8 | `bidir_PAD[3]`    | `g_bidirs[3].bidir_pad`     | digital         | bidir     | `counter1_value[7]` (MSB) (out, when `enable=1`) / `inverter1.vin4` (in)   |

`bidir_oe[i]` is wired to `input_PAD[0]`, i.e. the bidir pads are **outputs when `enable = 1`** (counter1's MSB nibble visible externally) and **inputs when `enable = 0`** (external stimuli drive inverter1's `vin1..vin4`).


## South (left → right)

| # | Top-level port    | Pad-cell instance         | Type            | Direction | Role                                  |
| - | ----------------- | ------------------------- | --------------- | --------- | ------------------------------------- |
| 1 | `output_PAD[4]`   | `g_outputs[4].output_pad`   | digital         | out       | `counter2_value[0]` (LSB)             |
| 2 | `output_PAD[5]`   | `g_outputs[5].output_pad`   | digital         | out       | `counter2_value[1]`                   |
| 3 | `output_PAD[6]`   | `g_outputs[6].output_pad`   | digital         | out       | `counter2_value[2]`                   |
| 4 | `output_PAD[7]`   | `g_outputs[7].output_pad`   | digital         | out       | `counter2_value[3]`                   |
| 5 | `output_PAD[8]`   | `g_outputs[8].output_pad`   | digital         | out       | `counter2_value[4]`                   |
| 6 | `output_PAD[9]`   | `g_outputs[9].output_pad`   | digital         | out       | `counter2_value[5]`                   |
| 7 | `output_PAD[10]`  | `g_outputs[10].output_pad`  | digital         | out       | `counter2_value[6]`                   |
| 8 | `output_PAD[11]`  | `g_outputs[11].output_pad`  | digital         | out       | `counter2_value[7]` (MSB)             |


## East (bottom → top)

| # | Top-level port    | Pad-cell instance         | Type            | Direction | Role                                                        |
| - | ----------------- | ------------------------- | --------------- | --------- | ----------------------------------------------------------- |
| 1 | `analog_PAD[0]`   | `g_analogs[0].analog_pad`   | analog          | inout     | `inverter2.vin1`  (channel 1 input,  routed via `padres`)   |
| 2 | `analog_PAD[1]`   | `g_analogs[1].analog_pad`   | analog          | inout     | `inverter2.vin2`  (channel 2 input,  routed via `padres`)   |
| 3 | `analog_PAD[2]`   | `g_analogs[2].analog_pad`   | analog          | inout     | `inverter2.vout1` (channel 1 output, routed via `padbare`)  |
| 4 | `analog_PAD[3]`   | `g_analogs[3].analog_pad`   | analog          | inout     | `inverter2.vout2` (channel 2 output, routed via `padbare`)  |
| 5 | `output_PAD[12]`  | `g_outputs[12].output_pad`  | digital         | out       | `inverter1.vout1`                                           |
| 6 | `output_PAD[13]`  | `g_outputs[13].output_pad`  | digital         | out       | `inverter1.vout2`                                           |
| 7 | `output_PAD[14]`  | `g_outputs[14].output_pad`  | digital         | out       | `inverter1.vout3`                                           |
| 8 | `output_PAD[15]`  | `g_outputs[15].output_pad`  | digital         | out       | `inverter1.vout4`                                           |

`inverter2` has four channels in total. Only **channels 1 and 2** are exposed off-chip. Channels 3 and 4 have `vin3`, `vout3`, `vin4`, `vout4` tied to `VSS` inside [chip_core.sv](../rtl/chip_core.sv).

The `sg13g2_IOPadAnalog` cell exposes two internal nodes per pad:

| Net      | Path through pad cell                          | Use case                                                  |
| -------- | ---------------------------------------------- | --------------------------------------------------------- |
| `padres` | Via the pad's **secondary** ESD resistor       | Input signals: the series resistor limits ESD current and protects sensitive gate oxides |
| `padbare` | **Direct** connection to the pad metal (only primary ESD diodes present) | Output signals: bypasses the resistor to minimise parasitic RC and signal distortion |

`inverter2.vin1/vin2` are connected to `analog_PADRES[0:1]` (through the resistor) and `inverter2.vout1/vout2` are driven onto `analog_PADBARE[2:3]` (direct connection). In [chip_core.sv](../rtl/chip_core.sv), these appear as the corresponding core nets `analog_padres[0:1]` and `analog_padbare[2:3]`.
