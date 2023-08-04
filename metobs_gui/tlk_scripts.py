#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 09:40:08 2023

@author: thoverga
"""

#%% Load vlinder toolkit (not shure what is best)
import sys
from io import StringIO

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox


import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error, Notification
# method1: add the toolkit to path,
# sys.path.append(path_handler.TLK_dir)
# from vlinder_toolkit import Dataset

# method2: loead as package
# print('CHANGE THE TOOLKIT PACKAGE LOCATION !!')
# debug_path = '/home/thoverga/Documents/VLINDER_github/MetObs_toolkit'
# sys.path.insert(0, debug_path)
import metobs_toolkit



#%% Mapping
# when specific manipulation has to be done on values

tlk_to_gui = {
    'window_variation__max_increase_per_second': {'multiply': 3600.0},
    'window_variation__max_decrease_per_second' : {'multiply': 3600.0},
    'step__max_increase_per_second' : {'multiply': 3600.0},
    'step__max_decrease_per_second' : {'multiply': 3600.0},

    'persistance__time_window_to_check': {'remove': 'h'},
    'window_variation__time_window_to_check': {'remove': 'h'},
}


gui_to_tlk = {
    'window_variation__max_increase_per_second': {'devide': 3600.0},
    'window_variation__max_decrease_per_second' : {'devide': 3600.0},
    'step__max_increase_per_second' : {'devide': 3600.0},
    'step__max_decrease_per_second' : {'devide': 3600.0},

    'persistance__time_window_to_check': {'append': 'h'},
    'window_variation__time_window_to_check': {'append': 'h'},
}

def _append(x, val):
    return str(x)+str(val)
def _div(x, val):
    return float(x)/float(val)
def _multiply(x, val):
    return float(x) * float(val)
def _remove(x, val):
    return str(x).replace(str(val), '')


qc_not_in_gui = ['duplicated_timestamp', 'internal_consistency'] #not present in gui

#%% Helpers

class CapturingPrint(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

# class Capturing_logs(list):
#     def __enter__(self):
#         self._stderr = sys.stderr
#         sys.stderr = self._stringio_err = StringIO()
#         return self
#     def __exit__(self, *args):
#         self.extend(self._stringio_err.getvalue().splitlines())
#         del self._stringio_err    # free up some memory
#         sys.stderr = self._stderr

#%% Initialisation of widgets


# def get_default_settings():
#     "Get default settings for initiating the widgets"
#     _dummy = metobs_toolkit.Dataset()
#     return _dummy.settings



# def set_qc_default_settings(main):
#     # set default settings

#     main.obstype_selector.addItems(['temp']) #TODO: for now only QC on temp
#     obstype = main.obstype_selector.currentText()

#     # Get standard tlk settings
#     qc_set = main.default_settings.qc['qc_check_settings']

#     for checkname in qc_set:
#         if checkname in qc_not_in_gui:
#             continue
#         check_set = qc_set[checkname][obstype]
#         for set_name, set_val in check_set.items():
#             widgetname = checkname+'__'+set_name
#             if widgetname in tlk_to_gui:
#                 apl=list(tlk_to_gui[widgetname].keys())[0]
#                 val =list(tlk_to_gui[widgetname].values())[0]

#                 if apl == 'multiply': set_val = _multiply(set_val, val)
#                 elif apl == 'devide': set_val = _div(set_val, val)
#                 elif apl == 'append': set_val = _append(set_val, val)
#                 elif apl == 'remove': set_val = _remove(set_val, val)



#             print(f' {widgetname} : {set_val}')

#             widg = getattr(main, widgetname)
#             if isinstance(widg, type(QSpinBox())):
#                 print('spinbox')
#                 widg.setValue(int(set_val))
#             elif isinstance(widg, type(QDoubleSpinBox())):
#                 widg.setValue(float(set_val))
#                 print('doublspinbox')


# def apply_qualitycontrol(main):
#     # check if dataset exist
#     if isinstance(main.dataset, type(None)):
#         Error('Cannot apply quality control, first make a Dataset.')

#     with Capturing() as terminaloutput:
#         main.dataset.apply_quality_control()
#         print('QC IS DONE')

#     # make mergedf for visualising
#     with Capturing() as terminaloutput:
#         comb_df = main.dataset.combine_all_to_obsspace()

#     # write terminal output to
#     main.prompt.append('\n \n ------ Qualtiy control ----- \n \n')
#     for line in terminaloutput:
#         main.prompt.append(line + '\n')

#     return comb_df


# def update_qc_settings(main, dataset, obstype):
#     qc_set = dataset.settings.qc['qc_check_settings']

#     for checkname in qc_set:
#         if checkname in qc_not_in_gui:
#             continue
#         check_set = qc_set[checkname][obstype]
#         for set_name, _ in check_set.items():
#             widgetname = checkname+'__'+set_name

#             widget = getattr(main, widgetname)
#             widget_val = widget.value()

#             if widgetname in gui_to_tlk:
#                 apl=list(gui_to_tlk[widgetname].keys())[0]
#                 val =list(gui_to_tlk[widgetname].values())[0]

#                 if apl == 'multiply': set_val = _multiply(widget_val, val)
#                 elif apl == 'devide': set_val = _div(widget_val, val)
#                 elif apl == 'append': set_val = _append(widget_val, val)
#                 elif apl == 'remove': set_val = _remove(widget_val, val)
#             else:
#                 set_val = widget_val
#             #set value
#             dataset.settings.qc['qc_check_settings'][checkname][obstype][set_name] = set_val

#%%



def import_dataset_from_file(data_path, metadata_path, template_path,
                             freq_est_method,
                             freq_est_simplyfy,
                             freq_est_simplyfy_toll,
                             kwargs_data,
                             kwargs_metadata,
                             gap_def,
                             sync, sync_tol,
                             sync_force,
                             sync_force_freq):



    try:
        # init dataset
        dataset = metobs_toolkit.Dataset()
        dataset.update_settings(input_data_file=data_path,
                                input_metadata_file=metadata_path,
                                template_file=template_path,
                                )
        # update gap defenition
        dataset.update_qc_settings(gapsize_in_records=int(gap_def))
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset initialisation and settings update',
                             error_msg]


    # import data
    try:
        dataset.import_data_from_file(freq_estimation_method = freq_est_method,
                                      freq_estimation_simplify = freq_est_simplyfy,
                                      freq_estimation_simplify_error=freq_est_simplyfy_toll,
                                      kwargs_data_read=kwargs_data,
                                      kwargs_metadata_read=kwargs_metadata)
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset importing data', error_msg]

    # syncronize
    if sync:
        try:
            if sync_force:
                print('hierD')
                dataset.sync_observations(tollerance = sync_tol,
                                      verbose=True,
                                      _force_resolution_minutes=sync_force_freq,
                                      _drop_target_nan_dt=False)
            else:
                print('hierE')
                dataset.sync_observations(tollerance = sync_tol,
                                      verbose=True,
                                      _force_resolution_minutes=None,
                                      _drop_target_nan_dt=False)
        except Exception as e:
            error_msg = str(e)
            return None, False, ['Dataset syncronization', error_msg]


    return dataset, True, ['error_theme', 'error_msg']


def coarsen_timeres(dataset, target_freq, origin, method):
    try:

        dataset.coarsen_time_resolution(origin=origin,
                                        freq=target_freq,
                                        method=method)
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset coarsen timeresolution', error_msg]


    return dataset, True, ['error_theme', 'error_msg']


def import_dataset_from_pkl(pkl_name, pkl_folder):
    try:
        dataset = metobs_toolkit.Dataset()
        dataset = dataset.import_dataset(folder_path=pkl_folder,
                                         filename=pkl_name)
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset import from pkl',
                            error_msg]

    return dataset, True, ['error_theme', 'error_msg']


def save_dataset_to_pkl(dataset, pkl_name, pkl_folder):
    try:
        dataset.save_dataset(outputfolder=pkl_folder,
                             filename=pkl_name)
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset save to pkl',
                             error_msg]
    return None, True, ['error_theme', 'error_msg']



def get_dataset_info(dataset):
    with CapturingPrint() as infolist:
        dataset.get_info()
    return infolist



def combine_to_obsspace(dataset):
    try:
        comb_df = dataset.combine_all_to_obsspace()
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Combine dataset to observation-space',
                             error_msg]
    return comb_df, True, ['error_theme', 'error_msg']



def get_altitude(dataset):
    try:
        with CapturingPrint() as infolist:
            dataset.get_altitude()
    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Get altidude error',
                       error_msg]
    return True, infolist, ['error_theme', 'error_msg']


def get_lcz(dataset):
    try:
        with CapturingPrint() as infolist:
            dataset.get_lcz()
    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Get lcz error',
                       error_msg]
    return True, infolist, ['error_theme', 'error_msg']


def get_landcover(dataset, buffers, aggbool, gee_map, overwrite=True):
    try:
        with CapturingPrint() as infolist:
            _ = dataset.get_landcover(buffers=buffers,
                                      aggregate=aggbool,
                                      gee_map=gee_map,
                                      overwrite=overwrite)
    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Get landcover error',
                       error_msg]
    return True, infolist, ['error_theme', 'error_msg']




#%% Toolkit functions





