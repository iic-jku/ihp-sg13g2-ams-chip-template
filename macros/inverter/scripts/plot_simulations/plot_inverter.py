# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: Simon Dorrer
# Description: AC and DC plots for the inverter macro based on ngspice exports.
# Created: 06.05.2026
# Last Modified: 06.05.2026
# ============================================

# Imports
import numpy as np
import matplotlib.pyplot as plt
import ngspice2python as ng
from pathlib import Path
# ============================================

# Plotting Configuration
# ============================================
# Enable interactive mode so plots do not block execution
plt.ion()
plt.close("all")

# Matplotlib Settings
# %matplotlib qt
# %matplotlib inline

# Pure Matplotlib text rendering (no external LaTeX dependency)
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.size": 14,
})
# =========================================================================

def main():
    # Resolve data and output paths relative to this script
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load ngspice open-loop AC simulation data
    # ------------------------------------------------------------------
    ngspice_file = data_dir / "inverter_tb_ac_ol.txt"

    data_frequency = ng.loadngspicecol(str(ngspice_file), "frequency")
    frequency = data_frequency[0::2]

    data_mag_dB = ng.loadngspicecol(str(ngspice_file), "v(Aol_dB)")
    mag_dB = data_mag_dB[0::2]

    data_phase = ng.loadngspicecol(str(ngspice_file), "v(Aol_arg)")
    phase_deg = data_phase[0::2]

    # ------------------------------------------------------------------
    # 2. Bode Plot (AC)
    # ------------------------------------------------------------------
    ac_color_mag = '#0c5da5'
    ac_color_phase = '#ff6b35'

    fig1, axs = plt.subplots(2)
    fig1.set_figwidth(10)
    fig1.set_figheight(7)
    fig1.suptitle('Inverter - AC Open-Loop Response')

    # Magnitude
    axs[0].set_xscale('log')
    axs[0].plot(frequency, mag_dB, color=ac_color_mag, linewidth=2.4)
    axs[0].set_xlabel('$f$ (Hz)')
    axs[0].set_ylabel(r'$|A_\mathrm{ol}(f)|$ (dB)')
    axs[0].set_xlim(1, 1e9)
    axs[0].set_ylim(-20, 40)
    axs[0].set_yticks(np.arange(-20, 40, 10.0))
    axs[0].grid(visible=True, which='both', linestyle='--', alpha=0.5)

    # Phase
    axs[1].set_xscale('log')
    axs[1].plot(frequency, phase_deg, color=ac_color_phase, linewidth=2.4)
    axs[1].set_xlabel('$f$ (Hz)')
    axs[1].set_ylabel(r'$\angle A_\mathrm{ol}(f)$ ($^\circ$)')
    axs[1].set_xlim(1, 1e9)
    axs[1].set_ylim(45, 185)
    axs[1].set_yticks(np.arange(45, 185, 45.0))
    axs[1].grid(visible=True, which='both', linestyle='--', alpha=0.5)

    # Characteristic Bode-plot values: DC gain, -3 dB cutoff, transit frequency.
    # Magnitude is monotonically decreasing in frequency, so reverse the
    # arrays to feed np.interp (which requires ascending xp).
    mag_dB_asc = mag_dB[::-1]
    freq_desc = frequency[::-1]
    phase_desc = phase_deg[::-1]

    Aol_dB = float(mag_dB[0])
    Aol_VV = 10.0 ** (Aol_dB / 20.0)
    f_cu = float(np.interp(Aol_dB - 3.0, mag_dB_asc, freq_desc))
    phase_cu = float(np.interp(Aol_dB - 3.0, mag_dB_asc, phase_desc))
    f_T = float(np.interp(0.0, mag_dB_asc, freq_desc))
    phase_T = float(np.interp(0.0, mag_dB_asc, phase_desc))

    def _fmt_hz(f):
        for prefix, scale in (('G', 1e9), ('M', 1e6), ('k', 1e3)):
            if f >= scale:
                return rf"{f/scale:.2f}\,\mathrm{{{prefix}Hz}}"
        return rf"{f:.2f}\,\mathrm{{Hz}}"

    marker_color = '#444444'
    line_kw = dict(color=marker_color, linestyle=':', linewidth=1.2, alpha=0.85)
    point_kw = dict(marker='o', color=marker_color, linestyle='None',
                    markersize=6, zorder=5)
    box_kw = dict(boxstyle='round,pad=0.4', fc='white',
                  ec=marker_color, alpha=0.9)

    # Magnitude markers (lines + dots)
    axs[0].axhline(Aol_dB, **line_kw)
    axs[0].axvline(f_cu, **line_kw)
    axs[0].axvline(f_T, **line_kw)
    axs[0].plot([frequency[0]], [Aol_dB], **point_kw)
    axs[0].plot([f_cu], [Aol_dB - 3.0], **point_kw)
    axs[0].plot([f_T], [0.0], **point_kw)

    # Magnitude info box (lower-left corner)
    mag_text = '\n'.join((
        rf'$A_\mathrm{{ol}} = {Aol_dB:.1f}\,\mathrm{{dB}}\;({Aol_VV:.1f}\,\mathrm{{V/V}})$',
        rf'$f_\mathrm{{cu}} = {_fmt_hz(f_cu)}$',
        rf'$f_\mathrm{{T}} = {_fmt_hz(f_T)}$',
    ))
    axs[0].text(0.02, 0.05, mag_text, transform=axs[0].transAxes,
                ha='left', va='bottom', color=marker_color, bbox=box_kw,
                zorder=6)

    # Phase markers (lines + dots)
    axs[1].axvline(f_cu, **line_kw)
    axs[1].axvline(f_T, **line_kw)
    axs[1].plot([f_cu], [phase_cu], **point_kw)
    axs[1].plot([f_T], [phase_T], **point_kw)

    # Phase info box (lower-left corner — empty for an inverting stage
    # whose phase starts near 180 deg and falls with frequency)
    phase_text = '\n'.join((
        rf'$\angle A_\mathrm{{ol}}(f_\mathrm{{cu}}) = {phase_cu:.1f}^\circ$',
        rf'$\angle A_\mathrm{{ol}}(f_\mathrm{{T}}) = {phase_T:.1f}^\circ$',
    ))
    axs[1].text(0.02, 0.05, phase_text, transform=axs[1].transAxes,
                ha='left', va='bottom', color=marker_color, bbox=box_kw,
                zorder=6)

    plt.tight_layout()
    plt.show()

    # ------------------------------------------------------------------
    # 3. Export AC figures and CSV
    # ------------------------------------------------------------------
    fig1.savefig(str(figures_dir / "inverter_tb_ac_ol.svg"), bbox_inches='tight')
    fig1.savefig(str(figures_dir / "inverter_tb_ac_ol.pdf"), bbox_inches='tight')
    np.savetxt(str(figures_dir / "inverter_tb_ac_ol.csv"),
               np.column_stack((frequency, mag_dB, phase_deg)), comments="",
               header="frequency,Aol_dB,Aol_arg", delimiter=",")

    # ------------------------------------------------------------------
    # 4. Load ngspice DC simulation data
    # ------------------------------------------------------------------
    ngspice_file_dc = data_dir / "inverter_tb_dc_vout.txt"

    vin = ng.loadngspicecol(str(ngspice_file_dc), "v(vin)")
    vout = ng.loadngspicecol(str(ngspice_file_dc), "v(vout)")

    # Local slope dVout/dVin (numerical derivative)
    gain = np.gradient(vout, vin)

    # ------------------------------------------------------------------
    # 5. Transfer Plot (DC)
    # ------------------------------------------------------------------
    dc_color = '#0c5da5'
    gain_color = '#ff6b35'
    vin_color = '#2f855a'

    fig2, ax1 = plt.subplots(figsize=(10, 6.2))
    ax2 = ax1.twinx()
    fig2.suptitle('Inverter - DC Transfer Characteristic')

    ax1.plot(vin, vout, color=dc_color, linewidth=2.6, label=r'$V_\mathrm{out}(V_\mathrm{in})$')
    ax1.plot(vin, vin, color=vin_color, linewidth=1.5, linestyle='-.', label=r'$V_\mathrm{out}=V_\mathrm{in}$')
    ax2.plot(vin, gain, color=gain_color, linewidth=1.8, linestyle='--', label=r'$\mathrm{d}V_\mathrm{out}/\mathrm{d}V_\mathrm{in}$')

    ax1.set_xlabel(r'$V_\mathrm{in}$ (V)')
    ax1.set_xlim(0, 1.5)
    ax1.set_ylabel(r'$V_\mathrm{out}$ (V)')
    ax1.set_ylim(0, 1.5)
    ax1.set_yticks(np.arange(0, 1.5, 0.25))
    ax1.grid(visible=True, which='major', linestyle='--', alpha=0.45)

    ax2.set_ylabel(r'$\mathrm{d}V_\mathrm{out}/\mathrm{d}V_\mathrm{in}$')
    ax2.set_ylim(-50, 0)
    ax2.set_yticks(np.arange(-50, 0, 10))

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='center left')
    plt.tight_layout()
    plt.show()

    # ------------------------------------------------------------------
    # 6. Export DC figures and CSV
    # ------------------------------------------------------------------
    fig2.savefig(str(figures_dir / "inverter_tb_dc_vout.svg"), bbox_inches='tight')
    fig2.savefig(str(figures_dir / "inverter_tb_dc_vout.pdf"), bbox_inches='tight')
    np.savetxt(str(figures_dir / "inverter_tb_dc_vout.csv"),
               np.column_stack((vin, vout, gain)), comments="",
               header="vin,vout,dvout_dvin", delimiter=",")
    # =========================================================================

# Main Execution
if __name__ == '__main__':
    main()

    # Keep plots open
    input("\nPress Enter to close plots and exit...")
# =========================================================================