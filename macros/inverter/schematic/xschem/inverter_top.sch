v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Quad Inverter (Top-Level)} 830 -1700 0 0 1 1 {}
N 1160 -560 1160 -540 {lab=VDD}
N 1160 -460 1160 -440 {lab=VSS}
N 1160 -840 1160 -820 {lab=VDD}
N 1160 -740 1160 -720 {lab=VSS}
N 1160 -1120 1160 -1100 {lab=VDD}
N 1160 -1020 1160 -1000 {lab=VSS}
N 1160 -1400 1160 -1380 {lab=VDD}
N 1160 -1300 1160 -1280 {lab=VSS}
N 1040 -1060 1100 -1060 {lab=vin3}
N 1040 -1340 1100 -1340 {lab=vin4}
N 1240 -1340 1300 -1340 {lab=vout4}
N 1240 -1060 1300 -1060 {lab=vout3}
N 1240 -780 1300 -780 {lab=vout2}
N 1040 -780 1100 -780 {lab=vin2}
N 1040 -500 1100 -500 {lab=vin1}
N 1240 -500 1300 -500 {lab=vout1}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/ipin.sym} 1040 -1340 0 0 {name=p10 lab=vin4}
C {devices/iopin.sym} 1160 -1400 3 0 {name=p11 lab=VDD}
C {devices/iopin.sym} 1160 -1280 1 0 {name=p1 lab=VSS}
C {devices/iopin.sym} 1300 -1340 0 0 {name=p6 lab=vout4}
C {devices/ipin.sym} 1040 -1060 0 0 {name=p2 lab=vin3}
C {devices/ipin.sym} 1040 -780 0 0 {name=p3 lab=vin2}
C {devices/ipin.sym} 1040 -500 0 0 {name=p4 lab=vin1}
C {devices/iopin.sym} 1300 -1060 0 0 {name=p7 lab=vout3}
C {devices/iopin.sym} 1300 -780 0 0 {name=p8 lab=vout2}
C {devices/iopin.sym} 1300 -500 0 0 {name=p9 lab=vout1}
C {inverter.sym} 1160 -500 0 0 {name=x1}
C {lab_pin.sym} 1160 -560 1 0 {name=p12 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -440 3 0 {name=p13 sig_type=std_logic lab=VSS}
C {inverter.sym} 1160 -780 0 0 {name=x2}
C {lab_pin.sym} 1160 -840 1 0 {name=p16 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -720 3 0 {name=p17 sig_type=std_logic lab=VSS}
C {inverter.sym} 1160 -1060 0 0 {name=x3}
C {lab_pin.sym} 1160 -1120 1 0 {name=p20 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1160 -1000 3 0 {name=p21 sig_type=std_logic lab=VSS}
C {inverter.sym} 1160 -1340 0 0 {name=x4}
