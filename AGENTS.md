# Repository conventions

Guidance for coding agents and contributors working in this repo (a Makefile-driven analog mixed-signal chip on the ihp-sg13g2 Open-PDK).

This repo is the ihp-sg13g2 AMS chip template or a chip copied from it. Items marked (template) describe the shipped example content (the `counter`, `inverter` and `vco` macros, the logos, the tutorial), which a derived chip renames, replaces or removes. `README.md` documents every top-level target, and `macros/README.md` and each `macros/<name>/README.md` document the macro targets.

## Repository layout

- `Makefile`: the chip flow. `make` alone runs `make help`, which lists every target from its `## ` comment and explains the variables (`CELL`, `EXT_MODE`, `DRC_LEVEL`, `TB`, `SCRIPT`, `VERSION` and more).
- `rtl/chip_top.sv` (pad ring) and `rtl/chip_core.sv` (macro instances and glue logic).
- `flow/librelane/`: `config.yaml`, `chip_top.sdc` and `pdn_cfg.tcl` of the chip LibreLane run. `flow/artistic` is a git submodule (ArtistIC logo tool), fetched by `make init-submodules`.
- `macros/<name>/`: one hard macro per folder with its own `Makefile` (`help`, `all`, `clean`, PDK guard) and `README.md`. The chip reads the committed views in `macros/<name>/final/`.
- `macros/counter/` (template, digital): `rtl/`, `flow/librelane/`, `fpga/`, `testbenches/{verilog,cocotb,xschem}/`, hardened with LibreLane.
- `macros/inverter/` (template, analog): `schematic/xschem/`, `layout/`, `testbenches/xschem/`, `verification/cace/`, verified with KLayout and Magic.
- `macros/vco/` (template, RF, under construction): `schematic/xschem/`, `testbenches/xschem/` with ngspice and VACASK benches (a `_vacask` in the testbench name selects VACASK), the coil layout script `scripts/layout/vco_ind.py` (`make klayout-script CELL=vco_ind`), the Palace EM simulation of the coil in `verification/em/` (`make sim-em`), and its snp2le model in `netlist/spice/` and `netlist/spectre/` (`make snp2le`). Not built by the chip yet.
- `macros/Makefile`: one job, `make macro FROM=<macro> NAME=<name>` starts a new macro as a renamed copy of an existing one.
- `ip/`: bondpad `sg13g2_ip__bondpad_70x70` and the logos `sg13g2_ip__jku` and `sg13g2_ip__jku_names` (template), each with a `Makefile`. `ip/sg13g2_io_custom/` is third-party IHP IO cell data.
- `schematic/xschem/`, `testbenches/xschem/`, `testbenches/cocotb/`: chip schematic, symbols and testbenches. Every folder holding schematics has its own `xschemrc`, see "Xschem Configuration" in `README.md`.
- `layout/`, `netlist/`, `verification/`, `render/img/`: build outputs, committed. `packaging/` holds `config.yaml` and `scripts/run_bondplan.py` for `make bondplan` plus their committed outputs. `release/v.<VERSION>/` holds published versions.
- `doc/`: hand-maintained `specifications.md`, `pinout.md` and `floorplan.md` plus tool and PDK notes. A number changed in `flow/librelane/config.yaml`, `rtl/` or `packaging/config.yaml` is mirrored there.
- `tutorial/` (template): the Quarto tutorial, `make -C tutorial` renders it locally.

## Environment and PDK

- Run every target inside the IIC-OSIC-TOOLS container, tag `2026.10` or later. CI uses `hpretl/iic-osic-tools:latest`.
- The PDK is `ihp-sg13g2`, which is also the PDK a fresh container starts on.
- `sak-pdk ihp-sg13g2` selects it for the current shell only. `.designinit` exports the same variables (`PDK`, `PDKPATH`, `STD_CELL_LIBRARY`, `SPICE_USERINIT_DIR`, `KLAYOUT_PATH`), and copied into the container's `designs/` folder it selects the PDK at every start. In a shell that does not keep state between commands, select the PDK in the same command line as `make`.
- PDK guard: the top-level, `macros/`, macro and IP Makefiles compare `$PDK` with `REQUIRED_PDK` (default `ihp-sg13g2`) when parsed and stop with an error that names the `sak-pdk` call to run. Exempt goals are `help` and `clean` (`macros/Makefile`: `help` only), plus `clean-all` at the top level. Fix the PDK instead of passing `REQUIRED_PDK=`: a wrong PDK runs the wrong rule decks, LEFs and cells, and the results still look valid.
- `open`, `sim-view-cocotb`, `librelane-openroad` and `librelane-klayout` open a GUI and block until it closes, so they need the container desktop. `sim-view-xschem` opens windows only when a display is available, headless it just writes the figures.

