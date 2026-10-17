# ihp-sg13g2 VCO

A 20 GHz LC voltage-controlled oscillator built from CMOS devices only, the RF macro of this template. It is the starting point for RF blocks: next to the analog flow of the [inverter](../inverter/README.md) it carries the RF layer, the EM simulation of the passives with AWS Palace, their lumped-element models from snp2le, and the periodic steady-state, small-signal and noise analyses of VACASK.

> [!NOTE]
> This macro is under construction on the branch `add-rf-macro`. The schematic, its simulations, the coil layout and the EM model of the coil are in place. The layout of the active cells, the post-layout simulation and the chip integration follow, see [Status](#status). The chip top-level does not build it yet.

> [!IMPORTANT]
> The VACASK testbenches need the IIC-OSIC-TOOLS container with tag `2026.10` or later: the oscillator PSS (`oscillator=1`), `pac` and `pnoise` arrived in VACASK after the `2026.09` image.


## Specification

| Parameter | Target | Simulated (TT, 27 C, 1.5 V) |
| --- | --- | --- |
| Oscillation frequency | 20 GHz | 20.60 GHz at `vtune` = 0.75 V |
| Tuning range | 18.5 GHz to 21.5 GHz or wider | 19.60 GHz to 22.15 GHz for `vtune` from 0 V to 1.5 V |
| Tuning gain | | 0.79 GHz/V to 2.19 GHz/V, 2.11 GHz/V at 0.75 V |
| Phase noise | not optimized, reported | -85.3 dBc/Hz at 1 MHz, see [Limitations](#limitations) |
| Output power | -10 dBm or more per output into 50 Ohm | -9.4 dBm |
| Supply | `VDD` = 1.5 V, the chip core supply | 8.7 mA |
| Bias | 100 uA reference current into `ibias_100u` | |
| Power down | `di_en` low turns every current off | |

The simulated values are schematic-level, with the coil model fitted to the EM simulation of the coil's layout (see [EM Simulation of the Coil](#em-simulation-of-the-coil)). Layout parasitics of the active cells will lower the frequency, so the tuning range is centered above 20 GHz on purpose.

This is a simple VCO to learn the RF flow on, not an optimized design. It goes through each step once, from the schematic over the coil's layout, EM simulation and lumped-element model to the oscillator analyses of VACASK. [Limitations](#limitations) lists where it falls short and what a better design would change.


## Circuit

| Cell | Function |
| --- | --- |
| `vco_top` | the macro: bias, core and buffer, and the pins |
| `vco_core` | LC tank and negative resistance: the PMOS current source `Mtop` on the center tap of the coil, the cross-coupled NMOS pair `M1`/`M2`, the varactor array, and the center-tap capacitor `Cct` |
| `vco_ind` | the center-tapped tank coil: the PDK `inductor3` for LVS, the lumped-element model `vco_ind_le` for simulation |
| `vco_var` | the varactor array: three `sg13_hv_svaricap` with `Nx=8` each, gates on the tank, wells on `vtune` |
| `vco_buf` | AC-coupled differential output buffer with 50 Ohm back-termination |
| `vco_bias` | the enable logic and the bias: gate voltages of the core current source and the buffer tail, and the buffer gate bias |

**Core.** The cross-coupled NMOS pair (20 um / 0.13 um each) has its sources on `VSS`, and the PMOS current source `Mtop` (3 mA) feeds the center tap of the coil from `VDD`. This top biasing sets the tank common mode to the gate-source voltage of the pair, about 0.75 V, instead of to `VDD`. That is what the varactor needs: `sg13_hv_svaricap` is an accumulation-mode MOS varactor whose capacitance changes most around 0 V gate-to-well voltage, so with the gates on the tank and the wells on `vtune`, a tune voltage from 0 V to `VDD` sweeps it across that transition. With the center tap on `VDD` the same tune range would only reach the flat accumulation part of the curve. Each tank node swings between about 0.13 V and 1.21 V, so no device sees more than the supply. `Cct` (about 1 pF) shorts the current-source noise at twice the oscillation frequency.

**Coil.** The tank coil is the PDK's center-tapped `inductor3` (TopMetal2 windings, TopMetal1 underpass and feeds) with 2 turns, 4 um width, 4 um spacing, 58 um inner and 82 um outer diameter. Its layout comes from a KLayout Python script, and its EM simulation gives 472 pH differential with a Q of 11.3 at 20 GHz, see [EM Simulation of the Coil](#em-simulation-of-the-coil). The PDK has no SPICE model for it, so `vco_ind` holds two views of the same coil. The PDK device is what KLayout LVS extracts, and every simulation netlist skips it (`spice_ignore` is a `tcleval` of the LVS switch, `spectre_ignore=true`). The lumped-element model `vco_ind_le` is what simulation uses, and the LVS netlist skips it (`lvs_ignore=open`). It is fitted with `make snp2le` to the EM result. Its substrate network returns to the global ground node, so `VSS` has to be the ground of every testbench.

**Varactor.** One `sg13_hv_svaricap` with `Nx=8` measures 31 fF to 21 fF differential (63 fF to 41 fF per tank node) for `vtune` from 0 V to 1.5 V, with a differential Q of 23 to 30 at 20 GHz. The well resistance of the model is about 200 Ohm per varactor. It only carries common-mode current and does not load the differential tank, but its thermal noise reaches the frequency through the tuning gain like noise on `vtune` does.

**Buffer.** A differential pair (24 um / 0.13 um each, 6 mA tail) is AC-coupled to the tank through 150 fF MIM capacitors and biased at `vbg_buf` (about 1.1 V) through 24 kOhm resistors. Each output has a 50 Ohm `rppd` resistor to `VDD`, so the buffer is back-terminated for a 50 Ohm measurement setup, and the load has to be AC-coupled.

**Bias and enable.** The 100 uA reference current enters the diode-connected NMOS `MN0`. `MN1` mirrors it into the diode-connected PMOS `MP1`, which sets the core current through `Mtop` (30:1), and `MBt` in the buffer mirrors `MN0` 60:1. `MP2` mirrors the PMOS reference into `Rg` and the diode `MN3`, which sets `vbg_buf` to a gate-source voltage plus 0.45 V. RC low-pass filters (48 kOhm, 1.35 pF) on the two gate lines keep the reference noise off the tank. `di_en` passes two inverters. Low, it pulls the NMOS gate lines to `VSS` and the PMOS gate line to `VDD`, so every current is off.


## Pins

| Pin | Direction | Function |
| --- | --- | --- |
| `VDD` | inout | supply, 1.5 V |
| `VSS` | inout | ground |
| `ibias_100u` | input | reference current, 100 uA into the macro |
| `di_en` | input | enable, active high |
| `vtune` | input | tuning voltage, 0 V to `VDD` |
| `rf_out_p`, `rf_out_n` | inout | differential RF output, 50 Ohm back-terminated to `VDD`, the load has to be AC-coupled |


## Simulation Results

All results are from the testbenches in [`testbenches/xschem/`](testbenches/xschem/), plotted by `make sim-view-xschem` into [`testbenches/xschem/plot_simulations/figures/`](testbenches/xschem/plot_simulations/figures/).

| Testbench | Simulator | Analyses | Result |
| --- | --- | --- | --- |
| `vco_top_tb_tran` | ngspice | start-up transient, 2 ns | 20.60 GHz, tank 0.13 V to 1.21 V, 212 mVpp per output (-9.5 dBm), 8.7 mA |
| `vco_top_tb_pss_vacask` | VACASK | oscillator PSS, PNOISE, PAC | 20.60 GHz, -9.4 dBm per output at the fundamental, -85.3 dBc/Hz at 1 MHz, K_VCO 2.18 GHz/V at 10 MHz (PAC) |
| `vco_top_tb_tune_vacask` | VACASK | one 1.5 ns transient per tuning voltage | 19.60 GHz to 22.15 GHz for `vtune` from 0 V to 1.5 V |
| `vco_ind_tb_acsp_vacask` | VACASK | ACSP, S-parameters of the coil model from 0 Hz to 60 GHz | 483 pH and Q 11.0 at 20.25 GHz, against 472 pH and Q 11.3 from EM |

The ngspice transient and the VACASK PSS agree on the oscillation frequency within 0.01 %, and the tuning gain from PAC agrees with the slope of the tuning curve within 4 %. A `make sim-all` takes about 2 minutes.


## Directory Structure

<details>
<summary>Show Directory Structure</summary>

```text
📁 vco/
├─ 📁 layout/
│  └─ vco_ind.gds
├─ 📁 netlist/
│  ├─ 📁 layout/
│  ├─ 📁 schematic/
│  ├─ 📁 spectre/
│  │  └─ vco_ind_le.inc
│  └─ 📁 spice/
│     └─ vco_ind_le.spice
├─ 📁 schematic/
│  └─ 📁 xschem/
│     ├─ vco_bias.sch
│     ├─ vco_bias.sym
│     ├─ vco_buf.sch
│     ├─ vco_buf.sym
│     ├─ vco_core.sch
│     ├─ vco_core.sym
│     ├─ vco_ind.sch
│     ├─ vco_ind.sym
│     ├─ vco_ind_le.sym
│     ├─ vco_top.sch
│     ├─ vco_top.sym
│     ├─ vco_var.sch
│     ├─ vco_var.sym
│     └─ xschemrc
├─ 📁 scripts/
│  ├─ 📁 layout/
│  │  └─ vco_ind.py
│  ├─ check_boundary.py
│  └─ check_pex_ports.py
├─ 📁 testbenches/
│  └─ 📁 xschem/
│     ├─ 📁 models/
│     │  ├─ cornerMOShv.lib
│     │  ├─ sg13g2_svaricaphv_mod.lib
│     │  └─ sg13g2_svaricaphv_mod_mismatch.lib
│     ├─ 📁 plot_simulations/
│     │  ├─ 📁 data/
│     │  ├─ 📁 figures/
│     │  ├─ ngspice2python.py
│     │  ├─ plot_vco_ind.py
│     │  ├─ plot_vco_top.py
│     │  └─ vacask2data.py
│     ├─ vco_ind_tb_acsp_vacask.sch
│     ├─ vco_top_tb_pss_vacask.sch
│     ├─ vco_top_tb_tran.sch
│     ├─ vco_top_tb_tune_vacask.sch
│     └─ xschemrc
├─ 📁 verification/
│  ├─ 📁 drc/
│  ├─ 📁 em/
│  │  ├─ 📁 layout/
│  │  │  └─ vco_ind.gds
│  │  ├─ 📁 palace_model/
│  │  │  └─ 📁 vco_ind_data/
│  │  ├─ 📁 s-parameter/
│  │  │  └─ vco_ind.s3p
│  │  └─ 📁 scripts/
│  │     └─ palace_vco_ind.py
│  └─ 📁 lvs/
├─ Makefile
└─ README.md
```

</details>

The layouts of the active cells, the exported views (`final/`) and the layout renders (`render/`) follow, in the same places as in the [inverter](../inverter/README.md#directory-structure).


## Makefile Targets

### Show Available Targets

The default Make target is `help`, so running `make` prints usage and all available targets with short descriptions.

```sh
make
make help
```

All targets that operate on a specific cell accept an optional `CELL=<cellname>` parameter. The default is the top-level cell (`vco_top`).


### PDK Guard

Every target except `help` and `clean` needs the `ihp-sg13g2` PDK and stops at parse time when `$PDK` differs, exactly as in the [inverter](../inverter/README.md#pdk-guard). Switch the PDK with `sak-pdk ihp-sg13g2`.


### Open the Design Files

```sh
make open
make open OPEN_ARGS=--all
```

Opens the design files of this folder in the `sak-open.py` file browser, see [Open the Design Files](../inverter/README.md#open-the-design-files) in the inverter.


### Run Xschem Testbench Simulation

Runs a single Xschem testbench in batch mode: saves the schematic, exports the netlist to `testbenches/xschem/simulations/`, and runs the simulator. The testbench name selects the simulator:

- A name that contains `_vacask` is netlisted in the Spectre format (`xschem set netlist_type spectre`) and run with VACASK.
- Any other name is netlisted in the SPICE format and run with `ngspice -b`, as in the inverter.

```sh
make sim-xschem                              # run the default testbench (vco_top_tb_tran)
make sim-xschem TB=vco_top_tb_pss_vacask     # oscillator PSS, phase noise (PNOISE) and tuning gain (PAC)
make sim-xschem TB=vco_top_tb_tune_vacask    # tuning curve, one transient per tuning voltage
make sim-xschem TB=vco_ind_tb_acsp_vacask    # S-parameters of the coil model (ACSP), to compare with the EM result
```

Both simulators write their results as text tables to `testbenches/xschem/plot_simulations/data/`. ngspice does it with `wrdata` at the end of the `.control` block. VACASK does it with its own postprocess hook: the last line of the control block runs [`vacask2data.py`](testbenches/xschem/plot_simulations/vacask2data.py), which turns the rawfile of every analysis into `data/<TB>_<analysis>.txt` with the column layout of `wrdata`, so the same `ngspice2python.loadngspicecol()` reads both. Since the hook is part of the testbench, the Simulate button of the schematic exports the data as well. The control block starts with `abort always`, so a failed analysis stops VACASK with a nonzero exit code instead of leaving old rawfiles behind for the export.

Things that are specific to these testbenches:

- **The coil model is included by every testbench**, `netlist/spice/vco_ind_le.spice` for ngspice and `netlist/spectre/vco_ind_le.inc` for VACASK, which also declares the `inductor` and `mutual` devices it needs. The ACSP testbench of the coil declares `capacitor` as well, because Xschem declares a device only when a symbol of the schematic uses it.
- **ACSP is VACASK's S-parameter analysis.** Each port is a voltage source and its series resistor, which sets the port impedance, and `ports` lists the pairs in port order.
- **The VACASK testbenches read a patched copy of the HV corner file** from `testbenches/xschem/models/`. The PDK's VACASK model of `sg13_hv_svaricap` keeps an ngspice voltage term `v(2,4)` in its well resistance, which VACASK cannot evaluate. All coefficients of that term are 0, so the copy replaces it by 0 and the model is unchanged. VACASK looks for an include next to the file that names it first, so the copied corner file picks up the patched model next to it and everything else from the PDK.
- **The oscillator PSS runs with `pss_minpts=4000`**, four times the default number of steps per period. At the default the shooting Newton cycles without converging. The tuning curve uses transients rather than one PSS per tuning voltage, see [Limitations](#limitations).
- **The ngspice transient sets `rshunt=1e12`.** The varactor model has a node without a DC path, and without the 1 TOhm shunts the operating point takes more than a minute of gmin stepping.
- **Every testbench kicks the oscillation** with an initial condition on the two tank nodes, since the operating point is the symmetric, unstable solution.


### Plot Xschem Simulation Results

```sh
make sim-view-xschem                       # run the default plotting script (plot_vco_top)
make sim-view-xschem SCRIPT=plot_vco_top
make sim-view-xschem SCRIPT=plot_vco_ind      # the coil, same as make view-em-sim
```

[`plot_vco_top.py`](testbenches/xschem/plot_simulations/plot_vco_top.py) plots whatever the three testbenches of `vco_top` have written to `data/`: the start-up transient, the PSS waveform and output spectrum, the phase noise and the tuning gain from PNOISE and PAC, and the tuning curve, whose frequencies it takes from the zero crossings of the last 0.5 ns of each transient. [`plot_vco_ind.py`](testbenches/xschem/plot_simulations/plot_vco_ind.py) plots the differential inductance and Q and the S-parameters of the coil from the EM result, and from the ACSP testbench next to it once that has run. Both write the figures and CSV files to `testbenches/xschem/plot_simulations/figures/` and open the plot windows when a display is available.


### Simulate All

```sh
make sim-all
```

Runs `vco_top_tb_tran`, `vco_top_tb_pss_vacask` and `vco_top_tb_tune_vacask` in sequence. `sim-view-xschem` is not part of it, because it blocks until the plot windows are closed.


### Generate a Layout with a KLayout Python Script

```sh
make klayout-script CELL=vco_ind
```

Runs `scripts/layout/<CELL>.py` in KLayout batch mode and writes `layout/<CELL>.gds`. So far the coil is the only cell with a script. [`vco_ind.py`](scripts/layout/vco_ind.py) places the PDK's `inductor3` PCell, flattens it into the cell `vco_ind` so the GDS carries no PCell context, adds a `ptap1` substrate tap with the `VSS` label left of the feeds, and labels the feed pins on their metals. The cell passes `make klayout-drc CELL=vco_ind` and `make klayout-lvs CELL=vco_ind`. Three details of the PCell:

- `d` is the inner diameter: 58 um gives the 82 um outer diameter. The PCell centers the octagon in a 142 um by 142 um keep-out (layer `IND` with the no-fill layers and `PWell.block`) and runs the feeds 31 um down to its lower edge, where the pins sit: `LA` and `LB` on TopMetal1 at x = -8 um and 8 um, `LC` on TopMetal2 at x = 0.
- `subE=0`: passed as the boolean `False` from a script, the PCell still draws the backside etch layer `LBE` under the coil.
- The pin labels repeat the PCell's own names in upper case. KLayout LVS names a net after every label on it and fails the strict port check when a net carries both `LA` and `la`. It compares names case-insensitively, so `LA` matches the schematic pin `la`.


### EM Simulation of the Coil

```sh
make sim-em                 # EM layout, Palace model, solve, Touchstone files
make copy-sparam            # copy the result to verification/em/s-parameter/vco_ind.s3p
make view-em-sim            # plot L, Q and the S-parameters, against the model once the ACSP testbench has run
make em-model               # sim-em, copy-sparam, snp2le and the ACSP testbench in one go
make sim-em NP=8            # more MPI processes
```

`sim-em` runs [`palace_vco_ind.py`](verification/em/scripts/palace_vco_ind.py), which builds two things from `layout/vco_ind.gds` with gds2palace:

- **The EM layout** `verification/em/layout/vco_ind.gds`: the coil metals (TopMetal1, TopVia2, TopMetal2) and a Metal1 ground as in the inductor synthesis example of the PDK's Palace flow, a 20 um wide frame half a coil diameter (41 um) away from the windings and a tongue from the frame up under the three feeds. The ports are 50 Ohm lumped ports, vertical sheets from the tongue up to the pin metal at the lower end of each feed pin: port 1 at `LA`, port 2 at `LB`, port 3 at the center tap `LC`, the port order of snp2le's `inductor-ct`.
- **The Palace model** in `verification/em/palace_model/vco_ind_data/`: the PDK stackup `SG13G2_200um.xml` with its 200 um lossy substrate, a sweep from 0 Hz to 60 GHz in 0.75 GHz steps to cover the third harmonic (gds2palace replaces 0 Hz by 10 MHz and 20 MHz), Palace's adaptive frequency sweep, second-order elements and 3 um cells along the conductors.

Palace solves the model, and `combine_extend_snp.py` of the PDK writes `vco_ind.s3p` and three variants of it to `output/vco_ind/`: `_dc` with an extrapolated DC point, and `_deembedded` with the inductance of the vertical ports subtracted. `copy-sparam` takes the raw file, because the vertical port stands for the via stack down to the transistors, which the coil sees in the circuit as well.

**The metals are volumes.** gds2palace models a metal either as a hollow shell with a surface impedance (`surface`, its default) or as a solid with the bulk conductivity of the stackup (`volume`). The coil's traces are 4 um wide and 2 um (TopMetal1) or 3 um (TopMetal2) thick, the case where the surface model is least accurate: it applies the surface impedance to the side walls as well and so counts them as extra cross-section. The differential values at 20.25 GHz:

| Metals | Via fields | Cells in the metals | L | R | Q |
| --- | --- | --- | --- | --- | --- |
| surface | merged | 3 um | 469 pH | 3.61 Ohm | 16.5 |
| volume | merged | 1 um | 472 pH | 4.62 Ohm | 13.0 |
| volume (committed) | fill-factor corrected | 1 um | 472 pH | 5.34 Ohm | 11.3 |
| volume | fill-factor corrected | 0.5 um | 473 pH | 5.26 Ohm | 11.4 |
| volume | fill-factor corrected | 0.5 um | 473 pH | 5.25 Ohm | 11.5 |

The DC resistance shows which one is right. From the drawn lengths and the stackup, the traces have 1.72 Ohm, and the four TopVia2 fields in the current path add 1.1 Ohm (2 x 2 vias each, 1.1 Ohm per via as in the PDK's `sg13g2_typ.itf`). At 10 MHz the committed model gives 2.93 Ohm, while the surface model gives 1.65 Ohm, less than the traces alone. The surface model does reproduce the snp2le example of the same geometry by Volker Muehlhaus, the source of the first coil model (468 pH and Q 16.3 there, 469 pH and Q 16.5 here), so the rest of the setup agrees with the PDK flow. Two more settings follow from the comparison:

- `fill_factor_correction`: gds2palace merges each via array into one block to keep the mesh small. A block of the coil is 2.5 times the area of its vias, so without the correction the four via fields have 40 % of their resistance.
- 1 um cells inside TopMetal1 and TopMetal2, close to the skin depth of TopMetal2 at 20 GHz (0.65 um). Halving them to 0.5 um changes L by 0.1 % and Q by 1.6 %, for twice the unknowns.

The volume model has 2.4 times the unknowns of the surface model (590 k against 250 k). With `NP=4` the sweep takes about 25 minutes and 8 GB of memory, 2 GB per process. The EM layout, the Palace configuration, its outputs and the Touchstone file are committed. The mesh `vco_ind.msh` is not, `sim-em` rebuilds it in a few seconds.


### Lumped-Element Model of the Coil

Fits a lumped-element model to the S-parameters of a passive with [snp2le](https://github.com/iic-jku/snp2le) and writes it for both simulators, `netlist/spice/<EM>_le.spice` (ngspice) and `netlist/spectre/<EM>_le.inc` (VACASK). The `.SUBCKT` name is the file stem, which is also the name of the symbol that instantiates it (`vco_ind_le.sym`).

```sh
make snp2le                                   # fit verification/em/s-parameter/vco_ind.s3p
make snp2le SNP=<file.sNp>                    # fit another Touchstone file
make snp2le EM=<structure> SNP=<file.sNp> LE_MODEL=universal ORDER=8
```

- `EM` names the structure and the output files (default: `vco_ind`).
- `SNP` is the Touchstone file (default: `verification/em/s-parameter/<EM>.s3p`, written by `make copy-sparam`).
- `LE_MODEL` is an snp2le structure, `inductor-ct` for a center-tapped coil (default), `inductor-wideband` or `inductor-pi` for a two-port coil, or `universal` for a vector fit of order `ORDER` (default: 6).

The committed model is fitted with the defaults to the EM result of the drawn coil: two coil segments per half, peak differential Q 13.6 at 40 GHz against 14.1 in the data. `make sim-xschem TB=vco_ind_tb_acsp_vacask` and `make view-em-sim` compare it with the EM data. From 1.5 GHz to 40 GHz the model is within 3 % of the EM inductance and within 4 % of its Q. At 20 GHz it is 2.3 % high in inductance (483 pH against 472 pH), which lowers the oscillation frequency by about 1 %, and 8 % low at 60 GHz. A fit band up to 45 GHz (`--fmax 45GHz`) brings 20 GHz to 1.2 % but the third harmonic to -15 %, so the default stays.


### Layout, Verification and Build

The layout targets are those of the [inverter](../inverter/README.md) and work the same way once `layout/` holds the cells: `klayout-drc`, `magic-drc`, `klayout-lvs`, `magic-lvs`, their `*-lvs-netlist` exporters, `symbol-pex`, `klayout-pex`, `magic-pex`, `klayout-verify`, `magic-verify`, `check-boundary`, `lef`, `lib`, `verilog`, `copy-gds`, `render-gds` and `build-top`. Two things differ:

- **Magic does not extract the PDK inductor**, so `magic-verify-all` covers `vco_bias`, `vco_buf` and `vco_var`, while `klayout-verify-all` covers every cell.
- **A parasitic extraction of a cell that contains the coil is not its RF model.** RC extraction misses the coil's inductance and its coupling: KPEX turns `vco_ind` into a single 42 fF capacitor. `klayout-verify-all` therefore runs only DRC and LVS on `vco_ind`, and the post-layout model of the core will combine the extraction of the active devices with the EM model of the coil and its leads.

Today `layout/` holds the coil: `make klayout-drc CELL=vco_ind` and `make klayout-lvs CELL=vco_ind` pass. The LVS netlist exporters `make klayout-lvs-netlist CELL=<cell>` and `make magic-lvs-netlist CELL=<cell>` work for every cell.


### Verify, Build and Simulate All

```sh
make all
```

Runs `klayout-verify-all`, `magic-verify-all`, `build-top` and `sim-all`, as in the inverter. It needs the layout, so on this branch only `sim-all` runs through.


### Clean

`make clean` deletes the generated files: `final/`, `netlist/schematic/`, `netlist/layout/`, `netlist/pex/`, `render/img/`, the DRC and LVS reports, the Xschem `simulations/` folders and the `plot_simulations/` outputs. The EM results in `verification/em/` and the lumped-element models in `netlist/spice/` and `netlist/spectre/` stay, because an EM run takes half an hour.

> [!WARNING]
> Most of these outputs are committed in this repository, so `make clean` leaves a deletion set in `git status`. Run `git restore .` to get them back if you did not mean to remove them.


## Limitations

This VCO is kept simple on purpose. These are the places where it falls short, and what a better design would change:

- **Phase noise** is -85.3 dBc/Hz at 1 MHz, where 20 GHz CMOS LC oscillators in the literature reach about -105 dBc/Hz to -115 dBc/Hz. PNOISE puts 92 % of it on the bias chain of the core current source (`Rp`, `MN0`, `MP1`, `MN1`) and 0.2 % on the coil. The cause is the top biasing: the core current sets the tank common mode, which is the varactor's gate voltage, so the frequency pushes by about -300 MHz/mA and any current noise becomes frequency noise. In the first simulations, ten times the resistance and four times the capacitance in both bias filters (476 kOhm, 5.4 pF) lowered the phase noise by about 14 dB, but the 2.6 us time constant keeps the frequency settling for about 10 us after every disturbance, and the oscillator PSS then no longer converges reliably. A center tap held at a regulated voltage removes the coupling at its source. After that the tank Q sets the limit, and the coil's Q of 11 at 20 GHz is low: wider traces and fewer turns raise it.
- **The oscillator PSS is fragile.** With these filters it converges at the nominal tuning voltage, but not at every tuning voltage with the same settings, which is why the tuning curve uses transients. Slow states (the bias filters, the AC coupling of the buffer, the DC blocks of the load) make the shooting Newton overshoot.
- **PNOISE and PAC are pinned below about 0.6 MHz.** The tuning gain from PAC is flat at 2.18 GHz/V above 3 MHz and falls below 1 MHz, and the phase noise flattens there too. More harmonics (`truncharm` 20, 40, 60) change nothing. So read the phase noise from about 1 MHz up (at 1 MHz it is about 1.3 dB optimistic), and check it against a transient-noise simulation.


## Status

The macro is built in steps, each one reviewed before the next:

- [x] Folder structure, `Makefile` and `README.md`
- [x] Schematics of all cells, LVS netlists exported for KLayout and Magic
- [x] Testbenches: start-up transient (ngspice), oscillator PSS with PNOISE and PAC, and the tuning curve (VACASK)
- [x] Layout of the coil, generated as a KLayout Python script from the PDK `inductor3`, DRC and LVS clean
- [x] EM simulation of the drawn coil with Palace (gds2palace, volume metals) and its snp2le model, checked with ACSP
- [ ] Corners (TT, SS, FF, supply and temperature), enable and power-up transient
- [ ] More RF analyses: transient noise as the cross-check of PNOISE, HB, HBAC and HBNOISE on the buffer, ACSP of the buffer
- [ ] Layout of the active cells, one per method: hand-drawn in KLayout, generated with GDSFactory, and a KLayout Python script
- [ ] DRC, LVS and PEX of every cell, post-layout simulation with the EM model of the coil
- [ ] Chip integration: the 20 GHz output needs RF pads or a divider to an existing pad, and the coil occupies both TopMetal layers of the chip power grid
- [ ] Tutorial chapter after the analog macro


## Start a New RF Macro from This One

`make macro FROM=vco NAME=<name>` in [`macros/`](../) copies and renames this macro as for the other two, see [Start a New Macro from an Existing One](../README.md#start-a-new-macro-from-an-existing-one).
