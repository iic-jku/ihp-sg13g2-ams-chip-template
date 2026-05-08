v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1620 -1120 2420 -720 {flags=graph
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
B 2 1620 -700 2420 -300 {flags=graph
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
T {Testbench for transient analysis - 8-Bit Up Counter} 600 -1720 0 0 1 1 {}
N 200 -360 200 -320 {
lab=GND}
N 200 -720 200 -680 {
lab=VDD}
N 200 -620 200 -580 {
lab=GND}
N 200 -460 200 -420 {lab=clock}
N 580 -720 580 -680 {lab=reset_n}
N 580 -620 580 -580 {lab=GND}
N 580 -460 580 -420 {lab=enable}
N 580 -360 580 -320 {lab=GND}
N 1100 -500 1140 -500 {lab=clock}
N 1100 -380 1140 -380 {lab=reset_n}
N 1100 -440 1140 -440 {lab=enable}
N 1240 -560 1240 -540 {lab=VDD}
N 1240 -340 1240 -320 {lab=GND}
N 1340 -440 1380 -440 {lab=b[0..7] bus=true}
C {devices/vsource.sym} 200 -650 0 0 {name=VDD value="1.5"}
C {devices/gnd.sym} 200 -580 0 0 {name=l6 lab=GND}
C {devices/vdd.sym} 200 -720 0 0 {name=l8 lab=VDD}
C {devices/vsource.sym} 200 -390 0 0 {name=vclk value="pulse(0 1.5 0 10p 10p \{0.5/fclk\} \{1/fclk\})"
}
C {devices/lab_wire.sym} 200 -460 0 0 {name=p2 sig_type=std_logic lab=clock}
C {devices/gnd.sym} 200 -320 0 0 {name=l1 lab=GND}
C {devices/title-3.sym} 0 0 0 0 {name=l3 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/launcher.sym} 1680 -1300 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1680 -1200 0 0 {name=h1
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
C {devices/lab_wire.sym} 580 -720 0 0 {name=p1 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 580 -580 0 0 {name=l2 lab=GND}
C {devices/vsource.sym} 580 -650 0 0 {name=vrst value="pulse(0 1.5 \{1/fclk\} 10p 10p \{0.5/fclk*800\} \{1/fclk*600\} 1)"
}
C {devices/gnd.sym} 580 -320 0 0 {name=l9 lab=GND}
C {devices/vsource.sym} 580 -390 0 0 {name=ven value="pulse(1.5 0 \{4/fclk\} 10p 10p \{0.5/fclk*100\} \{1/fclk*100\} 1)"
}
C {devices/lab_wire.sym} 580 -460 0 0 {name=p11 sig_type=std_logic lab=enable}
C {devices/launcher.sym} 1680 -1250 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/lab_wire.sym} 1100 -500 0 0 {name=p10 sig_type=std_logic lab=clock}
C {devices/lab_wire.sym} 1100 -380 0 0 {name=p12 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 1240 -320 0 0 {name=l7 lab=GND}
C {devices/vdd.sym} 1240 -560 0 0 {name=l10 lab=VDD}
C {devices/lab_wire.sym} 1100 -440 0 0 {name=p13 sig_type=std_logic lab=enable}
C {devices/lab_wire.sym} 1380 -440 0 1 {name=p14 sig_type=std_logic lab=b[0..7]}
C {devices/code_shown.sym} 1980 -1310 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerDIO.lib dio_tt
"}
C {counter_top.sym} 1240 -440 0 0 {name=x1}
