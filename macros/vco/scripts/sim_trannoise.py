# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Run the VACASK transient noise of vco_top over seeds and read the phase noise from the tank's zero crossings, against PNOISE.

import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from scipy.signal import welch

# The rawfile module moved into the vacask package in 2026-10
try:
    from vacask.rawfile import rawread
except ImportError:
    from rawfile import rawread

NOISE_SETTLE = 500e-9  # s dropped from each record, in which the noise of the slow bias filters builds up
OFFSETS = [1e6, 2e6, 3e6, 5e6, 10e6, 20e6, 50e6, 100e6]  # Hz at which the comparison is printed


def run_seed(args):
    src, seed, stop = args
    run_dir = os.path.dirname(os.path.abspath(src))
    with open(src, encoding="utf-8") as f:
        text = f.read()
    # VACASK names a rawfile after its analysis, so the benches and seeds that share the folder need their own names
    stem = os.path.basename(src).replace(".spectre", "")
    text = text.replace("analysis settle ", f"analysis {stem}_settle_s{seed} ").replace("analysis noisy ", f"analysis {stem}_noisy_s{seed} ")
    text = re.sub(r"\bnoiseseed=\d+", f"noiseseed={seed}", text)
    if stop:
        text = re.sub(r"(analysis \S+_noisy_s\d+ tran stop=)\S+", rf"\g<1>{stop}", text)
    deck = src.replace(".spectre", f"_s{seed}.spectre")
    with open(deck, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    log = deck.replace(".spectre", ".log")
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run(["vacask", os.path.basename(deck)], stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT, cwd=run_dir, check=False)
    return seed, r.returncode, os.path.join(run_dir, f"{stem}_noisy_s{seed}.raw")


def crossings(raw_path):
    """Rising zero crossings of the tank's differential voltage, between the samples by linear interpolation."""
    data = rawread(raw_path).get()
    t = np.asarray(data["time"])
    vd = np.asarray(data["x1:rf_p"]) - np.asarray(data["x1:rf_n"])
    i = np.flatnonzero((vd[:-1] < 0) & (vd[1:] >= 0))
    return t[i] + (t[i + 1] - t[i]) * (0 - vd[i]) / (vd[i + 1] - vd[i])


def phase_noise(all_crossings, f_res):
    """L(f) from the period-to-period phase difference, which is white where the phase itself is a random walk that a window would leak.

    Every seed starts from the same stored state, so what they share is a drift and not noise: it is subtracted, and the factor N/(N-1)
    gives back each seed's own share of that mean.
    """
    tc = [t[t > t[0] + NOISE_SETTLE] for t in all_crossings]
    n = min(t.size for t in tc)
    periods = np.array([np.diff(t[:n]) for t in tc])
    t_mean = periods.mean()
    dphi = 2 * np.pi * (periods - t_mean) / t_mean
    n_seeds = dphi.shape[0]
    if n_seeds > 1:
        dphi = (dphi - dphi.mean(axis=0)) * np.sqrt(n_seeds / (n_seeds - 1))
    f0 = 1 / t_mean
    nperseg = min(int(f0 / f_res), dphi.shape[1])
    f, s = welch(dphi, fs=f0, window="hann", nperseg=nperseg, noverlap=nperseg // 2, detrend="constant", axis=1)
    # Bin 1 sits in the Hann main lobe of the removed mean and reads 0.8 dB low (5/6), the last bin is Nyquist, which welch does not double.
    f, s = f[2:-1], s[:, 2:-1]
    s_phi = s / (4 * np.sin(np.pi * f / f0) ** 2)
    per_seed = 10 * np.log10(s_phi / 2)
    return f0, f, per_seed, n * t_mean


def smooth(f, y, per_decade=20):
    """Means of the PSD over log-spaced bands, so that the scatter of single bins does not read as a difference.

    A band is labeled with the geometric mean of its own bins: the middle of its edges is up to 6 % off where it holds one bin.
    """
    n_bands = int(np.log10(f[-1] / f[0]) * per_decade)
    bands = np.minimum((np.log(f / f[0]) / np.log(f[-1] / f[0]) * n_bands).astype(int), n_bands - 1)
    out_f, out_y, out_n = [], [], []
    for band in np.unique(bands):
        m = bands == band
        out_f.append(np.exp(np.log(f[m]).mean()))
        out_y.append(10 * np.log10(np.mean(10 ** (y[m] / 10))))
        out_n.append(np.count_nonzero(m))
    return np.array(out_f), np.array(out_y), np.array(out_n)


def reference(pnoise, pss):
    """L(f) of the PNOISE run, as plot_vco_top.py reads it, in the bench's own data tables."""
    tab = np.genfromtxt(pnoise, names=True, deletechars="", usecols=(0, 1))
    with open(pss, encoding="utf-8") as f:
        head = f.readline().split()
    d = np.loadtxt(pss, skiprows=1)
    t = d[:, head.index("time")]
    vod = d[:, head.index("vout_p")] - d[:, head.index("vout_n")]
    grid = np.linspace(t[0], t[-1], 1024, endpoint=False)
    v1 = 2 * np.abs(np.fft.rfft(np.interp(grid, t, vod))[1]) / grid.size
    names = tab.dtype.names
    return tab[names[0]], 10 * np.log10(tab[names[1]] / (v1 ** 2 / 2))


def reference_at(f, f_pn, l_pn):
    """The PNOISE L(f) at the bands, NaN above its sweep, where np.interp would hold its last value up to half the carrier."""
    return np.interp(np.log10(f), np.log10(f_pn), l_pn, right=np.nan)


def main():
    parser = argparse.ArgumentParser(description="Run the VACASK transient noise of vco_top and compare it with PNOISE.")
    parser.add_argument("netlist", help="netlist of vco_top_tb_trannoise_vacask, written by make netlist-xschem")
    parser.add_argument("--seeds", type=int, default=8, help="number of seeds, one VACASK process each (default: 8)")
    parser.add_argument("--stop", help="length of the noisy record, overriding the bench, for a trial (for example 2n)")
    parser.add_argument("--no-run", action="store_true", help="only read the rawfiles of an earlier run")
    parser.add_argument("--fres", type=float, default=500e3, help="Welch resolution in Hz (default: 500 kHz)")
    parser.add_argument("--pnoise", required=True, help="PNOISE table of vco_top_tb_pss_vacask")
    parser.add_argument("--pss", required=True, help="PSS table of vco_top_tb_pss_vacask")
    parser.add_argument("--data", required=True, help="L(f) table to write")
    args = parser.parse_args()

    src = os.path.abspath(args.netlist)
    run_dir = os.path.dirname(src)
    if args.no_run:
        stem = os.path.basename(src).replace(".spectre", "")
        raws = [os.path.join(run_dir, f"{stem}_noisy_s{s}.raw") for s in range(args.seeds)]
    else:
        print(f"sim_trannoise.py: {args.seeds} seeds in {run_dir}", flush=True)
        with ThreadPoolExecutor(max_workers=args.seeds) as pool:
            done = list(pool.map(run_seed, [(src, s, args.stop) for s in range(args.seeds)]))
        bad = [s for s, rc, _ in done if rc]
        raws = [r for s, rc, r in done if not rc]
        print(f"sim_trannoise.py: {len(raws)} seeds finished" + (f", seeds {bad} aborted" if bad else ""), flush=True)
        if args.stop:
            print("sim_trannoise.py: trial run, no spectrum")
            sys.exit(1 if bad else 0)
    if len(raws) < 2:
        sys.exit("sim_trannoise.py: fewer than two seeds finished")

    f0, f, per_seed, length = phase_noise([crossings(r) for r in raws], args.fres)
    mean = 10 * np.log10(np.mean(10 ** (per_seed / 10), axis=0))
    fb, lb, _ = smooth(f, mean)
    spread = np.array([smooth(f, s)[1] for s in per_seed]).std(axis=0) / np.sqrt(per_seed.shape[0])
    f_pn, l_pn = reference(args.pnoise, args.pss)
    np.savetxt(args.data, np.column_stack((fb, lb, spread, reference_at(fb, f_pn, l_pn))),
               header="f_offset_hz L_trannoise_dbc_hz seed_error_db L_pnoise_dbc_hz", comments="", fmt="%.6e")
    print(f"sim_trannoise.py: {f0 / 1e9:.3f} GHz, {per_seed.shape[0]} seeds of {length * 1e6:.2f} us, wrote {args.data}")
    for off in OFFSETS:
        if fb[0] <= off <= fb[-1]:
            lt = np.interp(np.log10(off), np.log10(fb), lb)
            lp = np.interp(np.log10(off), np.log10(f_pn), l_pn)
            e = np.interp(np.log10(off), np.log10(fb), spread)
            print(f"  {off / 1e6:6.0f} MHz: transient noise {lt:7.1f} dBc/Hz (+- {e:.1f} dB), PNOISE {lp:7.1f} dBc/Hz, difference {lt - lp:+.1f} dB")


if __name__ == "__main__":
    main()
