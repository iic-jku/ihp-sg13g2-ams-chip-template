# ihp-sg13g2 Counter

> [!IMPORTANT]
> This repository requires the [IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS) container with tag `2026.05` or later.

<p align="center">
  <a href="render/img/counter_top_white.png">
    <img src="render/img/counter_top_white.png" alt="Render of the ihp-sg13g2 counter layout (700um x 1130um)" width=50%>
  </a>
  <br>
  <em>Render of the ihp-sg13g2 counter layout (700um x 1130um).</em>
</p>


## Directory Structure

```text
📁 counter/
├─ 📁 final/
│  ├─ 📁 gds/
│  │  └─ counter_top.gds
│  ├─ 📁 lef/
│  │  └─ counter_top.lef
│  ├─ 📁 lib/
│  │  ├─ 📁 nom_fast_1p32V_m40C/
│  │  ├─ 📁 nom_fast_1p65V_m40C/
│  │  ├─ 📁 nom_slow_1p35V_125C/
│  │  ├─ 📁 nom_typ_1p20V_25C/
│  │  └─ 📁 nom_typ_1p50V_25C/
│  ├─ 📁 nl/
│  │  └─ counter_top.nl.v
│  ├─ 📁 pnl/
│  │  └─ counter_top.pnl.v
│  ├─ 📁 spef/
│  │  └─ 📁 nom/
│  └─ 📁 vh/
│     └─ counter_top.vh
├─ 📁 flow/
│  ├─ 📁 final/
│  │  ├─ 📁 def/
│  │  ├─ 📁 gds/
│  │  ├─ 📁 json_h/
│  │  ├─ 📁 klayout_gds/
│  │  ├─ 📁 lef/
│  │  ├─ 📁 lib/
│  │  ├─ 📁 mag/
│  │  ├─ 📁 mag_gds/
│  │  ├─ 📁 nl/
│  │  ├─ 📁 odb/
│  │  ├─ 📁 pnl/
│  │  ├─ 📁 render/
│  │  ├─ 📁 sdc/
│  │  ├─ 📁 sdf/
│  │  ├─ 📁 spef/
│  │  ├─ 📁 spice/
│  │  ├─ 📁 vh/
│  │  ├─ metrics.csv
│  │  └─ metrics.json
│  ├─ 📁 librelane/
│  │  ├─ config.yaml
│  │  ├─ impl.sdc
│  │  ├─ pin_order.cfg
│  │  └─ signoff.sdc
│  └─ 📁 reports/
│     ├─ hold_setup_timing.rpt
│     ├─ lvs.netgen.rpt
│     ├─ manufacturability.rpt
│     ├─ stat.rpt
│     ├─ yosys_post_dff.rpt
│     ├─ yosys_pre_techmap.rpt
│     └─ yosys_synth_check.rpt
├─ 📁 fpga/
│  ├─ Makefile
│  ├─ pico-ice.pcf
│  └─ README.md
├─ 📁 netlist/
│  ├─ 📁 nl/
│  │  └─ counter_top.nl.v
│  ├─ 📁 pnl/
│  │  └─ counter_top.pnl.v
│  ├─ 📁 spice/
│  │  └─ counter_top.spice
│  └─ 📁 xspice/
│     ├─ 📁 counter_top/
│     │  └─ counter_top.xspice
│     ├─ reorder_xspice_pins.py
│     ├─ spi2xspice.py
│     └─ verilog2xspice.sh
├─ 📁 render/
│  ├─ 📁 blender/
│  └─ 📁 img/
│     ├─ counter_top_black.png
│     ├─ counter_top_librelane.png
│     └─ counter_top_white.png
├─ 📁 rtl/
│  ├─ *.sv
│  └─ counter_top.sv
├─ 📁 schematic/
│  ├─ counter_top.sym
│  └─ xschemrc
├─ 📁 scripts/
│  └─ lay2img.py
├─ 📁 testbenches/
│  ├─ 📁 cocotb/
│  │  ├─ counter_top_tb.gtkw
│  │  ├─ counter_top_tb.py
│  │  └─ counter_top_tb.surf.ron
│  ├─ 📁 verilog/
│  │  ├─ counter_top_tb.gtkw
│  │  ├─ counter_top_tb.surf.ron
│  │  └─ counter_top_tb.sv
│  └─ 📁 xschem/
│     ├─ counter_top_tb_tran.sch
│     └─ xschemrc
├─ Makefile
└─ README.md
```


