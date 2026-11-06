# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Run the power-up and enable transient of the post-layout vco_top over supply orders and corners and measure it per period.

import argparse
import csv
import math
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

# The peak voltage the thin-oxide devices of the pair may see, as in sim_corners.py
V_PEAK_MAX = 1.5
V_SWING_MIN = 0.5
SETTLED = 20e-9  # s, the window that defines the settled values, before di_en falls or the run ends
F_AVG = 100  # periods of the moving average that reads the frequency's settling
DF_SETTLED = 10e6  # Hz, how close to its settled value the frequency has to come

# Times in s, overriding the .param lines of the bench. Tr is the supply ramp, Ten_r the rise of di_en, Tdis its fall.
SEQUENCES = {
    # Supplies first, then di_en up and down: what the enable does to the output and to the running core
    "enable": dict(Tr=10e-9, Tvdd=0, Tcore=0, Ten=100e-9, Ten_r=100e-12, Tdis=460e-9, Tstop=500e-9),
    # Everything at once, di_en tied to VDD
    "together": dict(Tr=10e-9, Tvdd=0, Tcore=0, Ten=0, Ten_r=10e-9, Tdis=1, Tstop=400e-9),
    # The same at a tenth of the ramp, the hardest step on the center tap
    "fast": dict(Tr=1e-9, Tvdd=0, Tcore=0, Ten=0, Ten_r=1e-9, Tdis=1, Tstop=400e-9),
    # vdd_core has its own pad, so either supply can come first
    "core_first": dict(Tr=10e-9, Tvdd=100e-9, Tcore=0, Ten=100e-9, Ten_r=10e-9, Tdis=1, Tstop=500e-9),
    "vdd_first": dict(Tr=10e-9, Tvdd=0, Tcore=300e-9, Ten=0, Ten_r=10e-9, Tdis=1, Tstop=500e-9),
}
ALL_CORNERS = [(c, t, v) for c in ("mos_tt", "mos_ss", "mos_ff") for t in (-40.0, 27.0, 85.0) for v in (0.0, 1.5)]
# The nominal point, the two corners closest to not starting and the two with the highest tank node
WORST_CORNERS = [("mos_tt", 27.0, 0.75), ("mos_ss", -40.0, 0.0), ("mos_ss", 85.0, 0.0), ("mos_ff", -40.0, 0.0), ("mos_ff", -40.0, 1.5)]


def deck(src, seq, corner, temp, vcore, vtune, raw, threads):
    times = SEQUENCES[seq]
    netlist_dir = os.path.dirname(os.path.abspath(src))
    out = []
    with open(src, encoding="utf-8") as f:
        for line in f:
            s = line.rstrip("\n")
            if s.startswith(".include ") and not os.path.isabs(s.split()[1]):
                s = ".include " + os.path.normpath(os.path.join(netlist_dir, s.split()[1]))
            s = re.sub(r"^\.lib (cornerMOS(lv|hv)\.lib) mos_\w+$", rf".lib \1 {corner}", s)
            s = re.sub(r"^\.temp .*", f".temp {temp}", s)
            s = re.sub(r"^\.param Vcore=.*", f".param Vcore={vcore}", s)
            s = re.sub(r"^\.param Vtune=.*", f".param Vtune={vtune}", s)
            for name, value in times.items():
                s = re.sub(rf"^\.param {name}=.*", f".param {name}={value:g}", s)
            s = re.sub(r"^tran (\S+) \S+$", rf"tran \1 {times['Tstop']:g}", s)
            s = re.sub(r"^write \S+", f"write {raw}", s)
            if s == "set filetype=binary":
                s += f"\nset num_threads={threads}"
            if s.startswith(("wrdata", "set wr_", "+ v(")):
                s = "* " + s
            out.append(s)
    return "\n".join(out) + "\n"


