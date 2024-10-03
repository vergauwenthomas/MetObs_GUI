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

inputdata = '/home/thoverga/Desktop/siebe_toolkit_scripts/Siebe_2024.csv'
inputmetadata = '/home/thoverga/Desktop/siebe_toolkit_scripts/GPS meetpunten GENK.csv'
inputtemplate='/home/thoverga/Documents/VLINDER_github/MetObs_GUI/metobs_gui/cache/templates/siebe_template.json'




dataset = metobs_toolkit.Dataset()

dataset.import_data_from_file(input_data_file=inputdata,
                              input_metadata_file=inputmetadata,
                              template_file=inputtemplate)


#%%
import inspect 
def get_default_args(func):
    signature = inspect.signature(func)
    return {k:v.default for k,v in signature.parameters.items()}


print(get_default_args(metobs_toolkit.Dataset.make_plot))


#%%
# df = dataset.get_full_status_df()
# df = df.reset_index()












