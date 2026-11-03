* NGSPICE file created from vco_buf.ext - technology: ihp-sg13g2

.subckt vco_buf VSS VDD vbn_buf rf_out_n rf_out_p vbg_buf rf_p rf_n
X0 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=1.7p ps=10.68u w=5u l=0.5u
X1 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X2 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X3 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X4 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X5 a_n2502_n1000# a_n4850_2214# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X6 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X7 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X8 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X9 vbg_buf a_n4850_2214# VSS rhigh l=8u w=0.5u
X10 a_n2502_n1000# a_n4850_2214# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X11 rf_out_n a_n4850_2214# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X12 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X13 rf_out_n a_n4850_2214# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X14 a_n2502_n1000# a_n4850_2214# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X15 rf_out_p a_368_464# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.68p ps=4.68u w=2u l=0.13u
X16 rf_out_n a_n4850_2214# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X17 a_n2502_n1000# a_368_464# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X18 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X19 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X20 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X21 VDD rf_out_p VSS rppd l=1.65u w=10u
X22 rf_out_p a_368_464# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X23 a_n2502_n1000# a_n4850_2214# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X24 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X25 a_368_464# rf_n cap_cmim l=10u w=10u
X26 VDD rf_out_n VSS rppd l=1.65u w=10u
X27 a_n2502_n1000# a_368_464# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X28 rf_out_n a_n4850_2214# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.68p ps=4.68u w=2u l=0.13u
X29 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X30 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X31 vbg_buf a_368_464# VSS rhigh l=8u w=0.5u
X32 rf_out_p a_368_464# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X33 a_n2502_n1000# a_368_464# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X34 rf_out_p a_368_464# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X35 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X36 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X37 a_n4850_2214# rf_p cap_cmim l=10u w=10u
X38 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X39 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X40 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X41 a_n2502_n1000# a_n4850_2214# rf_out_n VSS sg13_lv_nmos ad=0.68p pd=4.68u as=0.38p ps=2.38u w=2u l=0.13u
X42 a_n2502_n1000# a_368_464# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X43 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X44 rf_out_n a_n4850_2214# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X45 rf_out_p a_368_464# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X46 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X47 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X48 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X49 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X50 a_n2502_n1000# vbn_buf VSS VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X51 a_n2502_n1000# a_n4850_2214# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X52 a_n2502_n1000# a_368_464# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X53 rf_out_n a_n4850_2214# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X54 rf_out_p a_368_464# a_n2502_n1000# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X55 a_n2502_n1000# a_368_464# rf_out_p VSS sg13_lv_nmos ad=0.68p pd=4.68u as=0.38p ps=2.38u w=2u l=0.13u
X56 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X57 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X58 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=0.95p pd=5.38u as=0.95p ps=5.38u w=5u l=0.5u
X59 VSS vbn_buf a_n2502_n1000# VSS sg13_lv_nmos ad=1.7p pd=10.68u as=0.95p ps=5.38u w=5u l=0.5u
.ends

