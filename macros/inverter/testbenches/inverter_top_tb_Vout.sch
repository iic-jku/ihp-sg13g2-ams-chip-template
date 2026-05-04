v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1660 -720 2460 -320 {flags=graph
y1=0
y2=1.5
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1.5
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="vin
vout"
color="4 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0}
B 2 1660 -1160 2460 -760 {flags=graph
y1=-0.0008
y2=-7.4e-10
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1.5
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
T {Testbench for Output Voltage Swing analysis - Inverter} 520 -1730 0 0 1 1 {}
N 1320 -1100 1320 -1060 {lab=VDD}
N 1320 -1000 1320 -960 {lab=GND}
N 960 -860 960 -840 {lab=vin}
N 900 -860 960 -860 {lab=vin}
N 960 -860 1020 -860 {lab=vin}
N 1320 -860 1400 -860 {lab=vout}
N 1080 -960 1080 -900 {lab=VDD}
N 1080 -820 1080 -760 {lab=GND}
N 960 -780 960 -760 {lab=GND}
N 1220 -860 1220 -840 {lab=vout}
N 1160 -860 1220 -860 {lab=vout}
N 1220 -780 1220 -760 {lab=GND}
N 1320 -860 1320 -840 {lab=vout}
N 1220 -860 1320 -860 {lab=vout}
N 1320 -780 1320 -760 {lab=GND}
C {devices/code_shown.sym} 40 -1250 0 0 {name=NGSPICE
only_toplevel=true 
value="
.include ../../netlist/pex/iqmod_mfb_lpf_ota_core_inv_NF20_pex.spice
.param VDD=1.5
.csparam VDD=VDD
.param Vcm=VDD/2
.csparam Vcm=Vcm
.param temp=27
.param Cload=10p
.param Rload=1k
.options savecurrents klu method=gear reltol=1e-3 abstol=1e-15 gmin=1e-15
.control

save all

* Operating Point Analysis
op
remzerovec
write @schname\\\\.raw
set appendwrite

* DC Sweep
dc Vgsp 0 $&VDD 1m
remzerovec
write @schname\\\\.raw
set appendwrite

* Plotting
plot vin vout

* Measurement
meas dc Vgsp_at_Vcm when vout=Vcm
print Vgsp_at_Vcm

* Write Data
unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata $PROJECT_PATH/scripts/plot_simulations/data/iqmod_mfb_lpf_ota_core_inv_tb_Vout.txt v(vin) v(vout)

*quit
.endc
"}
C {devices/launcher.sym} 1720 -1340 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {title-3.sym} 0 0 0 0 {name=l2 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/launcher.sym} 1720 -1220 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw dc"
}
C {devices/launcher.sym} 1720 -1280 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/code_shown.sym} 1960 -1330 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerDIO.lib dio_tt
"}
C {devices/vsource.sym} 1320 -1030 0 0 {name=VDD value=\{VDD\}}
C {devices/gnd.sym} 1320 -960 0 0 {name=l3 lab=GND}
C {vdd.sym} 1320 -1100 0 0 {name=l7 lab=VDD}
C {devices/lab_pin.sym} 1400 -860 0 1 {name=l12 sig_type=std_logic lab=vout}
C {devices/lab_pin.sym} 900 -860 0 0 {name=l22 sig_type=std_logic lab=vin}
C {devices/gnd.sym} 960 -760 0 0 {name=l26 lab=GND}
C {devices/gnd.sym} 1080 -760 0 0 {name=l1 lab=GND}
C {capa.sym} 1220 -810 0 0 {name=C1
m=1
value=\{Cload\}
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 1320 -810 0 0 {name=R1
value=\{Rload\}
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {vdd.sym} 1080 -960 0 0 {name=l4 lab=VDD}
C {devices/gnd.sym} 1220 -760 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} 1320 -760 0 0 {name=l6 lab=GND}
C {devices/vsource.sym} 960 -810 0 0 {name=Vgsp value=0
}
C {iqmod_mfb_lpf_ota_core_inv_NF20.sym} 1080 -1160 0 0 {name=x1
spice_ignore=true}
C {iqmod_mfb_lpf_ota_core_inv_NF20_pex.sym} 1080 -1340 0 0 {name=x2
spice_ignore=true}
C {iqmod_mfb_lpf_ota_core_inv_NF20_pex.sym} 1080 -860 0 0 {name=x3
}
