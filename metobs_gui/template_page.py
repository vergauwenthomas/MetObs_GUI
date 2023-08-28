#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 13:30:48 2023

@author: thoverga
"""
from pathlib import Path
import os
import copy
import pytz
from PyQt5.QtWidgets import QFileDialog, QComboBox


# from main import MainWindow as MW

from metobs_gui.json_save_func import get_saved_vals, update_json_file
from metobs_gui.data_func import readfile, isvalidfile, get_columns

from metobs_gui.import_data_page import set_possible_templates


import metobs_gui.template_func as template_func
import metobs_gui.path_handler as path_handler

from metobs_gui.errors import Error, Notification



# =============================================================================
# Initialise values
# =============================================================================
def init_template_page(MW):

    MW.session['mapping'] = {}
    MW.session['mapping']['started'] = False

    # list all templates in the cache
    MW.session['templates'] = {}
    MW.session['templates']['cache'] = template_func.get_all_templates() # name.csv : path
    MW.session['templates']['in_use']: {} # name.csv : path

    # set data paths to saved files
    set_datapaths_init(MW)

    # set static spinners
    MW.browse_format.addItems(['long', 'wide', 'single-station'])
    MW.wide_obs_type.addItems(list(template_func.Obs_map_values.keys()))

    MW.timezone_spinner.addItems(pytz.common_timezones)
    MW.timezone_spinner.setCurrentText('UTC')

    # disable format options
    MW.wide_obs_type.setEnabled(False) # disable comboBox
    MW.wide_obs_units.setEnabled(False)
    MW.wide_obs_desc.setEnabled(False)
    MW.stationname.setEnabled(False)

    # disable all widgest for the mapping
    for box in _get_obstype_boxes(MW): box.setEnabled(False)
    for box in _get_metadata_boxes(MW): box.setEnabled(False)



def set_datapaths_init(MW):
    """
    Read saved values to look for a path for the data and metadata file.

    """
    saved_vals = get_saved_vals()

    # set datafile path
    if 'data_file_path' in saved_vals:
        MW.data_file_T.setText(str(saved_vals['data_file_path']))
        # MW.data_file_T_2.setText(str(saved_vals['data_file_path']))

    # set metadata file path
    if 'metadata_file_path' in saved_vals:
        MW.metadata_file_T.setText(str(saved_vals['metadata_file_path']))
        # MW.metadata_file_T_2.setText(str(saved_vals['metadata_file_path']))





# =============================================================================
# Triggers
# =============================================================================
# ----- browse files -------#

def browsefiles_data(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select data file', str(Path.home()))
    MW.data_file_T.setText(fname[0]) #update text

def browsefiles_metadata(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select metadata file', str(Path.home()))
    MW.metadata_file_T.setText(fname[0]) #update text

# ----- save paths --------
def save_path(MW, savebool, savekey, saveval):
    if savebool:
        savedict = {str(savekey): str(saveval)}
        update_json_file(savedict)

# ----- enable specific format settings --------
def enable_format_widgets(MW):
    dat_format = str(MW.browse_format.currentText())
    if dat_format == 'long':
        MW.wide_obs_type.setEnabled(False) # disable comboBox
        MW.wide_obs_units.setEnabled(False)
        MW.wide_obs_desc.setEnabled(False)
        MW.stationname.setEnabled(False)
    elif dat_format == 'wide':
        MW.wide_obs_type.setEnabled(True) # disable comboBox
        MW.wide_obs_units.setEnabled(True)
        MW.wide_obs_desc.setEnabled(True)
        MW.stationname.setEnabled(False)

    else:
        MW.wide_obs_type.setEnabled(False) # disable comboBox
        MW.wide_obs_units.setEnabled(False)
        MW.wide_obs_desc.setEnabled(False)
        MW.stationname.setEnabled(True)

    if MW.session['mapping']['started']:
        if (dat_format == 'long') | (dat_format == 'single-station'):
            # enable all
            for box in _get_obstype_boxes(MW): box.setEnabled(True)
            for box in _get_datetime_boxes(MW): box.setEnabled(True)
            _get_name_box(MW).setEnabled(True)
            if MW.use_metadata.isChecked():
                for box in _get_metadata_boxes(MW): box.setEnabled(True)
                lab_txt = 'Station name/ID (=column in BOTH data and metadata files)'
            else:
                # update label text for more info.
                lab_txt = 'Station name/ID (=column in the data file)'

        else:
            for box in _get_obstype_boxes(MW): box.setEnabled(False)
            for box in _get_datetime_boxes(MW): box.setEnabled(True)
            if MW.use_metadata.isChecked():
                for box in _get_metadata_boxes(MW): box.setEnabled(True)
                _get_name_box(MW).setEnabled(True)
                lab_txt = 'Station name/ID (=column in the metadata file)'
            else:

                MW.name_col_CB.setCurrentText(template_func.not_mapable)
                _get_name_box(MW).setEnabled(False)
                lab_txt = 'Station name/ID (data columns are used)'

        MW.stationname.setText(lab_txt)


def prepare_for_mapping(MW):
    MW.session['mapping']['started'] = True

    dat_format = str(MW.browse_format.currentText())
    _get_name_box(MW).setEnabled(True)
    if (dat_format == 'long') | (dat_format == 'single-station'):
        # First try reading the datafile
        # 1. THe data file
        datafile = MW.data_file_T.text()
        valid, _msg = isvalidfile(datafile, filetype='.csv')
        if not valid:
            Error(_msg)
            return
        # Read columns
        df_head = readfile(datafile, nrows=20)[0]
        df_cols = list(df_head.columns)
        MW.session['mapping']['data_head'] = df_head.copy() #save for tests on template
        MW.session['mapping']['data_cols'] = df_cols.copy() #save for tests on template
        # Get the obstype spinners
        csv_columns = df_cols
        csv_columns.insert(0, template_func.not_mapable)

        # enable all obs boxes for colum mapping
        for box in _get_obstype_boxes(MW): box.setEnabled(True)
        for box in _get_datetime_boxes(MW): box.setEnabled(True)


        # set column and default values
        template_func.set_obstype_spinner_values(MW, csv_columns)
        template_func.set_time_spinner_values(MW, csv_columns)
        template_func.set_obstype_desc_defaults(MW)
        template_func.set_obstype_units_defaults(MW)
        template_func.set_datetime_defaults(MW)
    else:
        csv_columns = []
        if not MW.use_metadata.isChecked():
            # no metadata and wide format
            _get_name_box(MW).setEnabled(False)



    #2. The metadata
    if MW.use_metadata.isChecked():
        metadatafile = MW.metadata_file_T.text()
        valid, _msg = isvalidfile(metadatafile, filetype='.csv')
        if not valid:
            Error(_msg)
            return
        metadf_head = readfile(metadatafile, nrows=20)[0]
        metadf_cols = list(metadf_head.columns)
        MW.session['mapping']['metadata_head'] = metadf_head.copy() #save for tests on template
        MW.session['mapping']['metadata_cols'] = metadf_cols.copy() #save for tests on template
        metadf_cols.insert(0, template_func.not_mapable)

        # enable all obs boxes for colum mapping
        for box in _get_metadata_boxes(MW): box.setEnabled(True)

        # set column and default values
        template_func.set_metadata_spinner_values(MW, metadf_cols)
    else:
        metadf_cols = []

    template_func.set_name_spinner_values(MW, csv_columns, metadf_cols)
    # enable the build button
    MW.build_B.setEnabled(True)


# -------  Build template ---------

def build_template(MW):
    MW.session['mapping']['template_df'] = None
    df, succes = template_func.make_template_build(MW)
    if succes:
        MW.session['mapping']['template_df'] = df.copy()
        MW.templmodel.setDataFrame(df)
        MW.save_template.setEnabled(True) #enable the save button

def save_template_call(MW):
    # test if template is not empty
    if MW.session['mapping']['template_df'] is None:
        Error('Template error', 'The template has not been succesfully build. It is not possible to save.')
        return
    if MW.session['mapping']['template_df'].empty:
        Error('Template error', 'The template is empty. It is not possible to save.')
        return
    # form path to save the template
    template_name = str(MW.templatename.text())
    if not template_name.endswith('.csv'):
        filename = template_name + '.csv'
    else:
        filename = template_name
    target_path = os.path.join(path_handler.template_dir, filename)

    if path_handler.file_exist(target_path):
        Error(f'{target_path} already exists! Change name of the template file and save again.')
        return

    # save template
    temp_df =MW.session['mapping']['template_df']
    temp_df.to_csv(path_or_buf=target_path, sep=',', index=False)

    Notification(f'Template ({filename}) is saved!')

    # update dict
    MW.session['templates']['in_use'] = {filename : target_path}
    # update cache templates
    MW.session['templates']['cache'] = template_func.get_all_templates() # name.csv : path

    # Trigger update spinner on import page so the saved templ appears in the spinner there
    set_possible_templates(MW)


def show_data_head(MW):
    # 1. THe data file
    datafile = MW.data_file_T.text()
    valid, _msg = isvalidfile(datafile, filetype='.csv')
    if not valid:
        Error(_msg)
        return
    # Read columns
    df_head = readfile(datafile, nrows=20)[0]
    MW.templmodel.setDataFrame(df_head)

def show_metadata_head(MW):
   metadatafile = MW.metadata_file_T.text()
   valid, _msg = isvalidfile(metadatafile, filetype='.csv')
   if not valid:
       Error(_msg)
       return
   # Read columns
   metadf_head = readfile(metadatafile, nrows=20)[0]
   MW.templmodel.setDataFrame(metadf_head)



def show_template(MW):
    if not 'template_df' in MW.session['mapping']:
        Error('View error', 'The template is not been succesfully build yet.')
        return
    MW.templmodel.setDataFrame(MW.session['mapping']['template_df'])


# =============================================================================
# helpers
# =============================================================================
def _get_obstype_boxes(MW):
    return [MW.temp_col_CB, MW.temp_units_CB, MW.temp_desc_T,
             MW.radtemp_col_CB, MW.radtemp_units_CB, MW.radtemp_desc_T,
             MW.hum_col_CB, MW.hum_units_CB, MW.hum_desc_T,
             MW.pre_col_CB, MW.pre_units_CB, MW.pre_desc_T,
             MW.pre_s_col_CB, MW.pre_s_units_CB, MW.pre_s_desc_T,
             MW.wind_col_CB, MW.wind_units_CB, MW.wind_desc_T,
             MW.gust_col_CB, MW.gust_units_CB, MW.gust_desc_T,
             MW.dir_col_CB, MW.dir_units_CB, MW.dir_desc_T,
             MW.p_col_CB, MW.p_units_CB, MW.p_desc_T,
             MW.psea_col_CB, MW.psea_units_CB, MW.psea_desc_T]

def _get_datetime_boxes(MW):
     return [MW.datetime_col_CB, MW.datetime_fmt_T,
             MW.date_col_CB, MW.date_fmt_T,
             MW.time_col_CB, MW.time_fmt_T]


def _get_metadata_boxes(MW):
    return [MW.lat_col_CB, MW.lon_col_CB,
            MW.loc_col_CB, MW.call_col_CB, MW.network_col_CB]

def _get_name_box(MW):
    return MW.name_col_CB


