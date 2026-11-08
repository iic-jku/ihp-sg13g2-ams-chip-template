# sg13g2_ip__rfpad_70x70

An 80 µm × 250 µm RF pad cell for the IHP SG13G2 130 nm CMOS process, generated with the KLayout PCell engine. It takes the slot of `sg13g2_IOPadAnalog` plus its bondpad at one place of the pad ring, for a signal that needs less than half the load of that cell (204 fF against about 475 fF) and a defined return path under the pad. The chip does not use it by default.

## Directory Structure

<details>
<summary>Show Directory Structure</summary>

```text
📁 sg13g2_ip__rfpad_70x70/
├─ Makefile                             # Build automation
├─ 📁 script/
│  └─ rfpad.py                          # KLayout generator of the RF pad
├─ 📁 schematic/
│  └─ 📁 xschem/                        # Schematic and symbol, the LVS reference
├─ 📁 netlist/
│  ├─ 📁 schematic/                     # CDL netlist from Xschem
│  └─ 📁 layout/                        # Netlist extracted by KLayout LVS
├─ 📁 final/
│  ├─ 📁 gds/
│  │  └─ sg13g2_ip__rfpad_70x70.gds     # Generated GDSII layout
│  ├─ 📁 lef/
│  │  └─ sg13g2_ip__rfpad_70x70.lef     # LEF macro for place-and-route
│  ├─ 📁 lib/
│  │  └─ sg13g2_ip__rfpad_70x70.lib     # Liberty view
│  └─ 📁 vh/
│     └─ sg13g2_ip__rfpad_70x70.vh      # Verilog blackbox stub
└─ 📁 verification/
   ├─ 📁 drc/                           # DRC reports
   └─ 📁 lvs/                           # LVS report
```

</details>


## Usage

The default Make target is `help`, so running `make` prints usage and all available targets with short descriptions.

```bash
make
make help
```

Build everything (clean, generate the cell, generate Verilog, run DRC and LVS):

```bash
make all
```

### PDK Guard

Every target except `help` and `clean` needs the `ihp-sg13g2` PDK. A wrong `$PDK`, for example `ihp-sg13cmos5l` from the sibling CMOS5L template, breaks this IP in both directions: the `rfpad` target reads the KLayout technology from `$PDK_ROOT/$PDK` and asks for `sg13g2` by name, which another PDK does not provide, and `sak-drc.sh` runs the DRC against the rule deck of whatever `$PDK` says. The Makefile therefore compares `$PDK` against `REQUIRED_PDK` once when it is parsed, before any target runs. Switch the PDK with `sak-pdk ihp-sg13g2`, pass `REQUIRED_PDK=` to skip the check, or `REQUIRED_PDK=<pdk>` to require a different PDK.


### Individual Targets

| Target        | Description                                                                                                          |
| ------------- | -------------------------------------------------------------------------------------------------------------------- |
| `rfpad`       | Generate GDS, LEF and Liberty via `rfpad.py`, which stops on a broken geometry or connectivity |
| `verilog`     | Generate the Verilog blackbox stub |
| `klayout-drc` | Run KLayout DRC using `sak-drc.sh`, passes only with exactly the waived `Pad.fR_M1` markers (usage: `make klayout-drc [CELL=<cellname>] [DRC_LEVEL=<precheck\|macro\|regular>] [DRC_JOBS=<n>]`) |
| `magic-drc`   | Run Magic DRC using `sak-drc.sh` (usage: `make magic-drc [CELL=<cellname>]`), not part of `make all` |
| `gdscheck-drc` | Run gdscheck DRC using `sak-drc.sh` (usage: `make gdscheck-drc [CELL=<cellname>] [DRC_LEVEL=<precheck\|macro\|regular>] [GDSCHECK_SUITE=<suite>\|GDSCHECK_DECKS=<decks>] [DRC_JOBS=<n>]`) |
| `klayout-lvs-netlist` | Export the CDL netlist from Xschem |
| `klayout-lvs` | Run KLayout LVS against the schematic |
| `open`        | Browse this folder with `sak-open.py` and open each file in its tool |
| `clean`       | Remove all generated output directories |


