# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2025-2026 The Chip Team
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
    
    # Iterate over Adc_cl_dB MC results
    Adc_cl_dB_arr = []
    for Adc_cl_dB in results['Adc_cl_dB']:
        Adc_cl_dB_arr.append(Adc_cl_dB)
    print(f'Adc_cl_dB_arr = {Adc_cl_dB_arr}')
    
    # Delete statistical outliers in Adc_cl_dB_arr
    Adc_cl_dB_arr = [val for val in Adc_cl_dB_arr if -20 <= val <= 20]
    print(f'Adc_cl_dB_arr = {Adc_cl_dB_arr}')
    
    # Iterate over fcu MC results
    fcu_arr = []
    for fcu in results['fcu']:
        fcu_arr.append(fcu)
    print(f'fcu_arr = {fcu_arr}')
    
    # Delete statistical outliers in fcu_arr
    fcu_arr = [val for val in fcu_arr if 1 <= val <= 1e6]
    print(f'fcu_arr = {fcu_arr}')
    
    # Iterate over CMRR_dc_dB MC results
    CMRR_dc_dB_arr = []
    for CMRR_dc_dB in results['CMRR_dc_dB']:
        CMRR_dc_dB_arr.append(CMRR_dc_dB)
    print(f'CMRR_dc_dB_arr = {CMRR_dc_dB_arr}')
    
    # Delete statistical outliers in CMRR_dc_dB_arr
    CMRR_dc_dB_arr = [val for val in CMRR_dc_dB_arr if 1 <= val <= 200]
    print(f'CMRR_dc_dB_arr = {CMRR_dc_dB_arr}')
    
    # # Iterate over PSRR_dc_dB MC results
    # PSRR_dc_dB_arr = []
    # for PSRR_dc_dB in results['PSRR_dc_dB']:
        # PSRR_dc_dB_arr.append(PSRR_dc_dB)
    # print(f'PSRR_dc_dB_arr = {PSRR_dc_dB_arr}')
    
    # # Delete statistical outliers in PSRR_dc_dB_arr
    # PSRR_dc_dB_arr = [val for val in PSRR_dc_dB_arr if 1 <= val <= 200]
    # print(f'PSRR_dc_dB_arr = {PSRR_dc_dB_arr}')
    
    # Save data as .csv
    csv_filename = Path(__file__).with_suffix('.csv').name
    np.savetxt(f'cace/scripts/{csv_filename}',
               # np.column_stack((np.array(Adc_cl_dB_arr), np.array(fcu_arr), np.array(CMRR_dc_dB_arr), np.array(PSRR_dc_dB_arr))), comments = "", 
               # header = "Adc_cl_dB_arr,fcu_arr,CMRR_dc_dB_arr,PSRR_dc_dB_arr", delimiter = ",")
               np.column_stack((np.array(Adc_cl_dB_arr), np.array(fcu_arr), np.array(CMRR_dc_dB_arr))), comments = "", 
               header = "Adc_cl_dB_arr,fcu_arr,CMRR_dc_dB_arr", delimiter = ",")
    
    # return {'Adc_cl_dB_arr': Adc_cl_dB_arr, 'fcu_arr': fcu_arr, 'CMRR_dc_dB_arr': CMRR_dc_dB_arr, 'PSRR_dc_dB_arr': PSRR_dc_dB_arr}
    return {'Adc_cl_dB_arr': Adc_cl_dB_arr, 'fcu_arr': fcu_arr, 'CMRR_dc_dB_arr': CMRR_dc_dB_arr}
# ============================================