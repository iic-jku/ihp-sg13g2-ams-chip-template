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
T {Testbench for transient analysis - 8-Bit Up Counter} 600 -1730 0 0 1 1 {}
N 120 -360 120 -320 {
lab=GND}
N 120 -720 120 -680 {
lab=VDD}
N 120 -620 120 -580 {
lab=GND}
N 120 -460 120 -420 {lab=clock}
N 500 -720 500 -680 {lab=reset_n}
N 500 -620 500 -580 {lab=GND}
N 500 -460 500 -420 {lab=enable}
N 500 -360 500 -320 {lab=GND}
N 960 -500 1000 -500 {lab=clock}
N 960 -380 1000 -380 {lab=reset_n}
N 960 -440 1000 -440 {lab=enable}
N 1100 -560 1100 -540 {lab=VDD}
N 1100 -340 1100 -320 {lab=GND}
N 1200 -440 1540 -440 {lab=b[0..7] bus=true}
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
C {devices/vsource.sym} 120 -650 0 0 {name=VDD value="1.5"}
C {devices/gnd.sym} 120 -580 0 0 {name=l6 lab=GND}
C {devices/vdd.sym} 120 -720 0 0 {name=l8 lab=VDD}
C {devices/vsource.sym} 120 -390 0 0 {name=vclk value="pulse(0 1.5 0 10p 10p \{0.5/fclk\} \{1/fclk\})"
}
C {devices/lab_wire.sym} 120 -460 0 0 {name=p2 sig_type=std_logic lab=clock}
C {devices/gnd.sym} 120 -320 0 0 {name=l1 lab=GND}
C {devices/title-3.sym} 0 0 0 0 {name=l3 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/launcher.sym} 1700 -1580 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1700 -1480 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw tran"
}
C {code_shown.sym} 60 -1510 0 0 {name=NGSPICE
only_toplevel=false
value="
*True Mixed Signal Simulation (.xspice)
.include ../../../netlist/xspice/counter_top.xspice
.param VDD=1.5
.param temp=27
.param fclk=50e6
.csparam fclk=fclk
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15
.control

set num_threads=8

save all

* User Constants
let tstop = 10u
let tstep = 1/fclk

* Operating Point Analysis
op
remzerovec
write @schname\\\\.raw
set appendwrite

* Transient Analysis
tran $&tstep $&tstop
write @schname\\\\.raw

plot v(clock) v(enable) v(reset_n)
plot v(b7) v(b6) v(b5) v(b4) v(b3) v(b2) v(b1) v(b0)

* Writing Data
unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata ../../../scripts/plot_simulations/data/@schname\\\\.txt clock enable reset_n b0 b1 b2 b3 b4 b5 b6 b7

*quit
.endc"}
C {devices/lab_wire.sym} 500 -720 0 0 {name=p1 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 500 -580 0 0 {name=l2 lab=GND}
C {devices/vsource.sym} 500 -650 0 0 {name=vrst value="pulse(0 1.5 \{1/fclk\} 10p 10p \{0.5/fclk*800\} \{1/fclk*600\} 1)"
}
C {devices/gnd.sym} 500 -320 0 0 {name=l9 lab=GND}
C {devices/vsource.sym} 500 -390 0 0 {name=ven value="pulse(1.5 0 \{4/fclk\} 10p 10p \{0.5/fclk*100\} \{1/fclk*100\} 1)"
}
C {devices/lab_wire.sym} 500 -460 0 0 {name=p11 sig_type=std_logic lab=enable}
C {devices/launcher.sym} 1700 -1530 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/lab_wire.sym} 960 -500 0 0 {name=p10 sig_type=std_logic lab=clock}
C {devices/lab_wire.sym} 960 -380 0 0 {name=p12 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 1100 -320 0 0 {name=l7 lab=GND}
C {devices/vdd.sym} 1100 -560 0 0 {name=l10 lab=VDD}
C {devices/lab_wire.sym} 960 -440 0 0 {name=p13 sig_type=std_logic lab=enable}
C {devices/lab_wire.sym} 1540 -440 0 1 {name=p14 sig_type=std_logic lab=b[0..7]}
C {devices/code_shown.sym} 2000 -1590 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerDIO.lib dio_tt
"}
C {counter_top.sym} 1100 -440 0 0 {name=x1}
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