## The Cell

`make rfpad` runs `script/rfpad.py` in KLayout batch mode. The cell is fixed, it has no parameters.

| y (µm, 0 is the die edge) | Content |
| --- | --- |
| 0 to 70 | The `bondpad` PCell: octagon, 70 µm, `bottomMetal` `3`, with its Passiv opening redrawn 2.7 µm inside `dfpad` so that no TopVia2 sits under it (`Pad.kR`), over a solid Metal1 shield on `vss` with a 3 µm collar |
| 70 to 250 | The rail bands of `sg13g2_IOPadAnalog` shifted by 70 µm, read from the LEF in `ip/sg13g2_io_custom`, the ESD pair, the supply clamp and the RF line |

**Ports.** `vss`, `vdd`, `iovss`, `iovdd`, `pad` and `padbare`. `pad` is the plate and `padbare` the inner end of the same TopMetal2 conductor, with no series resistor between them. There is no `padres`. `padbare` is 2.0 µm wide on TopMetal2 at y 240 to 250. It is a LEF and Verilog alias, the schematic has no such node.

**RF line.** The plate leaves through a teardrop, 14.92 µm wide for the 7 µm that `Pad.fR` asks for, then a 45° taper onto 4.92 µm up to the ESD tap at y 210, then 2.0 µm. It runs through a corridor cut in the TopMetal2 and TopMetal1 rails, 5 µm from the rails on either side. The last `iovss` band keeps its 5 µm from the wider ESD bar instead. `iovss` and `iovdd` cross the line on Metal3, Metal4 and Metal5 and on the Metal2 strips under them.

**ESD.** `diodevss_2kv` and `diodevdd_2kv` connect the pad to the core rails `vss` and `vdd`, not to `iovss` and `iovdd`. An RC-triggered clamp between `vdd` and `vss` takes the strike from there, because IHP's pad ring clamps `vdd` only to `iovss`. It is the circuit of `sg13g2_IOPadVdd` with its source on `vss` and a 1512 µm / 0.6 µm `sg13_hv_nmos`. What the pad survives also depends on the circuit behind it and the chip's rails, so simulate HBM on the chip.

**A pad above `vdd`.** The pad clamps at `vdd` plus one diode. With `vdd` at 1.2 V, `diodevdd_2kv` and `diodevss_2kv` together draw this DC current (ngspice, `dio_tt`):

| Pad voltage | 27 °C | 125 °C |
| --- | --- | --- |
| 1.35 V | 3.1 pA | 0.6 nA |
| 1.55 V | 0.14 nA | 31 nA |
| 1.75 V | 18 nA | 6.6 µA |

A circuit on its own, higher supply can therefore drive this pad, but `vdd` has to come up no later than that supply, or the diode conducts into the unpowered rail.

**Capacitance on the pad node.** 204 fF at 0.6 V and 27 °C, and the Liberty view carries that value with no timing arc. Its junctions grow to 57 fF at a pad voltage of 1.35 V with `vdd` at 1.2 V, and to 63 fF at 125 °C.

| Part | fF | Source |
| --- | --- | --- |
| All metal on the node | 152.1 | Magic, `sak-pex.sh -m 2` |
| `diodevss_2kv` at 0.6 V | 27.2 | PDK model card |
| `diodevdd_2kv` at 0.6 V to `vdd` | 24.6 | PDK model card |

The schematic carries the metal as four `Cm_*` capacitors, one per chip net, with `lvs_ignore=open`, so a simulation charges them and LVS never sees them. None of this is an EM solve, and at 20 GHz the 180 µm line is no longer a lumped capacitor.

**Checks.** DRC and LVS both miss a pad shorted to a rail, because the rails carry no device and two touching shapes are one polygon. So `rfpad.py` checks the cell before it writes any view, and stops if one of these fails:

