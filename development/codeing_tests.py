#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 14:55:36 2024

@author: thoverga
"""

import sys, os
sys.path.insert(0, '/home/thoverga/Documents/VLINDER_github/MetObs_toolkit')
import metobs_toolkit


print(metobs_toolkit.__version__)


#%%

dataset = metobs_toolkit.Dataset()

dataset.import_data_from_file(input_data_file=metobs_toolkit.demo_datafile,
                              input_metadata_file=metobs_toolkit.demo_metadatafile,
                              template_file=metobs_toolkit.demo_template)



#%%
df = dataset.get_full_status_df()
# df = df.reset_index()









