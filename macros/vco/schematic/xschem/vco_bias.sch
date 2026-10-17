v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {VCO Bias and Enable} 300 -1740 0 0 1 1 {}
T {ibias_100u: 100 uA into the macro. MN1, MP1 and the 30:1 Mtop of the core
set the 3 mA core current, MBt of the buffer mirrors MN0 60:1 for 6 mA.
Rp/Cp and Rn/Cn (48 kOhm, 1.35 pF, 2.5 MHz) filter the reference noise.
di_en low: MNd0 and MNd1 pull the NMOS gates to VSS, MPd the PMOS gate to VDD.} 2500 -1440 0 0 0.3 0.3 {}
N 2280 -1320 2400 -1320 {lab=VDD}
N 2280 -280 2400 -280 {lab=VSS}
N 580 -680 620 -680 {lab=VDD}
N 620 -710 620 -680 {lab=VDD}
N 580 -710 620 -710 {lab=VDD}
N 580 -740 580 -710 {lab=VDD}
N 580 -520 620 -520 {lab=VSS}
N 620 -520 620 -490 {lab=VSS}
N 580 -490 620 -490 {lab=VSS}
N 580 -490 580 -460 {lab=VSS}
N 580 -650 580 -600 {lab=en_b}
N 580 -600 580 -550 {lab=en_b}
N 520 -680 540 -680 {lab=di_en}
N 520 -680 520 -600 {lab=di_en}
N 520 -600 520 -520 {lab=di_en}
N 520 -520 540 -520 {lab=di_en}
N 780 -680 820 -680 {lab=VDD}
N 820 -710 820 -680 {lab=VDD}
N 780 -710 820 -710 {lab=VDD}
N 780 -740 780 -710 {lab=VDD}
N 780 -520 820 -520 {lab=VSS}
N 820 -520 820 -490 {lab=VSS}
N 780 -490 820 -490 {lab=VSS}
N 780 -490 780 -460 {lab=VSS}
N 780 -650 780 -600 {lab=en}
N 780 -600 780 -550 {lab=en}
N 720 -680 740 -680 {lab=en_b}
N 720 -680 720 -600 {lab=en_b}
N 720 -600 720 -520 {lab=en_b}
N 720 -520 740 -520 {lab=en_b}
N 460 -600 520 -600 {lab=di_en}
N 580 -600 640 -600 {lab=en_b}
N 640 -600 720 -600 {lab=en_b}
N 640 -600 640 -440 {lab=en_b}
N 780 -600 860 -600 {lab=en}
N 460 -1180 1000 -1180 {lab=ibias_100u}
N 1000 -470 1000 -280 {lab=VSS}
N 1000 -500 1040 -500 {lab=VSS}
N 1040 -500 1040 -280 {lab=VSS}
N 940 -500 960 -500 {lab=ibias_100u}
N 940 -580 940 -500 {lab=ibias_100u}
N 940 -580 1000 -580 {lab=ibias_100u}
N 1060 -1100 1060 -1050 {lab=ibias_100u}
N 1000 -1100 1060 -1100 {lab=ibias_100u}
N 1020 -1020 1060 -1020 {lab=VSS}
N 1020 -1020 1020 -990 {lab=VSS}
N 1020 -990 1060 -990 {lab=VSS}
N 1060 -990 1060 -960 {lab=VSS}
N 1100 -1020 1140 -1020 {lab=en_b}
N 1000 -760 1090 -760 {lab=ibias_100u}
N 1150 -760 1240 -760 {lab=vbn_buf}
N 1240 -760 1240 -690 {lab=vbn_buf}
N 1240 -760 1360 -760 {lab=vbn_buf}
N 1360 -760 1360 -670 {lab=vbn_buf}
N 1360 -640 1400 -640 {lab=VSS}
N 1400 -640 1400 -610 {lab=VSS}
N 1360 -610 1400 -610 {lab=VSS}
N 1360 -610 1360 -580 {lab=VSS}
N 1300 -640 1320 -640 {lab=en_b}
N 1360 -760 1440 -760 {lab=vbn_buf}
N 1000 -880 1560 -880 {lab=ibias_100u}
N 1000 -1180 1000 -1100 {lab=ibias_100u}
N 1000 -1100 1000 -880 {lab=ibias_100u}
N 1000 -880 1000 -760 {lab=ibias_100u}
N 1000 -760 1000 -580 {lab=ibias_100u}
N 1000 -580 1000 -530 {lab=ibias_100u}
N 1600 -850 1600 -280 {lab=VSS}
N 1600 -880 1640 -880 {lab=VSS}
N 1640 -880 1640 -280 {lab=VSS}
N 1600 -1320 1600 -1230 {lab=VDD}
N 1600 -1200 1640 -1200 {lab=VDD}
N 1640 -1320 1640 -1200 {lab=VDD}
N 1540 -1200 1560 -1200 {lab=vbp_ref}
N 1540 -1200 1540 -1120 {lab=vbp_ref}
N 1540 -1120 1600 -1120 {lab=vbp_ref}
N 1600 -1170 1600 -1120 {lab=vbp_ref}
N 1600 -1120 1600 -1060 {lab=vbp_ref}
N 1600 -1060 1600 -910 {lab=vbp_ref}
N 1600 -1060 1690 -1060 {lab=vbp_ref}
N 1840 -1320 1840 -1180 {lab=VDD}
N 1750 -1060 1840 -1060 {lab=vbp_core}
N 1840 -1120 1840 -1060 {lab=vbp_core}
N 1960 -1320 1960 -1210 {lab=VDD}
N 1960 -1180 2000 -1180 {lab=VDD}
N 2000 -1320 2000 -1180 {lab=VDD}
N 1900 -1180 1920 -1180 {lab=en}
N 1840 -1060 1960 -1060 {lab=vbp_core}
N 1960 -1150 1960 -1060 {lab=vbp_core}
N 1960 -1060 2040 -1060 {lab=vbp_core}
N 2040 -1060 2120 -1060 {lab=vbp_core}
N 2040 -1200 2040 -1060 {lab=vbp_core}
N 2040 -1200 2220 -1200 {lab=vbp_core}
N 2240 -1320 2240 -1230 {lab=VDD}
N 2240 -1200 2280 -1200 {lab=VDD}
N 2280 -1320 2280 -1200 {lab=VDD}
N 2240 -1170 2240 -1080 {lab=vbg_buf}
N 2240 -1080 2240 -1030 {lab=vbg_buf}
N 2240 -970 2240 -840 {lab=nbg}
N 2240 -840 2240 -790 {lab=nbg}
N 2180 -760 2200 -760 {lab=nbg}
N 2180 -840 2180 -760 {lab=nbg}
N 2180 -840 2240 -840 {lab=nbg}
N 2240 -730 2240 -280 {lab=VSS}
N 2240 -760 2280 -760 {lab=VSS}
N 2280 -760 2280 -280 {lab=VSS}
N 2240 -1080 2360 -1080 {lab=vbg_buf}
N 2360 -1080 2360 -1040 {lab=vbg_buf}
N 2360 -1080 2440 -1080 {lab=vbg_buf}
N 420 -280 1000 -280 {lab=VSS}
N 1000 -280 1040 -280 {lab=VSS}
N 1040 -280 1600 -280 {lab=VSS}
N 1600 -280 1640 -280 {lab=VSS}
N 420 -1320 1600 -1320 {lab=VDD}
N 1600 -1320 1640 -1320 {lab=VDD}
N 1640 -1320 1840 -1320 {lab=VDD}
N 1840 -1320 1960 -1320 {lab=VDD}
N 1960 -1320 2000 -1320 {lab=VDD}
N 2000 -1320 2240 -1320 {lab=VDD}
N 2240 -1320 2280 -1320 {lab=VDD}
N 1640 -280 2240 -280 {lab=VSS}
N 2240 -280 2280 -280 {lab=VSS}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/iopin.sym} 420 -1320 0 1 {name=p1 lab=VDD}
C {devices/iopin.sym} 420 -280 0 1 {name=p2 lab=VSS}
C {sg13g2_pr/sg13_lv_pmos.sym} 560 -680 0 0 {name=MPi1
l=0.13u
w=1u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X}
C {sg13g2_pr/sg13_lv_nmos.sym} 560 -520 0 0 {name=MNi1
l=0.13u
w=0.5u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {devices/lab_pin.sym} 580 -740 3 0 {name=l1 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 580 -460 1 0 {name=l2 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_pmos.sym} 760 -680 0 0 {name=MPi2
l=0.13u
w=1u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X}
C {sg13g2_pr/sg13_lv_nmos.sym} 760 -520 0 0 {name=MNi2
l=0.13u
w=0.5u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {devices/lab_pin.sym} 780 -740 3 0 {name=l3 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 780 -460 1 0 {name=l4 sig_type=std_logic lab=VSS}
C {devices/ipin.sym} 460 -600 0 0 {name=p3 lab=di_en}
C {devices/lab_pin.sym} 640 -440 1 0 {name=l5 sig_type=std_logic lab=en_b}
C {devices/lab_pin.sym} 860 -600 0 1 {name=l6 sig_type=std_logic lab=en}
C {devices/ipin.sym} 460 -1180 0 0 {name=p4 lab=ibias_100u}
C {sg13g2_pr/sg13_lv_nmos.sym} 980 -500 0 0 {name=MN0
l=0.5u
w=2.5u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {sg13g2_pr/sg13_lv_nmos.sym} 1080 -1020 0 1 {name=MNd0
l=0.13u
w=1u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {devices/lab_pin.sym} 1060 -960 1 0 {name=l7 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1140 -1020 0 1 {name=l8 sig_type=std_logic lab=en_b}
C {sg13g2_pr/rhigh.sym} 1120 -760 3 0 {name=Rn
w=0.5e-6
l=16e-6
m=1
b=0
model=rhigh
body=VSS
spiceprefix=X}
C {sg13g2_pr/cap_cmim.sym} 1240 -660 0 0 {name=Cn
w=30e-6
l=30e-6
m=1
model=cap_cmim
spiceprefix=X}
C {devices/lab_pin.sym} 1240 -630 1 0 {name=l9 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 1340 -640 0 0 {name=MNd1
l=0.13u
w=1u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {devices/lab_pin.sym} 1360 -580 1 0 {name=l10 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1300 -640 0 0 {name=l11 sig_type=std_logic lab=en_b}
C {devices/iopin.sym} 1440 -760 0 0 {name=p5 lab=vbn_buf}
C {sg13g2_pr/sg13_lv_nmos.sym} 1580 -880 0 0 {name=MN1
l=0.5u
w=2.5u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {sg13g2_pr/sg13_lv_pmos.sym} 1580 -1200 0 0 {name=MP1
l=0.5u
w=5u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X}
C {devices/lab_wire.sym} 1600 -1060 0 0 {name=l12 sig_type=std_logic lab=vbp_ref}
C {sg13g2_pr/rhigh.sym} 1720 -1060 3 0 {name=Rp
w=0.5e-6
l=16e-6
m=1
b=0
model=rhigh
body=VSS
spiceprefix=X}
C {sg13g2_pr/cap_cmim.sym} 1840 -1150 0 0 {name=Cp
w=30e-6
l=30e-6
m=1
model=cap_cmim
spiceprefix=X}
C {sg13g2_pr/sg13_lv_pmos.sym} 1940 -1180 0 0 {name=MPd
l=0.13u
w=1u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X}
C {devices/lab_pin.sym} 1900 -1180 0 0 {name=l13 sig_type=std_logic lab=en}
C {devices/iopin.sym} 2120 -1060 0 0 {name=p6 lab=vbp_core}
C {sg13g2_pr/sg13_lv_pmos.sym} 2220 -1200 0 0 {name=MP2
l=0.5u
w=5u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X}
C {sg13g2_pr/rppd.sym} 2240 -1000 0 0 {name=Rg
w=0.5e-6
l=8.5e-6
m=1
b=0
model=rppd
body=VSS
spiceprefix=X}
C {sg13g2_pr/sg13_lv_nmos.sym} 2220 -760 0 0 {name=MN3
l=0.5u
w=2.5u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X}
C {devices/lab_wire.sym} 2240 -840 0 0 {name=l14 sig_type=std_logic lab=nbg}
C {sg13g2_pr/cap_cmim.sym} 2360 -1010 0 0 {name=Cg
w=20e-6
l=20e-6
m=1
model=cap_cmim
spiceprefix=X}
C {devices/lab_pin.sym} 2360 -980 1 0 {name=l15 sig_type=std_logic lab=VSS}
C {devices/iopin.sym} 2440 -1080 0 0 {name=p7 lab=vbg_buf}
