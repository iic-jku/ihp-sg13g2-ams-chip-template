v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {sg13g2_ip__rfpad_70x70, 80 x 250 um RF bond pad

Desd_vss, Desd_vdd  the PDK's 2 kV ESD diode pair, 35 um2 pad junction
         each, on the core rails vdd and vss. The third terminal (well
         tie of diodevss, substrate tie of diodevdd) is live and wired.

Cm_*     metal capacitance of the pad node, per chip net. Not devices,
         so lvs_ignore=open keeps them out of the LVS netlist while
         a simulation charges them. Magic extraction of the layout
         grouped by rail band.

iovss and iovdd carry no device, so LVS compares vdd, vss and pad.
padbare is a LEF and Verilog alias of pad, not a node.} 440 -830 0 0 0.2 0.2 {}
T {vdd/vss supply clamp, IHP's IOPadVdd clamp with its source on vss and
the NMOS doubled. Rtrig and Mcap set the trigger, 131 kOhm x ~6 pF, the
inverter holds Mclamp on for about a microsecond after a fast vdd rise.
Rtrig is 25 x rppd 1 x 20 um in series.} 1060 -670 0 0 0.2 0.2 {}
N 320 -580 320 -530 {lab=vdd}
N 240 -500 290 -500 {lab=vss}
N 320 -470 320 -400 {lab=pad}
N 520 -400 520 -330 {lab=pad}
N 520 -270 520 -220 {lab=vss}
N 440 -300 490 -300 {lab=vdd}
N 720 -300 720 -220 {lab=vss}
N 820 -300 820 -180 {lab=iovss}
N 440 -580 440 -300 {lab=vdd}
N 320 -580 440 -580 {lab=vdd}
N 120 -580 320 -580 {lab=vdd}
N 240 -500 240 -220 {lab=vss}
N 120 -220 240 -220 {lab=vss}
N 720 -400 720 -360 {lab=pad}
N 520 -400 720 -400 {lab=pad}
N 240 -220 520 -220 {lab=vss}
N 820 -400 820 -360 {lab=pad}
N 720 -400 820 -400 {lab=pad}
N 120 -180 820 -180 {lab=iovss}
N 920 -440 920 -400 {lab=pad}
N 820 -400 920 -400 {lab=pad}
N 120 -620 920 -620 {lab=iovdd}
N 920 -620 920 -500 {lab=iovdd}
N 1020 -440 1020 -400 {lab=pad}
N 920 -400 1020 -400 {lab=pad}
N 440 -580 1020 -580 {lab=vdd}
N 1020 -580 1020 -500 {lab=vdd}
N 1420 -370 1420 -220 {lab=vss}
N 1420 -400 1460 -400 {lab=vss}
N 1080 -280 1090 -280 {lab=vss}
N 1260 -290 1260 -220 {lab=vss}
N 1200 -320 1220 -320 {lab=clamp_rc}
N 1260 -320 1300 -320 {lab=vss}
N 1200 -500 1220 -500 {lab=clamp_rc}
N 1260 -500 1300 -500 {lab=vdd}
N 1120 -400 1120 -320 {lab=clamp_rc}
N 520 -220 720 -220 {lab=vss}
N 1120 -580 1120 -500 {lab=vdd}
N 1300 -580 1420 -580 {lab=vdd}
N 1080 -280 1080 -220 {lab=vss}
N 1260 -220 1300 -220 {lab=vss}
N 1080 -220 1120 -220 {lab=vss}
N 1160 -280 1160 -220 {lab=vss}
N 1150 -280 1160 -280 {lab=vss}
N 1120 -220 1160 -220 {lab=vss}
N 1160 -220 1260 -220 {lab=vss}
N 1300 -320 1300 -220 {lab=vss}
N 1260 -580 1260 -530 {lab=vdd}
N 1120 -580 1260 -580 {lab=vdd}
N 1300 -580 1300 -500 {lab=vdd}
N 1200 -400 1200 -320 {lab=clamp_rc}
N 1120 -400 1200 -400 {lab=clamp_rc}
N 1120 -440 1120 -400 {lab=clamp_rc}
N 1200 -500 1200 -400 {lab=clamp_rc}
N 1260 -400 1260 -350 {lab=clamp_g}
N 1300 -220 1420 -220 {lab=vss}
N 1460 -400 1460 -220 {lab=vss}
N 1420 -220 1460 -220 {lab=vss}
N 1260 -580 1300 -580 {lab=vdd}
N 1420 -580 1420 -430 {lab=vdd}
N 1260 -400 1380 -400 {lab=clamp_g}
N 1260 -470 1260 -400 {lab=clamp_g}
N 1120 -280 1120 -220 {lab=vss}
N 320 -400 520 -400 {lab=pad}
N 120 -400 320 -400 {lab=pad}
N 1020 -580 1120 -580 {lab=vdd}
N 720 -220 1080 -220 {lab=vss}
C {devices/title.sym} 160 0 0 0 {name=l1 author="(c) 2026 Simon Dorrer and Harald Pretl, Apache-2.0 WITH SHL-2.1"}
C {devices/iopin.sym} 120 -220 2 0 {name=p1 lab=vss}
C {devices/iopin.sym} 120 -580 2 0 {name=p2 lab=vdd}
C {devices/iopin.sym} 120 -180 2 0 {name=p3 lab=iovss}
C {devices/iopin.sym} 120 -620 2 0 {name=p4 lab=iovdd}
C {devices/iopin.sym} 120 -400 0 1 {name=p5 lab=pad}
C {sg13g2_pr/diodevdd_2kv.sym} 320 -500 0 0 {name=Desd_vdd
model=diodevdd_2kv
m=1
spiceprefix=X
}
C {sg13g2_pr/diodevss_2kv.sym} 520 -300 0 0 {name=Desd_vss
model=diodevss_2kv
m=1
spiceprefix=X
}
C {devices/capa.sym} 720 -330 0 0 {name=Cm_vss
m=1
value=115.60f
lvs_ignore=open
}
C {devices/capa.sym} 820 -330 0 0 {name=Cm_iovss
m=1
value=14.47f
lvs_ignore=open
}
C {devices/capa.sym} 920 -470 2 0 {name=Cm_iovdd
m=1
value=5.23f
lvs_ignore=open
}
C {devices/capa.sym} 1020 -470 2 0 {name=Cm_vdd
m=1
value=16.79f
lvs_ignore=open
}
C {sg13g2_pr/sg13_hv_nmos.sym} 1400 -400 0 0 {name=Mclamp
l=0.6u
w=1512u
ng=168
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 1120 -300 1 0 {name=Mcap
l=9.5u
w=126u
ng=14
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 1240 -320 0 0 {name=Minv_n
l=0.5u
w=108u
ng=16
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 1240 -500 0 0 {name=Minv_p
l=0.5u
w=350u
ng=50
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/rppd.sym} 1120 -470 0 0 {name=Rtrig
w=1e-6
l=500e-6
model=rppd
body=vss
spiceprefix=X
b=0
m=1
}
C {lab_wire.sym} 1190 -400 0 0 {name=p6 sig_type=std_logic lab=clamp_rc}
C {lab_wire.sym} 1360 -400 0 0 {name=p7 sig_type=std_logic lab=clamp_g}
