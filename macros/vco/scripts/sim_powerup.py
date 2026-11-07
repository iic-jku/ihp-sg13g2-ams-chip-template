# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Run the power-up and enable transient of the post-layout vco_top over VDD and di_en orders and corners and measure it.

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
DRIFT_AT = 0.8  # of the enable window: the output and the current there must already match its end
DRIFT_MAX = 1.0  # %, above this the window is too short to call anything settled

# Times in s, overriding the .param lines of the bench. Tr is the ramp of VDD, Ten_r the rise of di_en, Tdis its fall.
SEQUENCES = {
    # VDD first, then di_en up and down. The bias filters take the buffer current to 99 % in 6.3 us at worst,
    # and the 2 us after di_en falls show the output while vbg_buf decays.
    "enable": dict(Tr=10e-9, Tvdd=0, Ten=100e-9, Ten_r=100e-12, Tdis=8.1e-6, Tstop=10.1e-6),
    # di_en stays low: nothing may oscillate, short enough for all corners
    "disabled": dict(Tr=10e-9, Tvdd=0, Ten=1, Ten_r=100e-12, Tdis=2, Tstop=100e-9),
    # The sequences below read only the tank's start and peak, the buffer does not settle in their windows.
    # Everything at once, di_en tied to VDD
    "together": dict(Tr=10e-9, Tvdd=0, Ten=0, Ten_r=10e-9, Tdis=1, Tstop=400e-9),
    # The same at a tenth of the ramp, the hardest step on the center tap
    "fast": dict(Tr=1e-9, Tvdd=0, Ten=0, Ten_r=1e-9, Tdis=1, Tstop=400e-9),
    # di_en comes from the digital side, so it can be high before VDD or rise after it
    "en_first": dict(Tr=10e-9, Tvdd=100e-9, Ten=0, Ten_r=10e-9, Tdis=1, Tstop=500e-9),
    "vdd_first": dict(Tr=10e-9, Tvdd=0, Ten=300e-9, Ten_r=10e-9, Tdis=1, Tstop=500e-9),
}
ALL_CORNERS = [(c, t, v) for c in ("mos_tt", "mos_ss", "mos_ff") for t in (-40.0, 27.0, 85.0) for v in (0.0, 1.5)]
# The nominal point, the two corners closest to not starting and the two with the highest tank node
WORST_CORNERS = [("mos_tt", 27.0, 0.75), ("mos_ss", -40.0, 0.0), ("mos_ss", 85.0, 0.0), ("mos_ff", -40.0, 0.0), ("mos_ff", -40.0, 1.5)]


def deck(src, seq, corner, temp, vtune, raw, threads):
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


def period_mean(t, y, tc):
    """Time-weighted mean of y over each period. The steps of ngspice are not uniform, so a plain mean of the samples is biased."""
    q = np.concatenate(([0.0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(t))))
    return np.diff(np.interp(tc, t, q)) / np.diff(tc)


def window_mean(t, y, mask):
    """Time-weighted mean of y over the samples in mask."""
    t, y = t[mask], y[mask]
    return np.trapezoid(y, t) / (t[-1] - t[0])


def frequency(tc_mid, mask):
    n = np.count_nonzero(mask)
    return (n - 1) / (tc_mid[mask][-1] - tc_mid[mask][0]) if n > 1 else math.nan


