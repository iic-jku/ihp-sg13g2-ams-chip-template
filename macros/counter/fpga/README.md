# ihp-sg13g2 RISC-V FPGA Flow

> [!IMPORTANT]
> This flow is intended to run inside the `ihp130/macros/riscv/fpga/` directory and requires an FPGA toolchain with `iverilog`, `yosys`, `nextpnr-ice40`, `icepack`, and `dfu-util`.
>
> The default synthesis flow targets iCE40 (`TARGET=synth_ice40`).

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


## Simulation

RTL simulation is performed with Icarus Verilog.

Build and run the simulation:

```sh
make simulation
```

To only build the simulation executable:

```sh
make test_pre
```


## Lint

Run Verilator lint checks:

```sh
make lint
```


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
> `make all` includes `flash_bitstream`, so it will attempt to program the FPGA.


## Convert to Verilog

Convert the SystemVerilog top module to Verilog:

```sh
make convert
```


## Build All

Run the complete FPGA flow (simulation, synthesis, place-and-route, bitstream generation, and flashing):

```sh
make all
```