## Build, simulate, verify

```sh
make help                          # targets and variables
make all                           # build-all, magic-drc of chip_top and chip_top_logo_fill, sim-all, bondplan
make build-all                     # submodules, bondpad, logos, macros, build-top
make build-top                     # librelane-nodrc, copy reports/GDS/netlists/render, add-logo-fill, render-gds
make sim-rtl-cocotb                # chip RTL simulation (cocotb on Icarus Verilog)
make sim-all                       # RTL and gate-level cocotb, gate-level Xschem/ngspice
make klayout-drc-regular           # full KLayout DRC of layout/chip_top_logo_fill.gds.gz
make klayout-verify CELL=<cell>    # KLayout DRC, LVS and PEX of layout/<cell>.gds.gz
make magic-verify CELL=<cell>      # Magic DRC, Magic/Netgen LVS and Magic PEX
make regression                    # the CI smoke test
make -C macros/counter lint-verilog-all     # Verilator lint (template macro)
make -C macros/counter sim-rtl-verilog      # Icarus Verilog testbench
make -C macros/counter sim-rtl-cocotb       # cocotb testbench
make -C macros/counter all                  # lint, FPGA build, LibreLane, Magic PEX, simulations
make -C macros/inverter sim-xschem TB=<tb>  # one Xschem testbench in batch mode (template macro)
make -C macros/inverter all                 # KLayout and Magic DRC/LVS/PEX, LEF/LIB/Verilog stub, simulations, CACE
```

- Start with the narrowest target: lint and RTL simulation before any LibreLane run. CI allows `make regression` up to 360 minutes.
- `make all` and the `build-*` and `copy-*` targets overwrite committed outputs. Check `git status` afterwards and commit outputs only when they belong to the change.
- The Xschem targets netlist in batch mode and run `ngspice -b`, so `plot` commands in a testbench `.control` block do nothing. Testbenches write results with `wrdata` to `testbenches/xschem/plot_simulations/data/`, and `sim-view-xschem` plots them.
- The top-level `sim-gl-xschem` includes `macros/counter/netlist/xspice/counter_top.xspice` (template), which `clean-all` deletes. Run `make build-counter` before it.
- `build-top` runs `librelane-nodrc` on purpose until IHP fixes the `metal1_pin_offgrid` errors (see the comment in `Makefile`). Run DRC separately with `magic-drc`, `klayout-drc-minimum` or `klayout-drc-regular`.

## Conventions

