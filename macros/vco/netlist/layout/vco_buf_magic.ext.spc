* NGSPICE file created from vco_buf.ext - technology: ihp-sg13g2

.subckt vco_buf VSS VDD vbn_buf rf_out_n rf_out_p vbg_buf rf_p rf_n
X0 rf_out_n a_n4850_2514# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X1 rf_out_p a_368_764# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X2 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X3 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X4 a_n5142_n500# a_368_764# rf_out_p VSS sg13_lv_nmos ad=0.68p pd=4.68u as=0.38p ps=2.38u w=2u l=0.13u
X5 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.85p ps=5.68u w=2.5u l=0.5u
X6 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X7 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X8 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.85p pd=5.68u as=0.475p ps=2.88u w=2.5u l=0.5u
X9 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X10 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X11 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X12 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X13 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X14 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X15 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X16 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X17 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X18 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X19 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X20 a_n5142_n500# a_n4850_2514# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X21 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X22 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X23 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X24 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X25 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X26 a_n5142_n500# a_n4850_2514# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X27 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X28 vbg_buf a_n4850_2514# VSS rhigh l=8u w=0.5u
X29 rf_out_n a_n4850_2514# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X30 a_368_764# rf_n cap_cmim l=10u w=10u
X31 rf_out_n a_n4850_2514# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X32 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X33 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X34 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X35 rf_out_p a_368_764# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.68p ps=4.68u w=2u l=0.13u
X36 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X37 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X38 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X39 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X40 rf_out_n a_n4850_2514# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X41 a_n5142_n500# a_n4850_2514# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X42 a_n5142_n500# a_368_764# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X43 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X44 VDD rf_out_p VSS rppd l=1.65u w=10u
X45 a_n5142_n500# a_n4850_2514# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X46 rf_out_p a_368_764# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X47 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X48 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X49 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X50 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X51 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X52 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X53 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X54 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X55 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X56 VDD rf_out_n VSS rppd l=1.65u w=10u
X57 rf_out_n a_n4850_2514# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.68p ps=4.68u w=2u l=0.13u
X58 a_n5142_n500# a_368_764# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X59 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X60 vbg_buf a_368_764# VSS rhigh l=8u w=0.5u
X61 rf_out_p a_368_764# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X62 a_n4850_2514# rf_p cap_cmim l=10u w=10u
X63 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X64 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X65 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X66 a_n5142_n500# a_368_764# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X67 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X68 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X69 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X70 rf_out_p a_368_764# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X71 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X72 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X73 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X74 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X75 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X76 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X77 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X78 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X79 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X80 a_n5142_n500# a_n4850_2514# rf_out_n VSS sg13_lv_nmos ad=0.68p pd=4.68u as=0.38p ps=2.38u w=2u l=0.13u
X81 a_n5142_n500# a_368_764# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X82 rf_out_n a_n4850_2514# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X83 rf_out_p a_368_764# a_n5142_n500# VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X84 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X85 VSS vbn_buf a_n5142_n500# VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X86 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X87 a_n5142_n500# vbn_buf VSS VSS sg13_lv_nmos ad=0.475p pd=2.88u as=0.475p ps=2.88u w=2.5u l=0.5u
X88 a_n5142_n500# a_n4850_2514# rf_out_n VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
X89 a_n5142_n500# a_368_764# rf_out_p VSS sg13_lv_nmos ad=0.38p pd=2.38u as=0.38p ps=2.38u w=2u l=0.13u
.ends

