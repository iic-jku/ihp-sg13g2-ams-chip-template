* NGSPICE file created from vco_bias.ext - technology: ihp-sg13g2

.subckt vco_bias di_en ibias_100u vbn_buf vbg_buf VSS VDD
X0 VSS vbn_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0.33288n ps=0.76406m w=8u l=10u
X1 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X2 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X3 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X4 a_4268_n12616# a_4268_n12616# VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X5 ibias_100u vbn_buf VSS rhigh l=32u w=0.5u
X6 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X7 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X8 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X9 a_794_n12180# a_94_n12180# VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X10 a_1494_n10160# a_794_n12180# VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X11 ibias_100u a_94_n12180# VSS VSS sg13_lv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X12 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X13 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X14 VSS vbg_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X15 a_1494_n10160# a_1494_n10160# VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=1.7p ps=10.68u w=5u l=0.5u
X16 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X17 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X18 a_94_n12180# di_en VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X19 a_1494_n10160# ibias_100u VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X20 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X21 VSS vbg_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X22 a_794_n12180# a_94_n12180# VSS VSS sg13_lv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=0.13u
X23 a_314_n13910# vbg_buf VSS rhigh l=32u w=0.5u
X24 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X25 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X26 ibias_100u ibias_100u VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X27 vbn_buf a_94_n12180# VSS VSS sg13_lv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X28 VSS vbn_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X29 a_314_n13910# a_4268_n12616# VSS rppd l=8.5u w=0.5u
X30 a_314_n13910# a_1494_n10160# VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=1.7p ps=10.68u w=5u l=0.5u
X31 a_94_n12180# di_en VSS VSS sg13_lv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=0.13u
X32 VSS vbg_buf VSS VSS sg13_lv_nmos ad=2.72p pd=16.68u as=0 ps=0 w=8u l=10u
X33 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
X34 VSS vbn_buf VSS VSS sg13_lv_nmos ad=1.52p pd=8.38u as=0 ps=0 w=8u l=10u
.ends

