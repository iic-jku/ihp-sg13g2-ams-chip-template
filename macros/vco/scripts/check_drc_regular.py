# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Check a macro's KLayout DRC report at regular level: only the density rules, which the chip's fill resolves, may fail.

import argparse
import collections
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

# Global densities of Activ, GatPoly and the metals, which a macro cannot meet before the chip's fill. The macro level
# leaves them out, but also rules a macro has to meet on its own, such as the minimum metal areas Mn.d.
DENSITY = re.compile(r"(AFil|GFil)\.g\d*|M\d\.[jk]|TM\d\.[cd]")


def main():
    parser = argparse.ArgumentParser(description="Check a KLayout DRC report at regular level.")
    parser.add_argument("report_dir", help="folder with the .lyrdb report of sak-drc.sh -k -l regular")
    args = parser.parse_args()

    # sak-drc.sh writes the extra rules, the density and the antenna checks into subfolders of the run folder
    reports = glob.glob(os.path.join(args.report_dir, "**", "*.lyrdb"), recursive=True)
    if not reports:
        sys.exit(f"check_drc_regular.py: no .lyrdb report in {args.report_dir}, did the DRC run?")
    counts = collections.Counter()
    for report in reports:
        for item in ET.parse(report).getroot().find("items"):
            counts[item.findtext("category").strip("'")] += 1
    failed = {rule: n for rule, n in sorted(counts.items()) if not DENSITY.fullmatch(rule)}
    density = sorted(rule for rule in counts if DENSITY.fullmatch(rule))
    print(f"check_drc_regular.py: {len(density)} density rules left for the chip's fill: {' '.join(density) or 'none'}")
    if failed:
        sys.exit(f"check_drc_regular.py: rules other than density failed in {args.report_dir}: {failed}")
    print("check_drc_regular.py: no rule other than density failed")


if __name__ == "__main__":
    main()
