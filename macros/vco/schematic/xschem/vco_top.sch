v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {20 GHz LC VCO, CMOS Only} 300 -1740 0 0 1 1 {}
T {VDD 1.5 V: 6.0 mA (buffer tail 5.8 mA, bias 0.2 mA). vdd_core 0.72 V from its own pad: 4.05 mA.
ibias_100u: 100 uA into the macro. di_en: 1 enables, 0 turns the buffer and bias currents off.
vtune: 0 V to VDD. rf_out_p/rf_out_n: 50 Ohm back-terminated, AC-couple the load.} 560 -1500 0 0 0.4 0.4 {}
N 600 -1380 680 -1380 {lab=VDD}
N 600 -1320 680 -1320 {lab=VSS}
N 600 -1260 680 -1260 {lab=vdd_core}
N 840 -1220 840 -1180 {lab=ibias_100u}
N 900 -1220 900 -1180 {lab=di_en}
N 1020 -1080 1800 -1080 {lab=vbn_buf}
N 1800 -1080 1800 -740 {lab=vbn_buf}
N 1020 -1120 1860 -1120 {lab=vbg_buf}
N 1860 -1120 1860 -740 {lab=vbg_buf}
N 1460 -660 1700 -660 {lab=rf_p}
N 1460 -620 1700 -620 {lab=rf_n}
N 1140 -640 1220 -640 {lab=vtune}
N 1980 -660 2060 -660 {lab=rf_out_p}
N 1980 -620 2060 -620 {lab=rf_out_n}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {vco_bias.sym} 760 -1000 0 0 {name=xbias}
C {vco_core.sym} 1240 -560 0 0 {name=xcore}
C {vco_buf.sym} 1720 -560 0 0 {name=xbuf}
C {devices/lab_pin.sym} 960 -1180 3 0 {name=l1 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 960 -980 1 0 {name=l2 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1380 -740 3 0 {name=l3 sig_type=std_logic lab=vdd_core}
C {devices/lab_pin.sym} 1380 -540 1 0 {name=l4 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1920 -740 3 0 {name=l5 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 1920 -540 1 0 {name=l6 sig_type=std_logic lab=VSS}
C {devices/iopin.sym} 600 -1380 0 1 {name=p1 lab=VDD}
C {devices/lab_pin.sym} 680 -1380 0 1 {name=l7 sig_type=std_logic lab=VDD}
C {devices/iopin.sym} 600 -1320 0 1 {name=p2 lab=VSS}
C {devices/lab_pin.sym} 680 -1320 0 1 {name=l8 sig_type=std_logic lab=VSS}
C {devices/iopin.sym} 600 -1260 0 1 {name=p8 lab=vdd_core}
C {devices/lab_pin.sym} 680 -1260 0 1 {name=l14 sig_type=std_logic lab=vdd_core}
C {devices/ipin.sym} 840 -1220 1 0 {name=p3 lab=ibias_100u}
C {devices/ipin.sym} 900 -1220 1 0 {name=p4 lab=di_en}
C {devices/lab_wire.sym} 1800 -1080 0 0 {name=l10 sig_type=std_logic lab=vbn_buf}
C {devices/lab_wire.sym} 1860 -1120 0 0 {name=l11 sig_type=std_logic lab=vbg_buf}
C {devices/lab_wire.sym} 1580 -660 0 0 {name=l12 sig_type=std_logic lab=rf_p}
C {devices/lab_wire.sym} 1580 -620 0 0 {name=l13 sig_type=std_logic lab=rf_n}
C {devices/ipin.sym} 1140 -640 0 0 {name=p5 lab=vtune}
C {devices/iopin.sym} 2060 -660 0 0 {name=p6 lab=rf_out_p}
C {devices/iopin.sym} 2060 -620 0 0 {name=p7 lab=rf_out_n}
