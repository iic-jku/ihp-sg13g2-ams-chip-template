v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {VCO Output Buffer, AC-Coupled Differential Pair with 50 Ohm Loads} 300 -1740 0 0 1 1 {}
T {Cc and Rb couple the tank AC only, so the pair biases at vbg_buf
whatever the tank common mode. RL back-terminates each output
for a 50 Ohm load, the load has to be AC-coupled.
MB1 inverts rf_p into rf_out_n. Tail current 6 mA.} 1780 -1440 0 0 0.3 0.3 {}
N 1180 -1460 1680 -1460 {lab=VDD}
N 1100 -280 1680 -280 {lab=VSS}
N 900 -1460 900 -1130 {lab=VDD}
N 1180 -1460 1180 -1130 {lab=VDD}
N 900 -1070 900 -960 {lab=rf_out_n}
N 900 -960 900 -790 {lab=rf_out_n}
N 1180 -1070 1180 -960 {lab=rf_out_p}
N 1180 -960 1180 -790 {lab=rf_out_p}
N 840 -960 900 -960 {lab=rf_out_n}
N 1180 -960 1240 -960 {lab=rf_out_p}
N 900 -730 900 -620 {lab=tail}
N 900 -620 1040 -620 {lab=tail}
N 1180 -730 1180 -620 {lab=tail}
N 1040 -620 1180 -620 {lab=tail}
N 1040 -620 1040 -490 {lab=tail}
N 1040 -430 1040 -280 {lab=VSS}
N 1040 -460 1100 -460 {lab=VSS}
N 1100 -460 1100 -280 {lab=VSS}
N 520 -460 1000 -460 {lab=vbn_buf}
N 900 -760 940 -760 {lab=VSS}
N 940 -760 940 -680 {lab=VSS}
N 1140 -760 1180 -760 {lab=VSS}
N 1140 -760 1140 -680 {lab=VSS}
N 650 -760 700 -760 {lab=gp}
N 700 -760 860 -760 {lab=gp}
N 700 -850 700 -760 {lab=gp}
N 1380 -760 1430 -760 {lab=gn}
N 1220 -760 1380 -760 {lab=gn}
N 1380 -850 1380 -760 {lab=gn}
N 520 -760 590 -760 {lab=rf_p}
N 1490 -760 1580 -760 {lab=rf_n}
N 700 -1260 700 -910 {lab=vbg_buf}
N 520 -1260 700 -1260 {lab=vbg_buf}
N 700 -1260 1380 -1260 {lab=vbg_buf}
N 1380 -1260 1380 -910 {lab=vbg_buf}
N 420 -1460 900 -1460 {lab=VDD}
N 900 -1460 1180 -1460 {lab=VDD}
N 420 -280 1040 -280 {lab=VSS}
N 1040 -280 1100 -280 {lab=VSS}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/iopin.sym} 420 -1460 0 1 {name=p1 lab=VDD}
C {devices/iopin.sym} 420 -280 0 1 {name=p2 lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 880 -760 0 0 {name=MB1
l=0.13u
w=24u
ng=12
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {sg13g2_pr/sg13_lv_nmos.sym} 1200 -760 0 1 {name=MB2
l=0.13u
w=24u
ng=12
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {sg13g2_pr/rppd.sym} 900 -1100 0 0 {name=RL1
w=10e-6
l=1.65e-6
m=1
b=0
model=rppd
body=VSS
spiceprefix=X}
C {sg13g2_pr/rppd.sym} 1180 -1100 0 0 {name=RL2
w=10e-6
l=1.65e-6
m=1
b=0
model=rppd
body=VSS
spiceprefix=X}
C {devices/iopin.sym} 840 -960 0 1 {name=p3 lab=rf_out_n}
C {devices/iopin.sym} 1240 -960 0 0 {name=p4 lab=rf_out_p}
C {sg13g2_pr/sg13_lv_nmos.sym} 1020 -460 0 0 {name=MBt
l=0.5u
w=150u
ng=60
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {devices/ipin.sym} 520 -460 0 0 {name=p5 lab=vbn_buf}
C {devices/lab_pin.sym} 940 -680 1 0 {name=l1 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1140 -680 1 0 {name=l2 sig_type=std_logic lab=VSS}
C {sg13g2_pr/cap_cmim.sym} 620 -760 1 0 {name=Cc1
w=10e-6
l=10e-6
m=1
model=cap_cmim
spiceprefix=X}
C {sg13g2_pr/cap_cmim.sym} 1460 -760 3 0 {name=Cc2
w=10e-6
l=10e-6
m=1
model=cap_cmim
spiceprefix=X}
C {sg13g2_pr/rhigh.sym} 700 -880 0 0 {name=Rb1
w=0.5e-6
l=8e-6
m=1
b=0
model=rhigh
body=VSS
spiceprefix=X}
C {sg13g2_pr/rhigh.sym} 1380 -880 0 0 {name=Rb2
w=0.5e-6
l=8e-6
m=1
b=0
model=rhigh
body=VSS
spiceprefix=X}
C {devices/iopin.sym} 520 -760 0 1 {name=p6 lab=rf_p}
C {devices/iopin.sym} 1580 -760 0 0 {name=p7 lab=rf_n}
C {devices/lab_wire.sym} 700 -760 0 0 {name=l3 sig_type=std_logic lab=gp}
C {devices/lab_wire.sym} 1380 -760 0 0 {name=l4 sig_type=std_logic lab=gn}
C {devices/lab_wire.sym} 1040 -620 0 0 {name=l5 sig_type=std_logic lab=tail}
C {devices/ipin.sym} 520 -1260 0 0 {name=p8 lab=vbg_buf}
