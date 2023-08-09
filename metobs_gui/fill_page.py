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

from metobs_gui.json_save_func import get_saved_vals
from metobs_gui.extra_windows import (_show_missing_obs_df,
                                      _show_gaps_df,
                                      _show_obsspace,
                                      _show_missing_obs_fill_df,
                                      _show_gaps_fill_df,
                                      _show_timeseries)



import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error, Notification
from metobs_gui.template_func import Obs_map_values
from metobs_gui.metadata_page import _coordinates_available

# =============================================================================
# init page
# =============================================================================


def init_fill_page(MW):

    # init obstype
    MW.fill_obstype.addItems(list(Obs_map_values.keys()))
    MW.fill_obstype.setCurrentText('temp') #default

    # init techniques
    MW.fill_missing_technique.addItems(['interpolation'])
    MW.fill_gaps_technique.addItems(['interpolation', 'debias modeldata', 'automatic'])
    MW.fill_gaps_technique.setCurrentText('interpolation')



    # init settings
    interp_methods = ['linear', 'time','nearest']
    MW.missing_interp_method.addItems(interp_methods)
    MW.missing_interp_method.setCurrentText('time')
    MW.gap_interp_method.addItems(interp_methods)
    MW.gap_interp_method.setCurrentText('time')


    setup_gap_settings(MW)




# =============================================================================
# setup
# =============================================================================

def setup_gap_settings(MW):

    groups = _widget_grouper(MW)
    # 3 options: linear gapfill, debias gapfill and automatic

    if str(MW.fill_gaps_technique.currentText()) == 'interpolation':
        interp_group = True
        debias_group =False
        auto_group=False
        # use_modeldata = False




    elif str(MW.fill_gaps_technique.currentText()) == 'debias modeldata':
        interp_group = False
        debias_group =True
        auto_group=False
        # use_modeldata = True

    else:
        interp_group = True
        debias_group =True
        auto_group=True
        # use_modeldata = True



    for widg in groups['interp_group']: widg.setEnabled(interp_group)
    for widg in groups['debias_group']: widg.setEnabled(debias_group)
    for widg in groups['auto_group']: widg.setEnabled(auto_group)


def setup_convert_outliers(MW):
    if MW.apply_convert_outl.isChecked():
        MW.gapsize_conv.setEnabled(True)
        MW.conv_outliers.setEnabled(True)
        assume_gapsize(MW)
    else:
        MW.gapsize_conv.setEnabled(False)
        MW.conv_outliers.setEnabled(False)


# # =============================================================================
# # triggers
# # =============================================================================


def assume_gapsize(MW):
    labeltext = '(info) The assumed gapsize in time is: '
    if MW.dataset is None:
        labeltext += 'UNKNONW'
        MW.display_gapsize.setText(labeltext)
        return
    if not "dataset_resolution" in MW.dataset.metadf.columns:
        labeltext += 'UNKNONW'
        MW.display_gapsize.setText(labeltext)
        return
    # check if resolution is the same for all stations
    if len(MW.dataset.metadf['dataset_resolution'].unique()) > 1:
        labeltext += 'UNKNONW'
        MW.display_gapsize.setText(labeltext)
        return

    # get first element
    freq = MW.dataset.metadf['dataset_resolution'].iloc[0]
    gapsize = int(MW.gapsize_conv.value()) * freq
    labeltext += str(gapsize)
    MW.display_gapsize.setText(labeltext)
    return


def convert_outl_to_mis(MW):
    if MW.dataset is None:
        Error('No Dataset', 'There is no dataset loaded.')
        return
    if MW.dataset.df.empty:
        Error('Empty Dataset', 'The loaded dataset is empty.')
        return
    if MW.dataset.outliersdf.empty:
        Notification('There are no outliers in the Dataset!')
        return

    obstype = str(MW.fill_obstype.currentText())
    gapsize = int(MW.gapsize_conv.value())

    MW.prompt_metadata.appendPlainText(f'\n---- Convert {obstype} outliers to missing observations and gaps---- \n')
    # convert outliers to gaps and missing
    dataset, _cont, terminal, _msg = tlk_scripts.convert_outliers_to_missing_and_gaps(
                                    dataset=MW.dataset,
                                    obstype=obstype,
                                    ngapsize=gapsize)

    if not _cont:
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)

    MW.dataset = dataset
    MW.prompt_metadata.appendPlainText(f'\n---- Convert {obstype} outliers to missing observations and gaps ---> Done! ---- \n')
    Notification(f'The {obstype}-outliers are converted to missing observations and gaps.')




