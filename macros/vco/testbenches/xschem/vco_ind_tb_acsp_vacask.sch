v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Testbench for ACSP analysis - Tank Coil Model vs. EM Data} 450 -1730 0 0 1 1 {}
T {Port 1 at la, port 2 at lb, port 3 at the center tap lc, all 50 Ohm, the order of the EM ports.
plot_vco_ind.py compares the S-parameters with verification/em/s-parameter/vco_ind.s3p.} 600 -1300 0 0 0.3 0.3 {}
N 700 -1110 700 -1070 {lab=p1}
N 700 -1010 700 -970 {lab=a1}
N 700 -910 700 -870 {lab=GND}
N 900 -1110 900 -1070 {lab=p2}
N 900 -1010 900 -970 {lab=a2}
N 900 -910 900 -870 {lab=GND}
N 1100 -1110 1100 -1070 {lab=p3}
N 1100 -1010 1100 -970 {lab=a3}
N 1100 -910 1100 -870 {lab=GND}
N 1340 -940 1380 -940 {lab=p1}
N 1580 -940 1620 -940 {lab=p2}
N 1480 -1040 1480 -1000 {lab=p3}
N 1520 -880 1520 -840 {lab=GND}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {vco_ind.sym} 1400 -900 0 0 {name=x1}
C {devices/lab_pin.sym} 1340 -940 0 0 {name=l2 sig_type=std_logic lab=p1}
C {devices/lab_pin.sym} 1620 -940 0 1 {name=l3 sig_type=std_logic lab=p2}
C {devices/lab_pin.sym} 1480 -1040 3 0 {name=l4 sig_type=std_logic lab=p3}
C {devices/gnd.sym} 1520 -840 0 0 {name=l5 lab=GND}
C {devices/lab_pin.sym} 700 -1110 3 0 {name=l6 sig_type=std_logic lab=p1}
C {devices/res.sym} 700 -1040 0 0 {name=Rp1
value=50
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 700 -990 0 0 {name=l7 sig_type=std_logic lab=a1}
C {devices/vsource.sym} 700 -940 0 0 {name=Vp1 value="dc=0"}
C {devices/gnd.sym} 700 -870 0 0 {name=l8 lab=GND}
C {devices/lab_pin.sym} 900 -1110 3 0 {name=l9 sig_type=std_logic lab=p2}
C {devices/res.sym} 900 -1040 0 0 {name=Rp2
value=50
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 900 -990 0 0 {name=l10 sig_type=std_logic lab=a2}
C {devices/vsource.sym} 900 -940 0 0 {name=Vp2 value="dc=0"}
C {devices/gnd.sym} 900 -870 0 0 {name=l11 lab=GND}
C {devices/lab_pin.sym} 1100 -1110 3 0 {name=l12 sig_type=std_logic lab=p3}
C {devices/res.sym} 1100 -1040 0 0 {name=Rp3
value=50
footprint=1206
device=resistor
m=1}
C {devices/lab_wire.sym} 1100 -990 0 0 {name=l13 sig_type=std_logic lab=a3}
C {devices/vsource.sym} 1100 -940 0 0 {name=Vp3 value="dc=0"}
C {devices/gnd.sym} 1100 -870 0 0 {name=l14 lab=GND}
C {devices/simulator_commands_shown.sym} 60 -1500 0 0 {name=Script_VACASK
simulator=vacask
only_toplevel=false
value="
control
  abort always

  // S-parameters of the coil model. Each port is a source and its series resistor, which sets Z0.
  // The linear sweep starts at DC and steps 0.15 GHz, so every point of the EM grid above 0.75 GHz is on it.
  analysis sp1 acsp ports=[\\"Vp1\\", \\"Rp1\\", \\"Vp2\\", \\"Rp2\\", \\"Vp3\\", \\"Rp3\\"] from=0 to=60G mode=\\"lin\\" points=400

  postprocess(PYTHON, \\"../plot_simulations/vacask2data.py\\", \\"vco_ind_tb_acsp_vacask\\")
endc
"}
C {devices/simulator_commands_shown.sym} 1980 -1330 0 0 {name=Libs_VACASK
simulator=vacask
only_toplevel=false
value="
// devices of the snp2le coil model, see netlist/spectre/vco_ind_le.inc. Xschem declares
// resistor and vsource for the ports, but capacitor only when the schematic has one.
load \\"capacitor.osdi\\"
model capacitor capacitor
load \\"inductor.osdi\\"
model inductor inductor
model mutual mutual
include \\"../../../netlist/spectre/vco_ind_le.inc\\"
"}
C {devices/launcher.sym} 1720 -1330 0 0 {name=h2
descr="Simulate"
tclcommand="set sim(spectre,default) 0; xschem set netlist_type spectre; xschem save; xschem netlist; xschem simulate"}
C {devices/launcher.sym} 1720 -1210 0 0 {name=h1
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/sp1.raw"}
