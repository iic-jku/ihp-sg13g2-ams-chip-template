v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Inverter with Dummies and with LV Transistors} 610 -1700 0 0 1 1 {}
N 1140 -850 1140 -790 {
lab=vin}
N 1100 -850 1140 -850 {
lab=vin}
N 1140 -910 1140 -850 {
lab=vin}
N 1220 -1100 1220 -1060 {lab=VDD}
N 1220 -1140 1220 -1100 {lab=VDD}
N 1220 -640 1220 -600 {lab=VSS}
N 1220 -600 1220 -560 {lab=VSS}
N 1140 -790 1180 -790 {lab=vin}
N 1140 -910 1180 -910 {lab=vin}
N 1220 -1000 1220 -970 {lab=VDD}
N 1220 -970 1220 -940 {lab=VDD}
N 1220 -850 1220 -820 {lab=vout}
N 1220 -760 1220 -730 {lab=VSS}
N 1220 -730 1220 -700 {lab=VSS}
N 1140 -1030 1180 -1030 {lab=VDD}
N 1140 -1100 1140 -1030 {lab=VDD}
N 1140 -1100 1220 -1100 {lab=VDD}
N 1140 -670 1180 -670 {lab=VSS}
N 1140 -670 1140 -600 {lab=VSS}
N 1140 -600 1220 -600 {lab=VSS}
N 1140 -970 1220 -970 {lab=VDD}
N 1140 -1030 1140 -970 {lab=VDD}
N 1140 -730 1220 -730 {lab=VSS}
N 1140 -730 1140 -670 {lab=VSS}
N 1220 -1030 1320 -1030 {lab=VDD}
N 1220 -910 1320 -910 {lab=VDD}
N 1220 -790 1320 -790 {lab=VSS}
N 1220 -670 1320 -670 {lab=VSS}
N 1220 -850 1360 -850 {
lab=vout}
N 1220 -880 1220 -850 {lab=vout}
N 1320 -1030 1320 -910 {lab=VDD}
N 1320 -790 1320 -670 {lab=VSS}
N 1320 -670 1320 -560 {lab=VSS}
N 1320 -1140 1320 -1030 {lab=VDD}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/ipin.sym} 1100 -850 0 0 {name=p10 lab=vin}
C {devices/iopin.sym} 1220 -1140 3 0 {name=p11 lab=VDD}
C {devices/iopin.sym} 1220 -560 1 0 {name=p1 lab=VSS}
C {sg13_lv_nmos.sym} 1200 -670 0 0 {name=Mdummy1
l=1.0u
w=2.0u
ng=2
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13_lv_pmos.sym} 1200 -1030 0 0 {name=Mdummy2
l=1.0u
w=12.0u
ng=2
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13_lv_nmos.sym} 1200 -790 0 0 {name=M1
l=1.0u
w=20.0u
ng=20
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13_lv_pmos.sym} 1200 -910 0 0 {name=M2
l=1.0u
w=120.0u
ng=20
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {annotate_fet_params.sym} 1520 -740 0 0 {name=annot1 ref=M1}
C {annotate_fet_params.sym} 1520 -1020 0 0 {name=annot2 ref=M2}
C {devices/iopin.sym} 1360 -850 0 0 {name=p6 lab=vout}
C {lab_pin.sym} 1320 -1140 1 0 {name=p16 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1320 -560 3 0 {name=p17 sig_type=std_logic lab=VSS}
