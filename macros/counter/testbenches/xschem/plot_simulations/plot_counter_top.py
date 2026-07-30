# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: Simon Dorrer
# Description: Transient plots for the counter macro based on ngspice exports.
# Created: 08.05.2026
# Last Modified: 08.05.2026
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
    "font.size": 12,
})
# =========================================================================

def main():
    # Resolve data and output paths relative to this script
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load ngspice gate-level transient simulation data
    # ------------------------------------------------------------------
    ngspice_file = data_dir / "counter_top_tb_tran.txt"

    data_time = ng.loadngspicecol(str(ngspice_file), "time") * 1e6
    data_clock = ng.loadngspicecol(str(ngspice_file), "clock")
    data_enable = ng.loadngspicecol(str(ngspice_file), "enable")
    data_reset_n = ng.loadngspicecol(str(ngspice_file), "reset_n")
    data_b0 = ng.loadngspicecol(str(ngspice_file), "b0")
    data_b1 = ng.loadngspicecol(str(ngspice_file), "b1")
    data_b2 = ng.loadngspicecol(str(ngspice_file), "b2")
    data_b3 = ng.loadngspicecol(str(ngspice_file), "b3")
    data_b4 = ng.loadngspicecol(str(ngspice_file), "b4")
    data_b5 = ng.loadngspicecol(str(ngspice_file), "b5")
    data_b6 = ng.loadngspicecol(str(ngspice_file), "b6")
    data_b7 = ng.loadngspicecol(str(ngspice_file), "b7")

    # Subsample data for clearer plots and smaller CSV output.
    # data_time = data_time[1::4]
    # data_clock = data_clock[1::4]
    # data_enable = data_enable[1::4]
    # data_reset_n = data_reset_n[1::4]
    # data_b0 = data_b0[1::4]
    # data_b1 = data_b1[1::4]
    # data_b2 = data_b2[1::4]
    # data_b3 = data_b3[1::4]
    # data_b4 = data_b4[1::4]
    # data_b5 = data_b5[1::4]
    # data_b6 = data_b6[1::4]
    # data_b7 = data_b7[1::4]

    # ------------------------------------------------------------------
    # 2. Transient Plot
    # ------------------------------------------------------------------
    signals = [
        ("CLK", data_clock, "#0c5da5"),
        ("RST_n", data_reset_n, "#00b945"),
        ("EN", data_enable, "#ff9500"),
        ("B0", data_b0, "#ff6b35"),
        ("B1", data_b1, "#845ec2"),
        ("B2", data_b2, "#2c73d2"),
        ("B3", data_b3, "#008f7a"),
        ("B4", data_b4, "#c34a36"),
        ("B5", data_b5, "#4d8076"),
        ("B6", data_b6, "#7b2cbf"),
        ("B7", data_b7, "#b39f00"),
    ]
    y_ticks = [0.0, 0.5, 1.0, 1.5]

    fig1, axs = plt.subplots(len(signals), sharex=True)
    fig1.set_figwidth(16)
    fig1.set_figheight(9)
    fig1.suptitle('Counter Top - Gate-Level Transient Simulation')

    for ax, (name, values, color) in zip(axs, signals):
        ax.plot(data_time, values, color=color, linewidth=1.3)
        ax.set_ylabel(f'{name} (V)', fontsize=11)
        ax.set_ylim(-0.1, 1.6)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(["0", "0.5", "1.0", "1.5"], fontsize=8)
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(True, alpha=0.4)

    axs[-1].set_xlabel(r'$t$ ($\mu$s)')
    fig1.tight_layout(rect=[0, 0, 1, 0.98], pad=0.5, w_pad=0.1, h_pad=0.1)
    plt.show()

    # ------------------------------------------------------------------
    # 3. Export transient figures and CSV
    # ------------------------------------------------------------------
    fig1.savefig(str(figures_dir / "counter_top_tb_tran.svg"), bbox_inches='tight')
    fig1.savefig(str(figures_dir / "counter_top_tb_tran.pdf"), bbox_inches='tight')
    np.savetxt(
        str(figures_dir / "counter_top_tb_tran.csv"),
        np.column_stack((
            data_time, data_clock, data_reset_n, data_enable,
            data_b0, data_b1, data_b2, data_b3,
            data_b4, data_b5, data_b6, data_b7,
        )),
        comments="",
        header="time,clock,reset_n,enable,b0,b1,b2,b3,b4,b5,b6,b7",
        delimiter=",",
    )
    # =========================================================================

# Main Execution
if __name__ == '__main__':
    main()

    # Keep plots open
    input("\nPress Enter to close plots and exit...")
# =========================================================================