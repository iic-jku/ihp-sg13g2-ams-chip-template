v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {20 GHz LC VCO, Post-Layout} 300 -1740 0 0 1 1 {}
T {vco_top as KPEX extracts it without the coil and the varactor array (full RC, make klayout-pex-leads),
with the coil's EM model and the array's schematic where they connect, for vco_top_tb_tran_lpe.
The extraction has a port at each of their pins: vco_ind_LA, LB and LC at the coil's feeds, so rf_p and rf_n
are the tank at the feeds, vco_var_rf_p and rf_n at the middle of the array's buses. The testbench includes the netlists.} 300 -1560 0 0 0.4 0.4 {}
C {title-3.sym} 0 0 0 0 {name=l0 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/iopin.sym} 400 -1300 0 1 {name=p1 lab=VDD}
C {devices/iopin.sym} 400 -1260 0 1 {name=p2 lab=VSS}
C {devices/iopin.sym} 400 -1220 0 1 {name=p3 lab=vdd_core}
C {devices/ipin.sym} 400 -1180 0 0 {name=p4 lab=ibias_100u}
C {devices/ipin.sym} 400 -1140 0 0 {name=p5 lab=di_en}
C {devices/ipin.sym} 400 -1100 0 0 {name=p6 lab=vtune}
C {devices/iopin.sym} 400 -1060 0 1 {name=p7 lab=rf_out_p}
C {devices/iopin.sym} 400 -1020 0 1 {name=p8 lab=rf_out_n}
C {vco_top_leads.sym} 1000 -600 0 0 {name=xleads}
C {devices/lab_pin.sym} 980 -900 0 0 {name=l1 sig_type=std_logic lab=ibias_100u}
C {devices/lab_pin.sym} 980 -860 0 0 {name=l2 sig_type=std_logic lab=di_en}
C {devices/lab_pin.sym} 980 -800 0 0 {name=l3 sig_type=std_logic lab=vtune}
C {devices/lab_pin.sym} 980 -760 0 0 {name=l4 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 980 -720 0 0 {name=l5 sig_type=std_logic lab=vdd_core}
C {devices/lab_pin.sym} 980 -680 0 0 {name=l6 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1300 -900 0 1 {name=l7 sig_type=std_logic lab=rf_out_p}
C {devices/lab_pin.sym} 1300 -860 0 1 {name=l8 sig_type=std_logic lab=rf_out_n}
C {devices/lab_pin.sym} 1300 -800 0 1 {name=l9 sig_type=std_logic lab=rf_p}
C {devices/lab_pin.sym} 1300 -760 0 1 {name=l10 sig_type=std_logic lab=rf_n}
C {devices/lab_pin.sym} 1300 -720 0 1 {name=l11 sig_type=std_logic lab=vco_ind_LC}
C {devices/lab_pin.sym} 1300 -680 0 1 {name=l12 sig_type=std_logic lab=vco_var_rf_p}
C {devices/lab_pin.sym} 1300 -640 0 1 {name=l13 sig_type=std_logic lab=vco_var_rf_n}
C {devices/lab_pin.sym} 1140 -580 1 0 {name=l14 sig_type=std_logic lab=vco_var_VSS}
C {vco_ind_le.sym} 1600 -1000 0 0 {name=xind}
C {devices/lab_pin.sym} 1580 -1040 0 0 {name=l15 sig_type=std_logic lab=rf_p}
C {devices/lab_pin.sym} 1780 -1040 0 1 {name=l16 sig_type=std_logic lab=rf_n}
C {devices/lab_pin.sym} 1680 -1100 3 0 {name=l17 sig_type=std_logic lab=vco_ind_LC}
C {vco_var.sym} 1600 -600 0 0 {name=xvar}
C {devices/lab_pin.sym} 1580 -640 0 0 {name=l18 sig_type=std_logic lab=vco_var_rf_p}
C {devices/lab_pin.sym} 1780 -640 0 1 {name=l19 sig_type=std_logic lab=vco_var_rf_n}
C {devices/lab_pin.sym} 1680 -700 3 0 {name=l20 sig_type=std_logic lab=vtune}
C {devices/lab_pin.sym} 1720 -580 1 0 {name=l21 sig_type=std_logic lab=vco_var_VSS}
