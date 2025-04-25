#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:16:12 2023

@author: thoverga
"""

import pprint

from metobs_gui.errors import Error, Notification
import metobs_gui.common_functions as common_func
from metobs_gui.tlk_scripts import gui_wrap, get_function_defaults

import metobs_gui.pretty_formatter as pretty_formatter
import metobs_gui.tlk_scripts as tlk_scripts
from metobs_gui.extra_windows import DatasetTimeSeriesDialog
from metobs_gui.dataframelab import DataDialog

# =============================================================================
# init page
# =============================================================================
def init_qc_page(MW):
    #disable spinners based on default 
    pass
# =============================================================================
# setup page
# =============================================================================

def setup_triggers(MW):
    #checks triggers 
    MW.buddy_with_altdif.stateChanged.connect(lambda: _react_buddy_with_altdiff(MW))
    MW.buddy_with_lapserate.stateChanged.connect(lambda: _react_buddy_with_lapserate(MW))
   
    #spinner change
    MW.obstype_spinner.currentTextChanged.connect(lambda: _react_qc_trg_obstype_change(MW))

    #QC checks
    MW.apply_rep_check.clicked.connect(lambda: _react_rep_check(MW))
    MW.apply_gross_val_check.clicked.connect(lambda: _react_gross_val_check(MW))
    MW.apply_persis_check.clicked.connect(lambda: _react_persist_check(MW))
    MW.apply_step_check.clicked.connect(lambda: _react_step_check(MW))
    MW.apply_wind_var_check.clicked.connect(lambda: _react_window_var_check(MW))
    MW.apply_buddy_check.clicked.connect(lambda: _react_buddy_check(MW))

    # buttons
    # MW.apply_qc.clicked.connect(lambda: _react_apply_qc(MW))
    
    #analyse buttons
    MW.get_info_qc.clicked.connect(lambda: _react_get_info(MW))
    MW.show_dataset_qc.clicked.connect(lambda: _react_show_data(MW))
    MW.plot_dataset_qc.clicked.connect(lambda: _react_plot_dataset(MW))
    



# =============================================================================
# Reactions
# =============================================================================

def _react_buddy_with_altdiff(MW):
    if MW.buddy_with_altdif.isChecked():
        MW.buddy_max_elev_diff.setEnabled(True)
    else:
        MW.buddy_max_elev_diff.setEnabled(False)

def _react_buddy_with_lapserate(MW):
    if MW.buddy_with_lapserate.isChecked():
        MW.buddy_lapserate.setEnabled(True)
    else:
        MW.buddy_lapserate.setEnabled(False)

def  _react_qc_trg_obstype_change(MW):
    if MW.obstype_spinner.currentText == 'temp':
        MW.buddy_with_lapserate.setChecked(True)
    else:
        MW.buddy_with_lapserate.setChecked(False)

    _react_buddy_with_lapserate(MW)






def check_dataset_before_qc(MW):
    if MW.Dataset.df.empty:
        Error('There is no data to apply QC on.')
    

def _react_rep_check(MW):
    func = MW.Dataset.repetitions_check
    #set plaintext prompt
    prompt = MW.prompt_qc

    #Test if dataset has records
    check_dataset_before_qc(MW)

    #get defaults
    func_kwargs = get_function_defaults(func)

    #scrape and Update the default kwargs with settings
    trg_obstype = MW.obstype_spinner.currentText()
    func_kwargs.update({
        'target_obstype': trg_obstype,
        'max_N_repetitions': int(MW.rep_max_rep.value())
    })

    #Apply the qc check
    _ret, succes, stout = gui_wrap(
                            func = func,
                            func_kwargs=func_kwargs,
                            plaintext=prompt,
                            log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when applying repetitions check.', stout)
        return

    Notification(f'Repetitions check applied on {trg_obstype} observations.')



def _react_gross_val_check(MW):
    func = MW.Dataset.gross_value_check
    #set plaintext prompt
    prompt = MW.prompt_qc

    #Test if dataset has records
    check_dataset_before_qc(MW)

    #get defaults
    func_kwargs = get_function_defaults(func)

    #scrape and Update the default kwargs with settings
    trg_obstype = MW.obstype_spinner.currentText()
    func_kwargs.update({
        'target_obstype': trg_obstype,
        'lower_threshold': MW.gross_min.value(),
        'upper_threshold': MW.gross_max.value()
    })

    #Apply the qc check
    _ret, succes, stout = gui_wrap(
                            func = func,
                            func_kwargs=func_kwargs,
                            plaintext=prompt,
                            log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when applying gross value check.', stout)
        return

    Notification(f'Gross value  check applied on {trg_obstype} observations.')

def _react_persist_check(MW):
    func = MW.Dataset.persistence_check
    #set plaintext prompt
    prompt = MW.prompt_qc

    #Test if dataset has records
    check_dataset_before_qc(MW)

    #get defaults
    func_kwargs = get_function_defaults(func)

    #scrape and Update the default kwargs with settings
    trg_obstype = MW.obstype_spinner.currentText()
    func_kwargs.update({
        'target_obstype': trg_obstype,
        'timewindow': f'{int(MW.pers_window.value())}min',
        'min_records_per_window': int(MW.pers_min_n.value())
    })

    #Apply the qc check
    _ret, succes, stout = gui_wrap(
                            func = func,
                            func_kwargs=func_kwargs,
                            plaintext=prompt,
                            log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when applying persistence check.', stout)
        return

    Notification(f'Persistence check applied on {trg_obstype} observations.')
def _react_step_check(MW):
    func = MW.Dataset.step_check
    #set plaintext prompt
    prompt = MW.prompt_qc

    #Test if dataset has records
    check_dataset_before_qc(MW)

    #get defaults
    func_kwargs = get_function_defaults(func)

    #scrape and Update the default kwargs with settings
    trg_obstype = MW.obstype_spinner.currentText()
    func_kwargs.update({
        'target_obstype': trg_obstype,
        'max_increase_per_second': float(MW.step_max_inc.value())/3600.0,
        'max_decrease_per_second': float(MW.step_max_dec.value())/3600.0
    })

    #Apply the qc check
    _ret, succes, stout = gui_wrap(
                            func = func,
                            func_kwargs=func_kwargs,
                            plaintext=prompt,
                            log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when applying step check.', stout)
        return

    Notification(f'Step check applied on {trg_obstype} observations.')
    
def _react_window_var_check(MW):
    func = MW.Dataset.window_variation_check
    #set plaintext prompt
    prompt = MW.prompt_qc

    #Test if dataset has records
    check_dataset_before_qc(MW)

    #get defaults
    func_kwargs = get_function_defaults(func)

    #scrape and Update the default kwargs with settings
    trg_obstype = MW.obstype_spinner.currentText()
    func_kwargs.update({
        'target_obstype': trg_obstype,
        'timewindow': f'{int(MW.var_window.value())}min',
        'min_records_per_window': int(MW.var_min_n.value()),
        'max_increase_per_second': float(MW.var_max_inc_hour.value())/3600.0, 
        'max_decrease_per_second': float(MW.var_max_dec_hour.value())/3600.0
    })

    #Apply the qc check
    _ret, succes, stout = gui_wrap(
                            func = func,
                            func_kwargs=func_kwargs,
                            plaintext=prompt,
                            log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when applying window variation check.', stout)
        return

    Notification(f'Window variation check applied on {trg_obstype} observations.')

def _react_buddy_check(MW):
    func = MW.Dataset.buddy_check
    #set plaintext prompt
    prompt = MW.prompt_qc

    #Test if dataset has records
    check_dataset_before_qc(MW)

    #get defaults
    func_kwargs = get_function_defaults(func)

    #scrape and Update the default kwargs with settings
    trg_obstype = MW.obstype_spinner.currentText()
    
    if MW.buddy_max_elev_diff.isEnabled():
        max_alt_diff = float(MW.buddy_max_elev_diff.value())
    else:
        max_alt_diff = None

    if MW.buddy_lapserate.isEnabled():
        lapserate = float(MW.buddy_lapserate.value())
    else:
        lapserate = None
    

    func_kwargs.update({
        'target_obstype': trg_obstype,
        'buddy_radius': float(MW.buddy_rad.value()),
        'min_sample_size': int(MW.buddy_min_n.value()),
        'max_alt_diff': max_alt_diff,
        'min_std': float(MW.buddy_min_std.value()),
        'std_threshold': float(MW.buddy_threshold.value()),
        'N_iter': int(MW.buddy_iter.value()),
        'instantanious_tolerance': f'{int(MW.buddy_int_tol.value())}min',
        'lapserate': lapserate
    })

    #Apply the qc check
    _ret, succes, stout = gui_wrap(
                            func = func,
                            func_kwargs=func_kwargs,
                            plaintext=prompt,
                            log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when applying buddy check.', stout)
        return

    Notification(f'Buddy check applied on {trg_obstype} observations.')
    

def _react_apply_qc(MW):
    
    obstype = MW.obstype_spinner.currentText()
    prompt_title=f'---------Apply QC on {obstype} --------- '
    pretty_formatter.set_prompt_subsection(text=prompt_title,
                                           prompt=MW.prompt_qc)

    if MW.Dataset.df.empty:
        Error('There is no data to apply QC on.')
        return
    #Scrape the UI
    ui_settings = {
        'obstype': obstype,
        'dupl_timestamp_keep':None,}
    
    if MW.rep_check.isChecked():
        ui_settings.update(
            {'rep_max_valid_repetitions':int(MW.rep_max_rep.value())})
    
    if MW.gros_check.isChecked():
        ui_settings.update(
            {'gross_value_min_value':float(MW.gross_min.value()),
            'gross_value_max_value':float(MW.gross_max.value())})
    
    if MW.pers_check.isChecked():
        ui_settings.update(
            {'persis_time_win_to_check':f'{int(MW.pers_window.value())}min',
            'persis_min_num_obs':int(MW.pers_min_n.value())})
        
    if MW.step_check.isChecked():
        ui_settings.update({
        'step_max_increase_per_sec':float(MW.step_max_inc.value())/3600.0,
        'step_max_decrease_per_sec':float(MW.step_max_dec.value())/3600.0,})
        
    if MW.var_check.isChecked():
        ui_settings.update({
            'win_var_max_increase_per_sec':float(MW.var_max_inc_hour.value())/3600.0,
            'win_var_max_decrease_per_sec':float(MW.var_max_dec_hour.value())/3600.0,
            'win_var_time_win_to_check':f'{int(MW.var_window.value())}min',
            'win_var_min_num_obs':int(MW.var_min_n.value())})
        
    if MW.budd_check.isChecked():
        ui_settings.update(
            {'buddy_radius':int(MW.buddy_rad.value()),
             'buddy_min_sample_size':int(MW.buddy_min_n.value()),
             'buddy_max_elev_diff':int(MW.buddy_max_elev_diff.value()),
             'buddy_min_std':float(MW.buddy_min_std.value()),
             'buddy_threshold':float(MW.buddy_threshold.value()),
             'buddy_elev_gradient': float(MW.buddy_lapsrate.value())})
        
    
    #update display with scraped values
    MW.prompt_qc.appendPlainText(pprint.pformat(ui_settings))
    #Update the settings of the Dataset
    _ret, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.update_qc_settings,
                                               ui_settings)
    if not succes:
        Error('Error when updateting QC settings.', stout)
        return

    #Now apply QC
    apply_qc_kwargs = {
        'obstype':obstype,
        'gross_value':MW.gros_check.isChecked(),
        'persistence':MW.pers_check.isChecked(),
        'repetitions':MW.rep_check.isChecked(),
        'step':MW.step_check.isChecked(),
        'window_variation':MW.var_check.isChecked()}
    #Apply regular QC
    _ret, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.apply_quality_control,
                                               apply_qc_kwargs)
    if not succes:
        Error('Error when applying QC checks.', stout)
        return
    MW.prompt_qc.appendPlainText(str(stout))
    
    if MW.budd_check.isChecked():
        buddy_check_kargs={
            'obstype':obstype,
            'use_constant_altitude':MW.const_alt_approx.isChecked(),
            'haversine_approx':True,
            }
        
        _ret, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.apply_buddy_check,
                                                   buddy_check_kargs)
        if not succes:
            Error('Error when applying buddy check.', stout)
            return
    
        MW.prompt_qc.appendPlainText(str(stout))
    
    Notification(f'Quality control is applied on {obstype} observations.')




def _react_get_info(MW):
    prompt = getattr(MW, 'prompt_qc')
    common_func.display_info_in_plaintext(
        plaintext=prompt,
        metobs_obj=MW.Dataset,
    )

def _react_show_data(MW):
    MW._dlg = DataDialog(dataset=MW.Dataset) #launched when created

def _react_plot_dataset(MW):
    MW._dlg = DatasetTimeSeriesDialog(dataset=MW.Dataset)#launched when created
        
    
