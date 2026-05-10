# Chip Floorplan

This document describes the physical floorplan of the AMS template chip and
is the human-readable companion to the macro `instances:` blocks in
[flow/librelane/config.yaml](../flow/librelane/config.yaml).

Related documents:
- Pinout: [pinout.md](pinout.md)
- Chip specifications: [specifications.md](specifications.md)


## Die / core geometry

| Parameter                | Value                                                |
| ------------------------ | ---------------------------------------------------- |
| `DIE_AREA`               | `[0, 0, 2000, 2000]` µm  (2 mm × 2 mm)               |
| `CORE_AREA`              | `[365, 365, 1635, 1635]` µm  (1270 µm × 1270 µm)     |
| Padframe margin per side | 365 µm (between die edge and core)                   |
| `FP_SIZING`              | `absolute`                                           |
| Clock period             | 20 ns (≈ 50 MHz)                                     |
| Core supply              | 1.5 V (`VDD` / `VSS`)                                |
| I/O supply               | 3.3 V (`IOVDD` / `IOVSS`)                            |

The 365 µm padframe margin holds the bondpads, IHP IO cells, corner cells,
fillers and the chip-level power ring (TopMetal1 horizontal + TopMetal2
vertical, 15 µm wide, 5 µm spacing — see `flow/librelane/config.yaml` and
[flow/librelane/pdn_cfg.tcl](../flow/librelane/pdn_cfg.tcl)).


## Hard macros

Five hard macros are placed inside the core:

| Macro instance              | Cell                                  | Size (W × H)     | Lower-left (x, y) | Upper-right (x, y) | Orientation |
| --------------------------- | ------------------------------------- | ---------------- | ----------------- | ------------------ | ----------- |
| `i_chip_core.sram_0`        | `RM_IHPSG13_1P_1024x32_c2_bm_bist`    | ≈ 471 × 691 µm   | (435, 435)        | ≈ (906, 1126)      | N           |
| `i_chip_core.counter1`      | `counter_top`                         | 200 × 100 µm     | (435, 1300)       | (635, 1400)        | N           |
| `i_chip_core.counter2`      | `counter_top`                         | 200 × 100 µm     | (435, 1150)       | (635, 1250)        | N           |
| `i_chip_core.inverter1`     | `inverter_top`                        | 54.18 × 81.92 µm | (1440, 1260)      | (1494.18, 1341.92) | N           |
| `i_chip_core.inverter2`     | `inverter_top`                        | 54.18 × 81.92 µm | (1440, 630)       | (1494.18, 711.92)  | N           |

The values are kept in the `instances:` blocks of
`flow/librelane/config.yaml`. The `inverter_top` coordinates are tied to the
Metal3 routing grid (`X` is a multiple of 0.48 µm, `Y` a multiple of 0.42 µm).

> [!NOTE]
> All five macro rectangles are **disjoint**. LibreLane's floorplan, padring,
> manual macro placement and PDN-generation steps do **not** enforce
> non-overlap; the first step that complains is global placement (RePlAce),
> which silently diverges if the floorplan is geometrically impossible. After
> editing any `location:` value, re-check the table above for overlaps.


## Macro placement (top view)

The macros divide the core into three columns: the south-west column holds
the SRAM, the west column (above the SRAM) holds the two counters stacked
vertically, and the east column holds the two inverters stacked vertically.

```text
y=1635 ┌─────────────────────────────────────────────────┐ NE
        │                                                 │
        │                                                 │
        │ ┌─counter1──────┐                               │
   1400 │ │ 200 x 100 µm  │                ┌─inverter1─┐  │
        │ │ (435,1300)─►  │                │ 54 x 82   │  │
        │ │   (635,1400)  │                │(1440,1260)│  │
   1300 │ └───────────────┘                │   (1494,  │  │
        │                                  │     1342) │  │
        │ ┌─counter2──────┐                └───────────┘  │
   1250 │ │ 200 x 100 µm  │                               │
        │ │ (435,1150)─►  │                               │
        │ │   (635,1250)  │                               │
   1150 │ └───────────────┘                               │
        │                                                 │
   1126 │ ┌─sram_0─────────────────────┐                  │
        │ │ ≈ 471 x 691 µm             │                  │
        │ │ (435,435) ─► ≈ (906,1126)  │                  │
        │ │                            │  ┌─inverter2─┐   │
        │ │                            │  │ 54 x 82   │   │
    712 │ │                            │  │(1440,630) │   │
        │ │                            │  │   (1494,  │   │
        │ │                            │  │      712) │   │
    630 │ │                            │  └───────────┘   │
        │ │                            │                  │
    435 │ └────────────────────────────┘                  │
        │                                                 │
y= 365  └─────────────────────────────────────────────────┘ SE
        x=365            906          1440        1635
```

