v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {VCO Varactor Array} 300 -1740 0 0 1 1 {}
T {Three sg13_hv_svaricap with Nx=8 each, gates on the tank, wells on vtune.
Differential C 31 fF to 21 fF per varactor from vtune 0 V to 1.5 V,
Q about 25 at 20 GHz. Their substrate (body=VSS) is the VSS port.} 480 -1300 0 0 0.3 0.3 {}
N 740 -1040 600 -1040 {lab=rf_p}
N 820 -1040 960 -1040 {lab=rf_n}
N 780 -1070 780 -1130 {lab=vtune}
N 740 -880 600 -880 {lab=rf_p}
N 820 -880 960 -880 {lab=rf_n}
N 740 -720 600 -720 {lab=rf_p}
N 820 -720 960 -720 {lab=rf_n}
N 600 -1040 600 -880 {lab=rf_p}
N 600 -880 600 -720 {lab=rf_p}
N 960 -1040 960 -880 {lab=rf_n}
N 960 -880 960 -720 {lab=rf_n}
N 600 -880 480 -880 {lab=rf_p}
N 960 -880 1080 -880 {lab=rf_n}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {sg13g2_pr/sg13_svaricap.sym} 780 -1040 0 0 {name=Cvar1
w=3.74u
l=0.3u
Nx=8
model=sg13_hv_svaricap
body=VSS
spiceprefix=X}
C {devices/ipin.sym} 780 -1130 1 0 {name=p1 lab=vtune}
C {sg13g2_pr/sg13_svaricap.sym} 780 -880 0 0 {name=Cvar2
w=3.74u
l=0.3u
Nx=8
model=sg13_hv_svaricap
body=VSS
spiceprefix=X}
C {devices/lab_pin.sym} 780 -910 3 0 {name=l1 sig_type=std_logic lab=vtune}
C {sg13g2_pr/sg13_svaricap.sym} 780 -720 0 0 {name=Cvar3
w=3.74u
l=0.3u
Nx=8
model=sg13_hv_svaricap
body=VSS
spiceprefix=X}
C {devices/lab_pin.sym} 780 -750 3 0 {name=l2 sig_type=std_logic lab=vtune}
C {devices/iopin.sym} 480 -880 0 1 {name=p2 lab=rf_p}
C {devices/iopin.sym} 1080 -880 0 0 {name=p3 lab=rf_n}
C {devices/iopin.sym} 780 -560 1 0 {name=p4 lab=VSS}
