* NGSPICE file created from vco_bias.ext - technology: ihp-sg13g2

.subckt vco_bias di_en ibias_100u vbn_buf vbg_buf VSS VDD
X0 VSS vbn_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0.38223n ps=0.8305m w=8u l=10u
X1 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X2 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X3 a_4788_n10584# a_4745_n10448# VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X4 a_4400_n11078# a_4400_n11078# VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X5 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X6 vbn_buf ibias_100u VSS rhigh l=32u w=0.5u
X7 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X8 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X9 vbn_buf a_4745_n10448# VSS VSS sg13_lv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X10 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X11 a_4788_n10584# a_4745_n10448# VSS VSS sg13_lv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=0.13u
X12 vbg_buf VSS cap_cmim l=19.1u w=19.5u
X13 ibias_100u a_4745_n10448# VSS VSS sg13_lv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X14 a_4400_n9292# a_5408_n8864# VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=1.7p ps=10.68u w=5u l=0.5u
X15 VDD VDD VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=45.026p ps=0.22748m w=1u l=0.13u
X16 a_4745_n10448# di_en VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X17 a_4745_n10448# di_en VSS VSS sg13_lv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=0.13u
X18 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X19 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X20 ibias_100u ibias_100u VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X21 VSS vbg_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X22 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X23 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X24 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X25 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X26 a_5408_n8864# a_5408_n8864# VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=1.7p ps=10.68u w=5u l=0.5u
X27 VDD VDD VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=0 ps=0 w=5u l=0.5u
X28 vbg_buf a_4400_n9292# VSS rhigh l=32u w=0.5u
X29 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X30 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X31 VSS VSS VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0 ps=0 w=2.5u l=0.5u
X32 VDD VDD VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=0 ps=0 w=5u l=0.5u
X33 VSS VSS VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0 ps=0 w=2.5u l=0.5u
X34 VSS vbn_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X35 a_4400_n9292# a_4400_n11078# VSS rppd l=8.5u w=0.5u
X36 a_5408_n8864# ibias_100u VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X37 vbg_buf VSS cap_cmim l=7.28u w=13.6u
X38 VSS vbg_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X39 a_5408_n8864# a_4788_n10584# VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X40 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X41 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X42 VDD VDD VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=0 ps=0 w=5u l=0.5u
.ends