def per_period(raw):
    """Crossing times of the tank's differential voltage, and between them its swing, the output's, VDD's current and the tap's voltage."""
    t, vp, vn, vo = raw["time"], raw["v(x1.rf_p)"], raw["v(x1.rf_n)"], raw["v(vout_p)"]
    vd = vp - vn
    i = np.flatnonzero((vd[:-1] < 0) & (vd[1:] >= 0))
    if i.size < 3:
        return None
    tc = t[i] + (t[i + 1] - t[i]) * (0 - vd[i]) / (vd[i + 1] - vd[i])
    idx = i[:-1], i[1:]
    swing = np.array([np.ptp(vd[a:b + 1]) for a, b in zip(*idx)])
    vout = np.array([np.ptp(vo[a:b + 1]) for a, b in zip(*idx)])
    return tc, swing, vout, period_mean(t, -raw["i(vdd)"], tc), period_mean(t, raw["v(x1.vdd_core)"], tc)


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
    t_end = min(tm["Tdis"], tm["Tstop"])
    win = (t > t_end - SETTLED) & (t <= t_end)
    i_vdd, v_out = -raw["i(vdd)"], raw["v(vout_p)"]
    row["vtap_v"] = window_mean(t, raw["v(x1.vdd_core)"], win)
    if seq == "disabled":
        # Nothing may oscillate, so there are no periods to measure over
        row.update({
            "swing_v": np.ptp((raw["v(x1.rf_p)"] - raw["v(x1.rf_n)"])[win]),
            "vout_off_mv": np.ptp(v_out[win]) * 1e3,
            "idd_off_ua": window_mean(t, i_vdd, win) * 1e6,
        })
        return row
    pp = per_period(raw)
    if pp is None:
        return row
    tc, swing, vout, idd, vtap = pp
    tc_mid = tc[:-1]
    settled = (tc_mid > t_end - SETTLED) & (tc_mid <= t_end)
    if not settled.any():
        return row
    sw = swing[settled].mean()
    # The core starts once VDD is up and di_en has closed the tap feed's switch
    core_up = max(tm["Tvdd"] + tm["Tr"], tm["Ten"] + tm["Ten_r"])
    # Before di_en falls, so the run's end does not count as the output settling
    upto = tc_mid <= t_end
    row.update({
        "swing_v": sw,
        "vtank_settled_v": raw["v(x1.rf_p)"][win].max(),
        # From the moment the core can start: negative if the tank starts during the ramp
        "t_osc_ns": (first_settled(tc_mid[upto], swing[upto], 0.9 * sw) - core_up) * 1e9,
    })
    if seq == "enable":
        # Before di_en and after it falls the tank stands, so these read the waveforms and not the periods
        pre = (t > tm["Ten"] - SETTLED) & (t <= tm["Ten"])
        t_check = tm["Ten"] + DRIFT_AT * (tm["Tdis"] - tm["Ten"])
        check = (tc_mid > t_check - SETTLED) & (tc_mid <= t_check)
        last = t > tm["Tstop"] - SETTLED
        vo, i0, f0 = vout[settled].mean(), idd[settled].mean(), frequency(tc_mid, settled)
        vo_off = np.ptp(v_out[pre])
        drift = max(abs(vout[check].mean() / vo - 1), abs(idd[check].mean() / i0 - 1)) * 100
        avg = F_AVG / (tc[F_AVG:] - tc[:-F_AVG])
        off = avg[(tc[:-F_AVG] > t_end - SETTLED - F_AVG / f0) & (tc[F_AVG:] <= t_end)]
        f_final = off.mean() if off.size else f0
        bad = np.flatnonzero((np.abs(avg - f_final) > DF_SETTLED) & (tc[F_AVG:] <= t_end))
        # In bins of 1 ns from di_en's fall, against the disabled level
        edges = np.arange(tm["Tdis"], tm["Tstop"], 1e-9)
        k = np.searchsorted(t, edges)
        vbin = np.array([np.ptp(v_out[a:b + 1]) for a, b in zip(k[:-1], k[1:])])
        low = np.flatnonzero(vbin <= vo_off + 0.1 * (vo - vo_off))
        row.update({
            "f0_ghz": f0 / 1e9,
            "vout_pp_mv": vo * 1e3,
            "idd_ma": i0 * 1e3,
            "t_en90_ns": (first_settled(tc_mid[upto], vout[upto], 0.9 * vo) - tm["Ten"]) * 1e9,
            "t_en99_ns": (first_settled(tc_mid[upto], vout[upto], 0.99 * vo) - tm["Ten"]) * 1e9,
            "t_f10mhz_ns": (tc[F_AVG:][bad[-1] + 1] - tm["Ten"]) * 1e9 if bad.size and bad[-1] + 1 < avg.size else math.nan,
            "drift_pct": drift,
            "vout_off_mv": vo_off * 1e3,
            "idd_off_ua": window_mean(t, i_vdd, pre) * 1e6,
            "t_dis10_ns": (edges[low[0] + 1] - tm["Tdis"]) * 1e9 if low.size else math.nan,
            "vout_dis_mv": np.ptp(v_out[last]) * 1e3,
            "idd_dis_ua": window_mean(t, i_vdd, last) * 1e6,
        })
        if drift > DRIFT_MAX or abs(frequency(tc_mid, check) - f0) > DF_SETTLED or not low.size:
            row["status"] = "not settled"
    return row


