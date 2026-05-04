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

| Target    | Description                                  |
| --------- | -------------------------------------------- |
| `bondpad` | Generate GDS and LEF via `bondpad.py`        |
| `verilog` | Generate Verilog blackbox stub (`inout pad`) |
| `drc`     | Run IHP DRC checks using `run_drc.py`        |
| `clean`   | Remove all generated output directories      |

### Parameters

The following Makefile variables can be overridden:

| Variable   | Default  | Description                        |
| ---------- | -------- | ---------------------------------- |
| `DIAMETER` | `70.0`   | Bondpad diameter/side length in µm |
| `SHAPE`    | `square` | Bondpad shape (`square`/`octagon`/`circle`)  |

Example — generate a octagon 70 µm bondpad:

```bash
make bondpad DIAMETER=70.0 SHAPE=octagon
```


## Bondpad Generator Script

The `script/bondpad.py` script runs in KLayout batch mode. It:

1. Instantiates the `bondpad` PCell from the `SG13_dev` library
2. Flattens the PCell into a static layout
3. Exports the layout as GDSII
4. Generates a matching LEF file (with `pad` pin on Metal2–TopMetal2 and metal obstruction layers)

The metal stack used for the bondpad covers Metal2 through TopMetal2, with the `bottom_metal` parameter set to index 1 (Metal2) by default.


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
