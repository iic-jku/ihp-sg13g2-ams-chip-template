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

 wire _000_;
 wire _001_;
 wire _002_;
 wire _003_;
 wire _004_;
 wire _005_;
 wire _006_;
 wire _007_;
 wire _008_;
 wire _009_;
 wire _010_;
 wire _011_;
 wire _012_;
 wire _013_;
 wire _014_;
 wire _015_;
 wire _016_;
 wire _017_;
 wire _018_;
 wire _019_;
 wire _020_;
 wire _021_;
 wire _022_;
 wire _023_;
 wire _024_;
 wire _025_;
 wire _026_;
 wire _027_;
 wire _028_;
 wire _029_;
 wire _030_;
 wire net29;
 wire net30;
 wire net31;
 wire net32;
 wire net33;
 wire net34;
 wire net35;
 wire net36;
 wire net37;
 wire net38;
 wire net39;
 wire net40;
 wire net41;
 wire net42;
 wire net43;
 wire clknet_0_clock_i;
 wire net13;
 wire net14;
 wire net15;
 wire net16;
 wire net17;
 wire net18;
 wire net19;
 wire net20;
 wire net21;
 wire net22;
 wire net23;
 wire net24;
 wire net25;
 wire net26;
 wire net27;
 wire net28;
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
 wire net11;
 wire net12;
 wire net;
 wire clknet_1_0__leaf_clock_i;
 wire clknet_1_1__leaf_clock_i;

 sg13g2_hv_decap_8 FILLER_0_106 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_113 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_120 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_127 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_13 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_134 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_141 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_148 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_155 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_162 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_169 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_176 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_183 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_190 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_197 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_0_20 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_204 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_211 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_218 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_0_225 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_230 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_237 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_244 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_251 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_258 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_265 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_272 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_279 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_0_286 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_29 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_292 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_0_299 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_0_303 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_313 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_320 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_327 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_334 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_341 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_348 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_355 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_36 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_362 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_369 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_376 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_383 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_0_390 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_43 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_50 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_57 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_6 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_64 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_71 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_78 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_85 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_92 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_0_99 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_1_0 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_1_159 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_1_161 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_1_320 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_1_324 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_1_387 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_1_391 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_1_7 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_1_93 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_0 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_108 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_115 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_122 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_129 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_2_136 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_14 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_2_140 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_2_145 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_2_153 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_157 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_175 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_181 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_188 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_195 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_202 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_209 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_2_21 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_216 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_222 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_229 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_2_236 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_245 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_25 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_252 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_259 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_266 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_2_273 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_277 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_290 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_297 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_304 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_311 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_318 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_325 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_335 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_342 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_349 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_35 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_356 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_363 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_2_374 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_382 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_389 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_2_391 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_42 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_49 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_56 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_63 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_7 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_70 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_76 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_2_83 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_2_90 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_2_92 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_107 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_3_114 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_3_13 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_164 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_171 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_178 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_185 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_3_192 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_3_20 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_237 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_244 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_251 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_3_258 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_300 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_319 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_326 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_333 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_34 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_340 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_347 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_354 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_361 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_368 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_375 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_382 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_3_389 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_3_391 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_41 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_48 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_55 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_6 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_62 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_69 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_3_76 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_3_83 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_4_0 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_4_103 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_4_110 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_4_135 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_4_142 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_4_170 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_4_243 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_4_245 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_4_279 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_4_327 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_4_391 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_4_7 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_4_89 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_0 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_104 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_11 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_111 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_115 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_123 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_130 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_137 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_144 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_151 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_158 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_165 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_183 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_19 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_190 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_197 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_204 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_211 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_5_215 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_5_220 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_227 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_234 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_241 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_248 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_255 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_262 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_269 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_279 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_28 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_286 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_293 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_300 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_307 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_314 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_321 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_339 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_346 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_353 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_360 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_367 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_371 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_38 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_387 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_1 FILLER_5_391 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_45 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_52 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_59 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_fill_2 FILLER_5_63 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_7 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_4 FILLER_5_75 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_83 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_90 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_decap_8 FILLER_5_97 (.VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_xor2_1 _063_ (.B(net1),
    .A(net3),
    .X(_008_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _064_ (.A(net11),
    .B(_008_),
    .X(_003_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand2_1 _065_ (.Y(_009_),
    .A(net3),
    .B(net1),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_xnor2_1 _066_ (.Y(_010_),
    .A(net4),
    .B(_009_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _067_ (.A(net11),
    .B(_010_),
    .X(_004_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand3_1 _068_ (.B(net3),
    .C(net1),
    .A(net4),
    .Y(_011_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_xnor2_1 _069_ (.Y(_012_),
    .A(net5),
    .B(_011_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _070_ (.A(net11),
    .B(_012_),
    .X(_005_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and4_1 _071_ (.A(net4),
    .B(net3),
    .C(net5),
    .D(net1),
    .X(_013_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_buf_8 _072_ (.A(_013_),
    .X(_014_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_xor2_1 _073_ (.B(_014_),
    .A(net6),
    .X(_015_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _074_ (.A(net11),
    .B(_015_),
    .X(_006_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand2_1 _075_ (.Y(_016_),
    .A(net11),
    .B(net7),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_a21oi_1 _076_ (.VSS(VSS),
    .VDD(VDD),
    .A1(net6),
    .A2(_014_),
    .Y(_017_),
    .B1(_016_));
 sg13g2_hv_inv_1 _077_ (.VDD(VDD),
    .Y(_018_),
    .A(net7),
    .VSS(VSS));
 sg13g2_hv_nand4_1 _078_ (.B(net6),
    .C(_018_),
    .A(net11),
    .Y(_019_),
    .VDD(VDD),
    .VSS(VSS),
    .D(_014_));
 sg13g2_hv_nand2b_1 _079_ (.Y(_007_),
    .B(_019_),
    .A_N(_017_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_2 _080_ (.A(net6),
    .B(net7),
    .X(_020_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand2_1 _081_ (.Y(_021_),
    .A(net11),
    .B(net8),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_a21oi_1 _082_ (.VSS(VSS),
    .VDD(VDD),
    .A1(_014_),
    .A2(_020_),
    .Y(_022_),
    .B1(_021_));
 sg13g2_hv_inv_1 _083_ (.VDD(VDD),
    .Y(_023_),
    .A(net8),
    .VSS(VSS));
 sg13g2_hv_nand4_1 _084_ (.B(_023_),
    .C(_014_),
    .A(net11),
    .Y(_024_),
    .VDD(VDD),
    .VSS(VSS),
    .D(_020_));
 sg13g2_hv_nand2b_1 _085_ (.Y(_000_),
    .B(_024_),
    .A_N(_022_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nor2b_1 _086_ (.A(net9),
    .B_N(net12),
    .Y(_025_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _087_ (.A(net12),
    .B(net9),
    .X(_026_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand3_1 _088_ (.B(_014_),
    .C(_020_),
    .A(net8),
    .Y(_027_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_mux2_1 _089_ (.A0(_025_),
    .A1(_026_),
    .S(_027_),
    .X(_001_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nor2b_1 _090_ (.A(net10),
    .B_N(net12),
    .Y(_028_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_and2_1 _091_ (.A(net12),
    .B(net10),
    .X(_029_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_nand4_1 _092_ (.B(net9),
    .C(_014_),
    .A(net8),
    .Y(_030_),
    .VDD(VDD),
    .VSS(VSS),
    .D(_020_));
 sg13g2_hv_mux2_1 _093_ (.A0(_028_),
    .A1(_029_),
    .S(_030_),
    .X(_002_),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_sdfbbp_1 _094_ (.Q(net8),
    .RESET_B(net38),
    .SET_B(net39),
    .D(_000_),
    .SCE(net22),
    .SCD(net23),
    .CLK(clknet_1_1__leaf_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_tielo _094__23 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net22));
 sg13g2_hv_tielo _094__24 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net23));
 sg13g2_hv_tiehi _094__39 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net38));
 sg13g2_hv_tiehi _094__40 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net39));
 sg13g2_hv_sdfbbp_1 _095_ (.Q(net9),
    .RESET_B(net42),
    .SET_B(net43),
    .D(_001_),
    .SCE(net26),
    .SCD(net27),
    .CLK(clknet_1_1__leaf_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_tielo _095__27 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net26));
 sg13g2_hv_tielo _095__28 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net27));
 sg13g2_hv_tiehi _095__43 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net42));
 sg13g2_hv_tiehi _095__44 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net43));
 sg13g2_hv_sdfbbp_1 _096_ (.Q(net10),
    .RESET_B(net30),
    .SET_B(net31),
    .D(_002_),
    .SCE(net14),
    .SCD(net15),
    .CLK(clknet_1_1__leaf_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_tielo _096__15 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net14));
 sg13g2_hv_tielo _096__16 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net15));
 sg13g2_hv_tiehi _096__31 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net30));
 sg13g2_hv_tiehi _096__32 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net31));
 sg13g2_hv_sdfbbp_1 _097_ (.Q(net3),
    .RESET_B(net32),
    .SET_B(net33),
    .D(_003_),
    .SCE(net16),
    .SCD(net17),
    .CLK(clknet_1_0__leaf_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_tielo _097__17 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net16));
 sg13g2_hv_tielo _097__18 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net17));
 sg13g2_hv_tiehi _097__33 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net32));
 sg13g2_hv_tiehi _097__34 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net33));
 sg13g2_hv_sdfbbp_1 _098_ (.Q(net4),
    .RESET_B(net40),
    .SET_B(net41),
    .D(_004_),
    .SCE(net24),
    .SCD(net25),
    .CLK(clknet_1_0__leaf_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_tielo _098__25 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net24));
 sg13g2_hv_tielo _098__26 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net25));
 sg13g2_hv_tiehi _098__41 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net40));
 sg13g2_hv_tiehi _098__42 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net41));
 sg13g2_hv_sdfbbp_1 _099_ (.Q(net5),
    .RESET_B(net36),
    .SET_B(net37),
    .D(_005_),
    .SCE(net20),
    .SCD(net21),
    .CLK(clknet_1_0__leaf_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_tielo _099__21 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net20));
 sg13g2_hv_tielo _099__22 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net21));
 sg13g2_hv_tiehi _099__37 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net36));
 sg13g2_hv_tiehi _099__38 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net37));
 sg13g2_hv_sdfbbp_1 _100_ (.Q(net6),
    .RESET_B(net28),
    .SET_B(net29),
    .D(_006_),
    .SCE(net),
    .SCD(net13),
    .CLK(clknet_1_1__leaf_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_tielo _100__13 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net));
 sg13g2_hv_tielo _100__14 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net13));
 sg13g2_hv_tiehi _100__29 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net28));
 sg13g2_hv_tiehi _100__30 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net29));
 sg13g2_hv_sdfbbp_1 _101_ (.Q(net7),
    .RESET_B(net34),
    .SET_B(net35),
    .D(_007_),
    .SCE(net18),
    .SCD(net19),
    .CLK(clknet_1_0__leaf_clock_i),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_tielo _101__19 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net18));
 sg13g2_hv_tielo _101__20 (.VDD(VDD),
    .VSS(VSS),
    .L_LO(net19));
 sg13g2_hv_tiehi _101__35 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net34));
 sg13g2_hv_tiehi _101__36 (.VDD(VDD),
    .VSS(VSS),
    .L_HI(net35));
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
 sg13g2_hv_dlygate4sd2_1 fanout11 (.A(net2),
    .X(net11),
    .VDD(VDD),
    .VSS(VSS));
 sg13g2_hv_dlygate4sd2_1 fanout12 (.A(net2),
    .X(net12),
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