def read_raw(path):
    """A binary ngspice rawfile with one real plot, as {vector name: array}."""
    with open(path, "rb") as f:
        names, n_vars, n_points = [], 0, 0
        while True:
            line = f.readline().decode("utf-8", "replace").strip()
            if line.startswith("No. Variables:"):
                n_vars = int(line.split(":")[1])
            elif line.startswith("No. Points:"):
                n_points = int(line.split(":")[1])
            elif line == "Variables:":
                names = [f.readline().decode("utf-8").split()[1].lower() for _ in range(n_vars)]
                # The current of a source reads vdd#branch or i(vdd), depending on the ngspice build
                names = [f"i({n[:-len('#branch')]})" if n.endswith("#branch") else n for n in names]
            elif line == "Binary:":
                break
            elif not line and f.peek(1) == b"":
                raise RuntimeError(f"{path}: not a binary rawfile")
        data = np.fromfile(f, dtype=np.float64, count=n_vars * n_points)
    n_points = data.size // n_vars
    return {name: data[i::n_vars][:n_points] for i, name in enumerate(names)}


def per_period(raw):
    """Crossing times of the tank's differential voltage, and between them its swing, the output's and the highest node."""
    t, vp, vn, vo = raw["time"], raw["v(x1.rf_p)"], raw["v(x1.rf_n)"], raw["v(vout_p)"]
    vd = vp - vn
    i = np.flatnonzero((vd[:-1] < 0) & (vd[1:] >= 0))
    if i.size < 3:
        return None
    tc = t[i] + (t[i + 1] - t[i]) * (0 - vd[i]) / (vd[i + 1] - vd[i])
    idx = i[:-1], i[1:]
    swing = np.array([np.ptp(vd[a:b + 1]) for a, b in zip(*idx)])
    vout = np.array([np.ptp(vo[a:b + 1]) for a, b in zip(*idx)])
    return tc, swing, vout


def first_settled(tc, y, target):
    """First time from which y stays at or above target."""
    below = np.flatnonzero(y < target)
    k = below[-1] + 1 if below.size else 0
    return tc[k] if k < tc.size else math.nan


def measure(raw, seq):
    tm = SEQUENCES[seq]
    t = raw["time"]
    vpeak = max(raw["v(x1.rf_p)"].max(), raw["v(x1.rf_n)"].max())
    row = {"vpeak_v": vpeak}
    pp = per_period(raw)
    if pp is None:
        return row
    tc, swing, vout = pp
    tc_mid = tc[:-1]
    t_end = min(tm["Tdis"], tm["Tstop"])
    settled = (tc_mid > t_end - SETTLED) & (tc_mid <= t_end)
    if not settled.any():
        return row
    win = (t > t_end - SETTLED) & (t <= t_end)
    sw, vo = swing[settled].mean(), vout[settled].mean()
    f0 = (np.count_nonzero(settled) - 1) / (tc_mid[settled][-1] - tc_mid[settled][0])
    core_up = tm["Tcore"] + tm["Tr"]
    # Before di_en falls, so the run's end does not count as the output settling
    upto = tc_mid <= t_end
    avg = F_AVG / (tc[F_AVG:] - tc[:-F_AVG])
    off = avg[(tc[:-F_AVG] > t_end - SETTLED - F_AVG / f0) & (tc[F_AVG:] <= t_end)]
    f_final = off.mean() if off.size else f0
    bad = np.flatnonzero((np.abs(avg - f_final) > DF_SETTLED) & (tc[F_AVG:] <= t_end))
    en_up = tm["Ten"] + (tm["Ten_r"] if seq != "enable" else 0)
    row.update({
        "f0_ghz": f0 / 1e9,
        "swing_v": sw,
        "vtank_settled_v": raw["v(x1.rf_p)"][win].max(),
        "vout_pp_mv": vo * 1e3,
        # From the moment the supply of the core is up: negative if the tank starts during the ramp
        "t_osc_ns": (first_settled(tc_mid[upto], swing[upto], 0.9 * sw) - core_up) * 1e9,
        "t_en90_ns": (first_settled(tc_mid[upto], vout[upto], 0.9 * vo) - en_up) * 1e9,
        "t_en99_ns": (first_settled(tc_mid[upto], vout[upto], 0.99 * vo) - en_up) * 1e9,
        "t_f10mhz_ns": (tc[F_AVG:][bad[-1] + 1] - en_up) * 1e9 if bad.size and bad[-1] + 1 < avg.size else math.nan,
        "idd_ma": -raw["i(vdd)"][win].mean() * 1e3,
        "icore_ma": -raw["i(vcore)"][win].mean() * 1e3,
    })
    if seq == "enable":
        before = (t > tm["Ten"] - SETTLED) & (t <= tm["Ten"])
        pre = (tc_mid > tm["Ten"] - SETTLED) & (tc_mid <= tm["Ten"])
        f_off = (np.count_nonzero(pre) - 1) / (tc_mid[pre][-1] - tc_mid[pre][0]) if pre.sum() > 1 else math.nan
        late = tc_mid > tm["Tdis"]
        low = np.flatnonzero(vout[late] <= 0.1 * vo)
        row.update({
            "df_en_mhz": (f0 - f_off) / 1e6,
            "vout_off_mv": vout[pre].mean() * 1e3 if pre.any() else math.nan,
            "t_dis10_ns": (tc_mid[late][low[0]] - tm["Tdis"]) * 1e9 if low.size else math.nan,
            "idd_off_ua": -raw["i(vdd)"][before].mean() * 1e6,
        })
    return row


