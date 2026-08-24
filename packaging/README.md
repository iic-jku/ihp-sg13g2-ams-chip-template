# Packaging

## Automated Bondplan Generation

The bondplan (die placed in the package cavity + all bondwires + pin table)
is generated fully automatically by [scripts/run_bondplan.py](scripts/run_bondplan.py), driven by [config.yaml](config.yaml). The config is structured like a LibreLane `config.yaml`: flat `UPPER_CASE` keys, `dir::` paths relative to the config file, and placement as `location` / `orientation`. No new config style to learn. `{design}` in any value expands to `DESIGN_NAME`, so file and cell names follow a rename automatically.

### Requirements

- KLayout Python module (`pya`) and PyYAML. Both available out of the box in the [IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS) container.
- The die GDS with `Passiv` pad openings and pad name labels (`TopMetal2.text`), e.g. the final chip layout `../layout/chip_top_logo_fill.gds.gz`.
- The EUROPRACTICE package library GDS (`layout/EP_PACKAGES_08022018.gds`, download link under Useful Links). A pre-made package GDS with lead frame polygons and pin number texts works as well.

### Quick Start

```bash
make bondplan                        # from the repository root
make bondplan VERSION=2.1.0          # override the version
```

or directly:

```bash
cd packaging
python3 scripts/run_bondplan.py config.yaml VERSION=1.0.0
```

Any config key can be overridden with `KEY=VALUE` on the command line. The Makefile passes its `VERSION` this way, so the version number lives in the Makefile only and never has to be maintained in `config.yaml`. It is available as the `{version}` placeholder (used in the `Die` title block field).

### Directory Structure

| Path | Content |
|---|---|
| `config.yaml` | flow configuration incl. the full pinout |
| `scripts/run_bondplan.py` | the flow (plain Python, KLayout `pya` API) |
| `layout/` | package library (input) + generated package / bondplan / die-extract GDS |
| `render/` | generated PNG / SVG images |
| `result.md` | generated bond report (summary + bond table) |

### Package Library

The package sheet does not need to be prepared by hand. Point `PACKAGE_LIBRARY_GDS` at the EUROPRACTICE master drawing and pick a `PACKAGE_NAME`. The flow copies that sheet cell into `PACKAGE_GDS` (dropping the template paper layer 207/0) and auto-detects the lead frame cell inside it:

```yaml
PACKAGE_LIBRARY_GDS: dir::layout/EP_PACKAGES_08022018.gds
PACKAGE_NAME: OP_QFN32_A4_FIT
# PACKAGE_GDS: ...              # default: <library dir>/<PACKAGE_NAME>.gds
```

Supported packages in `EP_PACKAGES_08022018.gds`, with a lead frame and numbered pins on layers 210/211 (the `_FIT` variants are scaled to fit the A4 print):

| `PACKAGE_NAME` | Pins | Lead frame cell |
|---|---|---|
| `OP_QFN16_A4` / `OP_QFN16_A4_FIT` | 16 | `OP_QFN16` |
| `OP_QFN24_A4` / `OP_QFN24_A4_FIT` | 24 | `OP_QFN24` |
| `OP_QFN32_A4` / `OP_QFN32_A4_FIT` | 32 | `OP_QFN32` |
| `OP_QFN48_A4` / `OP_QFN48_A4_FIT` | 48 | `OP_QFN48` |
| `OP_QFN56_A4` / `OP_QFN56_A4_FIT` | 56 | `OP_QFN56` |
| `OP_SOIC16_A4` | 16 | `OP_SOIC16` |

The library's remaining drawings (DIL, CLCC, CPGA, CERQUAD, and the larger QFN/SOIC variants) use older drawing conventions without a machine-readable lead frame and are rejected with a descriptive error.

Infeasible configurations abort with clear messages: an unknown `PACKAGE_NAME` (the error lists all available cells), a `PINOUT` pin number beyond the package's pin count, a package drawing without a usable lead frame, and a die that (with its `DIE_PLACEMENT`) does not fit into the package inner area.

### How the Flow Works

