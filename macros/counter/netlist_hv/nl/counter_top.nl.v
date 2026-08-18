module counter_top (clock_i,
    enable_i,
    reset_n_i,
    counter_value_o);
 input clock_i;
 input enable_i;
 input reset_n_i;
 output [7:0] counter_value_o;

 wire _00_;
 wire _01_;
 wire _02_;
 wire _03_;
 wire _04_;
 wire _05_;
 wire _06_;
 wire _07_;
 wire _08_;
 wire _09_;
 wire _10_;
 wire _11_;
 wire _12_;
 wire _13_;
 wire _14_;
 wire _15_;
 wire _16_;
 wire _17_;
 wire _18_;
 wire _19_;
 wire _20_;
 wire _21_;
 wire _22_;
 wire _23_;
 wire _24_;
 wire _25_;
 wire _26_;
 wire _27_;
 wire _28_;
 wire _29_;
 wire _30_;
 wire _31_;
 wire _32_;
 wire net11;
 wire net12;
 wire net13;
 wire net14;
 wire net15;
 wire net16;
 wire net17;
 wire clknet_0_clock_i;
 wire net3;
 wire net4;
 wire net5;
 wire net6;
 wire net7;
 wire net8;
 wire net9;
 wire net10;
 wire net1;
 wire net2;
 wire net;
 wire clknet_1_0__leaf_clock_i;
 wire clknet_1_1__leaf_clock_i;

 sg13g2_hv_fill_8 FILLER_0_106 ();
 sg13g2_hv_fill_8 FILLER_0_114 ();
 sg13g2_hv_fill_8 FILLER_0_122 ();
 sg13g2_hv_fill_8 FILLER_0_130 ();
 sg13g2_hv_fill_8 FILLER_0_138 ();
 sg13g2_hv_fill_8 FILLER_0_14 ();
 sg13g2_hv_fill_2 FILLER_0_146 ();
 sg13g2_hv_decap_4 FILLER_0_155 ();
 sg13g2_hv_fill_1 FILLER_0_159 ();
 sg13g2_hv_fill_8 FILLER_0_164 ();
 sg13g2_hv_fill_8 FILLER_0_172 ();
 sg13g2_hv_fill_8 FILLER_0_180 ();
 sg13g2_hv_fill_8 FILLER_0_188 ();
 sg13g2_hv_fill_8 FILLER_0_196 ();
 sg13g2_hv_fill_8 FILLER_0_204 ();
 sg13g2_hv_fill_8 FILLER_0_212 ();
 sg13g2_hv_fill_8 FILLER_0_22 ();
 sg13g2_hv_fill_8 FILLER_0_220 ();
 sg13g2_hv_fill_8 FILLER_0_228 ();
 sg13g2_hv_fill_8 FILLER_0_236 ();
 sg13g2_hv_fill_8 FILLER_0_244 ();
 sg13g2_hv_fill_8 FILLER_0_252 ();
 sg13g2_hv_fill_8 FILLER_0_260 ();
 sg13g2_hv_decap_4 FILLER_0_268 ();
 sg13g2_hv_fill_1 FILLER_0_272 ();
 sg13g2_hv_fill_8 FILLER_0_280 ();
 sg13g2_hv_fill_8 FILLER_0_288 ();
 sg13g2_hv_fill_8 FILLER_0_296 ();
 sg13g2_hv_fill_8 FILLER_0_30 ();
 sg13g2_hv_fill_8 FILLER_0_304 ();
 sg13g2_hv_fill_8 FILLER_0_312 ();
 sg13g2_hv_fill_8 FILLER_0_320 ();
 sg13g2_hv_fill_8 FILLER_0_328 ();
 sg13g2_hv_fill_8 FILLER_0_336 ();
 sg13g2_hv_fill_8 FILLER_0_344 ();
 sg13g2_hv_fill_8 FILLER_0_352 ();
 sg13g2_hv_fill_8 FILLER_0_360 ();
 sg13g2_hv_fill_8 FILLER_0_368 ();
 sg13g2_hv_fill_8 FILLER_0_376 ();
 sg13g2_hv_fill_8 FILLER_0_38 ();
 sg13g2_hv_fill_8 FILLER_0_384 ();
 sg13g2_hv_fill_8 FILLER_0_50 ();
 sg13g2_hv_fill_8 FILLER_0_58 ();
 sg13g2_hv_fill_8 FILLER_0_6 ();
 sg13g2_hv_fill_8 FILLER_0_66 ();
 sg13g2_hv_fill_8 FILLER_0_74 ();
 sg13g2_hv_fill_8 FILLER_0_82 ();
 sg13g2_hv_fill_8 FILLER_0_90 ();
 sg13g2_hv_fill_8 FILLER_0_98 ();
 sg13g2_hv_fill_8 FILLER_1_0 ();
 sg13g2_hv_fill_8 FILLER_1_104 ();
 sg13g2_hv_fill_8 FILLER_1_112 ();
 sg13g2_hv_fill_8 FILLER_1_120 ();
 sg13g2_hv_fill_8 FILLER_1_128 ();
 sg13g2_hv_fill_8 FILLER_1_195 ();
 sg13g2_hv_decap_4 FILLER_1_203 ();
 sg13g2_hv_fill_1 FILLER_1_260 ();
 sg13g2_hv_decap_4 FILLER_1_286 ();
 sg13g2_hv_fill_8 FILLER_1_333 ();
 sg13g2_hv_fill_8 FILLER_1_341 ();
 sg13g2_hv_fill_8 FILLER_1_349 ();
 sg13g2_hv_fill_2 FILLER_1_35 ();
 sg13g2_hv_fill_8 FILLER_1_357 ();
 sg13g2_hv_fill_8 FILLER_1_365 ();
 sg13g2_hv_fill_8 FILLER_1_373 ();
 sg13g2_hv_fill_8 FILLER_1_381 ();
 sg13g2_hv_fill_2 FILLER_1_389 ();
 sg13g2_hv_fill_1 FILLER_1_391 ();
 sg13g2_hv_decap_4 FILLER_1_8 ();
 sg13g2_hv_fill_8 FILLER_1_80 ();
 sg13g2_hv_fill_8 FILLER_1_88 ();
 sg13g2_hv_fill_8 FILLER_1_96 ();
 sg13g2_hv_fill_8 FILLER_2_0 ();
 sg13g2_hv_fill_8 FILLER_2_104 ();
 sg13g2_hv_fill_2 FILLER_2_112 ();
 sg13g2_hv_fill_1 FILLER_2_114 ();
 sg13g2_hv_fill_8 FILLER_2_136 ();
 sg13g2_hv_fill_8 FILLER_2_144 ();
 sg13g2_hv_fill_8 FILLER_2_152 ();
 sg13g2_hv_fill_8 FILLER_2_16 ();
 sg13g2_hv_fill_8 FILLER_2_160 ();
 sg13g2_hv_fill_8 FILLER_2_168 ();
 sg13g2_hv_fill_8 FILLER_2_176 ();
 sg13g2_hv_fill_8 FILLER_2_184 ();
 sg13g2_hv_fill_8 FILLER_2_192 ();
 sg13g2_hv_fill_1 FILLER_2_200 ();
 sg13g2_hv_fill_8 FILLER_2_228 ();
 sg13g2_hv_fill_8 FILLER_2_236 ();
 sg13g2_hv_fill_8 FILLER_2_24 ();
 sg13g2_hv_fill_8 FILLER_2_244 ();
 sg13g2_hv_fill_8 FILLER_2_259 ();
 sg13g2_hv_fill_8 FILLER_2_267 ();
 sg13g2_hv_fill_8 FILLER_2_275 ();
 sg13g2_hv_fill_8 FILLER_2_283 ();
 sg13g2_hv_decap_8 FILLER_2_291 ();
 sg13g2_hv_fill_8 FILLER_2_302 ();
 sg13g2_hv_fill_8 FILLER_2_310 ();
 sg13g2_hv_fill_8 FILLER_2_318 ();
 sg13g2_hv_fill_8 FILLER_2_32 ();
 sg13g2_hv_fill_8 FILLER_2_326 ();
 sg13g2_hv_fill_8 FILLER_2_334 ();
 sg13g2_hv_fill_8 FILLER_2_342 ();
 sg13g2_hv_fill_8 FILLER_2_350 ();
 sg13g2_hv_fill_8 FILLER_2_358 ();
 sg13g2_hv_fill_8 FILLER_2_366 ();
 sg13g2_hv_fill_8 FILLER_2_374 ();
 sg13g2_hv_fill_8 FILLER_2_382 ();
 sg13g2_hv_fill_2 FILLER_2_390 ();
 sg13g2_hv_fill_8 FILLER_2_40 ();
 sg13g2_hv_fill_8 FILLER_2_48 ();
 sg13g2_hv_fill_8 FILLER_2_56 ();
 sg13g2_hv_fill_8 FILLER_2_64 ();
 sg13g2_hv_fill_8 FILLER_2_72 ();
 sg13g2_hv_fill_8 FILLER_2_8 ();
 sg13g2_hv_fill_8 FILLER_2_80 ();
 sg13g2_hv_fill_8 FILLER_2_88 ();
 sg13g2_hv_fill_8 FILLER_2_96 ();
 sg13g2_hv_fill_8 FILLER_3_140 ();
 sg13g2_hv_fill_8 FILLER_3_148 ();
 sg13g2_hv_decap_4 FILLER_3_156 ();
 sg13g2_hv_fill_1 FILLER_3_160 ();
 sg13g2_hv_fill_8 FILLER_3_165 ();
 sg13g2_hv_fill_2 FILLER_3_173 ();
 sg13g2_hv_fill_8 FILLER_3_215 ();
 sg13g2_hv_fill_8 FILLER_3_223 ();
 sg13g2_hv_fill_8 FILLER_3_231 ();
 sg13g2_hv_fill_8 FILLER_3_239 ();
 sg13g2_hv_fill_2 FILLER_3_247 ();
 sg13g2_hv_fill_8 FILLER_3_289 ();
 sg13g2_hv_fill_8 FILLER_3_297 ();
 sg13g2_hv_fill_8 FILLER_3_305 ();
 sg13g2_hv_fill_8 FILLER_3_31 ();
 sg13g2_hv_fill_8 FILLER_3_313 ();
 sg13g2_hv_fill_8 FILLER_3_321 ();
 sg13g2_hv_fill_8 FILLER_3_329 ();
 sg13g2_hv_fill_8 FILLER_3_337 ();
 sg13g2_hv_fill_8 FILLER_3_345 ();
 sg13g2_hv_fill_8 FILLER_3_353 ();
 sg13g2_hv_fill_8 FILLER_3_361 ();
 sg13g2_hv_fill_8 FILLER_3_369 ();
 sg13g2_hv_fill_8 FILLER_3_377 ();
 sg13g2_hv_decap_8 FILLER_3_385 ();
 sg13g2_hv_fill_8 FILLER_3_39 ();
 sg13g2_hv_fill_8 FILLER_3_47 ();
 sg13g2_hv_decap_8 FILLER_3_55 ();
 sg13g2_hv_fill_2 FILLER_3_6 ();
 sg13g2_hv_fill_1 FILLER_3_8 ();
 sg13g2_hv_fill_8 FILLER_3_81 ();
 sg13g2_hv_fill_8 FILLER_3_89 ();
 sg13g2_hv_fill_2 FILLER_3_97 ();
 sg13g2_hv_fill_1 FILLER_3_99 ();
 sg13g2_hv_fill_8 FILLER_4_0 ();
 sg13g2_hv_fill_8 FILLER_4_133 ();
 sg13g2_hv_decap_4 FILLER_4_141 ();
 sg13g2_hv_fill_2 FILLER_4_145 ();
 sg13g2_hv_fill_2 FILLER_4_219 ();
 sg13g2_hv_fill_1 FILLER_4_221 ();
 sg13g2_hv_fill_8 FILLER_4_243 ();
 sg13g2_hv_decap_4 FILLER_4_251 ();
 sg13g2_hv_fill_1 FILLER_4_288 ();
 sg13g2_hv_fill_8 FILLER_4_332 ();
 sg13g2_hv_fill_8 FILLER_4_340 ();
 sg13g2_hv_fill_8 FILLER_4_348 ();
 sg13g2_hv_fill_8 FILLER_4_356 ();
 sg13g2_hv_fill_8 FILLER_4_364 ();
 sg13g2_hv_fill_8 FILLER_4_372 ();
 sg13g2_hv_fill_8 FILLER_4_380 ();
 sg13g2_hv_decap_4 FILLER_4_388 ();
 sg13g2_hv_fill_8 FILLER_4_59 ();
 sg13g2_hv_fill_2 FILLER_4_67 ();
 sg13g2_hv_fill_1 FILLER_4_8 ();
 sg13g2_hv_decap_4 FILLER_4_85 ();
 sg13g2_hv_fill_1 FILLER_4_89 ();
 sg13g2_hv_fill_8 FILLER_5_0 ();
 sg13g2_hv_fill_8 FILLER_5_102 ();
 sg13g2_hv_decap_8 FILLER_5_110 ();
 sg13g2_hv_fill_1 FILLER_5_12 ();
 sg13g2_hv_fill_8 FILLER_5_123 ();
 sg13g2_hv_fill_8 FILLER_5_131 ();
 sg13g2_hv_fill_8 FILLER_5_139 ();
 sg13g2_hv_fill_8 FILLER_5_147 ();
 sg13g2_hv_fill_8 FILLER_5_155 ();
 sg13g2_hv_decap_4 FILLER_5_163 ();
 sg13g2_hv_fill_2 FILLER_5_167 ();
 sg13g2_hv_fill_8 FILLER_5_175 ();
 sg13g2_hv_fill_2 FILLER_5_183 ();
 sg13g2_hv_fill_8 FILLER_5_189 ();
 sg13g2_hv_decap_4 FILLER_5_19 ();
 sg13g2_hv_fill_8 FILLER_5_197 ();
 sg13g2_hv_fill_8 FILLER_5_205 ();
 sg13g2_hv_fill_8 FILLER_5_213 ();
 sg13g2_hv_fill_8 FILLER_5_227 ();
 sg13g2_hv_fill_2 FILLER_5_23 ();
 sg13g2_hv_fill_8 FILLER_5_235 ();
 sg13g2_hv_fill_8 FILLER_5_243 ();
 sg13g2_hv_fill_8 FILLER_5_251 ();
 sg13g2_hv_fill_8 FILLER_5_259 ();
 sg13g2_hv_decap_4 FILLER_5_267 ();
 sg13g2_hv_fill_2 FILLER_5_271 ();
 sg13g2_hv_fill_8 FILLER_5_279 ();
 sg13g2_hv_fill_8 FILLER_5_287 ();
 sg13g2_hv_fill_8 FILLER_5_29 ();
 sg13g2_hv_fill_2 FILLER_5_295 ();
 sg13g2_hv_fill_8 FILLER_5_301 ();
 sg13g2_hv_fill_8 FILLER_5_309 ();
 sg13g2_hv_fill_8 FILLER_5_317 ();
 sg13g2_hv_fill_8 FILLER_5_331 ();
 sg13g2_hv_fill_8 FILLER_5_339 ();
 sg13g2_hv_fill_8 FILLER_5_347 ();
 sg13g2_hv_fill_8 FILLER_5_355 ();
 sg13g2_hv_fill_8 FILLER_5_363 ();
 sg13g2_hv_fill_8 FILLER_5_37 ();
 sg13g2_hv_decap_4 FILLER_5_371 ();
 sg13g2_hv_fill_2 FILLER_5_375 ();
 sg13g2_hv_fill_8 FILLER_5_383 ();
 sg13g2_hv_fill_1 FILLER_5_391 ();
 sg13g2_hv_fill_8 FILLER_5_45 ();
 sg13g2_hv_fill_8 FILLER_5_53 ();
 sg13g2_hv_decap_4 FILLER_5_61 ();
 sg13g2_hv_fill_8 FILLER_5_71 ();
 sg13g2_hv_decap_4 FILLER_5_8 ();
 sg13g2_hv_fill_8 FILLER_5_86 ();
 sg13g2_hv_decap_4 FILLER_5_94 ();
 sg13g2_hv_and4_1 _41_ (.A(net5),
    .B(net1),
    .C(net4),
    .D(net3),
    .X(_08_));
 sg13g2_hv_buf_8 _42_ (.A(_08_),
    .X(_09_));
 sg13g2_hv_xor2_1 _43_ (.B(_09_),
    .A(net6),
    .X(_10_));
 sg13g2_hv_and2_1 _44_ (.A(net2),
    .B(_10_),
    .X(_00_));
 sg13g2_hv_nand2_1 _45_ (.Y(_11_),
    .A(net7),
    .B(net2));
 sg13g2_hv_a21oi_1 _46_ (.A1(net6),
    .A2(_09_),
    .Y(_12_),
    .B1(_11_));
 sg13g2_hv_inv_1 _47_ (.Y(_13_),
    .A(net7));
 sg13g2_hv_nand4_1 _48_ (.B(net6),
    .C(net2),
    .A(_13_),
    .Y(_14_),
    .D(_09_));
 sg13g2_hv_nand2b_1 _49_ (.Y(_01_),
    .B(_14_),
    .A_N(_12_));
 sg13g2_hv_and2_2 _50_ (.A(net7),
    .B(net6),
    .X(_15_));
 sg13g2_hv_nand2_1 _51_ (.Y(_16_),
    .A(net8),
    .B(net2));
 sg13g2_hv_a21oi_1 _52_ (.A1(_09_),
    .A2(_15_),
    .Y(_17_),
    .B1(_16_));
 sg13g2_hv_inv_1 _53_ (.Y(_18_),
    .A(net8));
 sg13g2_hv_nand4_1 _54_ (.B(net2),
    .C(_09_),
    .A(_18_),
    .Y(_19_),
    .D(_15_));
 sg13g2_hv_nand2b_1 _55_ (.Y(_02_),
    .B(_19_),
    .A_N(_17_));
 sg13g2_hv_nor2b_1 _56_ (.A(net9),
    .B_N(net2),
    .Y(_20_));
 sg13g2_hv_and2_1 _57_ (.A(net9),
    .B(net2),
    .X(_21_));
 sg13g2_hv_nand3_1 _58_ (.B(_09_),
    .C(_15_),
    .A(net8),
    .Y(_22_));
 sg13g2_hv_mux2_1 _59_ (.A0(_20_),
    .A1(_21_),
    .S(_22_),
    .X(_03_));
 sg13g2_hv_and4_1 _60_ (.A(net9),
    .B(net8),
    .C(net7),
    .D(net6),
    .X(_23_));
 sg13g2_hv_nand2_1 _61_ (.Y(_24_),
    .A(net10),
    .B(net2));
 sg13g2_hv_a21oi_1 _62_ (.A1(_09_),
    .A2(_23_),
    .Y(_25_),
    .B1(_24_));
 sg13g2_hv_inv_1 _63_ (.Y(_26_),
    .A(net10));
 sg13g2_hv_nand4_1 _64_ (.B(net2),
    .C(_09_),
    .A(_26_),
    .Y(_27_),
    .D(_23_));
 sg13g2_hv_nand2b_1 _65_ (.Y(_04_),
    .B(_27_),
    .A_N(_25_));
 sg13g2_hv_xor2_1 _66_ (.B(net3),
    .A(net1),
    .X(_28_));
 sg13g2_hv_and2_1 _67_ (.A(net2),
    .B(_28_),
    .X(_05_));
 sg13g2_hv_nand2_1 _68_ (.Y(_29_),
    .A(net1),
    .B(net3));
 sg13g2_hv_xnor2_1 _69_ (.Y(_30_),
    .A(net4),
    .B(_29_));
 sg13g2_hv_and2_1 _70_ (.A(net2),
    .B(_30_),
    .X(_06_));
 sg13g2_hv_nand3_1 _71_ (.B(net4),
    .C(net3),
    .A(net1),
    .Y(_31_));
 sg13g2_hv_xnor2_1 _72_ (.Y(_32_),
    .A(net5),
    .B(_31_));
 sg13g2_hv_and2_1 _73_ (.A(net2),
    .B(_32_),
    .X(_07_));
 sg13g2_hv_dfrbpq_1 _74_ (.RESET_B(net16),
    .D(_02_),
    .Q(net8),
    .CLK(clknet_1_1__leaf_clock_i));
 sg13g2_hv_tiehi _74__17 (.L_HI(net16));
 sg13g2_hv_dfrbpq_1 _75_ (.RESET_B(net14),
    .D(_03_),
    .Q(net9),
    .CLK(clknet_1_1__leaf_clock_i));
 sg13g2_hv_tiehi _75__15 (.L_HI(net14));
 sg13g2_hv_dfrbpq_1 _76_ (.RESET_B(net12),
    .D(_04_),
    .Q(net10),
    .CLK(clknet_1_1__leaf_clock_i));
 sg13g2_hv_tiehi _76__13 (.L_HI(net12));
 sg13g2_hv_dfrbpq_1 _77_ (.RESET_B(net17),
    .D(_05_),
    .Q(net3),
    .CLK(clknet_1_0__leaf_clock_i));
 sg13g2_hv_tiehi _77__18 (.L_HI(net17));
 sg13g2_hv_dfrbpq_1 _78_ (.RESET_B(net13),
    .D(_06_),
    .Q(net4),
    .CLK(clknet_1_0__leaf_clock_i));
 sg13g2_hv_tiehi _78__14 (.L_HI(net13));
 sg13g2_hv_dfrbpq_1 _79_ (.RESET_B(net15),
    .D(_07_),
    .Q(net5),
    .CLK(clknet_1_0__leaf_clock_i));
 sg13g2_hv_tiehi _79__16 (.L_HI(net15));
 sg13g2_hv_dfrbpq_1 _80_ (.RESET_B(net11),
    .D(_00_),
    .Q(net6),
    .CLK(clknet_1_0__leaf_clock_i));
 sg13g2_hv_tiehi _80__12 (.L_HI(net11));
 sg13g2_hv_dfrbpq_1 _81_ (.RESET_B(net),
    .D(_01_),
    .Q(net7),
    .CLK(clknet_1_1__leaf_clock_i));
 sg13g2_hv_tiehi _81__11 (.L_HI(net));
 sg13g2_hv_buf_16 clkbuf_0_clock_i (.X(clknet_0_clock_i),
    .A(clock_i));
 sg13g2_hv_buf_16 clkbuf_1_0__f_clock_i (.X(clknet_1_0__leaf_clock_i),
    .A(clknet_0_clock_i));
 sg13g2_hv_buf_16 clkbuf_1_1__f_clock_i (.X(clknet_1_1__leaf_clock_i),
    .A(clknet_0_clock_i));
 sg13g2_hv_buf_1 input1 (.A(enable_i),
    .X(net1));
 sg13g2_hv_buf_1 input2 (.A(reset_n_i),
    .X(net2));
 sg13g2_hv_buf_1 output10 (.A(net10),
    .X(counter_value_o[7]));
 sg13g2_hv_buf_1 output3 (.A(net3),
    .X(counter_value_o[0]));
 sg13g2_hv_buf_1 output4 (.A(net4),
    .X(counter_value_o[1]));
 sg13g2_hv_buf_1 output5 (.A(net5),
    .X(counter_value_o[2]));
 sg13g2_hv_buf_1 output6 (.A(net6),
    .X(counter_value_o[3]));
 sg13g2_hv_buf_1 output7 (.A(net7),
    .X(counter_value_o[4]));
 sg13g2_hv_buf_1 output8 (.A(net8),
    .X(counter_value_o[5]));
 sg13g2_hv_buf_1 output9 (.A(net9),
    .X(counter_value_o[6]));
endmodule
