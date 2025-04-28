#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 12:23:55 2023

@author: thoverga
"""


import os
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog
# from metobs_gui.extra_windows import _show_metadf, _show_spatial_html

from metobs_gui.tlk_scripts import gui_wrap, get_function_defaults
from metobs_gui.extra_windows import DatasetTimeSeriesDialog
from metobs_gui.dataframelab import DataDialog
import metobs_gui.common_functions as common_func
import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error, Notification
import metobs_gui.pretty_formatter as pretty_formatter

import metobs_gui.gf_page.settingsdialog as dialogs


all_outl_convert_label = 'ALL outliers'

gf_methods_displayer = {'interpolation': 'Interpolation',
                        'raw_model_gf': 'Raw model gapfill',
                        'debiased_model_gf': 'Debiased model gapfill',
                        'diurnal_gf': 'Diurnal-debiased model gapfill',
                        'weighted_gf': 'Weighted Diurnal-debiased model gapfill'}

# =============================================================================
# init page
# =============================================================================

def init_fill_page(MW):
    MW.method_spinner.clear()
    MW.method_spinner.addItems(list(gf_methods_displayer.values()))

# =============================================================================
# setup page
# =============================================================================

def setup_triggers(MW):
    MW.convert_outliers.clicked.connect(lambda: _react_conv_outliers_to_gaps(MW))

    MW.update_method_settings.clicked.connect(lambda: _react_method_settings(MW))
    MW.fill_gaps_button.clicked.connect(lambda: _react_fill_gaps(MW))
    #analyse buttons
    MW.get_info_gf.clicked.connect(lambda: _react_get_info(MW))
    MW.show_dataset_gf.clicked.connect(lambda: _react_show_data(MW))
    MW.plot_dataset_gf.clicked.connect(lambda: _react_plot_dataset(MW))
    


# =============================================================================
# Reactions
# =============================================================================

    

def _react_conv_outliers_to_gaps(MW):
    func = MW.Dataset.convert_outliers_to_gaps
    #set plaintext prompt
    prompt = MW.prompt_fill

    #get defaults
    func_kwargs = get_function_defaults(func)

    #scrape and Update the default kwargs with settings
    trg_obstype = MW.convert_outliers_trgs.currentText()
    if trg_obstype == all_outl_convert_label:
        func_kwargs['all_observations'] = True
    else:
        func_kwargs['all_observations'] = False
        func_kwargs['obstype'] = trg_obstype


    #Apply the conversion
    _ret, succes, stout = gui_wrap(
                            func = func,
                            func_kwargs=func_kwargs,
                            plaintext=prompt,
                            log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error converting outliers to gaps', stout)
        return

    Notification(f'The outliers are converted to gaps!')


def _react_dataset_loaded(MW):
    #will be triggered if a dataset is loaded, no triggers on this page

    #add 'ALL' to the spinner for selecting the trg for outl->gap conv
    
    MW.convert_outliers_trgs.addItems([all_outl_convert_label])
    MW.convert_outliers_trgs.setCurrentText(all_outl_convert_label)

def _react_fill_gaps(MW):
    func = getattr(MW.Dataset, MW._gf_settings_dict['MetObs_method'])
    print(func)

    #set plaintext prompt
    prompt = MW.prompt_fill

    #get defaults
    func_kwargs = MW._gf_settings_dict
    del func_kwargs['MetObs_method']

    #Apply the qc check
    _ret, succes, stout = gui_wrap(
                            func = func,
                            func_kwargs=func_kwargs,
                            plaintext=prompt,
                            log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when filling the gaps', stout)
        return
    Notification(f'Gap fill is succesfully applied!')


def _react_method_settings(MW):
    #get obstype
    method = MW.method_spinner.currentText()

    if method == gf_methods_displayer['interpolation']:
        launch_interp_settings(MW)
    elif method == gf_methods_displayer['raw_model_gf']:
        launch_raw_model_gf_settings(MW)
    elif method == gf_methods_displayer['debiased_model_gf']:
        launch_debias_model_gf_settings(MW)
    elif method == gf_methods_displayer['diurnal_gf']:
        launch_diurnal_debias_model_gf_settings(MW)
    elif method == gf_methods_displayer['weighted_gf']:
        launch_weighted_diurnal_debias_model_gf_settings(MW)
    else:
        Error(f'Unforseen method: {method}')
    #check if there are gaps for this observationtype
    

        
def launch_interp_settings(MW):
    obstype = MW.fill_obstype.currentText()
    dlg = dialogs.InterpolationSettingsDialog(trgobstype=obstype,
                                              func=MW.Dataset.interpolate_gaps)
    
    if dlg.exec():
        #when pushed the "ok" button
        pass
    
        #scrape the info of the closing window
        settings = dlg.get_settings() #get the latest data from dialo
       
        MW._gf_settings_dict = settings
        
        MW.fill_gaps_button.setEnabled(True)

        #Display the setings
        MW.prompt_fill.appendPlainText(' ------- Settings for gapfilling ---------')
        common_func.display_dict_in_plaintext(plaintext=MW.prompt_fill,
                                              displaydict=settings,
                                              cleanup=False)
        Notification('Settings for interpolation are set, you can now fill the gaps!')
    else: 
        #When closed or clicked on cancel
        print ('Dialog closed, no gap fill settings saved.')
        
        MW.fill_gaps_button.setEnabled(True)
    
    
def launch_weighted_diurnal_debias_model_gf_settings(MW):
    obstype = MW.fill_obstype.currentText()
    dlg = dialogs.WeightedDiurnalDebiasModeldataGFSettingsDialog(
                trgobstype=obstype,
                func=MW.Dataset.fill_gaps_with_weighted_diurnal_debiased_modeldata
                )
                                                                 
    
    if dlg.exec():
        #when pushed the "ok" button
        pass
    
        #scrape the info of the closing window
        settings = dlg.get_settings() #get the latest data from dialo
       
        MW._gf_settings_dict = settings
        
        MW.fill_gaps_button.setEnabled(True)

        #Display the setings
        MW.prompt_fill.appendPlainText(' ------- Settings for gapfilling ---------')
        common_func.display_dict_in_plaintext(plaintext=MW.prompt_fill,
                                              displaydict=settings,
                                              cleanup=False)
        Notification('Settings for weighted diurnal debiased modeldata gapfill are set, you can now fill the gaps!')
    else: 
        #When closed or clicked on cancel
        print ('Dialog closed, no gap fill settings saved.')
        MW.fill_gaps_button.setEnabled(True)
    


def launch_raw_model_gf_settings(MW):
    obstype = MW.fill_obstype.currentText()
    dlg = dialogs.RawModeldataGFSettingsDialog(
        trgobstype=obstype,
        func=MW.Dataset.fill_gaps_with_raw_modeldata                                     
        )
    
    if dlg.exec():
        #when pushed the "ok" button
        pass
    
        #scrape the info of the closing window
        settings = dlg.get_settings() #get the latest data from dialo
       
        MW._gf_settings_dict = settings
        
        MW.fill_gaps_button.setEnabled(True)

        #Display the setings
        MW.prompt_fill.appendPlainText(' ------- Settings for gapfilling ---------')
        common_func.display_dict_in_plaintext(plaintext=MW.prompt_fill,
                                              displaydict=settings,
                                              cleanup=False)
        Notification('Settings for raw model data gapfill are set, you can now fill the gaps!')
    else: 
        #When closed or clicked on cancel
        print ('Dialog closed, no gap fill settings saved.')
        MW.fill_gaps_button.setEnabled(True)
    

def launch_debias_model_gf_settings(MW):
    obstype = MW.fill_obstype.currentText()
    dlg = dialogs.DebiasModeldataGFSettingsDialog(
        trgobstype=obstype,
        func=MW.Dataset.fill_gaps_with_debiased_modeldata)
    
    if dlg.exec():
        #when pushed the "ok" button
        pass
    
        #scrape the info of the closing window
        settings = dlg.get_settings() #get the latest data from dialo
       
        MW._gf_settings_dict = settings
        
        MW.fill_gaps_button.setEnabled(True)

        #Display the setings
        MW.prompt_fill.appendPlainText(' ------- Settings for gapfilling ---------')
        common_func.display_dict_in_plaintext(plaintext=MW.prompt_fill,
                                              displaydict=settings,
                                              cleanup=False)
        Notification('Settings for debiased modeldata gapfill are set, you can now fill the gaps!')
    else: 
        #When closed or clicked on cancel
        print ('Dialog closed, no gap fill settings saved.')
        MW.fill_gaps_button.setEnabled(True)
    

def launch_diurnal_debias_model_gf_settings(MW):
    obstype = MW.fill_obstype.currentText()
    dlg = dialogs.DiurnalDebiasModeldataGFSettingsDialog(
        trgobstype=obstype,
        func=MW.Dataset.fill_gaps_with_diurnal_debiased_modeldata)
    
    if dlg.exec():
        #when pushed the "ok" button
        pass
    
        #scrape the info of the closing window
        settings = dlg.get_settings() #get the latest data from dialo
       
        MW._gf_settings_dict = settings
        
        MW.fill_gaps_button.setEnabled(True)

        #Display the setings
        MW.prompt_fill.appendPlainText(' ------- Settings for gapfilling ---------')
        common_func.display_dict_in_plaintext(plaintext=MW.prompt_fill,
                                              displaydict=settings,
                                              cleanup=False)
        
        Notification('Settings for diurnal debiased modeldata gapfill are set, you can now fill the gaps!')
    else: 
        #When closed or clicked on cancel
        print ('Dialog closed, no gap fill settings saved.')
        MW.fill_gaps_button.setEnabled(True)
    
    
# =============================================================================
# Reactions of analysing buttons
# =============================================================================

def _react_get_info(MW):
    prompt = getattr(MW, 'prompt_fill')
    common_func.display_info_in_plaintext(
        plaintext=prompt,
        metobs_obj=MW.Dataset,
    )

def _react_show_data(MW):
    MW._dlg = DataDialog(dataset=MW.Dataset) #launched when created

def _react_plot_dataset(MW):
    MW._dlg = DatasetTimeSeriesDialog(dataset=MW.Dataset)#launched when created
        