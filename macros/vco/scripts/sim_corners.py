# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Run the netlisted start-up transient of vco_top at MOS and resistor corners, temperatures, VDD and vtune values.

import argparse
import csv
import itertools
import math
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# The peak voltage the thin-oxide devices of the pair may see: the chip core supply. Each tank node is the drain of one
# pair device and the gate of the other, so its maximum is checked against this.
V_PEAK_MAX = 1.5
# A tank swinging less than this between its extremes has not started, or only barely
V_SWING_MIN = 0.5
R_LOAD = 50.0  # load per output in the bench (Ohm)


def deck(src, corner, res, temp, vdd, vtune, threads):
    """The bench netlist with one corner pair, temperature, VDD and vtune, writing nothing but its measurements."""
    out = []
    netlist_dir = os.path.dirname(os.path.abspath(src))
    for line in open(src):
        s = line.rstrip("\n")
        if s.startswith(".include ") and not os.path.isabs(s.split()[1]):
            s = ".include " + os.path.normpath(os.path.join(netlist_dir, s.split()[1]))
        s = re.sub(r"^\.lib (cornerMOS(lv|hv)\.lib) mos_\w+$", rf".lib \1 {corner}", s)
        s = re.sub(r"^\.lib cornerRES\.lib res_\w+$", f".lib cornerRES.lib {res}", s)
        s = re.sub(r"^\.temp .*", f".temp {temp}", s)
        s = re.sub(r"^\.param VDD=.*", f".param VDD={vdd}", s)
        s = re.sub(r"^\.param Vtune=.*", f".param Vtune={vtune}", s)
        if s == "save all":
            s = f"set num_threads={threads}\nsave v(x1.rf_p) v(x1.rf_n) v(vout_p) i(VDD) v(x1.vdd_core)"
        if s.startswith(("write ", "wrdata", "+ v(x1.rf_p)", "set wr_")):
            s = "* " + s
        out.append(s)
    return "\n".join(out) + "\n"


def run(job):
    path = job["deck"]
    log = path[:-len(".spice")] + ".log"
    with open(log, "w") as f:
        subprocess.run(["ngspice", "-b", path], stdout=f, stderr=subprocess.STDOUT, cwd=os.path.dirname(path))
    vals = {}
    for line in open(log, errors="replace"):
        m = re.match(r"^(\w+)\s+=\s+([-+0-9.eE]+)", line)
        if m:
            vals[m.group(1)] = float(m.group(2))
    return job, vals


def main():
    parser = argparse.ArgumentParser(description="Run the start-up transient of vco_top over corners.")
    parser.add_argument("netlist", help="netlist of vco_top_tb_tran, written by make sim-xschem TB=vco_top_tb_tran")
    parser.add_argument("--corners", nargs="+", default=["mos_tt", "mos_ss", "mos_ff"],
                        help="MOS corners, applied to the LV and the HV models (default: mos_tt mos_ss mos_ff)")
    parser.add_argument("--temps", nargs="+", type=float, default=[-40.0, 27.0, 85.0], help="temperatures in C")
    parser.add_argument("--res", nargs="+", default=["res_typ"], help="resistor corners (default: res_typ)")
    parser.add_argument("--vdd", nargs="+", type=float, default=[1.5], help="VDD values in V (default: 1.5)")
    parser.add_argument("--vtune", nargs="+", type=float, default=[0.0, 1.5], help="vtune values in V")
    parser.add_argument("--jobs", type=int, default=4, help="ngspice runs in parallel (default: 4)")
    parser.add_argument("--threads", type=int, default=3, help="threads of each ngspice run (default: 3)")
    parser.add_argument("--vpeak-max", type=float, default=V_PEAK_MAX,
                        help=f"a tank node above this fails the run, 0 only reports it (default: {V_PEAK_MAX} V)")
    parser.add_argument("--csv", required=True, help="output table")
    args = parser.parse_args()

    run_dir = os.path.join(os.path.dirname(os.path.abspath(args.netlist)), "corners")
    os.makedirs(run_dir, exist_ok=True)
    jobs = []
    for corner, res, temp, vdd, vtune in itertools.product(args.corners, args.res, args.temps, args.vdd, args.vtune):
        name = f"{corner}_{res}_t{temp:g}_vdd{vdd:g}_vt{vtune:g}"
        path = os.path.join(run_dir, f"{name}.spice")
        with open(path, "w") as f:
            f.write(deck(args.netlist, corner, res, temp, vdd, vtune, args.threads))
        jobs.append({"deck": path, "corner": corner, "res": res, "temp": temp, "vdd": vdd, "vtune": vtune})

    print(f"sim_corners.py: {len(jobs)} transients, {args.jobs} at a time, in {run_dir}")
    rows, failed = [], 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for job, v in pool.map(run, jobs):
            row = {k: job[k] for k in ("corner", "res", "temp", "vdd", "vtune")}
            swing = v.get("vtank_max", math.nan) - v.get("vtank_min", math.nan)
            if "f0" not in v or not swing >= V_SWING_MIN:
                status = "no oscillation"
            elif args.vpeak_max > 0 and v["vtank_max"] > args.vpeak_max:
                status = f"peak above {args.vpeak_max} V"
            else:
                status = "ok"
            failed += status != "ok"
            vpp = v.get("vout_pp", math.nan)
            row.update({
                "f0_ghz": v.get("f0", math.nan) / 1e9,
                "vtank_max_v": v.get("vtank_max", math.nan),
                "vtank_min_v": v.get("vtank_min", math.nan),
                "pout_dbm": 10 * math.log10((vpp / 2) ** 2 / 2 / R_LOAD / 1e-3) if vpp > 0 else math.nan,
                "idd_ma": -v.get("idd", math.nan) * 1e3,
                "vtap_v": v.get("vtap", math.nan),
                "status": status,
            })
            rows.append(row)
            print(f"  {row['corner']:7s} {row['res']:7s} {row['temp']:6.0f} C  VDD {row['vdd']:.2f} V  vtune {row['vtune']:.2f} V:  "
                  f"{row['f0_ghz']:7.3f} GHz  tank {row['vtank_min_v']:.3f} V to {row['vtank_max_v']:.3f} V  "
                  f"{row['pout_dbm']:6.2f} dBm  tap {row['vtap_v']:.3f} V  VDD {row['idd_ma']:.2f} mA  {status}")

    os.makedirs(os.path.dirname(os.path.abspath(args.csv)), exist_ok=True)
    with open(args.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    ok = [r for r in rows if r["status"] == "ok"]
    if ok:
        print(f"sim_corners.py: f0 {min(r['f0_ghz'] for r in ok):.3f} GHz to {max(r['f0_ghz'] for r in ok):.3f} GHz, "
              f"highest tank node {max(r['vtank_max_v'] for r in ok):.3f} V, "
              f"lowest output {min(r['pout_dbm'] for r in ok):.2f} dBm, wrote {args.csv}")
    if failed:
        sys.exit(f"sim_corners.py: {failed} of {len(rows)} corners failed, see the status column")


if __name__ == "__main__":
    main()
