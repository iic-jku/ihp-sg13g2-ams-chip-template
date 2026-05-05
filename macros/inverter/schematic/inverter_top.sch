v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Quad Inverter (Top-Level)} 830 -1700 0 0 1 1 {}
N 1160 -520 1160 -500 {lab=VDD}
N 1160 -420 1160 -400 {lab=VSS}
N 1180 -520 1180 -480 {lab=nwell1}
N 1180 -440 1180 -400 {lab=psub}
N 1160 -800 1160 -780 {lab=VDD}
N 1160 -700 1160 -680 {lab=VSS}
N 1180 -800 1180 -760 {lab=nwell1}
N 1180 -720 1180 -680 {lab=psub}
N 1160 -1080 1160 -1060 {lab=VDD}
N 1160 -980 1160 -960 {lab=VSS}
N 1180 -1080 1180 -1040 {lab=nwell2}
N 1180 -1000 1180 -960 {lab=psub}
N 1160 -1360 1160 -1340 {lab=VDD}
N 1160 -1260 1160 -1240 {lab=VSS}
N 1180 -1360 1180 -1320 {lab=nwell2}
N 1180 -1280 1180 -1240 {lab=psub}
N 1040 -1020 1100 -1020 {lab=vin3}
N 1040 -1300 1100 -1300 {lab=vin4}
N 1240 -1300 1300 -1300 {lab=vout4}
N 1240 -1020 1300 -1020 {lab=vout3}
N 1240 -740 1300 -740 {lab=vout2}
N 1040 -740 1100 -740 {lab=vin2}
N 1040 -460 1100 -460 {lab=vin1}
N 1240 -460 1300 -460 {lab=vout1}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/ipin.sym} 1040 -1300 0 0 {name=p10 lab=vin4}
C {devices/iopin.sym} 1160 -1360 3 0 {name=p11 lab=VDD}
C {devices/iopin.sym} 1160 -1240 1 0 {name=p1 lab=VSS}
C {devices/iopin.sym} 1300 -1300 0 0 {name=p6 lab=vout4}
C {devices/ipin.sym} 1040 -1020 0 0 {name=p2 lab=vin3}
C {devices/ipin.sym} 1040 -740 0 0 {name=p3 lab=vin2}
C {devices/ipin.sym} 1040 -460 0 0 {name=p4 lab=vin1}
C {devices/iopin.sym} 1300 -1020 0 0 {name=p7 lab=vout3}
C {devices/iopin.sym} 1300 -740 0 0 {name=p8 lab=vout2}
C {devices/iopin.sym} 1300 -460 0 0 {name=p9 lab=vout1}
C {inverter.sym} 1160 -460 0 0 {name=x1}
C {lab_pin.sym} 1160 -520 1 0 {name=p12 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -400 3 0 {name=p13 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1180 -400 3 0 {name=p14 sig_type=std_logic lab=psub}
C {lab_pin.sym} 1180 -520 3 1 {name=p15 sig_type=std_logic lab=nwell1}
C {inverter.sym} 1160 -740 0 0 {name=x2}
C {lab_pin.sym} 1160 -800 1 0 {name=p16 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -680 3 0 {name=p17 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1180 -680 3 0 {name=p18 sig_type=std_logic lab=psub}
C {lab_pin.sym} 1180 -800 3 1 {name=p19 sig_type=std_logic lab=nwell1}
C {inverter.sym} 1160 -1020 0 0 {name=x3}
C {lab_pin.sym} 1160 -1080 1 0 {name=p20 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -960 3 0 {name=p21 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1180 -960 3 0 {name=p22 sig_type=std_logic lab=psub}
C {lab_pin.sym} 1180 -1080 3 1 {name=p23 sig_type=std_logic lab=nwell2}
C {inverter.sym} 1160 -1300 0 0 {name=x4}
C {lab_pin.sym} 1180 -1240 3 0 {name=p26 sig_type=std_logic lab=psub}
C {lab_pin.sym} 1180 -1360 3 1 {name=p27 sig_type=std_logic lab=nwell2}
