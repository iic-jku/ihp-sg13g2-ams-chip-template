v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1640 -1440 2440 -1040 {flags=graph
y1=0.00011
y2=1.5
ypos1=0.00011
ypos2=1.5
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="clock
reset_n
enable
b7
b6
b5
b4"
color="4 5 12 10 10 10 10"
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1
linewidth_mult=4
digital=1
legend=1}
B 2 1640 -1020 2440 -620 {flags=graph
y1=0.00011
y2=1.5
ypos1=0.00011
ypos2=1.5
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="b3
b2
b1
b0
BITS;b7,b6,b5,b4,b3,b2,b1,b0"
color="10 10 10 10 21"
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1
linewidth_mult=4
digital=1
legend=1}
B 2 1640 -600 2440 -200 {flags=graph
y1=0.00011
y2=1.5
ypos1=0.00011
ypos2=1.5
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1
linewidth_mult=4
digital=1
legend=1
color="4 4 4 4 4 4 4 4"
node="bit7
bit6
bit5
bit4
bit3
bit2
bit1
bit0"}
T {Testbench for transient analysis - 8-Bit Up Counter (RTL)} 600 -1730 0 0 1 1 {}
N 120 -360 120 -320 {
lab=GND}
N 120 -460 120 -420 {lab=clock}
N 500 -720 500 -680 {lab=reset_n}
N 500 -620 500 -580 {lab=GND}
N 500 -460 500 -420 {lab=enable}
N 500 -360 500 -320 {lab=GND}
N 960 -500 1000 -500 {lab=clock}
N 960 -380 1000 -380 {lab=reset_n}
N 960 -440 1000 -440 {lab=enable}
N 1200 -440 1540 -440 {lab=b[7..0] bus=true}
N 1220 -600 1220 -580 {lab=bit0}
N 1220 -520 1220 -450 {lab=b0}
N 1260 -300 1260 -280 {lab=bit1}
N 1260 -430 1260 -360 {lab=b1}
N 1300 -600 1300 -580 {lab=bit2}
N 1300 -520 1300 -450 {lab=b2}
N 1340 -300 1340 -280 {lab=bit3}
N 1340 -430 1340 -360 {lab=b3}
N 1380 -600 1380 -580 {lab=bit4}
N 1380 -520 1380 -450 {lab=b4}
N 1420 -300 1420 -280 {lab=bit5}
N 1420 -430 1420 -360 {lab=b5}
N 1460 -600 1460 -580 {lab=bit6}
N 1460 -520 1460 -450 {lab=b6}
N 1500 -300 1500 -280 {lab=bit7}
N 1500 -430 1500 -360 {lab=b7}
C {devices/vsource.sym} 120 -390 0 0 {name=vclk value="pulse(0 1.5 0 10p 10p \{0.5/fclk\} \{1/fclk\})"
}
C {devices/lab_wire.sym} 120 -460 0 0 {name=p2 sig_type=std_logic lab=clock}
C {devices/gnd.sym} 120 -320 0 0 {name=l1 lab=GND}
C {devices/title-3.sym} 0 0 0 0 {name=l3 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/launcher.sym} 1700 -1630 0 0 {name=h3
descr="Build Icarus Verilog object" 
tclcommand="execute 1 sh -c \\"cd $netlist_dir/../../.. && make build-rtl-xschem SIM=icarus\\""
}
C {devices/launcher.sym} 1700 -1580 0 0 {name=h4
descr="Build Verilator object" 
tclcommand="execute 1 sh -c \\"cd $netlist_dir/../../.. && make build-rtl-xschem SIM=verilator\\""
}
C {devices/launcher.sym} 1700 -1530 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; file mkdir $netlist_dir; write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save; xschem simulate"
}
C {devices/launcher.sym} 1700 -1480 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw tran"
}
C {code_shown.sym} 60 -1620 0 0 {name=NGSPICE
only_toplevel=false
value="
*RTL Simulation: the d_cosim instance A1 runs the RTL that make build-rtl-xschem or a Build launcher compiled
.param fclk=50e6
.csparam fclk=fclk
.options klu method=gear reltol=1e-3 abstol=1e-12 gmin=1e-12 rshunt=1e14
.control

* Bridges that ngspice inserts between the analog nets and the digital ports of A1.
* One input threshold, since Icarus Verilog counts a clock edge that passes through X (0 to X to 1) twice.
pre_set auto_bridge_d_in = ( \\".model auto_adc adc_bridge(in_low=0.75 in_high=0.75
+ rise_delay=500p fall_delay=500p)\\" \\"auto_bridge%d [ %s ] [ %s ] auto_adc\\" )
pre_set auto_bridge_d_out = ( \\".model auto_dac dac_bridge(out_low=0 out_high=1.5)\\"
+ \\"auto_bridge%d [ %s ] [ %s ] auto_dac\\" )

* User Constants
let tstop = 10u
let tstep = 1/fclk

* Transient Analysis
tran $&tstep $&tstop
write @schname\\\\.raw

plot v(clock) v(enable) v(reset_n)
plot v(b7) v(b6) v(b5) v(b4) v(b3) v(b2) v(b1) v(b0)

* Writing Data
set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt clock enable reset_n b0 b1 b2 b3 b4 b5 b6 b7

* Check at falling clock edges, away from every input change.
* The counter reaches 3 before enable falls, holds it while enable is low, then counts once per cycle.
* A failed meas leaves the -1 and fails the check.
let count = (v(b0) + 2*v(b1) + 4*v(b2) + 8*v(b3) + 16*v(b4) + 32*v(b5) + 64*v(b6) + 128*v(b7)) / 1.5
let c10 = -1
let c50 = -1
let c150 = -1
let c200 = -1
let t10 = 10.5*tstep
let t50 = 50.5*tstep
let t150 = 150.5*tstep
let t200 = 200.5*tstep
meas tran c10 find count at=$&t10
meas tran c50 find count at=$&t50
meas tran c150 find count at=$&t150
meas tran c200 find count at=$&t200
if abs(c10 - 3) > 0.5 | abs(c50 - 3) > 0.5 | abs(c150 - 99) > 0.5 | abs(c200 - 149) > 0.5
  echo ERROR: counter_top_rtl does not count as expected
  if $?batchmode
    quit 1
  end
end

*quit
.endc"}
C {devices/lab_wire.sym} 500 -720 0 0 {name=p1 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 500 -580 0 0 {name=l2 lab=GND}
C {devices/vsource.sym} 500 -650 0 0 {name=vrst value="pulse(0 1.5 \{1.5/fclk\} 10p 10p \{0.5/fclk*800\} \{1/fclk*600\} 1)"
}
C {devices/gnd.sym} 500 -320 0 0 {name=l9 lab=GND}
C {devices/vsource.sym} 500 -390 0 0 {name=ven value="pulse(1.5 0 \{4.5/fclk\} 10p 10p \{0.5/fclk*100\} \{1/fclk*100\} 1)"
}
C {devices/lab_wire.sym} 500 -460 0 0 {name=p11 sig_type=std_logic lab=enable}
C {devices/lab_wire.sym} 960 -500 0 0 {name=p10 sig_type=std_logic lab=clock}
C {devices/lab_wire.sym} 960 -380 0 0 {name=p12 sig_type=std_logic lab=reset_n}
C {devices/lab_wire.sym} 960 -440 0 0 {name=p13 sig_type=std_logic lab=enable}
C {devices/lab_wire.sym} 1540 -440 0 1 {name=p14 sig_type=std_logic lab=b[7..0]}
C {counter_top_rtl.sym} 1100 -440 0 0 {name=A1}
C {devices/lab_wire.sym} 1220 -600 1 0 {name=p3 sig_type=std_logic lab=bit0}
C {bus_tap.sym} 1210 -440 0 0 {name=l4 lab=0}
C {res.sym} 1220 -550 0 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 1260 -280 1 1 {name=p4 sig_type=std_logic lab=bit1}
C {bus_tap.sym} 1250 -440 2 1 {name=l5 lab=1}
C {res.sym} 1260 -330 2 1 {name=R2
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 1300 -600 1 0 {name=p5 sig_type=std_logic lab=bit2}
C {bus_tap.sym} 1290 -440 0 0 {name=l11 lab=2}
C {res.sym} 1300 -550 0 0 {name=R3
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 1340 -280 1 1 {name=p6 sig_type=std_logic lab=bit3}
C {bus_tap.sym} 1330 -440 2 1 {name=l12 lab=3}
C {res.sym} 1340 -330 2 1 {name=R4
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 1380 -600 1 0 {name=p7 sig_type=std_logic lab=bit4}
C {bus_tap.sym} 1370 -440 0 0 {name=l13 lab=4}
C {res.sym} 1380 -550 0 0 {name=R5
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 1420 -280 1 1 {name=p8 sig_type=std_logic lab=bit5}
C {bus_tap.sym} 1410 -440 2 1 {name=l14 lab=5}
C {res.sym} 1420 -330 2 1 {name=R6
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 1460 -600 1 0 {name=p9 sig_type=std_logic lab=bit6}
C {bus_tap.sym} 1450 -440 0 0 {name=l15 lab=6}
C {res.sym} 1460 -550 0 0 {name=R7
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 1500 -280 1 1 {name=p15 sig_type=std_logic lab=bit7}
C {bus_tap.sym} 1490 -440 2 1 {name=l16 lab=7}
C {res.sym} 1500 -330 2 1 {name=R8
value=1k
footprint=1206
device=resistor
m=1}
