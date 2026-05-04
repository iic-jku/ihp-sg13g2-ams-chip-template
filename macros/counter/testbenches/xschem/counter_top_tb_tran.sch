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
x2=4e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="clock
reset_n
enable
bits7
bits6
bits5
bits4"
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
x2=4e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="bits3
bits2
bits1
bits0
BITS;bits7,bits6,bits5,bits4,bits3,bits2,bits1,bits0"
color="10 10 10 10 21"
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1
linewidth_mult=4
digital=1
legend=1}
T {Testbench for transient analysis - 8-Bit Counter} 600 -1720 0 0 1 1 {}
N 300 -360 300 -320 {
lab=GND}
N 300 -720 300 -680 {
lab=VDD}
N 300 -620 300 -580 {
lab=GND}
N 300 -460 300 -420 {lab=clock}
N 680 -720 680 -680 {lab=reset_n}
N 680 -620 680 -580 {lab=GND}
N 680 -460 680 -420 {lab=enable}
N 680 -360 680 -320 {lab=GND}
N 1160 -500 1200 -500 {lab=clock}
N 1160 -380 1200 -380 {lab=reset_n}
N 1160 -440 1200 -440 {lab=enable}
N 1280 -560 1280 -540 {lab=VDD}
N 1280 -340 1280 -320 {lab=GND}
N 1380 -440 1420 -440 {lab=bits[0..3] bus=true}
C {devices/vsource.sym} 300 -650 0 0 {name=VDD value="1.5"}
C {devices/gnd.sym} 300 -580 0 0 {name=l6 lab=GND}
C {devices/vdd.sym} 300 -720 0 0 {name=l8 lab=VDD}
C {devices/vsource.sym} 300 -390 0 0 {name=vclk value="pulse(0 1.5 0 10p 10p \{0.5/fclk\} \{1/fclk\})"
}
C {devices/lab_wire.sym} 300 -460 0 0 {name=p2 sig_type=std_logic lab=clock}
C {devices/gnd.sym} 300 -320 0 0 {name=l1 lab=GND}
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
.include ../../netlist/xspice/counter_top/counter_top.xspice
.param VDD=1.5
.param temp=27
.param fclk=50e6
.csparam fclk=fclk
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15
.control

set num_threads=8

save all

* User Constants
let tstop = 5u
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
wrdata $DESIGNS/ihp-sg13g2-ams-chip-template/macros/counter/scripts/plot_simulations/data/counter_top_tb_tran.txt clock enable reset_n b0 b1 b2 b3 b4 b5 b6 b7

quit
.endc"}
C {devices/lab_wire.sym} 680 -720 0 0 {name=p1 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 680 -580 0 0 {name=l2 lab=GND}
C {devices/vsource.sym} 680 -650 0 0 {name=vrst value="pulse(0 1.5 \{1/fclk\} 10p 10p \{0.5/fclk*100\} \{1/fclk*100\})"
}
C {devices/gnd.sym} 680 -320 0 0 {name=l9 lab=GND}
C {devices/vsource.sym} 680 -390 0 0 {name=ven value="pulse(0 1.5 \{4/fclk\} 10p 10p \{0.5/fclk*100\} \{1/fclk*100\})"
}
C {devices/lab_wire.sym} 680 -460 0 0 {name=p11 sig_type=std_logic lab=enable}
C {devices/launcher.sym} 1680 -1250 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/lab_wire.sym} 1160 -500 0 0 {name=p10 sig_type=std_logic lab=clock}
C {devices/lab_wire.sym} 1160 -380 0 0 {name=p12 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 1280 -320 0 0 {name=l7 lab=GND}
C {devices/vdd.sym} 1280 -560 0 0 {name=l10 lab=VDD}
C {devices/lab_wire.sym} 1160 -440 0 0 {name=p13 sig_type=std_logic lab=enable}
C {devices/lab_wire.sym} 1420 -440 0 1 {name=p14 sig_type=std_logic lab=bits[0..3]}
C {counter_board_bus.sym} 1280 -440 0 0 {name=x1}
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
