# sg13g2_ip__bondpad_70x70

A 70 µm × 70 µm square bondpad for the IHP SG13G2 130 nm CMOS process, generated using the KLayout PCell engine and the `SG13_dev` library.

## Directory Structure

```
sg13g2_ip__bondpad_70x70/
├── Makefile                                # Build automation
├── script/
│   └── bondpad.py                          # KLayout PCell-based bondpad generator
├── final/
│   ├── gds/
│   │   └── sg13g2_ip__bondpad_70x70.gds    # Generated GDSII layout
│   ├── lef/
│   │   └── sg13g2_ip__bondpad_70x70.lef    # LEF macro for place-and-route
│   └── vh/
│       └── sg13g2_ip__bondpad_70x70.v      # Verilog blackbox stub
└── verification/
    └── drc/                                # DRC report
```


## Usage

Build everything (clean, generate bondpad, generate Verilog, run DRC):

```bash
make all
```

### Individual Targets

| Target        | Description                                                                                                          |
| ------------- | -------------------------------------------------------------------------------------------------------------------- |
| `bondpad`     | Generate GDS and LEF via `bondpad.py` (usage: `make bondpad [DIAMETER=<um>] [SHAPE=<square\|octagon\|circle>] [BOTTOM_METAL=<1-6>]`) |
| `verilog`     | Generate Verilog blackbox stub (`inout pad`)                                                                         |
| `klayout-drc` | Run KLayout DRC using `run_drc.py` (usage: `make klayout-drc [CELL=<cellname>]`)                                     |
| `magic-drc`   | Run Magic DRC using `sak-drc.sh` (usage: `make magic-drc [CELL=<cellname>]`)                                         |
| `clean`       | Remove all generated output directories                                                                              |

### Parameters

The following Makefile variables can be overridden:

| Variable       | Default  | Description                                                                                |
| -------------- | -------- | ------------------------------------------------------------------------------------------ |
| `DIAMETER`     | `70.0`   | Bondpad diameter/side length in µm                                                         |
| `SHAPE`        | `square` | Bondpad shape (`square`/`octagon`/`circle`)                                                |
| `BOTTOM_METAL` | `3`      | Lowest metal in the pad stack (`1`=Metal1 .. `5`=Metal5, `6`=TopMetal1). Top is fixed to TopMetal2. |

Example — generate an octagonal 70 µm bondpad starting at Metal2:

```bash
make bondpad DIAMETER=70.0 SHAPE=octagon BOTTOM_METAL=2
```

> **Note:** The SG13_dev `bondpad` PCell expects its bottom-metal parameter as the string choice `'1'..'5'` or `'TM1'`. `bondpad.py` maps the integer `BOTTOM_METAL` (1..6) to that choice automatically, and also writes the matching `OBS` range into the LEF so the GDS and LEF stay consistent.


## Bondpad Generator Script

The `script/bondpad.py` script runs in KLayout batch mode. It:

1. Instantiates the `bondpad` PCell from the `SG13_dev` library
2. Flattens the PCell into a static layout
3. Exports the layout as GDSII
4. Generates a matching LEF file (with `pad` pin on Metal2–TopMetal2 and metal obstruction layers)

The metal stack used for the bondpad covers `Metal3` through `TopMetal2` by default (`BOTTOM_METAL=3`, matching the SG13G2 PDK default). Override `BOTTOM_METAL` to start the stack at a different layer.


## Design Rule Check (DRC)

Runs DRC on the GDS layout in `final/gds/`. Reports are saved to `verification/drc/`.

**KLayout DRC** uses `run_drc.py` from the IHP Open-PDK with relaxed rules (FEOL, density checks, and extra rules disabled):

```sh
make klayout-drc
make klayout-drc CELL=sg13g2_ip__bondpad_70x70
```

**Magic DRC** uses `sak-drc.sh`:

```sh
make magic-drc
make magic-drc CELL=sg13g2_ip__bondpad_70x70
```
