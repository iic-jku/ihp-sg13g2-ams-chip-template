v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 2540 -1920 3340 -1520 {flags=graph
y1=-0.56
y2=2.1
ypos1=0.1
ypos2=2.1
divy=5
subdivy=1
unity=1
x1=-0.0074551832
x2=-0.0054407567
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="clock
reset_n
analog_en
spi_si
spi_sclk
spi_sram_ce
uart_tx"
color="4 21 12 17 17 17 5"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 2540 -1500 3340 -1100 {flags=graph
y1=-0.56
y2=2.1
ypos1=0.4
ypos2=2.4
divy=5
subdivy=1
unity=1
x1=-0.0074551832
x2=-0.0054407567
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="i2c_sda
i2c_sda_oe
i2c_scl
gpio_0
gpio_1
gpio_2
gpio_3"
color="4 4 4 21 21 21 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 2540 -1080 3340 -680 {flags=graph
y1=-0.56
y2=2.1
ypos1=0.4
ypos2=2.4
divy=5
subdivy=1
unity=1
x1=-0.0074551832
x2=-0.0054407567
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="I_ae
ds_I_oe
ds_I_p
ds_I_n
ds_Q_n
ds_Q_p
ds_Q_oe
Q_ae"
color="4 4 4 4 21 21 21 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 2540 -660 3340 -260 {flags=graph
y1=-0.56
y2=2.1
ypos1=0.5
ypos2=2.5
divy=5
subdivy=1
unity=1
x1=-0.0074551832
x2=-0.0054407567
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="lo_I_oe
lo_I
lo_Ix
lo_Qx
lo_Q
lo_Q_oe"
color="4 4 4 21 21 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
T {Testbench for transient analysis - WSPR Transmitter RISC-V CPU} 840 -2310 0 0 1 1 {}
N 1220 -1720 1220 -1680 {lab=VDD}
N 1220 -1620 1220 -1580 {lab=GND}
N 1540 -1620 1540 -1580 {lab=GND}
N 1540 -1740 1540 -1680 {lab=clock}
N 1220 -1420 1220 -1400 {lab=VDD}
N 1220 -400 1220 -380 {lab=GND}
N 1900 -1620 1900 -1580 {lab=GND}
N 1900 -1740 1900 -1680 {lab=reset_n}
N 680 -400 680 -360 {lab=gpio_0}
N 740 -400 740 -360 {lab=gpio_1}
N 800 -400 800 -360 {lab=gpio_2}
N 860 -400 860 -360 {lab=gpio_3}
N 240 -560 240 -380 {lab=GND}
N 240 -1080 280 -1080 {lab=GND}
N 240 -820 280 -820 {lab=GND}
N 240 -1080 240 -820 {lab=GND}
N 240 -560 280 -560 {lab=GND}
N 240 -820 240 -560 {lab=GND}
N 860 -1440 860 -1400 {lab=GND}
N 800 -1440 860 -1440 {lab=GND}
N 240 -1440 240 -1080 {lab=GND}
N 680 -1440 680 -1400 {lab=GND}
N 240 -1440 680 -1440 {lab=GND}
N 740 -1440 740 -1400 {lab=GND}
N 680 -1440 740 -1440 {lab=GND}
N 800 -1440 800 -1400 {lab=GND}
N 740 -1440 800 -1440 {lab=GND}
N 200 -1280 280 -1280 {lab=clock}
N 200 -1220 280 -1220 {lab=reset_n}
N 200 -1040 280 -1040 {lab=spi_si}
N 200 -1000 280 -1000 {lab=spi_sclk}
N 200 -960 280 -960 {lab=spi_sram_ce}
N 200 -780 280 -780 {lab=i2c_sda}
N 200 -740 280 -740 {lab=i2c_sda_oe}
N 200 -700 280 -700 {lab=i2c_scl}
N 200 -520 280 -520 {lab=uart_tx}
N 2160 -1320 2240 -1320 {lab=I_ae}
N 2160 -1280 2240 -1280 {lab=ds_I_oe}
N 2160 -1200 2240 -1200 {lab=ds_I_p}
N 2160 -1120 2240 -1120 {lab=ds_I_n}
N 2160 -480 2240 -480 {lab=Q_ae}
N 2160 -520 2240 -520 {lab=ds_Q_oe}
N 2160 -600 2240 -600 {lab=ds_Q_p}
N 2160 -680 2240 -680 {lab=ds_Q_n}
N 2160 -1080 2240 -1080 {lab=lo_I_oe}
N 2160 -1000 2240 -1000 {lab=lo_I}
N 2160 -920 2240 -920 {lab=lo_Ix}
N 2160 -720 2240 -720 {lab=lo_Q_oe}
N 2160 -800 2240 -800 {lab=lo_Q}
N 2160 -880 2240 -880 {lab=lo_Qx}
N 2200 -560 2200 -380 {lab=GND}
N 2160 -1240 2200 -1240 {lab=GND}
N 2160 -560 2200 -560 {lab=GND}
N 2200 -640 2200 -560 {lab=GND}
N 2160 -640 2200 -640 {lab=GND}
N 2200 -760 2200 -640 {lab=GND}
N 2160 -760 2200 -760 {lab=GND}
N 2200 -840 2200 -760 {lab=GND}
N 2160 -840 2200 -840 {lab=GND}
N 2200 -960 2200 -840 {lab=GND}
N 2160 -960 2200 -960 {lab=GND}
N 2200 -1040 2200 -960 {lab=GND}
N 2160 -1040 2200 -1040 {lab=GND}
N 2200 -1160 2200 -1040 {lab=GND}
N 2160 -1160 2200 -1160 {lab=GND}
N 2200 -1240 2200 -1160 {lab=GND}
N 2080 -1400 2240 -1400 {lab=analog_en}
C {devices/code_shown.sym} 80 -2110 0 0 {name=NGSPICE
only_toplevel=true 
value="
* Gate-Level Analog Mixed Signal Simulation (.xspice)
.include /foss/designs/Chip/ihp130/macros/riscv/netlist/xspice/riscv_top/riscv_top.xspice
.param VDD=1.5
.param temp=27
.param fclk=56e6
.csparam fclk=fclk
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15
.control

set num_threads=16

save all

* User Constants
let tstop = 25u
let tstep = 1/fclk

* Operating Point Analysis
op
remzerovec
write @schname\\\\.raw
set appendwrite

* Transient Analysis
tran $&tstep $&tstop
write @schname\\\\.raw

*quit
.endc
"}
C {devices/vsource.sym} 1220 -1650 0 0 {name=VDD value=\{VDD\}}
C {devices/gnd.sym} 1220 -1580 0 0 {name=l3 lab=GND}
C {devices/launcher.sym} 2600 -2130 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 2600 -2010 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw tran"
}
C {devices/launcher.sym} 2600 -2070 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {vdd.sym} 1220 -1720 0 0 {name=l7 lab=VDD}
C {devices/lab_wire.sym} 1540 -1740 0 0 {name=p17 sig_type=std_logic lab=clock}
C {devices/gnd.sym} 1540 -1580 0 0 {name=l11 lab=GND}
C {devices/vsource.sym} 1540 -1650 0 0 {name=vclk value="pulse(0 \{VDD\} 0 10p 10p \{0.5/fclk\} \{1/fclk\})"
}
C {devices/code_shown.sym} 2880 -2120 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerDIO.lib dio_tt
"}
C {title-2.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/lab_wire.sym} 1900 -1740 0 0 {name=p18 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 1900 -1580 0 0 {name=l10 lab=GND}
C {devices/vsource.sym} 1900 -1650 0 0 {name=vrst value="pulse(\{VDD\} 0 \{2/fclk\} 10p 10p \{2/fclk\} 1 1)"
}
C {vdd.sym} 1220 -1420 0 0 {name=l2 lab=VDD}
C {devices/gnd.sym} 1220 -380 0 0 {name=l4 lab=GND}
C {devices/lab_wire.sym} 200 -1220 0 0 {name=p1 sig_type=std_logic lab=reset_n}
C {devices/lab_wire.sym} 200 -1280 0 0 {name=p2 sig_type=std_logic lab=clock}
C {devices/lab_wire.sym} 680 -360 3 0 {name=p3 sig_type=std_logic lab=gpio_0}
C {devices/lab_wire.sym} 740 -360 3 0 {name=p4 sig_type=std_logic lab=gpio_1}
C {devices/lab_wire.sym} 800 -360 3 0 {name=p5 sig_type=std_logic lab=gpio_2}
C {devices/lab_wire.sym} 860 -360 3 0 {name=p6 sig_type=std_logic lab=gpio_3}
C {devices/lab_wire.sym} 200 -700 0 0 {name=p7 sig_type=std_logic lab=i2c_scl}
C {devices/lab_wire.sym} 200 -740 0 0 {name=p8 sig_type=std_logic lab=i2c_sda_oe}
C {devices/lab_wire.sym} 200 -780 0 0 {name=p9 sig_type=std_logic lab=i2c_sda}
C {devices/lab_wire.sym} 200 -520 0 0 {name=p10 sig_type=std_logic lab=uart_tx}
C {devices/lab_wire.sym} 200 -960 0 0 {name=p11 sig_type=std_logic lab=spi_sram_ce}
C {devices/lab_wire.sym} 200 -1000 0 0 {name=p12 sig_type=std_logic lab=spi_sclk}
C {devices/lab_wire.sym} 200 -1040 0 0 {name=p13 sig_type=std_logic lab=spi_si}
C {devices/gnd.sym} 240 -380 0 0 {name=l5 lab=GND}
C {devices/lab_wire.sym} 2240 -1320 0 1 {name=p14 sig_type=std_logic lab=I_ae}
C {devices/lab_wire.sym} 2240 -1280 0 1 {name=p15 sig_type=std_logic lab=ds_I_oe}
C {devices/lab_wire.sym} 2240 -1200 0 1 {name=p16 sig_type=std_logic lab=ds_I_p}
C {devices/lab_wire.sym} 2240 -1120 0 1 {name=p19 sig_type=std_logic lab=ds_I_n}
C {devices/lab_wire.sym} 2240 -1080 0 1 {name=p20 sig_type=std_logic lab=lo_I_oe}
C {devices/lab_wire.sym} 2240 -1000 0 1 {name=p21 sig_type=std_logic lab=lo_I}
C {devices/lab_wire.sym} 2240 -920 0 1 {name=p22 sig_type=std_logic lab=lo_Ix}
C {devices/lab_wire.sym} 2240 -480 0 1 {name=p30 sig_type=std_logic lab=Q_ae}
C {devices/lab_wire.sym} 2240 -520 0 1 {name=p31 sig_type=std_logic lab=ds_Q_oe}
C {devices/lab_wire.sym} 2240 -600 0 1 {name=p32 sig_type=std_logic lab=ds_Q_p}
C {devices/lab_wire.sym} 2240 -680 0 1 {name=p33 sig_type=std_logic lab=ds_Q_n}
C {devices/lab_wire.sym} 2240 -720 0 1 {name=p23 sig_type=std_logic lab=lo_Q_oe}
C {devices/lab_wire.sym} 2240 -800 0 1 {name=p24 sig_type=std_logic lab=lo_Q}
C {devices/lab_wire.sym} 2240 -880 0 1 {name=p25 sig_type=std_logic lab=lo_Qx}
C {devices/gnd.sym} 2200 -380 0 0 {name=l6 lab=GND}
C {riscv_top.sym} 1220 -900 0 0 {name=x1}
C {devices/lab_wire.sym} 2240 -1400 0 1 {name=p26 sig_type=std_logic lab=analog_en}
