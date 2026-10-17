# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: Simon Dorrer
# Description: Plots of the VCO top macro from the ngspice transient, the VACASK PSS, PNOISE and PAC bench and the VACASK tuning bench.
# Created: 17.10.2026
# Last Modified: 17.10.2026
# ============================================

# Imports
import re
import numpy as np
import matplotlib.pyplot as plt
import ngspice2python as ng
from pathlib import Path
# ============================================

# Plotting Configuration
# ============================================
# Interactive mode stays off: the plt.show() at the end of main() then blocks in the GUI
# event loop, which is what draws the windows in the first place.
plt.close("all")

# Pure Matplotlib text rendering (no external LaTeX dependency)
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.size": 14,
})

R_LOAD = 50.0  # load per output in the benches (Ohm)
# =========================================================================


def save(fig, figures_dir, name, columns=None, header=None):
    fig.savefig(str(figures_dir / f"{name}.svg"), bbox_inches='tight')
    fig.savefig(str(figures_dir / f"{name}.pdf"), bbox_inches='tight')
    if columns is not None:
        np.savetxt(str(figures_dir / f"{name}.csv"), np.column_stack(columns), comments="", header=header, delimiter=",")


def one_period_spectrum(t, v, n=1024):
    """Fourier coefficients (peak amplitudes, complex) of one period of a PSS waveform, resampled on a uniform grid."""
    T = t[-1] - t[0]
    tu = t[0] + np.arange(n) * T / n
    c = np.fft.rfft(np.interp(tu, t, v)) / n
    c[1:] *= 2
    return T, c


def complex_col(file, name):
    return ng.loadngspicecol(file, f"re({name})") + 1j * ng.loadngspicecol(file, f"im({name})")


def plot_tran(data_dir, figures_dir):
    """ngspice transient: start-up and steady state."""
    file = str(data_dir / "vco_top_tb_tran.txt")
    time = ng.loadngspicecol(file, "time")
    vp = ng.loadngspicecol(file, "v(x1.rf_p)")
    vn = ng.loadngspicecol(file, "v(x1.rf_n)")
    op = ng.loadngspicecol(file, "v(vout_p)")
    on = ng.loadngspicecol(file, "v(vout_n)")
    t_ns = time * 1e9

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle('VCO Top - Transient Response (ngspice)')
    ax1.plot(t_ns, vp - vn, color='#0c5da5', linewidth=1.2, label=r'$V_\mathrm{rf,p} - V_\mathrm{rf,n}$ (tank)')
    ax1.set_xlabel(r'$t$ (ns)')
    ax1.set_ylabel(r'$V$ (V)')
    ax1.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax1.legend(loc='upper right')
    m = time > time[-1] - 200e-12
    ax2.plot(t_ns[m], vp[m], color='#0c5da5', linewidth=2.0, label=r'$V_\mathrm{rf,p}$')
    ax2.plot(t_ns[m], vn[m], color='#ff6b35', linewidth=2.0, linestyle='--', label=r'$V_\mathrm{rf,n}$')
    ax2.plot(t_ns[m], op[m] - on[m], color='#2f855a', linewidth=2.0, label=r'$V_\mathrm{out,p} - V_\mathrm{out,n}$')
    ax2.set_xlabel(r'$t$ (ns)')
    ax2.set_ylabel(r'$V$ (V)')
    ax2.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax2.legend(loc='upper right')
    plt.tight_layout()
    save(fig, figures_dir, "vco_top_tb_tran", (t_ns, vp, vn, op, on), "time_ns,v_rf_p,v_rf_n,v_out_p,v_out_n")


