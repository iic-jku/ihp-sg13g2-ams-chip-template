
# CACE Summary for inverter

**netlist source**: schematic

|      Parameter       |         Tool         |     Result      | Min Limit  |  Min Value   | Typ Target |  Typ Value   | Max Limit  |  Max Value   |  Status  |
| :------------------- | :------------------- | :-------------- | ---------: | -----------: | ---------: | -----------: | ---------: | -----------: | :------: |
| Open-loop dc gain    | ngspice              | Adc_ol_dB            |            3 dB |  10.839 dB |          any |  31.329 dB |          any |  32.155 dB |   Pass ✅    |
| Upper -3dB cut-off frequency | ngspice              | fcu                  |      1000000 Hz | 2424180.000 Hz |          any | 2988080.000 Hz |          any | 24825000.000 Hz |   Pass ✅    |
| Open-loop dc gain - Monte Carlo | ngspice              | Adc_ol_dB            |            3 dB |   4.742 dB |          any |  22.120 dB |          any |  33.945 dB |   Pass ✅    |
| Upper -3dB cut-off frequency - Monte Carlo | ngspice              | fcu                  |      1000000 Hz | 2041980.000 Hz |          any | 8099625.000 Hz |          any | 43834500.000 Hz |   Pass ✅    |
| Open-loop dc gain - Mismatch | ngspice              | Adc_ol_dB            |            3 dB |  29.970 dB |          any |  31.296 dB |          any |  32.096 dB |   Pass ✅    |
| Upper -3dB cut-off frequency - Mismatch | ngspice              | fcu                  |      1000000 Hz | 2657720.000 Hz |          any | 2902820.000 Hz |          any | 3364770.000 Hz |   Pass ✅    |

