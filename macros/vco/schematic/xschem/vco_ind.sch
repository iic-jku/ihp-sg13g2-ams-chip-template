v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Tank Coil, PDK Device for LVS, Lumped-Element Model for Simulation} 300 -1740 0 0 1 1 {}
T {PDK inductor3 for LVS: 2 turns, w 4 um, s 4 um, d 82 um.
The PDK has no SPICE model for it, so it is skipped
in every simulation netlist (spice_ignore, spectre_ignore).} 480 -1400 0 0 0.3 0.3 {}
T {snp2le model vco_ind_le for simulation, skipped in the LVS netlist
(lvs_ignore=open). A testbench includes netlist/spice/vco_ind_le.spice
(ngspice) or netlist/spectre/vco_ind_le.inc (VACASK). Its substrate
network returns to the global ground, so VSS must be the ground node.} 980 -1400 0 0 0.3 0.3 {}
N 700 -930 700 -1060 {lab=la}
N 480 -1060 700 -1060 {lab=la}
N 700 -1060 1000 -1060 {lab=la}
N 1000 -1060 1000 -920 {lab=la}
N 1000 -920 1040 -920 {lab=la}
N 660 -900 580 -900 {lab=lc}
N 580 -900 580 -1140 {lab=lc}
N 480 -1140 580 -1140 {lab=lc}
N 580 -1140 1140 -1140 {lab=lc}
N 1140 -1140 1140 -980 {lab=lc}
N 700 -870 700 -760 {lab=lb}
N 480 -760 700 -760 {lab=lb}
N 700 -760 1280 -760 {lab=lb}
N 1280 -760 1280 -920 {lab=lb}
N 1280 -920 1240 -920 {lab=lb}
N 730 -870 730 -830 {lab=VSS}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {sg13g2_pr/inductor3.sym} 700 -900 0 0 {name=L1
w=4e-6
s=4e-6
d=82e-6
nr_r=2
m=1
device=inductor3
spiceprefix=X
spice_ignore="tcleval([expr \{$lvs_ignore ? 0 : 1\}])"
spectre_ignore=true}
C {vco_ind_le.sym} 1060 -880 0 0 {name=x1
lvs_ignore=open}
C {devices/iopin.sym} 480 -1060 0 1 {name=p1 lab=la}
C {devices/iopin.sym} 480 -1140 0 1 {name=p2 lab=lc}
C {devices/iopin.sym} 480 -760 0 1 {name=p3 lab=lb}
C {devices/iopin.sym} 730 -830 1 0 {name=p4 lab=VSS}