Pad order on each side (see [pinout.md](pinout.md) for the full per-pad
breakdown):

| Side  | Pad order (along the side, away from origin)                                          |
| ----- | ------------------------------------------------------------------------------------- |
| West  | SRAM_out, VSS, VDD, IOVSS, IOVDD, enable, rst_n, clk      (bottom → top)              |
| North | counter1[3:0] (4 outputs), counter1[7:4] / inv1.vin (4 bidir)      (left → right)     |
| South | counter2[7:0] (8 outputs)                                          (left → right)     |
| East  | inverter2 ch1/ch2 analog (4 pads), inverter1.vout1..vout4 (4 outputs) (bottom → top)  |


## Power-distribution network (PDN)

The PDN is generated by [flow/librelane/pdn_cfg.tcl](../flow/librelane/pdn_cfg.tcl)
on top of the chip-level grid that LibreLane builds from the `PDN_*` keys
in `config.yaml`.

| Domain / macro       | Stripes                                                       | Connect          |
| -------------------- | ------------------------------------------------------------- | ---------------- |
| Chip core            | TopMetal1 horizontal + TopMetal2 vertical                     | TM2 ↔ TM1        |
| Core ring            | TM1 + TM2, 15 µm wide, 5 µm spacing, `-connect_to_pads`       | core ring ↔ pads |
| `sram_0` (custom)    | Metal5 stripes, 2.81 µm wide, 11.24 µm pitch                  | M4 ↔ M5 ↔ TM1    |
| `inverter1/2` (custom) | none added — relies on chip-level stripes                   | TM2 ↔ TM1, TM2 ↔ M5 |
| Default macro grid   | TM2 ↔ TM1 (used by counter1 / counter2)                       | TM2 ↔ TM1        |

The SRAM has a secondary `VDDARRAY!` supply pin in its LEF in addition to
`VDD!`/`VSS!`. The two `PDN_MACRO_CONNECTIONS` lines in `config.yaml` bind
both pin sets to the chip-level `VDD` / `VSS` nets.


## Logos

Two decorative IPs sit in the bottom-left and top-left corners of the die
(outside the core, between the core ring and the bondpad ring):

| Instance     | Cell                  | Location (lower-left)                                                  |
| ------------ | --------------------- | ---------------------------------------------------------------------- |
| `jku_logo`   | `sg13g2_ip__jku`      | `($DIE_AREA[0] + 36.4 + 20.4, $DIE_AREA[3] - 36.4 - 120.4)` = (56.8, 1843.2) |
| `jku_names`  | `sg13g2_ip__jku_names`| `($DIE_AREA[2] - 36.4 - 120.4, $DIE_AREA[3] - 36.4 - 120.4)`                |

Both logos are listed in `IGNORE_DISCONNECTED_MODULES` so LibreLane does not
flag them as floating logic.


## Constraints when editing the floorplan

For every macro `M` placed at `(X, Y)` with size `W × H`:

1. **Inside the core:** `X ≥ 365`, `Y ≥ 365`, `X + W ≤ 1635`, `Y + H ≤ 1635`.
2. **No overlap** with any other macro rectangle (RePlAce will diverge with
   `[GPL-0305]` otherwise).
3. **Aligned to the row grid:** the `inverter_top` macro additionally
   requires `X` and `Y` to be multiples of the Metal3 pitches (0.48 µm,
   0.42 µm).
4. **Clear of the IO ring:** routing inside the bondpad area is reserved
   for the padframe.
