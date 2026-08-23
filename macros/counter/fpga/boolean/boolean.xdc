# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# RealDigital Boolean pin map for counter_top.
# See https://www.realdigital.org/hardware/boolean for the board pinout.

# 100 MHz on-board oscillator
set_property -dict {PACKAGE_PIN F14 IOSTANDARD LVCMOS33} [get_ports {clock_i}]

# sw[0] toggle: 0 = held in reset, 1 = run
set_property -dict {PACKAGE_PIN V2 IOSTANDARD LVCMOS33} [get_ports {reset_n_i}]
# sw[1] toggle: enable
set_property -dict {PACKAGE_PIN U2 IOSTANDARD LVCMOS33} [get_ports {enable_i}]

# The eight rightmost on-board LEDs
set_property -dict {PACKAGE_PIN G1 IOSTANDARD LVCMOS33} [get_ports {counter_value_o[0]}]
set_property -dict {PACKAGE_PIN G2 IOSTANDARD LVCMOS33} [get_ports {counter_value_o[1]}]
set_property -dict {PACKAGE_PIN F1 IOSTANDARD LVCMOS33} [get_ports {counter_value_o[2]}]
set_property -dict {PACKAGE_PIN F2 IOSTANDARD LVCMOS33} [get_ports {counter_value_o[3]}]
set_property -dict {PACKAGE_PIN E1 IOSTANDARD LVCMOS33} [get_ports {counter_value_o[4]}]
set_property -dict {PACKAGE_PIN E2 IOSTANDARD LVCMOS33} [get_ports {counter_value_o[5]}]
set_property -dict {PACKAGE_PIN E3 IOSTANDARD LVCMOS33} [get_ports {counter_value_o[6]}]
set_property -dict {PACKAGE_PIN E5 IOSTANDARD LVCMOS33} [get_ports {counter_value_o[7]}]
