# Extracted Layout Netlists

Layout netlists of `chip_top`, extracted from the GDS during LVS.

They are written by `make klayout-lvs` (`chip_top_klayout.cir`) and by `make magic-lvs` (`chip_top_magic.ext.spc`), which move the extracted netlist here out of the LVS run folder in `verification/lvs/`.

This folder stays empty until the top-level LVS is finished. See [Layout Versus Schematic (LVS)](../../README.md#layout-versus-schematic-lvs) in the top-level README.
