# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: Simon Dorrer
# Created: 06.05.2026
# Last Modified: 06.05.2026
# Description: Transient plots for the inverter top macro based on ngspice exports.
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
    # 1. Load ngspice transient simulation data
    # ------------------------------------------------------------------
    ngspice_file = data_dir / "inverter_top_tb_tran.txt"

    time = ng.loadngspicecol(str(ngspice_file), "time")
    vin = ng.loadngspicecol(str(ngspice_file), "v(vin)")
    vout1 = ng.loadngspicecol(str(ngspice_file), "v(vout1)")
    vout2 = ng.loadngspicecol(str(ngspice_file), "v(vout2)")
    vout3 = ng.loadngspicecol(str(ngspice_file), "v(vout3)")
    vout4 = ng.loadngspicecol(str(ngspice_file), "v(vout4)")

    # Display-friendly axis scale
    time_ms = time * 1e3

    # ------------------------------------------------------------------
    # 2. Transient Plot (Voltages over Time)
    # ------------------------------------------------------------------
    vin_color = '#0c5da5'
    vout1_color = '#ff6b35'
    vout2_color = '#2f855a'
    vout3_color = '#805ad5'
    vout4_color = '#c05621'

    fig1, ax = plt.subplots(figsize=(10, 6.2))
    fig1.suptitle('Inverter Top - Transient Response')

    ax.plot(time_ms, vin, color=vin_color, linewidth=2.4, label=r'$V_\mathrm{in}$')
    ax.plot(time_ms, vout1, color=vout1_color, linewidth=2.0, linestyle='-', label=r'$V_\mathrm{out1}$')
    ax.plot(time_ms, vout2, color=vout2_color, linewidth=2.0, linestyle='--', label=r'$V_\mathrm{out2}$')
    ax.plot(time_ms, vout3, color=vout3_color, linewidth=2.0, linestyle='-.', label=r'$V_\mathrm{out3}$')
    ax.plot(time_ms, vout4, color=vout4_color, linewidth=2.0, linestyle=':', label=r'$V_\mathrm{out4}$')

    ax.set_xlabel(r'$t$ (ms)')
    ax.set_ylabel(r'$V$ (V)')
    ax.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax.legend(loc='best')
    plt.tight_layout()
    plt.show()

    # ------------------------------------------------------------------
    # 3. Export transient figures and CSV
    # ------------------------------------------------------------------
    fig1.savefig(str(figures_dir / "inverter_top_tb_tran.svg"), bbox_inches='tight')
    fig1.savefig(str(figures_dir / "inverter_top_tb_tran.pdf"), bbox_inches='tight')
    np.savetxt(str(figures_dir / "inverter_top_tb_tran.csv"),
               np.column_stack((time_ms, vin, vout1, vout2, vout3, vout4)), comments="",
               header="time_ms,vin,vout1,vout2,vout3,vout4", delimiter=",")
    # ============================================

# Main Execution
if __name__ == '__main__':
    main()

    # Keep plots open
    input("\nPress Enter to close plots and exit...")
# =========================================================================