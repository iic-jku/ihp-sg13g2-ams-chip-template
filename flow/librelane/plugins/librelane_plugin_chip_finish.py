# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

"""Chip finishing steps of the LibreLane chip flow: logo and fill.

ChipFinish.Logo and ChipFinish.Fill write the view logo_fill_gds, the file <DESIGN_NAME>_logo_fill.gds with the top cell <DESIGN_NAME>_logo_fill around the chip, the logo and the fill. The GDS view keeps the unfilled chip, so --save-views-to writes both files into its gds/ folder.
LibreLane loads this module because its folder is on PYTHONPATH, see LIBRELANE in the Makefile.
"""

import os
import re
import shutil
from decimal import Decimal
from typing import Dict, List, Literal, Optional, Tuple

from librelane.common import Path, get_script_dir
from librelane.config import Variable
from librelane.logging import info
from librelane.state import DesignFormat, State
from librelane.steps import MetricsUpdate, Step, StepError, ViewsUpdate
from librelane.steps.klayout import Filler as KLayoutFiller
from librelane.steps.magic import Filler as MagicFiller

LOGO_FILL_GDS = DesignFormat(
    "logo_fill_gds",
    "gds",
    "GDSII Stream with Logo and Fill",
    folder_override="gds",
)
LOGO_FILL_GDS.register()


def _layer(spec: str) -> Tuple[int, int]:
    layer, datatype = spec.split("/")
    return int(layer), int(datatype)


def _pdk_variable(step: type, name: str) -> Variable:
    # Shared with the stock filler steps, so the flow sees one variable and not two that collide
    return next(var for var in step.config_vars if var.name == name)


@Step.factory.register()
class Logo(Step):
    """
    Places a logo image on the chip with the ArtistIC scripts and puts the chip and the logo into the new top cell <DESIGN_NAME>_logo_fill.
    """

    id = "ChipFinish.Logo"
    name = "Logo"

    inputs = [DesignFormat.GDS]
    outputs = [LOGO_FILL_GDS]

    config_vars = [
        Variable(
            "CHIP_FINISH_ARTISTIC_DIR",
            Path,
            "The scripts folder of ArtistIC.",
        ),
        Variable(
            "CHIP_FINISH_LOGO_IMAGE",
            Path,
            "Monochrome PNG of the logo. Each pixel becomes a 2 µm square on the chip.",
        ),
        Variable(
            "CHIP_FINISH_LOGO_LAYER",
            str,
            "Layer and datatype of the logo, for example 134/0.",
        ),
        Variable(
            "CHIP_FINISH_LOGO_POSITION",
            Tuple[Decimal, Decimal],
            "Lower-left corner of the logo image, measured from the die origin.",
            units="µm",
        ),
        Variable(
            "CHIP_FINISH_LOGO_NOFILL_LAYERS",
            List[str],
            "Layers that get a rectangle around the logo, for example the nofill datatype of a filler.",
            default=[],
        ),
        Variable(
            "CHIP_FINISH_LOGO_NOFILL_MARGIN",
            Decimal,
            "Margin between the logo and the rectangles of CHIP_FINISH_LOGO_NOFILL_LAYERS.",
            default=0,
            units="µm",
        ),
    ]

    def run(self, state_in: State, **kwargs) -> Tuple[ViewsUpdate, MetricsUpdate]:
        kwargs, env = self.extract_env(kwargs)
        design = self.config["DESIGN_NAME"]
        scripts = self.config["CHIP_FINISH_ARTISTIC_DIR"]
        layer, datatype = _layer(self.config["CHIP_FINISH_LOGO_LAYER"])
        x, y = self.config["CHIP_FINISH_LOGO_POSITION"]

        chip_gds = str(state_in[DesignFormat.GDS])
        metal_gds = os.path.join(self.step_dir, "top_metal.gds")
        logo_gds = os.path.join(self.step_dir, "logo.gds")
        out_gds = os.path.join(self.step_dir, f"{design}_logo_fill.gds")

        # meerkat_interface.py writes meerkat_design.py, which export_top_metal.py and merge_logo.py read from the working directory
        self.run_subprocess(
            [
                "python3",
                os.path.join(scripts, "meerkat_interface.py"),
                *("-i", chip_gds, "-m", metal_gds, "-g", logo_gds, "-o", out_gds),
                *("-w", self.step_dir, "-l", str(layer), "-d", str(datatype)),
                *("-n", f"{design}_logo_fill"),
            ],
            log_to=os.path.join(self.step_dir, "meerkat_interface.log"),
            env=env,
            cwd=self.step_dir,
        )
        self.run_subprocess(
            ["klayout", "-b", "-r", os.path.join(scripts, "export_top_metal.py")],
            log_to=os.path.join(self.step_dir, "export_top_metal.log"),
            env=env,
            cwd=self.step_dir,
        )
        # export_top_metal.py exits without a file when the chip has no shapes on the logo layer
        if not os.path.exists(metal_gds):
            raise StepError(f"No {layer}/{datatype} shapes in {chip_gds}.")

        self.run_subprocess(
            [
                "python3",
                os.path.join(scripts, "meerkat.py"),
                *("-m", f"{x},{y}", "-i", str(self.config["CHIP_FINISH_LOGO_IMAGE"]), "-g", metal_gds),
                *("-l", str(layer), "-d", str(datatype), "-n", design, "-o", logo_gds),
            ],
            log_to=os.path.join(self.step_dir, "meerkat.log"),
            silent=True,  # one progress line per image column
            env=env,
            cwd=self.step_dir,
        )

        if nofill_layers := self.config["CHIP_FINISH_LOGO_NOFILL_LAYERS"]:
            import klayout.db as kdb

            layout = kdb.Layout()
            layout.read(logo_gds)
            top = layout.top_cell()
            box = top.dbbox().enlarged(float(self.config["CHIP_FINISH_LOGO_NOFILL_MARGIN"]))
            for spec in nofill_layers:
                top.shapes(layout.layer(*_layer(spec))).insert(box)
            layout.write(logo_gds)

        self.run_subprocess(
            ["klayout", "-b", "-r", os.path.join(scripts, "merge_logo.py")],
            log_to=os.path.join(self.step_dir, "merge_logo.log"),
            env=env,
            cwd=self.step_dir,
        )

        return {LOGO_FILL_GDS: Path(out_gds)}, {}


