v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Testbench for the tuning curve (transient) - 20 GHz VCO} 450 -1730 0 0 1 1 {}
N 1180 -1120 1180 -1080 {lab=ibias_100u}
N 1240 -1120 1240 -1080 {lab=di_en}
N 1300 -1120 1300 -1080 {lab=VDD}
N 1300 -880 1300 -840 {lab=GND}
N 1020 -980 1080 -980 {lab=vtune}
N 1360 -1000 1480 -1000 {lab=rf_out_p}
N 1540 -1000 1600 -1000 {lab=vout_p}
N 1600 -1000 1600 -970 {lab=vout_p}
N 1600 -910 1600 -870 {lab=GND}
N 1600 -1000 1660 -1000 {lab=vout_p}
N 1360 -960 1440 -960 {lab=rf_out_n}
N 1440 -960 1440 -800 {lab=rf_out_n}
N 1440 -800 1480 -800 {lab=rf_out_n}
N 1540 -800 1600 -800 {lab=vout_n}
N 1600 -800 1600 -770 {lab=vout_n}
N 1600 -710 1600 -670 {lab=GND}
N 1600 -800 1660 -800 {lab=vout_n}
N 700 -910 700 -870 {lab=VDD}
N 700 -810 700 -770 {lab=GND}
N 820 -910 820 -870 {lab=di_en}
N 820 -810 820 -770 {lab=GND}
N 940 -910 940 -870 {lab=vtune}
N 940 -810 940 -770 {lab=GND}
N 820 -1250 820 -1210 {lab=VDD}
N 820 -1150 820 -1110 {lab=ibias_100u}
C {title-3.sym} 0 0 0 0 {name=l1 author="Simon Dorrer" rev=1.0 lock=true}
C {vco_top.sym} 1100 -900 0 0 {name=x1}
C {devices/lab_pin.sym} 1180 -1120 3 0 {name=l1 sig_type=std_logic lab=ibias_100u}
C {devices/lab_pin.sym} 1240 -1120 3 0 {name=l2 sig_type=std_logic lab=di_en}
C {devices/vdd.sym} 1300 -1120 0 0 {name=l3 lab=VDD}
C {devices/gnd.sym} 1300 -840 0 0 {name=l4 lab=GND}
C {devices/lab_pin.sym} 1020 -980 0 0 {name=l5 sig_type=std_logic lab=vtune}
C {devices/lab_wire.sym} 1440 -1000 0 0 {name=l6 sig_type=std_logic lab=rf_out_p}
C {devices/capa.sym} 1510 -1000 1 0 {name=Cp
m=1
value=10p
footprint=1206
device="ceramic capacitor"}
C {devices/res.sym} 1600 -940 0 0 {name=Rp
value=50
footprint=1206
device=resistor
m=1}
C {devices/gnd.sym} 1600 -870 0 0 {name=l7 lab=GND}
C {devices/lab_pin.sym} 1660 -1000 0 1 {name=l8 sig_type=std_logic lab=vout_p}
C {devices/lab_wire.sym} 1440 -800 0 0 {name=l9 sig_type=std_logic lab=rf_out_n}
C {devices/capa.sym} 1510 -800 1 0 {name=Cn
m=1
value=10p
footprint=1206
device="ceramic capacitor"}
C {devices/res.sym} 1600 -740 0 0 {name=Rn
value=50
footprint=1206
device=resistor
m=1}
C {devices/gnd.sym} 1600 -670 0 0 {name=l10 lab=GND}
C {devices/lab_pin.sym} 1660 -800 0 1 {name=l11 sig_type=std_logic lab=vout_n}
C {devices/vsource.sym} 700 -840 0 0 {name=VDD value="dc=vdd"}
C {devices/vdd.sym} 700 -910 0 0 {name=l12 lab=VDD}
C {devices/gnd.sym} 700 -770 0 0 {name=l13 lab=GND}
C {devices/vsource.sym} 820 -840 0 0 {name=Ven value="dc=vdd"}
C {devices/lab_pin.sym} 820 -910 3 0 {name=l14 sig_type=std_logic lab=di_en}
C {devices/gnd.sym} 820 -770 0 0 {name=l15 lab=GND}
C {devices/vsource.sym} 940 -840 0 0 {name=Vtune value="dc=0.75 spur=\{0\} smag=[1]"}
C {devices/lab_pin.sym} 940 -910 3 0 {name=l16 sig_type=std_logic lab=vtune}
C {devices/gnd.sym} 940 -770 0 0 {name=l17 lab=GND}
C {devices/isource.sym} 820 -1180 0 0 {name=Ibias value="dc=ibias"}
C {devices/vdd.sym} 820 -1250 0 0 {name=l18 lab=VDD}
C {devices/lab_pin.sym} 820 -1110 1 0 {name=l19 sig_type=std_logic lab=ibias_100u}
C {devices/simulator_commands_shown.sym} 60 -1500 0 0 {name=Script_VACASK
simulator=vacask
only_toplevel=false
value="
control
  abort always

  // Supply and reference current, read by the sources.
  var vdd=1.5
  var ibias=100u

  options strictsave=1
  save v(\\"x1:rf_p\\") v(\\"x1:rf_n\\")

  // Tuning curve: a 1.5 ns transient per tuning voltage, the voltage is in the analysis name.
  // The plot script takes the frequency from the zero crossings of the last 0.5 ns.
  // A transient per point is used because the oscillator PSS does not converge at every tuning voltage.
  alter instance(\\"Vtune\\") dc=0
  analysis tune_0p00 tran stop=1.5n step=0.5p maxstep=0.5p ic=\{\\"x1:rf_p\\", 0.8, \\"x1:rf_n\\", 0.7\}
  alter instance(\\"Vtune\\") dc=0.25
  analysis tune_0p25 tran stop=1.5n step=0.5p maxstep=0.5p ic=\{\\"x1:rf_p\\", 0.8, \\"x1:rf_n\\", 0.7\}
  alter instance(\\"Vtune\\") dc=0.5
  analysis tune_0p50 tran stop=1.5n step=0.5p maxstep=0.5p ic=\{\\"x1:rf_p\\", 0.8, \\"x1:rf_n\\", 0.7\}
  alter instance(\\"Vtune\\") dc=0.75
  analysis tune_0p75 tran stop=1.5n step=0.5p maxstep=0.5p ic=\{\\"x1:rf_p\\", 0.8, \\"x1:rf_n\\", 0.7\}
  alter instance(\\"Vtune\\") dc=1
  analysis tune_1p00 tran stop=1.5n step=0.5p maxstep=0.5p ic=\{\\"x1:rf_p\\", 0.8, \\"x1:rf_n\\", 0.7\}
  alter instance(\\"Vtune\\") dc=1.25
  analysis tune_1p25 tran stop=1.5n step=0.5p maxstep=0.5p ic=\{\\"x1:rf_p\\", 0.8, \\"x1:rf_n\\", 0.7\}
  alter instance(\\"Vtune\\") dc=1.5
  analysis tune_1p50 tran stop=1.5n step=0.5p maxstep=0.5p ic=\{\\"x1:rf_p\\", 0.8, \\"x1:rf_n\\", 0.7\}

  postprocess(PYTHON, \\"../plot_simulations/vacask2data.py\\", \\"vco_top_tb_tune_vacask\\")
endc
"}
C {devices/simulator_commands_shown.sym} 1980 -1330 0 0 {name=Libs_VACASK
simulator=vacask
only_toplevel=false
value="
include \\"sg13g2_vacask_common.lib\\"
include \\"cornerMOSlv.lib\\" section=mos_tt
// patched copy of the HV corner file, its svaricap model has no v() term, see ../models/
include \\"../models/cornerMOShv.lib\\" section=mos_tt
include \\"cornerRES.lib\\" section=res_typ
include \\"cornerCAP.lib\\" section=cap_typ
// devices of the snp2le coil model, see netlist/spectre/vco_ind_le.inc
load \\"inductor.osdi\\"
model inductor inductor
model mutual mutual
include \\"../../../netlist/spectre/vco_ind_le.inc\\"
"}
C {devices/launcher.sym} 1720 -1330 0 0 {name=h2
descr="Simulate" 
tclcommand="set sim(spectre,default) 0; xschem set netlist_type spectre; xschem save; xschem netlist; xschem simulate"}
C {devices/launcher.sym} 1720 -1270 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"}
C {devices/launcher.sym} 1720 -1210 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/tune_0p75.raw"}