def apply_fill_missing(MW):
    # check if dataset is not empty
    if MW.dataset is None:
        Error('No Dataset', 'There is no dataset loaded.')
        return
    if MW.dataset.df.empty:
        Error('Empty Dataset', 'The loaded dataset is empty.')
        return

    obstype = str(MW.fill_obstype.currentText())
    method= str(MW.fill_missing_technique.currentText())
    if method != 'interpolation':
        Error('103', f'missing obs method {method} not implemented yet')
        return

    interpolation_method = str(MW.missing_interp_method.currentText())

    # start prompting
    MW.prompt_metadata.appendPlainText(f'\n---- Filling missing {obstype} observations---- \n')

    # update the settings of the dataset
    dataset, _cont, terminal, _msg = tlk_scripts.update_gap_and_missing_fill(
                    dataset=MW.dataset,
                    missing_obs_interpolation_method=interpolation_method)

    if not _cont:
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)

    MW.dataset = dataset

    # fill missing observations

    dataset, _cont, terminal, _msg = tlk_scripts.fill_missing_observations(
                                            dataset=MW.dataset,
                                            obstype = obstype)

    if not _cont:
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)

    MW.dataset = dataset
    MW.prompt_metadata.appendPlainText(f'\n---- Filling missing {obstype} observations ---> Done! ---- \n')
    Notification(f'The missing {obstype} records are filled.')


def apply_fill_gaps(MW):
    # check if dataset is not empty
    if MW.dataset is None:
        Error('No Dataset', 'There is no dataset loaded.')
        return
    if MW.dataset.df.empty:
        Error('Empty Dataset', 'The loaded dataset is empty.')
        return

    # check if there are gaps
    if len(MW.dataset.gaps) == 0:
        Error('No gaps', 'There are no gaps to fill in the Dataset.')
        return

    obstype = str(MW.fill_obstype.currentText())

    # 3 methods:
    gapfill_method = str(MW.fill_gaps_technique.currentText())

    MW.prompt_metadata.appendPlainText(f'\n---- Filling {obstype} gaps using {gapfill_method} ---- \n')

    if gapfill_method == 'interpolation':
        interp_method = str(MW.gap_interp_method.currentText())
        max_interp = int(MW.gap_max_interp.value())

        # update the settings of the dataset
        dataset, _cont, terminal, _msg = tlk_scripts.update_gap_and_missing_fill(
                        dataset=MW.dataset,
                        gap_interpolation_method=interp_method,
                        gap_interpolation_max_consec_fill=max_interp)


        if not _cont:
            Error(_msg[0], _msg[1])
            return
        for line in terminal:
            MW.prompt_fill.appendPlainText(line)

        MW.dataset = dataset

        # fill gaps with interpolation
        dataset, _cont, terminal, _msg = tlk_scripts.interpolate_gaps(
                            dataset = MW.dataset,
                            obstype=obstype,
                            overwrite=True)

        if not _cont:
            Error(_msg[0], _msg[1])
            return
        for line in terminal:
            MW.prompt_fill.appendPlainText(line)

        MW.dataset = dataset


    elif gapfill_method == 'debias modeldata':
        # check if the modeldata is compatible:
        compatible = check_if_modeldata_can_be_used(MW, obstype)
        if not compatible:
            return

        pref_lead_hours = int(MW.gap_pref_lead.value())
        min_lead_hours = int(MW.gap_min_lead.value())
        pref_trail_hours = int(MW.gap_pref_trail.value())
        min_trail_hours = int(MW.gap_min_trail.value())

        # update the settings of the dataset
        dataset, _cont, terminal, _msg = tlk_scripts.update_gap_and_missing_fill(
                        dataset=MW.dataset,
                        gap_debias_prefered_leading_period_hours=pref_lead_hours,
                        gap_debias_prefered_trailing_period_hours=pref_trail_hours,
                        gap_debias_minimum_leading_period_hours=min_lead_hours,
                        gap_debias_minimum_trailing_period_hours=min_trail_hours,
                        )


        if not _cont:
            Error(_msg[0], _msg[1])
            return
        for line in terminal:
            MW.prompt_fill.appendPlainText(line)

        MW.dataset = dataset

        # fill gaps with debias model
        dataset, _cont, terminal, _msg = tlk_scripts.debias_fill_gaps(
                        dataset=MW.dataset,
                        modeldata=MW.modeldata,
                        method='debias',
                        obstype=obstype,
                        overwrite=True)

        if not _cont:
            Error(_msg[0], _msg[1])
            return
        for line in terminal:
            MW.prompt_fill.appendPlainText(line)

        MW.dataset = dataset


    else:
        # automatic

        # check if the modeldata is compatible:
        compatible = check_if_modeldata_can_be_used(MW, obstype)
        if not compatible:
            return
        interp_method = str(MW.gap_interp_method.currentText())
        max_interp = int(MW.gap_max_interp.value())
        pref_lead_hours = int(MW.gap_pref_lead.value())
        min_lead_hours = int(MW.gap_min_lead.value())
        pref_trail_hours = int(MW.gap_pref_trail.value())
        min_trail_hours = int(MW.gap_min_trail.value())
        max_interp_duration_hours =str(int(MW.gap_debias_max_interp_hours.value()))+'H'

        # update the settings of the dataset
        dataset, _cont, terminal, _msg = tlk_scripts.update_gap_and_missing_fill(
                        dataset=MW.dataset,
                        gap_interpolation_method=interp_method,
                        gap_interpolation_max_consec_fill=max_interp,
                        gap_debias_prefered_leading_period_hours=pref_lead_hours,
                        gap_debias_prefered_trailing_period_hours=pref_trail_hours,
                        gap_debias_minimum_leading_period_hours=min_lead_hours,
                        gap_debias_minimum_trailing_period_hours=min_trail_hours,
                        automatic_max_interpolation_duration_str=max_interp_duration_hours)


        if not _cont:
            Error(_msg[0], _msg[1])
            return
        for line in terminal:
            MW.prompt_fill.appendPlainText(line)

        MW.dataset = dataset

        # fill gaps automatic
        dataset, _cont, terminal, _msg = tlk_scripts.automatic_fill_gaps(
                                dataset = MW.dataset,
                                modeldata = MW.modeldata,
                                max_interp_dur_str = max_interp_duration_hours,
                                obstype=obstype,
                                overwrite=True)


        if not _cont:
            Error(_msg[0], _msg[1])
            return
        for line in terminal:
            MW.prompt_fill.appendPlainText(line)

        MW.dataset = dataset

    MW.prompt_metadata.appendPlainText(f'\n---- Filling {obstype} gaps using {gapfill_method} ---> Done ---- \n')
    Notification(f'The {obstype} gaps are filled using the {gapfill_method} method.')

