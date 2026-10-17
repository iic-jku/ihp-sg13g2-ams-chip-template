# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: Simon Dorrer
# Description: Plots of the tank coil, the EM result of verification/em/s-parameter/vco_ind.s3p against the snp2le model from the VACASK ACSP bench.
# Created: 17.10.2026
# Last Modified: 17.10.2026
# ============================================

# Imports
import numpy as np
import matplotlib.pyplot as plt
import skrf as rf
import ngspice2python as ng
from pathlib import Path
# ============================================

# Plotting Configuration
# ============================================
plt.close("all")

# Pure Matplotlib text rendering (no external LaTeX dependency)
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.size": 14,
})

Z0 = 50.0  # port impedance of the EM ports and of the bench (Ohm)
F_MARK = 20e9  # frequency the summary is printed at (Hz)
# =========================================================================


def save(fig, figures_dir, name, columns=None, header=None):
    fig.savefig(str(figures_dir / f"{name}.svg"), bbox_inches='tight')
    fig.savefig(str(figures_dir / f"{name}.pdf"), bbox_inches='tight')
    if columns is not None:
        np.savetxt(str(figures_dir / f"{name}.csv"), np.column_stack(columns), comments="", header=header, delimiter=",")


def diff_lq(f, s):
    """Differential inductance and Q between ports 1 and 2, with the center tap (port 3) open."""
    eye = np.eye(s.shape[1])
    z = Z0 * np.linalg.solve((eye - s).transpose(0, 2, 1), (eye + s).transpose(0, 2, 1)).transpose(0, 2, 1)
    zd = z[:, 0, 0] + z[:, 1, 1] - z[:, 0, 1] - z[:, 1, 0]
    w = 2 * np.pi * np.where(f > 0, f, np.nan)
    return zd.imag / w, zd.imag / zd.real


def load_acsp(file, ports=3):
    """S-matrix from the VACASK ACSP table, columns re(s(i,j)) and im(s(i,j)) as written by vacask2data.py."""
    f = ng.loadngspicecol(file, "frequency")
    s = np.zeros((len(f), ports, ports), dtype=complex)
    for i in range(ports):
        for j in range(ports):
            name = f"s({i + 1},{j + 1})"
            try:
                re = ng.loadngspicecol(file, f"re({name})")
                im = ng.loadngspicecol(file, f"im({name})")
            except ValueError:  # a purely real vector is written as one column
                re, im = ng.loadngspicecol(file, name), 0.0
            s[:, i, j] = re + 1j * im
    return f, s


def plot_coil(em_file, acsp_file, figures_dir):
    em = rf.Network(str(em_file))
    if em.z0.size and not np.allclose(em.z0, Z0):
        em.renormalize(Z0)
    f_em, s_em = em.f, em.s
    l_em, q_em = diff_lq(f_em, s_em)
    have_model = acsp_file.exists()
    if have_model:
        f_mod, s_mod = load_acsp(str(acsp_file))
        l_mod, q_mod = diff_lq(f_mod, s_mod)

    fig, ax = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    ax[0, 0].plot(f_em / 1e9, l_em * 1e12, 'o', markersize=4, color='#1f77b4', label='EM (Palace)')
    ax[0, 1].plot(f_em / 1e9, q_em, 'o', markersize=4, color='#1f77b4', label='EM (Palace)')
    if have_model:
        ax[0, 0].plot(f_mod / 1e9, l_mod * 1e12, '-', linewidth=2.0, color='#ff6b35', label='Model (ACSP)')
        ax[0, 1].plot(f_mod / 1e9, q_mod, '-', linewidth=2.0, color='#ff6b35', label='Model (ACSP)')
    ax[0, 0].set_ylabel(r'$L_\mathrm{diff}$ (pH)')
    ax[0, 0].set_ylim(0, 2 * np.nanmax(l_em[f_em <= 30e9]) * 1e12)
    ax[0, 1].set_ylabel(r'$Q_\mathrm{diff}$')
    ax[0, 1].set_ylim(bottom=0)

    colors = ['#1f77b4', '#2ca02c', '#d62728']
    for k, (i, j) in enumerate([(0, 0), (1, 1), (2, 2)]):
        ax[1, 0].plot(f_em / 1e9, 20 * np.log10(np.abs(s_em[:, i, j])), 'o', markersize=3, color=colors[k])
        if have_model:
            ax[1, 0].plot(f_mod / 1e9, 20 * np.log10(np.abs(s_mod[:, i, j])), '-', color=colors[k], label=f'$S_{{{i + 1}{j + 1}}}$')
    for k, (i, j) in enumerate([(1, 0), (2, 0), (2, 1)]):
        ax[1, 1].plot(f_em / 1e9, 20 * np.log10(np.abs(s_em[:, i, j])), 'o', markersize=3, color=colors[k])
        if have_model:
            ax[1, 1].plot(f_mod / 1e9, 20 * np.log10(np.abs(s_mod[:, i, j])), '-', color=colors[k], label=f'$S_{{{i + 1}{j + 1}}}$')
    ax[1, 0].set_ylabel('Reflection (dB)')
    ax[1, 1].set_ylabel('Transmission (dB)')

    for a in ax.flat:
        a.axvline(F_MARK / 1e9, color='gray', linestyle=':', linewidth=1.0)
        a.grid(True, alpha=0.3)
        a.legend(loc='best', fontsize=11)
    for a in ax[1]:
        a.set_xlabel('Frequency (GHz)')
    fig.suptitle('Tank coil: EM (dots) vs. snp2le model (lines)' if have_model else 'Tank coil: EM result')
    plt.tight_layout()

    k_em = np.argmin(np.abs(f_em - F_MARK))
    print(f"EM:    L_diff = {l_em[k_em] * 1e12:.1f} pH, Q_diff = {q_em[k_em]:.1f} at {f_em[k_em] / 1e9:.2f} GHz")
    if have_model:
        k_mod = np.argmin(np.abs(f_mod - f_em[k_em]))
        print(f"Model: L_diff = {l_mod[k_mod] * 1e12:.1f} pH, Q_diff = {q_mod[k_mod]:.1f} at {f_mod[k_mod] / 1e9:.2f} GHz")
        # Model resampled on the EM grid, so the CSV holds one table
        l_mod_em = np.interp(f_em, f_mod, l_mod)
        q_mod_em = np.interp(f_em, f_mod, q_mod)
        save(fig, figures_dir, "vco_ind_tb_acsp_vacask", (f_em, l_em, q_em, l_mod_em, q_mod_em),
             "f_hz,ldiff_em_h,qdiff_em,ldiff_model_h,qdiff_model")
    else:
        save(fig, figures_dir, "vco_ind_em", (f_em, l_em, q_em), "f_hz,ldiff_em_h,qdiff_em")


def main():
    # Resolve data and output paths relative to this script
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    em_file = script_dir.parents[2] / "verification" / "em" / "s-parameter" / "vco_ind.s3p"

    if not em_file.exists():
        raise SystemExit(f"plot_vco_ind.py: {em_file} not found, run make sim-em and make copy-sparam first")
    plot_coil(em_file, data_dir / "vco_ind_tb_acsp_vacask_sp1.txt", figures_dir)

    # Open the plot windows (blocks until they are closed)
    plt.show()
    # ============================================


# Main Execution
if __name__ == '__main__':
    main()
# ==============================================================================
