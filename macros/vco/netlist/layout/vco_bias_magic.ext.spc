* NGSPICE file created from vco_bias.ext - technology: ihp-sg13g2

.subckt vco_bias di_en en_b vbn_buf vbg_buf VSS VDD
X0 VSS vbn_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0.38223n ps=0.8305m w=8u l=10u
X1 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X2 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X3 a_4788_n10584# en_b VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X4 a_4400_n11078# a_4400_n11078# VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X5 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X6 vbn_buf a_3900_n11998# VSS rhigh l=32u w=0.5u
X7 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X8 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X9 vbn_buf en_b VSS VSS sg13_lv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X10 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X11 a_4788_n10584# en_b VSS VSS sg13_lv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=0.13u
X12 vbg_buf VSS cap_cmim l=19.1u w=17.5u
X13 a_3900_n11998# en_b VSS VSS sg13_lv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X14 a_4400_n9292# a_5408_n8864# VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=1.7p ps=10.68u w=5u l=0.5u
X15 VDD VDD VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=41.581p ps=0.19678m w=1u l=0.13u
X16 en_b di_en VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X17 en_b di_en VSS VSS sg13_lv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=0.13u
X18 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X19 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X20 a_3900_n11998# a_3900_n11998# VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X21 VSS vbg_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X22 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X23 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X24 a_3900_n9292# en_b VDD VDD sg13_lv_pmos ad=0.68p pd=4.68u as=0.68p ps=4.68u w=2u l=0.13u
X25 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X26 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X27 a_5408_n8864# a_5408_n8864# VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=1.7p ps=10.68u w=5u l=0.5u
X28 VDD VDD VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=0 ps=0 w=5u l=0.5u
X29 vbg_buf a_4400_n9292# VSS rhigh l=32u w=0.5u
X30 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X31 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X32 VSS VSS VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0 ps=0 w=2.5u l=0.5u
X33 VSS VSS VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0 ps=0 w=2.5u l=0.5u
X34 VSS vbn_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X35 a_4400_n9292# a_4400_n11078# VSS rppd l=8.5u w=0.5u
X36 a_5408_n8864# a_3900_n11998# VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X37 vbg_buf VSS cap_cmim l=7.28u w=13.6u
X38 VSS vbg_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X39 a_5408_n8864# a_4788_n10584# VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X40 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X41 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X42 a_3900_n9292# a_3900_n11998# VSS rppd l=13.1u w=0.5u
X43 VDD VDD VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=0 ps=0 w=5u l=0.5u
.ends

