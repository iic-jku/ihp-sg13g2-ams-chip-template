v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 4 200 -1560 2180 -1480 {fill = false}
T {Quad Inverter (Top-Level)} 830 -1700 0 0 1 1 {}
T {Note that the nw and sub nets are using conditional net labels! Adding further labels also needs to have these options set!!!} 210 -1540 0 0 0.6 0.6 {}
N 1160 -480 1160 -460 {lab=VDD}
N 1160 -380 1160 -360 {lab=VSS}
N 1180 -480 1180 -440 {lab=nwell1}
N 1180 -400 1180 -360 {lab=psub}
N 1160 -760 1160 -740 {lab=VDD}
N 1160 -660 1160 -640 {lab=VSS}
N 1180 -760 1180 -720 {lab=nwell1}
N 1180 -680 1180 -640 {lab=psub}
N 1160 -1040 1160 -1020 {lab=VDD}
N 1160 -940 1160 -920 {lab=VSS}
N 1180 -1040 1180 -1000 {lab=nwell2}
N 1180 -960 1180 -920 {lab=psub}
N 1160 -1320 1160 -1300 {lab=VDD}
N 1160 -1220 1160 -1200 {lab=VSS}
N 1180 -1320 1180 -1280 {lab=nwell2}
N 1180 -1240 1180 -1200 {lab=psub}
N 1040 -980 1100 -980 {lab=vin3}
N 1040 -1260 1100 -1260 {lab=vin4}
N 1240 -1260 1300 -1260 {lab=vout4}
N 1240 -980 1300 -980 {lab=vout3}
N 1240 -700 1300 -700 {lab=vout2}
N 1040 -700 1100 -700 {lab=vin2}
N 1040 -420 1100 -420 {lab=vin1}
N 1240 -420 1300 -420 {lab=vout1}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/ipin.sym} 1040 -1260 0 0 {name=p10 lab=vin4}
C {devices/iopin.sym} 1160 -1320 3 0 {name=p11 lab=VDD}
C {devices/iopin.sym} 1160 -1200 1 0 {name=p1 lab=VSS}
C {devices/iopin.sym} 1300 -1260 0 0 {name=p6 lab=vout4}
C {devices/ipin.sym} 1040 -980 0 0 {name=p2 lab=vin3}
C {devices/ipin.sym} 1040 -700 0 0 {name=p3 lab=vin2}
C {devices/ipin.sym} 1040 -420 0 0 {name=p4 lab=vin1}
C {devices/iopin.sym} 1300 -980 0 0 {name=p7 lab=vout3}
C {devices/iopin.sym} 1300 -700 0 0 {name=p8 lab=vout2}
C {devices/iopin.sym} 1300 -420 0 0 {name=p9 lab=vout1}
C {inverter.sym} 1160 -420 0 0 {name=x1}
C {lab_pin.sym} 1160 -480 1 0 {name=p12 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -360 3 0 {name=p13 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1180 -360 3 0 {name=p14 sig_type=std_logic lab="tcleval([expr \{$lvs_ignore ? \{VSS\} : \{psub\}\}])"}
C {lab_pin.sym} 1180 -480 3 1 {name=p15 sig_type=std_logic lab="tcleval([expr \{$lvs_ignore ? \{VDD\} : \{nwell1\}\}])"}
C {inverter.sym} 1160 -700 0 0 {name=x2}
C {lab_pin.sym} 1160 -760 1 0 {name=p16 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -640 3 0 {name=p17 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1180 -640 3 0 {name=p18 sig_type=std_logic lab="tcleval([expr \{$lvs_ignore ? \{VSS\} : \{psub\}\}])"}
C {lab_pin.sym} 1180 -760 3 1 {name=p19 sig_type=std_logic lab="tcleval([expr \{$lvs_ignore ? \{VDD\} : \{nwell1\}\}])"}
C {inverter.sym} 1160 -980 0 0 {name=x3}
C {lab_pin.sym} 1160 -1040 1 0 {name=p20 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -920 3 0 {name=p21 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1180 -920 3 0 {name=p22 sig_type=std_logic lab="tcleval([expr \{$lvs_ignore ? \{VSS\} : \{psub\}\}])"}
C {lab_pin.sym} 1180 -1040 3 1 {name=p23 sig_type=std_logic lab="tcleval([expr \{$lvs_ignore ? \{VDD\} : \{nwell2\}\}])"}
C {inverter.sym} 1160 -1260 0 0 {name=x4}
C {lab_pin.sym} 1180 -1200 3 0 {name=p26 sig_type=std_logic lab="tcleval([expr \{$lvs_ignore ? \{VSS\} : \{psub\}\}])"}
C {lab_pin.sym} 1180 -1320 3 1 {name=p27 sig_type=std_logic lab="tcleval([expr \{$lvs_ignore ? \{VDD\} : \{nwell2\}\}])"}
