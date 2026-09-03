# Macros

Every folder here is one macro with its own `Makefile` and `README.md`, following the same conventions as the chip top-level (`make help`, `make all`, `make clean`). The chip builds them through `make build-<macro>` and cleans them through `make clean-all` in the top-level [`Makefile`](../Makefile). The two shipped macros are the two archetypes a new block starts from:

| Macro | Kind | Source of truth | Flow |
| --- | --- | --- | --- |
| [`counter/`](counter/) | digital | SystemVerilog in `rtl/` | Verilator lint, Icarus Verilog and cocotb simulation, LibreLane hardening with DRC and LVS inside the run, XSPICE model for the mixed-signal Xschem simulation, FPGA emulation on three boards |
| [`inverter/`](inverter/) | analog | Xschem schematic and hand-drawn GDS in `layout/` | Four Xschem testbenches, KLayout and Magic DRC, LVS and PEX, LEF, Liberty and Verilog stub export by Magic, CACE characterization |

The `Makefile` in this folder has one job: it starts a new macro as a renamed copy of an existing one.


## Directory Structure

```text
📁 macros/
├─ 📁 counter/                digital macro, see counter/README.md
├─ 📁 inverter/               analog macro, see inverter/README.md
├─ 📁 scripts/
│  └─ rename_gds_cells.py     renames the cells inside a GDS, used by make macro
├─ Makefile
└─ README.md
```


## Makefile Targets

### Show Available Targets

```sh
make help
```


### Start a New Macro from an Existing One

```sh
make macro FROM=<macro> NAME=<name>
```

`FROM` is the macro to copy, `inverter` for an analog block, `counter` for a digital one, or any macro of your own that is already here. `NAME` is the name of the new macro: a lowercase letter followed by lowercase letters, digits or underscores, so that it works as a file name, a GDS cell name and a Verilog module name alike. The top cell follows the convention of the copied macro, so `NAME=amp` gives the cells `amp` and `amp_top` from the inverter, and `NAME=fifo` gives the module `fifo_top` from the counter.

The target refuses to run when `NAME` exists already. Otherwise it does, in this order:

1. Copies every file of `FROM` that git knows about, tracked or untracked but not ignored. LibreLane runs, `sim_build/`, `__pycache__/` and the other ignored build outputs stay behind. Outside a git checkout it falls back to copying the whole folder.
2. Runs `make clean` in the copy, so that the committed build outputs of the copied macro (`final/`, `netlist/`, `render/img/`, the reports) are gone as well.
3. Renames every file and folder whose name carries `FROM`.
4. Replaces `FROM` inside every text file, in its three spellings `inverter`, `Inverter` and `INVERTER`. That covers `TOP` in the `Makefile` and in every `fpga/<board>/Makefile`, `DESIGN_NAME` and `VERILOG_FILES` in `flow/librelane/config.yaml`, the symbol instances and the `.include` lines in the Xschem testbenches, `name:`, `template:` and `script:` in the CACE yaml, the file names in the plot scripts, the module names and include guards in the RTL, and `lib_name` and `lib_path` in the `.klib` library map.
5. Renames the cells inside every GDS in `layout/` with [`scripts/rename_gds_cells.py`](scripts/rename_gds_cells.py). The DRC, LVS and PEX targets pass the file name as the cell name, so the two must match. `<TOP>.klay.gds` references the unit cell from a library that `<TOP>.klay.klib` maps to the unit cell GDS, and that link is stored inside the GDS by library name and cell name, where no text edit reaches it. The script relinks it to the renamed cell of the renamed library, which is what KLayout resolves through its Library Manager plugin when you open the layout afterwards. The geometry does not change, an XOR of every layer against the source is empty.
6. Lists what still carries the old name. `README.md` files and notebooks are left alone on purpose, they describe the copied design rather than reference it, and a blind rename would turn their prose into nonsense. Anything else in that list is something the target could not know about.

The copy is a complete macro that builds as one: `make all` in the new folder passes exactly as it does in the source, because nothing but names has changed. So the copy is the moment to commit, before the real work starts.

For a new analog macro named `amp` and a new digital macro named `fifo`:

```sh
cd macros
make macro FROM=inverter NAME=amp
make macro FROM=counter NAME=fifo
```

> [!NOTE]
> The target runs in the IIC-OSIC-TOOLS container: it needs GNU `find`, `grep`, `sed` and `xargs`, and `klayout` with the PDK technology on `KLAYOUT_PATH` for the GDS step, which the container sets up.


### What Is Left to Do

The new macro still implements the copied design under its new name. What follows is the work the target cannot do.

#### From the Inverter (Analog)

