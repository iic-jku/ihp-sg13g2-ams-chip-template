# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2025-2026 The Chip Team
# SPDX-License-Identifier: Apache-2.0
# Author: Simon Dorrer
# Description: Bode plot of the 3rd-order MFB LPF closed-loop AC simulation
#              (ngspice) compared with the analytical Prototype Filter transfer
#              function exported by 3rd_order_mfb_lpf_designer.py.
# Created: 13.12.2024
# Last Modified: 14.03.2026
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

# Use LaTeX if available, otherwise fallback gracefully
try:
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif', size=14)
except Exception:
    print("Warning: LaTeX not available. Using standard fonts.")
    plt.rc('font', size=12)
# =========================================================================

def main():
    # Resolve data and output paths relative to this script
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load ngspice closed-loop AC simulation data
    # ------------------------------------------------------------------
    ngspice_file = data_dir / "inverter_top_tb_ac_ol.txt"

    data_frequency = ng.loadngspicecol(str(ngspice_file), "frequency")
    frequency = data_frequency[0::2]

    data_mag_dB = ng.loadngspicecol(str(ngspice_file), "v(Amag_dB)")
    mag_dB = data_mag_dB[0::2]

    data_phase = ng.loadngspicecol(str(ngspice_file), "v(Aarg)")
    phase_deg = data_phase[0::2]

    # ------------------------------------------------------------------
    # 2. Load analytical Prototype Filter Bode data (from designer)
    # ------------------------------------------------------------------
    prototype_filter_file = data_dir / "3rd_order_mfb_lpf_prototype_bode.csv" # "biquad_mfb_lpf_prototype_bode.csv"
    prototype_filter_data = np.genfromtxt(str(prototype_filter_file), delimiter=',', names=True)
    freq_prototype = prototype_filter_data['frequency']
    mag_dB_prototype = prototype_filter_data['mag_dB']
    phase_deg_prototype = prototype_filter_data['phase_deg']

    # ------------------------------------------------------------------
    # 3. Bode Plot
    # ------------------------------------------------------------------
    fig1, axs = plt.subplots(2)
    fig1.set_figwidth(10)
    fig1.set_figheight(7)

    # Magnitude
    axs[0].set_xscale('log')
    axs[0].plot(frequency, mag_dB, linewidth=2, label='ngspice Simulation')
    axs[0].plot(freq_prototype, mag_dB_prototype, linewidth=2, linestyle='--', label='Prototype Filter (Analytical)')
    axs[0].set_xlabel('$f$ (Hz)')
    axs[0].set_ylabel('Magnitude (dB)')
    axs[0].grid(visible=True, which='both', linestyle='--', alpha=0.5)
    axs[0].legend(loc='lower left')

    # Phase
    axs[1].set_xscale('log')
    axs[1].plot(frequency, phase_deg, linewidth=2, label='ngspice Simulation')
    axs[1].plot(freq_prototype, phase_deg_prototype, linewidth=2, linestyle='--', label='Prototype Filter (Analytical)')
    axs[1].set_xlabel('$f$ (Hz)')
    axs[1].set_ylabel(r'Phase ($^\circ$)')
    axs[1].grid(visible=True, which='both', linestyle='--', alpha=0.5)
    axs[1].legend(loc='lower left')
    plt.tight_layout()
    plt.show()

    # ------------------------------------------------------------------
    # 4. Export figures and CSV
    # ------------------------------------------------------------------
    fig1.savefig(str(figures_dir / "inverter_top_tb_ac_ol.svg"), bbox_inches='tight')
    fig1.savefig(str(figures_dir / "inverter_top_tb_ac_ol.pdf"), bbox_inches='tight')
    np.savetxt(str(figures_dir / "inverter_top_tb_ac_ol.csv"),
               np.column_stack((frequency, mag_dB, phase_deg)), comments="",
               header="frequency,Amag_dB,Aarg", delimiter=",")
    # ============================================

# Main Execution
if __name__ == '__main__':
    main()

    # Keep plots open
    input("\nPress Enter to close plots and exit...")
# =========================================================================