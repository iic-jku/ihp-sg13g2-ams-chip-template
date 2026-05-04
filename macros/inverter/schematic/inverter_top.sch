v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Due to the mobility difference between holes and electrons, the size of PMOS is 2-3 times larger than that of NMOS for an inverter.
The sizing, however, depends very much on the application. If we don't care about the output rising time, we could just simply make (W/L)p=(W/L)n.

The following three cases are the most relevant:
1. (W/L)p=(W/L)n
2. (W/L)p=2(W/L)n
3. (W/L)p=3(W/L)n
Compare the propagation delay in these cases.} 240 -1410 0 0 0.5 0.5 {}
T {Inverter with Dummies and with LV Transistors} 610 -1700 0 0 1 1 {}
N 1120 -700 1120 -640 {
lab=vin}
N 1080 -700 1120 -700 {
lab=vin}
N 1120 -760 1120 -700 {
lab=vin}
N 1200 -700 1200 -670 {
lab=vout}
N 1200 -950 1200 -910 {lab=VDD}
N 1200 -990 1200 -950 {lab=VDD}
N 1200 -490 1200 -450 {lab=VSS}
N 1200 -450 1200 -410 {lab=VSS}
N 1120 -640 1160 -640 {lab=vin}
N 1120 -760 1160 -760 {lab=vin}
N 1200 -820 1200 -790 {lab=VDD}
N 1200 -580 1200 -550 {lab=VSS}
N 1200 -850 1200 -820 {lab=VDD}
N 1200 -610 1200 -580 {lab=VSS}
N 1120 -880 1160 -880 {lab=VDD}
N 1120 -950 1120 -880 {lab=VDD}
N 1120 -950 1200 -950 {lab=VDD}
N 1120 -520 1160 -520 {lab=VSS}
N 1120 -520 1120 -450 {lab=VSS}
N 1120 -450 1200 -450 {lab=VSS}
N 1120 -820 1200 -820 {lab=VDD}
N 1120 -880 1120 -820 {lab=VDD}
N 1120 -580 1200 -580 {lab=VSS}
N 1120 -580 1120 -520 {lab=VSS}
N 1200 -880 1300 -880 {lab=#net1}
N 1200 -760 1300 -760 {lab=#net1}
N 1300 -820 1300 -760 {lab=#net1}
N 1300 -900 1300 -880 {lab=#net1}
N 1300 -990 1300 -960 {lab=VDD}
N 1200 -640 1300 -640 {lab=#net2}
N 1200 -520 1300 -520 {lab=#net2}
N 1300 -580 1300 -520 {lab=#net2}
N 1300 -520 1300 -500 {lab=#net2}
N 1300 -440 1300 -410 {lab=VSS}
N 1200 -700 1340 -700 {
lab=vout}
N 1300 -820 1340 -820 {lab=nwell}
N 1300 -580 1340 -580 {lab=psub}
N 1200 -730 1200 -700 {
lab=vout}
N 1300 -880 1300 -820 {lab=#net1}
N 1300 -640 1300 -580 {lab=#net2}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/ipin.sym} 1080 -700 0 0 {name=p3 lab=vin}
C {devices/iopin.sym} 1200 -990 3 0 {name=p4 lab=VDD}
C {devices/iopin.sym} 1200 -410 1 0 {name=p5 lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 1180 -640 0 0 {name=M1
l=0.13u
w=54.0u
ng=54
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1180 -760 0 0 {name=M2
l=0.13u
w=162.0u
ng=54
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1180 -520 0 0 {name=Mdummy1
l=0.13u
w=2.0u
ng=2
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1180 -880 0 0 {name=Mdummy2
l=0.13u
w=6.0u
ng=2
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/ntap1_ring.sym} 1300 -930 0 0 {name=R1
model=ntap1
spiceprefix=X
w=30.88e-6
l=5.02e-6
rw=0.3e-6
lvs_ignore=short}
C {lab_pin.sym} 1300 -990 1 0 {name=p11 sig_type=std_logic lab=VDD}
C {sg13g2_pr/ptap1_ring.sym} 1300 -470 2 1 {name=R2
model=ptap1
spiceprefix=X
w=30.88e-6
l=3.38e-6
rw=0.3e-6
lvs_ignore=short}
C {lab_pin.sym} 1300 -410 3 0 {name=p12 sig_type=std_logic lab=VSS}
C {devices/iopin.sym} 1340 -700 0 0 {name=p6 lab=vout}
C {devices/iopin.sym} 1340 -820 0 0 {name=p1 lab=nwell}
C {devices/iopin.sym} 1340 -580 0 0 {name=p2 lab=psub}
