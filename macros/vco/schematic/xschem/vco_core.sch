v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {VCO Core, Top-Biased NMOS Cross-Coupled Pair} 300 -1740 0 0 1 1 {}
T {Mtop feeds the center tap, so the tank common mode settles at the
Vgs of M1 and M2, about 0.75 V. vtune from 0 V to VDD then sweeps
the accumulation-mode varactors across their C-V transition at 0 V
gate-to-well. Cct shorts the current-source noise at 2 f0.
Core current 3 mA, tank swing 0.08 V to 1.35 V per node.} 1440 -1440 0 0 0.3 0.3 {}
N 940 -1460 1340 -1460 {lab=VDD}
N 1120 -280 1340 -280 {lab=VSS}
N 880 -1460 880 -1390 {lab=VDD}
N 880 -1360 940 -1360 {lab=VDD}
N 940 -1460 940 -1360 {lab=VDD}
N 520 -1360 840 -1360 {lab=vbp_core}
N 880 -1330 880 -1260 {lab=vct}
N 880 -1260 880 -1220 {lab=vct}
N 880 -1260 1120 -1260 {lab=vct}
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
N 420 -1460 880 -1460 {lab=VDD}
N 880 -1460 940 -1460 {lab=VDD}
N 640 -280 700 -280 {lab=VSS}
N 700 -280 1060 -280 {lab=VSS}
N 420 -280 640 -280 {lab=VSS}
N 1060 -280 1120 -280 {lab=VSS}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/iopin.sym} 420 -1460 0 1 {name=p1 lab=VDD}
C {devices/iopin.sym} 420 -280 0 1 {name=p2 lab=VSS}
C {sg13g2_pr/sg13_lv_pmos.sym} 860 -1360 0 0 {name=Mtop
l=0.5u
w=150u
ng=30
m=1
model=sg13_lv_pmos
spiceprefix=X}
C {devices/ipin.sym} 520 -1360 0 0 {name=p3 lab=vbp_core}
C {vco_ind.sym} 800 -1120 0 0 {name=xind}
C {sg13g2_pr/cap_cmim.sym} 1120 -1230 0 0 {name=Cct
w=25e-6
l=25e-6
m=1
model=cap_cmim
spiceprefix=X}
C {devices/lab_pin.sym} 1120 -1200 1 0 {name=l1 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 920 -1100 1 0 {name=l2 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 880 -1260 0 0 {name=l3 sig_type=std_logic lab=vct}
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
