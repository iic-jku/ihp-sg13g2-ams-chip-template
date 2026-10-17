* NGSPICE file created from vco_bias.ext - technology: ihp-sg13g2

.subckt vco_bias di_en ibias_100u vbp_core vbg_buf vbn_buf VSS VDD
X0 vbn_buf a_94_n100# VSS VSS sg13_lv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X1 vbg_buf VSS cap_cmim l=20u w=20u
X2 a_94_n100# di_en VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X3 ibias_100u ibias_100u VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X4 VDD vbp_core cap_cmim l=30u w=30u
X5 a_94_n100# di_en VSS VSS sg13_lv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=0.13u
X6 a_2868_1824# vbp_core VSS rhigh l=16u w=0.5u
X7 vbg_buf vbp_core VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=1.7p ps=10.68u w=5u l=0.5u
X8 ibias_100u a_94_n100# VSS VSS sg13_lv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X9 a_2868_1824# ibias_100u VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X10 vbg_buf a_4268_n536# VSS rppd l=8.5u w=0.5u
X11 vbn_buf VSS cap_cmim l=30u w=30u
X12 a_794_n100# a_94_n100# VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
X13 a_4268_n536# a_4268_n536# VSS VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.85p ps=5.68u w=2.5u l=0.5u
X14 a_2868_1824# a_2868_1824# VDD VDD sg13_lv_pmos ad=1.7p pd=10.68u as=1.7p ps=10.68u w=5u l=0.5u
X15 a_794_n100# a_94_n100# VSS VSS sg13_lv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=0.13u
X16 ibias_100u vbn_buf VSS rhigh l=16u w=0.5u
X17 vbp_core a_794_n100# VDD VDD sg13_lv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.13u
.ends