1. **Extract**: reads the die layout GDS with a layer map so only `DIE_EXTRACT_LAYERS` (Passiv, TopVia2, TopMetal2) are loaded and writes the lightweight die view `DIE_EXTRACT_GDS` (top cell renamed to `DIE_EXTRACT_CELL`).
2. **Detect die pads**: merged `Passiv` (9/0) openings larger than `DIE_PAD_MIN_SIZE` are the bondpads. Their names come from the `TopMetal2.text` (134/25) labels placed on the pad centers by LibreLane. No LEF file is needed.
3. **Analyze the package**: inside the lead frame cell (auto-detected, or set via `PACKAGE_FOOTPRINT_CELL`) the lead polygons (210/0) and the pin number texts (211/0) are read. Each pin number is matched to its nearest lead. The bond point lies on the ray from the package center through the lead (`BONDWIRE_LEAD_SITE`: 0 = lead tip, 1 = outer end). The package *inner border* (the square touching the lead tips) is derived from the lead geometry.
4. **Place the die**: `DIE_PLACEMENT.location` is the lower-left corner of the (oriented) die outline relative to the lower-left corner of the inner border. Omit it to center the die. `orientation` accepts the LibreLane/DEF values `N/S/E/W/FN/FS/FE/FW`.
5. **Draw the bondwires**: `PINOUT` maps each package pin to a die pad name. Wires are `BONDWIRE_WIDTH` wide paths on `BONDWIRE_LAYER` (`Exchange0.drawing - 190/0`, a documentation-only layer, nothing in the PDK consumes it). A bond table (`pin pad`) is written on `BONDWIRE_TEXT_LAYER` next to the plan. In sheet mode the lead frame is shifted automatically so that plan and table sit inside the drawing frame with equal side margins. The package pin numbers are re-drawn centered on their wire attach points, just outside the package outline (`PACKAGE_PIN_LABEL_OFFSET`).
6. **Check & export**: wire lengths (`BONDWIRE_MAX_LENGTH`), wire crossings, the minimum wire-to-wire gap, the landing skew of each wire on its lead (`BONDWIRE_MAX_SKEW`) and guard clearances (see below) are checked and reported. Outputs are the bondplan GDS, a bond report and zero-border PNG / SVG images in `_white` / `_black` variants (following the `sak-render.py` naming convention). The report (`BONDPLAN_REPORT`) is a Markdown summary plus a bond table with per-wire length, bearing, lead skew and minimum gap. A `.csv` extension writes raw CSV instead.

### Pinout Format

```yaml
PINOUT:
  1:  "clk_PAD"                 # pin 1 -> die pad labeled clk_PAD
  7:  "IOVDD"                   # duplicate names (VDD/VSS/...) are
  8:  "VDD"                     #   resolved by shortest-wire assignment
  16: ["VSS", "VSS"]            # a list = several wires to one lead
  17: ~                         # ~ (null) = NC pin
  EPAD: ["VSS", "IOVSS"]        # downbonds to the exposed pad (GND),
                                #   drawn parallel to neighbouring wires
```

Unlisted pins are reported as NC. Unbonded named pads are reported too, so a forgotten connection is visible in the log.

### Guarded Wires

Sensitive (e.g. RF) wires can be marked as *guarded*. The checker then warns if any other bondwire comes closer than `GUARD_SPACING`:

```yaml
GUARDED_PINS: [[17, 18, 19, 20]]  # pins or [groups], where wires within
GUARD_SPACING: 60                 #   one group are exempt from each other
```

Grouping matters for differential pairs / quads or analog channels: the analog wires above (`analog_PAD[0..3]`, the inverter2 channels) may sit close to *each other* by design, but nothing else should crowd them.

### Drawing Sheet / Title Block

With `SHEET_KEEP: true` the EUROPRACTICE A4 drawing frame stays in the bondplan GDS, and `SHEET_FIELDS` fills in its title block. Keys match the label texts on the sheet (case and colon insensitive). Values are written right next to the label and may use computed placeholders:

```yaml
SHEET_KEEP: true
SHEET_FIELDS:
  Request: "JKU IICQC - {design}"
  Date: "{date}"
  Die: "{design}"
  "Size incl scribe": "{die_width_mm} x {die_height_mm} mm"
  "Max. wire length": "{max_wire_length_mm} mm"
  Taped: {value: "X", dx: 500}    # mapping form: manual placement offset
```

Available placeholders: `{design}` `{date}` `{wire_count}` `{bondwire_width_um}` `{max_wire_length_um}` / `{max_wire_length_mm}` `{min_wire_length_um}` `{min_gap_um}` `{die_width_um/mm}` `{die_height_um/mm}` `{pad_pitch_um}` `{pad_opening_um}`. Set `IMAGE_REGION: full` to render the whole sheet (cropped to the frame border). With `package` only the footprint and the bond table are rendered.

Further sheet options:

```yaml
LID: Glued                        # X into the Taped/Sealed/Glued/Glass box
SHEET_TEXT_SCALE:                 # shrink/grow the sheet's own texts
  "QFN32(5x5)": 0.7
SHEET_NOTES: []                   # optional free-text lines, stacked below
SHEET_NOTES_ANCHOR: "Extra Info"  #   the anchor label
```

`Glued` is the standard lid for open-molded plastic packages (OmPP): the die sits in an open cavity and the cover is glued on after wire bonding. *Die Attach* is the material fixing the die onto the paddle. Conductive epoxy connects the die backside to the exposed pad (GND).

#### Computed vs. manual title block values

Everything reachable via a `{placeholder}` is **derived from the layouts and the generated bondplan** on every run and can never go stale:

