module counter_top (clock_i,
    enable_i,
    reset_n_i,
    VDD,
    VSS,
    counter_value_o);
 input clock_i;
 input enable_i;
 input reset_n_i;
 inout VDD;
 inout VSS;
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

 sg13g2_hv_fill_8 FILLER_0_106 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_114 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_122 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_130 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_138 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_14 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_0_146 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_0_155 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_0_159 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_164 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_172 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_180 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_188 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_196 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_204 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_212 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_22 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_220 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_228 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_236 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_244 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_252 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_260 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_0_268 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_0_272 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_280 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_288 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_296 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_30 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_304 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_312 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_320 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_328 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_336 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_344 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_352 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_360 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_368 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_376 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_38 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_384 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_50 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_58 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_6 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_66 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_74 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_82 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_90 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_0_98 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_0 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_104 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_112 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_120 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_128 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_195 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_1_203 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_1_260 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_1_286 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_333 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_341 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_349 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_1_35 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_357 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_365 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_373 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_381 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_1_389 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_1_391 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_1_8 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_80 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_88 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_1_96 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_0 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_104 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_112 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_2_114 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_136 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_144 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_152 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_16 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_160 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_168 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_176 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_184 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_192 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_2_200 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_228 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_236 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_24 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_244 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_259 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_267 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_275 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_283 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_291 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_302 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_310 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_318 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_32 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_326 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_334 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_342 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_350 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_358 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_366 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_374 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_382 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_390 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_40 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_48 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_56 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_64 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_72 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_8 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_80 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_88 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_2_96 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_140 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_148 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_3_156 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_3_160 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_165 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_3_173 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_215 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_223 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_231 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_239 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_3_247 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_289 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_297 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_305 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_31 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_313 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_321 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_329 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_337 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_345 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_353 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_361 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_369 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_377 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_385 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_39 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_47 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_55 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_3_6 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_3_8 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_81 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_3_89 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_3_97 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_3_99 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_0 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_133 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_4_141 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_4_145 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_4_219 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_4_221 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_243 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_4_251 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_4_288 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_332 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_340 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_348 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_356 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_364 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_372 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_380 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_4_388 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_4_59 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_4_67 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_4_8 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_4_85 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_4_89 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_0 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_102 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_110 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_5_12 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_123 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_131 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_139 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_147 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_155 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_163 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_167 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_175 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_183 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_189 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_19 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_197 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_205 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_213 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_227 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_23 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_235 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_243 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_251 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_259 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_267 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_271 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_279 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_287 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_29 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_295 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_301 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_309 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_317 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_331 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_339 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_347 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_355 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_363 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_37 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_371 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_375 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_383 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_5_391 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_45 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_53 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_61 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_71 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_8 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_8 FILLER_5_86 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_94 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and4_1 _41_ (.A(net5),
    .B(net1),
    .C(net4),
    .D(net3),
    .X(_08_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_8 _42_ (.A(_08_),
    .X(_09_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_xor2_1 _43_ (.B(_09_),
    .A(net6),
    .X(_10_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _44_ (.A(net2),
    .B(_10_),
    .X(_00_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand2_1 _45_ (.Y(_11_),
    .A(net7),
    .B(net2),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_a21oi_1 _46_ (.VSS(VSS),
    .VDD(VDD),
    .A1(net6),
    .A2(_09_),
    .Y(_12_),
    .B1(_11_));
 sg13g2_hv_inv_1 _47_ (.VDD(VDD),
    .Y(_13_),
    .A(net7),
    .VSS(VSS));
 sg13g2_hv_nand4_1 _48_ (.B(net6),
    .C(net2),
    .A(_13_),
    .Y(_14_),
    .VDD(VDD),
    .VSS(VSS),
    .D(_09_));
 sg13g2_hv_nand2b_1 _49_ (.Y(_01_),
    .B(_14_),
    .A_N(_12_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_2 _50_ (.A(net7),
    .B(net6),
    .X(_15_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand2_1 _51_ (.Y(_16_),
    .A(net8),
    .B(net2),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_a21oi_1 _52_ (.VSS(VSS),
    .VDD(VDD),
    .A1(_09_),
    .A2(_15_),
    .Y(_17_),
    .B1(_16_));
 sg13g2_hv_inv_1 _53_ (.VDD(VDD),
    .Y(_18_),
    .A(net8),
    .VSS(VSS));
 sg13g2_hv_nand4_1 _54_ (.B(net2),
    .C(_09_),
    .A(_18_),
    .Y(_19_),
    .VDD(VDD),
    .VSS(VSS),
    .D(_15_));
 sg13g2_hv_nand2b_1 _55_ (.Y(_02_),
    .B(_19_),
    .A_N(_17_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nor2b_1 _56_ (.A(net9),
    .B_N(net2),
    .Y(_20_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _57_ (.A(net9),
    .B(net2),
    .X(_21_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand3_1 _58_ (.B(_09_),
    .C(_15_),
    .A(net8),
    .Y(_22_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_mux2_1 _59_ (.A0(_20_),
    .A1(_21_),
    .S(_22_),
    .X(_03_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and4_1 _60_ (.A(net9),
    .B(net8),
    .C(net7),
    .D(net6),
    .X(_23_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand2_1 _61_ (.Y(_24_),
    .A(net10),
    .B(net2),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_a21oi_1 _62_ (.VSS(VSS),
    .VDD(VDD),
    .A1(_09_),
    .A2(_23_),
    .Y(_25_),
    .B1(_24_));
 sg13g2_hv_inv_1 _63_ (.VDD(VDD),
    .Y(_26_),
    .A(net10),
    .VSS(VSS));
 sg13g2_hv_nand4_1 _64_ (.B(net2),
    .C(_09_),
    .A(_26_),
    .Y(_27_),
    .VDD(VDD),
    .VSS(VSS),
    .D(_23_));
 sg13g2_hv_nand2b_1 _65_ (.Y(_04_),
    .B(_27_),
    .A_N(_25_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_xor2_1 _66_ (.B(net3),
    .A(net1),
    .X(_28_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _67_ (.A(net2),
    .B(_28_),
    .X(_05_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand2_1 _68_ (.Y(_29_),
    .A(net1),
    .B(net3),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_xnor2_1 _69_ (.Y(_30_),
    .A(net4),
    .B(_29_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _70_ (.A(net2),
    .B(_30_),
    .X(_06_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand3_1 _71_ (.B(net4),
    .C(net3),
    .A(net1),
    .Y(_31_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_xnor2_1 _72_ (.Y(_32_),
    .A(net5),
    .B(_31_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _73_ (.A(net2),
    .B(_32_),
    .X(_07_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_dfrbpq_1 _74_ (.RESET_B(net16),
    .VSS(VSS),
    .VDD(VDD),
    .D(_02_),
    .Q(net8),
    .CLK(clknet_1_1__leaf_clock_i));
 sg13g2_hv_tiehi _74__17 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net16));
 sg13g2_hv_dfrbpq_1 _75_ (.RESET_B(net14),
    .VSS(VSS),
    .VDD(VDD),
    .D(_03_),
    .Q(net9),
    .CLK(clknet_1_1__leaf_clock_i));
 sg13g2_hv_tiehi _75__15 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net14));
 sg13g2_hv_dfrbpq_1 _76_ (.RESET_B(net12),
    .VSS(VSS),
    .VDD(VDD),
    .D(_04_),
    .Q(net10),
    .CLK(clknet_1_1__leaf_clock_i));
 sg13g2_hv_tiehi _76__13 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net12));
 sg13g2_hv_dfrbpq_1 _77_ (.RESET_B(net17),
    .VSS(VSS),
    .VDD(VDD),
    .D(_05_),
    .Q(net3),
    .CLK(clknet_1_0__leaf_clock_i));
 sg13g2_hv_tiehi _77__18 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net17));
 sg13g2_hv_dfrbpq_1 _78_ (.RESET_B(net13),
    .VSS(VSS),
    .VDD(VDD),
    .D(_06_),
    .Q(net4),
    .CLK(clknet_1_0__leaf_clock_i));
 sg13g2_hv_tiehi _78__14 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net13));
 sg13g2_hv_dfrbpq_1 _79_ (.RESET_B(net15),
    .VSS(VSS),
    .VDD(VDD),
    .D(_07_),
    .Q(net5),
    .CLK(clknet_1_0__leaf_clock_i));
 sg13g2_hv_tiehi _79__16 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net15));
 sg13g2_hv_dfrbpq_1 _80_ (.RESET_B(net11),
    .VSS(VSS),
    .VDD(VDD),
    .D(_00_),
    .Q(net6),
    .CLK(clknet_1_0__leaf_clock_i));
 sg13g2_hv_tiehi _80__12 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net11));
 sg13g2_hv_dfrbpq_1 _81_ (.RESET_B(net),
    .VSS(VSS),
    .VDD(VDD),
    .D(_01_),
    .Q(net7),
    .CLK(clknet_1_1__leaf_clock_i));
 sg13g2_hv_tiehi _81__11 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net));
 sg13g2_hv_buf_16 clkbuf_0_clock_i (.X(clknet_0_clock_i),
    .A(clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_16 clkbuf_1_0__f_clock_i (.X(clknet_1_0__leaf_clock_i),
    .A(clknet_0_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_16 clkbuf_1_1__f_clock_i (.X(clknet_1_1__leaf_clock_i),
    .A(clknet_0_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 input1 (.A(enable_i),
    .X(net1),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 input2 (.A(reset_n_i),
    .X(net2),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 output10 (.A(net10),
    .X(counter_value_o[7]),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 output3 (.A(net3),
    .X(counter_value_o[0]),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 output4 (.A(net4),
    .X(counter_value_o[1]),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 output5 (.A(net5),
    .X(counter_value_o[2]),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 output6 (.A(net6),
    .X(counter_value_o[3]),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 output7 (.A(net7),
    .X(counter_value_o[4]),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 output8 (.A(net8),
    .X(counter_value_o[5]),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_1 output9 (.A(net9),
    .X(counter_value_o[6]),
    .VDD(VDD),
    .VSS(VSS));
endmodule
