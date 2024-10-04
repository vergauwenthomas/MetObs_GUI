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

# dataset.import_data_from_file(input_data_file=inputdata,
#                               input_metadata_file=inputmetadata,
#                               template_file=inputtemplate)


modeldata = metobs_toolkit.import_modeldata_from_pkl(folder_path='/home/thoverga/Documents/VLINDER_github/MetObs_GUI/metobs_gui/cache/modeldata',
                                                     filename='temp_and_pres_Siebe.pkl')

dataset.gee_datasets['ERA5-land'] = modeldata


obstype_model='temp'
dataset=None
obstype_dataset='temp'


dataset.gee_datasets['ERA5-land'].make_plot(obstype_model=obstype_model,
                                     Dataset = dataset,
                                     obstype_dataset=obstype_dataset,
                                     stationnames=stationnames,
                                     starttime=None,
                                     endtime=None,
                                     title=None,
                                     show_outliers=show_outliers,
                                     show_filled=True,
                                     legend=True,
                                     # _ax=self.axes)
#%%


#%%
# ui_settings={'dupl_timestamp_keep': None,
#  'gross_value_max_value': 21.0,
#  'gross_value_min_value': -15.0,
#  'obstype': 'temp',
#  'persis_min_num_obs': 5,
#  'persis_time_win_to_check': '60min',
#  'rep_max_valid_repetitions': 5,
#  'step_max_decrease_per_sec': -0.002777777777777778,
#  'step_max_increase_per_sec': 0.0022222222222222222,
#  'win_var_max_decrease_per_sec': 0.002777777777777778,
#  'win_var_max_increase_per_sec': 0.0022222222222222222,
#  'win_var_min_num_obs': 3,
#  'win_var_time_win_to_check': '60min'}


# dataset.update_qc_settings(**ui_settings)

# def appl(func, kwargs):
#     func(**kwargs)

# appl(dataset.update_qc_settings,ui_settings)
# qc_set={'obstype': 'temp',
#         'gross_value': True,
#         'persistence': True,
#         'repetitions': True,
#         'step': True,
#         'window_variation': True}

# appl(dataset.apply_quality_control, qc_set)

# # dataset.apply_quality_control()

# dataset.get_info()


#%%
# import inspect 
# def get_default_args(func):
#     signature = inspect.signature(func)
#     return {k:v.default for k,v in signature.parameters.items()}


# print(get_default_args(metobs_toolkit.Dataset.make_plot))


#%%
# df = dataset.get_full_status_df()
# df = df.reset_index()












