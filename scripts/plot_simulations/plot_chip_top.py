# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0
# Author: Simon Dorrer
# Created: 12.05.2026
# Last Modified: 12.05.2026
# Description: Transient plots for the chip top macro based on ngspice exports.
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
    ngspice_file = data_dir / "chip_top_tb_tran.txt"

    time = ng.loadngspicecol(str(ngspice_file), "time")
    vin = ng.loadngspicecol(str(ngspice_file), "v(vin)")
    # ToDo

    # Display-friendly axis scale
    time_us = time * 1e6

    # ------------------------------------------------------------------
    # 2. Transient Plot (Voltages over Time)
    # ------------------------------------------------------------------
    vin_color = '#0c5da5'

    fig1, ax = plt.subplots(figsize=(10, 6.2))
    fig1.suptitle('Chip Top - Transient Response')

    ax.plot(time_us, vin, color=vin_color, linewidth=2.4, label=r'$V_\mathrm{in}$')
    # ToDo

    ax.set_xlabel(r'$t$ (µs)')
    ax.set_ylabel(r'$V$ (V)')
    ax.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax.legend(loc='best')
    plt.tight_layout()
    plt.show()

    # ------------------------------------------------------------------
    # 3. Export transient figures and CSV
    # ------------------------------------------------------------------
    fig1.savefig(str(figures_dir / "chip_top_tb_tran.svg"), bbox_inches='tight')
    fig1.savefig(str(figures_dir / "chip_top_tb_tran.pdf"), bbox_inches='tight')
    np.savetxt(str(figures_dir / "chip_top_tb_tran.csv"),
               np.column_stack((time_us, ToDo)), comments="",
               header="time_us, ToDo", delimiter=",")
    # ============================================

# Main Execution
if __name__ == '__main__':
    main()

    # Keep plots open
    input("\nPress Enter to close plots and exit...")
# =========================================================================