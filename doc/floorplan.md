# Chip Floorplan

This document describes the physical floorplan of this chip and is the human-readable companion to the macro `instances` blocks in [config.yaml](../flow/librelane/config.yaml).

Related documents:
- Pinout: [pinout.md](pinout.md)
- Specifications: [specifications.md](specifications.md)


## Die / core geometry

| Parameter                | Value                                                |
| ------------------------ | ---------------------------------------------------- |
| `DIE_AREA`               | `[0, 0, 1600, 1600]` µm  (1.6 mm × 1.6 mm)           |
| `CORE_AREA`              | `[365, 365, 1235, 1235]` µm  (870 µm × 870 µm)       |
| Padframe margin per side | 365 µm (between die edge and core)                   |
| `FP_SIZING`              | `absolute`                                           |
| Clock period             | 20 ns (50 MHz)                                       |
| Core supply              | 1.5 V (`VDD` / `VSS`)                                |
| I/O supply               | 3.3 V (`IOVDD` / `IOVSS`)                            |

The 365 µm padframe margin holds the [bondpads](../ip/sg13g2_ip__bondpad_70x70/), [JKU](../ip/sg13g2_ip__jku/), [names](../ip/sg13g2_ip__jku_names/) and [template name](../ip/sg13g2_ip__template_name/) logos, IHP IO cells, corner cells, fillers and the top-level power ring (TopMetal1 vertical + TopMetal2 horizontal, 15 µm wide, 5 µm spacing, see [config.yaml](../flow/librelane/config.yaml) and [pdn_cfg.tcl](../flow/librelane/pdn_cfg.tcl)).


## Hard macros

Five hard macros are placed inside the core:

| Macro instance              | Cell                                  | Size (W × H)       | Lower-left (x, y) | Upper-right (x, y) | Orientation |
| --------------------------- | ------------------------------------- | ------------------ | ----------------- | ------------------ | ----------- |
| `i_chip_core.sram_0`        | `RM_IHPSG13_1P_1024x32_c2_bm_bist`    | 416.64 × 336.46 µm | (435, 493)        | (851.64, 829.46)   | N           |
| `i_chip_core.counter1`      | `counter_top`                         | 200 × 100 µm       | (700, 997)        | (900, 1097)        | N           |
| `i_chip_core.counter2`      | `counter_top`                         | 200 × 100 µm       | (935, 498)        | (1135, 598)        | FS          |
| `i_chip_core.inverter1`     | `inverter_top`                        | 54.18 × 81.92 µm   | (1080.00, 853.86) | (1134.18, 935.78)  | N           |
| `i_chip_core.inverter2`     | `inverter_top`                        | 54.18 × 81.92 µm   | (1080.00, 658.14) | (1134.18, 740.06)  | N           |

The values are kept in the `instances` blocks of [config.yaml](../flow/librelane/config.yaml). The `inverter_top` coordinates are tied to the `Metal3` routing grid (`X` is a multiple of 0.48 µm, `Y` a multiple of 0.42 µm). See [Librelane Cheatsheet](librelane/librelane_cheatsheet.md) for more details on the orientation and configurations.


## Macro placement (top view)

With the current `CORE_AREA` `[365,365,1235,1235]`, the SRAM and `counter2` sit in the lower half of the core, `counter1` is x-centered on the die in the upper half, and both inverter instances sit on the right. [prep-ic/chip_top.json](prep-ic/chip_top.json) holds the same floorplan as a PREP-IC project.

```text
y=1235 ┌───────────────────────────────────────────────┐
       │                                               │
       │                 ┌─counter1─┐                  │
 1097  │                 │(700,997) │                  │
       │                 └──────────┘                  │
       │                                               │
  936  │                                   ┌inv1────┐  │
       │                                   │(1080,  │  │
       │                                   │ 853.86)│  │
  740  │                                   └inv2────┘  │
       │                                   ┌────────┐  │
       │                                   │(1080,  │  │
  658  │                                   │ 658.14)│  │
       │ ┌─sram_0───────────────────────┐  └────────┘  │
       │ │ (435,493) → (851.64, 829.46) │              │
  598  │ │                              │ ┌counter2──┐ │
       │ │                              │ │(935,498) │ │
  493  │ └──────────────────────────────┘ └──────────┘ │
       │                                               │
y= 365 └───────────────────────────────────────────────┘
       x=365         906       935          1080      1235
```

