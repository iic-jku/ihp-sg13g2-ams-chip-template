v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 4 200 -1480 2180 -1400 {fill = false}
T {Inverter with Dummies and with LV Transistors} 610 -1700 0 0 1 1 {}
T {Note that the nw and sub nets are using conditional net labels! Adding further labels also needs to have these options set!!!} 210 -1460 0 0 0.6 0.6 {}
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
N 1220 -1030 1320 -1030 {lab=nwell}
N 1220 -910 1320 -910 {lab=nwell}
N 1320 -970 1320 -910 {lab=nwell}
N 1320 -1050 1320 -1030 {lab=nwell}
N 1320 -1140 1320 -1110 {lab=VDD}
N 1220 -790 1320 -790 {lab=psub}
N 1220 -670 1320 -670 {lab=psub}
N 1320 -730 1320 -670 {lab=psub}
N 1320 -670 1320 -650 {lab=psub}
N 1320 -590 1320 -560 {lab=VSS}
N 1220 -850 1360 -850 {
lab=vout}
N 1320 -970 1360 -970 {lab=nwell}
N 1320 -730 1360 -730 {lab=psub}
N 1220 -880 1220 -850 {lab=vout}
N 1320 -1030 1320 -970 {lab=nwell}
N 1320 -790 1320 -730 {lab=psub}
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
C {ntap1_ring.sym} 1320 -1080 0 0 {name=R1
model=ntap1
spiceprefix=X
w=32.68e-6
l=8.02e-6
rw=0.3e-6
lvs_ignore=short
}
C {lab_pin.sym} 1320 -1140 1 0 {name=p3 sig_type=std_logic lab=VDD}
C {ptap1_ring.sym} 1320 -620 2 1 {name=R2
model=ptap1
spiceprefix=X
w=32.68e-6
l=3.38e-6
rw=0.3e-6
lvs_ignore=short
}
C {lab_pin.sym} 1320 -560 3 0 {name=p12 sig_type=std_logic lab=VSS}
C {devices/iopin.sym} 1360 -850 0 0 {name=p6 lab=vout}
C {devices/iopin.sym} 1360 -970 0 0 {name=p2 lab="tcleval([expr \{$lvs_ignore ? \{VDD\} : \{nwell\}\}])"}
C {devices/iopin.sym} 1360 -730 0 0 {name=p4 lab="tcleval([expr \{$lvs_ignore ? \{VSS\} : \{psub\}\}])"}
