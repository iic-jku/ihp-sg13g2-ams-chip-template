# An Open-Source Analog-Mixed Signal Chip Design Template for the ihp-sg13g2 Open-PDK

[![Quarto Publish](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/actions/workflows/quarto-publish.yml/badge.svg?branch=main)](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template/actions/workflows/quarto-publish.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18378633.svg)](https://doi.org/10.5281/zenodo.18378633)

(c) 2026 Simon Dorrer and Harald Pretl

Institute for Integrated Circuits and Quantum Computing, Johannes Kepler University (JKU), Linz, Austria

> [!IMPORTANT]
> This repository requires the [IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS) container with tag `2026.05` or later.

<p align="center">
  <a href="render/img/chip_top_black.png">
    <img src="render/img/chip_top_black.png" alt="Chip render of the ihp-sg13g2 analog-mixed signal template chip (TODOmm x TODOmm)" width=70%>
  </a>
  <br>
  <em>Chip render of the ihp-sg13g2 analog-mixed signal template chip (TODOmm x TODOmm).</em>
</p>


## Overview

This shell-script-driven repository uses OpenROAD Flow-Scripts (ORFS) to synthesize a digital macro and demonstrates gate-level simulation with Ngspice in Xschem for use in analog mixed-signal designs. Looking for something more powerful? A newer template repository ([ihp-sg13g2-ams-chip-template](https://github.com/iic-jku/ihp-sg13g2-ams-chip-template)) simulates, builds, and fully verifies (LVS, DRC, PEX) a complete analog mixed-signal chip, including padframe generation and top-level assembly. It uses:

- **LibreLane Flow** for digital macro hardening, padframe generation and top-level assembly
- **Xschem** for schematic entry
- **Ngspice**, **VACASK** and **CACE** for analog simulation
- **KLayout** for viewing and routing of the layout
- **Magic+Netgen** and **KLayout** for LVS, DRC and PEX verification
- **Verilog**, **cocotb**, **GTKWave** and **Surfer** for digital simulation

This template repository is Makefile-driven and provides a universal design flow solution: Just clone the repo, run `make all`, and get a tapeout-ready analog-mixed signal chip. This is the starting point for your own custom silicon. Focus on your design and do not care about the tools and the design flow!


## Tutorial

A step-by-step tutorial, including additional exercises, can be found [here](https://iic-jku.github.io/ihp-sg13g2-ams-chip-template/index.html).


## Directory Structure

```text
📁 ihp-sg13g2-ams-chip-template/
├─ 📁 doc/
│  └─ pinout.md
├─ 📁 flow/
│  ├─ 📁 artistic/
│  ├─ 📁 librelane/
│  │  ├─ config.yaml
│  │  ├─ pdn_cfg.tcl
│  │  └─ chip_top.sdc
│  ├─ 📁 logo/
│  │  └─ chip_logo_mono.png
│  └─ 📁 reports/
│     ├─ antenna_summary.rpt
│     ├─ antenna_violations.rpt
│     ├─ hold_setup_timing.rpt
│     ├─ lvs.netgen.rpt
│     ├─ manufacturability.rpt
│     ├─ stat.rpt
│     ├─ yosys_post_dff.rpt
│     ├─ yosys_pre_techmap.rpt
│     └─ yosys_synth_check.rpt
├─ 📁 ip/
│  ├─ 📁 sg13g2_io_custom/
│  ├─ 📁 sg13g2_ip__bondpad_70x70/
│  │  ├─ 📁 final/
│  │  ├─ 📁 script/
│  │  ├─ 📁 verification/
│  │  ├─ Makefile
│  │  └─ README.md
│  ├─ 📁 sg13g2_ip__ce/
│  │  ├─ 📁 final/
│  │  ├─ 📁 logo/
│  │  ├─ 📁 script/
│  │  ├─ 📁 verification/
│  │  ├─ Makefile
│  │  └─ README.md
│  ├─ 📁 sg13g2_ip__ce_names/
│  │  ├─ 📁 final/
│  │  ├─ 📁 logo/
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
├─ 📁 macros/
│  ├─ 📁 coupled_resonator_lc_bpf/
│  │  ├─ 📁 schematic/
│  │  ├─ 📁 scripts/
│  │  └─ 📁 testbenches/
│  ├─ 📁 inverter/
│  │  ├─ 📁 final/
│  │  ├─ 📁 layout/
│  │  ├─ 📁 netlist/
│  │  ├─ 📁 render/
│  │  ├─ 📁 schematic/
│  │  ├─ 📁 scripts/
│  │  ├─ 📁 testbenches/
│  │  ├─ 📁 verification/
│  │  ├─ Makefile
│  │  └─ README.md
│  └─ 📁 counter/
│     ├─ 📁 final/
│     ├─ 📁 flow/
│     ├─ 📁 fpga/
│     ├─ 📁 netlist/
│     ├─ 📁 render/
│     ├─ 📁 rtl/
│     ├─ 📁 schematic/
│     ├─ 📁 scripts/
│     ├─ 📁 testbenches/
│     ├─ Makefile
│     └─ README.md
├─ 📁 netlist/
│  ├─ 📁 layout/
│  │  └─ chip_top.spice
│  ├─ 📁 nl/
│  │  └─ chip_top.nl.v
│  ├─ 📁 pex/
│  │  ├─ reorder_spice_pins.py
│  │  ├─ chip_top_klayout_pex_*.spice
│  │  └─ chip_top_magic_pex_*.spice
│  ├─ 📁 pnl/
│  │  └─ chip_top.pnl.v
│  └─ 📁 spice/
│     └─ chip_top.spice
├─ 📁 release/
│  ├─ 📁 v.1.0.0/
│  │  ├─ 📁 doc/
│  │  ├─ 📁 gds/
│  │  ├─ 📁 img/
│  │  └─ ReleaseNote.md
│  └─ 📁 v.2.0.0/
│     ├─ 📁 gds/
│     └─ 📁 netlist/
├─ 📁 render/
│  ├─ 📁 blender/
│  └─ 📁 img/
│     ├─ chip_top_black.png
│     ├─ chip_top_librelane.png
│     └─ chip_top_white.png
├─ 📁 rtl/
│  ├─ chip_core.sv
│  └─ chip_top.sv
├─ 📁 schematic/
│  ├─ chip.sch
│  ├─ chip.sym
│  ├─ chip_top.sch
│  ├─ chip_top.sym
│  ├─ chip_top_pex.sym
│  └─ xschemrc
├─ 📁 scripts/
│  ├─ add_logo_fill.sh
│  ├─ add_rectangle.py
│  ├─ gds_xor.py
│  └─ lay2img.py
├─ 📁 testbenches/
│  ├─ 📁 cocotb/
│  │  ├─ chip_top_tb.gtkw
│  │  ├─ chip_top_tb.surf.ron
│  │  └─ chip_top_tb.py
│  └─ 📁 xschem/
│     ├─ chip_tb_tran.sch
│     ├─ chip_top_tb_tran.sch
│     └─ xschemrc
├─ 📁 verification/
│  ├─ 📁 drc/
│  │  ├─ chip_top.magic.drc.rpt
│  │  └─ chip_top_logo_fill.magic.drc.rpt
│  └─ 📁 lvs/
│     └─ chip_top.lvs.out
├─ Makefile
└─ README.md
```


## Show Available Targets

The default Make target is `help`, so running `make` prints usage and all available targets with short descriptions.

```sh
make
make help
```


## Initialize Git Submodules

Initializes and updates the repository submodules (for example `artistic`):

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

The cocotb simulations generate a waveform file under `testbenches/cocotb/sim_build/chip_top.fst`.
You can view it with a waveform viewer such as [GTKWave](https://gtkwave.github.io/gtkwave/) or [Surfer](https://surfer-project.org/).
The waveform viewer can be changed with `WAVEFORM_VIEWER=<gtkwave|surfer>` (default: `gtkwave`).

```sh
make sim-view-cocotb                                          # view chip_top waveform with GTKWave (default)
make sim-view-cocotb WAVEFORM_VIEWER=surfer                   # use Surfer instead
```

Each cocotb simulation folder contains a pre-configured waveform layout file (`<CELL>_tb.gtkw` for GTKWave, `<CELL>_tb.surf.ron` for Surfer).
The view target loads it automatically together with the current `.fst`, so signal formatting is preserved across runs.

To run all non-interactive simulation targets in sequence (RTL cocotb, GL cocotb, and GL Xschem), use:

```sh
make sim-all
```

> [!NOTE]
> `sim-view-cocotb` is intentionally **not** called by `sim-all`.
> It opens a waveform viewer GUI (GTKWave or Surfer), which blocks the shell until the window is closed.
> It is designed for interactive use and must be called manually after the simulation has completed.


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

To copy the yosys, antenna-violation, DRC errors, hold & setup violation, timing, LVS, and manufacturability reports from the latest run into `flow/reports/`, run:

```sh
make copy-reports
```

This only works if the latest run completed without errors. This command is also available for the digital macros.


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

For each digital macro the following commands are executed: `make librelane`, `make copy-reports`, and `make render-gds`.

> [!TIP]
> Each macro has its own `Makefile` and `README.md` with additional targets, such as linting, simulation, and verification.
> For example, to lint the counter or run its simulation, refer to [macros/counter/README.md](macros/counter/README.md).

### Build Analog Macros

Each analog macro has its own `klayout-verify` and `magic-verify` targets that runs LVS, DRC, and PEX for the top level cell.

To build the inverter macro:

```sh
make build-inverter
```

All analog macros are included in `build-macros` alongside the digital macros.


## Build All

To build the bondpad, logos and macros, run LibreLane for the top-level chip, copy the reports, GDS, netlist, and LibreLane render, add the logo and fill structures, render the final GDS, and open it in the OpenROAD GUI, run:

```sh
make build-all
```

> [!NOTE]
> The `make build-all` target does **not** currently build the digital macros (e.g., counter, inverter).
> To build specific macros, use `make build-counter`, `make build-inverter`, or `make build-macros` to build all enabled macros separately.

This is useful if you want to rebuild the chip from scratch. Clone the repository, enter the IIC-OSIC-TOOLS environment, and run `make build-all`.


## Export Schematic Netlist for LVS

Exports the schematic netlist for LVS from Xschem and places it in `netlist/schematic/`.

The `EV_PRECISION` parameter sets the number of significant digits used by Xschem's `ev` function when calculating device properties (default: 5). Increase this to avoid LVS mismatches caused by floating-point rounding differences between Xschem and KLayout (see [xschem#465](https://github.com/StefanSchippers/xschem/issues/465)).

Currently, KLayout LVS extracts `ntap` and `ptap` devices, so the schematic netlist must include them as well. In contrast, Magic + Netgen LVS does not extract `ntap` and `ptap`. Therefore, the schematic uses `lvs_ignore = short` for these devices and conditional net labels (see [xschem#474](https://github.com/StefanSchippers/xschem/issues/474)). To make this effective during schematic netlist export, `set lvs_ignore 1` must be set in the `magic-lvs-netlist` target.

KLayout uses CDL netlists, while Magic uses SPICE netlists. Accordingly, `klayout-lvs-netlist` uses the Xschem commands `set spiceprefix 1`, `set lvs_netlist 1`, `set top_is_subckt 1`, and `set lvs_ignore 0`. In contrast, `magic-lvs-netlist` uses `set spiceprefix 1`, `set lvs_netlist 0`, `set top_is_subckt 1`, and `set lvs_ignore 1`.

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

Exports the schematic netlist from Xschem, then runs LVS. Compares the GDS layout in `layout/` against the schematic netlist in `netlist/schematic/`. Reports are saved to `verification/lvs/`. The extracted layout netlist is moved to `netlist/layout/`.

**KLayout LVS** uses `run_lvs.py` from the IHP Open-PDK:

```sh
make klayout-lvs
make klayout-lvs CELL=chip_top
```

**Magic + Netgen LVS** uses `sak-lvs.sh`:

```sh
make magic-lvs
make magic-lvs CELL=chip_top
```


## Design Rule Check (DRC)

Runs DRC on the GDS layout in `layout/`. Reports are saved to `verification/drc/`.

**KLayout DRC (minimum)** runs a pre-check KLayout DRC on the final top-level layout with logo and fill structures:

```sh
make klayout-drc-minimum
```

**KLayout DRC (regular)** runs a regular KLayout DRC on the final top-level layout with logo and fill structures:

```sh
make klayout-drc-regular
```

**KLayout DRC** uses `run_drc.py` from the IHP Open-PDK with relaxed rules (FEOL, density checks, and extra rules disabled):

```sh
make klayout-drc
make klayout-drc CELL=chip_top
```

**Magic DRC** uses `sak-drc.sh`:

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
- `1` = C-decoupled
- `2` = C-coupled
- `3` = full-RC (default)

> **Note:** For `klayout-pex`, `EXT_MODE=1` (C-decoupled) is not yet supported by kpex and automatically falls back to `EXT_MODE=2` (CC) with a warning.

The `.subckt` name in the extracted SPICE file is automatically renamed from `<CELL>_flat` (kpex) or `<CELL>` (Magic) to `<CELL>_pex`.

If a matching Xschem symbol (`schematic/<CELL>_pex.sym`) exists, the `.subckt` pin order in the extracted SPICE file is automatically reordered to match the symbol's pin positions. This ensures the PEX netlist can be used directly with the corresponding Xschem symbol for simulation regardless of the selected `EXT_MODE`.

**KLayout PEX** uses `kpex` with the Magic extraction engine currently (2.5D engine is work in progress):

```sh
make klayout-pex
make klayout-pex CELL=chip_top
make klayout-pex CELL=chip_top EXT_MODE=3
```

**Magic PEX** uses `sak-pex.sh`:

```sh
make magic-pex
make magic-pex CELL=chip_top
make magic-pex CELL=chip_top EXT_MODE=3
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


## Build and Verify All

Runs full simulation (`sim-all`), then `build-all`, followed by Magic DRC for both `chip_top` and `chip_top_logo_fill`:

```sh
make all
```


## Release

Copies the final top-level GDS with logo and fill structures from `layout/` to `release/v.<VERSION>/gds/`, copies the generated netlists into `release/v.<VERSION>/netlist/`, and copies the chip renders into `release/v.<VERSION>/img/`.

The following netlist folders are exported:

- `netlist/layout` -> `release/v.<VERSION>/netlist/layout`
- `netlist/pnl` -> `release/v.<VERSION>/netlist/pnl`
- `netlist/spice` -> `release/v.<VERSION>/netlist/spice`

The following chip renders are exported:

- `render/img/chip_top_black.png` -> `release/v.<VERSION>/img/chip_top_black.png`
- `render/img/chip_top_white.png` -> `release/v.<VERSION>/img/chip_top_white.png`
- `render/img/chip_top_librelane.png` -> `release/v.<VERSION>/img/chip_top_librelane.png`

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


## Acknowledgements

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