def envelope(raw, points=600):
    """The run per period, thinned out for a plot: time, frequency, swing, output and supply currents."""
    pp = per_period(raw)
    tc, swing, vout = pp
    t = tc[:-1]
    avg = np.full(t.size, np.nan)
    avg[:-F_AVG + 1] = F_AVG / (tc[F_AVG:] - tc[:-F_AVG])
    grid = np.linspace(t[0], raw["time"][-1], points)
    k = np.minimum(np.searchsorted(t, grid), t.size - 1)
    return np.column_stack((t[k], avg[k], swing[k], vout[k],
                            -np.interp(t[k], raw["time"], raw["i(vdd)"]), -np.interp(t[k], raw["time"], raw["i(vcore)"])))


def run(job):
    path = job["deck"]
    log = path[:-len(".spice")] + ".log"
    with open(log, "w", encoding="utf-8") as f:
        subprocess.run(["ngspice", "-b", path], stdout=f, stderr=subprocess.STDOUT, cwd=os.path.dirname(path), check=False)
    raw = read_raw(job["raw"]) if os.path.exists(job["raw"]) else None
    row = measure(raw, job["seq"]) if raw else {}
    env = envelope(raw) if raw and job.get("keep") and per_period(raw) else None
    if raw:
        os.remove(job["raw"])
    return job, row, env


