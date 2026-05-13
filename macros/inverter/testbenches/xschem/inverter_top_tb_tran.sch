v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1660 -1160 2460 -760 {flags=graph
y1=-0.0032
y2=-0.0029
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=0.005
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0


dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
color=4
node=i(VDD)}
B 2 1660 -740 2460 -340 {flags=graph
y1=0.33
y2=0.99
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=0.005
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="vin
vout1
vout2
vout3
vout4"
color="4 7 10 12 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0}
T {Testbench for transient analysis - Quad Inverter (Top-Level)} 450 -1730 0 0 1 1 {}
N 1000 -920 1000 -880 {lab=VDD}
N 1000 -820 1000 -780 {lab=GND}
N 760 -460 760 -440 {lab=vin}
N 700 -460 760 -460 {lab=vin}
N 840 -460 880 -460 {lab=vin}
N 1440 -460 1520 -460 {lab=vout1}
N 760 -380 760 -360 {lab=GND}
N 1320 -460 1320 -440 {lab=vout1}
N 1440 -460 1440 -440 {lab=vout1}
N 1320 -460 1440 -460 {lab=vout1}
N 1320 -380 1320 -360 {lab=GND}
N 1440 -380 1440 -360 {lab=GND}
N 1000 -380 1000 -360 {lab=GND}
N 1000 -680 1000 -660 {lab=VDD}
N 840 -580 880 -580 {lab=vin}
N 840 -500 840 -460 {lab=vin}
N 760 -460 840 -460 {lab=vin}
N 840 -540 880 -540 {lab=vin}
N 840 -580 840 -540 {lab=vin}
N 840 -500 880 -500 {lab=vin}
N 840 -540 840 -500 {lab=vin}
N 1440 -620 1520 -620 {lab=vout2}
N 1320 -620 1320 -600 {lab=vout2}
N 1440 -620 1440 -600 {lab=vout2}
N 1320 -620 1440 -620 {lab=vout2}
N 1320 -540 1320 -520 {lab=GND}
N 1440 -540 1440 -520 {lab=GND}
N 1440 -780 1520 -780 {lab=vout3}
N 1320 -780 1320 -760 {lab=vout3}
N 1440 -780 1440 -760 {lab=vout3}
N 1320 -780 1440 -780 {lab=vout3}
N 1320 -700 1320 -680 {lab=GND}
N 1440 -700 1440 -680 {lab=GND}
N 1440 -940 1520 -940 {lab=vout4}
N 1320 -940 1320 -920 {lab=vout4}
N 1440 -940 1440 -920 {lab=vout4}
N 1320 -940 1440 -940 {lab=vout4}
N 1320 -860 1320 -840 {lab=GND}
N 1440 -860 1440 -840 {lab=GND}
N 1120 -580 1160 -580 {lab=vout4}
N 1120 -540 1200 -540 {lab=vout3}
N 1120 -500 1240 -500 {lab=vout2}
N 1240 -620 1240 -500 {lab=vout2}
N 1120 -460 1320 -460 {lab=vout1}
N 1240 -620 1320 -620 {lab=vout2}
N 1200 -780 1320 -780 {lab=vout3}
N 1200 -780 1200 -540 {lab=vout3}
N 1160 -940 1160 -580 {lab=vout4}
N 1160 -940 1320 -940 {lab=vout4}
C {devices/code_shown.sym} 60 -1410 0 0 {name=NGSPICE
only_toplevel=true 
value="
.include ../../../netlist/pex/inverter_top_magic_pex_3.spice
.param VDD=1.5
.csparam VDD=VDD
.param Vcm=VDD/2
.param temp=27
.param Cload=10p
.param Rload=1k
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15
.control

save all

* Operating Point Analysis
op
remzerovec
write @schname\\\\.raw
set appendwrite

* Transient Analysis
tran 1u 5m
write @schname\\\\.raw

* Plotting
plot vin vout1 vout2 vout3 vout4
plot i(VDD)

* Measurements
meas tran vin_peak MAX v(vin)
meas tran vout_peak MAX v(vout1)

let Adm = vout_peak / vin_peak
let Adm_dB = vdb(Adm)
print Adm_dB

meas tran vout_pp_max MAX v(vout1)
meas tran vout_pp_min MIN v(vout1)
let vout_pp = vout_pp_max - vout_pp_min
print vout_pp

* Write Data
unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata ../../../scripts/plot_simulations/data/@schname\\\\.txt
+ v(vin) v(vout1) v(vout2) v(vout3) v(vout4)

*quit
.endc
"}
C {devices/launcher.sym} 1720 -1330 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {title-3.sym} 0 0 0 0 {name=l2 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/launcher.sym} 1720 -1210 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw tran"
}
C {devices/launcher.sym} 1720 -1270 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/vsource.sym} 1000 -850 0 0 {name=VDD value=\{VDD\}}
C {devices/gnd.sym} 1000 -780 0 0 {name=l3 lab=GND}
C {vdd.sym} 1000 -920 0 0 {name=l7 lab=VDD}
C {devices/lab_pin.sym} 1520 -460 0 1 {name=l12 sig_type=std_logic lab=vout1}
C {devices/vsource.sym} 760 -410 0 1 {name=vsine spice_ignore=False value="sin(\{Vcm\} 10m 1k)"
}
C {devices/lab_pin.sym} 700 -460 0 0 {name=l22 sig_type=std_logic lab=vin}
C {devices/gnd.sym} 760 -360 0 0 {name=l26 lab=GND}
C {devices/code_shown.sym} 1980 -1330 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerDIO.lib dio_tt
"}
C {vdd.sym} 1000 -680 0 0 {name=l4 lab=VDD}
C {capa.sym} 1320 -410 0 0 {name=C1
m=1
value=\{Cload\}
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 1440 -410 0 0 {name=R1
value=\{Rload\}
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/gnd.sym} 1320 -360 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} 1440 -360 0 0 {name=l6 lab=GND}
C {inverter_top.sym} 1000 -1180 0 0 {name=x2
spice_ignore=true}
C {inverter_top_pex.sym} 1360 -1180 0 0 {name=x3
spice_ignore=true}
C {devices/gnd.sym} 1000 -360 0 0 {name=l8 lab=GND}
C {devices/lab_pin.sym} 1520 -620 0 1 {name=l1 sig_type=std_logic lab=vout2}
C {capa.sym} 1320 -570 0 0 {name=C2
m=1
value=\{Cload\}
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 1440 -570 0 0 {name=R2
value=\{Rload\}
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/gnd.sym} 1320 -520 0 0 {name=l9 lab=GND}
C {devices/gnd.sym} 1440 -520 0 0 {name=l10 lab=GND}
C {devices/lab_pin.sym} 1520 -780 0 1 {name=l11 sig_type=std_logic lab=vout3}
C {capa.sym} 1320 -730 0 0 {name=C3
m=1
value=\{Cload\}
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 1440 -730 0 0 {name=R3
value=\{Rload\}
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/gnd.sym} 1320 -680 0 0 {name=l13 lab=GND}
C {devices/gnd.sym} 1440 -680 0 0 {name=l14 lab=GND}
C {devices/lab_pin.sym} 1520 -940 0 1 {name=l15 sig_type=std_logic lab=vout4}
C {capa.sym} 1320 -890 0 0 {name=C4
m=1
value=\{Cload\}
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 1440 -890 0 0 {name=R4
value=\{Rload\}
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/gnd.sym} 1320 -840 0 0 {name=l16 lab=GND}
C {devices/gnd.sym} 1440 -840 0 0 {name=l17 lab=GND}
C {inverter_top.sym} 1000 -520 0 0 {name=x1}
C {devices/code_shown.sym} 1650 -1430 0 0 {name=SAVE only_toplevel=true
format="tcleval( @value )"
value=".include [file rootname [xschem get schname]].save
"}
