# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: Simon Dorrer
# Description: Transient plots for the chip top-level testbench based on ngspice exports.
# Created: 12.05.2026
# Last Modified: 12.05.2026
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

def plot_digital(fig_title, signals, data_time, figures_dir, filename, fig_height=9):
    """Stack digital signals in separate subplots sharing the time axis."""
    y_ticks = [0.0, 1.0, 2.0, 3.0, 4.0]
    fig, axs = plt.subplots(len(signals), sharex=True)
    if len(signals) == 1:
        axs = [axs]
    fig.set_figwidth(16)
    fig.set_figheight(fig_height)
    fig.suptitle(fig_title)

    for ax, (name, values, color) in zip(axs, signals):
        ax.plot(data_time, values, color=color, linewidth=1.3)
        ax.set_ylabel(f'{name} (V)', fontsize=11)
        ax.set_ylim(-0.2, 4.2)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(["0", "1.0", "2.0", "3.0", "4.0"], fontsize=8)
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(True, alpha=0.4)

    axs[-1].set_xlabel(r'$t$ ($\mu$s)')
    fig.tight_layout(rect=[0, 0, 1, 0.98], pad=0.5, w_pad=0.1, h_pad=0.1)
    plt.show()
    fig.savefig(str(figures_dir / f"{filename}.svg"), bbox_inches='tight')
    fig.savefig(str(figures_dir / f"{filename}.pdf"), bbox_inches='tight')
    return fig
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

    time       = ng.loadngspicecol(str(ngspice_file), "time")
    clock      = ng.loadngspicecol(str(ngspice_file), "v(clock)")
    reset_n    = ng.loadngspicecol(str(ngspice_file), "v(reset_n)")
    enable     = ng.loadngspicecol(str(ngspice_file), "v(enable)")
    sram_0_out = ng.loadngspicecol(str(ngspice_file), "v(sram_0_out)")
    inv1_dout1 = ng.loadngspicecol(str(ngspice_file), "v(inv1_dout1)")
    inv1_dout2 = ng.loadngspicecol(str(ngspice_file), "v(inv1_dout2)")
    inv1_dout3 = ng.loadngspicecol(str(ngspice_file), "v(inv1_dout3)")
    inv1_dout4 = ng.loadngspicecol(str(ngspice_file), "v(inv1_dout4)")
    inv2_vin1  = ng.loadngspicecol(str(ngspice_file), "v(inv2_vin1)")
    inv2_vout1 = ng.loadngspicecol(str(ngspice_file), "v(inv2_vout1)")
    inv2_vin2  = ng.loadngspicecol(str(ngspice_file), "v(inv2_vin2)")
    inv2_vout2 = ng.loadngspicecol(str(ngspice_file), "v(inv2_vout2)")
    c2_b0      = ng.loadngspicecol(str(ngspice_file), "v(counter2_value0)")
    c2_b1      = ng.loadngspicecol(str(ngspice_file), "v(counter2_value1)")
    c2_b2      = ng.loadngspicecol(str(ngspice_file), "v(counter2_value2)")
    c2_b3      = ng.loadngspicecol(str(ngspice_file), "v(counter2_value3)")
    c2_b4      = ng.loadngspicecol(str(ngspice_file), "v(counter2_value4)")
    c2_b5      = ng.loadngspicecol(str(ngspice_file), "v(counter2_value5)")
    c2_b6      = ng.loadngspicecol(str(ngspice_file), "v(counter2_value6)")
    c2_b7      = ng.loadngspicecol(str(ngspice_file), "v(counter2_value7)")
    c1_din1    = ng.loadngspicecol(str(ngspice_file), "v(counter1_value4_inv1_din1)")
    c1_din2    = ng.loadngspicecol(str(ngspice_file), "v(counter1_value5_inv1_din2)")

    # Display-friendly axis scale
    time_us = time * 1e6

    # ------------------------------------------------------------------
    # 2. Plot 1 (digital): CLK / RST_n / EN / SRAM / INV1 outputs
    # ------------------------------------------------------------------
    signals1 = [
        ("CLK",        clock,      "#0c5da5"),
        ("RST_n",      reset_n,    "#00b945"),
        ("EN",         enable,     "#ff9500"),
        ("SRAM_out",   sram_0_out, "#e63946"),
        ("INV1_dout1", inv1_dout1, "#845ec2"),
        ("INV1_dout2", inv1_dout2, "#2c73d2"),
        ("INV1_dout3", inv1_dout3, "#008f7a"),
        ("INV1_dout4", inv1_dout4, "#ff6b35"),
    ]
    plot_digital(
        "Chip Top — Digital Inverter Outputs (INV1)",
        signals1, time_us, figures_dir,
        "chip_top_tb_tran_digital1",
        fig_height=12,
    )

    # ------------------------------------------------------------------
    # 3. Plot 2 (digital): CLK / RST_n / EN / counter2 bits
    # ------------------------------------------------------------------
    signals2 = [
        ("CLK",   clock,   "#0c5da5"),
        ("RST_n", reset_n, "#00b945"),
        ("EN",    enable,  "#ff9500"),
        ("C2_B0", c2_b0,   "#ff6b35"),
        ("C2_B1", c2_b1,   "#845ec2"),
        ("C2_B2", c2_b2,   "#2c73d2"),
        ("C2_B3", c2_b3,   "#008f7a"),
        ("C2_B4", c2_b4,   "#c34a36"),
        ("C2_B5", c2_b5,   "#4d8076"),
        ("C2_B6", c2_b6,   "#7b2cbf"),
        ("C2_B7", c2_b7,   "#b39f00"),
    ]
    plot_digital(
        "Chip Top — Counter 2 Output Bits",
        signals2, time_us, figures_dir,
        "chip_top_tb_tran_digital2",
        fig_height=12,
    )

    # ------------------------------------------------------------------
    # 4. Plot 3 (digital): CLK / RST_n / EN / counter1→INV1 inputs
    # ------------------------------------------------------------------
    signals3 = [
        ("CLK",          clock,   "#0c5da5"),
        ("RST_n",        reset_n, "#00b945"),
        ("EN",           enable,  "#ff9500"),
        ("C1_val4/din1", c1_din1, "#845ec2"),
        ("C1_val5/din2", c1_din2, "#ff6b35"),
    ]
    plot_digital(
        "Chip Top — Counter 1 / INV1 Inputs (Bits 4–5)",
        signals3, time_us, figures_dir,
        "chip_top_tb_tran_digital3",
    )

    # ------------------------------------------------------------------
    # 5. Plot 4 (analog): INV2 input / output voltages — both channels
    # ------------------------------------------------------------------
    fig4, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 6))
    fig4.suptitle("Chip Top — Analog Inverter (INV2)")

    ax1.plot(time_us, inv2_vin1,  color="#0c5da5", linewidth=1.5, label=r'$V_\mathrm{in,1}$')
    ax1.plot(time_us, inv2_vout1, color="#ff6b35", linewidth=1.5, label=r'$V_\mathrm{out,1}$')
    ax1.set_ylabel(r'$V$ (V)')
    ax1.set_title("Channel 1 (200 kHz)")
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.4)

    ax2.plot(time_us, inv2_vin2,  color="#2c73d2", linewidth=1.5, label=r'$V_\mathrm{in,2}$')
    ax2.plot(time_us, inv2_vout2, color="#c34a36", linewidth=1.5, label=r'$V_\mathrm{out,2}$')
    ax2.set_ylabel(r'$V$ (V)')
    ax2.set_xlabel(r'$t$ ($\mu$s)')
    ax2.set_title("Channel 2 (400 kHz)")
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.4)

    fig4.tight_layout(rect=[0, 0, 1, 0.98])
    plt.show()
    fig4.savefig(str(figures_dir / "chip_top_tb_tran_analog_inv.svg"), bbox_inches='tight')
    fig4.savefig(str(figures_dir / "chip_top_tb_tran_analog_inv.pdf"), bbox_inches='tight')

    # ------------------------------------------------------------------
    # 6. Export combined CSV
    # ------------------------------------------------------------------
    np.savetxt(
        str(figures_dir / "chip_top_tb_tran.csv"),
        np.column_stack((
            time_us, clock, reset_n, enable, sram_0_out,
            inv1_dout1, inv1_dout2, inv1_dout3, inv1_dout4,
            inv2_vin1, inv2_vout1, inv2_vin2, inv2_vout2,
            c2_b0, c2_b1, c2_b2, c2_b3, c2_b4, c2_b5, c2_b6, c2_b7,
            c1_din1, c1_din2,
        )),
        comments="",
        header=(
            "time_us,clock,reset_n,enable,sram_0_out,"
            "inv1_dout1,inv1_dout2,inv1_dout3,inv1_dout4,"
            "inv2_vin1,inv2_vout1,inv2_vin2,inv2_vout2,"
            "counter2_value0,counter2_value1,counter2_value2,counter2_value3,"
            "counter2_value4,counter2_value5,counter2_value6,counter2_value7,"
            "counter1_value4_inv1_din1,counter1_value5_inv1_din2"
        ),
        delimiter=",",
    )
    # ============================================

# Main Execution
if __name__ == '__main__':
    main()

    # Keep plots open
    input("\nPress Enter to close plots and exit...")
# =========================================================================