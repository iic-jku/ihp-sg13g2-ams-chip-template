# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# Johannes Kepler University, Department for Integrated Circuits
#
# SPDX-License-Identifier: Apache-2.0

"""
LibreLane plugin: chip-finishing step for logo addition and metal fill.

Registers the custom step ``ChipFinish.LogoAndFill`` which wraps the
ArtistIC ``meerkat`` tool chain and the PDK KLayout filler script.
The step replaces ``KLayout.Filler`` in the ``Chip`` flow by setting::

    KLayout.Filler: "ChipFinish.LogoAndFill"

in the ``substituting_steps`` section of ``config.yaml``.

Operation sequence
------------------
1. ``meerkat_interface.py``  — configure file paths; write ``meerkat_design.py``
2. KLayout ``export_top_metal.py``  — extract TM2 geometry into a standalone GDS
3. ``meerkat.py``  — rasterise the PNG logo onto the TM2 layer
4. KLayout ``add_rectangle.py``  — add bounding boxes (repeated per layer)
5. KLayout ``merge_logo.py``  — merge logo GDS back into the chip GDS
6. KLayout PDK ``filler.py``  — run fill patterns on all layers
"""

import os
import subprocess
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple

from librelane.config import Variable
from librelane.state import DesignFormat
from librelane.steps import Step, StepError