- Makefile targets carry a `## <description>` comment on the rule line (that is what `make help` prints) and a `.PHONY:` line. Overridable variables use `?=` with a `# Override with: make <target> VAR=<value>` comment above them.
- A new target that does not read the PDK goes into `PDK_FREE_GOALS`, every other target inherits the guard.
- Verification and simulation targets take `CELL=<cell>` (default `TOP`) to work on a subcell.
- New macro: run `make macro FROM=<macro> NAME=<name>` in `macros/` (`NAME` is a lowercase identifier), then register it in every place listed under "Register the Macro at the Chip Top-Level" in `macros/README.md`. There is no central macro list. `.gitignore` and `REUSE.toml` already cover `macros/*/`.
- RTL is SystemVerilog. Each file starts with the SPDX lines and a `// Description:` comment. Modules sit between `` `default_nettype none `` and `` `default_nettype wire ``, and macro RTL also has an include guard (`` `ifndef __COUNTER_TOP__ ``).
- Shared constants are `` `define `` macros in `rtl/constants.sv` of the digital macro, not a package, because Yosys 0.64 cannot parse `import pkg::*` in a module header. That file compiles first.
- A digital macro lists its RTL files in four places: `MODULES_SYNTH` and `MODULES_SIM` in its `Makefile`, `VERILOG_FILES` in `flow/librelane/config.yaml`, `DUT_SRCS` in `fpga/dut.mk` and `sources` in `testbenches/cocotb/<TOP>_tb.py`. Keep them in step.
- When the ports of a digital macro change, rebuild its symbol as `macros/README.md` describes (`make symbol-gl`). `symbol-check`, which runs inside `generate-xspice`, rejects pins that no longer match the netlist.
- Analog layout (template `inverter`): `layout/<TOP>.klay.gds` is the KLayout editing source, and `layout/<TOP>.gds` is exported from it with `File > Export Layout For Tapeout` and read by every target. Never hand-edit the exported GDS. Re-export after each layout change and rerun DRC, LVS and PEX.
- Keep the PR boundary box (`prBoundary`, layer `189/0`) around a macro top cell. `make check-boundary` checks it, and the chip build fails without it.
- `<CELL>_pex.sym` is regenerated from `<CELL>.sym` before every extraction, so edit `<CELL>.sym`. Never strip `spectre_format` from a symbol, without it the instances silently drop out of a Spectre/VACASK netlist.

## License headers

- Every new source file (SystemVerilog, Python, shell, Makefile, `.mk`, YAML, Tcl, SDC, workflow) starts with two lines in its own comment syntax, after the shebang if there is one: `SPDX-FileCopyrightText: <year> <holders>` and `SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1`. Copy them from a neighboring file of the same kind.
- Files that cannot carry a comment (GDS, netlists, Xschem files, figures, reports, the root Markdown files) are annotated by path in `REUSE.toml`. A new one outside the existing globs needs an entry there.
- Third-party files keep their original copyright and license (last section of `REUSE.toml`, for example `ip/sg13g2_io_custom/**`). A file adapted from one adds this repo's holders to its existing copyright line, as `flow/librelane/chip_top.sdc` does.

## CI

- `.github/workflows/license-check.yml`: `reuse lint` on every push and pull request to `main`.
- `.github/workflows/regression.yml`: `make regression` in `hpretl/iic-osic-tools:latest` with `PDK=ihp-sg13g2`, nightly at 02:00 UTC (skipped when nothing was committed in the previous 25 hours) and on manual dispatch. It is a tool and flow smoke test with DRC skipped in the chip LibreLane run, not a sign-off. Logs go to the `regression-logs` artifact.
- `.github/workflows/quarto-publish.yml` (template): renders `tutorial/` and publishes it to `gh-pages` on every push to `main`. It installs `tutorial/requirements.txt`, so keep that file while the workflow exists.

## Do not break

- Run `make clean` or `make clean-all` only when asked. Most of what they delete is committed, and the LibreLane runs in `flow/librelane/runs/` are not tracked at all.
- Never hand-edit generated files: the top-level `layout/`, `netlist/` and `verification/`, and per macro `final/`, `netlist/` and `*_pex.sym`. Rerun the target that writes them. Leave `release/` alone, it holds published versions.
- Renaming `TOP` in `Makefile` also needs `DESIGN` in `scripts/add_logo_fill.sh` (step 2 of "Start a New Chip from This Template" in `README.md`) and the `chip_top` file names in `REUSE.toml`.
- The `Makefile` reads `PACKAGE_NAME:` from `packaging/config.yaml` with `sed`, so keep it a plain `key: value` line.

## Writing style

These rules apply to documentation, code comments, commit messages, and pull request descriptions in this repo.

- No em-dashes, no double-hyphen dashes, and no semicolons in prose. Code is exempt. Use commas, colons, periods, or parentheses, and split long sentences instead.
- Plain, factual tone: numbers, paths, and verdicts over adjectives, no filler.
- Never hard-wrap prose at a fixed column. Put each sentence or paragraph on one line and let the editor wrap it. When editing, never reflow neighboring lines.
- Keep comments short and accurate: say what is non-obvious and why, never restate what the code already shows.
- Commits and pull requests carry no AI attribution: no `Co-Authored-By` trailers and no "generated with" lines for any coding agent.