Pad order (away from origin) on each side (see [pinout.md](pinout.md) for the full per-pad breakdown):

| Side  | Pad order                                                                             |
| ----- | ------------------------------------------------------------------------------------- |
| West  | SRAM_out, VSS, VDD, IOVSS, IOVDD, enable, rst_n, clk                  (bottom → top)  |
| North | counter1[3:0] (4 outputs), counter1[7:4] / inv1.vin (4 bidir)         (left → right)  |
| South | counter2[7:0] (8 outputs)                                             (left → right)  |
| East  | inverter2 ch1/ch2 analog (4 pads), inverter1.vout1..vout4 (4 outputs) (bottom → top)  |


## Power-distribution network (PDN)

The PDN is generated by [pdn_cfg.tcl](../flow/librelane/pdn_cfg.tcl) on top of the chip top-level grid that LibreLane builds from the `PDN_*` keys in [config.yaml](../flow/librelane/config.yaml).

| Domain / macro         | Stripes                                                       | Connect            |
| ---------------------- | ------------------------------------------------------------- | ------------------ |
| Chip core              | TopMetal1 vertical + TopMetal2 horizontal                     | TM2 ↔ TM1          |
| Core ring              | TM1 + TM2, 15 µm wide, 5 µm spacing, `-connect_to_pads`       | core ring ↔ pads   |
| `sram_0` (custom)      | Metal5 stripes, 2.81 µm wide, 11.24 µm pitch                  | M4 ↔ M5 ↔ TM1      |
| `inverter1/2` (custom) | none added, relies on chip top-level stripes                 | TM2 ↔ TM1, TM2 ↔ M5|
| Default macro grid     | TM2 ↔ TM1 (used by counter1 / counter2)                       | TM2 ↔ TM1          |

The SRAM has a secondary `VDDARRAY!` supply pin in its LEF in addition to `VDD!`/`VSS!`. The two `PDN_MACRO_CONNECTIONS` lines in [config.yaml](../flow/librelane/config.yaml) bind both pin sets to the chip top-level `VDD` / `VSS` nets.


## Logos

Three decorative IPs sit in the corners of the die (outside the core, between the core ring and the seal ring), the JKU logo and the names in the upper corners and the template name in the lower left one:

| Instance        | Cell                       | Location                                                                        |
| --------------- | -------------------------- | ------------------------------------------------------------------------------- |
| `jku_logo`      | `sg13g2_ip__jku`           | `($DIE_AREA[0] + 36.4 + 20.4, $DIE_AREA[3] - 36.4 - 120.4)` = (56.8, 1443.2)    |
| `jku_names`     | `sg13g2_ip__jku_names`     | `($DIE_AREA[2] - 36.4 - 120.4, $DIE_AREA[3] - 36.4 - 120.4)` = (1443.2, 1443.2) |
| `template_name` | `sg13g2_ip__template_name` | `($DIE_AREA[0] + 36.4 + 20.4, $DIE_AREA[1] + 36.4 + 20.4)` = (56.8, 56.8)       |

All three logos are listed as `IGNORE_DISCONNECTED_MODULES` in [config.yaml](../flow/librelane/config.yaml) so LibreLane does not flag them as floating logic.


## Constraints when editing the floorplan

For every macro `M` placed at `(X, Y)` with size `W × H`:

1. **Inside the core:** `X ≥ 365`, `Y ≥ 365`, `X + W ≤ 1235`, `Y + H ≤ 1235`.
2. **No overlap** with any other macro rectangle (RePlAce will diverge with `[GPL-0305]` otherwise).
3. **Aligned to the row grid:** the `inverter_top` macro additionally requires `X` and `Y` to be multiples of the Metal3 pitches (0.48 µm, 0.42 µm).
4. **Clear of the IO ring:** routing inside the bondpad area is reserved for the padframe.
5. **Rows cut at `VSS` rails:** the macro and its 10 µm halo (`FP_MACRO_VERTICAL_HALO`) start on a row with `VSS` at the bottom (`N`, `y = 366.66 + k · 7.56` µm) and cover an even number of 3.78 µm rows. A cut at a `VDD` rail leaves the NWell of the cut row and of the full row beside it with a concave corner 0.24 µm from the well ties of the decap cells, and KLayout reports `NW.d` on each tie. For the counters and the SRAM the legal `Y` window is about 1 µm wide, so check the first and the last cut row in the DEF after a move.