def main():
    parser = argparse.ArgumentParser(description="Run the power-up and enable transient of the post-layout vco_top.")
    parser.add_argument("netlist", help="netlist of vco_top_tb_powerup_lpe, written by make netlist-xschem")
    parser.add_argument("--vcore", type=float, default=0.79, help="vdd_core in V (default: 0.79)")
    parser.add_argument("--sequences", nargs="+", default=list(SEQUENCES), choices=list(SEQUENCES), help="which supply orders to run")
    parser.add_argument("--all-corners-for", nargs="+", default=["enable"], help="sequences run at all 18 corners, the others at 5 (default: enable)")
    parser.add_argument("--smoke", action="store_true", help="only the nominal point of each sequence")
    parser.add_argument("--jobs", type=int, default=4, help="ngspice runs in parallel (default: 4)")
    parser.add_argument("--threads", type=int, default=2, help="threads of each ngspice run, without a limit each takes every CPU (default: 2)")
    parser.add_argument("--vpeak-max", type=float, default=V_PEAK_MAX, help=f"a tank node above this fails the run (default: {V_PEAK_MAX} V)")
    parser.add_argument("--csv", required=True, help="output table")
    parser.add_argument("--data", help="per-period record of the nominal enable run, for the plot")
    args = parser.parse_args()

    run_dir = os.path.join(os.path.dirname(os.path.abspath(args.netlist)), "powerup")
    os.makedirs(run_dir, exist_ok=True)
    jobs = []
    for seq in args.sequences:
        corners = WORST_CORNERS[:1] if args.smoke else ALL_CORNERS if seq in args.all_corners_for else WORST_CORNERS
        if seq in args.all_corners_for and not args.smoke:
            corners = WORST_CORNERS[:1] + corners  # the nominal point, which the corners do not hold
        for corner, temp, vtune in corners:
            name = f"{seq}_{corner}_t{temp:g}_vt{vtune:g}"
            path = os.path.join(run_dir, f"{name}.spice")
            raw = os.path.join(run_dir, f"{name}.raw")
            with open(path, "w", encoding="utf-8") as f:
                f.write(deck(args.netlist, seq, corner, temp, args.vcore, vtune, raw, args.threads))
            nominal = (corner, temp, vtune) == WORST_CORNERS[0]
            jobs.append({"deck": path, "raw": raw, "seq": seq, "corner": corner, "temp": temp, "vtune": vtune, "keep": seq == "enable" and nominal})

    print(f"sim_powerup.py: {len(jobs)} transients, {args.jobs} at a time, in {run_dir}", flush=True)
    rows, failed = [], 0
    fields = ["seq", "corner", "temp", "vtune", "status", "f0_ghz", "swing_v", "vpeak_v", "vtank_settled_v", "vout_pp_mv", "t_osc_ns", "t_en90_ns", "t_en99_ns",
              "t_f10mhz_ns", "df_en_mhz", "vout_off_mv", "t_dis10_ns", "idd_ma", "icore_ma", "idd_off_ua"]
    os.makedirs(os.path.dirname(os.path.abspath(args.csv)), exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool, open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="")
        w.writeheader()
        for job, v, env in pool.map(run, jobs):
            row = {k: job[k] for k in ("seq", "corner", "temp", "vtune")}
            row.update(v)
            if not v.get("swing_v", 0) >= V_SWING_MIN:
                row["status"] = "no oscillation"
            elif v["vpeak_v"] > args.vpeak_max:
                row["status"] = f"peak above {args.vpeak_max} V"
            else:
                row["status"] = "ok"
            failed += row["status"] != "ok"
            rows.append(row)
            w.writerow({k: (f"{x:.5g}" if isinstance(x, float) else x) for k, x in row.items()})
            f.flush()
            g = lambda k: v.get(k, math.nan)  # noqa: E731
            print(f"  {row['seq']:10s} {row['corner']:7s} {row['temp']:4.0f} C vtune {row['vtune']:.2f}: {g('f0_ghz'):7.3f} GHz  swing {g('swing_v'):.3f} V  "
                  f"peak {g('vpeak_v'):.3f} V (settled {g('vtank_settled_v'):.3f})  t_osc {g('t_osc_ns'):7.2f} ns  t_en99 {g('t_en99_ns'):7.1f} ns  {row['status']}", flush=True)
            if env is not None and args.data:
                os.makedirs(os.path.dirname(os.path.abspath(args.data)), exist_ok=True)
                np.savetxt(args.data, env, header="time f_avg_hz tank_swing_v vout_pp_v idd_a icore_a", comments="", fmt="%.6e")
    ok = [r for r in rows if r["status"] == "ok"]
    if ok:
        print(f"sim_powerup.py: highest node {max(r['vpeak_v'] for r in ok):.3f} V, slowest start {max(r['t_osc_ns'] for r in ok):.2f} ns, wrote {args.csv}")
    if failed:
        sys.exit(f"sim_powerup.py: {failed} of {len(rows)} runs failed, see the status column")


if __name__ == "__main__":
    main()
