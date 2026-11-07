v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {VCO Center Tap Feed} 300 -1740 0 0 1 1 {}
T {Rct feeds the coil's center tap from VDD, so the tap finds its own voltage: a slow corner draws less
current and the tap rises, a fast corner the other way round. No reference and no regulator.
MPs stops the core when en_b is high. Its on-resistance is part of the feed.} 300 -1560 0 0 0.4 0.4 {}
N 820 -1020 820 -960 {lab=VDD}
N 820 -960 820 -930 {lab=VDD}
N 820 -960 880 -960 {lab=VDD}
N 880 -960 880 -900 {lab=VDD}
N 820 -900 880 -900 {lab=VDD}
N 720 -900 780 -900 {lab=en_b}
N 820 -870 820 -810 {lab=n1}
N 820 -750 820 -680 {lab=vdd_core}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/iopin.sym} 820 -1020 3 0 {name=p1 lab=VDD}
C {devices/iopin.sym} 520 -1020 0 1 {name=p2 lab=VSS}
C {devices/ipin.sym} 720 -900 0 0 {name=p3 lab=en_b}
C {devices/iopin.sym} 820 -680 1 0 {name=p4 lab=vdd_core}
C {devices/lab_wire.sym} 820 -840 0 0 {name=l2 sig_type=std_logic lab=n1}
C {sg13g2_pr/sg13_lv_pmos.sym} 800 -900 0 0 {name=MPs
l=0.13u
w=96u
ng=32
m=1
model=sg13_lv_pmos
spiceprefix=X}
C {sg13g2_pr/rppd.sym} 820 -780 0 0 {name=Rct
w=17.3e-6
l=8.8e-6
m=1
b=0
model=rppd
body=VSS
spiceprefix=X}
