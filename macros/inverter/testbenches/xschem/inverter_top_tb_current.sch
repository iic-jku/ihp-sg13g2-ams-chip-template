v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Testbench for the current view - Quad Inverter (Top-Level)} 450 -1730 0 0 1 1 {}
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
* Current view of inverter_top (make current-view): the operating point at the
* worst case of the current limits, fast MOS at 1.65 V and 105 C, with every
* input at VDD/2, where each inverter draws its highest cross current
.param VDD=1.65
.csparam VDD=VDD
.param Vcm=VDD/2
.temp 105
.param Cload=10p
.param Rload=1k
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15
.control

save all
op
* current into the pins of the macro, VSS returns what VDD draws (the
* inputs and the capacitive loads carry no DC current)
let ivdd = -i(VDD)
let ivss = -ivdd
echo VDD $&ivdd > ../plot_simulations/data/inverter_top_tb_current.txt
echo VSS $&ivss >> ../plot_simulations/data/inverter_top_tb_current.txt
print ivdd

.endc
"}
C {devices/launcher.sym} 1720 -1330 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; file mkdir $netlist_dir; write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save; xschem simulate"
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
C {devices/vsource.sym} 760 -410 0 1 {name=vsine spice_ignore=False value=\{Vcm\}
}
C {devices/lab_pin.sym} 700 -460 0 0 {name=l22 sig_type=std_logic lab=vin}
C {devices/gnd.sym} 760 -360 0 0 {name=l26 lab=GND}
C {devices/code_shown.sym} 1980 -1330 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_ff
.lib cornerMOShv.lib mos_ff
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
value="
.include [file rootname [file tail [xschem get schname]]].save
"}