## Show Available Targets

The default Make target is `help`, so running `make` prints usage and all available targets with short descriptions.

```sh
make
make help
```


## Linting

To lint the Verilog/SystemVerilog source files with [Verilator](https://www.veripool.org/verilator/), run:

```sh
make lint-verilog              # lint the full counter_top design
make lint-verilog CELL=dsmod   # lint a single module
make lint-verilog-all          # lint dsmod, cordic_iterative, lo_gen, and counter_top
```

When `CELL=counter_top` (the default), all synthesis sources plus `constants.sv` are passed to Verilator.
For a single cell, the correct extension (`.sv` or `.v`) is detected automatically, and `constants.sv` is always included so opcode and funct constants are in scope.

The `lint-verilog-all` target runs these lint checks in sequence:

1. `make lint-verilog CELL=dsmod`
2. `make lint-verilog CELL=cordic_iterative`
3. `make lint-verilog CELL=lo_gen`
4. `make lint-verilog` (default: `counter_top`)

This is also the lint step used by `make all`.


## Verification and Simulation

We use [cocotb](https://www.cocotb.org/), a Python-based testbench environment, and [Icarus Verilog](https://github.com/steveicarus/iverilog) for the verification of the macro.

The simulation targets are unified and accept an optional `CELL` variable (default: `counter_top`).
The waveform viewer can be changed with `WAVEFORM_VIEWER=<gtkwave|surfer>` (default: `gtkwave`).

### RTL Verilog Simulation

Compiles the RTL with Icarus Verilog and runs the simulation.
When `CELL=counter_top` (the default), the full `COUNTER_MODULES_SIM` source list and the `.sv` testbench are selected automatically.
The waveform is written to `testbenches/verilog/<CELL>/` (e.g. `testbenches/verilog/counter_top/counter_top_tb.vcd`):

```sh
make sim-rtl-verilog              # run counter_top RTL simulation
make sim-rtl-verilog CELL=dsmod   # run dsmod RTL simulation
```

To view the waveform afterwards:

```sh
make sim-view-verilog                                          # view counter_top waveform
make sim-view-verilog CELL=dsmod                               # view dsmod waveform
make sim-view-verilog CELL=dsmod WAVEFORM_VIEWER=surfer        # use Surfer instead
```

Each simulation folder contains a pre-configured waveform layout file (`<CELL>_tb.gtkw` for GTKWave, `<CELL>_tb.surf.ron` for Surfer).
The view target loads it automatically together with the current `.vcd`, so signal formatting is preserved across runs.

### RTL / GL cocotb Simulation

The cocotb testbenches are located in `testbenches/cocotb/`.
For `CELL=dsmod`, the simulation delegates to the sub-Makefile in `testbenches/cocotb/dsmod/` (PSD, SNDR sweep, and ramp tests).
For all other cells the Python runner is invoked directly.

```sh
make sim-rtl-cocotb               # run counter_top RTL cocotb simulation
make sim-rtl-cocotb CELL=dsmod    # run dsmod cocotb test suite
```

See `testbenches/cocotb/dsmod/README.md` for `dsmod`-specific configuration options and environment variables.

To run the gate-level (GL) cocotb simulation:

```sh
make sim-gl-cocotb                # gate-level simulation of counter_top
```

> [!NOTE]
> Gate-level simulation requires the latest implementation in `flow/final/`.

A waveform file is generated under `testbenches/cocotb/<cell>/sim_build/<cell>.fst`.
To view it:

```sh
make sim-view-cocotb                                          # view counter_top waveform
make sim-view-cocotb CELL=dsmod                               # view dsmod waveform
make sim-view-cocotb CELL=dsmod WAVEFORM_VIEWER=surfer        # use Surfer instead
```

Each cocotb simulation folder contains a pre-configured waveform layout file (`<CELL>_tb.gtkw` for GTKWave, `<CELL>_tb.surf.ron` for Surfer).
The view target loads it automatically together with the current `.fst`, so signal formatting is preserved across runs.

### Gate-Level Xschem Simulation

Runs the mixed-signal gate-level transient simulation testbench in `testbenches/xschem/<CELL>_tb_tran.sch`:

```sh
make sim-gl-xschem                # run counter_top gate-level Xschem simulation
make sim-gl-xschem CELL=<cell>    # run gate-level Xschem simulation for another cell
```

> [!NOTE]
> This flow expects the generated XSPICE model in `netlist/xspice/counter_top/`. If needed, generate it first with:
>
> ```sh
> make generate-xspice
> ```


### Run All Simulations

To run all simulation targets in sequence:

```sh
make sim-all
```

This executes the following targets in order:

1. `sim-rtl-verilog CELL=dsmod`
2. `sim-rtl-cocotb CELL=dsmod`
3. `sim-rtl-verilog` (default: `counter_top`)
4. `sim-rtl-cocotb` (default: `counter_top`)
5. `sim-gl-cocotb` (default: `counter_top`)
6. `sim-gl-xschem` (default: `counter_top`)

> [!NOTE]
> The `sim-view-verilog` and `sim-view-cocotb` targets are intentionally **not** called by `sim-all`.
> Both open a waveform viewer GUI (GTKWave or Surfer), which blocks the shell until the window is closed.
> They are designed for interactive use and must be called manually after the simulation has completed.


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


## Copy Important Reports

To copy the yosys, antenna-violation, DRC errors, hold & setup violation, timing, LVS, and manufacturability reports from the latest run into `flow/reports/`, run:

```sh
make copy-reports
```

This only works if at least one LibreLane run exists in `flow/librelane/runs/` and the latest run completed without errors.


## Copy the Final GDS

To copy the latest GDS from `flow/final/gds/` into `final/gds/`, run:

```sh
make copy-gds
```

This assumes the final GDS view exists under `flow/final/gds/`.


## Copy the Final Netlist

To copy the latest SPICE, PnL, and Netlist files from `flow/final/` into `netlist/`, run:

```sh
make copy-netlist
```

This only works if the required final views exist in `flow/final/spice/`, `flow/final/pnl/`, and `flow/final/nl/`.


## Copy the Final Render

To copy the latest LibreLane render from `flow/final/render/` into `render/img/`, run:

```sh
make copy-render
```

This only works if the final render exists in `flow/final/render/`.


## Render Top Layout

Renders the final GDS from `final/gds/` with `scripts/lay2img.py` and saves it in the `render/img/` folder:

```sh
make render-gds
```

This only works if the latest run completed without errors.


## Build FPGA

To build the FPGA design, run:

```sh
make build-fpga
```


## Build All

To build the macro with LibreLane, copy its reports, copy GDS, copy netlists, copy the render, and render the final GDS, run:

```sh
make build-all
```


## Layout Versus Schematic (LVS) & Design Rule Check (DRC)

The LibreLane flow already includes LVS and DRC checks with Magic and KLayout, and they are saved in the flow/reports folder.


## Build and Verify All

Builds and verifies the whole macro by running both simulation and build steps:

- `lint-verilog-all`
- `sim-all`
- `build-all`

The LVS and DRC verification is done within the LibreLane flow.

```sh
make all
```


## Generate XSPICE File

To generate an XSPICE file of the macro for mixed-signal simulation in Xschem, run:

```sh
make generate-xspice
```

> [!NOTE]
> This command should not be run as part of `all`, since this XSPICE file is generated once with specific CPU settings for a more convenient simulation.
> This method does not work with the `.pnl.v` file in `flow/final/`. The `.nl.v` file from the LibreLane step `yosys-synthesis` must be used.
> Conversion pipeline: Copy gate-level Verilog (`.nl.v`) → Verilog with power pins (`.vp`) → SPICE (`.spice`) → XSPICE (`.xspice`) → Reorder pins in XSPICE file according to the Xschem symbol.
