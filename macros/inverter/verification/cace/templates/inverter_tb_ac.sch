v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
P 4 5 1550 -1760 1770 -1760 1770 -1660 1550 -1660 1550 -1760 {dash = 8}
P 4 5 1550 -1040 1770 -1040 1770 -940 1550 -940 1550 -1040 {dash = 8}
P 4 5 1530 -380 1750 -380 1750 -280 1530 -280 1530 -380 {dash = 8}
P 4 5 1800 -1480 1800 -860 320 -860 320 -1480 1800 -1480 {dash = 8}
P 4 5 1800 -2160 1800 -1540 320 -1540 320 -2160 1800 -2160 {dash = 8}
P 4 5 320 -800 1800 -800 1800 -160 320 -160 320 -800 {dash = 8}
T {Capacitive Load} 1550 -1610 0 0 0.25 0.25 {}
T {Template Testbench for AC analysis - Third Order MFB Lowpass Filter} 550 -2360 0 0 1.2 1.2 {}
T {Capacitive Load} 1550 -890 0 0 0.25 0.25 {}
T {Output CM voltage: vout_cm = (voutp_cm + voutn_cm)/2} 1470 -1270 0 0 0.2 0.2 {}
T {Closed-Loop Analysis (Acl, fcu)} 320 -2190 0 0 0.4 0.4 {}
T {Common-Mode Analysis (CMRR)} 320 -1510 0 0 0.4 0.4 {}
T {Capacitive Load} 1530 -230 0 0 0.25 0.25 {}
T {Power Supply Rejection Ratio Analysis (PSRR)} 320 -830 0 0 0.4 0.4 {}
N 900 -1900 940 -1900 {lab=vinp1}
N 900 -1820 940 -1820 {lab=vinn1}
N 1920 -2120 1920 -2080 {lab=VDD}
N 1920 -2020 1920 -1980 {lab=GND}
N 1680 -1880 1720 -1880 {lab=voutp1}
N 1580 -1840 1720 -1840 {lab=voutn1}
N 1580 -1840 1580 -1740 {lab=voutn1}
N 1580 -1680 1580 -1640 {lab=GND}
N 1680 -1880 1680 -1740 {lab=voutp1}
N 1680 -1680 1680 -1640 {lab=GND}
N 2100 -2020 2100 -1980 {
lab=GND}
N 2100 -2120 2100 -2080 {
lab=VSS}
N 900 -1180 940 -1180 {lab=vinp2}
N 900 -1100 940 -1100 {lab=vinn2}
N 1580 -960 1580 -920 {lab=GND}
N 1680 -960 1680 -920 {lab=GND}
N 1720 -1380 1720 -1300 {lab=GND}
N 1600 -1320 1600 -1300 {lab=GND}
N 1600 -1390 1680 -1390 {lab=#net1}
N 1600 -1390 1600 -1380 {lab=#net1}
N 1520 -1330 1560 -1330 {lab=GND}
N 1520 -1330 1520 -1300 {lab=GND}
N 1520 -1370 1560 -1370 {lab=voutn2}
N 1520 -1430 1680 -1430 {lab=voutp2}
N 1720 -2120 1720 -2100 {lab=vout1}
N 1720 -2040 1720 -2020 {lab=GND}
N 1660 -2090 1680 -2090 {lab=voutp1}
N 1660 -2050 1680 -2050 {lab=voutn1}
N 1720 -1460 1720 -1440 {lab=vout2}
N 900 -520 940 -520 {lab=Vcm3}
N 900 -440 940 -440 {lab=Vcm3}
N 1560 -300 1560 -260 {lab=GND}
N 1660 -300 1660 -260 {lab=GND}
N 900 -480 900 -440 {lab=Vcm3}
N 900 -520 900 -480 {lab=Vcm3}
N 820 -480 900 -480 {lab=Vcm3}
N 1700 -740 1700 -720 {lab=vout3}
N 1700 -660 1700 -640 {lab=GND}
N 1640 -710 1660 -710 {lab=voutp3}
N 1640 -670 1660 -670 {lab=voutn3}
N 1660 -500 1700 -500 {lab=voutp3}
N 1560 -460 1700 -460 {lab=voutn3}
N 1140 -720 1140 -680 {lab=vdd_noise}
N 1580 -1120 1720 -1120 {lab=voutn2}
N 1680 -1160 1720 -1160 {lab=voutp2}
N 1160 -940 1160 -920 {lab=GND}
N 1580 -1120 1580 -1020 {lab=voutn2}
N 1680 -1160 1680 -1020 {lab=voutp2}
N 1140 -2100 1140 -2080 {lab=VDD}
N 1160 -1660 1160 -1640 {lab=GND}
N 1160 -280 1160 -260 {lab=GND}
N 1560 -460 1560 -360 {lab=voutn3}
N 1660 -500 1660 -360 {lab=voutp3}
N 2460 -2120 2460 -2080 {lab=Vcm1}
N 2460 -2020 2460 -1980 {lab=GND}
N 2640 -2120 2640 -2080 {lab=Vcm2}
N 2640 -2020 2640 -1980 {lab=GND}
N 2820 -2120 2820 -2080 {lab=Vcm3}
N 2820 -2020 2820 -1980 {lab=GND}
N 1380 -1880 1680 -1880 {lab=voutp1}
N 1380 -1840 1580 -1840 {lab=voutn1}
N 1380 -500 1660 -500 {lab=voutp3}
N 1380 -460 1560 -460 {lab=voutn3}
N 660 -440 660 -420 {lab=vdd_noise}
N 660 -360 660 -340 {lab=#net2}
N 660 -280 660 -260 {lab=GND}
N 1380 -1160 1680 -1160 {lab=voutp2}
N 1380 -1120 1580 -1120 {lab=voutn2}
N 510 -1070 510 -1050 {lab=GND}
N 620 -1180 660 -1180 {lab=vinp2}
N 620 -1100 660 -1100 {lab=vinn2}
N 620 -1140 660 -1140 {lab=Vcm2}
N 420 -1150 460 -1150 {lab=vin}
N 380 -1870 400 -1870 {lab=vin}
N 400 -1870 400 -1850 {lab=vin}
N 620 -1900 660 -1900 {lab=vinp1}
N 620 -1820 660 -1820 {lab=vinn1}
N 400 -1870 460 -1870 {lab=vin}
N 400 -1790 400 -1760 {lab=GND}
N 510 -1790 510 -1760 {lab=GND}
N 620 -1860 660 -1860 {lab=Vcm1}
N 1140 -2080 1180 -2080 {lab=VDD}
N 1180 -2080 1180 -2060 {lab=VDD}
N 1140 -2080 1140 -2060 {lab=VDD}
N 1140 -1380 1140 -1360 {lab=VDD}
N 1140 -1360 1180 -1360 {lab=VDD}
N 1180 -1360 1180 -1340 {lab=VDD}
N 1140 -1360 1140 -1340 {lab=VDD}
N 1180 -700 1180 -680 {lab=VDD}
N 1220 -1660 1220 -1640 {lab=GND}
N 1220 -940 1220 -920 {lab=GND}
N 1220 -280 1220 -260 {lab=GND}
C {devices/code_shown.sym} 1920 -1550 0 0 {name=NGSPICE
simulator=ngspice
only_toplevel=false
value="
.include CACE\{DUT_path\}
.temp CACE\{temp\}
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15 SEED=CACE[CACE\{seed=12345\} + CACE\{iterations=0\}]
* Flag unsafe operating conditions (exceeds models' specified limits)
.option warn=1
.control

* optran 0 0 0 1u 1m 0

* save v(vin) v(vout1) v(vout2) v(vout3) v(vdd_noise) v(vin_dm) v(vin_cm)
save all

set num_threads=16

* AC Analysis
ac dec 101 1 1G

* Closed-loop gain
let Acl=v(vout1)/v(vin)
let Acl_dB = vdb(Acl)

* Common-mode gain
let Acm=v(vout2)/v(vin)
let Acm_dB = vdb(Acm)

* Common Mode Rejection Ratio (CMRR)
* let CMRR = v(vout1)/v(vout2)
let CMRR = v(Acl)/v(Acm)
let CMRR_dB = vdb(CMRR)
* let CMRR_dB = Acl_dB - Acm_dB

* PSRR
let PSRR = v(vdd_noise)/v(vout3)
let PSRR_dB = vdb(PSRR)

* Measurements
* 10Hz closed-loop gain
meas ac Adc_cl_dB find Acl_dB when frequency = 10

* Upper 3dB cut-off frequency
let Amag_fc = Adc_cl_dB-3
meas ac fcu find frequency when Acl_dB = Amag_fc FALL=1

* 10Hz CMRR
meas ac CMRR_dc_dB find CMRR_dB when frequency = 10

* 10Hz PSRR
meas ac PSRR_dc_dB find PSRR_dB when frequency = 10

echo $&Adc_cl_dB $&fcu $&CMRR_dc_dB $&PSRR_dc_dB > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data

.endc
"}
C {devices/vsource.sym} 1920 -2050 0 0 {name=VDD value=CACE\{vdd\}}
C {devices/capa.sym} 1580 -1710 0 0 {name=C1
m=1
value=CACE\{cload\}
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} 1720 -1880 0 1 {name=p3 sig_type=std_logic lab=voutp1}
C {lab_pin.sym} 1720 -1840 0 1 {name=p4 sig_type=std_logic lab=voutn1}
C {devices/lab_pin.sym} 900 -1900 0 0 {name=l1 sig_type=std_logic lab=vinp1}
C {devices/lab_pin.sym} 900 -1820 0 0 {name=l19 sig_type=std_logic lab=vinn1
}
C {devices/capa.sym} 1680 -1710 0 0 {name=C2
m=1
value=CACE\{cload\}
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 1720 -2120 0 1 {name=l12 sig_type=std_logic lab=vout1}
C {devices/vcvs.sym} 1720 -2070 0 0 {name=E1 value=1}
C {devices/lab_pin.sym} 1660 -2050 2 1 {name=l15 sig_type=std_logic lab=voutn1
}
C {devices/lab_pin.sym} 1660 -2090 0 0 {name=l23 sig_type=std_logic lab=voutp1}
C {devices/vsource.sym} 2100 -2050 0 0 {name=VSS value=0 savecurrent=false}
C {devices/gnd.sym} 2100 -1980 0 0 {name=l16 lab=GND}
C {devices/lab_wire.sym} 2100 -2120 0 0 {name=p1 sig_type=std_logic lab=VSS}
C {devices/gnd.sym} 1920 -1980 0 0 {name=l2 lab=GND}
C {devices/gnd.sym} 1720 -2020 0 0 {name=l6 lab=GND}
C {devices/gnd.sym} 1680 -1640 0 0 {name=l7 lab=GND}
C {devices/gnd.sym} 1580 -1640 0 0 {name=l8 lab=GND}
C {vdd.sym} 1920 -2120 0 0 {name=l21 lab=VDD}
C {devices/capa.sym} 1580 -990 0 0 {name=C3
m=1
value=CACE\{cload\}
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} 1720 -1160 0 1 {name=p2 sig_type=std_logic lab=voutp2}
C {lab_pin.sym} 1720 -1120 0 1 {name=p5 sig_type=std_logic lab=voutn2}
C {devices/capa.sym} 1680 -990 0 0 {name=C4
m=1
value=CACE\{cload\}
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1680 -920 0 0 {name=l31 lab=GND}
C {devices/gnd.sym} 1580 -920 0 0 {name=l32 lab=GND}
C {devices/lab_pin.sym} 1720 -1460 0 1 {name=l34 sig_type=std_logic lab=vout2}
C {devices/vcvs.sym} 1720 -1410 0 0 {name=E8 value=0.5}
C {devices/gnd.sym} 1720 -1300 0 0 {name=l36 lab=GND}
C {devices/lab_pin.sym} 1520 -1370 2 1 {name=l39 sig_type=std_logic lab=voutn2
}
C {devices/lab_pin.sym} 1520 -1430 0 0 {name=l40 sig_type=std_logic lab=voutp2
}
C {devices/vcvs.sym} 1600 -1350 0 0 {name=E10 value=-1}
C {devices/gnd.sym} 1600 -1300 0 0 {name=l45 lab=GND}
C {devices/gnd.sym} 1520 -1300 0 0 {name=l46 lab=GND}
C {devices/gnd.sym} 1560 -260 0 0 {name=l20 lab=GND}
C {devices/gnd.sym} 1160 -260 0 0 {name=l42 lab=GND}
C {lab_pin.sym} 1700 -500 0 1 {name=p6 sig_type=std_logic lab=voutp3}
C {lab_pin.sym} 1700 -460 0 1 {name=p7 sig_type=std_logic lab=voutn3}
C {devices/gnd.sym} 1660 -260 0 0 {name=l43 lab=GND}
C {devices/lab_pin.sym} 820 -480 0 0 {name=l47 sig_type=std_logic lab=Vcm3}
C {devices/lab_pin.sym} 1700 -740 0 1 {name=l14 sig_type=std_logic lab=vout3}
C {devices/lab_pin.sym} 1640 -670 2 1 {name=l48 sig_type=std_logic lab=voutn3
}
C {devices/lab_pin.sym} 1640 -710 0 0 {name=l49 sig_type=std_logic lab=voutp3}
C {devices/gnd.sym} 1700 -640 0 0 {name=l50 lab=GND}
C {devices/capa.sym} 1560 -330 0 0 {name=C5
m=1
value=CACE\{cload\}
footprint=1206
device="ceramic capacitor"}
C {devices/capa.sym} 1660 -330 0 0 {name=C6
m=1
value=CACE\{cload\}
footprint=1206
device="ceramic capacitor"}
C {title-2.sym} 0 0 0 0 {name=l67 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/vcvs.sym} 1700 -690 0 0 {name=E9 value=1}
C {devices/lab_pin.sym} 1140 -720 0 0 {name=l44 sig_type=std_logic lab=vdd_noise}
C {devices/gnd.sym} 1160 -920 0 0 {name=l30 lab=GND}
C {devices/gnd.sym} 1160 -1640 0 0 {name=l5 lab=GND}
C {vdd.sym} 1140 -2100 0 0 {name=l9 lab=VDD}
C {devices/vsource.sym} 2460 -2050 0 0 {name=Vcm1 value=CACE\{vcm\}
}
C {devices/lab_pin.sym} 2460 -2120 2 0 {name=l72 sig_type=std_logic lab=Vcm1}
C {devices/gnd.sym} 2460 -1980 0 0 {name=l73 lab=GND}
C {devices/vsource.sym} 2640 -2050 0 0 {name=Vcm2 value=CACE\{vcm\}
}
C {devices/lab_pin.sym} 2640 -2120 2 0 {name=l74 sig_type=std_logic lab=Vcm2}
C {devices/gnd.sym} 2640 -1980 0 0 {name=l75 lab=GND}
C {devices/vsource.sym} 2820 -2050 0 0 {name=Vcm3 value=CACE\{vcm\}
}
C {devices/lab_pin.sym} 2820 -2120 2 0 {name=l76 sig_type=std_logic lab=Vcm3}
C {devices/gnd.sym} 2820 -1980 0 0 {name=l77 lab=GND}
C {devices/gnd.sym} 660 -260 0 0 {name=l52 lab=GND}
C {devices/vsource.sym} 660 -310 0 0 {name=VDD_PSRR value=CACE\{vdd\}}
C {devices/vsource.sym} 660 -390 0 0 {name=VDD_NOISE value="dc 0 ac 1"}
C {devices/lab_pin.sym} 660 -440 1 0 {name=l41 sig_type=std_logic lab=vdd_noise}
C {iqmod_mfb_lpf.sym} 1160 -1860 0 0 {name=x1
spice_ignore=false}
C {iqmod_mfb_lpf.sym} 1160 -1140 0 0 {name=x2
spice_ignore=false}
C {iqmod_mfb_lpf.sym} 1160 -480 0 0 {name=x3
spice_ignore=false}
C {devices/lab_pin.sym} 900 -1180 0 0 {name=l10 sig_type=std_logic lab=vinp2}
C {devices/lab_pin.sym} 900 -1100 0 0 {name=l11 sig_type=std_logic lab=vinn2}
C {devices/lab_pin.sym} 660 -1180 2 0 {name=l60 sig_type=std_logic lab=vinp2}
C {devices/lab_pin.sym} 660 -1100 2 0 {name=l61 sig_type=std_logic lab=vinn2}
C {devices/lab_pin.sym} 420 -1150 0 0 {name=l62 sig_type=std_logic lab=vin}
C {devices/lab_pin.sym} 660 -1140 2 0 {name=l63 sig_type=std_logic lab=Vcm2}
C {devices/gnd.sym} 510 -1050 0 0 {name=l64 lab=GND}
C {devices/vsource.sym} 400 -1820 0 0 {name=vin value="dc 0 ac 1"
}
C {devices/lab_pin.sym} 660 -1900 2 0 {name=l13 sig_type=std_logic lab=vinp1}
C {devices/lab_pin.sym} 660 -1820 2 0 {name=l17 sig_type=std_logic lab=vinn1}
C {devices/lab_pin.sym} 380 -1870 0 0 {name=l18 sig_type=std_logic lab=vin}
C {devices/gnd.sym} 400 -1760 0 0 {name=l57 lab=GND}
C {devices/gnd.sym} 510 -1760 0 0 {name=l59 lab=GND}
C {devices/lab_pin.sym} 660 -1860 2 0 {name=l56 sig_type=std_logic lab=Vcm1}
C {devices/code_shown.sym} 1920 -1770 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_CACE\{corner_mos\}
.lib cornerMOShv.lib mos_CACE\{corner_mos\}
.lib cornerRES.lib res_CACE\{corner_rc\}
.lib cornerCAP.lib cap_CACE\{corner_rc\}
"}
C {vdd.sym} 1140 -1380 0 0 {name=l3 lab=VDD}
C {vdd.sym} 1180 -700 0 0 {name=l4 lab=VDD}
C {single2dm.sym} 540 -1860 0 0 {name=x4 gain=1}
C {single2cm.sym} 540 -1140 0 0 {name=x5 gain=1}
C {devices/gnd.sym} 1220 -1640 0 0 {name=l22 lab=GND}
C {devices/gnd.sym} 1220 -920 0 0 {name=l24 lab=GND}
C {devices/gnd.sym} 1220 -260 0 0 {name=l25 lab=GND}
