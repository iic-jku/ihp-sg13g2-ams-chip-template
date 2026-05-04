v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 60 -1860 860 -1460 {flags=graph
y1=-0.56
y2=2.1
ypos1=-0.56
ypos2=2.1
divy=5
subdivy=1
unity=1
x1=0
x2=4.3301839e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="clock
reset_n
spi_si
spi_sclk
spi_sram_ce
uart_tx"
color="4 21 12 12 12 17"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 900 -1860 1700 -1460 {flags=graph
y1=-0.56
y2=2.1
ypos1=-0.56
ypos2=2.1
divy=5
subdivy=1
unity=1
x1=0
x2=4.3301839e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="i2c_sda
i2c_scl
gpio_0
gpio_1
gpio_2
gpio_3"
color="4 4 21 21 21 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 1740 -1860 2540 -1460 {flags=graph
y1=-0.56
y2=2.1
ypos1=2.9506742
ypos2=5.6106742
divy=5
subdivy=1
unity=1
x1=0
x2=4.3301839e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="ds_I_p
ds_I_n
ds_Q_n
ds_Q_p"
color="4 4 21 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1}
B 2 2580 -1860 3380 -1460 {flags=graph
y1=-0.56
y2=2.1
ypos1=-0.56
ypos2=2.1
divy=5
subdivy=1
unity=1
x1=0
x2=4.3301839e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="lo_I
lo_Ix
lo_Qx
lo_Q"
color="4 4 21 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0
digital=1
hilight_wave=4}
B 2 60 -2280 860 -1880 {flags=graph
y1=-0.0066
y2=0.0013
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=4.3301839e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0


dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
color="4 21"
node="i(VDD)
i(VIO)"}
B 2 1740 -1420 2540 -1020 {flags=graph
y1=-8.3e-11
y2=0.36
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=4.3301839e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="vout_RF
vout_RF_filt"
color="4 7"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0}
B 2 900 -2280 1700 -1880 {flags=graph
y1=1.5
y2=3.3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=4.3301839e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="v(VDD)
v(VIO)"
color="4 21"
dataset=-1
unitx=1
logx=0
logy=0
linewidth_mult=3
autoload=0}
T {Testbench for transient analysis - WSPR Transmitter} 950 -2390 0 0 1 1 {}
N 2380 -2080 2380 -2040 {lab=VDD}
N 2380 -1980 2380 -1940 {lab=GND}
N 1760 -1980 1760 -1940 {lab=GND}
N 1760 -2100 1760 -2040 {lab=clock}
N 2060 -1980 2060 -1940 {lab=GND}
N 2060 -2100 2060 -2040 {lab=reset_n}
N 1420 -790 1420 -750 {lab=vout_RF}
N 1580 -650 1580 -570 {lab=GND}
N 1740 -630 1740 -570 {lab=GND}
N 1740 -750 1740 -690 {lab=vout_RF_filt}
N 1420 -750 1420 -690 {lab=vout_RF}
N 1420 -630 1420 -570 {lab=GND}
N 1420 -750 1480 -750 {lab=vout_RF}
N 1680 -750 1740 -750 {lab=vout_RF_filt}
N 1740 -790 1740 -750 {lab=vout_RF_filt}
N 920 -300 920 -200 {lab=GND}
N 560 -300 560 -200 {lab=GND}
N 440 -300 440 -200 {lab=GND}
N 260 -420 260 -200 {lab=GND}
N 260 -600 320 -600 {lab=GND}
N 260 -720 320 -720 {lab=GND}
N 260 -720 260 -600 {lab=GND}
N 560 -1260 560 -1200 {lab=GND}
N 440 -1260 560 -1260 {lab=GND}
N 260 -1020 260 -720 {lab=GND}
N 440 -1260 440 -1200 {lab=GND}
N 260 -1260 440 -1260 {lab=GND}
N 1280 -360 1280 -200 {lab=GND}
N 1220 -600 1280 -600 {lab=GND}
N 1280 -900 1280 -600 {lab=GND}
N 1220 -480 1280 -480 {lab=GND}
N 1280 -600 1280 -480 {lab=GND}
N 1220 -900 1280 -900 {lab=GND}
N 1280 -1020 1280 -900 {lab=GND}
N 1220 -1020 1280 -1020 {lab=GND}
N 1220 -1140 1280 -1140 {lab=GND}
N 1280 -1080 1280 -1020 {lab=GND}
N 1220 -1080 1280 -1080 {lab=GND}
N 1280 -1140 1280 -1080 {lab=GND}
N 1220 -360 1280 -360 {lab=GND}
N 1280 -420 1280 -360 {lab=GND}
N 1220 -420 1280 -420 {lab=GND}
N 1280 -480 1280 -420 {lab=GND}
N 1220 -960 1320 -960 {lab=VDD}
N 1220 -540 1320 -540 {lab=VDD}
N 1320 -960 1320 -540 {lab=VDD}
N 220 -660 320 -660 {lab=VDD}
N 500 -1300 500 -1200 {lab=VDD}
N 860 -1300 860 -1200 {lab=VDD}
N 220 -1300 220 -660 {lab=VDD}
N 180 -1140 320 -1140 {lab=clock}
N 180 -1080 320 -1080 {lab=reset_n}
N 1320 -1300 1320 -960 {lab=VDD}
N 1220 -840 1360 -840 {lab=vout_RF}
N 1360 -840 1360 -780 {lab=vout_RF}
N 1220 -780 1360 -780 {lab=vout_RF}
N 1220 -720 1360 -720 {lab=vout_RF}
N 1360 -720 1360 -660 {lab=vout_RF}
N 1220 -660 1360 -660 {lab=vout_RF}
N 1360 -750 1360 -720 {lab=vout_RF}
N 1360 -750 1420 -750 {lab=vout_RF}
N 1360 -780 1360 -750 {lab=vout_RF}
N 920 -1260 920 -1200 {lab=GND}
N 800 -1260 920 -1260 {lab=GND}
N 620 -1260 620 -1200 {lab=GND}
N 560 -1260 620 -1260 {lab=GND}
N 680 -1260 680 -1200 {lab=GND}
N 620 -1260 680 -1260 {lab=GND}
N 740 -1260 740 -1200 {lab=GND}
N 680 -1260 740 -1260 {lab=GND}
N 800 -1260 800 -1200 {lab=GND}
N 740 -1260 800 -1260 {lab=GND}
N 380 -1300 380 -1200 {lab=VIO}
N 800 -300 800 -160 {lab=gpio_3}
N 740 -300 740 -160 {lab=gpio_2}
N 680 -300 680 -160 {lab=gpio_1}
N 620 -300 620 -160 {lab=gpio_0}
N 220 -240 500 -240 {lab=VDD}
N 220 -660 220 -240 {lab=VDD}
N 500 -300 500 -240 {lab=VDD}
N 860 -300 860 -240 {lab=VDD}
N 860 -240 1320 -240 {lab=VDD}
N 1320 -540 1320 -240 {lab=VDD}
N 180 -480 320 -480 {lab=i2c_scl}
N 180 -360 320 -360 {lab=uart_tx}
N 180 -840 320 -840 {lab=spi_sram_ce}
N 180 -900 320 -900 {lab=spi_sclk}
N 180 -960 320 -960 {lab=spi_si}
N 260 -1020 320 -1020 {lab=GND}
N 260 -1260 260 -1020 {lab=GND}
N 260 -420 320 -420 {lab=GND}
N 260 -600 260 -420 {lab=GND}
N 180 -540 320 -540 {lab=i2c_sda}
N 980 -300 980 -160 {lab=ds_Q_p}
N 1040 -300 1040 -160 {lab=ds_Q_n}
N 1100 -300 1100 -160 {lab=lo_Q}
N 1160 -300 1160 -160 {lab=lo_Qx}
N 980 -1340 980 -1200 {lab=ds_I_p}
N 1040 -1340 1040 -1200 {lab=ds_I_n}
N 1100 -1340 1100 -1200 {lab=lo_I}
N 1160 -1340 1160 -1200 {lab=lo_Ix}
N 180 -780 320 -780 {lab=VIO}
N 380 -300 380 -160 {lab=VIO}
N 2520 -2080 2520 -2040 {lab=VIO}
N 2520 -1980 2520 -1940 {lab=GND}
C {devices/code.sym} 2910 -2060 0 0 {name=NGSPICE
only_toplevel=true 
value="
*.include ../../verification/pex/chip_top_pex.spice
.include /foss/designs/Chip/ihp130/macros/counter/netlist/xspice/counter_top/counter_top.xspice
.param IOVDD=3.3
.param VDD=1.5
.param temp=27
.param Cload=10p
.param Rload=1k
.param fclk=56e6
.csparam fclk=fclk
.param fsig=124.600e3
.csparam fsig=fsig
.param flo=fclk/2
.csparam flo=flo
* .options klu reltol=1e-3 abstol=1e-12 gmin=1e-12 rshunt=1e12
.control

pre_osdi $PDK_ROOT/$PDK/libs.tech/ngspice/osdi/psp103.osdi
pre_osdi $PDK_ROOT/$PDK/libs.tech/ngspice/osdi/psp103_nqs.osdi
pre_osdi $PDK_ROOT/$PDK/libs.tech/ngspice/osdi/r3_cmc.osdi

set num_threads=32

* save all

* User Constants
* Increase tstop --> more FFT bins
* Decrease tstep --> higher fs/2 in FFT
let fmin = 0.1 * flo
let fmax = 5 * flo
let tstart = 1/fsig
let tstop = 2/fsig
let tstep = 0.1/flo

* Transient Operating Point Analysis
*optran 0 0 0 $&tstep $&tstart 0
op
remzerovec
write @schname\\\\.raw
set appendwrite

* Transient Analysis
tran $&tstep 1u 0
*tran $&tstep $&tstop $&tstart
write @schname\\\\.raw

* Plotting
plot vout_RF vout_RF_filt

* Write Data
unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata $DESIGNS/Chip/ihp130/scripts/plot_simulations/data/chip_top_tb_tran.txt v(clock) v(reset_n) v(vout_RF) v(vout_RF_filt)

* FFT vout_RF_filt
setplot tran1
linearize vout_RF_filt
set specwindow=hanning
fft vout_RF_filt
setplot sp2

let N = length(vout_RF_filt)
let fres = frequency[n-1]/n
let fmin_idx = ceil(const.fmin/fres)
let fmax_idx = ceil(const.fmax/fres)
let vout_RF_filt_spec = mag(vout_RF_filt)
let vout_RF_filt_spec_slice = vout_RF_filt_spec[fmin_idx,fmax_idx]
let freq = frequency[fmin_idx,fmax_idx]
meas sp vout_RF_filt_max max vout_RF_filt_spec_slice
let vout_RF_filt_spec_db = 20*log10(vout_RF_filt_spec_slice/vout_RF_filt_max)
plot vout_RF_filt_spec_db vs freq

* Write Data
setscale freq
unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata $DESIGNS/Chip/ihp130/scripts/plot_simulations/data/chip_top_tb_tran_fft_filt.txt v(vout_RF_filt_spec_db)

* Calc HD2, HD3
* let sig_idx = ceil(const.f_sig/fres)
* let hd2_idx = 2*sig_idx
* let hd3_idx = 3*sig_idx
* let sig_pwr = iod_spec[sig_idx-1]^2+iod_spec[sig_idx]^2+iod_spec[sig_idx+1]^2
* let hd2_pwr = iod_spec[hd2_idx-1]^2+iod_spec[hd2_idx]^2+iod_spec[hd2_idx+1]^2
* let hd3_pwr = iod_spec[hd3_idx-1]^2+iod_spec[hd3_idx]^2+iod_spec[hd3_idx+1]^2
* let hd2 = sqrt(hd2_pwr/sig_pwr)
* let hd3 = sqrt(hd3_pwr/sig_pwr)
* let hd2_dB = 20*log10(hd2)
* let hd3_dB = 20*log10(hd3)
* print hd2_dB
* print hd3_dB

*quit
*rusage all
.endc
"}
C {devices/launcher.sym} 2680 -2050 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 2680 -1930 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw tran"
}
C {devices/launcher.sym} 2680 -1990 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/code_shown.sym} 3120 -2050 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerHBT.lib hbt_typ
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerDIO.lib dio_tt
"}
C {devices/vsource.sym} 2380 -2010 0 0 {name=VDD value=\{VDD\}}
C {devices/gnd.sym} 2380 -1940 0 0 {name=l3 lab=GND}
C {vdd.sym} 2380 -2080 0 0 {name=l7 lab=VDD}
C {devices/lab_wire.sym} 1760 -2100 0 0 {name=p17 sig_type=std_logic lab=clock}
C {devices/gnd.sym} 1760 -1940 0 0 {name=l11 lab=GND}
C {devices/vsource.sym} 1760 -2010 0 0 {name=vclk value="pulse(0 \{IOVDD\} 0 100p 100p \{0.5/fclk\} \{1/fclk\})"
}
C {devices/lab_wire.sym} 2060 -2100 0 0 {name=p18 sig_type=std_logic lab=reset_n}
C {devices/gnd.sym} 2060 -1940 0 0 {name=l10 lab=GND}
C {devices/vsource.sym} 2060 -2010 0 0 {name=vrst value="pulse(\{IOVDD\} 0 \{2/fclk\} 100p 100p \{2/fclk\} 1 1)"
}
C {devices/lab_wire.sym} 1740 -790 0 1 {name=l37 sig_type=std_logic lab=vout_RF_filt}
C {devices/lab_wire.sym} 1420 -790 0 1 {name=l21 sig_type=std_logic lab=vout_RF}
C {devices/gnd.sym} 1580 -570 0 0 {name=l36 lab=GND}
C {res.sym} 1740 -660 0 0 {name=R1
value=\{Rload\}
footprint=1206
device=resistor
m=1}
C {devices/gnd.sym} 1740 -570 0 0 {name=l42 lab=GND}
C {devices/capa.sym} 1420 -660 0 0 {name=C1
m=1
value=\{Cload\}
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1420 -570 0 0 {name=l43 lab=GND}
C {coupled_resonator_lc_bpf_1k_1k.sym} 1580 -750 0 0 {name=x3}
C {devices/lab_wire.sym} 180 -1080 0 0 {name=p1 sig_type=std_logic lab=reset_n}
C {devices/lab_wire.sym} 180 -1140 0 0 {name=p2 sig_type=std_logic lab=clock}
C {devices/lab_wire.sym} 180 -480 0 0 {name=p7 sig_type=std_logic lab=i2c_scl}
C {devices/lab_wire.sym} 180 -360 0 0 {name=p10 sig_type=std_logic lab=uart_tx}
C {devices/lab_wire.sym} 180 -840 0 0 {name=p11 sig_type=std_logic lab=spi_sram_ce}
C {devices/lab_wire.sym} 180 -900 0 0 {name=p12 sig_type=std_logic lab=spi_sclk}
C {devices/lab_wire.sym} 180 -960 0 0 {name=p13 sig_type=std_logic lab=spi_si}
C {devices/lab_wire.sym} 620 -160 3 0 {name=p3 sig_type=std_logic lab=gpio_0}
C {devices/lab_wire.sym} 680 -160 3 0 {name=p4 sig_type=std_logic lab=gpio_1}
C {devices/lab_wire.sym} 740 -160 3 0 {name=p5 sig_type=std_logic lab=gpio_2}
C {devices/lab_wire.sym} 800 -160 3 0 {name=p6 sig_type=std_logic lab=gpio_3}
C {devices/gnd.sym} 920 -200 0 0 {name=l4 lab=GND}
C {title-2.sym} 0 0 0 0 {name=l9 author="Simon Dorrer" rev=1.0 lock=true}
C {devices/gnd.sym} 560 -200 0 0 {name=l12 lab=GND}
C {devices/gnd.sym} 440 -200 0 0 {name=l13 lab=GND}
C {devices/gnd.sym} 260 -200 0 0 {name=l14 lab=GND}
C {devices/gnd.sym} 1280 -200 0 1 {name=l17 lab=GND}
C {vdd.sym} 220 -1300 0 0 {name=l16 lab=VDD}
C {vdd.sym} 860 -1300 0 0 {name=l15 lab=VDD}
C {vdd.sym} 500 -1300 0 0 {name=l18 lab=VDD}
C {vdd.sym} 1320 -1300 0 0 {name=l19 lab=VDD}
C {devices/lab_wire.sym} 980 -1340 3 1 {name=p20 sig_type=std_logic lab=ds_I_p}
C {devices/lab_wire.sym} 1040 -1340 3 1 {name=p21 sig_type=std_logic lab=ds_I_n}
C {devices/lab_wire.sym} 1100 -1340 3 1 {name=p23 sig_type=std_logic lab=lo_I}
C {devices/lab_wire.sym} 1160 -1340 3 1 {name=p24 sig_type=std_logic lab=lo_Ix}
C {devices/lab_wire.sym} 980 -160 3 0 {name=p32 sig_type=std_logic lab=ds_Q_p}
C {devices/lab_wire.sym} 1100 -160 3 0 {name=p14 sig_type=std_logic lab=lo_Q}
C {devices/lab_wire.sym} 1160 -160 3 0 {name=p25 sig_type=std_logic lab=lo_Qx}
C {devices/lab_wire.sym} 1040 -160 3 0 {name=p15 sig_type=std_logic lab=ds_Q_n}
C {devices/lab_wire.sym} 180 -540 0 0 {name=p9 sig_type=std_logic lab=i2c_sda}
C {code_shown.sym} 2620 -2190 0 0 {name=PAD_MODELS
only_toplevel=true
value="tcleval(
.include $::PDK_ROOT/$::PDK/libs.ref/sg13g2_io/spice/sg13g2_io.spi
)"
spice_ignore=false
      }
C {devices/vsource.sym} 2520 -2010 0 0 {name=VIO value=\{IOVDD\}}
C {devices/gnd.sym} 2520 -1940 0 0 {name=l2 lab=GND
value=\{IOVDD\}}
C {devices/lab_wire.sym} 2520 -2080 3 1 {name=p26 sig_type=std_logic lab=VIO}
C {devices/lab_wire.sym} 380 -1300 3 1 {name=p8 sig_type=std_logic lab=VIO}
C {devices/lab_wire.sym} 180 -780 0 0 {name=p16 sig_type=std_logic lab=VIO}
C {devices/lab_wire.sym} 380 -160 3 0 {name=p19 sig_type=std_logic lab=VIO}
C {chip_top.sym} 770 -750 0 0 {name=x1}