@Step.factory.register()
class LogoAndFill(Step):
    """Add the design logo to TM2 and run PDK metal fill on the chip-top GDS."""

    id = "ChipFinish.LogoAndFill"
    name = "Logo and Fill"
    long_name = "Chip Top Finishing: Logo Addition and Metal Fill"

    inputs = [DesignFormat.GDS]
    outputs = [DesignFormat.GDS]

    config_vars = [
        Variable(
            "ARTISTIC_SCRIPTS_DIR",
            Path,
            "Path to the ArtistIC scripts directory.  Must contain "
            "meerkat_interface.py, meerkat.py, export_top_metal.py, "
            "add_rectangle.py, and merge_logo.py.",
        ),
        Variable(
            "LOGO_IMAGE",
            Path,
            "Path to the monochrome PNG logo image.",
        ),
        Variable(
            "TOP_METAL_LAYER",
            int,
            "GDS layer number of the top metal layer used for logo placement "
            "(TM2 = 134 for IHP SG13G2).",
            default=134,
        ),
        Variable(
            "LOGO_MARGIN_LEFT",
            Decimal,
            "Logo left margin from the die origin (layout origin, not core "
            "origin) in µm.  Equal to CORE_LLX + LOGO_CORE_MARGIN_LEFT.",
            units="µm",
        ),
        Variable(
            "LOGO_MARGIN_BOTTOM",
            Decimal,
            "Logo bottom margin from the die origin in µm.  Equal to "
            "CORE_LLY + LOGO_CORE_MARGIN_BOTTOM.",
            units="µm",
        ),
        Variable(
            "LOGO_RECT_LAYERS",
            List[str],
            "Layer/datatype strings for bounding rectangles drawn around the "
            "logo (e.g. '134/23').  One rectangle is drawn per entry.",
            default=["134/23", "126/23"],
        ),
        Variable(
            "LOGO_RECT_MARGINS",
            List[Decimal],
            "Extra clearance in µm for each rectangle in LOGO_RECT_LAYERS.  "
            "Must have the same length as LOGO_RECT_LAYERS.",
            units="µm",
            default=[Decimal("20"), Decimal("0")],
        ),
    ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run(self, cmd: list, *, env: dict | None = None) -> None:
        """Run *cmd* as a subprocess, raising StepError on failure."""
        try:
            subprocess.run(
                cmd,
                check=True,
                env=env,
            )
        except subprocess.CalledProcessError as exc:
            raise StepError(
                f"Command failed (exit {exc.returncode}): {' '.join(str(c) for c in cmd)}"
            ) from exc

    # ------------------------------------------------------------------
    # Step entry point
    # ------------------------------------------------------------------

    def run(
        self,
        state_in,
        *args,
        **kwargs,
    ) -> Tuple[dict, dict]:
        design_name = str(self.config["DESIGN_NAME"])
        scripts_dir = str(self.config["ARTISTIC_SCRIPTS_DIR"])
        logo_img = str(self.config["LOGO_IMAGE"])
        top_metal = str(self.config["TOP_METAL_LAYER"])
        margin_left = str(self.config["LOGO_MARGIN_LEFT"])
        margin_bottom = str(self.config["LOGO_MARGIN_BOTTOM"])
        rect_layers: List[str] = self.config["LOGO_RECT_LAYERS"]
        rect_margins: List[Decimal] = self.config["LOGO_RECT_MARGINS"]

        pdk_root = str(self.config["PDK_ROOT"])
        pdk = str(self.config["PDK"])
        filler_script = os.path.join(
            pdk_root, pdk, "libs.tech", "klayout", "tech", "scripts", "filler.py"
        )

        gds_in = str(state_in[DesignFormat.GDS])
        step_dir = str(self.step_dir)

        gds_tm2 = os.path.join(step_dir, f"{design_name}_tm2.gds")
        gds_logo = os.path.join(step_dir, f"{design_name}_logo.gds")
        gds_out = os.path.join(step_dir, f"{design_name}_logo.gds.gz")
        gds_out_fill = os.path.join(step_dir, f"{design_name}_logo_fill.gds.gz")

        # Environment for KLayout macro calls: meerkat_design.py must be
        # importable, so add step_dir to PYTHONPATH.
        klayout_env = os.environ.copy()
        existing = klayout_env.get("PYTHONPATH", "")
        klayout_env["PYTHONPATH"] = f"{step_dir}:{existing}" if existing else step_dir

        # ── Step 1: generate meerkat_design.py and configure all paths ──
        self._run(
            [
                "python3",
                os.path.join(scripts_dir, "meerkat_interface.py"),
                "-i", gds_in,
                "-m", gds_tm2,
                "-g", gds_logo,
                "-o", gds_out,
                "-w", step_dir,
                "-l", top_metal,
                "-n", f"{design_name}_logo_fill",
            ]
        )

        # ── Step 2: export TM2 layer via KLayout ──
        self._run(
            ["klayout", "-zz", "-rm", os.path.join(scripts_dir, "export_top_metal.py")],
            env=klayout_env,
        )

        # ── Step 3: rasterise logo PNG onto TM2 layer ──
        self._run(
            [
                "python3",
                os.path.join(scripts_dir, "meerkat.py"),
                "-m", f"{margin_left},{margin_bottom}",
                "-i", logo_img,
                "-g", gds_tm2,
                "-l", top_metal,
                "-n", design_name,
                "-o", gds_logo,
            ]
        )

        # ── Step 4: add bounding rectangles around the logo ──
        for layer, margin in zip(rect_layers, rect_margins):
            self._run(
                [
                    "klayout", "-zz",
                    "-rd", f"gds_file={gds_logo}",
                    "-rd", f"layer={layer}",
                    "-rd", f"margin={margin}",
                    "-r", os.path.join(scripts_dir, "add_rectangle.py"),
                ]
            )

        # ── Step 5: merge logo GDS back into chip GDS ──
        self._run(
            ["klayout", "-zz", "-rm", os.path.join(scripts_dir, "merge_logo.py")],
            env=klayout_env,
        )

        # ── Step 6: run PDK fill patterns ──
        self._run(
            [
                "klayout", "-zz",
                "-rd", f"output_file={gds_out_fill}",
                "-r", filler_script,
                gds_out,
            ]
        )

        # ── Clean up intermediate files ──
        for f in [gds_tm2, gds_logo, gds_out, os.path.join(step_dir, "meerkat_design.py")]:
            try:
                os.remove(f)
            except FileNotFoundError:
                pass

        return {DesignFormat.GDS: Path(gds_out_fill)}, {}
