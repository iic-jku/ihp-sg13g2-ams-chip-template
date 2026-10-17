# ihp-sg13g2 VCO

A 20 GHz LC voltage-controlled oscillator built from CMOS devices only, the RF macro of this template. It is the starting point for RF blocks: next to the analog flow of the [inverter](../inverter/README.md) it carries the RF layer, the EM simulation of the passives with AWS Palace, their lumped-element models from snp2le, and the periodic steady-state, small-signal and noise analyses of VACASK.

> [!NOTE]
> This macro is under construction on the branch `add-rf-macro`. The schematic and its simulations are in place. The layout, the EM model of the drawn coil, the post-layout simulation and the chip integration follow, see [Status](#status). The chip top-level does not build it yet.

> [!IMPORTANT]
> The VACASK testbenches need the IIC-OSIC-TOOLS container with tag `2026.10` or later: the oscillator PSS (`oscillator=1`), `pac` and `pnoise` arrived in VACASK after the `2026.09` image.


## Specification

| Parameter | Target | Simulated (TT, 27 C, 1.5 V) |
| --- | --- | --- |
| Oscillation frequency | 20 GHz | 20.69 GHz at `vtune` = 0.75 V |
| Tuning range | 18.5 GHz to 21.5 GHz or wider | 19.73 GHz to 22.18 GHz for `vtune` from 0 V to 1.5 V |
| Tuning gain | | 0.8 GHz/V to 2.05 GHz/V, 1.9 GHz/V at 0.75 V |
| Phase noise | -100 dBc/Hz or better at 1 MHz | -84.9 dBc/Hz, missed, see [Open Issues](#open-issues) |
| Output power | -10 dBm or more per output into 50 Ohm | -8.6 dBm |
| Supply | `VDD` = 1.5 V, the chip core supply | 8.9 mA |
| Bias | 100 uA reference current into `ibias_100u` | |
| Power down | `di_en` low turns every current off | |

The simulated values are schematic-level, with the tank coil from an EM simulation of the same coil geometry (see [Circuit](#circuit)). Layout parasitics will lower the frequency, so the tuning range is centered above 20 GHz on purpose.


## Circuit

| Cell | Function |
| --- | --- |
| `vco_top` | the macro: bias, core and buffer, and the pins |
| `vco_core` | LC tank and negative resistance: the PMOS current source `Mtop` on the center tap of the coil, the cross-coupled NMOS pair `M1`/`M2`, the varactor array, and the center-tap capacitor `Cct` |
| `vco_ind` | the center-tapped tank coil: the PDK `inductor3` for LVS, the lumped-element model `vco_ind_le` for simulation |
| `vco_var` | the varactor array: three `sg13_hv_svaricap` with `Nx=8` each, gates on the tank, wells on `vtune` |
| `vco_buf` | AC-coupled differential output buffer with 50 Ohm back-termination |
| `vco_bias` | the enable logic and the bias: gate voltages of the core current source and the buffer tail, and the buffer gate bias |

**Core.** The cross-coupled NMOS pair (20 um / 0.13 um each) has its sources on `VSS`, and the PMOS current source `Mtop` (3 mA) feeds the center tap of the coil from `VDD`. This top biasing sets the tank common mode to the gate-source voltage of the pair, about 0.75 V, instead of to `VDD`. That is what the varactor needs: `sg13_hv_svaricap` is an accumulation-mode MOS varactor whose capacitance changes most around 0 V gate-to-well voltage, so with the gates on the tank and the wells on `vtune`, a tune voltage from 0 V to `VDD` sweeps it across that transition. With the center tap on `VDD` the same tune range would only reach the flat accumulation part of the curve. Each tank node swings between about 0.08 V and 1.35 V, so no device sees more than the supply. `Cct` (about 1 pF) shorts the current-source noise at twice the oscillation frequency.

**Coil.** The tank coil is the PDK's center-tapped `inductor3` (TopMetal2 windings, TopMetal1 underpass) with 2 turns, 4 um width, 4 um spacing and 82 um inner diameter: about 470 pH differential with a Q of about 16 at 20 GHz. The PDK has no SPICE model for it, so `vco_ind` holds two views of the same coil. The PDK device is what KLayout LVS extracts, and every simulation netlist skips it (`spice_ignore` is a `tcleval` of the LVS switch, `spectre_ignore=true`). The lumped-element model `vco_ind_le` is what simulation uses, and the LVS netlist skips it (`lvs_ignore=open`). Until the EM simulation of the drawn coil exists, the model is fitted with `make snp2le` to a Palace simulation of the same geometry by Volker Muehlhaus, shipped with snp2le as `ind_ct_n2_d82_w4_s4_ihp-sg13g2.s3p`. Its substrate network returns to the global ground node, so `VSS` has to be the ground of every testbench.

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
| `vco_top_tb_tran` | ngspice | start-up transient, 2 ns | 20.69 GHz, tank 0.08 V to 1.35 V, 239 mVpp per output (-8.4 dBm), 8.9 mA |
| `vco_top_tb_pss_vacask` | VACASK | oscillator PSS, PNOISE, PAC | 20.69 GHz, -8.6 dBm per output at the fundamental, -84.9 dBc/Hz at 1 MHz, K_VCO 1.99 GHz/V at 10 MHz (PAC) |
| `vco_top_tb_tune_vacask` | VACASK | one 1.5 ns transient per tuning voltage | 19.73 GHz to 22.18 GHz for `vtune` from 0 V to 1.5 V |

The ngspice transient and the VACASK PSS agree on the oscillation frequency within 0.01 %, and the tuning gain from PAC agrees with the slope of the tuning curve within 3 %. A `make sim-all` takes about 4 minutes.


## Directory Structure

<details>
<summary>Show Directory Structure</summary>

```text
📁 vco/
├─ 📁 netlist/
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
│     │  ├─ plot_vco_top.py
│     │  └─ vacask2data.py
│     ├─ vco_top_tb_pss_vacask.sch
│     ├─ vco_top_tb_tran.sch
│     ├─ vco_top_tb_tune_vacask.sch
│     └─ xschemrc
├─ Makefile
└─ README.md
```

</details>

The layout (`layout/`), the exported views (`final/`), the layout renders (`render/`), the verification reports (`verification/`) and the EM simulation (`verification/em/`) follow with the layout, in the same places as in the [inverter](../inverter/README.md#directory-structure).


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
```

Both simulators write their results as text tables to `testbenches/xschem/plot_simulations/data/`. ngspice does it with `wrdata` at the end of the `.control` block. VACASK does it with its own postprocess hook: the last line of the control block runs [`vacask2data.py`](testbenches/xschem/plot_simulations/vacask2data.py), which turns the rawfile of every analysis into `data/<TB>_<analysis>.txt` with the column layout of `wrdata`, so the same `ngspice2python.loadngspicecol()` reads both. Since the hook is part of the testbench, the Simulate button of the schematic exports the data as well. The control block starts with `abort always`, so a failed analysis stops VACASK with a nonzero exit code instead of leaving old rawfiles behind for the export.

Things that are specific to these testbenches:

- **The coil model is included by every testbench**, `netlist/spice/vco_ind_le.spice` for ngspice and `netlist/spectre/vco_ind_le.inc` for VACASK, which also declares the `inductor` and `mutual` devices it needs.
- **The VACASK testbenches read a patched copy of the HV corner file** from `testbenches/xschem/models/`. The PDK's VACASK model of `sg13_hv_svaricap` keeps an ngspice voltage term `v(2,4)` in its well resistance, which VACASK cannot evaluate. All coefficients of that term are 0, so the copy replaces it by 0 and the model is unchanged. VACASK looks for an include next to the file that names it first, so the copied corner file picks up the patched model next to it and everything else from the PDK.
- **The oscillator PSS runs with `pss_minpts=4000`**, four times the default number of steps per period. At the default the shooting Newton cycles without converging. The tuning curve uses transients rather than one PSS per tuning voltage, see [Open Issues](#open-issues).
- **The ngspice transient sets `rshunt=1e12`.** The varactor model has a node without a DC path, and without the 1 TOhm shunts the operating point takes more than a minute of gmin stepping.
- **Every testbench kicks the oscillation** with an initial condition on the two tank nodes, since the operating point is the symmetric, unstable solution.


### Plot Xschem Simulation Results

```sh
make sim-view-xschem                       # run the default plotting script (plot_vco_top)
make sim-view-xschem SCRIPT=plot_vco_top
```

[`plot_vco_top.py`](testbenches/xschem/plot_simulations/plot_vco_top.py) plots whatever the three testbenches have written to `data/`: the start-up transient, the PSS waveform and output spectrum, the phase noise and the tuning gain from PNOISE and PAC, and the tuning curve, whose frequencies it takes from the zero crossings of the last 0.5 ns of each transient. It writes the figures and CSV files to `testbenches/xschem/plot_simulations/figures/` and opens the plot windows when a display is available.


### Simulate All

```sh
make sim-all
```

Runs `vco_top_tb_tran`, `vco_top_tb_pss_vacask` and `vco_top_tb_tune_vacask` in sequence. `sim-view-xschem` is not part of it, because it blocks until the plot windows are closed.


### Lumped-Element Model of the Coil

Fits a lumped-element model to the S-parameters of a passive with [snp2le](https://github.com/iic-jku/snp2le) and writes it for both simulators, `netlist/spice/<EM>_le.spice` (ngspice) and `netlist/spectre/<EM>_le.inc` (VACASK). The `.SUBCKT` name is the file stem, which is also the name of the symbol that instantiates it (`vco_ind_le.sym`).

```sh
make snp2le                                   # fit verification/em/s-parameter/vco_ind.s3p
make snp2le SNP=<file.sNp>                    # fit another Touchstone file
make snp2le EM=<structure> SNP=<file.sNp> LE_MODEL=universal ORDER=8
```

- `EM` names the structure and the output files (default: `vco_ind`).
- `SNP` is the Touchstone file (default: `verification/em/s-parameter/<EM>.s3p`, written by the EM flow that follows with the layout).
- `LE_MODEL` is an snp2le structure, `inductor-ct` for a center-tapped coil (default), `inductor-wideband` or `inductor-pi` for a two-port coil, or `universal` for a vector fit of order `ORDER` (default: 6).

The committed model was fitted to the snp2le example of the same coil geometry:

```sh
make snp2le SNP=/usr/local/lib/python3.12/dist-packages/snp2le/examples/ind_ct_n2_d82_w4_s4_ihp-sg13g2.s3p
```


### Layout, Verification and Build

The layout targets are those of the [inverter](../inverter/README.md) and work the same way once `layout/` holds the cells: `klayout-drc`, `magic-drc`, `klayout-lvs`, `magic-lvs`, their `*-lvs-netlist` exporters, `symbol-pex`, `klayout-pex`, `magic-pex`, `klayout-verify`, `magic-verify`, `check-boundary`, `lef`, `lib`, `verilog`, `copy-gds`, `render-gds` and `build-top`. Two things differ:

- **Magic does not extract the PDK inductor**, so `magic-verify-all` covers `vco_bias`, `vco_buf` and `vco_var`, while `klayout-verify-all` covers every cell.
- **A parasitic extraction of a cell that contains the coil is not its RF model.** RC extraction misses the coil's inductance and its coupling, so the post-layout model of the core will combine the extraction of the active devices with the EM model of the coil and its leads.

The LVS netlist exporters run today: `make klayout-lvs-netlist CELL=<cell>` and `make magic-lvs-netlist CELL=<cell>` export every cell to `netlist/schematic/`.


### Verify, Build and Simulate All

```sh
make all
```

Runs `klayout-verify-all`, `magic-verify-all`, `build-top` and `sim-all`, as in the inverter. It needs the layout, so on this branch only `sim-all` runs through.


### Clean

`make clean` deletes the generated files: `final/`, `netlist/schematic/`, `netlist/layout/`, `netlist/pex/`, `render/img/`, the DRC and LVS reports, the Xschem `simulations/` folders and the `plot_simulations/` outputs. The lumped-element models in `netlist/spice/` and `netlist/spectre/` stay, because they are fitted to EM data that `make clean` cannot regenerate.

> [!WARNING]
> Most of these outputs are committed in this repository, so `make clean` leaves a deletion set in `git status`. Run `git restore .` to get them back if you did not mean to remove them.


## Open Issues

These are the findings of the first simulations, to be decided in the review:

- **Phase noise misses the target by 15 dB**, -84.9 dBc/Hz at 1 MHz. PNOISE puts 94 % of it on the bias chain of the core current source (`Rp`, `MN0`, `MP1`, `MN1`) and less than 2 % on the core devices. The cause is the top biasing: the core current sets the tank common mode, which is the varactor's gate voltage, so the frequency pushes by about -300 MHz/mA and any current noise becomes frequency noise. Ten times the resistance and four times the capacitance in both bias filters (476 kOhm, 5.4 pF) improved it to -98.5 dBc/Hz, but the 2.6 us time constant keeps the frequency settling for about 10 us after every disturbance, and the oscillator PSS then no longer converges reliably. A center tap held at a regulated voltage would remove the coupling at its source.
- **The oscillator PSS is fragile.** With these filters it converges at the nominal tuning voltage, but not at every tuning voltage with the same settings, which is why the tuning curve uses transients. Slow states (the bias filters, the AC coupling of the buffer, the DC blocks of the load) make the shooting Newton overshoot.
- **PNOISE and PAC are pinned below about 0.6 MHz.** The tuning gain from PAC is flat at 1.99 GHz/V above 3 MHz and falls below 1 MHz, and the phase noise flattens there too. More harmonics (`truncharm` 20, 40, 60) change nothing. So read the phase noise from about 1 MHz up (at 1 MHz it is about 1 dB optimistic), and check it against a transient-noise simulation.


## Status

The macro is built in steps, each one reviewed before the next:

- [x] Folder structure, `Makefile` and `README.md`
- [x] Schematics of all cells, LVS netlists exported for KLayout and Magic
- [x] Coil model from the snp2le example of the same geometry
- [x] Testbenches: start-up transient (ngspice), oscillator PSS with PNOISE and PAC, and the tuning curve (VACASK)
- [ ] Phase noise to target (see [Open Issues](#open-issues)), then corners (TT, SS, FF, supply and temperature), enable and power-up transient
- [ ] More RF analyses: transient noise as the cross-check of PNOISE, HB, HBAC and HBNOISE on the buffer, ACSP of the coil model and the buffer
- [ ] Layout of the coil, generated as a KLayout Python script from the PDK `inductor3`
- [ ] EM simulation of the drawn coil with Palace (gds2palace) and its snp2le model, replacing the example data
- [ ] Layout of the active cells, one per method: hand-drawn in KLayout, generated with GDSFactory, and a KLayout Python script
- [ ] DRC, LVS and PEX of every cell, post-layout simulation with the EM model of the coil
- [ ] Chip integration: the 20 GHz output needs RF pads or a divider to an existing pad, and the coil occupies both TopMetal layers of the chip power grid
- [ ] Tutorial chapter after the analog macro


## Start a New RF Macro from This One

`make macro FROM=vco NAME=<name>` in [`macros/`](../) copies and renames this macro as for the other two, see [Start a New Macro from an Existing One](../README.md#start-a-new-macro-from-an-existing-one).
