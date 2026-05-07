###############################################################################
# Created by write_sdc
###############################################################################
current_design counter_top
###############################################################################
# Timing Constraints
###############################################################################
create_clock -name clock_i -period 20.0000 [get_ports {clock_i}]
set_clock_transition 0.1500 [get_clocks {clock_i}]
set_clock_uncertainty 0.2500 clock_i
set_propagated_clock [get_clocks {clock_i}]
set_input_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {enable_i}]
set_input_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {reset_n_i}]
set_output_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {counter_value_o[0]}]
set_output_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {counter_value_o[1]}]
set_output_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {counter_value_o[2]}]
set_output_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {counter_value_o[3]}]
set_output_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {counter_value_o[4]}]
set_output_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {counter_value_o[5]}]
set_output_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {counter_value_o[6]}]
set_output_delay 4.0000 -clock [get_clocks {clock_i}] -add_delay [get_ports {counter_value_o[7]}]
###############################################################################
# Environment
###############################################################################
set_load -pin_load 0.0060 [get_ports {counter_value_o[7]}]
set_load -pin_load 0.0060 [get_ports {counter_value_o[6]}]
set_load -pin_load 0.0060 [get_ports {counter_value_o[5]}]
set_load -pin_load 0.0060 [get_ports {counter_value_o[4]}]
set_load -pin_load 0.0060 [get_ports {counter_value_o[3]}]
set_load -pin_load 0.0060 [get_ports {counter_value_o[2]}]
set_load -pin_load 0.0060 [get_ports {counter_value_o[1]}]
set_load -pin_load 0.0060 [get_ports {counter_value_o[0]}]
set_driving_cell -lib_cell sg13g2_buf_4 -pin {X} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {clock_i}]
set_driving_cell -lib_cell sg13g2_buf_4 -pin {X} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {enable_i}]
set_driving_cell -lib_cell sg13g2_buf_4 -pin {X} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {reset_n_i}]
###############################################################################
# Design Rules
###############################################################################
set_max_fanout 10.0000 [current_design]
