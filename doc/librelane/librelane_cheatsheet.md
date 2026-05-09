# LibreLane Cheatsheet

## LibreLane Final Directory Structure Explanation

The `final` directory in a LibreLane (or OpenLane-based) ASIC design flow contains the "golden" output files produced after the hardening process. These files represent various views of the design—from logical netlists to the final physical layout ready for manufacturing.

### 1. Physical Layout
* **`gds/`**: Contains the **GDSII** (.gds) file. This is the industry-standard binary format for the final integrated circuit layout, used for "tape out" and sent to the foundry for fabrication.
* **`mag/`**: Contains **Magic** layout files (.mag). These are native to the Magic VLSI tool, used for DRC (Design Rule Checking) and GDS generation.
* **`mag_gds/`**: Contains GDS files specifically generated or processed by the Magic tool.
* **`klayout_gds/`**: Contains GDS files optimized or generated for **KLayout**, often including extra metadata for easier visual debugging.

### 2. Design Exchange & Abstraction
* **`lef/`**: Contains **Library Exchange Format** files. These are "abstract" views containing pin locations and blockages used by placement and routing tools without revealing internal transistor geometry.
* **`def/`**: Contains **Design Exchange Format** files. A text-based representation of the physical design, including cell placement, power grids, and routing.

### 3. Netlists & Circuit Views
* **`nl/`**: Stands for **Netlist**. Contains the gate-level Verilog netlist produced after synthesis.
* **`pnl/`**: Stands for **Powered Netlist**. A Verilog netlist that includes explicit connections for power ($V_{DD}$) and ground ($V_{SS}$), critical for LVS (Layout vs. Schematic) checks.
* **`vh/`**: Contains **Verilog Headers**. Structural Verilog files used for hierarchy management or inclusion in other simulation environments.
* **`spice/`**: Contains **SPICE** netlists (.spice). Used for transistor-level simulations and as the primary reference for LVS to ensure the layout matches the electrical circuit.
* **`json_h/`**: Contains **Yosys JSON Headers**. A machine-readable version of the netlist used by internal LibreLane Python scripts for analysis.

### 4. Timing, Parasitics & Constraints
* **`sdc/`**: Contains **Synopsys Design Constraints** (.sdc). Defines timing requirements like clock periods, input/output delays, and false paths.
* **`spef/`**: Contains **Standard Parasitic Exchange Format** files. Represents the resistance and capacitance (parasitics) of the metal wires extracted from the layout.
* **`sdf/`**: Contains **Standard Delay Format** files. Used in gate-level simulations to annotate exact timing delays.
* **`lib/`**: Contains **Liberty** timing files (.lib). Provides timing, power, and area models for the design, treating it as a "macro" for higher-level integration.

### 5. Databases & Metrics
* **`odb/`**: Contains **OpenDB** (.odb) files. The internal binary database format for **OpenROAD**, combining LEF and DEF data for tool efficiency.
* **`metrics.json`**: A comprehensive summary of results (cell count, area, power, timing slack, DRC/LVS violations) in JSON format.
* **`metrics.csv`**: A spreadsheet-compatible version of the design metrics for tracking and comparison.


## Non-Default Rules (NDR)

