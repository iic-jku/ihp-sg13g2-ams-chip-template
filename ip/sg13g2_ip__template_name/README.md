# sg13g2_ip__template_name

A text logo reading `SG13G2 TEMPLATE`, for the bottom-left corner of the chip, rendered as a GDSII layout on a configurable metal layer (default `Metal5`) with `NoMetFiller` for the IHP SG13G2 130 nm CMOS process.

## Directory Structure

<details>
<summary>Show Directory Structure</summary>

```text
📁 sg13g2_ip__template_name/
├─ Makefile                             # Build automation
├─ 📁 logo/
│  └─ template_name.png                 # Source PNG image
├─ 📁 script/
│  └─ img2lay.py                        # PNG-to-GDS converter
├─ 📁 final/
│  ├─ 📁 gds/
│  │  └─ sg13g2_ip__template_name.gds   # Generated GDSII layout
│  ├─ 📁 lef/
│  │  └─ sg13g2_ip__template_name.lef   # LEF macro for place-and-route
│  ├─ 📁 lib/
│  │  └─ sg13g2_ip__template_name.lib   # Liberty timing stub
│  └─ 📁 vh/
│     └─ sg13g2_ip__template_name.vh    # Verilog blackbox stub
└─ 📁 verification/
   └─ 📁 drc/                           # DRC reports
```

</details>


## Usage

The default Make target is `help`, so running `make` prints usage and all available targets with short descriptions.

```bash
make
make help
```

Build everything (clean, generate logo GDS, LEF, Liberty, Verilog stub, run DRC):

```bash
make all
```

### PDK Guard

Every target except `help` and `clean` needs the `ihp-sg13g2` PDK. A wrong `$PDK`, for example `ihp-sg13cmos5l` from the sibling CMOS5L template, splits the IP across two technologies: `img2lay.py` resolves the `LAYER` name through the layer properties of the active PDK, and `sak-drc.sh` runs the DRC against its rule deck, while the metal stack the logo is meant for is the SG13G2 one. The Makefile therefore compares `$PDK` against `REQUIRED_PDK` once when it is parsed, before any target runs:

```bash
$ make all
Makefile:21: *** PDK is "ihp-sg13cmos5l", but this IP needs "ihp-sg13g2". Run `sak-pdk ihp-sg13g2` in this shell and retry, or pass REQUIRED_PDK= to skip this check.  Stop.
```

The check is a parse-time conditional at the top of the Makefile, not a prerequisite of each target. Switch the PDK with `sak-pdk ihp-sg13g2`, pass `REQUIRED_PDK=` to skip the check, or `REQUIRED_PDK=<pdk>` to require a different PDK.


### Individual Targets

| Target        | Description                                              |
|---------------|----------------------------------------------------------|
| `logo`        | Convert PNG to GDSII using `img2lay.py`                  |
| `lef`         | Generate LEF macro (CLASS BLOCK, OBS on `$(LAYER)`) |
| `lib`         | Generate Liberty timing stub (empty cell)                |
| `verilog`     | Generate Verilog blackbox stub (no ports)                |
| `klayout-drc` | Run KLayout DRC using `sak-drc.sh` (usage: `make klayout-drc [CELL=<cellname>] [DRC_LEVEL=<precheck\|macro\|regular>] [DRC_JOBS=<n>]`) |
| `magic-drc`   | Run Magic DRC using `sak-drc.sh` (usage: `make magic-drc [CELL=<cellname>]`)                                         |
| `gdscheck-drc` | Run gdscheck DRC using `sak-drc.sh` (usage: `make gdscheck-drc [CELL=<cellname>] [DRC_LEVEL=<precheck\|macro\|regular>] [GDSCHECK_SUITE=<suite>\|GDSCHECK_DECKS=<decks>] [DRC_JOBS=<n>]`) |
| `open`        | Browse this folder with `sak-open.py` and open each file in its tool      |
| `clean`       | Remove all generated output directories                  |

### Parameters

The following Makefile variables can be overridden:

| Variable      | Default  | Description                                                                           |
|---------------|----------|---------------------------------------------------------------------------------------|
| `BLOCK_SIZE`  | `100`    | Block edge in µm, the image is scaled to it                                           |
| `PIXEL_SIZE`  | `0.25`   | Pixel size in µm (must be ≥ 0.21 µm, the Metal5 minimum space, single pixels and single-pixel gaps are drawn as is) |
| `LAYER`       | `Metal5` | Metal layer the logo is drawn on, one of `Metal1`..`Metal5`, `TopMetal1` or `TopMetal2` |

Setting `LAYER` keeps the GDS artwork (`logo` target) and the LEF obstruction (`lef` target) consistent. The `logo` target hands the name to `img2lay.py`, which resolves it through the PDK's KLayout layer properties (`Metal5` is `67/0`), and the `lef` target writes the same name into the `OBS`.

```sh
make all LAYER=TopMetal1
```

The image is scaled to `BLOCK_SIZE`, so the GDS boundary and the LEF `SIZE` always agree.


## Logo Generator Script

The `script/img2lay.py` script converts a PNG image into a GDSII layout:

- Each horizontal run of dark pixels becomes a rectangle on the layer selected via `LAYER` (default `Metal5`, resolved to `67/0`)
- Boundary layers `prBoundary` (189/0) and `NoMetFiller` (160/0) mark the block outline
- Layers are given as `<layer>/<datatype>` or as a drawing-layer name of the active PDK, read from `$PDK_ROOT/$PDK/libs.tech/klayout/tech/<pdk>.lyp`
- `--invert` inverts the image (dark ↔ light)
- `--merge` merges the rectangles into polygons to reduce the polygon count
- `--pixel-size` sets the physical size of each pixel in µm
- `--block-size` scales the image to the given block edge in µm and draws the boundary layers at that size
- `--scale` downscales the image by a plain factor instead


## Design Rule Check (DRC)

Runs DRC on the GDS layout in `final/gds/`. All three flows use `sak-drc.sh` and write their reports into per-cell run folders: `verification/drc/<CELL>.magic.drc/` (Magic), `verification/drc/<CELL>.klayout.drc/` (KLayout, `.lyrdb`) and `verification/drc/<CELL>.gdscheck.drc/` (gdscheck, `.lyrdb`).

**KLayout DRC** uses `sak-drc.sh` at the selected `DRC_LEVEL` (`precheck`, `macro` [default], or `regular`), with at most `DRC_JOBS` processes (default: 4, or the CPU count if lower):

```sh
make klayout-drc
make klayout-drc CELL=sg13g2_ip__template_name
make klayout-drc DRC_LEVEL=regular
```

**Magic DRC** uses `sak-drc.sh`. `make all` leaves it out until the foundry cells of the chip are clean in Magic:

```sh
make magic-drc
make magic-drc CELL=sg13g2_ip__template_name
```

**gdscheck DRC** runs the standalone [gdscheck](https://github.com/aesc-silicon/gdscheck) engine (`sak-drc.sh -g`). `DRC_LEVEL` selects its suite (`precheck`, `core` for the default `macro`, or `main` for `regular`) and `GDSCHECK_SUITE` replaces it, or `GDSCHECK_DECKS` runs single rule decks instead, see the [top-level README](../../README.md#design-rule-check-drc). `make all` runs it:

```sh
make gdscheck-drc
make gdscheck-drc CELL=sg13g2_ip__template_name
```
