# Magic Layout Sources

This folder holds the layout of a cell drawn in [Magic](https://github.com/rtimothyedwards/magic). The template ships no Magic layout, because the inverter is drawn in KLayout and its sources live in [`../klayout/`](../klayout/). Draw in whichever tool you prefer: the DRC, LVS and PEX targets find the layout in either folder, and nothing else in the flow cares which one it came from.

## What Belongs Here

- `<cell>.mag`, one file per cell, including the subcells of the hierarchy.
- The device cells Magic generates when you place a parametrized device (`sg13g2_*_<random>.mag`). They are part of the layout and have to be committed with it, otherwise the hierarchy does not open on another machine.
- `<TOP>.gds`, the exported tapeout GDS written by `make export-gds`.
- Optionally a project `.magicrc`. `make export-gds` uses it when it is present and falls back to the PDK default `$PDK_ROOT/$PDK/libs.tech/magic/ihp-sg13g2.magicrc` when it is not.

Keeping the generated device cells out of `../klayout/` is the reason the two tools get their own folder. A Magic hierarchy of a few dozen cells is a few dozen files, and mixed into a KLayout folder it buries the handful of files that are actually the design.

## Working Here

Open a cell with the PDK loaded, from inside this folder:

```bash
cd macros/inverter/layout/magic
magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/ihp-sg13g2.magicrc <TOP>
```

Export the tapeout GDS after every layout change, from the macro folder:

```bash
make export-gds
```

`make export-gds` loads `<TOP>.mag` and writes `<TOP>.gds` next to it. That exported file is what the build targets read (`check-boundary`, `lef`, `copy-gds`, `render-gds`), so a layout change that is not exported is invisible to the build. The DRC, LVS and PEX targets read the exported GDS too, and fall back to the KLayout editing source only when there is no exported file, see [Layout Sources and the Exported Tapeout GDS](../../README.md#layout-sources-and-the-exported-tapeout-gds) in the macro README.

## The PR Boundary Box

The top cell has to draw a box on the `prBoundary` layer, which the chip flow reads to place the macro. Draw it in the Magic source so every export carries it, and check it with `make check-boundary`. See [PR Boundary Check](../../README.md#pr-boundary-check) in the macro README for what breaks without it.

The box comes out of `make export-gds` on `189/4` rather than the `189/0` a KLayout export writes, because Magic streams its boundary layer with datatype 4. Both are fine and nothing downstream has to be told which one it is: the PDK `cifin` maps every datatype of layer 189 to Magic's boundary (`calma BOUND 189 *`), which is what LibreLane reads back for the macro placement, and `check_boundary.py` accepts any datatype on 189 as well.
