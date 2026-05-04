v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1640 -700 2440 -300 {flags=graph
y1=13
y2=180
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-1
x2=10
divx=5
subdivx=8
xlabmag=1.0
ylabmag=1.0
node="\\"OL Phase; ph(vout)\\""
color=4
dataset=-1
unitx=1
logx=1
logy=0
linewidth_mult=4}
B 2 1640 -1120 2440 -720 {flags=graph
y1=-27
y2=32
ypos1=0
ypos2=2
divy=5
subdivy=4
unity=1
x1=-1
x2=10
divx=5
subdivx=8
xlabmag=1.0
ylabmag=1.0
node="\\"OL Magnitude; vout vin / db20()\\""
color=4
dataset=-1
unitx=1
logx=1
logy=0
linewidth_mult=4}
T {Design Testbench for AC OL analysis - Inverter} 600 -1730 0 0 1 1 {}
N 1360 -1080 1360 -1040 {lab=VDD}
N 1360 -980 1360 -940 {lab=GND}
N 1000 -840 1000 -820 {lab=vin}
N 940 -840 1000 -840 {lab=vin}
N 1000 -840 1060 -840 {lab=vin}
N 1360 -840 1440 -840 {lab=vout}
N 1120 -940 1120 -880 {lab=VDD}
N 1120 -800 1120 -740 {lab=GND}
N 1000 -760 1000 -740 {lab=GND}
N 1260 -840 1260 -820 {lab=vout}
N 1200 -840 1260 -840 {lab=vout}
N 1360 -840 1360 -820 {lab=vout}
N 1260 -840 1360 -840 {lab=vout}
N 1260 -760 1260 -740 {lab=GND}
N 1360 -760 1360 -740 {lab=GND}
C {devices/code_shown.sym} 60 -1450 0 0 {name=NGSPICE
only_toplevel=true 
value="
.include ../../netlist/pex/iqmod_mfb_lpf_ota_core_inv_NF20_pex.spice
.param VDD=1.5
.param Vcm=VDD/2
.param temp=27
.param Cload=10p
.param Rload=1k
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15
.control

* optran 0 0 0 1u 1m 0
save all

set wr_vecnames
set wr_singlescale

* User Constants
let f_min = 0.1
let f_max = 10G
let fdc = 1

* Operating Point Analysis
op
remzerovec
write @schname\\\\.raw
set appendwrite

* AC Analysis
ac dec 101 $&const.f_min $&const.f_max
remzerovec
write @schname\\\\.raw

* Plotting
let Aol = v(vout)/v(vin)		
let Aol_dB = vdb(Aol)
let Aol_arg = 180/PI*cphase(Aol)

plot Aol_dB ylabel 'Magnitude'
plot Aol_arg ylabel 'Phase'
plot Aol_dB Aol_arg ylabel 'Magnitude, Phase'

* Measurements
* DC open-loop gain
meas ac Adc_ol_dB find Aol_dB when frequency = fdc
print Adc_ol_dB

* 3dB cut-off frequency
let Aol_fc = Adc_ol_dB - 3
meas ac fc find frequency when Aol_dB = Aol_fc
print fc

* Unity Gain Bandwidth (Aol=1 or Aol_dB = 0dB)
meas ac UGB when Aol_dB=0  fall=1
print UGB

* Phase Margin at Aol=1 or Aol_dB = 0dB
meas ac arg_0dB find Aol_arg when Aol_dB=0
let PM = 180-abs(arg_0dB)
print PM

* Write Data
unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata $PROJECT_PATH/scripts/plot_simulations/data/iqmod_mfb_lpf_ota_core_inv_tb_ac_ol.txt v(Aol_dB) v(Aol_arg)

*quit
.endc
"}
C {devices/launcher.sym} 1700 -1280 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {title-3.sym} 0 0 0 0 {name=l2 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/launcher.sym} 1700 -1160 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw ac"
}
C {devices/launcher.sym} 1700 -1220 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/code_shown.sym} 1960 -1270 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerDIO.lib dio_tt
"}
C {devices/vsource.sym} 1360 -1010 0 0 {name=VDD value=\{VDD\}}
C {devices/gnd.sym} 1360 -940 0 0 {name=l3 lab=GND}
C {vdd.sym} 1360 -1080 0 0 {name=l7 lab=VDD}
C {devices/lab_pin.sym} 1440 -840 0 1 {name=l12 sig_type=std_logic lab=vout}
C {devices/vsource.sym} 1000 -790 0 1 {name=vin spice_ignore=False value="dc \{Vcm\} ac 1"
}
C {devices/lab_pin.sym} 940 -840 0 0 {name=l22 sig_type=std_logic lab=vin}
C {devices/gnd.sym} 1000 -740 0 0 {name=l26 lab=GND}
C {devices/gnd.sym} 1120 -740 0 0 {name=l1 lab=GND}
C {vdd.sym} 1120 -940 0 0 {name=l4 lab=VDD}
C {devices/code_shown.sym} 1640 -1370 0 0 {name=SAVE only_toplevel=true
format="tcleval( @value )"
value=".include [file rootname [xschem get schname]].save
"}
C {capa.sym} 1260 -790 0 0 {name=C1
m=1
value=\{Cload\}
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 1360 -790 0 0 {name=R1
value=\{Rload\}
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/gnd.sym} 1260 -740 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} 1360 -740 0 0 {name=l6 lab=GND}
C {iqmod_mfb_lpf_ota_core_inv_NF20.sym} 1120 -1160 0 0 {name=x1
spice_ignore=true}
C {iqmod_mfb_lpf_ota_core_inv_NF20_pex.sym} 1120 -1340 0 0 {name=x2
spice_ignore=true}
C {iqmod_mfb_lpf_ota_core_inv_NF20_pex.sym} 1120 -840 0 0 {name=x3
}
