# An Open-Source Analog Mixed-Signal Chip Design Template & Tutorial for the ihp-sg13g2 Open-PDK

[![License: Solderpad Hardware License v2.1](https://img.shields.io/badge/License-Solderpad%20Hardware%20License%20v2.1-blue.svg)](LICENSE)
[![Quarto Publish](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/actions/workflows/quarto-publish.yml/badge.svg?branch=main)](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/actions/workflows/quarto-publish.yml)
[![Regression](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/actions/workflows/regression.yml/badge.svg?branch=main)](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/actions/workflows/regression.yml)
[![License Check](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/actions/workflows/license-check.yml/badge.svg?branch=main)](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/actions/workflows/license-check.yml)
[![Tutorial](https://img.shields.io/badge/Tutorial-online-orange?logo=quarto)](https://iic-jku.github.io/ihp-sg13g2-ams-chip-template/index.html)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20129233.svg)](https://doi.org/10.5281/zenodo.20129233)

(c) 2026 Simon Dorrer and Harald Pretl

Institute for Integrated Circuits and Quantum Computing, Johannes Kepler University (JKU), Linz, Austria

> [!IMPORTANT]
> This repository requires the [IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS) container with tag `2026.07` or later.

<p align="center">
  <a href="render/img/chip_top_black.png">
    <img src="render/img/chip_top_black.png" alt="Chip render of the ihp-sg13g2 analog-mixed signal template chip (1.6 mm x 1.6 mm)" width=70%>
  </a>
  <br>
  <em>Chip render of the ihp-sg13g2 analog-mixed signal template chip (1.6 mm x 1.6 mm).</em>
</p>

<p align="center">
  <a href="render/img/chip_top_black_TM2.png">
    <img src="render/img/chip_top_black_TM2.png" alt="Render of the TopMetal2 AMS Chip logo, generated with the tool ArtistIC" width=70%>
  </a>
  <br>
  <em>Render of the TopMetal2 AMS Chip logo, generated with the tool ArtistIC.</em>
</p>


## Overview

This Makefile-driven repository simulates, builds, and fully verifies (LVS, DRC, PEX) a complete analog mixed-signal chip for the ihp-sg13g2 130nm Open-PDK, including padframe generation and top-level assembly. It uses:

- [**LibreLane**](https://github.com/librelane/librelane) for digital macro hardening, padframe generation and top-level assembly
- [**Xschem**](https://github.com/StefanSchippers/xschem) for schematic entry
- [**Ngspice**](https://github.com/danchitnis/ngspice-sf-mirror), [**VACASK**](https://codeberg.org/arpadbuermen/VACASK) and [**CACE**](https://github.com/fossi-foundation/cace) for analog simulation
- [**KLayout**](https://github.com/KLayout/klayout) for viewing and routing of the layout
- [**Magic**](https://github.com/rtimothyedwards/magic) + [**Netgen**](https://github.com/rtimothyedwards/netgen) and [**KLayout**](https://github.com/KLayout/klayout) for LVS, DRC and PEX verification
- **SystemVerilog**, [**cocotb**](https://github.com/cocotb/cocotb), [**GTKWave**](https://github.com/gtkwave/gtkwave) and [**Surfer**](https://gitlab.com/surfer-project/surfer) for digital simulation

The repository is the starting point for your own custom silicon and provides a universal design flow solution: Just clone the repo, enter the IIC-OSIC-TOOLS container, and run `make all` to get a tapeout-ready analog-mixed signal chip. Focus on your design and do not care about the tools and the design flow!

Furthermore, it serves as a regression test for the above-mentioned open-source tools and their dependencies using the ihp-sg13g2 Open-PDK.


## Tutorial

A step-by-step tutorial, including additional exercises, can be found [here](https://iic-jku.github.io/ihp-sg13g2-ams-chip-template/index.html).

An overview of the open source IC design landscape is presented [here](https://ic3.ie/resources/open-source-ic-design-day).

Are you interested in an open-source RFIC flow? Check it out [here](https://github.com/iic-jku/SG13CMOS_SPARX).


## Examples

Examples based on this template are:
- [TinyWhisper](https://github.com/iic-jku/TinyWhisper): An Open-Source Fully-Integrated Multi-Mode Short-Wave Transmitter for Amateur Radio Applications in 130-nm CMOS
- [SPARX](https://github.com/iic-jku/SG13G2_SPARX): An Open-Source, Automated, Programmatically Generated, Frequency-Scalable Six-Port Receiver in 130-nm CMOS
- wafer.space gf180mcuD MPW [Multi-Project Chip](https://github.com/iic-jku/gf180mcu-jku-projects)


## Chip Documentation

A designer-oriented description of this chip can be found in [doc/](doc/):

- **[doc/specifications.md](doc/specifications.md)**: top-level specifications (technology, supplies, clock, macro inventory, functional behaviour).
- **[doc/pinout.md](doc/pinout.md)**: full 32-pad bondpad table per side, with the `chip_top` port and the role each pad carries inside `chip_core`.
- **[doc/floorplan.md](doc/floorplan.md)**: die / core geometry, hard-macro placement coordinates, PDN strategy and the floorplan diagram.


## Directory Structure

```text
📁 ihp-sg13g2-ams-chip-template/
├─ 📁 .github/
│  └─ 📁 workflows/
│     ├─ license-check.yml
│     ├─ quarto-publish.yml
│     └─ regression.yml
├─ 📁 doc/
│  ├─ 📁 ihp-sg13g2-Open-PDK/
│  ├─ 📁 ihp-structure-proposals/
│  ├─ 📁 klayout/
│  ├─ 📁 librelane/
│  ├─ 📁 sizing/
│  ├─ floorplan.md
│  ├─ pinout.md
│  └─ specifications.md
├─ 📁 flow/
│  ├─ 📁 artistic/
│  ├─ 📁 librelane/
│  │  ├─ chip_top.sdc
│  │  ├─ config.yaml
│  │  └─ pdn_cfg.tcl
│  └─ 📁 logo/
│     └─ chip_logo_mono.png
├─ 📁 ip/
│  ├─ 📁 sg13g2_io_custom/
│  ├─ 📁 sg13g2_ip__bondpad_70x70/
│  │  ├─ 📁 final/
│  │  ├─ 📁 script/
│  │  ├─ 📁 verification/
│  │  ├─ Makefile
│  │  └─ README.md
│  ├─ 📁 sg13g2_ip__jku/
│  │  ├─ 📁 final/
│  │  ├─ 📁 logo/
│  │  ├─ 📁 script/
│  │  ├─ 📁 verification/
│  │  ├─ Makefile
│  │  └─ README.md
│  └─ 📁 sg13g2_ip__jku_names/
│     ├─ 📁 final/
│     ├─ 📁 logo/
│     ├─ 📁 script/
│     ├─ 📁 verification/
│     ├─ Makefile
│     └─ README.md
├─ 📁 layout/
│  ├─ chip_top.gds.gz
│  └─ chip_top_logo_fill.gds.gz
├─ 📁 LICENSES/
│  ├─ Apache-2.0.txt
│  ├─ LicenseRef-EUROPRACTICE.txt
│  └─ SHL-2.1.txt
├─ 📁 macros/
│  ├─ 📁 counter/
│  │  ├─ 📁 final/
│  │  ├─ 📁 flow/
│  │  ├─ 📁 fpga/
│  │  ├─ 📁 netlist/
│  │  ├─ 📁 render/
│  │  ├─ 📁 rtl/
│  │  ├─ 📁 schematic/
│  │  ├─ 📁 scripts/
│  │  ├─ 📁 testbenches/
│  │  ├─ 📁 verification/
│  │  ├─ Makefile
│  │  └─ README.md
│  └─ 📁 inverter/
│     ├─ 📁 final/
│     ├─ 📁 layout/
│     ├─ 📁 netlist/
│     ├─ 📁 render/
│     ├─ 📁 schematic/
│     ├─ 📁 scripts/
│     ├─ 📁 testbenches/
│     ├─ 📁 verification/
│     ├─ Makefile
│     └─ README.md
├─ 📁 netlist/
│  ├─ 📁 layout/
│  ├─ 📁 nl/
│  ├─ 📁 pex/
│  ├─ 📁 pnl/
│  └─ 📁 spice/
├─ 📁 packaging/
│  ├─ 📁 layout/
│  │  ├─ chip_top_bondplan.gds
│  │  ├─ chip_top_logo_TM2.gds.gz
│  │  ├─ EP_PACKAGES_08022018.gds
│  │  └─ OP_QFN32_A4_FIT.gds
│  ├─ 📁 render/
│  │  └─ chip_top_bondplan_{white,black}.{png,svg}
│  ├─ 📁 scripts/
│  │  └─ run_bondplan.py
│  ├─ config.yaml
│  ├─ README.md
│  └─ result.md
├─ 📁 release/
│  └─ 📁 v.1.0.0/
│     ├─ 📁 gds/
│     ├─ 📁 img/
│     ├─ 📁 netlist/
│     └─ README.md
├─ 📁 render/
│  ├─ 📁 blender/
│  └─ 📁 img/
├─ 📁 rtl/
│  ├─ chip_core.sv
│  └─ chip_top.sv
├─ 📁 schematic/
│  └─ 📁 xschem/
│     ├─ chip_top.sch
│     ├─ chip_top.sym
│     ├─ chip_top_pex.sym
│     └─ xschemrc
├─ 📁 scripts/
│  ├─ 📁 plot_simulations/
│  ├─ add_logo_fill.sh
│  ├─ add_rectangle.py
│  └─ lay2img.py
├─ 📁 testbenches/
│  ├─ 📁 cocotb/
│  │  ├─ chip_top_tb.gtkw
│  │  ├─ chip_top_tb.py
│  │  └─ chip_top_tb.surf.ron
│  └─ 📁 xschem/
│     ├─ chip_top_tb_tran.sch
│     └─ xschemrc
├─ 📁 tutorial/
│  ├─ 📁 fig/
│  ├─ _quarto.yml
│  ├─ index.qmd
│  ├─ Makefile
│  └─ requirements.txt
├─ 📁 verification/
│  ├─ 📁 drc/
│  ├─ 📁 lvs/
│  └─ 📁 reports/
│     ├─ antenna_summary.rpt
│     ├─ antenna_violations.rpt
│     ├─ hold_setup_timing.rpt
│     ├─ irdrop.rpt
│     ├─ lvs.netgen.rpt
│     ├─ manufacturability.rpt
│     ├─ stapostpnr_*.rpt
│     ├─ stat.rpt
│     ├─ yosys_post_dff.rpt
│     ├─ yosys_pre_techmap.rpt
│     └─ yosys_synth_check.rpt
├─ CITATION.cff
├─ LICENSE
├─ Makefile
├─ README.md
├─ REUSE.toml
└─ ToDo.md
```


## Show Available Targets

The default Make target is `help`, so running `make` prints usage and all available targets with short descriptions.

```sh
make
make help
```


## Initialize Git Submodules

Initializes and updates the repository submodules (for example [ArtistIC](https://github.com/pulp-platform/artistic)):

```sh
make init-submodules
```

Run this after cloning the repository, or whenever submodule pointers are updated.


## Simulation

We use [cocotb](https://www.cocotb.org/), a Python-based testbench environment, for the verification of the chip.
The underlying simulator is [Icarus Verilog](https://github.com/steveicarus/iverilog).

The simulation targets accept an optional `CELL` variable (default: `chip_top`).
The testbench is located in `testbenches/cocotb/chip_top_tb.py`. To run the RTL simulation, use:

```sh
make sim-rtl-cocotb
```

To run the gate-level (GL) simulation with cocotb, use:

```sh
make sim-gl-cocotb
```

To run the gate-level simulation with Xschem, use:

```sh
make sim-gl-xschem
```

> [!NOTE]
> `sim-gl-xschem` is available and converges, but it may take a long time depending on the hardware used.
> It is therefore **not** included in `sim-all` and must be called manually.

To plot the Xschem simulation results using the Python script in `scripts/plot_simulations/`, use:

```sh
make sim-view-xschem
make sim-view-xschem CELL=chip_top
```

The target runs `python3 scripts/plot_simulations/plot_<CELL>.py`. `CELL` defaults to `chip_top`.

> [!NOTE]
> `sim-view-xschem` is intentionally **not** called by `sim-all`.
> It opens the generated Python figures, which blocks the shell until the window is closed.
> It is designed for interactive use and must be called manually after the simulation has completed.

The cocotb simulations generate a waveform file under `testbenches/cocotb/sim_build/chip_top.fst`.
You can view it with a waveform viewer such as [GTKWave](https://gtkwave.github.io/gtkwave/) or [Surfer](https://surfer-project.org/).
The waveform viewer can be changed with `WAVEFORM_VIEWER=<gtkwave|surfer>` (default: `gtkwave`).

```sh
make sim-view-cocotb                                          # view chip_top waveform with GTKWave (default)
make sim-view-cocotb WAVEFORM_VIEWER=surfer                   # use Surfer instead
```

Each cocotb simulation folder contains a pre-configured waveform layout file (`<CELL>_tb.gtkw` for GTKWave, `<CELL>_tb.surf.ron` for Surfer).
The view target loads it automatically together with the current `.fst`, so signal formatting is preserved across runs.

To run all non-interactive simulation targets in sequence (RTL cocotb and GL cocotb), use:

```sh
make sim-all
```

> [!NOTE]
> `sim-view-cocotb` is intentionally **not** called by `sim-all`.
> It opens a waveform viewer GUI (GTKWave or Surfer), which blocks the shell until the window is closed.
> It is designed for interactive use and must be called manually after the simulation has completed.

> [!NOTE]
> `sim-gl-xschem` and `sim-view-xschem` are also **not** included in `sim-all` because `sim-gl-xschem` may take a long time depending on the hardware used.
> Run them manually with `make sim-gl-xschem` followed by `make sim-view-xschem` when needed.


## LibreLane Flow

Run the LibreLane flow with:

```sh
make librelane
```

Additional targets are available for different DRC configurations:

- `make librelane-nodrc` – run LibreLane without DRC checks
- `make librelane-magicdrc` – run LibreLane with only Magic DRC checks
- `make librelane-klayoutdrc` – run LibreLane with only KLayout DRC checks

These targets are also available for the digital macros. After the LibreLane flow completes successfully, the generated views are saved under `flow/final/`.


## View the Design

After completion, you can view the design using the OpenROAD GUI:

```sh
make librelane-openroad
```

Or using KLayout:

```sh
make librelane-klayout
```

These commands are also available for the digital macros.


## Copy Important Reports

To copy the Yosys synthesis checks, antenna-violation reports, post-PnR hold & setup timing summary, LVS report, and manufacturability report from the latest LibreLane run into `verification/reports/`, run:

```sh
make copy-reports
```

This only works if the latest run completed without errors. This command is also available for the digital macros.

> [!NOTE]
> The Magic and KLayout DRC reports are temporarily not copied because IHP's
> `metal1_pin_offgrid` rule trips on the pad ring. Once it is fixed upstream
> the corresponding `cp` lines in `Makefile :: copy-reports` will be re-enabled.


## Copy the Final GDS

To copy and compress the latest GDS from `flow/final/gds/` into `layout/`, run:

```sh
make copy-gds
```


## Copy the Final Netlist

To copy the latest SPICE, PnL, and NL netlists from `flow/final/spice/` into `netlist/spice/`, from `flow/final/pnl/` into `netlist/pnl/`, and from `flow/final/nl/` into `netlist/nl/`, run:

```sh
make copy-netlist
```

This only works if the latest run completed without errors.


## Copy the Final Render

To copy the latest LibreLane chip render from `flow/final/render/` into `render/img/`, run:

```sh
make copy-render
```

This creates `render/img/chip_top_librelane.png`. This only works if the latest run completed without errors.


## Render Top Layout

Renders the top-level GDS from `layout/` and saves it in the `render/img/` folder:

```sh
make render-gds
```

This only works if the latest run completed without errors. This command is also available for the digital macros.


## Build Bondpad

To build the bondpad in the `ip` folder, run the following command:

```sh
make build-bondpad
```


## Build Logos

To build the logos in the `ip` folder, run the following command:

```sh
make build-logos
```


## Build Macros

To build a specific macro, run the corresponding target from the `Makefile`. To build all currently enabled macros, run:

```sh
make build-macros
```

### Build Digital Macros

The following command builds the `counter` digital macro:

```sh
make build-counter
```

For each digital macro this dispatches to its in-tree `make all`, which lints, simulates, runs LibreLane, copies the reports, and renders the final GDS.

> [!TIP]
> Each macro has its own `Makefile` and `README.md` with additional targets, such as linting, simulation, and verification.
> For example, to lint the counter or run its simulation, refer to [macros/counter/README.md](macros/counter/README.md).

### Build Analog Macros

Each analog macro has its own `klayout-verify` and `magic-verify` targets that run LVS, DRC, and PEX for the top-level cell.

To build the inverter macro:

```sh
make build-inverter
```

All analog macros are included in `build-macros` alongside the digital macros.


## Build Top

To run LibreLane for the top-level chip and copy the resulting reports, GDS, netlist, and chip render back into the source tree, then add the logo + fill structures and render the final GDS, run:

```sh
make build-top
```

Internally this executes (in order): `librelane-nodrc` → `copy-reports` → `copy-gds` → `copy-netlist` → `copy-render` → `add-logo-fill` → `render-gds`.


## Build All

To initialise submodules, build the bondpad, build the logos, build the macros, and run the full `build-top` flow, run:

```sh
make build-all
```

This is useful if you want to rebuild the chip from scratch. Clone the repository, enter the IIC-OSIC-TOOLS environment, and run `make build-all`.


## Add Logo and Fill

To add the chip logo (PNG → GDS) and the fill structures on top of the LibreLane output (so the final GDS in `layout/` includes the artwork), run:

```sh
make add-logo-fill
```

This calls `scripts/add_logo_fill.sh` and writes `layout/chip_top_logo_fill.gds.gz`. The step is also called from `make build-top`.

> [!NOTE]
> In the future, it is planned to replace this script and Makefile target with a custom librelane step.


## Export Schematic Netlist for LVS

Exports the schematic netlist for LVS from Xschem and places it in `netlist/schematic/`.

The `EV_PRECISION` parameter sets the number of significant digits used by Xschem's `ev` function when calculating device properties (default: 5). Increase this to avoid LVS mismatches caused by floating-point rounding differences between Xschem and KLayout (see [xschem#465](https://github.com/StefanSchippers/xschem/issues/465)).

The `ntap` and `ptap` substrate contacts are ignored during LVS in both flows. `sak-lvs.sh` runs KLayout LVS with the `--disable_tap_extraction` option so it does not extract `ntap` and `ptap` devices from the layout (matching Magic + Netgen LVS).

KLayout uses CDL netlists, while Magic uses SPICE netlists. Accordingly, `klayout-lvs-netlist` uses the Xschem commands `set spiceprefix 1`, `set lvs_netlist 1`, `set top_is_subckt 1`, and `set lvs_ignore 1`, while `magic-lvs-netlist` uses `set spiceprefix 1`, `set lvs_netlist 0`, `set top_is_subckt 1`, and `set lvs_ignore 1`. Hence, switching between CDL and SPICE netlists can be done with `lvs_netlist`.

To extract a CDL schematic netlist for KLayout LVS, use:
```sh
make klayout-lvs-netlist
make klayout-lvs-netlist CELL=chip_top
make klayout-lvs-netlist EV_PRECISION=5
```

To extract a SPICE schematic netlist for Magic + Netgen LVS, use:
```sh
make magic-lvs-netlist
make magic-lvs-netlist CELL=chip_top
make magic-lvs-netlist EV_PRECISION=5
```


## Layout Versus Schematic (LVS)

Exports the schematic netlist from Xschem, then runs LVS. Compares the GDS layout in `layout/` against the schematic netlist in `netlist/schematic/`. Both flows use `sak-lvs.sh` and write their reports into per-cell run folders: `verification/lvs/<CELL>.magic.lvs/` (Magic + Netgen) and `verification/lvs/<CELL>.klayout.lvs/` (KLayout, `.lvsdb`). The run folders are wiped at the start of each run, so they always reflect the latest run only. The extracted layout netlist is moved to `netlist/layout/`.

**KLayout LVS** uses `sak-lvs.sh` (KLayout mode `-k`), which wraps `run_lvs.py` from the IHP Open-PDK:

```sh
make klayout-lvs
make klayout-lvs CELL=chip_top
```

**Magic + Netgen LVS** uses `sak-lvs.sh` (Magic + Netgen mode `-m`, the default), which extracts the layout netlist with Magic and compares it against the schematic netlist with Netgen, using the Netgen setup from the IHP Open-PDK:

```sh
make magic-lvs
make magic-lvs CELL=chip_top
```


## Design Rule Check (DRC)

Runs DRC on the GDS layout in `layout/`. Both flows use `sak-drc.sh` and write their reports into per-cell run folders: `verification/drc/<CELL>.magic.drc/` (Magic) and `verification/drc/<CELL>.klayout.drc/` (KLayout, `.lyrdb`). The run folders are wiped at the start of each run, so they always reflect the latest run only.

The `DRC_LEVEL` parameter selects the KLayout DRC level (`sak-drc.sh -l`). It is ignored by `magic-drc`, since Magic has no selectable rule decks and always runs the full rule set compiled into the PDK's Magic tech file:

- `precheck` = core FEOL + BEOL manufacturing rules only (fast iteration)
- `macro` = block-in-isolation sign-off: `precheck` plus off-grid, zero-area, and pin/label checks (default)
- `regular` = full-chip sign-off: all checks, including density and antenna

| Check | `precheck` | `macro` _(default)_ | `regular` |
| --- | :---: | :---: | :---: |
| FEOL + BEOL core rules | ✓ | ✓ | ✓ |
| Off-grid / angle | – | ✓ | ✓ |
| Zero-area / geometry | – | ✓ | ✓ |
| Pin / label | – | ✓ | ✓ |
| Recommended / extra rules | – | – | ✓ |
| Density (chip-level fill) | – | – | ✓ |
| Antenna | – | – | ✓ |

**KLayout DRC (minimum)** runs a pre-check (`precheck`) KLayout DRC on the final top-level layout with logo and fill structures:

```sh
make klayout-drc-minimum
```

**KLayout DRC (regular)** runs a full (`regular`) KLayout DRC on the final top-level layout with logo and fill structures:

```sh
make klayout-drc-regular
```

**KLayout DRC** runs a KLayout DRC at the selected `DRC_LEVEL`:

```sh
make klayout-drc
make klayout-drc CELL=chip_top
make klayout-drc CELL=chip_top DRC_LEVEL=regular
```

**Magic DRC** runs a Magic DRC with all subcells flattened (`sak-drc.sh -f "*"`):

```sh
make magic-drc
make magic-drc CELL=chip_top
```


## Parasitic Extraction (PEX)

Runs parasitic extraction on the GDS layout in `layout/`. The extracted SPICE netlist is written to `netlist/pex/`.

The extracted SPICE filenames include the selected extraction mode:
- `klayout-pex` writes `netlist/pex/<CELL>_klayout_pex_<EXT_MODE>.spice`
- `magic-pex` writes `netlist/pex/<CELL>_magic_pex_<EXT_MODE>.spice`

The `EXT_MODE` parameter selects the extraction mode:
- `1` = C-decoupled (default)
- `2` = C-coupled
- `3` = full-RC

> [!NOTE]
> For `klayout-pex`, `EXT_MODE=1` (C-decoupled) is not yet supported by kpex and automatically falls back to `EXT_MODE=2` (CC) with a warning.

The `.subckt` name in the extracted SPICE file is `<CELL>_pex`: `magic-pex` sets it directly via the `sak-pex.sh` option `-n <CELL>_pex`, while for `klayout-pex` it is automatically renamed from `<CELL>_flat` (kpex).

If a matching Xschem symbol (`schematic/<CELL>_pex.sym`) exists, the `.subckt` pin order in the extracted SPICE file is automatically reordered to match the symbol's pin positions. This ensures the PEX netlist can be used directly with the corresponding Xschem symbol for simulation regardless of the selected `EXT_MODE`.

**KLayout PEX** uses `kpex` with the Magic extraction engine currently (2.5D engine is work in progress):

```sh
make klayout-pex
make klayout-pex CELL=chip_top
make klayout-pex CELL=chip_top EXT_MODE=3
```

**Magic PEX** uses `sak-pex.sh`, which extracts the parasitics with Magic (C-decoupled, C-coupled, or full-RC):

```sh
make magic-pex
make magic-pex CELL=chip_top
make magic-pex CELL=chip_top EXT_MODE=3
```

For full-RC extraction (`EXT_MODE=3`), `magic-pex` additionally exposes the `sak-pex.sh` `extresist` tuning parameters. They are ignored in `EXT_MODE=1`/`2`:

- `THRESHOLD` - extresist threshold in mOhm (`-t`, default `10000` = 10 Ohm)
- `MINRES` - extresist minimum resistance in mOhm (`-r`, default `1000` = 1 Ohm)
- `MINDELAY` - extresist minimum delay in ps (`-y`, default `1`; `0` = gate by resistance)

```sh
make magic-pex CELL=chip_top EXT_MODE=3 THRESHOLD=5000 MINRES=500 MINDELAY=2
```


## Verify a Specific Cell

Runs LVS, DRC, and PEX for a specific cell (e.g. `chip_top`):

```sh
make klayout-verify CELL=chip_top
make magic-verify CELL=chip_top
```


## Verify Top Cell

Runs LVS, DRC, and PEX for the top cell:

```sh
make klayout-verify
make magic-verify
```


## Packaging (Bondplan Generation)

Generates the bondplan fully automatically: the die placed in the package cavity, all bondwires, a pin table, and the filled EUROPRACTICE title block. Inputs are the final chip GDS (`layout/chip_top_logo_fill.gds.gz`) and the EUROPRACTICE package library, from which the QFN32 drawing sheet is extracted:

```sh
make bondplan                        # uses the default VERSION (1.0.0)
make bondplan VERSION=2.1.0          # stamp another version on the sheet
```

The `VERSION` variable is passed to the flow and printed in the title block (`DIE: CHIP_TOP - V.1.0.0`), so the version number is maintained in the Makefile only.

The flow ([packaging/scripts/run_bondplan.py](packaging/scripts/run_bondplan.py)) is driven by [packaging/config.yaml](packaging/config.yaml), which holds the full package-pin-to-die-pad `PINOUT` in a LibreLane-style config format. It detects the die bondpads (`Passiv` openings and `TopMetal2.text` labels), places the die in the package cavity, draws the bondwires, and checks wire lengths, crossings, spacing, lead skew and analog guard clearances. Outputs:

- `packaging/layout/chip_top_bondplan.gds`: the bondplan GDS
- [packaging/result.md](packaging/result.md): bond report with summary and bond table
- `packaging/render/chip_top_bondplan_{white,black}.{png,svg}`: bonding diagram images

See [packaging/README.md](packaging/README.md) for the full flow documentation and configuration reference.

<p align="center">
  <a href="packaging/render/chip_top_bondplan_white.png">
    <img src="packaging/render/chip_top_bondplan_white.png" alt="Bonding diagram of the ihp-sg13g2 AMS template chip in a QFN32 package" width=70%>
  </a>
  <br>
  <em>Bonding diagram of the ihp-sg13g2 AMS template chip in a QFN32 package.</em>
</p>


## Build and Verify All

Runs full simulation (`sim-all`), then `build-all`, followed by Magic DRC for both `chip_top` and `chip_top_logo_fill`, and finally generates the bondplan (`bondplan`):

```sh
make all
```


## Release

Copies the final top-level GDS with logo and fill structures from `layout/` to `release/v.<VERSION>/gds/`, copies the generated netlists into `release/v.<VERSION>/netlist/`, and copies the chip renders and the bonding diagram into `release/v.<VERSION>/img/`.

The following netlist folders are exported:

- `netlist/layout` -> `release/v.<VERSION>/netlist/layout`
- `netlist/pnl` -> `release/v.<VERSION>/netlist/pnl`
- `netlist/spice` -> `release/v.<VERSION>/netlist/spice`

The following chip renders are exported:

- `render/img/chip_top_black.png` -> `release/v.<VERSION>/img/chip_top_black.png`
- `render/img/chip_top_white.png` -> `release/v.<VERSION>/img/chip_top_white.png`
- `render/img/chip_top_librelane.png` -> `release/v.<VERSION>/img/chip_top_librelane.png`

The bonding diagram is exported as well (see `make bondplan`):

- `packaging/render/chip_top_bondplan_black.png` -> `release/v.<VERSION>/img/chip_top_bondplan_black.png`
- `packaging/render/chip_top_bondplan_white.png` -> `release/v.<VERSION>/img/chip_top_bondplan_white.png`

> [!NOTE]
> `netlist/schematic` and `netlist/pex` are currently not copied by the `release` target.

Run with default version (`1.0.0`):

```sh
make release
```

Run with a custom version:

```sh
make release VERSION=2.1.0
```


## Regression

The `regression` target is the project's end-to-end smoke test for the [IIC-OSIC-TOOLS](https://github.com/iic-jku/iic-osic-tools) environment. Its goal is to exercise **every tool and flow** in the template at least once with the **shortest possible runtime**. It is a tool/flow regression, not a design sign-off.

```sh
make regression
```

This target also runs automatically in continuous integration: the [`regression`](.github/workflows/regression.yml) GitHub Actions workflow runs `make regression` inside the `IIC-OSIC-TOOLS` container nightly (and on manual dispatch), and its status is shown by the *Regression* badge at the top of this README. The scheduled run is gated so it only executes when there have been changes since the previous night.

To keep the runtime low while still covering the full toolchain, the regression makes the following trade-offs:

- The counter macro is hardened with `librelane-magicdrc` (only **Magic DRC** enabled, the slower KLayout DRC is skipped). Netgen LVS still runs as part of the flow.
- The chip top-level runs `librelane-nodrc`. All DRC checks are skipped to save runtime on the large top-level assembly. The macros and IP blocks are DRC-checked individually beforehand, so this only leaves the top-level routing/fill unchecked.
- KLayout DRC (`sak-drc.sh`) is skipped inside the LibreLane runs, but is still exercised in the bondpad and logo IP builds, and in the inverter `klayout-verify`.
- Only **one** logo (`sg13g2_ip__jku`) is regenerated. It is the only step that exercises the PNG to GDS flow. The second logo (`sg13g2_ip__jku_names`) uses an identical toolchain and reuses its committed views.
- Exactly **one** CACE parameter set is run (the AC VDD sweep `ac_params`, no Monte-Carlo). Swap `ac_params` for `ac_mc_params` / `ac_mm_params` in the target to also exercise the Monte-Carlo flow.

The regression runs bottom-up: first the inverter and counter macros, then the top-level assembly (submodules, bondpad, logo) and finally the chip top-level LibreLane run that integrates the freshly built macros and IP. After the counter is hardened, `copy-final` copies its fresh `flow/final/` views into `macros/counter/final/`, so that the gate-level simulation (`sim-gl-cocotb`) and the chip top-level integration use the freshly built outputs rather than the committed ones.

The following tools and flows are checked:

| Tool / flow | Where it is exercised |
| --- | --- |
| git submodules | `init-submodules` |
| KLayout scripting (bondpad generator), KLayout DRC, Magic DRC | `build-bondpad` |
| PNG to GDS logo generation, KLayout DRC, Magic DRC | `sg13g2_ip__jku all` (single logo) |
| Xschem + ngspice (analog simulation) | inverter `sim-xschem` (`inverter_tb_dc_vout`) |
| CACE (+ ngspice) | inverter CACE, single parameter set (`ac_params`) |
| KLayout LVS (`sak-lvs.sh`) + KLayout DRC (`sak-drc.sh`) + KLayout PEX (`kpex`) | inverter `klayout-verify CELL=inverter_top` |
| Magic extract + Netgen LVS (`sak-lvs.sh`) + Magic DRC (`sak-drc.sh`) + Magic PEX (`sak-pex.sh`) | inverter `magic-verify CELL=inverter_top` |
| Magic LEF export + LIB + Verilog stub + `lay2img` render | inverter `build-top` |
| Verilator lint | counter `lint-verilog-all` |
| Icarus Verilog (`iverilog`/`vvp`) | counter `sim-rtl-verilog` |
| cocotb (RTL + gate-level) | counter `sim-rtl-cocotb`, `sim-gl-cocotb` |
| yosys + nextpnr-ice40 + icepack (FPGA) | counter `build-fpga` |
| LibreLane (OpenROAD / yosys / KLayout streamout / Netgen LVS) | counter `librelane-magicdrc`, chip `librelane-nodrc` |
| Magic DRC (sign-off, run inside LibreLane) | counter `librelane-magicdrc` |
| `vlog2Verilog` / `vlog2Spice` / `spi2xspice` | counter `generate-xspice` |
| Xschem gate-level | counter `sim-gl-xschem` |


## Cite This Work

```
@software{2026_ams_chip_template,
	author = {Dorrer, Simon and Pretl, Harald},
	month = apr,
    year = {2026},
	title = {{GitHub Repository of an Open-Source Analog-Mixed Signal Chip Design Template for the ihp-sg13g2 Open-PDK}},
	url = {https://github.com/iic-jku/ihp-sg13g2-ams-chip-template},
	doi = {10.5281/zenodo.20129233}
}
```


## Acknowledgements

First, we would like to thank the open-source chip design community for its valuable input and constructive feedback. We especially thank 
- [Leo Moser](https://github.com/mole99), who initially started [template repositories](https://github.com/IHP-GmbH/ihp-sg13g2-librelane-template) based on the LibreLane flow.
- [Tim Edwards](https://github.com/RTimothyEdwards) for helping with Magic + Netgen LVS and PEX issues.
- [Krzysztof Herman](https://github.com/KrzysztofHerman) for discussions about the [directory structure](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/tree/main/doc/ihp-structure-proposals).

This project is funded by the JKU/SAL [IWS Lab](https://research.jku.at/de/projects/jku-lit-sal-intelligent-wireless-systems-lab-iws-lab/), a collaboration of [Johannes Kepler University](https://jku.at) and [Silicon Austria Labs](https://silicon-austria-labs.com).

<table width="100%">
  <tr>
    <td align="left" width="50%">
      <a href="https://iic.jku.at" target="_blank">
        <img src="tutorial/fig/funding/iic-jku.svg" alt="Johannes Kepler University: Institute for Integrated Circuits and Quantum Computing" width="94%"/>
      </a>
    </td>
    <td align="right" width="50%">
      <a href="https://silicon-austria-labs.com" target="_blank">
        <img src="tutorial/fig/funding/silicon-austria-labs-logo.svg" alt="Silicon Austria Labs" width="94%"/>
      </a>
    </td>
  </tr>
</table>

## License

Licensed under the **Solderpad Hardware License v2.1**, see [`LICENSE`](LICENSE).
