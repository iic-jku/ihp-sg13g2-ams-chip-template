# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2025-2026 Simon Dorrer
# SPDX-License-Identifier: Apache-2.0
# Master-Thesis
# @ JKU IICQC
# 2025
# Author: Simon Dorrer
# Description: This file reads the data from the MFB filter AC analysis and save it to a .csv file.
# Created: 14.08.2025
# Last Modified: 14.08.2025
# ============================================

# Imports
import numpy as np
from typing import Any
from pathlib import Path
# ============================================

# Functions
def postprocess(results: dict[str, list], conditions: dict[str, Any]) -> dict[str, list]:
    # Print results and conditions for debugging
    # print(f'results: {results}')
    # print(f'conditions: {conditions}')
    
    # Iterate over Adc_ol_dB MC results
    Adc_ol_dB_arr = []
    for Adc_ol_dB in results['Adc_ol_dB']:
        Adc_ol_dB_arr.append(Adc_ol_dB)
    print(f'Adc_ol_dB_arr = {Adc_ol_dB_arr}')
    
    # Delete statistical outliers in Adc_ol_dB_arr
    Adc_ol_dB_arr = [val for val in Adc_ol_dB_arr if -20 <= val <= 20]
    print(f'Adc_ol_dB_arr = {Adc_ol_dB_arr}')
    
    # Iterate over fcu MC results
    fcu_arr = []
    for fcu in results['fcu']:
        fcu_arr.append(fcu)
    print(f'fcu_arr = {fcu_arr}')
    
    # Delete statistical outliers in fcu_arr
    fcu_arr = [val for val in fcu_arr if 1 <= val <= 1e6]
    print(f'fcu_arr = {fcu_arr}')
    
    # Save data as .csv
    csv_filename = Path(__file__).with_suffix('.csv').name
    min_len = min(len(Adc_ol_dB_arr), len(fcu_arr))
    np.savetxt(f'cace/scripts/{csv_filename}',
               np.column_stack((np.array(Adc_ol_dB_arr[:min_len]), np.array(fcu_arr[:min_len]))),
               comments = "", header = "Adc_ol_dB_arr,fcu_arr", delimiter = ",")
    
    return {'Adc_ol_dB_arr': Adc_ol_dB_arr, 'fcu_arr': fcu_arr}
# ============================================