Introduced in [PR #869](https://github.com/librelane/librelane/pull/869). Useful for routing non-critical analog nets with wider widths/spacings.

### 1. `NON_DEFAULT_RULES`

**Step:** `OpenROAD.DetailedRouting`  
**Type:** `Optional[dict[str, NDR]]`

Defines one or more non-default rules. Each rule (keyed by its name) has three fields:

| Field | Type | Description |
|---|---|---|
| `width` | `List[str]` | Wire width. Can be a **single value** (applies to all layers), a **multiplier** like `*3` (multiplies default width by 3), or **layer/value pairs** like `[Metal1, 0.42, Metal2, 0.42, ...]`. |
| `spacing` | `List[str]` | Wire spacing. Same format as `width`: single value, multiplier (`*3`), or layer/value pairs. |
| `via` | `Optional[List[str]]` | Allowed vias for this rule, e.g. `[Cont, Via1, Via2, TopVia1]`. If omitted or set to `None`, default vias are used. |

#### Example

```yaml
NON_DEFAULT_RULES:
  ndr_2x:
    width: "*2"
    spacing: "*2"
  ndr_custom:
    width: [Metal1, "0.42", Metal2, "0.42", Metal3, "0.9"]
    spacing: [Metal1, "0.51", Metal2, "0.42", Metal3, "0.9"]
    via: [Cont, Via1, Via2]
```

### 2. `DRT_ASSIGN_NDR`

**Step:** `OpenROAD.DetailedRouting`  
**Type:** `Optional[dict[str, str]]`

Assigns nets to previously defined non-default rules. The net name is matched as a **regular expression**. Use `^name$` for exact matching.

#### Example

```yaml
DRT_ASSIGN_NDR:
  "^clk$": ndr_2x
  "analog_.*": ndr_custom
```

### 3. `CTS_APPLY_NDR`

**Step:** `OpenROAD.CTS`  
**Type:** `Literal["none", "root_only", "half", "full"]`  
**Default:** `"half"`

Controls automatic 2x-spacing NDR application to clock nets. Passed directly to OpenROAD's `clock_tree_synthesis -apply_ndr` flag.

| Value | Behavior |
|---|---|
| `none` | No NDR applied to clock nets. |
| `root_only` | NDR applied only to the root of the clock tree. |
| `half` | NDR applied to the upper half of the clock tree (excluding leaf-level nets). **This is the default.** |
| `full` | NDR applied to all clock tree nets except leaf-level nets. |

#### Example

```yaml
CTS_APPLY_NDR: full
```

### Important Notes

> **Note:** NDR cannot block routing on a specific layer. By omitting a specific layer (e.g. Metal1), default rules apply there. The router may still use this specific layer for short connections.

### Via Types in IHP SG13G2

The IHP SG13G2 technology LEF (`sg13g2_tech.lef`) defines three categories of vias: **cut layers**, **fixed via definitions**, and **GENERATE via rules** (for automatic arrays).

#### Metal Stack

| Layer | Direction | Min Width | Pitch | Thickness | DC Current Density |
|---|---|---|---|---|---|
| Metal1 | Horizontal | 0.16 µm | 0.42 µm | 0.40 µm | 1 mA/µm |
| Metal2 | Vertical | 0.20 µm | 0.48 µm | 0.45 µm | 2 mA/µm |
| Metal3 | Horizontal | 0.20 µm | 0.42 µm | 0.45 µm | 2 mA/µm |
| Metal4 | Vertical | 0.20 µm | 0.48 µm | 0.45 µm | 2 mA/µm |
| Metal5 | Horizontal | 0.20 µm | 0.42 µm | 0.45 µm | 2 mA/µm |
| TopMetal1 | Vertical | 1.64 µm | 3.28 µm | 2.0 µm | 15 mA/µm |
| TopMetal2 | Horizontal | 2.0 µm | 4.0 µm | 3.0 µm | 16 mA/µm |

#### Cut Layer Properties

| Cut Layer | Connects | Cut Size | Min Spacing | Resistance | DC Current (per cut) |
|---|---|---|---|---|---|
| Cont | GatPoly → Metal1 | 0.16 µm | 0.18 µm | 22 Ω | — |
| Via1 | Metal1 → Metal2 | 0.19 µm | 0.22 µm | 20 Ω | 0.4 mA |
| Via2 | Metal2 → Metal3 | 0.19 µm | 0.22 µm | 20 Ω | 0.4 mA |
| Via3 | Metal3 → Metal4 | 0.19 µm | 0.22 µm | 20 Ω | 0.4 mA |
| Via4 | Metal4 → Metal5 | 0.19 µm | 0.22 µm | 20 Ω | 0.4 mA |
| TopVia1 | Metal5 → TopMetal1 | 0.42 µm | 0.42 µm | 4 Ω | 1.4 mA |
| TopVia2 | TopMetal1 → TopMetal2 | 0.9 µm | 1.06 µm | 2.2 Ω | 10 mA |

#### Fixed Via Definitions

Fixed vias have pre-defined geometry (metal enclosures and cut positions). They are used by the NDR `via` field and as fallback when GENERATE rules cannot be applied.

##### Single-Cut Vias (Via1–Via4)

Each via layer (Via1 through Via4) has 9 single-cut variants with different metal enclosure orientations.

**Naming convention:** `ViaN_AB[_s]`

- `N` = via layer number (1–4)
- `A` = enclosure direction of the metal **below** (`X` = horizontal, `Y` = vertical)
- `B` = enclosure direction of the metal **above** (`X` = horizontal, `Y` = vertical)
- `_s` = wider (symmetric) enclosure on the metal above

| Via | Below Encl. | Above Encl. | Notes |
|---|---|---|---|
| `ViaN_XX` | Horizontal | Horizontal | Both metals extend in X |
| `ViaN_XX_s` | Horizontal | Horizontal (wide) | Wider above-metal enclosure |
| `ViaN_XY` | Horizontal | Vertical | Cross-direction transition |
| `ViaN_XY_s` | Horizontal | Vertical (wide) | Wider above-metal enclosure |
| `ViaN_YX` | Vertical | Horizontal | Cross-direction transition |
| `ViaN_YX_s` | Vertical | Horizontal (wide) | Wider above-metal enclosure |
| `ViaN_YY` | Vertical | Vertical | Both metals extend in Y |
| `ViaN_YY_s` | Vertical | Vertical (wide) | Wider above-metal enclosure |
| `ViaN_s` | Symmetric | Symmetric | Equal enclosure in all directions |

Example: `Via1_XY` — Metal1 enclosure extends horizontally, Metal2 enclosure extends vertically. Useful when routing transitions from horizontal Metal1 to vertical Metal2.

##### Double-Cut Vias (Via1–Via4)

Double-cut vias contain **two cut rectangles** in a single via instance, providing **2× current capacity** compared to single-cut vias and improved reliability.

**Naming convention:** `ViaN_DCVarDir`

- `DC` = Double Cut
- `Var` = enclosure variant (`1` or `2`):
  - `1` = above-metal enclosure aligned with the double-cut direction
  - `2` = above-metal enclosure perpendicular to the double-cut direction
- `Dir` = direction of the second cut relative to center:
  - `B` = second cut placed above (+Y)
  - `T` = second cut placed below (−Y)
  - `L` = second cut placed to the right (+X)
  - `R` = second cut placed to the left (−X)

| Via | Arrangement | Above-Metal Alignment | Notes |
|---|---|---|---|
| `ViaN_DC1B` | Vertical (+Y) | Aligned (tall) | Second cut above center |
| `ViaN_DC1T` | Vertical (−Y) | Aligned (tall) | Second cut below center |
| `ViaN_DC1L` | Horizontal (+X) | Aligned (wide) | Second cut right of center |
| `ViaN_DC1R` | Horizontal (−X) | Aligned (wide) | Second cut left of center |
| `ViaN_DC2B` | Vertical (+Y) | Perpendicular | Second cut above center |
| `ViaN_DC2T` | Vertical (−Y) | Perpendicular | Second cut below center |
| `ViaN_DC2L` | Horizontal (+X) | Perpendicular | Second cut right of center |
| `ViaN_DC2R` | Horizontal (−X) | Perpendicular | Second cut left of center |

Example: `Via1_DC1B` — two Via1 cuts arranged vertically (second cut at +Y), Metal2 enclosure tall/narrow (aligned with the vertical arrangement). Provides 0.8 mA DC current capacity.

##### TopVia Fixed Vias

| Via | Connects | Cut Size | Enclosure | Resistance |
|---|---|---|---|---|
| `TopVia1EWNS` | Metal5 → TopMetal1 | 0.42 µm | Metal5: 0.31 µm, TopMetal1: 0.75 µm | 4 Ω |
| `TopVia2EWNS` | TopMetal1 → TopMetal2 | 0.9 µm | TopMetal1: 0.95 µm, TopMetal2: 0.95 µm | 2.2 Ω |

`EWNS` = East-West-North-South — symmetric enclosure in all four directions. These are the only fixed via variants for the top metal transitions because TopMetal1/TopMetal2 have large minimum widths that inherently require symmetric enclosures.

#### GENERATE Via Rules (Automatic Arrays)

GENERATE rules allow the router to automatically create via **arrays** sized to match the wire width. Wider wires produce more cuts, lowering resistance and increasing current capacity.

| Rule | Cut Layer | Cut Spacing | Enclosure (Below) | Enclosure (Above) |
|---|---|---|---|---|
| `via1Array` | Via1 | 0.48 µm × 0.48 µm | Metal1: 0.05/0.01 µm | Metal2: 0.05/0.005 µm |
| `via2Array` | Via2 | 0.48 µm × 0.48 µm | Metal2: 0.05/0.005 µm | Metal3: 0.05/0.005 µm |
| `via3Array` | Via3 | 0.48 µm × 0.48 µm | Metal3: 0.05/0.005 µm | Metal4: 0.05/0.005 µm |
| `via4Array` | Via4 | 0.48 µm × 0.48 µm | Metal4: 0.05/0.005 µm | Metal5: 0.05/0.005 µm |
| `viaTop1Array` | TopVia1 | 0.84 µm × 0.84 µm | Metal5: 0.1/0.1 µm | TopMetal1: 0.42/0.42 µm |
| `viaTop2Array` | TopVia2 | 1.96 µm × 1.96 µm | TopMetal1: 0.5/0.5 µm | TopMetal2: 0.5/0.5 µm |

The router uses GENERATE rules when no specific fixed vias are mandated by NDR rules. When NDR `via` specifies fixed via types (e.g., `Via1_DC1B`), the router uses those fixed definitions instead.

#### Current Capacity Example (10 mA)

To carry 10 mA through a via transition:

| Cut Layer | Current per Cut | Cuts Needed | Notes |
|---|---|---|---|
| Via1–Via4 | 0.4 mA | 25 | With double-cut vias: 13 instances |
| TopVia1 | 1.4 mA | 8 | With `viaTop1Array` on 5 µm wire: ~25 cuts |
| TopVia2 | 10 mA | 1 | Single cut is sufficient |

With a 5 µm wide NDR wire and GENERATE via array rules, the router can fit approximately $\lfloor 5.0 / 0.48 \rfloor ^2 \approx 100$ cuts for Via1–Via4, far exceeding the 25 needed for 10 mA. When using fixed double-cut vias (e.g., `Via1_DC1B`), the router places multiple instances as space permits.

#### Summary of All Via Names

**Via1 (Metal1 → Metal2):** `Via1_XX`, `Via1_XX_s`, `Via1_XY`, `Via1_XY_s`, `Via1_YX`, `Via1_YX_s`, `Via1_YY`, `Via1_YY_s`, `Via1_s`, `Via1_DC1B`, `Via1_DC1T`, `Via1_DC1L`, `Via1_DC1R`, `Via1_DC2B`, `Via1_DC2T`, `Via1_DC2L`, `Via1_DC2R`

**Via2 (Metal2 → Metal3):** `Via2_XX`, `Via2_XX_s`, `Via2_XY`, `Via2_XY_s`, `Via2_YX`, `Via2_YX_s`, `Via2_YY`, `Via2_YY_s`, `Via2_s`, `Via2_DC1B`, `Via2_DC1T`, `Via2_DC1L`, `Via2_DC1R`, `Via2_DC2B`, `Via2_DC2T`, `Via2_DC2L`, `Via2_DC2R`

**Via3 (Metal3 → Metal4):** `Via3_XX`, `Via3_XX_s`, `Via3_XY`, `Via3_XY_s`, `Via3_YX`, `Via3_YX_s`, `Via3_YY`, `Via3_YY_s`, `Via3_s`, `Via3_DC1B`, `Via3_DC1T`, `Via3_DC1L`, `Via3_DC1R`, `Via3_DC2B`, `Via3_DC2T`, `Via3_DC2L`, `Via3_DC2R`

**Via4 (Metal4 → Metal5):** `Via4_XX`, `Via4_XX_s`, `Via4_XY`, `Via4_XY_s`, `Via4_YX`, `Via4_YX_s`, `Via4_YY`, `Via4_YY_s`, `Via4_s`, `Via4_DC1B`, `Via4_DC1T`, `Via4_DC1L`, `Via4_DC1R`, `Via4_DC2B`, `Via4_DC2T`, `Via4_DC2L`, `Via4_DC2R`

**TopVia1 (Metal5 → TopMetal1):** `TopVia1EWNS`

**TopVia2 (TopMetal1 → TopMetal2):** `TopVia2EWNS`

### How It Works

NDRs are created and assigned in `drt.tcl` right before detailed routing runs:

1. **NDR creation:** If `NON_DEFAULT_RULES` is set, the script iterates over each rule, extracts `width`, `spacing`, and `via`, and calls OpenROAD's `create_ndr`.
2. **NDR assignment:** If `DRT_ASSIGN_NDR` is set, the script iterates over all nets in the design, matches each net name against the provided regex patterns, and calls `assign_ndr` for matches.

This ensures the router respects the wider widths/spacings during detailed routing.

## The Eight LEF/DEF Orientations

LEF/DEF uses eight orientation codes to describe macro placement. All rotations are counter-clockwise.

| Code | Name | Rotation | Mirror | Description |
|---|---|---|---|---|
| `N` | North | 0° | None | Default orientation. Placed exactly as drawn. |
| `W` | West | 90° CCW | None | Original top edge becomes the left edge. |
| `S` | South | 180° CCW | None | Original top-right corner becomes bottom-left corner. |
| `E` | East | 270° CCW | None | Original top edge becomes the right edge. |
| `FN` | Flipped North | 0° | Y-axis | Mirrored horizontally. Left becomes right; top/bottom unchanged. |
| `FW` | Flipped West | 90° CCW | Y-axis | Mirrored horizontally, then rotated 90° CCW. Equivalent to mirroring across the diagonal axis. |
| `FS` | Flipped South | 0° | X-axis | Mirrored vertically. Top becomes bottom; left/right unchanged. |
| `FE` | Flipped East | 270° CCW | Y-axis | Mirrored horizontally, then rotated 270° CCW. |
