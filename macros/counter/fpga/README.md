# ihp-sg13g2 counter FPGA Flow

> [!IMPORTANT]
> This flow is intended to run inside the `ihp-sg13g2-ams-chip-template/macros/counter/fpga/` directory and requires an FPGA toolchain with `verilator`, `yosys`, `nextpnr-ice40`, `icepack`, `dfu-util`, `netlistsvg`, `svgo`, and `rsvg-convert`.
>
> The default synthesis flow targets iCE40 (`TARGET=synth_ice40`).

The FPGA flow uses RTL sources from `../rtl/` (`counter.sv`, `counter_top.sv`, `constants.sv`).

## Show Available Targets

The default Make target is `help`, so running `make` prints usage and all available targets with short descriptions.

```sh
make
make help
```


## Clean

Remove generated files:

```sh
make clean
```


## Lint

Run Verilator lint checks:

```sh
make lint-verilog
make lint-verilog CELL=counter
make lint-verilog-all
```

`make lint-verilog` defaults to `CELL=counter_top` and checks `constants.sv`, `counter.sv`, and `counter_top.sv`.
`make lint-verilog CELL=counter` checks the standalone `counter` cell together with `constants.sv`.
`make lint-verilog-all` runs both lint checks in sequence.


## Synthesis

Run technology-mapped synthesis for iCE40:

```sh
make synthesis
```

Use a custom Yosys synthesis command by overriding `TARGET`:

```sh
make synthesis TARGET=synth_ice40
```

Generate a generic synthesis netlist and Yosys graph:

```sh
make synthesis_generic
```


## Netlist Visualization

Generate a PDF from the iCE40 synthesized netlist:

```sh
make visualize_ice40
```

Generate a PDF from the generic synthesized netlist:

```sh
make visualize_generic
```


## Place-and-Route

Run place-and-route with nextpnr:

```sh
make pr
```

Run place-and-route in GUI mode:

```sh
make pr-gui
```

The constraints file used by this flow is `pico-ice.pcf`.


## Bitstream Generation and Flash

Generate a bitstream:

```sh
make gen_bitstream
```

Flash the generated bitstream:

```sh
make flash_bitstream
```

> [!NOTE]
> `flash_bitstream` is intentionally not part of `make all`.
> Use `make flash_bitstream` explicitly when you want to program the FPGA.


## Convert to Verilog

Convert the SystemVerilog top module to Verilog:

```sh
make convert
```


## Build All

Run the full FPGA flow target from the Makefile:

```sh
make all
```

The current `all` recipe executes these steps in order:

1. `make lint-verilog-all`
2. `make synthesis`
3. `make pr`
4. `make gen_bitstream`

> [!NOTE]
> `make all` intentionally stops after bitstream generation and does not call `flash_bitstream`.