# =============================================================================
# Diagnostics
# =============================================================================

def make_print_missing_obs(MW):
    if MW.dataset is None:
        Error('No Dataset', 'There is no dataset loaded.')
        return
    _cont, terminal, _msg = tlk_scripts.get_missing_obs_info(dataset=MW.dataset)
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    MW.prompt_fill.appendPlainText("\n \n")
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)


def make_print_gaps(MW):
    if MW.dataset is None:
        Error('No Dataset', 'There is no dataset loaded.')
        return
    _cont, terminal, _msg = tlk_scripts.get_gaps_info(dataset=MW.dataset)
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    MW.prompt_fill.appendPlainText("\n \n")
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)


def make_print_dataset(MW):
    if MW.dataset is None:
        Error('No Dataset', 'There is no dataset loaded.')
        return
    terminal = tlk_scripts.get_dataset_info(dataset=MW.dataset)

    MW.prompt_fill.appendPlainText("\n \n")
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)


def show_df_missing_obs(MW):
    _show_missing_obs_df(MW)
def show_df_gaps(MW):
    _show_gaps_df(MW)
def show_df_dataset(MW):
    _show_obsspace(MW)

def show_filled_df_missing_obs(MW):
    _show_missing_obs_fill_df(MW)
def show_filled_df_gaps(MW):
    _show_gaps_fill_df(MW)

def plot_dataset(MW):
    _show_timeseries(MW)




# # =============================================================================
# # helpers
# =============================================================================


def check_if_modeldata_can_be_used(MW, obstype):
    # check if modeldata exists
    if MW.modeldata is None:
        Error('No Modeldata', 'There is no Modeldata loaded, thus debias gapfill can not be performed.')
        return False

    if MW.modeldata.df.empty:
        Error('Empty Modeldata', 'The loaded  Modeldata is empty, thus debias gapfill can not be performed.')
        return False


    gapdf = MW.dataset.get_gaps_df()
    # check if period of modeldata has a full overlap
    start_model = MW.modeldata.df.index.get_level_values('datetime').min()
    end_model = MW.modeldata.df.index.get_level_values('datetime').max()

    start_gaps = gapdf['start_gap'].min()
    end_gaps = gapdf['end_gap'].max()

    # option A: modeldata exlusively later than gaps
    if start_model >= end_gaps:
        Error('Modeldata mismatch', 'The modeldata timeseries starts (({start_model}) later then the end of all the gaps ({end_gaps}).')
        return False
    # option B: modeldata exlusively before the gaps
    if end_model <= start_gaps:
        Error('Modeldata mismatch', f'The modeldata timeseries ends ({end_model}) before the start of the gaps ({start_gaps}).')
        return False


    # check if obstype is available in modeldata
    if not obstype in MW.modeldata.df.columns:
        Error('Modeldata missing', f'The modeldata does not contain the {obstype}-timeseries.')
        return False

    # check if required stations are present in modeldata
    stations_with_gaps = gapdf.index.to_series().unique()
    model_stations = MW.modeldata.df.index.get_level_values('name').unique()
    not_present = [gap_sta for gap_sta in stations_with_gaps if not gap_sta in list(model_stations)]
    if len(not_present) >0:
        Error('Modeldata missing stations', f'The modeldata does not contain timeseries for the following stations that have gaps: \n {not_present}.')
        return False

    return True



def _widget_grouper(MW):
    dic = {}

    # gapfill settings
    dic['debias_group'] = [MW.gap_pref_lead, MW.gap_min_lead, MW.gap_pref_trail,
                          MW.gap_min_trail]
    dic['interp_group'] = [MW.gap_interp_method, MW.gap_max_interp]
    dic['auto_group'] = [MW.gap_debias_max_interp_hours]

    return dic