def envelope(raw, points=600):
    """The whole run in time bins for a plot, also where the tank stands: time, frequency, swing, output, VDD's current and the tap's voltage."""
    t, vd = raw["time"], raw["v(x1.rf_p)"] - raw["v(x1.rf_n)"]
    tc = per_period(raw)[0]
    edges = np.linspace(t[0], t[-1], points + 1)
    rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (t >= a) & (t <= b)
        if np.count_nonzero(m) < 2:
            continue
        ncross = np.count_nonzero((tc >= a) & (tc <= b))
        rows.append((t[m][-1], ncross / (b - a) if ncross > 1 else np.nan, np.ptp(vd[m]), np.ptp(raw["v(vout_p)"][m]), window_mean(t, -raw["i(vdd)"], m), window_mean(t, raw["v(x1.vdd_core)"], m)))
    return np.array(rows)


def run(job):
    path = job["deck"]
    log = path[:-len(".spice")] + ".log"
    if not job["no_run"]:
        with open(log, "w", encoding="utf-8") as f:
            subprocess.run(["ngspice", "-b", path], stdout=f, stderr=subprocess.STDOUT, cwd=os.path.dirname(path), check=False)
    raw = read_raw(job["raw"]) if os.path.exists(job["raw"]) else None
    row = measure(raw, job["seq"]) if raw else {}
    env = envelope(raw) if raw and job.get("keep") and per_period(raw) else None
    # An enable run takes hours, so its rawfile stays for --no-run
    if raw and job["seq"] != "enable":
        os.remove(job["raw"])
    return job, row, env


