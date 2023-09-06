#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:16:12 2023

@author: thoverga
"""


from pathlib import Path
import copy
import os
import pytz
from PyQt5.QtWidgets import QFileDialog, QComboBox
from metobs_gui.errors import Error, Notification

from metobs_gui.path_handler import template_dir
from metobs_gui.data_func import isvalidfile

import metobs_gui.path_handler as path_handler
from metobs_gui.template_func import Obs_map_values

from metobs_gui.json_save_func import get_saved_vals, update_json_file


import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.log_displayer as log_displayer
from metobs_gui.extra_windows import _show_metadf, _show_obsspace, _show_timeseries

from metobs_toolkit import loggers as toolkit_logger



# =============================================================================
#  Init
# =============================================================================

def init_qc_page(MW):

    MW.obstype_spinner.addItems(list(Obs_map_values.keys()))
    MW.obstype_spinner.setCurrentText('temp') #default

    obstype_change(MW)



# =============================================================================
#  Triggers
# =============================================================================
def obstype_change(MW):
    # get selected obstype
    obstype_select = str(MW.obstype_spinner.currentText())
    MW.apply_qc.setText(f"Apply quality control on {obstype_select.upper()}")


def show_info(MW):
    # check if dataset exists
    if MW.dataset is None:
        Error('Dataset does not exist', 'No information can be shown because the dataset does not exist.')
        return

    # clear prompt
    MW.prompt_qc.clear()
    MW.prompt_qc.appendPlainText('\n---- Dataset information ---- \n')
    info = tlk_scripts.get_dataset_info(dataset = MW.dataset)
    for line in info:
        MW.prompt_qc.appendPlainText(line)


def show_metadf(MW):
    _show_metadf(MW)

def show_dataset(MW):
    _show_obsspace(MW)

def show_timeseries(MW):
    _show_timeseries(MW)




def apply_qc(MW):
    # Check if dataset exist
    if MW.dataset is None:
        Error('Dataset does not exist', 'No information can be shown because the dataset does not exist.')
        return

    # Check if obstype is in the dataset
    obstype = str(MW.obstype_spinner.currentText())
    if not (obstype in MW.dataset.df.columns ):
        Error(f'{obstype} not present', f'The {obstype} is not found in the dataset. These obstypes are found: {list(MW.dataset.df.columns)}')
        return
    MW.prompt_qc.appendPlainText(f'\n----  Apply Quality control on {obstype} ---- \n')

    # read arguments
    argdict = _read_qc_args(MW)

    # Check if buddy check could be executed
    if argdict['apply_buddy']:
        # if not _can_titan_run():
        #     Error('Titanlib not installed', 'It seems that titanlib is not installed, which is necessary for the buddy check.')
        #     return
        if not ('altitude' in MW.dataset.metadf.columns):
            Error('Altitude unknown', 'The buddy check uses the altitude of the stations. This is not present in the metadf. Use the "Get Altitude" button in the metadata tab first.')
            return


    # update qc settings
    _cont, terminal, _msg = tlk_scripts.update_qc_stats(
                dataset=MW.dataset,
                obstype=obstype,
                gapsize_in_records=None,
                dupl_timestamp_keep=None,
                # persistance
                persis_time_win_to_check=argdict['pers_window'],
                persis_min_num_obs=argdict['pers_min_n'],
                # repetitions
                rep_max_valid_repetitions=argdict['rep_max_rep'],
                # gros value
                gross_value_min_value=argdict['gros_min'],
                gross_value_max_value=argdict['gros_max'],
                # window variation
                win_var_max_increase_per_sec=argdict['winvar_max_inc'],
                win_var_max_decrease_per_sec=argdict['winvar_max_dec'],
                win_var_time_win_to_check=argdict['winvar_window'],
                win_var_min_num_obs=argdict['winvar_min_n'],
                # step check
                step_max_increase_per_sec=argdict['step_max_inc'],
                step_max_decrease_per_sec=argdict['step_max_dec'],
                # buddy check
                buddy_radius=argdict['buddy_rad'],
                buddy_num_min=argdict['buddy_min_n'],
                buddy_threshold=argdict['buddy_threshold'],
                buddy_max_elev_diff=argdict['buddy_max_elev_diff'],
                buddy_elev_gradient=argdict['buddy_lapsrate'],
                buddy_min_std=argdict['buddy_min_std'],
                buddy_debug=False)
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    for line in terminal:
        MW.prompt_qc.appendPlainText(line)

    # apply QC
    _cont, terminal, _msg = tlk_scripts.apply_qc(dataset=MW.dataset,
                                                 obstype=obstype,
                                                 gross_value= argdict['apply_gros'],
                                                 persistance=argdict['apply_pers'],
                                                 repetitions=argdict['apply_rep'],
                                                 step=argdict['apply_step'],
                                                 window_variation=argdict['apply_var'])
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    for line in terminal:
        MW.prompt_qc.appendPlainText(line)


    # apply buddy check
    if argdict['apply_buddy']:
        _cont, terminal, _msg = tlk_scripts.apply_buddy(dataset = MW.dataset,
                                                        obstype = obstype,
                                                        use_constant_altitude=False,
                                                        haversine_approx=True,
                                                        metric_epsg="31370")
        if not _cont:
            Error(_msg[0], _msg[1])
            return

        for line in terminal:
            MW.prompt_qc.appendPlainText(line)

    # # apply titan buddy check
    # if argdict['apply_buddy']:
    #     _cont, terminal, _msg = tlk_scripts.apply_titan_buddy(dataset = MW.dataset,
    #                                                           obstype = obstype,
    #                                                           use_constant_altitude=False)
    #     if not _cont:
    #         Error(_msg[0], _msg[1])
    #         return

    #     for line in terminal:
    #         MW.prompt_qc.appendPlainText(line)


    MW.prompt_qc.appendPlainText(f'\n----  Apply Quality control on {obstype} ---> Done! ---- \n')
    Notification(f'Quality control applied on {obstype}.')







# =============================================================================
# Helpers
# =============================================================================

# def _can_titan_run():
#     try:
#         import titanlib
#     except ModuleNotFoundError:
#         return False
#     return True


def _read_qc_args(MW):
    argdict = {}

    # bool values
    argdict['apply_rep'] = True if MW.rep_check.isChecked() else False
    argdict['apply_gros'] = True if MW.gros_check.isChecked() else False
    argdict['apply_pers'] = True if MW.pers_check.isChecked() else False
    argdict['apply_step'] = True if MW.step_check.isChecked() else False
    argdict['apply_var'] = True if MW.var_check.isChecked() else False
    argdict['apply_buddy'] = True if MW.budd_check.isChecked() else False

    # repetitions check
    argdict['rep_max_rep'] = int(MW.rep_max_rep.value())

    # gross value
    argdict['gros_max'] = float(MW.gross_max.value())
    argdict['gros_min'] = float(MW.gross_min.value())

    # persistance
    argdict['pers_window'] = str(int(MW.pers_window.value()))+'T'
    argdict['pers_min_n'] = int(MW.pers_min_n.value())

    # stepcheck
    argdict['step_max_inc'] = float(MW.step_max_inc.value())
    argdict['step_max_dec'] = float(MW.step_max_dec.value())

    # window variation
    argdict['winvar_window'] = str(int(MW.var_window.value()))+'T'
    argdict['winvar_min_n'] = int(MW.var_min_n.value())
    argdict['winvar_max_inc'] = float(MW.var_max_inc_hour.value())/3600.
    argdict['winvar_max_dec'] = float(MW.var_max_dec_hour.value())/3600.


    # buddy check
    argdict['buddy_rad'] = float(MW.buddy_rad.value())
    argdict['buddy_min_n'] = int(MW.buddy_min_n.value())
    argdict['buddy_threshold'] = float(MW.buddy_threshold.value())
    argdict['buddy_min_std'] = float(MW.buddy_min_std.value())
    argdict['buddy_max_elev_diff'] = float(MW.buddy_max_elev_diff.value())
    argdict['buddy_lapsrate'] = float(MW.buddy_lapsrate.value())

    return argdict