@Step.factory.register()
class Fill(Step):
    """
    Fills the unfilled output of ChipFinish.Logo with the tool in CHIP_FINISH_FILLER, checks the fill against CHIP_FINISH_FILL_LAYERS and CHIP_FINISH_FILL_BOUNDARY_LAYER, and adds the die outline.
    """

    id = "ChipFinish.Fill"
    name = "Fill"

    inputs = [LOGO_FILL_GDS]
    outputs = [LOGO_FILL_GDS]

    config_vars = [
        Variable(
            "CHIP_FINISH_FILLER",
            Literal["klayout", "magic", "gdsfill"],
            "The fill tool: the KLayout filler of the PDK, the Magic filler of the PDK or gdsfill.",
            default="klayout",
        ),
        Variable(
            "CHIP_FINISH_FILL_LAYERS",
            Dict[str, List[str]],
            "Each fill layer with the layers its fill has to stay out of. The step fails when fill lies in a keep-out, when klayout or magic leave a fill layer empty, or when gdsfill writes no fill at all. gdsfill rightly skips a layer that already meets its density target, so for it an empty layer is a warning.",
        ),
        Variable(
            "CHIP_FINISH_FILL_BOUNDARY_LAYER",
            Optional[str],
            "Layer of the seal ring. The step fails when fill lies outside the area it encloses.",
        ),
        Variable(
            "CHIP_FINISH_KLAYOUT_DISTANCES",
            Optional[Dict[str, Decimal]],
            "Distances between the shapes of the KLayout filler, set in copies of the PDK filler macros. A key names the variable in the macro, for example distance_m1, and has to occur in exactly one macro.",
            units="µm",
        ),
        Variable(
            "CHIP_FINISH_GDSFILL_CONFIG",
            Optional[Path],
            "Config file of gdsfill with the density targets per layer.",
        ),
        Variable(
            "CHIP_FINISH_DIE_OUTLINE_LAYER",
            Optional[str],
            "Layer that gets a rectangle on the bounding box of the filled chip.",
        ),
        _pdk_variable(KLayoutFiller, "KLAYOUT_FILLER_SCRIPT"),
        _pdk_variable(KLayoutFiller, "KLAYOUT_FILLER_DEFINES"),
        _pdk_variable(MagicFiller, "MAGIC_FILLER_SCRIPT"),
        _pdk_variable(MagicFiller, "MAGIC_FILLER_OPTIONS"),
    ]

    def run(self, state_in: State, **kwargs) -> Tuple[ViewsUpdate, MetricsUpdate]:
        kwargs, env = self.extract_env(kwargs)
        env["PDK_ROOT"] = self.config["PDK_ROOT"]
        env["PDK"] = self.config["PDK"]

        in_gds = str(state_in[LOGO_FILL_GDS])
        out_gds = os.path.join(self.step_dir, f"{self.config['DESIGN_NAME']}_logo_fill.gds")

        filler = self.config["CHIP_FINISH_FILLER"]
        info(f"Filling with {filler}…")
        if filler == "klayout":
            self.fill_klayout(in_gds, out_gds, env)
        elif filler == "magic":
            self.fill_magic(in_gds, out_gds, env)
        else:
            self.fill_gdsfill(in_gds, out_gds, env)

        self.check_and_outline(out_gds, filler)

        return {LOGO_FILL_GDS: Path(out_gds)}, {}

    def fill_klayout(self, in_gds: str, out_gds: str, env: Dict[str, str]):
        script = self.config["KLAYOUT_FILLER_SCRIPT"]
        if script is None:
            raise StepError(f"KLAYOUT_FILLER_SCRIPT is unset, the KLayout filler does not support {self.config['PDK']}.")

        # The PDK macros hard-code the distances, so filler.py runs on patched copies in a PDK tree of their own
        if distances := self.config["CHIP_FINISH_KLAYOUT_DISTANCES"]:
            macro_dir = os.path.join("libs.tech", "klayout", "tech", "macros")
            src = os.path.join(self.config["PDK_ROOT"], self.config["PDK"], macro_dir)
            root = os.path.join(self.step_dir, "pdk")
            dst = os.path.join(root, self.config["PDK"], macro_dir)
            os.makedirs(dst, exist_ok=True)
            found: Dict[str, List[str]] = {key: [] for key in distances}
            for name in sorted(os.listdir(src)):
                if "_filler_" not in name or not name.endswith(".lym"):
                    continue
                with open(os.path.join(src, name), encoding="utf-8") as f:
                    text = f.read()
                for key, value in distances.items():
                    # 'distance_m1' => 1.5 in a distance map, distance = 3.05 on a line of its own
                    pattern = rf"('{re.escape(key)}'\s*=>\s*|^\s*{re.escape(key)}\s*=\s*)[0-9.]+"
                    text, count = re.subn(pattern, lambda m: f"{m.group(1)}{value}", text, flags=re.M)
                    if count:
                        found[key].append(name)
                with open(os.path.join(dst, name), "w", encoding="utf-8") as f:
                    f.write(text)
            if bad := {key: names for key, names in found.items() if len(names) != 1}:
                raise StepError(f"CHIP_FINISH_KLAYOUT_DISTANCES: each key has to occur in exactly one filler macro of {src}, found {bad}.")
            env = {**env, "PDK_ROOT": root}

        defines = [arg for key, value in (self.config["KLAYOUT_FILLER_DEFINES"] or {}).items() for arg in ("-rd", f"{key}={value}")]
        self.run_subprocess(
            ["klayout", "-b", "-zz", "-r", str(script), "-rd", f"output_file={out_gds}", *defines, in_gds],
            log_to=os.path.join(self.step_dir, "klayout_filler.log"),
            env=env,
        )

    def fill_magic(self, in_gds: str, out_gds: str, env: Dict[str, str]):
        script = self.config["MAGIC_FILLER_SCRIPT"]
        if script is None:
            raise StepError(f"MAGIC_FILLER_SCRIPT is unset, the Magic filler does not support {self.config['PDK']}.")

        # generate_fill.py loads the cell named like the GDS file and writes its tiles and <name>_fill_pattern.gds.gz next to it, the only output name every PDK's version accepts
        work = os.path.join(self.step_dir, "magic")
        os.makedirs(work, exist_ok=True)
        top_name = f"{self.config['DESIGN_NAME']}_logo_fill"
        top_gds = os.path.join(work, f"{top_name}.gds")
        fill_gds = os.path.join(work, f"{top_name}_fill_pattern.gds.gz")
        shutil.copyfile(in_gds, top_gds)

        # ~/.magicrc of IIC-OSIC-TOOLS sources the PDK magicrc, which loads the regular tech over the -T GDS tech of generate_fill.py and quits, so Magic runs with a home of its own (IHP-Open-PDK#1380)
        self.run_subprocess(
            ["python3", str(script), os.path.basename(top_gds), *(self.config["MAGIC_FILLER_OPTIONS"] or [])],
            log_to=os.path.join(self.step_dir, "magic_filler.log"),
            env={**env, "HOME": work},
            cwd=work,
        )
        os.remove(top_gds)
        if not os.path.exists(fill_gds):
            raise StepError(f"The Magic filler wrote no {fill_gds}, see magic_filler.log.")

        self.run_subprocess(
            [
                "klayout",
                *("-b", "-zz", "-r", os.path.join(get_script_dir(), "klayout", "insert_cell.py")),
                *("-rd", f"input={in_gds}", "-rd", f"insert={fill_gds}", "-rd", f"output={out_gds}"),
            ],
            log_to=os.path.join(self.step_dir, "insert_fill.log"),
            env=env,
        )

    def fill_gdsfill(self, in_gds: str, out_gds: str, env: Dict[str, str]):
        # gdsfill fills the file in place
        shutil.copyfile(in_gds, out_gds)
        cmd = ["gdsfill", "fill", "--process", self.config["PDK"]]
        if config := self.config["CHIP_FINISH_GDSFILL_CONFIG"]:
            cmd += ["--config-file", str(config)]
        self.run_subprocess(
            [*cmd, out_gds],
            log_to=os.path.join(self.step_dir, "gdsfill.log"),
            env=env,
        )

    def check_and_outline(self, gds: str, filler: str):
        import klayout.db as kdb

        layout = kdb.Layout()
        layout.read(gds)
        top = layout.top_cell()
        dbu2 = layout.dbu**2

        inner = None
        if boundary := self.config["CHIP_FINISH_FILL_BOUNDARY_LAYER"]:
            inner = kdb.Region(top.begin_shapes_rec(layout.layer(*_layer(boundary)))).merged().holes()
            if inner.is_empty():
                raise StepError(f"CHIP_FINISH_FILL_BOUNDARY_LAYER: the shapes on {boundary} enclose no area.")

        errors, empty = [], []
        for spec, keepout_specs in self.config["CHIP_FINISH_FILL_LAYERS"].items():
            fill_layer = layout.layer(*_layer(spec))
            keepouts = {k: kdb.Region(top.begin_shapes_rec(layout.layer(*_layer(k)))) for k in keepout_specs}
            keepout = kdb.Region()
            for region in keepouts.values():
                keepout += region

            # gdsfill 0.1.11 reads neither nofill datatypes nor NoMetFiller (gdsfill#56) and writes its fill flat into the top cell, so its fill in a keep-out is removed instead of failing the step
            if filler == "gdsfill" and not keepout.is_empty():
                fill = kdb.Region(top.shapes(fill_layer))
                fill.merged_semantics = False
                kept = fill.not_overlapping(keepout)
                if fill.count() - kept.count():
                    hits = ", ".join(f"{fill.overlapping(region).count()} on {k}" for k, region in keepouts.items())
                    self.warn(f"Removed {fill.count() - kept.count()} gdsfill shapes on {spec} that overlap a keep-out ({hits}).")
                    top.shapes(fill_layer).clear()
                    top.shapes(fill_layer).insert(kept)

            fill = kdb.Region(top.begin_shapes_rec(fill_layer))
            inside = (fill & keepout).area() * dbu2
            outside = (fill - inner).area() * dbu2 if inner is not None else 0
            info(f"{spec}: {fill.count()} fill shapes, {inside:.1f} µm² in a keep-out, {outside:.1f} µm² outside the boundary.")
            if fill.is_empty():
                empty.append(spec)
            if inside > 0:
                errors.append(f"{inside:.1f} µm² of {spec} inside {', '.join(keepout_specs)}")
            if outside > 0:
                errors.append(f"{outside:.1f} µm² of {spec} outside the area {boundary} encloses")

        if empty:
            # The fixed patterns of klayout and magic fill every layer, gdsfill skips a layer that already meets its density target
            if filler != "gdsfill":
                errors.append(f"no fill on {', '.join(empty)}")
            elif len(empty) == len(self.config["CHIP_FINISH_FILL_LAYERS"]):
                errors.append("no fill on any layer")
            else:
                self.warn(f"No fill on {', '.join(empty)}.")

        if errors:
            raise StepError(f"{filler} fill failed the check:\n" + "\n".join(errors))

        if outline := self.config["CHIP_FINISH_DIE_OUTLINE_LAYER"]:
            top.shapes(layout.layer(*_layer(outline))).insert(top.bbox())
        layout.write(gds)
