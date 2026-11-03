v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {VCO Core, Voltage-Biased NMOS Cross-Coupled Pair} 300 -1740 0 0 1 1 {}
T {After Jung and Park, Electronics Letters 44(10), 2008: no current source,
the center tap of the coil sits on its own supply vdd_core (0.72 V, own pad).
The tank common mode is vdd_core, so vtune from 0 V to VDD sweeps the
accumulation-mode varactors across their C-V transition at 0 V gate-to-well.
Each tank node swings from about 0.12 V to 1.35 V, 1.9 times vdd_core.
The pair draws 4.05 mA at Vgs = vdd_core. Cct1 and Cct2 (4.9 pF) decouple
vdd_core at the center tap.} 1440 -1440 0 0 0.3 0.3 {}
N 1120 -280 1340 -280 {lab=VSS}
N 880 -1260 880 -1220 {lab=vdd_core}
N 880 -1260 1120 -1260 {lab=vdd_core}
N 1120 -1260 1220 -1260 {lab=vdd_core}
N 700 -1160 780 -1160 {lab=rf_p}
N 980 -1160 1060 -1160 {lab=rf_n}
N 700 -880 780 -880 {lab=rf_p}
N 980 -880 1060 -880 {lab=rf_n}
N 880 -980 880 -940 {lab=vtune}
N 520 -980 880 -980 {lab=vtune}
N 700 -1160 700 -880 {lab=rf_p}
N 700 -880 700 -660 {lab=rf_p}
N 700 -660 700 -600 {lab=rf_p}
N 700 -600 700 -490 {lab=rf_p}
N 1060 -1160 1060 -880 {lab=rf_n}
N 1060 -880 1060 -660 {lab=rf_n}
N 1060 -660 1060 -600 {lab=rf_n}
N 1060 -600 1060 -490 {lab=rf_n}
N 740 -460 780 -460 {lab=rf_n}
N 780 -460 980 -600 {lab=rf_n}
N 980 -600 1060 -600 {lab=rf_n}
N 980 -460 1020 -460 {lab=rf_p}
N 780 -600 980 -460 {lab=rf_p}
N 700 -600 780 -600 {lab=rf_p}
N 700 -430 700 -280 {lab=VSS}
N 1060 -430 1060 -280 {lab=VSS}
N 640 -460 700 -460 {lab=VSS}
N 640 -460 640 -280 {lab=VSS}
N 1060 -460 1120 -460 {lab=VSS}
N 1120 -460 1120 -280 {lab=VSS}
N 520 -660 700 -660 {lab=rf_p}
N 1060 -660 1240 -660 {lab=rf_n}
N 420 -1460 880 -1460 {lab=vdd_core}
N 880 -1460 880 -1260 {lab=vdd_core}
N 640 -280 700 -280 {lab=VSS}
N 700 -280 1060 -280 {lab=VSS}
N 420 -280 640 -280 {lab=VSS}
N 1060 -280 1120 -280 {lab=VSS}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/iopin.sym} 420 -1460 0 1 {name=p1 lab=vdd_core}
C {devices/iopin.sym} 420 -280 0 1 {name=p2 lab=VSS}
C {vco_ind.sym} 800 -1120 0 0 {name=xind}
C {sg13g2_pr/cap_cmim.sym} 1120 -1230 0 0 {name=Cct1
w=56e-6
l=39e-6
m=1
model=cap_cmim
spiceprefix=X}
C {devices/lab_pin.sym} 1120 -1200 1 0 {name=l1 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 920 -1100 1 0 {name=l2 sig_type=std_logic lab=VSS}
C {vco_var.sym} 800 -840 0 0 {name=xvar}
C {devices/ipin.sym} 520 -980 0 0 {name=p4 lab=vtune}
C {devices/lab_pin.sym} 920 -820 1 0 {name=l4 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 720 -460 0 1 {name=M1
l=0.13u
w=20u
ng=10
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {sg13g2_pr/sg13_lv_nmos.sym} 1040 -460 0 0 {name=M2
l=0.13u
w=20u
ng=10
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {devices/iopin.sym} 520 -660 0 1 {name=p5 lab=rf_p}
C {devices/iopin.sym} 1240 -660 0 0 {name=p6 lab=rf_n}
C {sg13g2_pr/cap_cmim.sym} 1220 -1230 0 0 {name=Cct2
w=42e-6
l=25.5e-6
m=1
model=cap_cmim
spiceprefix=X}
C {devices/lab_pin.sym} 1220 -1200 1 0 {name=l3 sig_type=std_logic lab=VSS}
