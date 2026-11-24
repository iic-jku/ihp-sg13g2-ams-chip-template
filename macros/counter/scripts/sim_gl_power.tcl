# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: OpenSTA power estimate of a gate-level netlist from the switching activity of its simulation, run by make sim-gl-power-cocotb, which sets the POWER_* variables.

foreach lib $::env(POWER_LIBS) {
	read_liberty $lib
}
foreach netlist $::env(POWER_NETLISTS) {
	read_verilog $netlist
}
link_design $::env(POWER_TOP)

# Reads without -corner add up, so each macro instance keeps the parasitics of its own SPEF
read_spef $::env(POWER_SPEF)
foreach {cell spef} $::env(POWER_MACRO_SPEFS) {
	foreach inst [get_cells -hierarchical -filter "ref_name == $cell"] {
		read_spef -path [get_full_name $inst] $spef
	}
}
read_sdc $::env(POWER_SDC)
read_vcd -scope $::env(POWER_TOP) $::env(POWER_VCD)

set rpt $::env(POWER_RPT)
set f [open $rpt w]
puts $f "Power of $::env(POWER_TOP) from the switching activity of $::env(POWER_VCD)"
puts $f "Liberty: [join [lmap lib $::env(POWER_LIBS) {file tail $lib}] {, }]"
puts $f ""
close $f
report_activity_annotation >> $rpt
report_power -digits 4 >> $rpt
set macros [get_cells -hierarchical -filter "is_hierarchical == true || is_memory == true"]
if {[llength $macros] > 0} {
	report_power -digits 4 -instances $macros >> $rpt
}

# read_vcd reports no error when its scope or the netlist does not match the simulation, and every pin it misses keeps the default activity
set f [open $rpt r]
set text [read $f]
close $f
if {![regexp {unannotated\s+0\s} $text]} {
	puts "Error: pins without activity from $::env(POWER_VCD), see report_activity_annotation in $rpt"
	exit 1
}