1. Replace the design: the schematics and symbols in `schematic/xschem/`, the layout sources `layout/<NAME>.gds` and `layout/<NAME>_top.klay.gds`, and the export `layout/<NAME>_top.gds`, see [Layout Sources and the Exported Tapeout GDS](inverter/README.md#layout-sources-and-the-exported-tapeout-gds). Keep the box on the `prBoundary` layer (`189/0`) around the top cell and resize it with the macro, `make check-boundary` verifies it.
2. Rewrite the testbenches in `testbenches/xschem/` and the plot scripts in `testbenches/xschem/plot_simulations/` for the new pins and measurements. `make symbol-pex` rebuilds `<CELL>_pex.sym` from the cell symbol, so only the cell symbol needs drawing.
3. Adapt the CACE datasheet `verification/cace/<NAME>.yaml` with its template and script, or delete the CACE folder together with the `sim-cace` line of `sim-all`.
4. The sizing notebook `scripts/sizing/sizing_<NAME>.ipynb` and the figures next to it are specific to the inverter, adapt or delete them.
5. Rewrite `README.md` and `render/blender/README.md`.

#### From the Counter (Digital)

1. Replace the RTL in `rtl/` and adjust `MODULES_SYNTH` and `MODULES_SIM` in the `Makefile` when you add or drop files. `rtl/constants.sv` keeps its name, its macros were renamed with the rest.
2. When the ports change, delete both symbols in `schematic/xschem/` instead of editing them. An edited copy of the counter symbol looks plausible, but `make symbol-check` rejects every pin that no longer matches a port. Harden once, scaffold the symbol from the ports of the hardened design, arrange it, and only then run the full flow:

    ```sh
    make librelane        # harden the new design
    make copy-netlist     # brings netlist/pnl/<TOP>.pnl.v into the tree
    make symbol-gl        # scaffold schematic/xschem/<TOP>.sym from its ports
    xschem schematic/xschem/<TOP>.sym   # rename pins to house style, arrange, draw the body
    make all
    ```

    The symbol has to exist before `generate-xspice` runs, so a `make all` on a macro that has none stops there and says so. Wire the Xschem testbench to the finished symbol afterwards, because its pins are what the testbench connects to by coordinate. See [Build the Xschem Symbol](counter/README.md#build-the-xschem-symbol).
3. Update `CLOCK_PORT` and `DIE_AREA` in `flow/librelane/config.yaml`, the pin placement in `flow/librelane/pin_order.cfg`, and the constraints in `impl.sdc` and `signoff.sdc`.
4. Rewrite the testbenches in `testbenches/verilog/`, `testbenches/cocotb/` and `testbenches/xschem/`, and the plot script in `testbenches/xschem/plot_simulations/`.
5. Update `DUT_SRCS` in `fpga/dut.mk` and the pin constraint file in each `fpga/<board>/` you care about to the ports of the new design. Delete the board folders you do not need, the dispatcher derives its board list from the folders that are there. See [fpga/README.md](counter/fpga/README.md).
6. Rewrite `README.md`, `fpga/README.md` and `render/blender/README.md`.


### Register the Macro at the Chip Top-Level

There is no central macro list. A new macro is added in these places, all relative to the repository root:

1. `Makefile`: a `build-<NAME>` target, its line in `build-macros`, and a `clean` line in `clean-all`.
2. `.gitignore`: the `simulations/` folders of the new macro and, for an analog macro, its CACE outputs. Copy the `macros/inverter` or `macros/counter` lines.
3. `rtl/chip_core.sv`: instantiate the macro.
4. `flow/librelane/config.yaml`: a `MACROS` entry with the view paths (`dir::../../macros/<NAME>/final/...`) and the instance placement. The placement of an analog macro snaps to the Metal3 routing grid, see [doc/floorplan.md](../doc/floorplan.md).
5. `flow/librelane/pdn_cfg.tcl`: a `define_pdn_grid -macro` block when the power pins of the macro are not on the layers of the default grid, see the `inverter_top` blocks at the end of the file.
6. `schematic/xschem/xschemrc`: a `source` line for the `xschemrc` of the new macro, without it the symbols of the macro do not resolve at the chip top-level.
7. `schematic/xschem/chip_top.sch`: place the symbol of the macro.
8. `testbenches/cocotb/chip_top_tb.py`: the `sources` list names the netlist or RTL and the stub of every macro.
9. The documentation: [doc/floorplan.md](../doc/floorplan.md), [doc/specifications.md](../doc/specifications.md), [doc/pinout.md](../doc/pinout.md) when pins change, and the top-level `README.md`.