- The cell outline, the pad stack areas, the `Pad.gR` enclosure of every TopVia2 in the pad and that none sits under the Passiv opening, and that the pad pin is one centred rectangle.
- The 3 µm shield collar, the widths of the RF line, and that the TopMetal2 rails keep exactly 5 µm from it with TopMetal1 cut in the same place.
- That no pad net metal reaches a cell edge, that each of `vss`, `vdd`, `iovss` and `iovdd` is its own net, and that every `iovss` and `iovdd` band is one conductor from Metal3 to TopMetal2.
- That the shield reaches `vss`, that each ESD terminal is on its rail, and that the clamp's stripes, rings, gate buses and RC node are on their nets.


## Design Rule Check (DRC) and LVS

All flows use `sak-drc.sh` and `sak-lvs.sh` and write their reports into per-cell run folders under `verification/drc/` and `verification/lvs/`. Results on image `ghcr.io/iic-jku/iic-osic-tools:nightly` (`8ea7cab3bd18`), PDK `ac438346`:

| Check | Result |
| --- | --- |
| `make klayout-lvs` | match |
| `make gdscheck-drc` (`core`) | clean, the `recommended` suite reports the 3 `Pad.fR` of the same collar |
| `make klayout-drc` (`macro`) | exactly 7 `Pad.fR_M1`, waived |
| `make klayout-drc DRC_LEVEL=regular` | fails: the 7 `Pad.fR_M1` plus `AFil.g`, `GFil.g`, `M3.k`, `M4.k` and `M5.k`, global density rules of the chip |
| `make magic-drc` | 418 markers on the TopVia1 and TopVia2 rings of the `bondpad` PCell, which the bare PCell reports too, and 2 `Slt.c` on the Metal1 shield, because Magic does not exempt the plate under `dfpad` as KLayout does. It is not part of `make all` |

`Pad.fR_M1` asks for 7 µm of Metal1 past `dfpad`. The Metal1 crossing `dfpad` is the shield's 3 µm collar, a ground plane that exits nowhere, and the 80 µm cell leaves 5 µm a side. Without the collar the rim field of the pad lands on the substrate, so the markers are waived by their exact count: one more or one less fails `make klayout-drc`.


## Using the RF Pad on a Chip

A chip instantiates it like `sg13g2_IOPadAnalog`, with `.pad` and `.padbare` and without `.padres`, and needs these entries in `flow/librelane/config.yaml`:

| Variable | Entry |
| --- | --- |
| `PAD_LEFS` | `final/lef/sg13g2_ip__rfpad_70x70.lef`, next to the IO library's LEF |
| `PAD_VERILOG_MODELS` | `final/vh/sg13g2_ip__rfpad_70x70.vh`, next to the IO library's Verilog |
| `EXTRA_GDS` | `final/gds/sg13g2_ip__rfpad_70x70.gds` |
| `LIB` | `final/lib/sg13g2_ip__rfpad_70x70.lib`, in every corner. `EXTRA_LIBS` does not work, Yosys then replaces the Verilog blackbox and the power ports are gone |
| `PAD_PLACE_IO_TERMINALS` | `sg13g2_ip__rfpad_70x70/pad`. `place_bondpad` is what creates a pad's top-level terminal, and this cell gets no bondpad |
| `PAD_CFG` | A copy of LibreLane's `scripts/openroad/common/pad_cfg.tcl` that moves every pad whose master matches no `PAD_BONDPAD_OFFSETS` regex outward by the bondpad depth, 70 µm, before `connect_by_abutment`. `place_pad` leaves the instance `FIRM`, so the script sets it to `PLACED` for the move and restores it |

The cell is 70 µm taller than the IO library's pads and its rail bands are drawn 70 µm further in, so its rails abut its neighbours only when its outer edge sits where the bondpads' outer edges are. `OpenROAD.PadRing` places every pad at the row, which leaves this cell 70 µm too far in with an open supply ring and no report. `PAD_BONDPAD_OFFSETS` already skips it, because its name does not match `sg13g2_IOPad*`. The width of 80 µm is that of the IO library's pads, so the pad pitch does not change.