| Placeholder | Source |
|---|---|
| `{die_width_mm}` / `{die_height_mm}` (Size incl scribe) | die GDS bounding box |
| `{pad_pitch_um}`, `{pad_opening_um}` | detected `Passiv` bondpad openings |
| `{max_wire_length_mm}`, `{min_wire_length_um}`, `{wire_count}`, `{min_gap_um}` | the generated bondwires / checker |
| `{bondwire_width_um}` | `BONDWIRE_WIDTH` |
| `{design}`, `{date}` | `DESIGN_NAME`, system date |
| `{version}` | `VERSION`, passed on the command line by the Makefile |

The remaining fields are **manual entries**, assembly decisions the layout cannot know: `Request`, `MPW`, `Die-thickness`, `Qty packaged`, `Qty naked`, `Die Attach`, the wire material, the `LID` choice and any free-text notes.

### Options Overview

Every key has a sensible default. A minimal config only needs `DIE_GDS`, `DIE_EXTRACT_LAYERS`, `DIE_EXTRACT_GDS`, a package (`PACKAGE_LIBRARY_GDS` + `PACKAGE_NAME`, or a pre-made `PACKAGE_GDS`), `BONDPLAN_GDS` and `PINOUT`. The most useful knobs:

| Key (default) | Effect |
|---|---|
| `DIE_CELL` / `PACKAGE_CELL` (top cell) | select cells explicitly |
| `PACKAGE_LIBRARY_GDS` / `PACKAGE_NAME` (off) | generate `PACKAGE_GDS` from the EUROPRACTICE package library |
| `PACKAGE_FOOTPRINT_CELL` (auto-detect) | cell with the lead/pin geometry, if auto-detection needs overriding |
| `PACKAGE_DELETE_TEXTS` ([]) | glob patterns of sheet texts to remove when generating the package (e.g. `"Updated by *"` for the template revision note) |
| `DIE_PAD_MIN_SIZE` (40 um) | Passiv openings smaller than this are ignored |
| `DIE_PLACEMENT` (centered, N) | die position/orientation in the cavity |
| `BONDWIRE_WIDTH` (25 um) | drawn wire width |
| `BONDWIRE_LEAD_SITE` (0.5) | where wires land on the lead (0 = tip, 1 = outer end) |
| `BONDWIRE_MAX_LENGTH` (3500 um) | length check threshold |
| `BONDWIRE_MAX_SKEW` (30 deg) | max wire angle vs. lead axis before warning |
| `GUARDED_PINS` ([]) / `GUARD_SPACING` (100 um) | clearance check around sensitive wires |
| `EPAD_WIRE_LENGTH` (500 um) | length of exposed-pad downbond stubs |
| `PACKAGE_PIN_LABEL_OFFSET` (250 um) | pin number distance outside the package outline |
| `PACKAGE_PIN_LABEL_SIZE` (from sheet) / `TABLE_TEXT_SIZE` (100 um) | font sizes of pin numbers / bond table |
| `TABLE_GAP` (400 um) | gap between plan and bond table (side margins stay equal automatically) |
| `BONDPLAN_TEXT_POLYGONS` (true) | convert texts to polygon glyphs so they scale in images and prints (the stroke font is uppercase-only) |
| `BONDPLAN_DELETE_LAYERS` ([]) | layers stripped from the output GDS |
| `SHEET_KEEP` (false) / `SHEET_FIELDS` ({}) | keep the drawing frame and fill its title block |
| `BONDPLAN_PNG` / `BONDPLAN_SVG` (off) | image export targets |
| `IMAGE_WIDTH` (2000 px), `IMAGE_OVERSAMPLING` (2) | image quality |
| `IMAGE_REGION` (`package`) | `package` = footprint + bond table, `full` = everything |

### Porting to another Package / Chip

The flow is not specific to this template chip. For a different chip or package you need: a die GDS with labeled `Passiv` pad openings, a package GDS whose footprint cell contains one lead polygon per pin plus numeric pin texts, and an updated `PINOUT`. Everything else (pad/lead detection, inner border, placement, checks, rendering) is derived from the geometry.

## Useful Links

- SERMA: https://www.serma-microelectronics.com/en/
- factronix: https://www.factronix.com/
- Plastic Open-Pak Packages, Open-molded Plastic Package (OmPP): https://www.qptechnologies.com/products/ompp/
- EUROPRACTICE - ASIC Packaging - Overview: https://europractice-ic.com/services/packaging/asic-packaging/
- EUROPRACTICE - ASIC Packaging - DRC: https://europractice-ic.com/wp-content/uploads/2020/06/ASIC_Prototype_Packaging_Design_Rules_2024.pdf
- EUROPRACTICE - ASIC Packaging - QFN-48: https://europractice-ic.com/wp-content/uploads/2019/06/MLP7X7-48-OP-02-R2-ECN-10501.pdf
- EUROPRACTICE - ASIC Packaging - GDS: https://europractice-ic.com/wp-content/uploads/2019/07/EP_PACKAGES_08022018.gds_.gz
- Take the DXF file from here: https://www.mirrorsemi.com/OpenChip.html and use https://www.artwork.com/gdsii/asm3500/windows/interface.htm to get the GDS file.