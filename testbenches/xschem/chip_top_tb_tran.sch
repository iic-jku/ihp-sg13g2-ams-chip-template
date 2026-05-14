v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1460 -1480 2260 -1080 {flags=graph
y1=-0.56
y2=2.1
ypos1=-0.23167344
ypos2=2.5128141
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
sram_0_out
\\"inv1_din1\\"; counter1_value4_inv1_din1
\\"inv1_din2\\"; counter1_value5_inv1_din2
\\"inv1_din3\\"; counter1_value6_inv1_din3
\\"inv1_din4\\"; counter1_value7_inv1_din4"
color="4 7 10 21 4 4 4 4"
dataset=0
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 1460 -1060 2260 -660 {flags=graph
y1=-0.56
y2=2.1
ypos1=-0.56
ypos2=2.1
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="counter2_value0
counter2_value1
counter2_value2
counter2_value3
counter2_value4
counter2_value5
counter2_value6
counter2_value7"
color="4 4 4 4 4 4 4 4"
dataset=0
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 2280 -1900 3080 -1500 {flags=graph
y1=-0.0066
y2=0.0013
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0


dataset=0
unitx=1
logx=0
logy=0
linewidth_mult=3
color="4 21"
node="i(VDD)
i(VIO)"}
B 2 1460 -640 2260 -240 {flags=graph
y1=0.74
y2=0.76
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="inv2_vin1
inv2_vout1"
color="4 7"
dataset=0
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0}
B 2 1460 -1900 2260 -1500 {flags=graph
y1=1.5
y2=3.3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="v(VDD)
v(VIO)"
color="4 21"
dataset=0
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0}
B 2 2280 -640 3080 -240 {flags=graph
y1=0.74
y2=0.76
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="inv2_vin2
inv2_vout2"
color="4 7"
dataset=0
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0}
B 2 2280 -1060 3080 -660 {flags=graph
y1=-0.56
y2=2.1
ypos1=-0.56
ypos2=2.1
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="inv1_dout1
inv1_dout2
inv1_dout3
inv1_dout4"
color="4 4 4 4"
dataset=0
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 2280 -1480 3080 -1080 {flags=graph
y1=-0.56
y2=2.1
ypos1=0.030713291
ypos2=2.4015049
divy=5
subdivy=1
unity=1
x1=0
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="counter1_value0
counter1_value1
counter1_value2
counter1_value3
\\"counter1_value4\\"; counter1_value4_inv1_din1
\\"counter1_value5\\"; counter1_value5_inv1_din2
\\"counter1_value6\\"; counter1_value6_inv1_din3
\\"counter1_value7\\"; counter1_value7_inv1_din4"
color="4 4 4 4 4 4 4 4"
dataset=0
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
T {Testbench for transient analysis - AMS Chip} 1105 -2385 0 0 1 1 {}
N 420 -2200 420 -2160 {lab=VDD}
N 420 -2100 420 -2060 {lab=GND}
N 420 -1600 420 -1560 {lab=GND}
N 420 -1720 420 -1660 {lab=clock}
N 820 -1600 820 -1560 {lab=GND}
N 820 -1720 820 -1660 {lab=reset_n}
N 460 -760 520 -760 {lab=GND}
N 620 -2200 620 -2160 {lab=VIO}
N 620 -2100 620 -2060 {lab=GND}
N 460 -640 520 -640 {lab=GND}
N 460 -760 460 -640 {lab=GND}
N 420 -700 520 -700 {lab=VDD}
N 380 -580 520 -580 {lab=sram_0_out}
N 380 -880 520 -880 {lab=enable}
N 380 -940 520 -940 {lab=reset_n}
N 380 -1000 520 -1000 {lab=clock}
N 580 -1200 580 -1060 {lab=counter1_value0}
N 640 -1200 640 -1060 {lab=counter1_value1}
N 700 -1200 700 -1060 {lab=counter1_value2}
N 760 -1200 760 -1060 {lab=counter1_value3}
N 820 -1200 820 -1060 {lab=counter1_value4_inv1_din1}
N 880 -1200 880 -1060 {lab=counter1_value5_inv1_din2}
N 940 -1200 940 -1060 {lab=counter1_value6_inv1_din3}
N 1000 -1200 1000 -1060 {lab=counter1_value7_inv1_din4}
N 1060 -1000 1200 -1000 {lab=inv1_dout4}
N 1060 -940 1200 -940 {lab=inv1_dout3}
N 1060 -880 1200 -880 {lab=inv1_dout2}
N 1060 -820 1200 -820 {lab=inv1_dout1}
N 1060 -760 1200 -760 {lab=inv2_vout2}
N 1060 -700 1200 -700 {lab=inv2_vout1}
N 580 -520 580 -380 {lab=counter2_value0}
N 640 -520 640 -380 {lab=counter2_value1}
N 700 -520 700 -380 {lab=counter2_value2}
N 760 -520 760 -380 {lab=counter2_value3}
N 820 -520 820 -380 {lab=counter2_value4}
N 880 -520 880 -380 {lab=counter2_value5}
N 940 -520 940 -380 {lab=counter2_value6}
N 1000 -520 1000 -380 {lab=counter2_value7}
N 460 -640 460 -380 {lab=GND}
N 420 -1200 420 -700 {lab=VDD}
N 380 -820 520 -820 {lab=VIO}
N 420 -1960 420 -1920 {lab=enable}
N 420 -1860 420 -1820 {lab=GND}
N 1120 -580 1200 -580 {lab=inv2_vin1}
N 1060 -640 1300 -640 {lab=inv2_vin2}
N 1120 -580 1120 -500 {lab=inv2_vin1}
N 1120 -440 1120 -380 {lab=GND}
N 1060 -580 1120 -580 {lab=inv2_vin1}
N 1300 -440 1300 -380 {lab=GND}
N 1300 -640 1300 -500 {lab=inv2_vin2}
C {devices/code.sym} 1760 -2070 0 0 {name=NGSPICE
only_toplevel=true 
value="
*.include ../../../verification/pex/chip_top_pex.spice
.include ../../../macros/counter/netlist/xspice/counter_top.xspice
.param IOVDD=3.3
.param VDD=1.5
.param Vcm=0.75
.param temp=27
.param Cload=10p
.param Rload=1k
.param fclk=50e6
.csparam fclk=fclk
.options klu method=gear reltol=3e-3 vntol=1e-5 abstol=1e-11 chgtol=1e-11 cshunt=100f
.control

set num_threads=32

* save all

* User Constants
let tstart = 0
let tstop = 10u
let tstep = 100n

* Transient Operating Point Analysis
*optran 0 0 0 $&tstep $&tstart 0
op
remzerovec
write @schname\\\\.raw
set appendwrite

* Transient Analysis
tran $&tstep $&tstop $&tstart
write @schname\\\\.raw

* Plotting
plot clock reset_n enable sram_0_out
plot inv2_vin1 inv2_vout1 inv2_vin2 inv2_vout2
plot inv1_dout1 inv1_dout2 inv1_dout3 inv1_dout4
plot counter2_value0 counter2_value1 counter2_value2 counter2_value3 counter2_value4 counter2_value5 counter2_value6 counter2_value7
plot counter1_value4_inv1_din1 counter1_value5_inv1_din2

* Write Data
unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata ../../../scripts/plot_simulations/data/chip_top_tb_tran.txt
+ v(clock) v(reset_n) v(enable) v(sram_0_out)
+ v(inv2_vin1) v(inv2_vout1) v(inv2_vin2) v(inv2_vout2)
+ v(inv1_dout1) v(inv1_dout2) v(inv1_dout3) v(inv1_dout4)
+ v(counter2_value0) v(counter2_value1) v(counter2_value2) v(counter2_value3)
+ v(counter2_value4) v(counter2_value5) v(counter2_value6) v(counter2_value7)
+ v(counter1_value4_inv1_din1) v(counter1_value5_inv1_din2)

*quit
*rusage all
.endc
"}
C {devices/launcher.sym} 1530 -2060 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1530 -1940 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw tran"
}
C {devices/launcher.sym} 1530 -2000 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/code_shown.sym} 1970 -2060 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib ../models/cornerDIO_custom.lib dio_tt
"}
C {devices/vsource.sym} 420 -2130 0 0 {name=VDD value=\{VDD\}}
C {devices/gnd.sym} 420 -2060 0 0 {name=l3 lab=GND}
C {vdd.sym} 420 -2200 0 0 {name=l7 lab=VDD}
C {devices/lab_wire.sym} 420 -1720 0 0 {name=p17 sig_type=std_logic lab=clock}
C {devices/gnd.sym} 420 -1560 0 0 {name=l11 lab=GND}
C {devices/vsource.sym} 420 -1630 0 0 {name=vclk value="pulse(0 \{IOVDD\} 0 100p 100p \{0.5/fclk\} \{1/fclk\})"
}
C {devices/lab_wire.sym} 820 -1720 0 0 {name=p18 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 820 -1560 0 0 {name=l10 lab=GND}
C {devices/vsource.sym} 820 -1630 0 0 {name=vrst value="pulse(\{IOVDD\} 0 \{2/fclk\} 100p 100p \{2/fclk\} 1 1)"
}
C {devices/lab_wire.sym} 380 -940 0 0 {name=p1 sig_type=std_logic lab=reset_n}
C {devices/lab_wire.sym} 380 -1000 0 0 {name=p2 sig_type=std_logic lab=clock}
C {title-2.sym} 0 0 0 0 {name=l9 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/gnd.sym} 460 -380 0 0 {name=l14 lab=GND}
C {vdd.sym} 420 -1200 0 0 {name=l16 lab=VDD}
C {devices/lab_wire.sym} 580 -1200 3 1 {name=p3 sig_type=std_logic lab=counter1_value0}
C {code_shown.sym} 1470 -2170 0 0 {name=PAD_MODELS
only_toplevel=true
value="tcleval(
.include $::PDK_ROOT/$::PDK/libs.ref/sg13g2_io/spice/sg13g2_io.spi
)"
spice_ignore=false
      }
C {devices/vsource.sym} 620 -2130 0 0 {name=VIO value=\{IOVDD\}}
C {devices/gnd.sym} 620 -2060 0 0 {name=l2 lab=GND
value=\{IOVDD\}}
C {devices/lab_wire.sym} 620 -2200 3 1 {name=p26 sig_type=std_logic lab=VIO}
C {chip_top.sym} 790 -790 0 0 {name=x1
}
C {devices/lab_wire.sym} 640 -1200 3 1 {name=p4 sig_type=std_logic lab=counter1_value1}
C {devices/lab_wire.sym} 700 -1200 3 1 {name=p5 sig_type=std_logic lab=counter1_value2}
C {devices/lab_wire.sym} 760 -1200 3 1 {name=p6 sig_type=std_logic lab=counter1_value3}
C {devices/lab_wire.sym} 580 -380 3 0 {name=p7 sig_type=std_logic lab=counter2_value0}
C {devices/lab_wire.sym} 640 -380 3 0 {name=p8 sig_type=std_logic lab=counter2_value1}
C {devices/lab_wire.sym} 700 -380 3 0 {name=p9 sig_type=std_logic lab=counter2_value2}
C {devices/lab_wire.sym} 760 -380 3 0 {name=p10 sig_type=std_logic lab=counter2_value3}
C {devices/lab_wire.sym} 820 -380 3 0 {name=p11 sig_type=std_logic lab=counter2_value4}
C {devices/lab_wire.sym} 880 -380 3 0 {name=p12 sig_type=std_logic lab=counter2_value5}
C {devices/lab_wire.sym} 940 -380 3 0 {name=p13 sig_type=std_logic lab=counter2_value6}
C {devices/lab_wire.sym} 1000 -380 3 0 {name=p14 sig_type=std_logic lab=counter2_value7}
C {devices/lab_wire.sym} 1200 -580 0 1 {name=p15 sig_type=std_logic lab=inv2_vin1}
C {devices/lab_wire.sym} 1200 -640 0 1 {name=p16 sig_type=std_logic lab=inv2_vin2}
C {devices/lab_wire.sym} 1200 -700 0 1 {name=p19 sig_type=std_logic lab=inv2_vout1}
C {devices/lab_wire.sym} 1200 -760 0 1 {name=p20 sig_type=std_logic lab=inv2_vout2}
C {devices/lab_wire.sym} 1200 -820 0 1 {name=p21 sig_type=std_logic lab=inv1_dout1}
C {devices/lab_wire.sym} 1200 -880 0 1 {name=p22 sig_type=std_logic lab=inv1_dout2}
C {devices/lab_wire.sym} 1200 -940 0 1 {name=p23 sig_type=std_logic lab=inv1_dout3}
C {devices/lab_wire.sym} 1200 -1000 0 1 {name=p24 sig_type=std_logic lab=inv1_dout4}
C {devices/lab_wire.sym} 380 -880 0 0 {name=p25 sig_type=std_logic lab=enable}
C {devices/lab_wire.sym} 380 -580 0 0 {name=p27 sig_type=std_logic lab=sram_0_out}
C {devices/lab_wire.sym} 380 -820 0 0 {name=p28 sig_type=std_logic lab=VIO}
C {devices/vsource.sym} 420 -1890 0 0 {name=Venable value="pulse(\{IOVDD\} 0 \{100/fclk\} 100p 100p \{100/fclk\} 1 1)"}
C {devices/gnd.sym} 420 -1820 0 0 {name=Venable1 lab=GND
value=\{IOVDD\}}
C {devices/lab_wire.sym} 420 -1960 0 0 {name=p29 sig_type=std_logic lab=enable}
C {devices/lab_wire.sym} 820 -1200 3 1 {name=p30 sig_type=std_logic lab=counter1_value4_inv1_din1}
C {devices/lab_wire.sym} 880 -1200 3 1 {name=p31 sig_type=std_logic lab=counter1_value5_inv1_din2}
C {devices/lab_wire.sym} 940 -1200 3 1 {name=p32 sig_type=std_logic lab=counter1_value6_inv1_din3}
C {devices/lab_wire.sym} 1000 -1200 3 1 {name=p33 sig_type=std_logic lab=counter1_value7_inv1_din4}
C {chip_top.sym} 3810 -330 0 0 {name=x2
spice_ignore=true}
C {chip_top_pex.sym} 3810 -990 0 0 {name=x3
spice_ignore=true}
C {devices/vsource.sym} 1120 -470 0 0 {name=vsine1 spice_ignore=False value="sin(\{Vcm\} 10m 200k)"
}
C {devices/gnd.sym} 1120 -380 0 1 {name=l26 lab=GND}
C {devices/vsource.sym} 1300 -470 0 0 {name=vsine2 spice_ignore=False value="sin(\{Vcm\} 10m 400k)"
}
C {devices/gnd.sym} 1300 -380 0 1 {name=l1 lab=GND}
