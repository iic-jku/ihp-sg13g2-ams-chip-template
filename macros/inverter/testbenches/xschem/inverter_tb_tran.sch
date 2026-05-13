v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1640 -1240 2440 -840 {flags=graph
y1=-0.0008
y2=-0.00074
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
B 2 1640 -820 2440 -420 {flags=graph
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
vout"
color="4 7"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0}
T {Testbench for transient analysis - Inverter} 740 -1730 0 0 1 1 {}
N 1380 -1080 1380 -1040 {lab=VDD}
N 1380 -980 1380 -940 {lab=GND}
N 980 -840 980 -820 {lab=vin}
N 920 -840 980 -840 {lab=vin}
N 980 -840 1040 -840 {lab=vin}
N 1380 -840 1460 -840 {lab=vout}
N 980 -760 980 -740 {lab=GND}
N 1260 -840 1260 -820 {lab=vout}
N 1380 -840 1380 -820 {lab=vout}
N 1260 -840 1380 -840 {lab=vout}
N 1180 -840 1260 -840 {lab=vout}
N 1260 -760 1260 -740 {lab=GND}
N 1380 -760 1380 -740 {lab=GND}
N 1100 -940 1100 -880 {lab=VDD}
N 1100 -800 1100 -740 {lab=GND}
C {devices/code_shown.sym} 80 -1370 0 0 {name=NGSPICE
only_toplevel=true 
value="
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
plot vin vout
plot i(VDD)

* Measurements
meas tran vin_peak MAX v(vin)
meas tran vout_peak MAX v(vout)

let Adm = vout_peak / vin_peak
let Adm_dB = vdb(Adm)
print Adm_dB

meas tran vout_pp_max MAX v(vout)
meas tran vout_pp_min MIN v(vout)
let vout_pp = vout_pp_max - vout_pp_min
print vout_pp

* Write Data
unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata ../../../scripts/plot_simulations/data/@schname\\\\.txt v(vin) v(vout)

*quit
.endc
"}
C {devices/launcher.sym} 1700 -1410 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {title-3.sym} 0 0 0 0 {name=l2 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/launcher.sym} 1700 -1290 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw tran"
}
C {devices/launcher.sym} 1700 -1350 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/vsource.sym} 1380 -1010 0 0 {name=VDD value=\{VDD\}}
C {devices/gnd.sym} 1380 -940 0 0 {name=l3 lab=GND}
C {vdd.sym} 1380 -1080 0 0 {name=l7 lab=VDD}
C {devices/lab_pin.sym} 1460 -840 0 1 {name=l12 sig_type=std_logic lab=vout}
C {devices/vsource.sym} 980 -790 0 1 {name=vsine spice_ignore=False value="sin(\{Vcm\} 10m 1k)"
}
C {devices/lab_pin.sym} 920 -840 0 0 {name=l22 sig_type=std_logic lab=vin}
C {devices/gnd.sym} 980 -740 0 0 {name=l26 lab=GND}
C {devices/code_shown.sym} 1960 -1410 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerDIO.lib dio_tt
"}
C {devices/gnd.sym} 1100 -740 0 0 {name=l1 lab=GND}
C {vdd.sym} 1100 -940 0 0 {name=l4 lab=VDD}
C {capa.sym} 1260 -790 0 0 {name=C1
m=1
value=\{Cload\}
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 1380 -790 0 0 {name=R1
value=\{Rload\}
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/gnd.sym} 1260 -740 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} 1380 -740 0 0 {name=l6 lab=GND}
C {inverter.sym} 1100 -840 0 0 {name=x1}
C {devices/code_shown.sym} 1630 -1510 0 0 {name=SAVE only_toplevel=true
format="tcleval( @value )"
value=".include [file rootname [xschem get schname]].save
"}
