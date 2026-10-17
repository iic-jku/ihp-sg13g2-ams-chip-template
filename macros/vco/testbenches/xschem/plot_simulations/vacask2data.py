# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: VACASK postprocess script, writes the results of every analysis of a testbench run as text tables to plot_simulations/data/.
# ============================================
#
# Last line of a VACASK control block: postprocess(PYTHON, "../plot_simulations/vacask2data.py", "<testbench>")
# VACASK runs it in simulations/, next to <testbench>.spectre and the rawfiles. Each analysis of the netlist becomes
# data/<testbench>_<analysis>.txt in the layout of ngspice's wrdata, complex vectors as the columns re(<name>) and im(<name>).

import re
import sys
from pathlib import Path

import numpy as np

# The rawfile module moved into the vacask package in 2026-10
try:
    from vacask.rawfile import rawread
except ImportError:
    from rawfile import rawread


def write_table(raw_path, txt_path):
    data = rawread(str(raw_path)).get()
    names, cols = [], []
    for name in data.names:
        vec = np.asarray(data[name])
        if np.iscomplexobj(vec) and np.any(vec.imag != 0):
            names += [f"re({name})", f"im({name})"]
            cols += [vec.real, vec.imag]
        else:
            names.append(name)
            cols.append(np.real(vec))
    with open(txt_path, "w") as f:
        f.write(" ".join(f"{n:<15s}" for n in names) + "\n")
        for row in np.column_stack(cols):
            f.write(" ".join(f"{v:.8e}" for v in row) + "\n")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: vacask2data.py <testbench>")
    tb = sys.argv[1]
    netlist = Path(f"{tb}.spectre")
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    analyses = re.findall(r"^\s*analysis\s+(\w+)\s+\w+", netlist.read_text(), re.M)
    if not analyses:
        sys.exit(f"vacask2data.py: no analysis found in {netlist}")
    for name in analyses:
        raws = sorted(Path(".").glob(f"{name}.raw")) + sorted(Path(".").glob(f"{name}.*.raw"))
        if not raws:
            sys.exit(f"vacask2data.py: no rawfile for analysis {name}")
        for raw in raws:
            suffix = raw.name[len(name):-len(".raw")].replace(".", "_")
            txt = data_dir / f"{tb}_{name}{suffix}.txt"
            write_table(raw, txt)
            print(f"vacask2data.py: {raw} -> {txt}")


if __name__ == "__main__":
    main()
# ==============================================================================
