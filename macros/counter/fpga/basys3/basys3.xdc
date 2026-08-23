# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# Basys 3 pin map for counter_top.
# See https://digilent.com/reference/programmable-logic/basys-3/reference-manual for the board pinout.

# 100 MHz on-board oscillator
set_property -dict { PACKAGE_PIN W5 IOSTANDARD LVCMOS33 } [get_ports clock_i]
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clock_i]

# sw[0] toggle: 0 = held in reset, 1 = run
set_property -dict { PACKAGE_PIN V17 IOSTANDARD LVCMOS33 } [get_ports reset_n_i]
# sw[1] toggle: enable
set_property -dict { PACKAGE_PIN V16 IOSTANDARD LVCMOS33 } [get_ports enable_i]

# The eight rightmost on-board LEDs
set_property -dict { PACKAGE_PIN U16 IOSTANDARD LVCMOS33 } [get_ports {counter_value_o[0]}]
set_property -dict { PACKAGE_PIN E19 IOSTANDARD LVCMOS33 } [get_ports {counter_value_o[1]}]
set_property -dict { PACKAGE_PIN U19 IOSTANDARD LVCMOS33 } [get_ports {counter_value_o[2]}]
set_property -dict { PACKAGE_PIN V19 IOSTANDARD LVCMOS33 } [get_ports {counter_value_o[3]}]
set_property -dict { PACKAGE_PIN W18 IOSTANDARD LVCMOS33 } [get_ports {counter_value_o[4]}]
set_property -dict { PACKAGE_PIN U15 IOSTANDARD LVCMOS33 } [get_ports {counter_value_o[5]}]
set_property -dict { PACKAGE_PIN U14 IOSTANDARD LVCMOS33 } [get_ports {counter_value_o[6]}]
set_property -dict { PACKAGE_PIN V14 IOSTANDARD LVCMOS33 } [get_ports {counter_value_o[7]}]
