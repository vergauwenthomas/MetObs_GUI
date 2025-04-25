#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:16:12 2023

@author: thoverga
"""

import pprint
# from pathlib import Path
# import copy
# import os
# import pytz
# from PyQt5.QtWidgets import QFileDialog, QComboBox
from metobs_gui.errors import Error, Notification

# from metobs_gui.path_handler import template_dir
# from metobs_gui.data_func import isvalidfile

import metobs_gui.path_handler as path_handler

import metobs_gui.pretty_formatter as pretty_formatter
import metobs_gui.tlk_scripts as tlk_scripts
from metobs_gui.extra_windows import MetadataDialog, DatasetTimeSeriesDialog
# import metobs_gui.log_displayer as log_displayer

# from metobs_toolkit import rootlog as toolkit_logger


# =============================================================================
# init page
# =============================================================================
def init_qc_page(MW):
    #disable spinners based on default 
    _react_use_repetition_check(MW)
    _react_use_grossvalue_check(MW)
    _react_use_persistance_check(MW)
    _react_use_step_check(MW)
    _react_use_var_check(MW)
    _react_use_buddy_check(MW)
    
# =============================================================================
# setup page
# =============================================================================

def setup_triggers(MW):
    #checks triggers    
    MW.rep_check.stateChanged.connect(lambda: _react_use_repetition_check(MW))
    MW.gros_check.stateChanged.connect(lambda: _react_use_grossvalue_check(MW))
    MW.pers_check.stateChanged.connect(lambda: _react_use_persistance_check(MW))
    MW.step_check.stateChanged.connect(lambda: _react_use_step_check(MW))
    MW.var_check.stateChanged.connect(lambda: _react_use_var_check(MW))
    MW.budd_check.stateChanged.connect(lambda: _react_use_buddy_check(MW))

    # buttons
    MW.apply_qc.clicked.connect(lambda: _react_apply_qc(MW))
    
    #analyse buttons
    MW.get_info_2.clicked.connect(lambda: _react_get_info(MW))
    MW.show_metadata_2.clicked.connect(lambda: _react_show_metadata(MW))
    MW.show_dataset_2.clicked.connect(lambda: _react_show_data(MW))
    MW.plot_dataset_2.clicked.connect(lambda: _react_plot_dataset(MW))
    



# =============================================================================
# Reactions
# =============================================================================
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
    pretty_formatter.set_prompt_subsection(text='------ Get info ---------',
                                           prompt=MW.prompt_qc)
    
    _, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.get_info, {})
    
    MW.prompt_qc.insertPlainText(str(stout))
    if not succes:
        Error(f'.get_info() error on {MW.Dataset}', stout)
        
    MW.prompt_qc.centerCursor()

def _react_show_metadata(MW):
    MW._dlg = MetadataDialog(df=MW.Dataset.metadf) #launched when created
def _react_show_data(MW):
    
    returndf, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.get_full_status_df, {})
   
    if succes:
        
        MW._dlg = DataDialog(df=returndf) #launched when created
    else:
        Error('Could not create a full status df.', stout)
    
def _react_plot_dataset(MW):
    MW._dlg = DatasetTimeSeriesDialog(dataset=MW.Dataset)
        
    
# =============================================================================
# Enable/disbale reactions
# =============================================================================

def _react_use_repetition_check(MW):
    related_widg = [MW.rep_max_rep]
    if MW.rep_check.isChecked():
        for widg in related_widg:
            widg.setEnabled(True)
    else:
        for widg in related_widg:
            widg.setEnabled(False)

def _react_use_grossvalue_check(MW):
    related_widg = [MW.gross_max, MW.gross_min]
    if MW.gros_check.isChecked():
        for widg in related_widg:
            widg.setEnabled(True)
    else:
        for widg in related_widg:
            widg.setEnabled(False)
            
def _react_use_persistance_check(MW):
    related_widg = [MW.pers_window,
                    MW.pers_min_n]
    if MW.pers_check.isChecked():
        for widg in related_widg:
            widg.setEnabled(True)
    else:
        for widg in related_widg:
            widg.setEnabled(False)
            
def _react_use_step_check(MW):
    related_widg = [MW.step_max_inc,
                    MW.step_max_dec]
    if MW.step_check.isChecked():
        for widg in related_widg:
            widg.setEnabled(True)
    else:
        for widg in related_widg:
            widg.setEnabled(False)

def _react_use_var_check(MW):
    related_widg = [MW.var_window,
                    MW.var_min_n,
                    MW.var_max_inc_hour,
                    MW.var_max_dec_hour]
    if MW.var_check.isChecked():
        for widg in related_widg:
            widg.setEnabled(True)
    else:
        for widg in related_widg:
            widg.setEnabled(False)

def _react_use_buddy_check(MW):
    related_widg = [MW.buddy_rad,
                    MW.buddy_min_n,
                    MW.buddy_threshold,
                    MW.buddy_min_std,
                    MW.buddy_max_elev_diff,
                    MW.buddy_lapsrate,
                    MW.const_alt_approx]
    if MW.budd_check.isChecked():
        for widg in related_widg:
            widg.setEnabled(True)
    else:
        for widg in related_widg:
            widg.setEnabled(False)