def main():
    parser = argparse.ArgumentParser(description="Run the power-up and enable transient of the post-layout vco_top.")
    parser.add_argument("netlist", help="netlist of vco_top_tb_powerup_lpe, written by make netlist-xschem")
    parser.add_argument("--sequences", nargs="+", default=list(SEQUENCES), choices=list(SEQUENCES), help="which orders of VDD and di_en to run")
    parser.add_argument("--all-corners-for", nargs="+", default=["disabled"], help="sequences run at all 18 corners, the others at 5 (default: disabled)")
    parser.add_argument("--smoke", action="store_true", help="only the nominal point of each sequence")
    parser.add_argument("--jobs", type=int, default=4, help="ngspice runs in parallel (default: 4)")
    parser.add_argument("--threads", type=int, default=2, help="threads of each ngspice run, without a limit each takes every CPU (default: 2)")
    parser.add_argument("--vpeak-max", type=float, default=V_PEAK_MAX, help=f"a tank node above this fails the run (default: {V_PEAK_MAX} V)")
    parser.add_argument("--no-run", action="store_true", help="only measure the rawfiles of an earlier enable run, and write only those rows")
    parser.add_argument("--csv", required=True, help="output table")
    parser.add_argument("--data", help="per-period record of the nominal enable run, for the plot")
    args = parser.parse_args()

    run_dir = os.path.join(os.path.dirname(os.path.abspath(args.netlist)), "powerup")
    os.makedirs(run_dir, exist_ok=True)
    jobs = []
    for seq in ["enable"] if args.no_run else args.sequences:
        corners = WORST_CORNERS[:1] if args.smoke else ALL_CORNERS if seq in args.all_corners_for else WORST_CORNERS
        if seq in args.all_corners_for and not args.smoke:
            corners = WORST_CORNERS[:1] + corners  # the nominal point, which the corners do not hold
        for corner, temp, vtune in corners:
            name = f"{seq}_{corner}_t{temp:g}_vt{vtune:g}"
            path = os.path.join(run_dir, f"{name}.spice")
            raw = os.path.join(run_dir, f"{name}.raw")
            with open(path, "w", encoding="utf-8") as f:
                f.write(deck(args.netlist, seq, corner, temp, vtune, raw, args.threads))
            nominal = (corner, temp, vtune) == WORST_CORNERS[0]
            jobs.append({"deck": path, "raw": raw, "seq": seq, "corner": corner, "temp": temp, "vtune": vtune, "keep": seq == "enable" and nominal, "no_run": args.no_run})

    print(f"sim_powerup.py: {len(jobs)} transients, {args.jobs} at a time, in {run_dir}", flush=True)
    rows, failed = [], 0
    fields = ["seq", "corner", "temp", "vtune", "status", "f0_ghz", "swing_v", "vpeak_v", "vtank_settled_v", "t_osc_ns", "vtap_v", "vout_off_mv", "idd_off_ua", "vout_pp_mv", "idd_ma",
              "t_en90_ns", "t_en99_ns", "t_f10mhz_ns", "drift_pct", "t_dis10_ns", "vout_dis_mv", "idd_dis_ua"]
    os.makedirs(os.path.dirname(os.path.abspath(args.csv)), exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool, open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="")
        w.writeheader()
        for job, v, env in pool.map(run, jobs):
            row = {k: job[k] for k in ("seq", "corner", "temp", "vtune")}
            row.update(v)
            if not v:
                row["status"] = "no result, see the log"
            elif job["seq"] == "disabled":
                row["status"] = "ok" if v["swing_v"] < V_SWING_MIN else "oscillates while disabled"
            elif not v.get("swing_v", 0) >= V_SWING_MIN:
                row["status"] = "no oscillation"
            elif v["vpeak_v"] > args.vpeak_max:
                row["status"] = f"peak above {args.vpeak_max} V"
            else:
                row.setdefault("status", "ok")
            failed += row["status"] != "ok"
            rows.append(row)
            w.writerow({k: (f"{x:.5g}" if isinstance(x, float) else x) for k, x in row.items()})
            f.flush()
            g = lambda k: v.get(k, math.nan)  # noqa: E731
            print(f"  {row['seq']:10s} {row['corner']:7s} {row['temp']:4.0f} C vtune {row['vtune']:.2f}: swing {g('swing_v'):.3f} V  peak {g('vpeak_v'):.3f} V  t_osc {g('t_osc_ns'):5.2f} ns  "
                  f"{g('f0_ghz'):7.3f} GHz  out {g('vout_pp_mv'):5.1f} mV  t_en99 {g('t_en99_ns'):7.1f} ns  t_dis10 {g('t_dis10_ns'):6.1f} ns  {row['status']}", flush=True)
            if env is not None and args.data:
                os.makedirs(os.path.dirname(os.path.abspath(args.data)), exist_ok=True)
                np.savetxt(args.data, env, header="time f_avg_hz tank_swing_v vout_pp_v idd_a vtap_v", comments="", fmt="%.6e")
    started = [r for r in rows if "t_osc_ns" in r]
    if started:
        print(f"sim_powerup.py: highest node {max(r['vpeak_v'] for r in started):.3f} V, slowest start {max(r['t_osc_ns'] for r in started):.2f} ns, wrote {args.csv}")
    if failed:
        sys.exit(f"sim_powerup.py: {failed} of {len(rows)} runs failed, see the status column")


if __name__ == "__main__":
    main()