def plot_pss(data_dir, figures_dir):
    """VACASK PSS waveform and output spectrum, phase noise from PNOISE, tuning gain from PAC."""
    tb = "vco_top_tb_pss_vacask"
    pss = str(data_dir / f"{tb}_pss.txt")
    t = ng.loadngspicecol(pss, "time")
    vp = ng.loadngspicecol(pss, "x1:rf_p")
    vn = ng.loadngspicecol(pss, "x1:rf_n")
    vod = ng.loadngspicecol(pss, "vout_p") - ng.loadngspicecol(pss, "vout_n")
    T, c_out = one_period_spectrum(t, vod)
    _, c_op = one_period_spectrum(t, ng.loadngspicecol(pss, "vout_p"))
    f0 = 1 / T
    v1 = abs(c_out[1])
    print(f"PSS: f0 = {f0 / 1e9:.3f} GHz, differential output fundamental {v1 * 1e3:.1f} mV, "
          f"{10 * np.log10(abs(c_op[1]) ** 2 / 2 / R_LOAD / 1e-3):.2f} dBm per output")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle(f'VCO Top - Periodic Steady State (VACASK), $f_0$ = {f0 / 1e9:.3f} GHz')
    ax1.plot(t * 1e12, vp, color='#0c5da5', linewidth=2.0, label=r'$V_\mathrm{rf,p}$')
    ax1.plot(t * 1e12, vn, color='#ff6b35', linewidth=2.0, linestyle='--', label=r'$V_\mathrm{rf,n}$')
    ax1.plot(t * 1e12, vod, color='#2f855a', linewidth=2.0, label=r'$V_\mathrm{out,p} - V_\mathrm{out,n}$')
    ax1.set_xlabel(r'$t$ (ps)')
    ax1.set_ylabel(r'$V$ (V)')
    ax1.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax1.legend(loc='upper right')
    k = np.arange(1, 8)
    p_dbm = 10 * np.log10(np.abs(c_op[k]) ** 2 / 2 / R_LOAD / 1e-3)
    ax2.stem(k * f0 / 1e9, p_dbm, bottom=-80, basefmt=' ')
    ax2.set_xlabel(r'$f$ (GHz)')
    ax2.set_ylabel(r'$P_\mathrm{out,p}$ (dBm)')
    ax2.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    plt.tight_layout()
    save(fig, figures_dir, f"{tb}_pss", (t * 1e12, vp, vn, vod), "time_ps,v_rf_p,v_rf_n,v_out_diff")

    # Phase noise: output noise around the first harmonic against the carrier's mean square
    pn = str(data_dir / f"{tb}_pnoise.txt")
    fm = ng.loadngspicecol(pn, "frequency")
    onoise = ng.loadngspicecol(pn, "onoise")
    L = 10 * np.log10(onoise / (v1 ** 2 / 2))
    L1M = np.interp(6, np.log10(fm), L)
    print(f"PNOISE: L(1 MHz) = {L1M:.1f} dBc/Hz")
    # Tuning gain: upper FM sideband of a 1 V tone on vtune, K = 2 fm |V_usb| / |V_1|
    pac = str(data_dir / f"{tb}_pac.txt")
    fa = ng.loadngspicecol(pac, "frequency")
    vusb = complex_col(pac, "vout_p;1") - complex_col(pac, "vout_n;1")
    kvco = 2 * fa * np.abs(vusb) / v1
    # below about 1 MHz the linearised phase is pinned and the sideband no longer grows as 1/f, see README
    print(f"PAC: K_VCO = {np.interp(7, np.log10(fa), kvco) / 1e9:.3f} GHz/V at 10 MHz")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle('VCO Top - Phase Noise (PNOISE) and Tuning Gain (PAC)')
    ax1.semilogx(fm, L, color='#0c5da5', linewidth=2.4)
    ax1.plot(1e6, L1M, 'o', color='#ff6b35', label=f'{L1M:.1f} dBc/Hz at 1 MHz')
    ax1.set_xlabel(r'$f_\mathrm{offset}$ (Hz)')
    ax1.set_ylabel(r'$\mathcal{L}$ (dBc/Hz)')
    ax1.grid(visible=True, which='both', linestyle='--', alpha=0.45)
    ax1.legend(loc='upper right')
    ax2.semilogx(fa, kvco / 1e9, color='#2f855a', linewidth=2.4)
    ax2.set_xlabel(r'$f_\mathrm{m}$ (Hz)')
    ax2.set_ylabel(r'$K_\mathrm{VCO}$ (GHz/V)')
    ax2.grid(visible=True, which='both', linestyle='--', alpha=0.45)
    plt.tight_layout()
    save(fig, figures_dir, f"{tb}_pnoise_pac", (fm, L, kvco), "f_offset_hz,L_dbc_hz,kvco_hz_per_v")


def frequency(t, v, t_start):
    """Oscillation frequency from the rising zero crossings of v after t_start, linearly interpolated."""
    i = np.where((v[:-1] < 0) & (v[1:] >= 0) & (t[:-1] >= t_start))[0]
    tz = t[i] - v[i] * (t[i + 1] - t[i]) / (v[i + 1] - v[i])
    return (len(tz) - 1) / (tz[-1] - tz[0])


def plot_tune(data_dir, figures_dir):
    """VACASK tuning curve: one transient per tuning voltage, the voltage is in the file name (tune_0p25 = 0.25 V)."""
    tb = "vco_top_tb_tune_vacask"
    files = sorted(data_dir.glob(f"{tb}_tune_*.txt"))
    vt = np.array([float(re.search(r"tune_(\d+p\d+)", f.stem).group(1).replace("p", ".")) for f in files])
    f0 = []
    for f in files:
        t = ng.loadngspicecol(str(f), "time")
        vd = ng.loadngspicecol(str(f), "x1:rf_p") - ng.loadngspicecol(str(f), "x1:rf_n")
        f0.append(frequency(t, vd, t[-1] - 0.5e-9))
    f0 = np.array(f0)
    order = np.argsort(vt)
    vt, f0 = vt[order], f0[order]
    kvco = np.gradient(f0, vt)
    for v, f, k in zip(vt, f0, kvco):
        print(f"tune: vtune = {v:.2f} V, f0 = {f / 1e9:.3f} GHz, K_VCO = {k / 1e9:.2f} GHz/V")

    fig, ax1 = plt.subplots(figsize=(10, 6.2))
    fig.suptitle('VCO Top - Tuning Curve (VACASK transient)')
    ax1.plot(vt, f0 / 1e9, 'o-', color='#0c5da5', linewidth=2.4, label=r'$f_0$')
    ax1.set_xlabel(r'$V_\mathrm{tune}$ (V)')
    ax1.set_ylabel(r'$f_0$ (GHz)', color='#0c5da5')
    ax1.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax2 = ax1.twinx()
    ax2.plot(vt, kvco / 1e9, 's--', color='#ff6b35', linewidth=2.0, label=r'$K_\mathrm{VCO}$')
    ax2.set_ylabel(r'$K_\mathrm{VCO}$ (GHz/V)', color='#ff6b35')
    plt.tight_layout()
    save(fig, figures_dir, tb, (vt, f0, kvco), "vtune_v,f0_hz,kvco_hz_per_v")


def main():
    # Resolve data and output paths relative to this script
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Plot what the benches have written so far
    if (data_dir / "vco_top_tb_tran.txt").exists():
        plot_tran(data_dir, figures_dir)
    if (data_dir / "vco_top_tb_pss_vacask_pss.txt").exists():
        plot_pss(data_dir, figures_dir)
    if list(data_dir.glob("vco_top_tb_tune_vacask_tune_*.txt")):
        plot_tune(data_dir, figures_dir)

    # Open the plot windows (blocks until they are closed)
    plt.show()
    # ============================================


# Main Execution
if __name__ == '__main__':
    main()
# ==============================================================================
