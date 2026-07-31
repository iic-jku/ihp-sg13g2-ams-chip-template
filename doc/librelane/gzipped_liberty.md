# Gzipped Liberty Files

The IIC-OSIC-TOOLS PDK currently ships the Liberty timing libraries uncompressed
(`*.lib`). Should they ever be shipped gzipped (`*.lib.gz`), this template adapts
automatically. This document explains the mechanism, what has been verified, and the one
issue that is **not** solved on our side.


## The Mechanism

The LibreLane configs reference the PDK Liberty files with a hardcoded extension, for
example in [`flow/librelane/config.yaml`](../../flow/librelane/config.yaml):

```yaml
LIB:
  "*_typ_1p50V_25C":
    - pdk_dir::libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p50V_25C.lib
```

Instead of running LibreLane on that file directly, the Makefiles generate a resolved copy
next to it and run LibreLane on that:

```sh
make librelane-config      # config.yaml -> config.resolved.yaml
```

Every `pdk_dir::libs.ref/<family>/lib/*.lib` reference is rewritten to whatever extension
the installed PDK actually provides. The extension is auto-detected per library family by
a `$(wildcard)` over `$PDK_ROOT/$PDK/libs.ref/<family>/lib/*.lib.gz`, so a PDK that
converts `sg13g2_stdcell` before `sg13g2_sram` still works. It can be overridden:

```sh
make librelane PDK_STDCELL_LIB_EXT=.lib.gz PDK_SRAM_LIB_EXT=.lib.gz
```

All `librelane*` targets depend on `librelane-config`, so no extra step is needed in normal
use. `config.resolved.yaml` is generated and therefore in [`.gitignore`](../../.gitignore).

Design notes worth keeping in mind when editing this:

- The generated file must stay **in the same directory** as `config.yaml`. LibreLane
  resolves `dir::` relative to the config file's location and creates `runs/` next to it,
  so a copy elsewhere would break every relative path and `--last-run`.
- `config.yaml` stays the single hand-edited source. Patching it in place with `sed -i`
  would leave the working tree permanently dirty; a `config.yaml.in` template would change
  what users of this template are supposed to edit.
- The rewrite is anchored on `pdk_dir::libs.ref/<family>/lib/`. It must **not** match the
  repo-tracked Liberty files under [`ip/`](../../ip/) and
  [`macros/`](../../macros/) (which LibreLane produces itself, uncompressed), nor the
  unrelated SPICE `.lib` include files in
  [`testbenches/xschem/models/`](../../testbenches/xschem/models/), which merely share the
  extension.
- Adding a new PDK library family to a config means adding a matching `-e` expression and
  `*_LIB_EXT` variable to the `librelane-config` target, or its libraries will never be
  rewritten.


## The Open Issue: The PDK Ships Its Own LIB Declarations

**Rewriting our config is necessary but not sufficient.**

The PDK ships `$PDK_ROOT/$PDK/libs.tech/librelane/config.tcl`, which declares the default
corner libraries itself:

```tcl
$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sg13g2_stdcell_typ_1p20V_25C.lib\
$::env(PDK_ROOT)/$::env(PDK)/libs.ref/sg13g2_io/lib/sg13g2_io_typ_1p2V_3p3V_25C.lib\
```

LibreLane loads and **validates these paths when it loads the PDK**, before any
design-level `LIB` override is applied. If the PDK Liberty files are gzipped but this file
is not updated, every design fails immediately with:

```
ERROR    Errors have occurred while loading the PDK configuration files.
ERROR    Path provided for variable 'CELL_LIBS.*_typ_1p20V_25C[0]' is invalid:
         '.../libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p20V_25C.lib' does not exist
```

This is not something the design side can work around, and **we deliberately do not patch
the PDK**. A PDK in that state is broken for every LibreLane user, not just for this
template, so keeping the Liberty files and `config.tcl` consistent is the job of whoever
gzips them (IHP-Open-PDK / IIC-OSIC-TOOLS). If gzipped libraries are ever proposed
upstream, this is the point to raise.


## What Has Been Verified

Tested on 2026-07-31 in `hpretl/iic-osic-tools:latest` (LibreLane v3.1.0.dev2, Yosys 0.67,
OpenSTA 3.1.0) by building a synthetic PDK whose `sg13g2_stdcell` and `sg13g2_io` Liberty
files are genuinely gzipped (with `config.tcl` patched to match) and running the counter
macro through `OpenROAD.STAPrePNR`:

| Consumer | Result |
| --- | --- |
| Yosys | Reads `.lib.gz` natively: `Found gzip magic in file '...', decompressing using zlib`. Synthesis produced a normal mapped netlist. |
| OpenSTA | Reads `.lib.gz`. All six corners produced real timing numbers. |
| LibreLane | Writes a decompressed `runs/<tag>/tmp/<hash>.lib` internally for its own Liberty pass, so compression costs nothing there. |

The flow exited 0 with an empty `error.log`. No decompress-to-scratch workaround is needed
on the design side.

To reproduce, mirror the PDK with symlinks, materialise only the `lib/` directories as
gzipped copies, patch `libs.tech/librelane/config.tcl` to match, and point `--pdk-root` at
the mirror.

> [!NOTE]
> `PDK` is unset under a bare `bash` entrypoint in that image. Use a login shell
> (`bash -l`) so that `/etc/profile.d/iic-osic-tools-setup.sh` sets `PATH` and `PDK`.
