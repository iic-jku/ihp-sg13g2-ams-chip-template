v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {VCO Core, Leads Extracted} 300 -1340 0 0 1 1 {}
T {xleads is the KPEX netlist (full RC) of vco_core without its subcells: the pair,
Cct1, Cct2 and every lead, written by make klayout-pex-leads CELL=vco_core.
The varactor array is its schematic (neither Magic nor KPEX extracts sg13_hv_svaricap),
the coil its EM model, as in vco_core.} 300 -1220 0 0 0.3 0.3 {}
N 300 -1000 380 -1000 {lab=vdd_core}
N 300 -940 380 -940 {lab=VSS}
N 300 -880 380 -880 {lab=vtune}
N 300 -820 380 -820 {lab=rf_p}
N 300 -760 380 -760 {lab=rf_n}
C {title-3.sym} 0 0 0 0 {name=l0 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/iopin.sym} 300 -1000 0 1 {name=p1 lab=vdd_core}
C {devices/iopin.sym} 300 -940 0 1 {name=p2 lab=VSS}
C {devices/ipin.sym} 300 -880 0 0 {name=p3 lab=vtune}
C {devices/iopin.sym} 300 -820 0 1 {name=p4 lab=rf_p}
C {devices/iopin.sym} 300 -760 0 1 {name=p5 lab=rf_n}
C {vco_core_leads.sym} 600 -600 0 0 {name=xleads}
C {vco_ind.sym} 1100 -800 0 0 {name=xind}
C {vco_var.sym} 1100 -500 0 0 {name=xvar}
C {devices/lab_pin.sym} 380 -1000 0 1 {name=l1 sig_type=std_logic lab=vdd_core}
C {devices/lab_pin.sym} 380 -940 0 1 {name=l2 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 380 -880 0 1 {name=l3 sig_type=std_logic lab=vtune}
C {devices/lab_pin.sym} 380 -820 0 1 {name=l4 sig_type=std_logic lab=rf_p}
C {devices/lab_pin.sym} 380 -760 0 1 {name=l5 sig_type=std_logic lab=rf_n}
C {devices/lab_pin.sym} 740 -780 3 0 {name=l6 sig_type=std_logic lab=vdd_core}
C {devices/lab_pin.sym} 740 -580 1 0 {name=l7 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 580 -680 0 0 {name=l8 sig_type=std_logic lab=vtune}
C {devices/lab_pin.sym} 820 -700 0 1 {name=l9 sig_type=std_logic lab=rf_p}
C {devices/lab_pin.sym} 820 -660 0 1 {name=l10 sig_type=std_logic lab=rf_n}
C {devices/lab_pin.sym} 1080 -840 0 0 {name=l11 sig_type=std_logic lab=rf_p}
C {devices/lab_pin.sym} 1280 -840 0 1 {name=l12 sig_type=std_logic lab=rf_n}
C {devices/lab_pin.sym} 1180 -900 3 0 {name=l13 sig_type=std_logic lab=vdd_core}
C {devices/lab_pin.sym} 1220 -780 1 0 {name=l14 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1080 -540 0 0 {name=l15 sig_type=std_logic lab=rf_p}
C {devices/lab_pin.sym} 1280 -540 0 1 {name=l16 sig_type=std_logic lab=rf_n}
C {devices/lab_pin.sym} 1180 -600 3 0 {name=l17 sig_type=std_logic lab=vtune}
C {devices/lab_pin.sym} 1220 -480 1 0 {name=l18 sig_type=std_logic lab=VSS}
