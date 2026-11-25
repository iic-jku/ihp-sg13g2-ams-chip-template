# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: Simon Dorrer
# Description: Transient plots for the counter macro based on ngspice exports.
# Created: 08.05.2026
# Last Modified: 24.11.2026
# ============================================

# Imports
import numpy as np
import matplotlib.pyplot as plt
import ngspice2python as ng
from pathlib import Path
# ============================================

# Plotting Configuration
# ============================================
# Interactive mode stays off: the plt.show() at the end of main() then blocks in the GUI
# event loop, which is what draws the windows in the first place. With plt.ion() the call
# returns immediately and nothing pumps that loop afterwards, so no window ever appears.
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

# Testbenches whose wrdata exports are plotted, with the title of their figure
TESTBENCHES = [
    ("counter_top_tb_tran", "Gate-Level"),
    ("counter_top_tb_tran_rtl", "RTL"),
]
# =========================================================================

def plot_transient(ngspice_file, figures_dir, tb_name, sim_kind):
    # ------------------------------------------------------------------
    # 1. Load ngspice transient simulation data
    # ------------------------------------------------------------------
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
    # The axis follows the supply, which the clock reaches as its maximum
    vdd = float(np.max(data_clock))
    y_ticks = [0.0, vdd / 3, 2 * vdd / 3, vdd]

    fig1, axs = plt.subplots(len(signals), sharex=True)
    fig1.set_figwidth(16)
    fig1.set_figheight(9)
    fig1.suptitle(f'Counter Top - {sim_kind} Transient Simulation')

    for ax, (name, values, color) in zip(axs, signals):
        ax.plot(data_time, values, color=color, linewidth=1.3)
        ax.set_ylabel(f'{name} (V)', fontsize=11)
        ax.set_ylim(-vdd / 15, vdd * 16 / 15)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(["0"] + [f"{t:.1f}" for t in y_ticks[1:]], fontsize=8)
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(True, alpha=0.4)

    axs[-1].set_xlabel(r'$t$ ($\mu$s)')
    fig1.tight_layout(rect=[0, 0, 1, 0.98], pad=0.5, w_pad=0.1, h_pad=0.1)

    # ------------------------------------------------------------------
    # 3. Export transient figures and CSV
    # ------------------------------------------------------------------
    fig1.savefig(str(figures_dir / f"{tb_name}.svg"), bbox_inches='tight')
    fig1.savefig(str(figures_dir / f"{tb_name}.pdf"), bbox_inches='tight')
    np.savetxt(
        str(figures_dir / f"{tb_name}.csv"),
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

def main():
    # Resolve data and output paths relative to this script
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Plot each testbench that has been simulated
    for tb_name, sim_kind in TESTBENCHES:
        ngspice_file = data_dir / f"{tb_name}.txt"
        if not ngspice_file.exists():
            print(f"Skipping {tb_name}: {ngspice_file} not found, run its simulation first.")
            continue
        plot_transient(ngspice_file, figures_dir, tb_name, sim_kind)

    # ------------------------------------------------------------------
    # Open the plot windows (blocks until they are closed)
    # ------------------------------------------------------------------
    plt.show()
    # =========================================================================

# Main Execution
if __name__ == '__main__':
    main()
# =========================================================================